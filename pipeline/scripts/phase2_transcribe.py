"""Phase 2: Transcribe audio to timestamped JSON via faster-whisper (CUDA).

Input: pipeline/data/{pipeline}/audio/*.mp3
Output: pipeline/data/{pipeline}/transcripts/*.json
Requires: NVIDIA CUDA (NZXTcos RTX 2080 SUPER or tsP3-cos RTX 2000 Ada)
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.checkpoint import Checkpoint


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio to timestamped JSON")
    parser.add_argument("--pipeline", required=True, help="Pipeline ID")
    parser.add_argument("--model", default="large-v3", help="Whisper model size")
    parser.add_argument("--limit", type=int, default=0, help="Max files to transcribe (0=all)")
    args = parser.parse_args()

    base = os.path.dirname(os.path.dirname(__file__))
    audio_dir = os.path.join(base, "data", args.pipeline, "audio")
    output_dir = os.path.join(base, "data", args.pipeline, "transcripts")
    os.makedirs(output_dir, exist_ok=True)

    checkpoint = Checkpoint(args.pipeline, "transcribe")

    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device="cuda", compute_type="float16")

    audio_files = sorted(glob.glob(os.path.join(audio_dir, "*.mp3")))
    count = 0

    for audio_path in audio_files:
        video_id = os.path.splitext(os.path.basename(audio_path))[0]
        if checkpoint.is_done(video_id):
            continue

        if args.limit and count >= args.limit:
            break

        print(f"Transcribing {video_id}...")
        segments, info = model.transcribe(audio_path, beam_size=5)

        transcript = {
            "video_id": video_id,
            "language": info.language,
            "duration": info.duration,
            "segments": [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text.strip(),
                }
                for seg in segments
            ],
        }

        output_path = os.path.join(output_dir, f"{video_id}.json")
        with open(output_path, "w") as f:
            json.dump(transcript, f, indent=2)

        checkpoint.mark_done(video_id)
        count += 1
        print(f"  OK - {len(transcript['segments'])} segments ({count})")

    print(f"Transcribed {count} new files. Total: {checkpoint.count()}")


if __name__ == "__main__":
    main()
