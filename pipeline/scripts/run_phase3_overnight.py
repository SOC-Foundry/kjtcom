#!/usr/bin/env python3
"""Overnight wrapper for Parts Unknown Phase 3 (v10.65).

Targets episodes 121-150 (if available) or the next 30 unprocessed videos.
Runs acquire → transcribe → extract → normalize → geocode → enrich → load.
"""
import subprocess
import sys
import os
import json

# Ensure we're in the project root
BASE_DIR = os.path.expanduser("~/dev/projects/kjtcom")
os.chdir(BASE_DIR)

# Set IAO_ITERATION
os.environ["IAO_ITERATION"] = "v10.65"

def get_next_batch(count=30):
    playlist_path = "pipeline/config/bourdain/playlist_urls.txt"
    checkpoint_path = "pipeline/data/bourdain/.checkpoint_transcribe.json"
    
    if not os.path.exists(playlist_path):
        return []
    
    with open(playlist_path) as f:
        urls = [line.strip() for line in f if line.strip()]
    
    processed = set()
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path) as f:
            processed = set(json.load(f).get("processed", []))
    
    todo = [u for u in urls if u not in processed]
    return todo[:count]

batch = get_next_batch(30)
if not batch:
    print("No new videos to process. Exiting.")
    sys.exit(0)

print(f"Targeting batch of {len(batch)} videos: {batch[:5]}...")

# Since phase1_acquire.py doesn't support list of IDs via CLI easily without a range
# We'll just run it with a limit or we can temporarily create a batch file.
batch_file = "/tmp/pu_phase3_batch.txt"
with open(batch_file, "w") as f:
    f.write("\n".join(batch))

PHASES = [
    ("acquire",   ["python3", "pipeline/scripts/phase1_acquire.py", "--pipeline", "bourdain", "--limit", str(len(batch))]),
    ("transcribe",["python3", "pipeline/scripts/phase2_transcribe.py", "--pipeline", "bourdain", "--limit", str(len(batch))]),
    ("extract",   ["python3", "pipeline/scripts/phase3_extract.py", "--pipeline", "bourdain", "--limit", str(len(batch))]),
    ("normalize", ["python3", "pipeline/scripts/phase4_normalize.py", "--pipeline", "bourdain"]),
    ("geocode",   ["python3", "pipeline/scripts/phase5_geocode.py", "--pipeline", "bourdain"]),
    ("enrich",    ["python3", "pipeline/scripts/phase6_enrich.py", "--pipeline", "bourdain"]),
    ("load",      ["python3", "pipeline/scripts/phase7_load.py", "--pipeline", "bourdain", "--database", "staging"]),
]

# ollama stop before transcription (G18)
print("Stopping Ollama to free GPU for transcription...", flush=True)
subprocess.run(["ollama", "stop", "qwen3.5:9b"], check=False)

# Verify GPU
subprocess.run(["nvidia-smi"], check=False)

for name, cmd in PHASES:
    print(f"\n=== PHASE {name.upper()} ===", flush=True)
    log_file = f"/tmp/pu_phase3_{name}.log"
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    # For acquire, use the full playlist file but we've limited it to the batch size
    # Note: phase1_acquire.py skips already-acquired, so this is safe.
    
    with open(log_file, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    
    if r.returncode != 0:
        print(f"PHASE 3 ABORTED at {name} (see {log_file})", flush=True)
        sys.exit(r.returncode)
    print(f"Phase {name} complete.", flush=True)

print("\nPHASE 3 COMPLETE", flush=True)
