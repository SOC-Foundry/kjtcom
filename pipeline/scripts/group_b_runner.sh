#!/usr/bin/env bash
# group_b_runner.sh -- Graduated production run for kjtcom pipelines.
# Usage: ./pipeline/scripts/group_b_runner.sh PIPELINE [TIMEOUT_SECONDS]
# Default timeout: 600
#
# Run in tmux:
#   tmux new -s calgold './pipeline/scripts/group_b_runner.sh calgold 600 2>&1 | tee pipeline/data/calgold/logs/prod_5.14_600s.log'

set -euo pipefail
cd "$(dirname "$0")/../.."  # Navigate to repo root (kjtcom/)

PIPELINE=${1:?Usage: group_b_runner.sh PIPELINE [TIMEOUT]}
TIMEOUT=${2:-600}
TOTAL_START=$(date +%s)
LOG_DIR="pipeline/data/${PIPELINE}/logs"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "kjtcom Production Run"
echo "Pipeline: ${PIPELINE}"
echo "Timeout: ${TIMEOUT}s"
echo "Started: $(date)"
echo "=========================================="

# -- Kill any GPU-hogging processes --
pkill -f "ollama" 2>/dev/null || true
sleep 2
nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | while read pid; do
    if [ -n "$pid" ]; then
        echo "WARNING: GPU process $pid still running, killing..."
        kill "$pid" 2>/dev/null || true
    fi
done
sleep 2

# -- Ensure LD_LIBRARY_PATH is set --
export LD_LIBRARY_PATH="/usr/local/lib/ollama/mlx_cuda_v13:/usr/local/lib/ollama/cuda_v12:${LD_LIBRARY_PATH:-}"

# -- Phase 1: Acquire --
echo ""
echo "=== Phase 1: Acquire ==="
python3 pipeline/scripts/phase1_acquire.py --pipeline "$PIPELINE" --limit 0
PHASE1_END=$(date +%s)
echo "Acquire complete: $(date) ($(( (PHASE1_END - TOTAL_START) / 60 )) min)"

# -- Phase 2: Transcribe --
echo ""
echo "=== Phase 2: Transcribe (timeout: ${TIMEOUT}s) ==="
TRANSCRIBE_TIMEOUT=$TIMEOUT python3 -u pipeline/scripts/phase2_transcribe.py --pipeline "$PIPELINE" --limit 0
PHASE2_END=$(date +%s)
echo "Transcribe complete: $(date) ($(( (PHASE2_END - PHASE1_END) / 60 )) min)"

# -- Phase 3: Extract --
echo ""
echo "=== Phase 3: Extract ==="
python3 pipeline/scripts/phase3_extract.py --pipeline "$PIPELINE" --limit 0
PHASE3_END=$(date +%s)
echo "Extract complete: $(date) ($(( (PHASE3_END - PHASE2_END) / 60 )) min)"

# -- Phase 4: Normalize --
echo ""
echo "=== Phase 4: Normalize ==="
python3 pipeline/scripts/phase4_normalize.py --pipeline "$PIPELINE" --limit 0
PHASE4_END=$(date +%s)
echo "Normalize complete: $(date) ($(( (PHASE4_END - PHASE3_END) / 60 )) min)"

# -- Phase 5: Geocode --
echo ""
echo "=== Phase 5: Geocode ==="
python3 pipeline/scripts/phase5_geocode.py --pipeline "$PIPELINE" --limit 0
PHASE5_END=$(date +%s)
echo "Geocode complete: $(date) ($(( (PHASE5_END - PHASE4_END) / 60 )) min)"

# -- Summary --
TOTAL_END=$(date +%s)
ELAPSED_MIN=$(( (TOTAL_END - TOTAL_START) / 60 ))
ELAPSED_HR=$(( ELAPSED_MIN / 60 ))

echo ""
echo "=========================================="
echo "Production Run Complete"
echo "Pipeline: ${PIPELINE}"
echo "Timeout: ${TIMEOUT}s"
echo "Finished: $(date)"
echo "Total runtime: ${ELAPSED_HR}h ${ELAPSED_MIN}m"
echo "=========================================="
echo ""
echo "Counts:"
echo "  Audio files:  $(ls pipeline/data/${PIPELINE}/audio/*.mp3 2>/dev/null | wc -l)"
echo "  Transcripts:  $(ls pipeline/data/${PIPELINE}/transcripts/*.json 2>/dev/null | wc -l)"
echo "  Extractions:  $(ls pipeline/data/${PIPELINE}/extracted/*.json 2>/dev/null | wc -l)"
echo "  Normalized:   $(ls pipeline/data/${PIPELINE}/normalized/*.jsonl 2>/dev/null | wc -l)"
echo "  Geocoded:     $(ls pipeline/data/${PIPELINE}/geocoded/*.jsonl 2>/dev/null | wc -l)"
echo ""
echo "NEXT: Review log, then relaunch with higher timeout or proceed to Phase 6-7."
