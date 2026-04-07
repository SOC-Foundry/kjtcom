#!/usr/bin/env python3
"""Run Qwen3.5-9B evaluator with schema-validated output.

v9.49: Schema validation + retry-with-feedback loop. Evaluator reads execution
context (event log, file checks, design doc), NOT build log. Build log is an
OUTPUT of the process, not an INPUT.
"""
import json
import jsonschema
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event
from utils.ollama_config import merge_defaults

OLLAMA_URL = 'http://localhost:11434/api/chat'
SCORES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'agent_scores.json')
PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HARNESS_PATH = os.path.join(PROJECT_DIR, 'docs', 'evaluator-harness.md')
SCHEMA_PATH = os.path.join(PROJECT_DIR, 'data', 'eval_schema.json')


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
    """Build 50-80KB context package for Qwen evaluation.

    v10.63 (ADR-014): rich context is the default. Falls through to
    docs/archive/ for any iteration whose artifacts have been moved.
    """
    parts = []

    # Current iteration artifacts (build + design + plan)
    for doc_type in ["build", "design", "plan"]:
        path = _find_doc(doc_type, iteration)
        if path:
            parts.append(f"=== CURRENT {doc_type.upper()} ({iteration}) ===")
            parts.append(open(path).read())

    # Few-shot precedent reports (ADR-014 calls out v10.59 as last known good Qwen output)
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
    """Build ground-truth execution context from event log, build log, changelog, and file system.

    v10.56: Also reads build log and changelog for evidence when event log
    has no entries for this iteration (fixes G55 empty context problem).
    """
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

    # v10.56: Read build log for additional evidence
    build_log_path = os.path.join(PROJECT_DIR, 'docs', f'kjtcom-build-{version}.md')
    if os.path.exists(build_log_path):
        try:
            with open(build_log_path) as f:
                build_content = f.read()
            lines.append(f"\nBuild log ({len(build_content)} chars):")
            lines.append(build_content[:3000])
        except Exception:
            pass

    # v10.56: Read changelog for evidence of completed work
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
    """Parse design doc to extract workstream count and names.

    Supports two formats:
    1. Table: | W1 | Name | ... |
    2. Heading: ### W1: Name (Priority)
    """
    if not os.path.exists(design_doc_path):
        return 0, []

    with open(design_doc_path) as f:
        content = f.read()

    lines = content.split("\n")
    w_count = 0
    w_names = []

    # Try heading format first: ### W1: Name (P0)
    import re
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
    """Validate Qwen's JSON output against the strict eval schema.

    Returns list of error strings. Empty list means valid.
    """
    schema = load_eval_schema()
    errors = []

    validator = jsonschema.Draft7Validator(schema)
    for error in sorted(validator.iter_errors(output), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        # Build expected vs actual hint
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


def normalize_llm_output(output, expected_count, expected_names, executing_agent):
    """ADR-014 (v10.63): Coerce common LLM deviations into schema shape.

    Small models (Qwen 9B, Gemini Flash) produce rich content but routinely
    skip required scaffolding fields, use natural-language priorities, and
    return improvements as a single string. Rather than rejecting and
    retrying with tighter constraints (which v10.60-62 proved fails),
    repair the response in place.
    """
    if not isinstance(output, dict):
        return output

    # Workstreams may come back as dict keyed by W1/W2/...
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
    for i in range(expected_count):
        src = ws_raw[i] if i < len(ws_raw) and isinstance(ws_raw[i], dict) else {}
        wid = src.get("id") or f"W{i+1}"
        name = src.get("name") or (expected_names[i] if i < len(expected_names) else f"Workstream {i+1}")

        prio = str(src.get("priority", "P1")).strip().lower()
        prio = priority_map.get(prio, prio.upper() if prio.upper() in ("P0","P1","P2","P3") else "P1")

        out = str(src.get("outcome", "partial")).strip().lower()
        out = outcome_map.get(out, "partial" if out not in ("complete","partial","failed","deferred") else out)

        try:
            score = int(src.get("score", 5))
        except (TypeError, ValueError):
            score = 5
        score = max(0, min(9, score))  # schema cap is 9

        evidence = src.get("evidence", "")
        if isinstance(evidence, list):
            evidence = "; ".join(str(x) for x in evidence)
        evidence = str(evidence)[:1000]
        if len(evidence) < 10:
            evidence = f"Evaluator did not return per-workstream evidence; see build log for {wid}."

        improvements = src.get("improvements", [])
        if isinstance(improvements, str):
            # split on newlines or semicolons
            parts = [p.strip(" -•*") for p in improvements.replace("\n", ";").split(";") if p.strip()]
            improvements = parts or [improvements]
        if not isinstance(improvements, list):
            improvements = [str(improvements)]
        improvements = list(improvements)
        _pad_options = [
            "Evaluator returned fewer than two improvements; consider re-running with a richer build log.",
            "Add a unit test fixture for normalize_llm_output() covering all coercion paths.",
        ]
        while len(improvements) < 2:
            improvements.append(_pad_options[len(improvements) % 2])
        improvements = [str(x)[:500] for x in improvements][:6]

        agents = src.get("agents") or [executing_agent]
        if not isinstance(agents, list):
            agents = [str(agents)]
        llms = src.get("llms") or ["qwen3.5:9b"]
        if not isinstance(llms, list):
            llms = [str(llms)]
        mcps = src.get("mcps") or ["-"]
        if not isinstance(mcps, list):
            mcps = [str(mcps)]
        # Strip MCP enum dump
        valid_mcps = {"Firebase", "Context7", "Firecrawl", "Playwright", "Dart", "-"}
        mcps = [m for m in mcps if m in valid_mcps] or ["-"]
        mcps = mcps[:5]

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
        })

    output["workstreams"] = fixed_ws

    # Trident normalization
    trident = output.get("trident", {}) or {}
    if not isinstance(trident, dict):
        trident = {}
    cost = str(trident.get("cost", ""))[:500]
    if len(cost) < 5:
        cost = "Cost not reported by evaluator."
    delivery = str(trident.get("delivery", ""))
    import re as _re
    if not _re.match(r'^\d+/\d+ workstreams', delivery):
        completed = sum(1 for w in fixed_ws if w["outcome"] == "complete")
        delivery = f"{completed}/{expected_count} workstreams complete (normalized from '{delivery[:60]}')"
    perf = str(trident.get("performance", ""))[:500]
    if len(perf) < 10:
        perf = "Performance not reported by evaluator."
    output["trident"] = {"cost": cost, "delivery": delivery, "performance": perf}

    # Iteration / summary safety
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

    return output


