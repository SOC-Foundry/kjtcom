#!/usr/bin/env python3
"""Run Qwen3.5-9B evaluator with schema-validated output.

v9.49: Schema validation + retry-with-feedback loop. Evaluator reads execution
context (event log, file checks, design doc), NOT build log. Build log is an
OUTPUT of the process, not an INPUT.

v10.65 (ADR-021): Synthesis audit trail. normalize_llm_output tracks coercions;
raises EvaluatorSynthesisExceeded if > 50% of required fields are synthesized.
Forces fall-through from Tier 1 (Qwen) to Tier 2 (Gemini).
"""
import json
import jsonschema
import os
import subprocess
import sys
import time
import re

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event
from utils.ollama_config import merge_defaults

OLLAMA_URL = 'http://localhost:11434/api/chat'
SCORES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'agent_scores.json')
PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HARNESS_PATH = os.path.join(PROJECT_DIR, 'docs', 'evaluator-harness.md')
SCHEMA_PATH = os.path.join(PROJECT_DIR, 'data', 'eval_schema.json')

class EvaluatorSynthesisExceeded(Exception):
    """Raised when the normalizer synthesizes > 50% of a workstream's required fields."""
    def __init__(self, workstream_id, ratio, fields):
        self.workstream_id = workstream_id
        self.ratio = ratio
        self.fields = fields
        super().__init__(f"Synthesis ratio {ratio:.2f} > 0.5 for {workstream_id}; fields: {fields}")


def load_harness():
    """Load evaluator harness as system prompt prefix."""
    try:
        with open(HARNESS_PATH) as f:
            return f.read()
    except FileNotFoundError:
        print(f"WARNING: Evaluator harness not found at {HARNESS_PATH}")
        return ""


