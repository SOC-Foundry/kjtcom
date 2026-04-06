#!/usr/bin/env python3
"""Generate cumulative agent leaderboard from agent_scores.json."""
import json
import sys
import os

SCORES_PATH = os.path.join(os.path.dirname(__file__), '..', 'agent_scores.json')


def generate():
    with open(SCORES_PATH) as f:
        raw = json.load(f)

    # Handle both canonical {iterations: [...]} and legacy flat array
    data = raw.get('iterations', raw) if isinstance(raw, dict) else raw

    # Aggregate per agent
    agents = {}
    total_prompt_tokens = 0
    total_eval_tokens = 0

    for entry in data:
        # Track evaluator tokens
        etokens = entry.get('evaluator_tokens', {})
        total_prompt_tokens += etokens.get('prompt_tokens', 0)
        total_eval_tokens += etokens.get('eval_tokens', 0)

        for score in entry.get('scores', []):
            name = score['agent']
            if name not in agents:
                agents[name] = {
                    'scores': [],
                    'iterations': [],
                    'prompt_tokens': 0,
                    'eval_tokens': 0
                }
            agents[name]['scores'].append(score['total'])
            agents[name]['iterations'].append(entry.get('iteration', '?'))
            agents[name]['prompt_tokens'] += score.get('prompt_tokens', 0)
            agents[name]['eval_tokens'] += score.get('eval_tokens', 0)

    # Generate table
    header = f'{"Agent":<30} | {"Iters":>5} | {"Avg":>7} | {"Best":>4} | {"Worst":>5} | {"Trend":>5} | {"Tokens":>8}'
    separator = '-' * len(header)

    print('=== Agent Leaderboard ===')
    print(f'Data: {len(data)} iterations')
    print()
    print(header)
    print(separator)

    for name, info in sorted(agents.items(), key=lambda x: -max(x[1]['scores'])):
        scores = info['scores']
        avg = sum(scores) / len(scores)
        best = max(scores)
        worst = min(scores)
        trend = scores[-1] - scores[0] if len(scores) > 1 else 0
        trend_str = f'+{trend}' if trend > 0 else str(trend)
        total_tokens = info['prompt_tokens'] + info['eval_tokens']

        print(f'{name:<30} | {len(scores):>5} | {avg:>5.1f}/50 | {best:>4} | {worst:>5} | {trend_str:>5} | {total_tokens:>8}')

    print(separator)
    print(f'\nEvaluator totals: prompt_tokens={total_prompt_tokens}, eval_tokens={total_eval_tokens}')

    return agents


if __name__ == '__main__':
    generate()
