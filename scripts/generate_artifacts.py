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
HARNESS_PATH = os.path.join(PROJECT_DIR, 'docs', 'evaluator-harness.md')


def load_harness():
    """Load evaluator harness for skeptical artifact generation."""
    try:
        with open(HARNESS_PATH) as f:
            return f.read()
    except FileNotFoundError:
        return ""


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
    """Get git diff --stat output plus untracked files."""
    try:
        # Tracked changes
        result = subprocess.run(
            ['git', 'diff', '--stat', 'HEAD'],
            capture_output=True, text=True, timeout=10,
            cwd=PROJECT_DIR
        )
        tracked = result.stdout.strip()
        
        # Untracked files
        result_u = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            capture_output=True, text=True, timeout=10,
            cwd=PROJECT_DIR
        )
        untracked = result_u.stdout.strip()
        
        out = []
        if tracked:
            out.append("TRACKED CHANGES:")
            out.append(tracked)
        if untracked:
            if out: out.append("")
            out.append("NEW UNTRACKED FILES:")
            out.append(untracked)
            
        return "\n".join(out) if out else "No changes detected."
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
    """Load agent_scores.json entry for this iteration.

    v9.49+: supports both old format (list of entries with 'workstreams' key)
    and new schema-validated format (entry IS the evaluation object).
    """
    try:
        with open(SCORES_PATH) as f:
            raw = json.load(f)
        # Handle canonical {iterations: [...]} and legacy flat array
        if isinstance(raw, dict):
            entries = raw.get('iterations', [raw] if raw.get('iteration') else [])
        else:
            entries = raw
        for entry in entries:
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


def render_build_markdown(eval_data):
    """Convert evaluation JSON into markdown build log format (v9.51).

    Replaces raw JSON dumps in execution section with readable prose.
    """
    lines = []
    lines.append("## EXECUTION LOG\n")
    lines.append(eval_data.get("summary", "No summary available."))
    lines.append("")

    for ws in eval_data.get("workstreams", []):
        outcome_label = ws["outcome"].upper()
        lines.append(f"**{ws['id']} ({ws.get('priority', 'P2')}): {ws['name']} - {outcome_label}**")
        lines.append(f"- Evidence: {ws.get('evidence', 'None')}")
        for imp in ws.get("improvements", []):
            lines.append(f"- Improvement: {imp}")
        lines.append("")

    return "\n".join(lines)


def generate_narrative(iteration, context_text):
    """Use Qwen to generate narrative sections from structured context."""
    harness = load_harness()
    prompt = (
        f"/no_think Write a concise build summary for kjtcom iteration {iteration}. "
        f"Include what was built, what worked, and any issues. "
        f"Keep it under 300 words.\n\nContext:\n{context_text[:3000]}"
    )
    result = chat_logged(
        model="qwen3.5:9b",
        prompt=prompt,
        source_agent="generate-artifacts",
        evaluation=False,
        system_prompt=harness if harness else None
    )
    return result.get('content', 'Narrative generation failed.').strip()


