"""Phase 1: Acquire audio from YouTube playlist via yt-dlp.

Input: pipeline/config/{pipeline}/playlist_urls.txt
Output: pipeline/data/{pipeline}/audio/*.mp3
"""

import argparse
import os
import subprocess
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.checkpoint import Checkpoint


def log_failure(pipeline, video_id, title, reason, http_status, retry_count):
    entry = {
        "video_id": video_id,
        "title": title,
        "reason": reason,
        "http_status": http_status,
        "retry_count": retry_count,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    path = f"pipeline/data/{pipeline}/parts_unknown_acquisition_failures.jsonl"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def search_gap_fill(query):
    """Search for an alternate upload if the primary is gone."""
    print(f"  Searching gap-fill for: {query}")
    try:
        result = subprocess.run(
            ["yt-dlp", "ytsearch1:" + query, "--get-id"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            alt_id = result.stdout.strip()
            print(f"  Found alternate: {alt_id}")
            return alt_id
    except Exception as e:
        print(f"  Gap-fill search failed: {e}")
    return None


def download_video(video_id, output_path, retry_limit=3):
    url = f"https://www.youtube.com/watch?v={video_id}"
    for attempt in range(retry_limit + 1):
        if attempt > 0:
            wait = 4 ** attempt
            print(f"  Retrying in {wait}s (attempt {attempt}/{retry_limit})...")
            time.sleep(wait)

        result = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", output_path, url],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            return True, None, None
        
        stderr = result.stderr.lower()
        if "deleted" in stderr or "unavailable" in stderr:
            return False, "deleted", result.returncode
        if "geo-restricted" in stderr or "blocked" in stderr:
            return False, "geo_blocked", result.returncode
        if "age-restricted" in stderr:
            return False, "age_gated", result.returncode
            
        # If it's a transient error, we continue the loop to retry
        if attempt == retry_limit:
            return False, "network_error", result.returncode
            
    return False, "unknown", -1


def main():
    parser = argparse.ArgumentParser(description="Download audio from YouTube playlist")
    parser.add_argument("--pipeline", required=True, help="Pipeline ID (e.g., calgold)")
    parser.add_argument("--limit", type=int, default=0, help="Max videos to download (0=all)")
    parser.add_argument("--range", help="Range of items to process (e.g., 29:60)")
    parser.add_argument("--show", help="Filter by show name in title (informational)")
    args = parser.parse_args()

    base = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(base, "config", args.pipeline)
    output_dir = os.path.join(base, "data", args.pipeline, "audio")
    os.makedirs(output_dir, exist_ok=True)

    playlist_file = os.path.join(config_dir, "playlist_urls.txt")
    if not os.path.exists(playlist_file):
        print(f"ERROR: {playlist_file} not found")
        sys.exit(1)

    checkpoint = Checkpoint(args.pipeline, "acquire")

    with open(playlist_file) as f:
        lines = [line.strip() for line in f if line.strip()]

    if args.range:
        try:
            start, end = map(int, args.range.split(":"))
            lines = lines[start-1:end]
            print(f"Targeting range {start}:{end} ({len(lines)} videos)")
        except ValueError:
            print(f"ERROR: Invalid range format {args.range}")
            sys.exit(1)

    count = 0
    for idx, line in enumerate(lines):
        video_id = line.split()[0]
        if checkpoint.is_done(video_id):
            continue

        if args.limit and count >= args.limit:
            break

        output_path = os.path.join(output_dir, f"{video_id}.mp3")
        
        print(f"[{idx+1}/{len(lines)}] Downloading {video_id}...")
        success, reason, status = download_video(video_id, output_path)

        if not success and reason == "deleted":
            # Try gap-fill
            alt_id = search_gap_fill(f"Bourdain Parts Unknown episode {video_id}")
            if alt_id:
                print(f"  Attempting gap-fill alternate: {alt_id}")
                success, reason, status = download_video(alt_id, os.path.join(output_dir, f"{alt_id}.mp3"))
                if success:
                    log_failure(args.pipeline, video_id, "N/A", f"gap_filled_by_{alt_id}", 0, 0)
                    video_id = alt_id # Use the alt_id for checkpointing

        if success:
            checkpoint.mark_done(video_id)
            count += 1
            print(f"  OK ({count})")
        else:
            log_failure(args.pipeline, video_id, "N/A", reason, status, 3)
            print(f"  FAILED: {reason}")

    print(f"Acquired {count} new videos. Total: {checkpoint.count()}")


if __name__ == "__main__":
    main()
