# EVENING DEPLOY REQUIRED (v10.66)

v10.66 is complete. Auto-deploy was skipped because Firebase CI token is missing
at `~/.config/firebase-ci-token.txt`.

## Action

```fish
cd ~/dev/projects/kjtcom/app
flutter build web --release
firebase deploy --only hosting
cd ..
set -x IAO_ITERATION v10.66
python3 scripts/postflight_checks/deployed_flutter_matches.py
python3 scripts/postflight_checks/deployed_claw3d_matches.py
```

Both `deployed_*` checks should flip to PASS after deploy.

## Iteration Status

- All 11 workstreams complete
- 5 artifacts on disk (design, plan, build, report, context)
- Context bundle: 374,779 bytes (>300KB target, §1-§11 populated)
- Harness: 1,111 lines, ADRs 023-025, Patterns 28-30 added
- claw3d.html in repo: v10.66 (G101 fixed)
- claw3d.html on live site: v10.64 (deferred until manual deploy above)
- Flutter app on live site: v10.65 (deferred until manual deploy above)
- Zero git writes by agent (Pillar 0)
- Zero interventions

## Optional: enable v10.67 auto-deploy

```fish
firebase login:ci
# save the printed token to ~/.config/firebase-ci-token.txt
chmod 600 ~/.config/firebase-ci-token.txt
```