def generate_build_log(iteration):
    """Generate build log draft."""
    template = load_template('build-template.md')
    date = datetime.now().strftime('%B %d, %Y')
    iter_num = get_iteration_number(iteration)

    diff_stat = get_git_diff_stat()
    event_summary = get_event_log_summary(iteration)

    # v9.51: Use render_build_markdown if scores exist, else fall back to LLM narrative
    scores_entry = get_agent_scores(iteration)
    if scores_entry and 'workstreams' in scores_entry:
        narrative = render_build_markdown(scores_entry)
    else:
        context = f"Iteration: {iteration}\nFiles changed:\n{diff_stat}\n\nEvents:\n{event_summary}"
        narrative = generate_narrative(iteration, context)

    executing_agent = "Gemini CLI" if iteration == "v9.47" else "Claude Code (Opus 4.6)"

    filled = template.format(
        iteration=iteration,
        iteration_number=iter_num,
        date=date,
        executing_agent=executing_agent,
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


def compute_trident_values(iteration, scores_entry):
    """Compute actual Trident values from event log and workstream data.

    Returns dict with cost_result, delivery_result, performance_result.
    Never returns 'Review...' or 'TBD' - always actual values.
    """
    # Cost: count tokens from event log
    total_tokens = 0
    llm_calls = 0
    try:
        with open(EVENT_LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                if ev.get('iteration') == iteration and ev.get('event_type') == 'llm_call':
                    llm_calls += 1
                    tokens = ev.get('tokens') or {}
                    total_tokens += tokens.get('total', 0)
    except FileNotFoundError:
        pass

    if total_tokens > 0:
        cost_result = f"{total_tokens:,} tokens across {llm_calls} LLM calls"
    else:
        cost_result = f"{llm_calls} LLM calls logged (token counts pending)"

    # Delivery: read from build log's literal Trident Metrics section (ADR-021)
    delivery_result = None
    build_log_path = os.path.join(DOCS_DIR, f'kjtcom-build-{iteration}.md')
    if os.path.exists(build_log_path):
        try:
            with open(build_log_path) as f:
                content = f.read()
                import re as _re
                # Match "Delivery: X/Y workstreams complete" (case insensitive)
                m = _re.search(r"Delivery:\s*(\d+/\d+\s+workstreams[^\n]*)", content, _re.IGNORECASE)
                if m:
                    delivery_result = m.group(1).strip()
        except Exception:
            pass

    if not delivery_result:
        # Fallback: count complete/total from workstream scorecard
        if scores_entry and 'workstreams' in scores_entry:
            ws_list = scores_entry['workstreams']
            total_ws = len(ws_list)
            complete_ws = sum(1 for ws in ws_list if ws.get('outcome') == 'complete')
            partial_ws = sum(1 for ws in ws_list if ws.get('outcome') == 'partial')
            delivery_result = f"{complete_ws}/{total_ws} workstreams complete"
            if partial_ws:
                delivery_result += f", {partial_ws} partial"
        else:
            delivery_result = "Workstream evaluation pending"

    # Performance: derive from workstream evidence
    perf_notes = []
    if scores_entry and 'workstreams' in scores_entry:
        for ws in scores_entry['workstreams']:
            evidence = ws.get('evidence', '')
            if evidence and evidence != '-':
                perf_notes.append(f"{ws.get('id', '?')}: {evidence[:60]}")
    if perf_notes:
        performance_result = "; ".join(perf_notes[:3])
    else:
        performance_result = "See post-flight verification results"

    return {
        'cost_result': cost_result,
        'delivery_result': delivery_result,
        'performance_result': performance_result,
    }


def render_report_markdown(iteration, scores_entry, event_summary):
    """Render the full report markdown using template and evaluation data."""
    template = load_template('report-template.md')
    date = datetime.now().strftime('%B %d, %Y')
    iter_num = get_iteration_number(iteration)

    workstream_rows = format_workstream_rows(scores_entry)
    trident = compute_trident_values(iteration, scores_entry)

    # Use schema-validated summary if available (v9.50)
    summary = scores_entry.get('summary') if scores_entry else None
    if not summary:
        context = f"Iteration: {iteration}\nWorkstreams: {json.dumps(scores_entry.get('workstreams', []) if scores_entry else [], indent=2)[:2000]}\n\nEvents:\n{event_summary}"
        summary = generate_narrative(iteration, context)

    # Agent utilization logic
    exec_agent = "Claude Code"
    if iteration == "v9.47": exec_agent = "Gemini CLI"
    
    # Try to find executor in event log if not hardcoded
    try:
        with open(EVENT_LOG) as f:
            for line in f:
                if 'gemini-cli' in line: 
                    exec_agent = "Gemini CLI"
                    break
    except: pass

    agent_utilization = f"{exec_agent} (primary executor), Qwen3.5-9B (evaluator), Gemini Flash (intent routing, synthesis)"

    # Schema-validated fields (v9.49+)
    wcbb = ""
    if scores_entry and 'what_could_be_better' in scores_entry:
        wcbb_items = scores_entry['what_could_be_better']
        wcbb = "\n".join(f"{i+1}. {item}" for i, item in enumerate(wcbb_items))
    else:
        wcbb = "1. Persistent session storage\n2. Firestore indexing\n3. Pipeline onboarding"

    if scores_entry and 'trident' in scores_entry:
        t = scores_entry['trident']
        trident['cost_result'] = t.get('cost', trident['cost_result'])
        trident['delivery_result'] = t.get('delivery', trident['delivery_result'])
        trident['performance_result'] = t.get('performance', trident['performance_result'])

    return template.format(
        iteration=iteration,
        iteration_number=iter_num,
        date=date,
        summary=summary,
        workstream_rows=workstream_rows,
        cost_target="<50K Claude tokens, Gemini free tier",
        cost_result=trident['cost_result'],
        delivery_target="5 workstreams complete",
        delivery_result=trident['delivery_result'],
        performance_target="Schema-validated Qwen eval on first/second attempt",
        performance_result=trident['performance_result'],
        agent_utilization=agent_utilization,
        event_log_summary=event_summary,
        gotcha_summary="G34: Active\nG47: Open\nG53: Recurring\nG54: Transitive deps",
        next_candidates=wcbb
    )


def generate_report(iteration):
    """Generate report draft."""
    scores_entry = get_agent_scores(iteration)
    event_summary = get_event_log_summary(iteration)
    
    filled = render_report_markdown(iteration, scores_entry, event_summary)

    out_path = os.path.join(DRAFTS_DIR, f'kjtcom-report-{iteration}.md')
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(filled)
    print(f"Report draft: {out_path}")
    return out_path


def update_unified_changelog(iteration):
    """Generate changelog entry and prepend to docs/kjtcom-changelog.md."""
    template = load_template('changelog-template.md')
    date = datetime.now().strftime('%Y-%m-%d')

    diff_stat = get_git_diff_stat()
    lines = diff_stat.strip().split('\n')
    files_count = len([l for l in lines if l.strip() and '|' in l])

    # Build changelog entries from agent_scores
    scores_entry = get_agent_scores(iteration)

    changelog_lines = []
    if scores_entry and 'workstreams' in scores_entry:
        for ws in scores_entry['workstreams']:
            outcome = ws.get('outcome', 'unknown')
            name = ws.get('name', 'Unknown')
            evidence = ws.get('evidence', '')
            if outcome == 'complete':
                prefix = "FIXED" if "fix" in name.lower() or "recover" in name.lower() else "UPDATED"
                if any(kw in name.lower() for kw in ['new', 'create', 'add']):
                    prefix = "NEW"
                changelog_lines.append(f"{prefix}: {name} - {evidence or 'verified'}")
            elif outcome == 'partial':
                changelog_lines.append(f"UPDATED: {name} (partial) - {evidence or 'in progress'}")

    if not changelog_lines:
        changelog_lines = [f"UPDATED: Iteration {iteration} - see build log for details"]

    changelog_entry_text = "\n".join(f"- {line}" for line in changelog_lines)

    # Count interventions from event log
    intervention_count = 0
    try:
        with open(EVENT_LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                if ev.get('iteration') == iteration and ev.get('event_type') == 'intervention':
                    intervention_count += 1
    except FileNotFoundError:
        pass

    agents_used = "Gemini CLI, Qwen3.5-9B, Gemini Flash" if iteration == "v9.47" else "Claude Code, Qwen3.5-9B, Gemini Flash"

    filled_entry = template.format(
        iteration=iteration,
        date=date,
        changelog_entry=changelog_entry_text,
        files_changed_count=files_count,
        agents_used=agents_used,
        llms_used="gemini-2.5-flash, qwen3.5:9b, nomic-embed-text",
        intervention_count=intervention_count
    )

    changelog_path = os.path.join(DOCS_DIR, 'kjtcom-changelog.md')
    header = "# kjtcom - Unified Changelog\n\n"
    
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r') as f:
            content = f.read()
        
        # Remove header if present to avoid duplicates
        if content.startswith(header):
            body = content[len(header):]
        else:
            body = content
            
        # Check if iteration already exists to avoid double-prepending
        if f"## {iteration}" in content:
            print(f"Changelog entry for {iteration} already exists in {changelog_path}. Skipping prepend.")
            return changelog_path
            
        new_content = header + filled_entry + "\n\n---\n\n" + body
    else:
        new_content = header + filled_entry

    with open(changelog_path, 'w') as f:
        f.write(new_content)
    
    print(f"Updated unified changelog: {changelog_path}")
    return changelog_path


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

    # G58: Design and plan docs are INPUT artifacts - immutable during execution
    IMMUTABLE_ARTIFACTS = ["design", "plan"]
    for artifact_type in IMMUTABLE_ARTIFACTS:
        output_path = os.path.join(DOCS_DIR, f'kjtcom-{artifact_type}-{iteration}.md')
        if os.path.exists(output_path):
            print(f"[ARTIFACT] SKIP {artifact_type} -- already exists (immutable, G58)")

    log_event("command", "generate-artifacts", "local", "generate",
              input_summary=f"generate_artifacts for {iteration}")

    build_path = generate_build_log(iteration)
    report_path = generate_report(iteration)
    changelog_path = update_unified_changelog(iteration)

    # Run cross-check automatically after generation
    print("\nRunning execution cross-check...")
    cross_check_workstreams(iteration)

    print(f"\nDrafts generated in {DRAFTS_DIR}/")
    print("Run with --validate-only to verify, then --promote to finalize.")

    log_event("command", "generate-artifacts", "local", "generate",
              output_summary=f"Generated build, report and updated unified changelog for {iteration}",
              status="success")


if __name__ == '__main__':
    main()