def validate_qwen_output(output, expected_count, expected_names):
    """Full validation: schema + workstream count + names (fuzzy) + banned phrases + mcps logic.

    Returns list of error strings. Empty list means valid.
    """
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
            
            # Normalize common delimiters: em-dash, en-dash, hyphen, colon
            def normalize_name(s):
                s = s.replace("—", " ").replace("–", " ").replace("-", " ").replace(":", " ")
                return " ".join(s.split()) # normalize whitespace

            expected_norm = normalize_name(expected)
            actual_norm = normalize_name(actual)
            
            # Check if one is a substring of another or they share significant words
            if expected_norm not in actual_norm and actual_norm not in expected_norm:
                # Check for word overlap (at least 2 significant words)
                expected_words = set(w for w in expected_norm.split() if len(w) > 3)
                actual_words = set(w for w in actual_norm.split() if len(w) > 3)
                overlap = expected_words.intersection(actual_words)
                
                if not overlap:
                    errors.append(
                        f"W{i+1} name mismatch: got '{actual}', expected '{expected}'"
                    )

        # Check for full MCP enum dump
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
    """Call Qwen via Ollama and return parsed response + token info."""
    payload = merge_defaults({
        'model': 'qwen3.5:9b',
        'messages': messages,
    }, evaluation=True)

    start_time = time.time()
    # v10.63: rich context bundle can exceed argv limits. Pipe via stdin.
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
    # Strip markdown fences
    raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^```\s*$', '', raw, flags=re.MULTILINE)
    # Fix trailing commas before } or ]
    raw = re.sub(r',\s*([}\]])', r'\1', raw)
    # Strip leading/trailing whitespace
    return raw.strip()


def parse_json_from_response(content):
    """Extract JSON object from Qwen response text."""
    if not content:
        return None

    content = repair_json(content)

    # Try object first (new schema format)
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        try:
            return json.loads(content[json_start:json_end])
        except json.JSONDecodeError:
            pass

    return None


def call_gemini_flash(prompt):
    """Call Gemini Flash via litellm for evaluator fallback.

    Returns (content_string, tokens_dict, latency_ms) or (None, {}, 0).
    """
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
            max_tokens=2048,
        )
        latency = int((time.time() - start_time) * 1000)
        content = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens or 0,
            'eval_tokens': response.usage.completion_tokens or 0,
            'total_tokens': response.usage.total_tokens or 0,
        }
        return content, tokens, latency
    except Exception as e:
        print(f"[EVAL] Gemini Flash call failed: {e}")
        return None, {}, 0


def generate_self_eval(build_log, design_doc, version, expected_names):
    """Generate a self-evaluation when all LLM evaluators fail.

    Parses the build log and design doc to produce an honest evaluation.
    Caps all scores at 7/10 to avoid self-grading bias.
    """
    import re

    workstreams = []
    for i, name in enumerate(expected_names):
        # Check build log for evidence of this workstream
        w_tag = f"W{i+1}"
        evidence_lines = []
        # Match W-tags, workstream names, and section headings (### W1: or ## W1:)
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

        # Determine priority from design doc
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
            "agents": ["claude-code"],
            "llms": ["qwen3.5:9b"],
            "mcps": ["-"],
            "score": min(score, 7),
            "improvements": [
                "Self-eval fallback used - Qwen and Gemini both failed schema validation",
                "Manual review recommended for accurate scoring"
            ]
        })

    total = len(expected_names)
    completed = sum(1 for ws in workstreams if ws['outcome'] == 'complete')

    return {
        "iteration": version,
        "summary": f"Self-evaluation fallback for {version}. Qwen and Gemini Flash both failed schema validation. {total} workstreams parsed from design doc. Scores capped at 7/10 to avoid self-grading bias.",
        "workstreams": workstreams,
        "trident": {
            "cost": "Minimal - self-eval required no LLM tokens",
            "delivery": f"{completed}/{total} workstreams completed (self-eval)",
            "performance": "Self-eval fallback triggered - evaluator pipeline needs repair"
        },
        "what_could_be_better": [
            "Qwen failed schema validation after 3 attempts - prompt or model issue",
            "Gemini Flash failed schema validation after 2 attempts - schema may be too strict",
            "Self-eval cannot provide the same quality as an independent evaluator"
        ]
    }


def build_evaluator_prompt(version, rich_context, expected_count, expected_names, executing_agent):
    """Build the shared evaluator prompt with rich context (v10.59)."""
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


def try_qwen_tier(base_prompt, harness, expected_count, expected_names, executing_agent, version, verbose=False):
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
            current_prompt = base_prompt + "\n\nERROR: Your response was not valid JSON. Return ONLY a JSON object, no markdown fences, no explanation."
            continue

        # ADR-014 normalization: coerce common deviations BEFORE validation.
        try:
            parsed = normalize_llm_output(parsed, expected_count, expected_names, executing_agent)
            errors = validate_qwen_output(parsed, expected_count, expected_names)
        except (AttributeError, TypeError) as e:
            errors = [f"Malformed workstream structure: {e}"]

        if not errors:
            print(f"[EVAL] Qwen schema validation passed on attempt {attempt + 1}")
            parsed['evaluator_tokens'] = tokens
            parsed['evaluator'] = 'qwen3.5:9b'
            parsed['tier_used'] = 'qwen'
            parsed['self_graded'] = False
            for ws in parsed.get('workstreams', []):
                print(f"  {ws['id']}: {ws['name']} - {ws['score']}/10 ({ws['outcome']})")
            return parsed

        print(f"[EVAL] Qwen validation failed attempt {attempt + 1} with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")

        feedback = "\n\nVALIDATION ERRORS - fix EVERY error below before retrying:\n"
        for i, err in enumerate(errors, 1):
            feedback += f"  {i}. {err}\n"
        feedback += "\nCritical reminders:"
        feedback += "\n  - score: integer 0-9 (NEVER 10)"
        feedback += "\n  - mcps: only from [\"Firebase\", \"Context7\", \"Firecrawl\", \"Playwright\", \"Dart\", \"-\"]"
        feedback += f"\n  - workstreams: exactly {expected_count} objects"
        feedback += f"\n  - agents: must include [\"{executing_agent}\"]"
        feedback += "\nReturn ONLY the corrected JSON object."
        current_prompt = base_prompt + feedback

    return None


def try_gemini_tier(base_prompt, expected_count, expected_names, verbose=False):
    """Tier 2: Gemini Flash via litellm (2 attempts)."""
    current_prompt = base_prompt

    for attempt in range(2):
        print(f"\n[EVAL] Gemini Flash attempt {attempt + 1}/2 (Qwen fallback)...")

        content, tokens, latency = call_gemini_flash(current_prompt)

        if verbose and content:
            print(f"[EVAL] Gemini raw response (first 500 chars): {content[:500]}")

        if not content:
            print("[EVAL] Gemini Flash returned empty response")
            continue

        parsed = parse_json_from_response(content)
        if parsed is None:
            current_prompt = base_prompt + "\n\nERROR: Not valid JSON. Return ONLY a JSON object."
            continue

        # ADR-014 normalization (Gemini path).
        # Gemini Flash needs an executing_agent reference; pull it from the closure.
        try:
            parsed = normalize_llm_output(parsed, expected_count, expected_names, "claude-code")
            errors = validate_qwen_output(parsed, expected_count, expected_names)
        except (AttributeError, TypeError) as e:
            errors = [f"Malformed workstream structure: {e}"]

        if not errors:
            print(f"[EVAL] Gemini Flash schema validation passed on attempt {attempt + 1}")
            parsed['evaluator_tokens'] = tokens
            parsed['evaluator'] = 'gemini-flash (qwen-fallback)'
            parsed['tier_used'] = 'gemini-flash'
            parsed['self_graded'] = False
            for ws in parsed.get('workstreams', []):
                print(f"  {ws['id']}: {ws['name']} - {ws['score']}/10 ({ws['outcome']})")
            return parsed

        print(f"[EVAL] Gemini validation failed attempt {attempt + 1} with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")

        feedback = "\n\nVALIDATION ERRORS:\n"
        for i, err in enumerate(errors, 1):
            feedback += f"  {i}. {err}\n"
        feedback += "\nReturn ONLY the corrected JSON object."
        current_prompt = base_prompt + feedback

    return None


def evaluate_with_retry(version, design_doc_path, max_retries=3, verbose=False, test_fallback=None):
    """Three-tier evaluator fallback chain (v10.56).

    Tier 1: Qwen3.5-9B via Ollama (3 attempts)
    Tier 2: Gemini Flash via litellm (2 attempts)
    Tier 3: Self-eval (always succeeds, scores capped at 7/10)
    """
    expected_count, expected_names = parse_workstream_count(design_doc_path)
    executing_agent = parse_executing_agent(design_doc_path)
    print(f"[EVAL] Expecting {expected_count} workstreams: {', '.join(expected_names)}")
    print(f"[EVAL] Executing agent: {executing_agent}")

    with open(design_doc_path) as f:
        design_content = f.read()

    rich_context = build_rich_context(version)
    if verbose:
        print(f"[EVAL] Rich context ({len(rich_context)} chars):")
        print(rich_context[:1000])

    harness = load_harness()

    base_prompt = build_evaluator_prompt(
        version, rich_context, expected_count,
        expected_names, executing_agent
    )

    # Tier 1: Qwen (skip if testing fallback)
    if test_fallback not in ('gemini', 'self-eval'):
        result = try_qwen_tier(base_prompt, harness, expected_count, expected_names, executing_agent, version, verbose)
        if result:
            return result
        print("[EVAL] Qwen tier exhausted. Falling through to Gemini Flash.")
    else:
        print(f"[EVAL] Skipping Qwen tier (--test-fallback {test_fallback})")

    # Tier 2: Gemini Flash (skip if testing self-eval)
    if test_fallback != 'self-eval':
        result = try_gemini_tier(base_prompt, expected_count, expected_names, verbose)
        if result:
            return result
        print("[EVAL] Gemini tier exhausted. Falling through to self-eval.")
    else:
        print("[EVAL] Skipping Gemini tier (--test-fallback self-eval)")

    # Tier 3: Self-eval (always succeeds; ADR-015 hard-caps scores at 7/10)
    print("[EVAL] Generating self-eval (Qwen + Gemini fallback). ADR-015 cap active.")
    build_log = ""
    # v10.63: include archive fallback (mid-reorg)
    for build_log_candidate in [
        os.path.join(PROJECT_DIR, 'docs', f'kjtcom-build-{version}.md'),
        os.path.join(PROJECT_DIR, 'docs', 'archive', f'kjtcom-build-{version}.md'),
        os.path.join(PROJECT_DIR, 'docs', 'drafts', f'kjtcom-build-{version}.md'),
    ]:
        if os.path.exists(build_log_candidate):
            with open(build_log_candidate) as f:
                build_log = f.read()
            print(f"[EVAL] Build log found: {build_log_candidate} ({len(build_log)} chars)")
            break
    if not build_log:
        print(f"[EVAL] WARNING: No build log found for {version} in docs/, docs/archive/ or docs/drafts/")

    result = generate_self_eval(build_log, design_content, version, expected_names)
    result['evaluator'] = 'self-eval (fallback)'
    result['evaluator_tokens'] = {}
    result['tier_used'] = 'self-eval'
    result['self_graded'] = True
    # ADR-015 enforcement: cap any score > 7 and preserve raw
    for ws in result.get('workstreams', []):
        if ws.get('score', 0) > 7:
            ws['raw_self_grade'] = ws['score']
            ws['score'] = 7
            ws['score_note'] = 'Self-grading cap applied (ADR-015)'
    return result


def write_report_markdown(version, evaluation, suffix=""):
    """Write the evaluation report as a markdown file.

    suffix: optional filename suffix (e.g. "-qwen") for retroactive runs that
    must not overwrite the original self-graded report.
    """
    report_path = os.path.join(PROJECT_DIR, 'docs', f'kjtcom-report-{version}{suffix}.md')
    evaluator = evaluation.get('evaluator', 'unknown')
    lines = []
    lines.append(f"# kjtcom - Report v{version.replace('v','')}")
    lines.append(f"")
    lines.append(f"**Evaluator:** {evaluator}")
    lines.append(f"**Date:** {time.strftime('%B %d, %Y')}")
    lines.append(f"")
    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(evaluation.get('summary', 'No summary available.'))
    lines.append(f"")
    lines.append(f"## Workstream Scores")
    lines.append(f"")
    lines.append(f"| # | Workstream | Priority | Outcome | Score | Evidence |")
    lines.append(f"|---|-----------|----------|---------|-------|----------|")
    for ws in evaluation.get('workstreams', []):
        lines.append(f"| {ws.get('id','?')} | {ws.get('name','?')} | {ws.get('priority','?')} | {ws.get('outcome','?')} | {ws.get('score',0)}/10 | {ws.get('evidence','')[:80]} |")
    lines.append(f"")
    lines.append(f"## Trident")
    lines.append(f"")
    trident = evaluation.get('trident', {})
    lines.append(f"- **Cost:** {trident.get('cost', 'N/A')}")
    lines.append(f"- **Delivery:** {trident.get('delivery', 'N/A')}")
    lines.append(f"- **Performance:** {trident.get('performance', 'N/A')}")
    lines.append(f"")
    lines.append(f"## What Could Be Better")
    lines.append(f"")
    for item in evaluation.get('what_could_be_better', []):
        lines.append(f"- {item}")
    lines.append(f"")
    lines.append(f"## Workstream Details")
    lines.append(f"")
    for ws in evaluation.get('workstreams', []):
        lines.append(f"### {ws.get('id','?')}: {ws.get('name','?')}")
        lines.append(f"- **Agents:** {', '.join(ws.get('agents', []))}")
        lines.append(f"- **LLMs:** {', '.join(ws.get('llms', []))}")
        lines.append(f"- **MCPs:** {', '.join(ws.get('mcps', []))}")
        lines.append(f"- **Improvements:**")
        for imp in ws.get('improvements', []):
            lines.append(f"  - {imp}")
        lines.append(f"")
    lines.append(f"---")
    lines.append(f"*Report {version}, {time.strftime('%B %d, %Y')}. Evaluator: {evaluator}.*")

    with open(report_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"[EVAL] Report written to {report_path}")
    return report_path


def save_scores(version, evaluation):
    """Save evaluation result to agent_scores.json (canonical iterations wrapper)."""
    try:
        with open(SCORES_PATH) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Handle legacy flat array format
    if isinstance(data, list):
        data = {'iterations': data}
    if 'iterations' not in data:
        data['iterations'] = []

    iterations = data['iterations']

    # Update existing entry or append
    found = False
    for entry in iterations:
        if entry.get('iteration') == version:
            entry.update(evaluation)
            found = True
            break

    if not found:
        evaluation['date'] = time.strftime('%Y-%m-%d')
        iterations.append(evaluation)

    with open(SCORES_PATH, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Evaluation saved to {SCORES_PATH} ({len(iterations)} entries)")


if __name__ == '__main__':
    version = 'v9.49'
    verbose = '--verbose' in sys.argv
    test_fallback = None

    if '--iteration' in sys.argv:
        idx = sys.argv.index('--iteration')
        if idx + 1 < len(sys.argv):
            version = sys.argv[idx + 1]
    elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        version = sys.argv[1]

    if '--test-fallback' in sys.argv:
        idx = sys.argv.index('--test-fallback')
        if idx + 1 < len(sys.argv):
            test_fallback = sys.argv[idx + 1]
            if test_fallback not in ('gemini', 'self-eval'):
                print(f"Invalid --test-fallback value: {test_fallback}")
                print("Valid values: gemini, self-eval")
                sys.exit(1)

    # v10.63: --rich-context (no-op flag, default behavior since v10.59) and
    # --retroactive (allows running against an archived iteration). Both accepted
    # for plan parity. Rich context is always built; retroactive routes through
    # the archive fallback already added to _find_doc().
    rich_context_flag = '--rich-context' in sys.argv  # accepted, default behavior
    retroactive_flag = '--retroactive' in sys.argv

    design_path = _find_doc('design', version) or f'docs/kjtcom-design-{version}.md'

    if not os.path.exists(design_path):
        print(f"Design doc not found: {design_path}")
        sys.exit(1)
    if retroactive_flag:
        print(f"[EVAL] Retroactive mode for {version}; design at {design_path}")

    # Three-tier evaluator fallback chain (v10.56)
    # Qwen (3 attempts) -> Gemini Flash (2 attempts) -> self-eval (always succeeds)
    evaluation = evaluate_with_retry(version, design_path, verbose=verbose, test_fallback=test_fallback)
    save_scores(version, evaluation)
    # Retroactive runs write to a -qwen suffix so the original report is preserved.
    suffix = "-qwen" if retroactive_flag else ""
    write_report_markdown(version, evaluation, suffix=suffix)

    evaluator = evaluation.get('evaluator', 'unknown')
    print(f"\n[EVAL] Evaluator: {evaluator}")
    print(f"[EVAL] Tokens: prompt={evaluation.get('evaluator_tokens', {}).get('prompt_tokens', 0)}, "
          f"eval={evaluation.get('evaluator_tokens', {}).get('eval_tokens', 0)}, "
          f"total={evaluation.get('evaluator_tokens', {}).get('total_tokens', 0)}")
