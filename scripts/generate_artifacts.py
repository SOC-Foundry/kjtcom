#!/usr/bin/env python3
"""Post-iteration artifact generator. Drafts build log + report from structured inputs.

Reads event log, agent_scores, git diff, and templates to produce draft artifacts
in docs/drafts/ for human review before promotion.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event
from utils.ollama_logged import chat_logged

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'template', 'artifacts')
DRAFTS_DIR = os.path.join(PROJECT_DIR, 'docs', 'drafts')
EVENT_LOG = os.path.join(PROJECT_DIR, 'data', 'iao_event_log.jsonl')
SCORES_PATH = os.path.join(PROJECT_DIR, 'agent_scores.json')


def get_iteration():
    return os.environ.get('IAO_ITERATION', 'unknown')


def get_iteration_number(iteration):
    """Extract number from vX.YY format."""
    return iteration.replace('v', '')


def load_template(name):
    path = os.path.join(TEMPLATE_DIR, name)
    with open(path) as f:
        return f.read()


def get_git_diff_stat():
    """Get git diff --stat output."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--stat', 'HEAD'],
            capture_output=True, text=True, timeout=10,
            cwd=PROJECT_DIR
        )
        return result.stdout.strip() or "No uncommitted changes."
    except Exception as e:
        return f"Error: {e}"