def load_eval_schema():
    """Load the strict JSON schema for evaluation output."""
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def load_gotcha_archive():
    """Load resolved gotchas for evaluator context."""
    archive_path = os.path.join(PROJECT_DIR, 'data', 'gotcha_archive.json')
    try:
        with open(archive_path) as f:
            data = json.load(f)
        return data.get('resolved_gotchas', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _find_doc(doc_type, iteration):
    """Locate an iteration doc, falling through to docs/archive/ (v10.63 mid-reorg)."""
    for loc in [
        f"docs/kjtcom-{doc_type}-{iteration}.md",
        f"docs/archive/kjtcom-{doc_type}-{iteration}.md",
        f"docs/drafts/kjtcom-{doc_type}-{iteration}.md",
    ]:
        if os.path.exists(loc):
            return loc
    return None


def build_rich_context(iteration):
    """Build 50-80KB context package for Qwen evaluation."""
    parts = []

    # Current iteration artifacts (build + design + plan)
    for doc_type in ["build", "design", "plan"]:
        path = _find_doc(doc_type, iteration)
        if path:
            parts.append(f"=== CURRENT {doc_type.upper()} ({iteration}) ===")
            parts.append(open(path).read())

    # Few-shot precedent reports
    for ver in ["v10.59", "v10.56", "v10.58"]:
        for loc in [f"docs/kjtcom-report-{ver}.md", f"docs/archive/kjtcom-report-{ver}.md"]:
            if os.path.exists(loc):
                parts.append(f"=== EXAMPLE REPORT ({ver}) — match this format ===")
                parts.append(open(loc).read())
                break

    # Middleware registry
    if os.path.exists("data/middleware_registry.json"):
        parts.append("=== MIDDLEWARE REGISTRY ===")
        parts.append(open("data/middleware_registry.json").read())

    # Gotcha archive
    if os.path.exists("data/gotcha_archive.json"):
        parts.append("=== GOTCHA ARCHIVE ===")
        parts.append(open("data/gotcha_archive.json").read())

    # ADRs from harness
    if os.path.exists("docs/evaluator-harness.md"):
        harness = open("docs/evaluator-harness.md").read()
        adr_start = harness.find("## 3.")
        adr_end = harness.find("## 4.")
        if adr_start > 0 and adr_end > 0:
            parts.append("=== ARCHITECTURE DECISIONS ===")
            parts.append(harness[adr_start:adr_end])

    # Recent changelog (first 5 entries)
    if os.path.exists("docs/kjtcom-changelog.md"):
        cl = open("docs/kjtcom-changelog.md").read()
        entries = cl.split("\n## ")[:6]
        parts.append("=== RECENT CHANGELOG ===")
        parts.append("\n## ".join(entries))

    ctx = "\n\n".join(parts)
    print(f"[EVAL] Rich context: {len(ctx):,} chars (~{len(ctx)//4:,} tokens)")
    return ctx


def build_execution_context(version):
    """Build ground-truth execution context from event log, build log, changelog, and file system."""
    event_log_path = os.path.join(PROJECT_DIR, 'data', 'iao_event_log.jsonl')

    lines = []
    events = []
    try:
        with open(event_log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                if ev.get('iteration') == version:
                    events.append(ev)
    except FileNotFoundError:
        lines.append("No event log found.")

    errors = [e for e in events if e.get('status') in ('error', 'timeout')]
    successes = [e for e in events if e.get('status') == 'success']
    lines.append(f"Total events: {len(events)}, successes: {len(successes)}, errors/timeouts: {len(errors)}")

    if successes:
        lines.append("Successful actions:")
        for e in successes:
            if e.get('event_type') == 'command':
                lines.append(f"  - {e.get('source_agent', '?')}: {e.get('action', '?')} {e.get('input_summary', '')}")

    if errors:
        lines.append("Errors/timeouts:")
        for e in errors[:10]:
            lines.append(f"  - {e.get('source_agent', '?')}: {e.get('action', '?')} -> {e.get('status')} ({e.get('error', 'N/A')[:80]})")

    # Read build log for additional evidence
    build_log_path = os.path.join(PROJECT_DIR, 'docs', f'kjtcom-build-{version}.md')
    if os.path.exists(build_log_path):
        try:
            with open(build_log_path) as f:
                build_content = f.read()
            lines.append(f"\nBuild log ({len(build_content)} chars):")
            lines.append(build_content[:3000])
        except Exception:
            pass

    # Read changelog for evidence of completed work
    changelog_path = os.path.join(PROJECT_DIR, 'docs', 'kjtcom-changelog.md')
    if os.path.exists(changelog_path):
        try:
            with open(changelog_path) as f:
                cl_content = f.read()
            # Extract entries for this version
            version_entries = []
            for cl_line in cl_content.split('\n'):
                if version in cl_line:
                    version_entries.append(cl_line)
            if version_entries:
                lines.append(f"\nChangelog entries for {version}:")
                for entry in version_entries[:20]:
                    lines.append(f"  {entry}")
        except Exception:
            pass

    # Check key file existence
    key_files = [
        'scripts/run_evaluator.py',
        'scripts/generate_artifacts.py',
        'data/eval_schema.json',
        'data/claw3d_components.json',
        'CLAUDE.md',
        'GEMINI.md',
        'docs/kjtcom-changelog.md',
        'docs/bourdain-scaling-plan.md',
        'app/web/architecture.html',
        'app/web/claw3d.html',
        'app/lib/widgets/mw_tab.dart',
    ]
    lines.append("\nKey file existence:")
    for kf in key_files:
        full = os.path.join(PROJECT_DIR, kf)
        exists = os.path.exists(full)
        line_count = 0
        if exists:
            try:
                with open(full) as f:
                    line_count = len(f.readlines())
            except:
                pass
        lines.append(f"  {'EXISTS' if exists else 'MISSING'}: {kf} ({line_count} lines)")

    return "\n".join(lines)


def parse_workstream_count(design_doc_path):
    """Parse design doc to extract workstream count and names."""
    if not os.path.exists(design_doc_path):
        return 0, []

    with open(design_doc_path) as f:
        content = f.read()

    lines = content.split("\n")
    w_count = 0
    w_names = []

    # Try heading format first: ### W1: Name (P0)
    for line in lines:
        m = re.match(r'^###\s+W(\d+)[:\s]+(.+?)(?:\s*\(P\d\))?\s*$', line)
        if m:
            w_count += 1
            w_names.append(m.group(2).strip())

    if w_count > 0:
        return w_count, w_names

    # Fallback: table format | W1 | Name | ... |
    in_table = False
    for line in lines:
        if "| #" in line and "Workstream" in line:
            in_table = True
            continue
        if in_table and line.startswith("|"):
            if "---" in line or "| #" in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[1].startswith("W"):
                w_count += 1
                w_names.append(parts[2])
        elif in_table and not line.strip().startswith("|") and not line.strip() == "":
            in_table = False

    return w_count, w_names


def validate_schema(output):
    """Validate JSON output against the strict eval schema."""
    schema = load_eval_schema()
    errors = []

    validator = jsonschema.Draft7Validator(schema)
    for error in sorted(validator.iter_errors(output), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        if error.validator == "type":
            hint = f"expected type '{error.validator_value}', got '{type(error.instance).__name__}'"
        elif error.validator == "enum":
            hint = f"must be one of {error.validator_value}, got '{error.instance}'"
        elif error.validator == "maximum":
            hint = f"must be <= {error.validator_value}, got {error.instance}"
        elif error.validator == "minimum":
            hint = f"must be >= {error.validator_value}, got {error.instance}"
        elif error.validator == "minItems":
            hint = f"must have >= {error.validator_value} items, got {len(error.instance) if isinstance(error.instance, list) else 0}"
        elif error.validator == "minLength":
            hint = f"must be >= {error.validator_value} chars, got {len(str(error.instance))} chars"
        elif error.validator == "required":
            hint = f"missing required field '{error.message.split(chr(39))[1]}'"
        else:
            hint = error.message[:120]
        errors.append(f"Field '{path}': {hint}")

    return errors


def parse_executing_agent(design_doc_path):
    """Parse design doc header for the recommended/executing agent."""
    if not os.path.exists(design_doc_path):
        return "claude-code"

    with open(design_doc_path) as f:
        for _ in range(20):
            line = f.readline()
            if not line: break
            if "**Recommended Agent:**" in line or "**Executing Agent:**" in line:
                agent = line.split(":")[-1].strip().lower()
                if "claude" in agent: return "claude-code"
                if "gemini" in agent: return "gemini-cli"
                return agent.replace(" ", "-")
    return "claude-code"


def normalize_llm_output(output, expected_count, expected_names, executing_agent, iteration="v0.0", synthesis_threshold=0.5):
    """ADR-014/021: Coerce common LLM deviations and track synthesis audit trail.

    Returns (normalized_output, synthesis_metadata).
    Raises EvaluatorSynthesisExceeded if any workstream's synthesis ratio > threshold.
    """
    if not isinstance(output, dict):
        return output, {"synthesized_fields": [], "synthesis_ratio_per_workstream": {}}

    ws_raw = output.get("workstreams", [])
    if isinstance(ws_raw, dict):
        ws_raw = list(ws_raw.values())
    if not isinstance(ws_raw, list):
        ws_raw = []

    priority_map = {
        "critical": "P0", "high": "P0", "p0": "P0",
        "medium": "P1", "med": "P1", "p1": "P1",
        "low": "P2", "p2": "P2",
        "minor": "P3", "p3": "P3",
    }
    outcome_map = {
        "success": "complete", "successful": "complete", "done": "complete",
        "complete": "complete", "completed": "complete",
        "partial": "partial", "in progress": "partial", "in-progress": "partial",
        "failed": "failed", "fail": "failed", "broken": "failed",
        "deferred": "deferred", "skipped": "deferred", "blocked": "deferred",
    }

    fixed_ws = []
    synthesized_fields = []
    ratios = {}

    for i in range(expected_count):
        src = ws_raw[i] if i < len(ws_raw) and isinstance(ws_raw[i], dict) else {}
        ws_synthesized = []
        
        wid = src.get("id") or f"W{i+1}"
        if not src.get("id"): ws_synthesized.append("id")
        
        name = src.get("name") or (expected_names[i] if i < len(expected_names) else f"Workstream {i+1}")
        if not src.get("name"): ws_synthesized.append("name")

        # 1. Priority (Required field)
        prio_raw = src.get("priority")
        if not prio_raw:
            prio = "P1"
            ws_synthesized.append("priority")
        else:
            prio = str(prio_raw).strip().lower()
            prio = priority_map.get(prio, prio.upper() if prio.upper() in ("P0","P1","P2","P3") else "P1")
            if prio != str(prio_raw): ws_synthesized.append(f"priority(coerced:{prio_raw}->{prio})")

        # 2. Outcome (Required field)
        out_raw = src.get("outcome")
        if not out_raw:
            out = "partial"
            ws_synthesized.append("outcome")
        else:
            out = str(out_raw).strip().lower()
            out = outcome_map.get(out, "partial" if out not in ("complete","partial","failed","deferred") else out)
            if out != str(out_raw): ws_synthesized.append(f"outcome(coerced:{out_raw}->{out})")

        # 3. Score (Required field)
        score_raw = src.get("score")
        if score_raw is None:
            score = 5
            ws_synthesized.append("score")
        else:
            try:
                score = int(score_raw)
            except (TypeError, ValueError):
                score = 5
                ws_synthesized.append(f"score(malformed:{score_raw}->5)")
        score = max(0, min(9, score))

        # 4. Evidence (Required field)
        evidence = src.get("evidence", "")
        if not evidence or len(str(evidence)) < 10:
            evidence = f"Evaluator did not return per-workstream evidence; see build log for {wid}."
            ws_synthesized.append("evidence")
        if isinstance(evidence, list):
            evidence = "; ".join(str(x) for x in evidence)
        evidence = str(evidence)[:1000]

        # 5. Improvements (Required field)
        improvements = src.get("improvements", [])
        if not improvements:
            ws_synthesized.append("improvements")
        elif isinstance(improvements, str):
            parts = [p.strip(" -•*") for p in improvements.replace("\n", ";").split(";") if p.strip()]
            improvements = parts or [improvements]
        
        if not isinstance(improvements, list):
            improvements = [str(improvements)]
        
        _pad_options = [
            "Evaluator returned fewer than two improvements; consider re-running with a richer build log.",
            "Add a unit test fixture for normalize_llm_output() covering all coercion paths.",
        ]
        while len(improvements) < 2:
            improvements.append(_pad_options[len(improvements) % 2])
            if "improvements_padded" not in ws_synthesized: ws_synthesized.append("improvements_padded")
        improvements = [str(x)[:500] for x in improvements][:6]

        # 6. Agents (Required field)
        agents = src.get("agents") or [executing_agent]
        if not src.get("agents"): ws_synthesized.append("agents")
        if not isinstance(agents, list):
            agents = [str(agents)]
            
        llms = src.get("llms") or ["qwen3.5:9b"]
        if not src.get("llms"): ws_synthesized.append("llms")
        if not isinstance(llms, list):
            llms = [str(llms)]
            
        mcps = src.get("mcps") or ["-"]
        if not src.get("mcps"): ws_synthesized.append("mcps")
        if not isinstance(mcps, list):
            mcps = [str(mcps)]
        valid_mcps = {"Firebase", "Context7", "Firecrawl", "Playwright", "Dart", "-"}
        mcps = [m for m in mcps if m in valid_mcps] or ["-"]
        mcps = mcps[:5]

        # ADR-021: Compute ratio based on 6 core Thompson Indicator Fields for workstreams
        # (priority, outcome, score, evidence, improvements, agents)
        core_fields = ["priority", "outcome", "score", "evidence", "improvements", "agents"]
        core_synthesized = [f for f in ws_synthesized if any(cf in f for cf in core_fields)]
        ratio = len(core_synthesized) / 6
        ratios[wid] = ratio
        
        for f in ws_synthesized:
            synthesized_fields.append(f"{wid}.{f}")

        fixed_ws.append({
            "id": wid,
            "name": name,
            "priority": prio,
            "outcome": out,
            "evidence": evidence,
            "agents": agents,
            "llms": llms,
            "mcps": mcps,
            "score": score,
            "improvements": improvements,
            "_synthesized_fields": ws_synthesized,
            "synthesis_ratio": ratio
        })
        
        if ratio > synthesis_threshold:
            raise EvaluatorSynthesisExceeded(wid, ratio, ws_synthesized)

    output["workstreams"] = fixed_ws

    # Trident normalization
    trident = output.get("trident", {}) or {}
    if not isinstance(trident, dict):
        trident = {}
    cost = str(trident.get("cost", ""))[:500]
    if len(cost) < 5:
        cost = "Cost not reported by evaluator."
        
    delivery = str(trident.get("delivery", ""))
    
    # G93: Prefer build log's literal Trident Metric (ADR-021)
    build_log_delivery = None
    build_log_path = _find_doc("build", iteration)
    if build_log_path:
        try:
            with open(build_log_path) as f:
                bl_content = f.read()
                # Match "Delivery: X/Y workstreams complete"
                m = re.search(r"Delivery:\s*(\d+/\d+\s+workstreams[^\n]*)", bl_content, re.IGNORECASE)
                if m:
                    build_log_delivery = m.group(1).strip()
        except Exception:
            pass

    if build_log_delivery:
        delivery = build_log_delivery
    elif not re.match(r'^\d+/\d+ workstreams', delivery):
        completed = sum(1 for w in fixed_ws if w["outcome"] == "complete")
        delivery = f"{completed}/{expected_count} workstreams complete (normalized)"
    
    perf = str(trident.get("performance", ""))[:500]
    if len(perf) < 10:
        perf = "Performance not reported by evaluator."
    output["trident"] = {"cost": cost, "delivery": delivery, "performance": perf}

    if not output.get("iteration"):
        output["iteration"] = "v0.0"
    summary = str(output.get("summary", ""))[:2000]
    if len(summary) < 50:
        summary = (summary + " (Evaluator returned a short summary; padded for schema compliance.)")[:2000]
    output["summary"] = summary

    wcb = output.get("what_could_be_better", [])
    if isinstance(wcb, str):
        wcb = [wcb]
    if not isinstance(wcb, list):
        wcb = [str(wcb)]
    if len(wcb) < 2:
        wcb = list(wcb) + ["Evaluator returned fewer than two improvement notes."]
    output["what_could_be_better"] = [str(x)[:500] for x in wcb][:8]

    return output, {"synthesized_fields": synthesized_fields, "synthesis_ratio_per_workstream": ratios}


def validate_qwen_output(output, expected_count, expected_names):
    """Full validation: schema + workstream count + names (fuzzy) + banned phrases + mcps logic."""
    errors = []

    # 1. JSON schema validation
    errors.extend(validate_schema(output))

    # 2. Workstream count
    ws_list = output.get("workstreams", [])
    if len(ws_list) != expected_count:
        errors.append(
            f"Workstream count: got {len(ws_list)}, expected {expected_count}"
        )

    # 3. Workstream name matching (Fuzzy)
    for i, ws in enumerate(ws_list):
        if i < len(expected_names):
            expected = expected_names[i].lower()
            actual = ws.get("name", "").lower()
            
            def normalize_name(s):
                s = s.replace("—", " ").replace("–", " ").replace("-", " ").replace(":", " ")
                return " ".join(s.split())

            expected_norm = normalize_name(expected)
            actual_norm = normalize_name(actual)
            
            if expected_norm not in actual_norm and actual_norm not in expected_norm:
                expected_words = set(w for w in expected_norm.split() if len(w) > 3)
                actual_words = set(w for w in actual_norm.split() if len(w) > 3)
                overlap = expected_words.intersection(actual_words)
                
                if not overlap:
                    errors.append(
                        f"W{i+1} name mismatch: got '{actual}', expected '{expected}'"
                    )

        mcps = ws.get("mcps", [])
        if len(mcps) >= 5 and all(m in mcps for m in ["Firebase", "Firecrawl", "Dart"]):
             errors.append(f"W{i+1}: Do NOT dump all MCPs. List ONLY the {len(mcps)} used.")

    # 4. Banned phrase check
    text = json.dumps(output)
    banned = ["robust validation", "clean release", "strategic shift", "healthy system", "TBD"]
    for phrase in banned:
        if phrase.lower() in text.lower():
            errors.append(f"Banned phrase found: '{phrase}'")

    return errors


def call_qwen(messages):
    """Call Qwen via Ollama."""
    payload = merge_defaults({
        'model': 'qwen3.5:9b',
        'messages': messages,
    }, evaluation=True)

    start_time = time.time()
    payload_json = json.dumps(payload)
    result = subprocess.run(
        ['curl', '-s', OLLAMA_URL, '-H', 'Content-Type: application/json', '--data-binary', '@-'],
        input=payload_json, capture_output=True, text=True, timeout=300
    )
    latency = int((time.time() - start_time) * 1000)

    try:
        response = json.loads(result.stdout)
        content = response['message']['content']
    except (json.JSONDecodeError, KeyError, TypeError):
        return None, {}, 0

    tokens = {
        'prompt_tokens': response.get('prompt_eval_count', 0),
        'eval_tokens': response.get('eval_count', 0),
        'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
    }

    return content, tokens, latency


def repair_json(raw):
    """Repair common LLM JSON issues before parsing."""
    import re
    raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^```\s*$', '', raw, flags=re.MULTILINE)
    raw = re.sub(r',\s*([}\]])', r'\1', raw)
    return raw.strip()


def parse_json_from_response(content):
    """Extract JSON object from response text."""
    if not content:
        return None
    content = repair_json(content)
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        try:
            return json.loads(content[json_start:json_end])
        except json.JSONDecodeError:
            pass
    return None


def call_gemini_flash(prompt):
    """Call Gemini Flash via litellm."""
    try:
        import litellm
    except ImportError:
        print("[EVAL] litellm not installed, skipping Gemini fallback")
        return None, {}, 0

    from utils.ollama_config import GEMINI_MODEL
    start_time = time.time()
    try:
        response = litellm.completion(
            model=GEMINI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=20000,
        )
        latency = int((time.time() - start_time) * 1000)
        content = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        usage = response.get('usage', {})
        print(f"[EVAL] Gemini Flash finished with reason: {finish_reason}, usage: {usage}")
        tokens = {
            'prompt_tokens': usage.get('prompt_tokens', 0),
            'eval_tokens': usage.get('completion_tokens', 0),
            'total_tokens': usage.get('total_tokens', 0),
        }
        return content, tokens, latency
    except Exception as e:
        print(f"[EVAL] Gemini Flash call failed: {e}")
        return None, {}, 0


def generate_self_eval(build_log, design_doc, version, expected_names):
    """Generate a self-evaluation when all LLM evaluators fail."""
    import re
    workstreams = []
    for i, name in enumerate(expected_names):
        w_tag = f"W{i+1}"
        evidence_lines = []
        name_words = [w.lower() for w in name.split() if len(w) > 3]
        for line in build_log.split('\n'):
            line_lower = line.lower()
            if w_tag in line or name.lower() in line_lower:
                evidence_lines.append(line.strip())
            elif any(word in line_lower for word in name_words):
                evidence_lines.append(line.strip())

        has_evidence = len(evidence_lines) > 0
        outcome = "partial" if has_evidence else "deferred"
        score = min(6, len(evidence_lines)) if has_evidence else 0
        priority = "P1"
        p_match = re.search(rf'W{i+1}[:\s].*?\((P\d)\)', design_doc)
        if p_match:
            priority = p_match.group(1)

        evidence_text = "; ".join(evidence_lines[:3]) if evidence_lines else "No build log evidence found for this workstream"

        workstreams.append({
            "id": w_tag,
            "name": name,
            "priority": priority,
            "outcome": outcome,
            "evidence": evidence_text[:200],
            "agents": ["gemini-cli"],
            "llms": ["qwen3.5:9b"],
            "mcps": ["-"],
            "score": min(score, 7),
            "improvements": [
                "Self-eval fallback used - Tier 1 and Tier 2 both failed or exceeded synthesis threshold.",
                "Manual review recommended for accurate scoring."
            ]
        })

    total = len(expected_names)
    completed = sum(1 for ws in workstreams if ws['outcome'] == 'complete')

    return {
        "iteration": version,
        "summary": f"Self-evaluation fallback for {version}. Tier 1 and Tier 2 both failed or exceeded synthesis threshold. {total} workstreams parsed from design doc. Scores capped at 7/10 to avoid self-grading bias.",
        "workstreams": workstreams,
        "trident": {
            "cost": "Minimal - self-eval required no LLM tokens",
            "delivery": f"{completed}/{total} workstreams completed (self-eval)",
            "performance": "Self-eval fallback triggered - evaluator pipeline needs repair"
        },
        "what_could_be_better": [
            "Qwen failed schema validation or synthesis check after 3 attempts.",
            "Gemini Flash failed schema validation or synthesis check after 2 attempts.",
            "Self-eval cannot provide the same quality as an independent evaluator."
        ]
    }


def build_evaluator_prompt(version, rich_context, expected_count, expected_names, executing_agent):
    """Build the shared evaluator prompt with rich context."""
    ws_list_str = "\n".join(f"  W{i+1}: {name}" for i, name in enumerate(expected_names))

    return f"""You are Qwen, the evaluator for kjtcom.

IMPORTANT: Study the EXAMPLE REPORTS in the context below. Your output must follow the Thompson Schema evaluation logic.
Use the build log and design doc to score each workstream 1-9 out of 10.
Use the middleware registry, gotcha archive, and ADRs for context about the project.

OUTPUT RULES:
- Return ONLY a JSON object. No markdown fences. No explanation. No preamble.
- score: integer 0-9 (NEVER 10)
- agents: must include [\"{executing_agent}\"]
- workstreams: exactly {expected_count} objects matching the names below.

WORKSTREAMS TO EVALUATE (exactly {expected_count}):
{ws_list_str}

=== RICH CONTEXT ===
{rich_context}

Return ONLY the JSON object following the structure:
{{"iteration":"{version}","summary":"...","workstreams":[...],"trident":{{"cost":"...","delivery":"...","performance":"..."}},"what_could_be_better":[...]}}"""


def try_qwen_tier(base_prompt, harness, expected_count, expected_names, executing_agent, version, threshold=0.5, verbose=False):
    """Tier 1: Qwen3.5-9B via Ollama (3 attempts)."""
    current_prompt = base_prompt
    tokens = {}

    for attempt in range(3):
        print(f"\n[EVAL] Qwen attempt {attempt + 1}/3...")

        messages = []
        if harness:
            messages.append({'role': 'system', 'content': harness})
        messages.append({'role': 'user', 'content': current_prompt})

        content, tokens, latency = call_qwen(messages)

        log_event("llm_call", "qwen3.5-9b", "qwen3.5:9b",
                  f"evaluate-schema-attempt-{attempt+1}",
                  input_summary=current_prompt[:200],
                  output_summary=(content or "")[:200],
                  tokens={"prompt": tokens.get('prompt_tokens', 0),
                          "eval": tokens.get('eval_tokens', 0),
                          "total": tokens.get('total_tokens', 0)},
                  latency_ms=latency,
                  status="success" if content else "empty_response")

        if verbose and content:
            print(f"[EVAL] Qwen raw response (first 500 chars): {content[:500]}")

        if not content:
            current_prompt = base_prompt + "\n\nERROR: Empty response. Return ONLY a JSON object."
            continue

        parsed = parse_json_from_response(content)
        if parsed is None:
            current_prompt = base_prompt + "\n\nERROR: Your response was not valid JSON. Return ONLY a JSON object."
            continue

        try:
            parsed, metadata = normalize_llm_output(parsed, expected_count, expected_names, executing_agent, version, threshold)
            errors = validate_qwen_output(parsed, expected_count, expected_names)
        except EvaluatorSynthesisExceeded as e:
            print(f"[EVAL] Qwen synthesis threshold exceeded: {e}")
            return None # Force fall-through
        except (AttributeError, TypeError) as e:
            errors = [f"Malformed workstream structure: {e}"]

        if not errors:
            print(f"[EVAL] Qwen schema validation passed on attempt {attempt + 1}")
            parsed['evaluator_tokens'] = tokens
            parsed['evaluator'] = 'qwen3.5:9b'
            parsed['tier_used'] = 'qwen'
            parsed['synthesis_metadata'] = metadata
            return parsed

        print(f"[EVAL] Qwen validation failed attempt {attempt + 1} with {len(errors)} errors.")
        current_prompt = base_prompt + "\n\nVALIDATION ERRORS:\n" + "\n".join(errors)

    return None


def try_gemini_tier(base_prompt, expected_count, expected_names, version, threshold=0.5, verbose=False):
    """Tier 2: Gemini Flash via litellm (2 attempts)."""
    current_prompt = base_prompt

    for attempt in range(2):
        print(f"\n[EVAL] Gemini Flash attempt {attempt + 1}/2 (Qwen fallback)...")
        content, tokens, latency = call_gemini_flash(current_prompt)

        if not content:
            print(f"[EVAL] Gemini Flash returned empty content (latency: {latency}ms)")
            continue

        if verbose:
            print(f"[EVAL] Gemini Flash raw response ({len(content)} chars): {content[:500]}")

        parsed = parse_json_from_response(content)
        if parsed is None:
            print(f"[EVAL] Gemini Flash returned invalid JSON")
            continue

        try:
            parsed, metadata = normalize_llm_output(parsed, expected_count, expected_names, "gemini-cli", version, threshold)
            errors = validate_qwen_output(parsed, expected_count, expected_names)
        except EvaluatorSynthesisExceeded as e:
            print(f"[EVAL] Gemini synthesis threshold exceeded: {e}")
            return None
        except (AttributeError, TypeError) as e:
            errors = [f"Malformed workstream structure: {e}"]

        if not errors:
            print(f"[EVAL] Gemini Flash validation passed on attempt {attempt + 1}")
            parsed['evaluator_tokens'] = tokens
            parsed['evaluator'] = 'gemini-flash (qwen-fallback)'
            parsed['tier_used'] = 'gemini-flash'
            parsed['synthesis_metadata'] = metadata
            return parsed

        print(f"[EVAL] Gemini validation failed attempt {attempt + 1} with {len(errors)} errors.")
        current_prompt = base_prompt + "\n\nVALIDATION ERRORS:\n" + "\n".join(errors)

    return None


def evaluate_with_retry(version, design_doc_path, threshold=0.5, verbose=False, test_fallback=None):
    """Three-tier evaluator fallback chain."""
    expected_count, expected_names = parse_workstream_count(design_doc_path)
    executing_agent = parse_executing_agent(design_doc_path)
    
    with open(design_doc_path) as f:
        design_content = f.read()

    rich_context = build_rich_context(version)
    harness = load_harness()

    base_prompt = build_evaluator_prompt(
        version, rich_context, expected_count,
        expected_names, executing_agent
    )

    # Tier 1: Qwen
    if test_fallback not in ('gemini', 'self-eval'):
        result = try_qwen_tier(base_prompt, harness, expected_count, expected_names, executing_agent, version, threshold, verbose)
        if result: return result
        print("[EVAL] Qwen tier exhausted or threshold exceeded. Falling through to Gemini Flash.")

    # Tier 2: Gemini Flash
    if test_fallback != 'self-eval':
        result = try_gemini_tier(base_prompt, expected_count, expected_names, version, threshold, verbose)
        if result: return result
        print("[EVAL] Gemini tier exhausted or threshold exceeded. Falling through to self-eval.")

    # Tier 3: Self-eval
    build_log = ""
    for loc in [f'docs/kjtcom-build-{version}.md', f'docs/archive/kjtcom-build-{version}.md', f'docs/drafts/kjtcom-build-{version}.md']:
        if os.path.exists(loc):
            with open(loc) as f: build_log = f.read()
            break
            
    result = generate_self_eval(build_log, design_content, version, expected_names)
    _, metadata = normalize_llm_output(result, expected_count, expected_names, executing_agent, version, 1.0) # threshold 1.0 for self-eval
    result['synthesis_metadata'] = metadata
    result['evaluator'] = 'self-eval (fallback)'
    result['tier_used'] = 'self-eval'
    
    for ws in result.get('workstreams', []):
        if ws.get('score', 0) > 7:
            ws['raw_self_grade'] = ws['score']
            ws['score'] = 7
            ws['score_note'] = 'Self-grading cap applied (ADR-015)'
    return result


def write_report_markdown(version, evaluation, suffix=""):
    """Write the evaluation report with synthesis audit trail."""
    report_path = os.path.join(PROJECT_DIR, 'docs', f'kjtcom-report-{version}{suffix}.md')
    evaluator = evaluation.get('evaluator', 'unknown')
    lines = [
        f"# kjtcom - Report v{version.replace('v','')}",
        "",
        f"**Evaluator:** {evaluator}",
        f"**Date:** {time.strftime('%B %d, %Y')}",
        "",
        "## Summary",
        "",
        evaluation.get('summary', 'No summary available.'),
        "",
        "## Workstream Scores",
        "",
        "| # | Workstream | Priority | Outcome | Score | Evidence |",
        "|---|-----------|----------|---------|-------|----------|",
    ]
    for ws in evaluation.get('workstreams', []):
        lines.append(f"| {ws.get('id','?')} | {ws.get('name','?')} | {ws.get('priority','?')} | {ws.get('outcome','?')} | {ws.get('score',0)}/10 | {ws.get('evidence','')[:80]} |")
    
    lines.extend([
        "",
        "## Trident",
        "",
        f"- **Cost:** {evaluation.get('trident', {}).get('cost', 'N/A')}",
        f"- **Delivery:** {evaluation.get('trident', {}).get('delivery', 'N/A')}",
        f"- **Performance:** {evaluation.get('trident', {}).get('performance', 'N/A')}",
        "",
        "## What Could Be Better",
        ""
    ])
    for item in evaluation.get('what_could_be_better', []):
        lines.append(f"- {item}")
        
    lines.extend(["", "## Workstream Details", ""])
    for ws in evaluation.get('workstreams', []):
        lines.append(f"### {ws.get('id','?')}: {ws.get('name','?')}")
        lines.append(f"- **Agents:** {', '.join(ws.get('agents', []))}")
        lines.append(f"- **LLMs:** {', '.join(ws.get('llms', []))}")
        lines.append(f"- **MCPs:** {', '.join(ws.get('mcps', []))}")
        
        # Synthesis Audit Section (ADR-021)
        ratio = ws.get('synthesis_ratio', 0)
        if ratio > 0:
            lines.append(f"- **Synthesis Audit:**")
            lines.append(f"  - Ratio: {ratio:.2f}")
            lines.append(f"  - Synthesized: {', '.join(ws.get('_synthesized_fields', []))}")
            
        lines.append(f"- **Improvements:**")
        for imp in ws.get('improvements', []):
            lines.append(f"  - {imp}")
        lines.append("")
        
    lines.append("---")
    lines.append(f"*Report {version}, {time.strftime('%B %d, %Y')}. Evaluator: {evaluator}.*")

    with open(report_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"[EVAL] Report written to {report_path}")
    return report_path


def save_scores(version, evaluation):
    """Save evaluation result to agent_scores.json."""
    try:
        with open(SCORES_PATH) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    if isinstance(data, list):
        data = {'iterations': data}
    if 'iterations' not in data:
        data['iterations'] = []

    found = False
    for entry in data['iterations']:
        if entry.get('iteration') == version:
            entry.update(evaluation)
            found = True
            break

    if not found:
        evaluation['date'] = time.strftime('%Y-%m-%d')
        data['iterations'].append(evaluation)

    with open(SCORES_PATH, 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    version = os.environ.get('IAO_ITERATION', 'v9.49')
    verbose = '--verbose' in sys.argv
    test_fallback = None
    threshold = 0.5

    if '--iteration' in sys.argv:
        idx = sys.argv.index('--iteration')
        if idx + 1 < len(sys.argv): version = sys.argv[idx + 1]
    
    if '--synthesis-threshold' in sys.argv:
        idx = sys.argv.index('--synthesis-threshold')
        if idx + 1 < len(sys.argv): threshold = float(sys.argv[idx + 1])

    if '--test-fallback' in sys.argv:
        idx = sys.argv.index('--test-fallback')
        if idx + 1 < len(sys.argv): test_fallback = sys.argv[idx + 1]

    retroactive_flag = '--retroactive' in sys.argv
    design_path = _find_doc('design', version) or f'docs/kjtcom-design-{version}.md'

    if not os.path.exists(design_path):
        print(f"Design doc not found: {design_path}")
        sys.exit(1)

    evaluation = evaluate_with_retry(version, design_path, threshold=threshold, verbose=verbose, test_fallback=test_fallback)
    save_scores(version, evaluation)
    suffix = "-tier2-corrected" if retroactive_flag else ""
    write_report_markdown(version, evaluation, suffix=suffix)

    print(f"\n[EVAL] Evaluator: {evaluation.get('evaluator')}")
    print(f"[EVAL] Tier: {evaluation.get('tier_used')}")
