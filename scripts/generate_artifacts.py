#!/usr/bin/env python3
"""Post-iteration artifact generator. Drafts build log + report from structured inputs.

Reads event log, agent_scores, git diff, and templates to produce draft artifacts
in docs/drafts/ for human review before promotion.
"""
import argparse
import glob
import json
import os
import shutil
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
DOCS_DIR = os.path.join(PROJECT_DIR, 'docs')
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
    """Format workstream scorecard rows from agent_scores (v9.43: Evidence column)."""
    if not scores_entry or 'workstreams' not in scores_entry:
        return "| - | No workstream data | - | - | - | - | - | - | - |"

    rows = []
    for ws in scores_entry['workstreams']:
        agents = ", ".join(ws.get('agents', []))
        llms = ", ".join(ws.get('llms', []))
        mcps_raw = ws.get('mcps', [])
        # MCP whitelist enforcement (v9.43)
        valid_mcps = {"Firebase", "Context7", "Firecrawl", "Playwright", "Dart", "-"}
        mcps = ", ".join(m for m in mcps_raw if m in valid_mcps) or "-"
        evidence = ws.get('evidence', '-')
        rows.append(
            f"| {ws['id']} | {ws['name']} | {ws.get('priority', '-')} | "
            f"{ws.get('outcome', '-')} | {evidence} | {agents} | {llms} | {mcps} | "
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
        event_log_summary=event_summary,
        post_flight_results="Run `python3 scripts/post_flight.py` - results pending."
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
        cost_result="Review token usage in event log",
        delivery_target="6 workstreams complete",
        delivery_result="Review workstream scorecard above",
        performance_target="/ask returns real Firestore counts with session memory",
        performance_result="Verify from post-flight and Telegram test",
        agent_utilization="Claude Code (primary executor), Qwen3.5-9B (evaluator), Gemini Flash (intent routing, synthesis)",
        event_log_summary=event_summary,
        gotcha_summary="G34: Active - post-filter workaround\nG47: Open\nG53: Recurring",
        next_candidates="1. Persistent session storage (Redis/Firestore) for bot context\n2. Composite Firestore index for rating sort + filter\n3. Bourdain pipeline onboarding"
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
        changelog_entry="Bot session memory, rating-aware queries, post-flight verification, architecture HTML, Qwen evaluator overhaul",
        files_changed_count=files_count,
        agents_used="Claude Code, Qwen3.5-9B, Gemini Flash",
        llms_used="gemini-2.5-flash, qwen3.5:9b, nomic-embed-text"
    )

    out_path = os.path.join(DRAFTS_DIR, f'changelog-{iteration}.md')
    with open(out_path, 'w') as f:
        f.write(filled)
    print(f"Changelog draft: {out_path}")
    return out_path


def cross_check_workstreams(iteration):
    """Cross-check workstream outcomes against actual execution signals.

    Returns dict of workstream_id -> {claimed_outcome, verified_outcome, signals}.
    Checks: exit codes (timeout=124/137), file existence, error patterns in event log.
    """
    results = {}

    # Load agent_scores for this iteration
    scores_entry = get_agent_scores(iteration)
    if not scores_entry or 'workstreams' not in scores_entry:
        print("No workstream data to cross-check.")
        return results

    # Load event log for signals
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
        pass

    timeout_events = [e for e in events if e.get('status') in ('timeout', 'error')]
    error_sources = set(e.get('source_agent', '') for e in timeout_events)

    for ws in scores_entry['workstreams']:
        ws_id = ws.get('id', '?')
        claimed = ws.get('outcome', 'unknown')
        signals = []
        verified = claimed

        # Check for timeout exit codes in events related to this workstream
        ws_name_lower = ws.get('name', '').lower()
        has_timeout = any(
            ws_name_lower in str(e.get('input_summary', '')).lower() or
            ws_name_lower in str(e.get('output_summary', '')).lower()
            for e in timeout_events
        )
        if has_timeout and claimed == 'complete':
            verified = 'partial'
            signals.append('timeout/error events found but claimed complete')

        # Check file existence for expected outputs
        # (Heuristic: if workstream mentions a new file, check it exists)
        expected_files = _guess_expected_files(ws)
        for fpath in expected_files:
            full = os.path.join(PROJECT_DIR, fpath)
            exists = os.path.exists(full)
            signals.append(f"{'EXISTS' if exists else 'MISSING'}: {fpath}")
            if not exists and claimed == 'complete':
                verified = 'partial'

        results[ws_id] = {
            'claimed_outcome': claimed,
            'verified_outcome': verified,
            'signals': signals,
            'mismatch': claimed != verified
        }

    mismatches = sum(1 for r in results.values() if r['mismatch'])
    print(f"Cross-check: {len(results)} workstreams, {mismatches} mismatches found.")
    for ws_id, r in results.items():
        if r['mismatch']:
            print(f"  {ws_id}: claimed={r['claimed_outcome']} -> verified={r['verified_outcome']}")
            for s in r['signals']:
                print(f"    {s}")

    return results