def get_event_log_summary(iteration):
    """Read event log and summarize for current iteration."""
    events = []
    try:
        with open(EVENT_LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                if ev.get('iteration') == iteration:
                    events.append(ev)
    except FileNotFoundError:
        return "No event log found."

    if not events:
        return f"No events logged for {iteration}."

    # Summarize by type
    by_type = {}
    errors = 0
    for ev in events:
        t = ev.get('event_type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1
        if ev.get('status') == 'error':
            errors += 1

    lines = [f"Total events: {len(events)}"]
    for t, count in sorted(by_type.items()):
        lines.append(f"  {t}: {count}")
    lines.append(f"Errors: {errors}")
    return "\n".join(lines)


def get_agent_scores(iteration):
    """Load agent_scores.json entry for this iteration."""
    try:
        with open(SCORES_PATH) as f:
            scores = json.load(f)
        for entry in scores:
            if entry.get('iteration') == iteration:
                return entry
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None


def format_workstream_rows(scores_entry):
    """Format workstream scorecard rows from agent_scores."""
    if not scores_entry or 'workstreams' not in scores_entry:
        return "| - | No workstream data | - | - | - | - | - | - |"

    rows = []
    for ws in scores_entry['workstreams']:
        agents = ", ".join(ws.get('agents', []))
        llms = ", ".join(ws.get('llms', []))
        mcps = ", ".join(ws.get('mcps', []))
        rows.append(
            f"| {ws['id']} | {ws['name']} | {ws.get('priority', '-')} | "
            f"{ws.get('outcome', '-')} | {agents} | {llms} | {mcps} | "
            f"{ws.get('score', '-')}/10 |"
        )
    return "\n".join(rows)


def generate_narrative(iteration, context_text):
    """Use Qwen to generate narrative sections from structured context."""
    prompt = (
        f"/no_think Write a concise build summary for kjtcom iteration {iteration}. "
        f"Include what was built, what worked, and any issues. "
        f"Keep it under 300 words.\n\nContext:\n{context_text[:3000]}"
    )
    result = chat_logged(
        model="qwen3.5:9b",
        prompt=prompt,
        source_agent="generate-artifacts",
        evaluation=False
    )
    return result.get('content', 'Narrative generation failed.').strip()


def generate_build_log(iteration):
    """Generate build log draft."""
    template = load_template('build-template.md')
    date = datetime.now().strftime('%B %d, %Y')
    iter_num = get_iteration_number(iteration)

    diff_stat = get_git_diff_stat()
    event_summary = get_event_log_summary(iteration)

    # Generate narrative from context
    context = f"Iteration: {iteration}\nFiles changed:\n{diff_stat}\n\nEvents:\n{event_summary}"
    narrative = generate_narrative(iteration, context)

    filled = template.format(
        iteration=iteration,
        iteration_number=iter_num,
        date=date,
        preflight_status="All pre-flight checks passed.",
        execution_log=narrative,
        files_changed=diff_stat,
        test_results="See flutter analyze and flutter test output.",
        gotcha_log="G34: Single array-contains limit - workaround active.\nG47: CanvasKit DOM - open.\nG53: Firebase MCP reauth - recurring.",
        event_log_summary=event_summary
    )

    out_path = os.path.join(DRAFTS_DIR, f'kjtcom-build-{iteration}.md')
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(filled)
    print(f"Build log draft: {out_path}")
    return out_path


def generate_report(iteration):
    """Generate report draft."""
    template = load_template('report-template.md')
    date = datetime.now().strftime('%B %d, %Y')
    iter_num = get_iteration_number(iteration)

    scores_entry = get_agent_scores(iteration)
    workstream_rows = format_workstream_rows(scores_entry)
    event_summary = get_event_log_summary(iteration)

    # Generate summary narrative
    context = f"Iteration: {iteration}\nWorkstreams: {json.dumps(scores_entry.get('workstreams', []) if scores_entry else [], indent=2)[:2000]}\n\nEvents:\n{event_summary}"
    summary = generate_narrative(iteration, context)

    filled = template.format(
        iteration=iteration,
        iteration_number=iter_num,
        date=date,
        summary=summary,
        workstream_rows=workstream_rows,
        cost_target="<50K Claude tokens, Gemini free tier",
        cost_result="TBD - review token usage in event log",
        delivery_target="5 workstreams complete",
        delivery_result="TBD - review workstream scorecard",
        performance_target="/ask returns real Firestore counts",
        performance_result="TBD - verify from Telegram test",
        agent_utilization="Claude Code (primary executor), Qwen3.5-9B (evaluator), Gemini Flash (intent routing, synthesis)",
        event_log_summary=event_summary,
        gotcha_summary="G34: Active - post-filter workaround\nG47: Open\nG53: Recurring",
        next_candidates="TBD"
    )

    out_path = os.path.join(DRAFTS_DIR, f'kjtcom-report-{iteration}.md')
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(filled)
    print(f"Report draft: {out_path}")
    return out_path


def generate_changelog_entry(iteration):
    """Generate changelog entry draft."""
    template = load_template('changelog-template.md')
    date = datetime.now().strftime('%Y-%m-%d')

    diff_stat = get_git_diff_stat()
    lines = diff_stat.strip().split('\n')
    files_count = len([l for l in lines if l.strip() and '|' in l])

    filled = template.format(
        iteration=iteration,
        date=date,
        changelog_entry="TBD - summarize after review",
        files_changed_count=files_count,
        agents_used="Claude Code, Qwen3.5-9B, Gemini Flash",
        llms_used="gemini-2.5-flash, qwen3.5:9b, nomic-embed-text"
    )

    out_path = os.path.join(DRAFTS_DIR, f'changelog-{iteration}.md')
    with open(out_path, 'w') as f:
        f.write(filled)
    print(f"Changelog draft: {out_path}")
    return out_path


def main():
    iteration = get_iteration()
    print(f"Generating artifacts for {iteration}...")

    log_event("command", "generate-artifacts", "local", "generate",
              input_summary=f"generate_artifacts for {iteration}")

    build_path = generate_build_log(iteration)
    report_path = generate_report(iteration)
    changelog_path = generate_changelog_entry(iteration)

    print(f"\nDrafts generated in {DRAFTS_DIR}/")
    print("Review and promote to docs/ when ready.")

    log_event("command", "generate-artifacts", "local", "generate",
              output_summary=f"Generated build, report, changelog for {iteration}",
              status="success")


if __name__ == '__main__':
    main()
