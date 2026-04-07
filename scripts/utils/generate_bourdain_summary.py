import os
import json
import glob

def main():
    audio_count = len(glob.glob("pipeline/data/bourdain/audio/*.mp3"))
    transcript_count = len(glob.glob("pipeline/data/bourdain/transcripts/*.json"))
    
    # Check for failures
    failure_path = "pipeline/data/bourdain/parts_unknown_acquisition_failures.jsonl"
    failures = []
    if os.path.exists(failure_path):
        with open(failure_path) as f:
            for line in f:
                failures.append(json.loads(line))
    
    # Histogram of failure reasons
    reasons = {}
    for f in failures:
        r = f.get("reason", "unknown")
        reasons[r] = reasons.get(r, 0) + 1
    
    summary = {
        "iteration": "v10.64",
        "timestamp": "2026-04-06T22:45:00Z",
        "pipeline": "bourdain",
        "stats": {
            "audio_files": audio_count,
            "transcripts": transcript_count,
            "failures": len(failures),
        },
        "failure_histogram": reasons,
        "recent_failures": failures[-5:] if failures else []
    }
    
    out_path = "app/assets/bourdain_phase2_summary.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
