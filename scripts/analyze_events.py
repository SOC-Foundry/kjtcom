#!/usr/bin/env python3
"""Analyze IAO event log and produce summary statistics.

Reads data/iao_event_log.jsonl and outputs:
- Total events, by type, by agent, error rate, token totals, latency stats
- Used by report generator and Telegram /status command
"""
import json
import os
import sys
from collections import Counter

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'iao_event_log.jsonl')


def load_events(iteration=None):
    """Load events from JSONL, optionally filtered by iteration."""
    events = []
    if not os.path.exists(LOG_PATH):
        return events
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if iteration and event.get('iteration') != iteration:
                    continue
                events.append(event)
            except json.JSONDecodeError:
                continue
    return events


def analyze(events):
    """Produce summary statistics from events."""
    if not events:
        return {
            'total_events': 0,
            'by_type': {},
            'by_agent': {},
            'by_target': {},
            'error_count': 0,
            'error_rate': 0.0,
            'total_tokens': {'prompt': 0, 'eval': 0, 'total': 0},
            'latency': {'min': 0, 'max': 0, 'avg': 0, 'p50': 0, 'p95': 0},
            'gotchas_triggered': []
        }

    by_type = Counter(e.get('event_type', 'unknown') for e in events)
    by_agent = Counter(e.get('source_agent', 'unknown') for e in events)
    by_target = Counter(e.get('target', 'unknown') for e in events)

    errors = [e for e in events if e.get('status') not in ('success',)]
    error_count = len(errors)

    # Token totals
    total_prompt = 0
    total_eval = 0
    for e in events:
        t = e.get('tokens')
        if t:
            total_prompt += t.get('prompt', 0)
            total_eval += t.get('eval', 0)

    # Latency stats
    latencies = [e.get('latency_ms') for e in events if e.get('latency_ms') is not None]
    latencies.sort()
    lat_stats = {'min': 0, 'max': 0, 'avg': 0, 'p50': 0, 'p95': 0}
    if latencies:
        lat_stats = {
            'min': latencies[0],
            'max': latencies[-1],
            'avg': int(sum(latencies) / len(latencies)),
            'p50': latencies[len(latencies) // 2],
            'p95': latencies[int(len(latencies) * 0.95)]
        }

    gotchas = [e.get('gotcha_triggered') for e in events
               if e.get('gotcha_triggered')]

    return {
        'total_events': len(events),
        'by_type': dict(by_type.most_common()),
        'by_agent': dict(by_agent.most_common()),
        'by_target': dict(by_target.most_common()),
        'error_count': error_count,
        'error_rate': round(error_count / len(events) * 100, 1) if events else 0,
        'total_tokens': {
            'prompt': total_prompt,
            'eval': total_eval,
            'total': total_prompt + total_eval
        },
        'latency': lat_stats,
        'gotchas_triggered': gotchas
    }


def print_summary(summary):
    """Print human-readable summary."""
    print('=== IAO Event Log Summary ===')
    print(f'Total events: {summary["total_events"]}')
    print(f'Error rate: {summary["error_rate"]}% ({summary["error_count"]} errors)')
    print()

    print('Events by type:')
    for t, c in summary['by_type'].items():
        print(f'  {t}: {c}')
    print()

    print('Events by agent:')
    for a, c in summary['by_agent'].items():
        print(f'  {a}: {c}')
    print()

    print('Events by target:')
    for t, c in summary['by_target'].items():
        print(f'  {t}: {c}')
    print()

    tok = summary['total_tokens']
    print(f'Tokens: prompt={tok["prompt"]}, eval={tok["eval"]}, total={tok["total"]}')

    lat = summary['latency']
    print(f'Latency (ms): min={lat["min"]}, avg={lat["avg"]}, '
          f'p50={lat["p50"]}, p95={lat["p95"]}, max={lat["max"]}')

    if summary['gotchas_triggered']:
        print(f'\nGotchas triggered: {", ".join(summary["gotchas_triggered"])}')


def main():
    iteration = sys.argv[1] if len(sys.argv) > 1 else None

    if iteration:
        print(f'Filtering events for iteration: {iteration}')

    events = load_events(iteration)
    summary = analyze(events)

    if '--json' in sys.argv:
        print(json.dumps(summary, indent=2))
    else:
        print_summary(summary)


if __name__ == '__main__':
    main()
