# tmux Quick Reference - v5.17 (RickSteves Production Run)

# Pre-flight
cd ~/dev/projects/kjtcom
df -h /home | tail -1
echo "Audio: "(command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l)
echo "Trans: "(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l)

# Archive docs and stage new ones
mv docs/ricksteves-*.md docs/archive/ 2>/dev/null
mv docs/calgold-*.md docs/archive/ 2>/dev/null
cp ~/Downloads/ricksteves-design-v5.17.md docs/
cp ~/Downloads/ricksteves-plan-v5.17.md docs/
git add docs/ && git commit -m "KT 5.17 docs in place" && git push

# Pass 1 (600s) - auto-restart wrapper for OOM recovery
# Expected runtime: 5-7 days
mkdir -p pipeline/data/ricksteves/logs
tmux new -s ricksteves 'cd ~/dev/projects/kjtcom && while true; do echo "=== LAUNCH $(date) ===" >> pipeline/data/ricksteves/logs/prod_5.17_600s.log; ./pipeline/scripts/group_b_runner.sh ricksteves 600 2>&1 | tee -a pipeline/data/ricksteves/logs/prod_5.17_600s.log; EXIT_CODE=$?; if [ $EXIT_CODE -eq 0 ]; then echo "Runner completed successfully"; break; fi; echo "Runner exited with code $EXIT_CODE, restarting in 60s..."; sleep 60; done'

# Daily monitoring (from another terminal)
echo "=== $(date) ===" && echo "Audio: "(command ls pipeline/data/ricksteves/audio/*.mp3 | wc -l) && echo "Trans: "(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l) && echo "Extra: "(command ls pipeline/data/ricksteves/extracted/*.json | wc -l) && echo "OOM restarts: "(grep -c "LAUNCH" pipeline/data/ricksteves/logs/prod_5.17_600s.log) && df -h /home | tail -1

# After Pass 1 completes
tail -50 pipeline/data/ricksteves/logs/prod_5.17_600s.log
grep -c "timed out\|TIMEOUT" pipeline/data/ricksteves/logs/prod_5.17_600s.log
git add . && git commit -m "KT 5.17 pass 1 complete (600s) - $(command ls pipeline/data/ricksteves/transcripts/*.json | wc -l) transcripts" && git push

# Pass 2 (1200s) - if timeouts > 0
tmux new -s ricksteves 'cd ~/dev/projects/kjtcom && while true; do echo "=== LAUNCH $(date) ===" >> pipeline/data/ricksteves/logs/prod_5.17_1200s.log; ./pipeline/scripts/group_b_runner.sh ricksteves 1200 2>&1 | tee -a pipeline/data/ricksteves/logs/prod_5.17_1200s.log; EXIT_CODE=$?; if [ $EXIT_CODE -eq 0 ]; then echo "Runner completed successfully"; break; fi; echo "Runner exited with code $EXIT_CODE, restarting in 60s..."; sleep 60; done'

# Pass 3 (1800s) - if still timeouts
tmux new -s ricksteves 'cd ~/dev/projects/kjtcom && while true; do echo "=== LAUNCH $(date) ===" >> pipeline/data/ricksteves/logs/prod_5.17_1800s.log; ./pipeline/scripts/group_b_runner.sh ricksteves 1800 2>&1 | tee -a pipeline/data/ricksteves/logs/prod_5.17_1800s.log; EXIT_CODE=$?; if [ $EXIT_CODE -eq 0 ]; then echo "Runner completed successfully"; break; fi; echo "Runner exited with code $EXIT_CODE, restarting in 60s..."; sleep 60; done'

# Quality sweep (after all passes)
python3 pipeline/scripts/phase4_normalize.py --pipeline ricksteves --limit 0
python3 pipeline/scripts/phase5_geocode.py --pipeline ricksteves --limit 0
