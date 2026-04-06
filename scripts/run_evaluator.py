#!/usr/bin/env python3
"""Run Qwen3.5-9B evaluator against a build log. v2: with token tracking + P3 logging."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event
from utils.ollama_config import merge_defaults

OLLAMA_URL = 'http://localhost:11434/api/chat'
SCORES_PATH = 'agent_scores.json'
HARNESS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'evaluator-harness.md')


def load_harness():
    """Load evaluator harness as system prompt prefix."""
    try:
        with open(HARNESS_PATH) as f:
            return f.read()
    except FileNotFoundError:
        print(f"WARNING: Evaluator harness not found at {HARNESS_PATH}")
        return ""


def run_evaluator(version, build_log_path, active_gotchas):
    with open(build_log_path) as f:
        build_log = f.read()

    with open('docs/archive/evaluator-prompt.md') as f:
        prompt_template = f.read()

    prompt = '/no_think\n' + (prompt_template
        .replace('{version}', version)
        .replace('{active_gotchas}', active_gotchas)
        .replace('{build_log_content}', build_log[:4000]))

    harness = load_harness()
    messages = []
    if harness:
        messages.append({'role': 'system', 'content': harness})
    messages.append({'role': 'user', 'content': prompt})

    payload = merge_defaults({
        'model': 'qwen3.5:9b',
        'messages': messages,
    }, evaluation=True)

    start_time = time.time()
    result = subprocess.run(
        ['curl', '-s', OLLAMA_URL, '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=180
    )

    response = json.loads(result.stdout)
    content = response['message']['content']
    latency = int((time.time() - start_time) * 1000)

    # Token tracking from Ollama response metadata
    tokens = {
        'prompt_tokens': response.get('prompt_eval_count', 0),
        'eval_tokens': response.get('eval_count', 0),
        'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
    }

    log_event("llm_call", "qwen3.5-9b", "qwen3.5:9b", "evaluate",
              input_summary=prompt[:200],
              output_summary=content[:200],
              tokens={"prompt": tokens['prompt_tokens'], "eval": tokens['eval_tokens'],
                      "total": tokens['total_tokens']},
              latency_ms=latency,
              status="success" if content.strip() else "empty_response")

    print(f'Tokens: prompt={tokens["prompt_tokens"]}, '
          f'eval={tokens["eval_tokens"]}, '
          f'total={tokens["total_tokens"]}')

    # Extract JSON from response
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        json_str = content[json_start:json_end]
        try:
            parsed = json.loads(json_str)
            # Inject token tracking into each score entry
            if 'scores' in parsed:
                for score in parsed['scores']:
                    if 'prompt_tokens' not in score:
                        score['prompt_tokens'] = 0
                        score['eval_tokens'] = 0
                        score['total_tokens'] = 0
            # Add evaluator token usage
            parsed['evaluator_tokens'] = tokens
            print(json.dumps(parsed, indent=2))
            return parsed, tokens
        except json.JSONDecodeError:
            pass

    print("RAW RESPONSE:")
    print(content)
    return None, tokens


def append_to_scores(entry, tokens):
    """Append evaluation entry to agent_scores.json with token tracking."""
    try:
        with open(SCORES_PATH) as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    if entry:
        # Add token tracking to the entry
        entry['evaluator_tokens'] = tokens
        scores.append(entry)
    else:
        # Minimal entry if parse failed
        scores.append({
            'iteration': 'unknown',
            'date': time.strftime('%Y-%m-%d'),
            'evaluator': 'qwen3.5:9b',
            'scores': [],
            'gotcha_events': [],
            'evaluator_tokens': tokens,
            'error': 'Failed to parse Qwen response'
        })

    with open(SCORES_PATH, 'w') as f:
        json.dump(scores, f, indent=2)

    print(f'\nAppended to {SCORES_PATH}')


def load_gotcha_archive():
    """Load resolved gotchas for evaluator context."""
    archive_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gotcha_archive.json')
    try:
        with open(archive_path) as f:
            data = json.load(f)
        return data.get('resolved_gotchas', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def build_execution_context(version):
    """Build ground-truth execution context from event log and file system.

    Returns a string describing what actually happened during execution.
    """
    project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    event_log_path = os.path.join(project_dir, 'data', 'iao_event_log.jsonl')

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

    # Summarize events
    errors = [e for e in events if e.get('status') in ('error', 'timeout')]
    successes = [e for e in events if e.get('status') == 'success']
    lines.append(f"Total events: {len(events)}, successes: {len(successes)}, errors/timeouts: {len(errors)}")

    if errors:
        lines.append("Errors/timeouts:")
        for e in errors[:10]:
            lines.append(f"  - {e.get('source_agent', '?')}: {e.get('action', '?')} -> {e.get('status')} ({e.get('error', 'N/A')[:80]})")

    # Check key file existence
    key_files = [
        'scripts/enrich_counties.py',
        'kjtcom-telegram-bot.service',
        'data/gotcha_archive.json',
        'data/middleware_registry.json',
        'scripts/post_flight.py',
        'scripts/build_architecture_html.py',
        'app/web/architecture.html',
        'data/schema_reference.json',
    ]
    lines.append("Key file existence:")
    for kf in key_files:
        full = os.path.join(project_dir, kf)
        lines.append(f"  {'EXISTS' if os.path.exists(full) else 'MISSING'}: {kf}")

    return "\n".join(lines)


def run_workstream_evaluator(version, design_doc_path):
    """Score individual workstreams from the design doc.

    Reads workstream definitions from design doc, asks Qwen to score each one,
    returns list of workstream score dicts for agent_scores.json.
    v9.42: includes execution context for ground-truth cross-check.
    """
    try:
        with open(design_doc_path) as f:
            design_content = f.read()
    except FileNotFoundError:
        print(f"Design doc not found: {design_doc_path}")
        return []

    # Build execution context for ground-truth scoring
    exec_context = build_execution_context(version)

    # Load gotcha archive for context
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

    prompt = f"""/no_think
