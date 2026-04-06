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
SCORES_PATH = 'agent_scores.json'
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
    """Build ground-truth execution context from event log and file system.

    Evaluator reads execution context, NOT build log.
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
        return "\n".join(lines)

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

    # Check key file existence
    key_files = [
        'scripts/run_evaluator.py',
        'scripts/generate_artifacts.py',
        'data/eval_schema.json',
        'CLAUDE.md',
        'GEMINI.md',
        'docs/kjtcom-changelog.md',
        'app/web/architecture.html',
        'app/web/claw3d.html',
        'app/lib/widgets/mw_tab.dart',
    ]
    lines.append("Key file existence:")
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
    """Parse design doc to extract workstream table and count W# rows."""
    if not os.path.exists(design_doc_path):
        return 0, []

    with open(design_doc_path) as f:
        content = f.read()

    lines = content.split("\n")
    w_count = 0
    w_names = []
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

    try:
        jsonschema.validate(output, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema error at {e.json_path}: {e.message}")

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


def build_fallback(version, expected_names):
    """Build a minimal valid fallback response when all retries fail."""
    workstreams = []
    for i, name in enumerate(expected_names):
        workstreams.append({
            "id": f"W{i+1}",
            "name": name,
            "priority": "P1" if i < 2 else ("P2" if i < 4 else "P3"),
            "outcome": "partial",
            "evidence": "Evaluation generated via fallback due to schema validation failure",
            "agents": ["claude-code"],
            "llms": ["qwen3.5:9b"],
            "mcps": ["-"],
            "score": 5,
            "improvements": [
                "Schema validation failed - manual review needed",
                "Qwen output did not conform after 3 attempts"
            ]
        })

    total = len(expected_names)
    return {
        "iteration": version,
        "summary": "Evaluation generated via fallback due to schema validation failure after 3 attempts.",
        "workstreams": workstreams,
        "trident": {
            "cost": "Within target - local Ollama inference",
            "delivery": f"0/{total} workstreams verified (fallback)",
            "performance": "Qwen schema compliance failed after 3 attempts"
        },
        "what_could_be_better": [
            "Qwen output did not conform to eval_schema.json after 3 retries",
            "Consider adjusting prompt structure for better schema compliance",
            "Manual evaluation may be needed for this iteration"
        ]
    }


def evaluate_with_retry(version, design_doc_path, max_retries=3):
    """Call Qwen, validate against schema, retry with specific feedback on failure.

    This is the core v9.49 schema-validated evaluation loop.
    """
    expected_count, expected_names = parse_workstream_count(design_doc_path)
    executing_agent = parse_executing_agent(design_doc_path)
    print(f"Expecting {expected_count} workstreams: {', '.join(expected_names)}")
    print(f"Executing agent parsed as: {executing_agent}")

    with open(design_doc_path) as f:
        design_content = f.read()

    exec_context = build_execution_context(version)

    gotchas = load_gotcha_archive()
    gotcha_summary = ""
    if gotchas:
        recent = [g for g in gotchas if g.get('iteration_resolved', '').startswith('v9.')]
        if recent:
            gotcha_summary = "\nRecently resolved gotchas:\n" + "\n".join(
                f"  {g['id']}: {g['description']} (resolved {g['iteration_resolved']})"
                for g in recent[:5]
            )

    harness = load_harness()

    # Build workstream list for prompt
    ws_list_str = "\n".join(f"  W{i+1}: {name}" for i, name in enumerate(expected_names))

    base_prompt = f"""/no_think
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

    current_prompt = base_prompt

    for attempt in range(max_retries):
        print(f"\nEvaluation attempt {attempt + 1}/{max_retries}...")

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

        if not content:
            current_prompt = base_prompt + "\n\nERROR: Empty response. Return ONLY a JSON object."
            continue

        parsed = parse_json_from_response(content)
        if parsed is None:
            current_prompt = base_prompt + "\n\nERROR: Your response was not valid JSON. Return ONLY a JSON object, no markdown fences, no explanation."
            continue

        errors = validate_qwen_output(parsed, expected_count, expected_names)

        if not errors:
            print(f"Schema validation passed on attempt {attempt + 1}")
            parsed['evaluator_tokens'] = tokens
            for ws in parsed.get('workstreams', []):
                print(f"  {ws['id']}: {ws['name']} - {ws['score']}/9 ({ws['outcome']})")
            return parsed

        print(f"Validation failed on attempt {attempt + 1} with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")

        # Build specific feedback for retry
        feedback = "\n\nVALIDATION ERRORS (fix all before retrying):\n"
        for err in errors:
            feedback += f"  - {err}\n"
        feedback += "\nReturn the corrected JSON object. Remember: score max is 9, not 10."
        current_prompt = base_prompt + feedback

    # All retries exhausted - use fallback
    print(f"Max retries ({max_retries}) exhausted. Using fallback.")
    fallback = build_fallback(version, expected_names)
    fallback['evaluator_tokens'] = tokens if tokens else {}
    return fallback


def save_scores(version, evaluation):
    """Save evaluation result to agent_scores.json."""
    try:
        with open(SCORES_PATH) as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    # Update existing entry or append
    found = False
    for entry in scores:
        if entry.get('iteration') == version:
            entry.update(evaluation)
            found = True
            break

    if not found:
        evaluation['date'] = time.strftime('%Y-%m-%d')
        scores.append(evaluation)

    with open(SCORES_PATH, 'w') as f:
        json.dump(scores, f, indent=2)

    print(f"Evaluation saved to {SCORES_PATH}")


if __name__ == '__main__':
    version = 'v9.49'

    if '--iteration' in sys.argv:
        idx = sys.argv.index('--iteration')
        if idx + 1 < len(sys.argv):
            version = sys.argv[idx + 1]
    elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        version = sys.argv[1]

    design_path = f'docs/kjtcom-design-{version}.md'

    if not os.path.exists(design_path):
        print(f"Design doc not found: {design_path}")
        sys.exit(1)

    # Schema-validated evaluation (v9.49+)
    # Evaluator reads design doc + event log + file checks, NOT build log
    evaluation = evaluate_with_retry(version, design_path)
    save_scores(version, evaluation)

    print(f"\nTokens: prompt={evaluation.get('evaluator_tokens', {}).get('prompt_tokens', 0)}, "
          f"eval={evaluation.get('evaluator_tokens', {}).get('eval_tokens', 0)}, "
          f"total={evaluation.get('evaluator_tokens', {}).get('total_tokens', 0)}")
