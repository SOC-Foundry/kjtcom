#!/usr/bin/env python3
"""Overnight wrapper for Parts Unknown Phase 2.

Runs acquire → transcribe → extract → normalize → geocode → enrich → load,
each phase logged to /tmp/pu_phase2_<phase>.log. Exits 0 on success,
non-zero on any phase failure (allows tmux session to terminate cleanly).
"""
import subprocess
import sys
import os

PHASES = [
    ("acquire",   ["python3", "pipeline/scripts/phase1_acquire.py", "--pipeline", "bourdain", "--range", "29:60"]),
    ("transcribe",["python3", "pipeline/scripts/phase2_transcribe.py", "--pipeline", "bourdain"]),
    ("extract",   ["python3", "pipeline/scripts/phase3_extract.py", "--pipeline", "bourdain", "--override-show", "Parts Unknown"]),
    ("normalize", ["python3", "pipeline/scripts/phase4_normalize.py", "--pipeline", "bourdain"]),
    ("geocode",   ["python3", "pipeline/scripts/phase5_geocode.py", "--pipeline", "bourdain"]),
    ("enrich",    ["python3", "pipeline/scripts/phase6_enrich.py", "--pipeline", "bourdain"]),
    ("load",      ["python3", "pipeline/scripts/phase7_load.py", "--pipeline", "bourdain", "--database", "staging"]),
]

# Ensure we're in the project root
os.chdir(os.path.expanduser("~/dev/projects/kjtcom"))

# Set IAO_ITERATION
os.environ["IAO_ITERATION"] = "v10.64"

# ollama stop before transcription (G18)
# Note: we use qwen3.5:9b as a dummy arg to avoid "accepts 1 arg" error if model exists
print("Stopping Ollama to free GPU for transcription...", flush=True)
subprocess.run(["ollama", "stop", "qwen3.5:9b"], check=False)

for name, cmd in PHASES:
    print(f"\n=== PHASE {name.upper()} ===", flush=True)
    log_file = f"/tmp/pu_phase2_{name}.log"
    # Use unbuffered output for logs (G72 candidate fix)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    with open(log_file, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    
    if r.returncode != 0:
        print(f"PHASE 2 ABORTED at {name} (see {log_file})", flush=True)
        sys.exit(r.returncode)
    print(f"Phase {name} complete.", flush=True)

print("\nPHASE 2 COMPLETE", flush=True)