You are evaluating workstreams for kjtcom iteration {version}.

IMPORTANT: Use the EXECUTION CONTEXT below as ground truth. If the execution context
shows errors/timeouts for a workstream, do NOT mark it as "complete". If files exist
that a workstream was supposed to create, that is evidence of completion.

MANDATORY RULES:
1. Include specific numbers from the event log and execution output. NEVER write "TBD", "Review...", or "Verify...". State the actual measured value.
2. The ONLY valid MCP servers are: Firebase, Context7, Firecrawl, Playwright, Dart. If a workstream did not use an MCP, write "-" in the mcps field. Do NOT invent MCP server names.
3. The "evidence" field MUST contain a file path, command output, or test result that proves the outcome. "Complete" without evidence is reclassified as "unverified".
4. Event counts in your response must match the execution context exactly.
5. Do not use corporate language like "delivered a successful deployment." State what was built and what it does.
6. Use the EXACT workstream names from the design doc W# labels. Do not rename, reorder, or combine workstreams.
7. TRIDENT VALUES: Cost must state actual token count or "within target"/"exceeded target". Delivery must state "X/Y workstreams complete". Performance must state the specific metric result. "Review..." is equivalent to "TBD" and is BANNED.

Based on the design document and execution context, score each workstream (W1-W6).
Return ONLY a JSON array of objects with these fields:
- id: "W1", "W2", etc.
- name: workstream name
- priority: "P1", "P2", or "P3"
- outcome: "complete", "partial", "failed", or "deferred"
- evidence: file path, command output, or test result proving outcome
- agents: list of agent names used (e.g. ["claude-code"])
- llms: list of LLM models used (e.g. ["gemini-2.5-flash"])
- mcps: list of MCP servers used, or ["-"] if none. ONLY valid values: Firebase, Context7, Firecrawl, Playwright, Dart
- score: 0-10 integer
- notes: one sentence summary with specific numbers (entity counts, file counts, etc.)

