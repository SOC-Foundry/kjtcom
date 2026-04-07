"""Phase 3: Extract structured entities via Gemini Flash API.

Input: pipeline/data/{pipeline}/transcripts/*.json
       pipeline/config/{pipeline}/extraction_prompt.md
Output: pipeline/data/{pipeline}/extracted/*.json
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.utils.checkpoint import Checkpoint


def main():
    parser = argparse.ArgumentParser(description="Extract entities via Gemini Flash")
    parser.add_argument("--pipeline", required=True, help="Pipeline ID")
    parser.add_argument("--limit", type=int, default=0, help="Max files to extract (0=all)")
    parser.add_argument("--timeout", type=int, default=300, help="API timeout in seconds")
    args = parser.parse_args()

    from google import genai

    base = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(base, "config", args.pipeline)
    transcript_dir = os.path.join(base, "data", args.pipeline, "transcripts")
    output_dir = os.path.join(base, "data", args.pipeline, "extracted")
    os.makedirs(output_dir, exist_ok=True)

    # Load extraction prompt
    prompt_path = os.path.join(config_dir, "extraction_prompt.md")
    with open(prompt_path) as f:
        system_prompt = f.read()

    checkpoint = Checkpoint(args.pipeline, "extract")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    transcript_files = sorted(glob.glob(os.path.join(transcript_dir, "*.json")))
    count = 0

    for transcript_path in transcript_files:
        video_id = os.path.splitext(os.path.basename(transcript_path))[0]
        if checkpoint.is_done(video_id):
            continue

        if args.limit and count >= args.limit:
            break

        with open(transcript_path) as f:
            transcript = json.load(f)

        # Build full text from segments
        full_text = " ".join(seg["text"] for seg in transcript["segments"])

        print(f"Extracting {video_id} ({len(full_text)} chars)...")

        prompt = f"{system_prompt}\n\n---\nVideo ID: {video_id}\nTranscript:\n{full_text}"

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            # Parse JSON from response
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            entities = json.loads(text)

            # G62: Force show name for pu_ prefixed files
            if video_id.startswith("pu_"):
                show_name = "Parts Unknown"
                # Check for "A Cooks Tour" in filename to be more precise
                if "A Cooks Tour" in video_id or "A Cook's Tour" in video_id:
                    show_name = "A Cook's Tour"
                
                for ent in entities:
                    ent["shows"] = [show_name]

        except Exception as e:
            print(f"  FAILED: {e}")
            continue

        output_path = os.path.join(output_dir, f"{video_id}.json")
        with open(output_path, "w") as f:
            json.dump(entities, f, indent=2)

        checkpoint.mark_done(video_id)
        count += 1
        print(f"  OK - {len(entities)} entities ({count})")

    print(f"Extracted {count} new files. Total: {checkpoint.count()}")


if __name__ == "__main__":
    main()