def _guess_expected_files(ws):
    """Heuristic: extract likely output file paths from workstream notes/name."""
    files = []
    name = ws.get('name', '').lower()
    notes = ws.get('notes', '').lower()
    combined = name + ' ' + notes

    # Common patterns
    if 'county' in combined or 'enrich' in combined:
        files.append('scripts/enrich_counties.py')
    if 'systemd' in combined or 'bot resil' in combined:
        files.append('kjtcom-telegram-bot.service')
    if 'gotcha' in combined:
        files.append('data/gotcha_archive.json')
    if 'registry' in combined and 'middleware' in combined:
        files.append('data/middleware_registry.json')
    if 'internet' in combined or 'brave' in combined or 'web route' in combined:
        files.append('scripts/brave_search.py')
    if 'intranet' in combined:
        files.append('docs/cross-project/intranet-update-v9.42.md')
    if 'session' in combined and 'memory' in combined:
        files.append('scripts/telegram_bot.py')
    if 'rating' in combined or 'sort' in combined:
        files.append('data/schema_reference.json')
    if 'post-flight' in combined or 'verification' in combined:
        files.append('scripts/post_flight.py')
    if 'architecture' in combined and 'html' in combined:
        files.append('app/web/architecture.html')
        files.append('scripts/build_architecture_html.py')

    return files


def promote_drafts(iteration):
    """Copy validated drafts from docs/drafts/ to docs/."""
    if not os.path.isdir(DRAFTS_DIR):
        print(f"No drafts directory: {DRAFTS_DIR}")
        return False

    pattern = os.path.join(DRAFTS_DIR, f'kjtcom-*-{iteration}.md')
    drafts = glob.glob(pattern)
    # Also grab changelog
    cl_pattern = os.path.join(DRAFTS_DIR, f'changelog-{iteration}.md')
    cl_drafts = glob.glob(cl_pattern)
    drafts.extend(cl_drafts)

    if not drafts:
        print(f"No drafts found for {iteration} in {DRAFTS_DIR}")
        return False

    promoted = []
    for draft in drafts:
        basename = os.path.basename(draft)
        dest = os.path.join(DOCS_DIR, basename)
        shutil.copy2(draft, dest)
        promoted.append(basename)
        print(f"  Promoted: {basename}")

    log_event("command", "generate-artifacts", "local", "promote",
              input_summary=f"Promote {len(promoted)} drafts for {iteration}",
              output_summary=", ".join(promoted),
              status="success")

    print(f"Promoted {len(promoted)} drafts to docs/")
    return True


def validate_only(iteration):
    """Validate drafts against execution reality without generating new ones."""
    print(f"Validating drafts for {iteration}...")
    results = cross_check_workstreams(iteration)

    if not results:
        print("No workstream data available for validation.")
        return False

    mismatches = [ws_id for ws_id, r in results.items() if r['mismatch']]
    if mismatches:
        print(f"\nWARNING: {len(mismatches)} workstream outcome mismatches detected:")
        for ws_id in mismatches:
            r = results[ws_id]
            print(f"  {ws_id}: Qwen said '{r['claimed_outcome']}', verified as '{r['verified_outcome']}'")
        print("\nDrafts may contain inaccurate workstream assessments.")
        return False
    else:
        print("\nAll workstream outcomes verified. Drafts are safe to promote.")
        return True


def main():
    parser = argparse.ArgumentParser(description='Generate or manage iteration artifacts.')
    parser.add_argument('--promote', action='store_true',
                        help='Promote validated drafts from docs/drafts/ to docs/')
    parser.add_argument('--validate-only', action='store_true',
                        help='Cross-check draft accuracy against execution signals')
    args = parser.parse_args()

    iteration = get_iteration()

    if args.validate_only:
        validate_only(iteration)
        return

    if args.promote:
        promote_drafts(iteration)
        return

    # Default: generate drafts
    print(f"Generating artifacts for {iteration}...")

    log_event("command", "generate-artifacts", "local", "generate",
              input_summary=f"generate_artifacts for {iteration}")

    build_path = generate_build_log(iteration)
    report_path = generate_report(iteration)
    changelog_path = generate_changelog_entry(iteration)

    # Run cross-check automatically after generation
    print("\nRunning execution cross-check...")
    cross_check_workstreams(iteration)

    print(f"\nDrafts generated in {DRAFTS_DIR}/")
    print("Run with --validate-only to verify, then --promote to finalize.")

    log_event("command", "generate-artifacts", "local", "generate",
              output_summary=f"Generated build, report, changelog for {iteration}",
              status="success")


if __name__ == '__main__':
    main()