Design document (first 3000 chars):
{design_content[:3000]}

EXECUTION CONTEXT (ground truth):
{exec_context}
{gotcha_summary}

Return ONLY the JSON array, no explanation."""

    ws_messages = []
    if harness:
        ws_messages.append({'role': 'system', 'content': harness})
    ws_messages.append({'role': 'user', 'content': prompt})

    payload = merge_defaults({
        'model': 'qwen3.5:9b',
        'messages': ws_messages,
    }, evaluation=True)

    start_time = time.time()
    result = subprocess.run(
        ['curl', '-s', OLLAMA_URL, '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=180
    )

    response = json.loads(result.stdout)
    content = response['message']['content']
    latency = int((time.time() - start_time) * 1000)

    tokens = {
        'prompt_tokens': response.get('prompt_eval_count', 0),
        'eval_tokens': response.get('eval_count', 0),
        'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
    }

    log_event("llm_call", "qwen3.5-9b", "qwen3.5:9b", "evaluate-workstreams",
              input_summary=prompt[:200],
              output_summary=content[:200],
              tokens={"prompt": tokens['prompt_tokens'], "eval": tokens['eval_tokens'],
                      "total": tokens['total_tokens']},
              latency_ms=latency,
              status="success" if content.strip() else "empty_response")

    # Parse JSON array from response
    json_start = content.find('[')
    json_end = content.rfind(']') + 1
    if json_start >= 0 and json_end > json_start:
        try:
            workstreams = json.loads(content[json_start:json_end])
            print(f"Workstream scores ({len(workstreams)} workstreams):")
            for ws in workstreams:
                print(f"  {ws.get('id', '?')}: {ws.get('name', '?')} - {ws.get('score', '?')}/10 ({ws.get('outcome', '?')})")
            return workstreams
        except json.JSONDecodeError:
            pass

    print("Failed to parse workstream scores from Qwen response.")
    print(f"Raw: {content[:500]}")
    return []


def append_workstreams_to_scores(version, workstreams):
    """Append workstream scores to the latest agent_scores.json entry."""
    try:
        with open(SCORES_PATH) as f:
            scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scores = []

    # Find or create entry for this version
    found = False
    for entry in scores:
        if entry.get('iteration') == version:
            entry['workstreams'] = workstreams
            found = True
            break

    if not found:
        scores.append({
            'iteration': version,
            'date': time.strftime('%Y-%m-%d'),
            'workstreams': workstreams,
        })

    with open(SCORES_PATH, 'w') as f:
        json.dump(scores, f, indent=2)

    print(f"Workstream scores saved to {SCORES_PATH}")


if __name__ == '__main__':
    version = sys.argv[1] if len(sys.argv) > 1 else 'v9.38'

    # Handle --iteration flag
    if '--iteration' in sys.argv:
        idx = sys.argv.index('--iteration')
        if idx + 1 < len(sys.argv):
            version = sys.argv[idx + 1]

    build_log_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('-') else f'docs/kjtcom-build-{version}.md'
    gotchas = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('-') else 'G34,G47,G53'

    # Standard evaluation
    if os.path.exists(build_log_path):
        entry, tokens = run_evaluator(version, build_log_path, gotchas)
        if '--append' in sys.argv:
            append_to_scores(entry, tokens)
    else:
        print(f"Build log not found: {build_log_path}, skipping standard evaluation.")
        entry, tokens = None, {}

    # Workstream evaluation
    if '--workstreams' in sys.argv or '--iteration' in sys.argv:
        design_path = f'docs/kjtcom-design-{version}.md'
        if os.path.exists(design_path):
            workstreams = run_workstream_evaluator(version, design_path)
            if workstreams:
                append_workstreams_to_scores(version, workstreams)
        else:
            print(f"Design doc not found: {design_path}, skipping workstream evaluation.")
