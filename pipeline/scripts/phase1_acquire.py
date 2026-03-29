"""Phase 1: Acquire audio from YouTube playlist via yt-dlp.

Input: pipeline/config/{pipeline}/playlist_urls.txt
Output: pipeline/data/{pipeline}/audio/*.mp3
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.checkpoint import Checkpoint


def main():
    parser = argparse.ArgumentParser(description="Download audio from YouTube playlist")
    parser.add_argument("--pipeline", required=True, help="Pipeline ID (e.g., calgold)")
    parser.add_argument("--limit", type=int, default=0, help="Max videos to download (0=all)")
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

    count = 0
    for line in lines:
        video_id = line.split()[0]
        if checkpoint.is_done(video_id):
            continue

        if args.limit and count >= args.limit:
            break

        output_path = os.path.join(output_dir, f"{video_id}.mp3")
        url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"Downloading {video_id}...")
        result = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", output_path, url],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            checkpoint.mark_done(video_id)
            count += 1
            print(f"  OK ({count})")
        else:
            print(f"  FAILED: {result.stderr[:200]}")

    print(f"Acquired {count} new videos. Total: {checkpoint.count()}")


if __name__ == "__main__":
    main()
