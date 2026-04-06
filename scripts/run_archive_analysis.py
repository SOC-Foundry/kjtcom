#!/usr/bin/env python3
"""Analyze pipeline archive reports to produce Bourdain scaling plan.

v10.56: Feed all CalGold + RickSteves Phase 1-5 reports to Qwen for analysis.
Produces docs/bourdain-scaling-plan.md with data-driven execution recommendations.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from utils.ollama_config import merge_defaults

OLLAMA_URL = 'http://localhost:11434/api/chat'
PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ARCHIVE_DIR = os.path.join(PROJECT_DIR, 'docs', 'archive')


def collect_pipeline_reports():
    """Collect all pipeline-specific reports and builds from archive."""
    content_parts = []
    total_chars = 0

    for prefix in ['calgold', 'ricksteves', 'tripledb']:
        for doc_type in ['report', 'build']:
            pattern = f"{prefix}-{doc_type}-v"
            files = sorted([
                f for f in os.listdir(ARCHIVE_DIR)
                if f.startswith(pattern) and f.endswith('.md')
            ])
            for fname in files:
                fpath = os.path.join(ARCHIVE_DIR, fname)
                with open(fpath) as f:
                    text = f.read()
                # Truncate large files to fit context
                if total_chars + len(text) > 180000:
                    text = text[:5000]
                content_parts.append(f"\n--- {fname} ---\n{text}")
                total_chars += len(text)

    return "\n".join(content_parts), total_chars


def build_analysis_prompt(archive_content):
    """Build the Qwen analysis prompt."""
    return f"""/no_think
You are analyzing pipeline execution reports from the kjtcom project to produce a scaling plan for the Bourdain pipeline.

CONTEXT:
- CalGold pipeline: 431 videos, 899 entities, completed Phase 0-5 across 6 iterations
- RickSteves pipeline: 403 videos, 4,182 entities, completed Phase 1-5 across 5 iterations
- TripleDB pipeline: 267 videos, 1,100 entities
- Bourdain pipeline: 114 videos total, Phase 1 complete (30 videos, 96 entities in staging)

The 7 phases are:
1. Acquire (yt-dlp download)
2. Transcribe (faster-whisper CUDA)
3. Extract (Gemini Flash API)
4. Normalize (schema v3 Thompson Indicator Fields)
5. Geocode (Nominatim)
6. Enrich (Google Places API)
7. Load to Firestore (staging)

ANALYSIS REQUIRED:
For each pipeline in the archive, identify:
1. Average iteration count per phase
2. Common failure patterns and interventions needed
3. Which phases were parallelized or collapsed together
4. Batch sizes used (videos per batch)
5. Entity yield per video (entities/video ratio)
6. Geocoding success rate
7. Time-consuming steps and bottlenecks

Then produce a CONCRETE execution plan for Bourdain:
- Remaining: 84 videos (31-114) need Phase 2-7
- GPU constraint: RTX 2080 SUPER 8GB VRAM, graduated tmux batches only
- Objective: Complete in minimum iterations (target: 2-3)
- All output goes to staging only

Output format: Write a markdown document suitable for docs/bourdain-scaling-plan.md

ARCHIVE REPORTS:
{archive_content}

Write the complete markdown document now."""


def call_qwen_analysis(prompt):
    """Call Qwen with large context for archive analysis."""
    payload = {
        'model': 'qwen3.5:9b',
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False,
        'think': False,
        'options': {
            'num_predict': 4096,
            'num_ctx': 32768,
        },
    }

    print(f"[ARCHIVE] Calling Qwen with {len(prompt)} char prompt...")
    start = time.time()

    result = subprocess.run(
        ['curl', '-s', OLLAMA_URL, '-d', json.dumps(payload)],
        capture_output=True, text=True, timeout=300
    )
    latency = int((time.time() - start) * 1000)

    try:
        response = json.loads(result.stdout)
        content = response['message']['content']
        tokens = response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
        print(f"[ARCHIVE] Qwen responded in {latency}ms, {tokens} total tokens")
        return content
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[ARCHIVE] Qwen failed: {e}")
        if result.stdout:
            print(f"[ARCHIVE] Raw output (first 500): {result.stdout[:500]}")
        return None


def main():
    output_path = os.path.join(PROJECT_DIR, 'docs', 'bourdain-scaling-plan.md')

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    print("[ARCHIVE] Collecting pipeline reports...")
    archive_content, total_chars = collect_pipeline_reports()
    print(f"[ARCHIVE] Collected {total_chars} chars from archive")

    prompt = build_analysis_prompt(archive_content)

    content = call_qwen_analysis(prompt)
    if not content:
        print("[ARCHIVE] Qwen failed. Trying Gemini Flash...")
        try:
            import litellm
            from utils.ollama_config import GEMINI_MODEL
            response = litellm.completion(
                model=GEMINI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4096,
            )
            content = response.choices[0].message.content
            print("[ARCHIVE] Gemini Flash succeeded")
        except Exception as e:
            print(f"[ARCHIVE] Gemini Flash also failed: {e}")
            content = None

    if not content:
        print("[ARCHIVE] All LLMs failed. Cannot produce scaling plan.")
        sys.exit(1)

    # Write output
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"[ARCHIVE] Scaling plan written to {output_path}")
    print(f"[ARCHIVE] {len(content)} chars, {len(content.splitlines())} lines")


if __name__ == '__main__':
    main()
