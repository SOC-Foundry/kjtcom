cd ~/dev/projects/kjtcom
mv docs/calgold-*.md docs/archive/ 2>/dev/null
mv docs/ricksteves-*.md docs/archive/ 2>/dev/null
cp ~/Downloads/calgold-plan-v5.14.md docs/
cp ~/Downloads/calgold-design-v5.14.md docs/

# Create the runner script (copy from plan Section A)
# Then:
chmod +x pipeline/scripts/group_b_runner.sh
bash -n pipeline/scripts/group_b_runner.sh && echo "Syntax OK"

# Verify timeout env var is wired in phase2_transcribe.py
grep "TRANSCRIBE_TIMEOUT" pipeline/scripts/phase2_transcribe.py

# Launch pass 1
mkdir -p pipeline/data/calgold/logs
tmux new -s calgold './pipeline/scripts/group_b_runner.sh calgold 600 2>&1 | tee pipeline/data/calgold/logs/prod_5.14_600s.log'
