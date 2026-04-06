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


def validate_qwen_output(output, expected_count, expected_names):
    """Full validation: schema + workstream count + names + banned phrases + mcps logic.

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

    # 3. Workstream name matching
    full_enum = ["Firebase", "Context7", "Firecrawl", "Playwright", "Dart", "-"]
    for i, ws in enumerate(ws_list):
        if i < len(expected_names):
            expected = expected_names[i]
            actual = ws.get("name", "")
            if actual.lower() != expected.lower():
                errors.append(
                    f"W{i+1} name mismatch: got '{actual}', expected '{expected}'"
                )
        
        # Check for full MCP enum dump
        mcps = ws.get("mcps", [])
        if len(mcps) >= 5 and all(m in mcps for m in ["Firebase", "Firecrawl", "Dart"]):
             errors.append(f"W{i+1}: Do NOT dump all MCPs. List ONLY the {len(mcps)} used.")

    # 4. Banned phrase check
    text = json.dumps(output)
    banned = ["successfully deployed", "robust validation", "clean release",
              "strategic shift", "healthy system", "Review...", "TBD"]
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
    result = subprocess.run(
        ['curl', '-s', OLLAMA_URL, '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=180
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


def parse_json_from_response(content):
    """Extract JSON object from Qwen response text."""
    if not content:
        return None

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
        for line in build_log.split('\n'):
            if w_tag in line or name.lower() in line.lower():
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


def build_evaluator_prompt(version, design_content, exec_context, expected_count, expected_names, executing_agent, gotcha_summary=""):
    """Build the shared evaluator prompt used by all tiers."""
    ws_list_str = "\n".join(f"  W{i+1}: {name}" for i, name in enumerate(expected_names))

    return f"""/no_think
You are evaluating workstreams for kjtcom iteration {version}.

IMPORTANT: Return a single JSON OBJECT (not array) conforming to the eval_schema.json schema.

The JSON object MUST have these top-level keys:
- "iteration": "{version}"
- "summary": "Plain text summary. 2-4 sentences describing what was built and what failed. NO JSON."
- "workstreams": array of exactly {expected_count} objects
- "trident": object with "cost", "delivery", "performance"
- "what_could_be_better": array of 3+ strings

Each workstream object MUST have: id, name, priority, outcome, evidence, agents, llms, mcps, score, improvements

CONSTRAINTS:
- agents: MUST include ["{executing_agent}"]. You are NOT the agent.
- score: integer 0-9 (NEVER 10)
- outcome: one of "complete", "partial", "failed", "deferred"
- priority: one of "P0", "P1", "P2", "P3"
- mcps: array of strings from ONLY: "Firebase", "Context7", "Firecrawl", "Playwright", "Dart", "-"
- improvements: array of 2+ strings per workstream
- evidence: string of 10+ characters with file path, command output, or test result
- delivery in trident: must match pattern "X/Y workstreams..."
- what_could_be_better: 3+ concrete suggestions

WORKSTREAMS TO EVALUATE (exactly {expected_count}):
{ws_list_str}

Use the EXECUTION CONTEXT as ground truth. If errors/timeouts exist for a workstream, do NOT mark "complete".

Design document (first 3000 chars):
{design_content[:3000]}

EXECUTION CONTEXT (ground truth):
{exec_context}
{gotcha_summary}

Return ONLY the JSON object, no explanation."""


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

        errors = validate_qwen_output(parsed, expected_count, expected_names)

        if not errors:
            print(f"[EVAL] Qwen schema validation passed on attempt {attempt + 1}")
            parsed['evaluator_tokens'] = tokens
            parsed['evaluator'] = 'qwen3.5:9b'
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

        errors = validate_qwen_output(parsed, expected_count, expected_names)

        if not errors:
            print(f"[EVAL] Gemini Flash schema validation passed on attempt {attempt + 1}")
            parsed['evaluator_tokens'] = tokens
            parsed['evaluator'] = 'gemini-flash (qwen-fallback)'
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

    exec_context = build_execution_context(version)
    if verbose:
        print(f"[EVAL] Execution context ({len(exec_context)} chars):")
        print(exec_context[:1000])

    gotchas = load_gotcha_archive()
    gotcha_summary = ""
    if gotchas:
        recent = [g for g in gotchas if g.get('iteration_resolved', '').startswith(('v9.', 'v10.'))]
        if recent:
            gotcha_summary = "\nRecently resolved gotchas:\n" + "\n".join(
                f"  {g['id']}: {g['description']} (resolved {g['iteration_resolved']})"
                for g in recent[:5]
            )

    harness = load_harness()

    base_prompt = build_evaluator_prompt(
        version, design_content, exec_context, expected_count,
        expected_names, executing_agent, gotcha_summary
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

    # Tier 3: Self-eval (always succeeds)
    print("[EVAL] Generating self-eval (Qwen + Gemini fallback).")
    build_log_path = os.path.join(PROJECT_DIR, 'docs', f'kjtcom-build-{version}.md')
    build_log = ""
    if os.path.exists(build_log_path):
        with open(build_log_path) as f:
            build_log = f.read()

    result = generate_self_eval(build_log, design_content, version, expected_names)
    result['evaluator'] = 'self-eval (fallback)'
    result['evaluator_tokens'] = {}
    return result


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

    design_path = f'docs/kjtcom-design-{version}.md'

    if not os.path.exists(design_path):
        print(f"Design doc not found: {design_path}")
        sys.exit(1)

    # Three-tier evaluator fallback chain (v10.56)
    # Qwen (3 attempts) -> Gemini Flash (2 attempts) -> self-eval (always succeeds)
    evaluation = evaluate_with_retry(version, design_path, verbose=verbose, test_fallback=test_fallback)
    save_scores(version, evaluation)

    evaluator = evaluation.get('evaluator', 'unknown')
    print(f"\n[EVAL] Evaluator: {evaluator}")
    print(f"[EVAL] Tokens: prompt={evaluation.get('evaluator_tokens', {}).get('prompt_tokens', 0)}, "
          f"eval={evaluation.get('evaluator_tokens', {}).get('eval_tokens', 0)}, "
          f"total={evaluation.get('evaluator_tokens', {}).get('total_tokens', 0)}")
