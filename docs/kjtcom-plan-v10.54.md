# kjtcom - Execution Plan v10.54

**Recommended Agent:** Claude Code
**Estimated Duration:** 3-4 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md/GEMINI.md saved (v10.54, >= 200 lines)
- [ ] Design + plan in docs/
- [ ] v9.53 docs to archive: mv docs/kjtcom-*-v9.53.md docs/archive/
- [ ] Clean: rm -f docs/drafts/*.md docs/changelog-v*.md
- [ ] Ollama (4 models). Bot restart. IAO_ITERATION=v10.54.
- [ ] Verify evaluator-harness.md line count: wc -l docs/evaluator-harness.md (target >= 400)

---

## STEP 1: Harness Regression Fix (W3) - 10 min

```fish
wc -l docs/evaluator-harness.md
# If < 400, restore from git history
git log --oneline docs/evaluator-harness.md | head -5
# Find the v9.52 commit where it was 528 lines, restore
```

---

## STEP 2: Claw3D Static Rebuild (W1) - 60 min

Read current app/web/claw3d.html. Rebuild from scratch per design doc W1.

Key implementation points:

1. **Scene setup:** Three.js with OrbitControls. Camera positioned above at ~30 degree angle looking at center. Background #0D1117.

2. **Elliptical disc layout:** calculate positions mathematically:
```javascript
// Inner ring (5 agents) at radius 3, evenly spaced
// Asteroid belt (5 MCPs) at radius 5
// Outer ring (4 gas giants) at radius 8
// Moons clustered sun-side of each giant
for (let i = 0; i < nodes.length; i++) {
    const angle = (i / nodes.length) * Math.PI * 2;
    node.position.x = Math.cos(angle) * ringRadius;
    node.position.z = Math.sin(angle) * ringRadius * 0.6; // elliptical
    node.position.y = 0; // flat disc
}
```

3. **Object materials:**
   - Active: `MeshStandardMaterial({ color: nodeColor, emissive: nodeColor, emissiveIntensity: 0.3 })`
   - Inactive: `MeshBasicMaterial({ color: 0x000000, wireframe: true, opacity: 0.3, transparent: true })`

4. **Connectors:**
   - Active: animated (use shader or `dashSize`/`gapSize` animation on `LineDashedMaterial`)
   - Inactive: `LineBasicMaterial({ color: 0x333333, transparent: true, opacity: 0.2 })`

5. **Hover tooltips:**
   - Raycaster on mousemove
   - HTML div overlay positioned at mouse
   - Shows: name, type, function, status, file path

6. **Iteration dropdown:**
   - Load data/claw3d_iterations.json
   - On change: update each node's material (solid vs wireframe)
   - Update each connector's material (animated vs static)

7. **Labels:** optional - small text labels near each planet/moon for readability. Use CSS2DRenderer or sprite text.

8. **Verify:** open in browser. All 46 nodes visible. No overlap. No off-screen objects. Hover works. Dropdown works.

---

## STEP 3: Phase 9 Retrospective (W2) - 60 min

1. Read all docs from archive:

```fish
ls docs/archive/ | grep -c "v9\."
ls docs/archive/ | grep "design.*v9\."
ls docs/archive/ | grep "report.*v9\."
```

2. For each iteration v9.27 through v9.53:
   - Read design doc: extract workstream table
   - Read report: extract scorecard outcomes
   - Cross-reference: planned vs actual

3. Produce docs/phase9-retrospective.md per design doc W2 structure

4. This is a large doc (likely 200-400 lines). Take time. Be thorough.

---

## STEP 4: Post-Flight + Phase 10 Docs (W4) - 20 min

```fish
python3 scripts/post_flight.py  # 8/8+ including MCPs
cd ~/dev/projects/kjtcom/app && flutter analyze && flutter test && flutter build web
cd ~/dev/projects/kjtcom && firebase deploy --only hosting
```

Update README to Phase 10 v10.54. Append changelog. Re-embed archive.

---

## STEP 5: Evaluation + Artifacts

```fish
python3 -u scripts/run_evaluator.py --iteration v10.54 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Artifacts:
- [ ] docs/kjtcom-design-v10.54.md (pre-staged)
- [ ] docs/kjtcom-plan-v10.54.md (pre-staged)
- [ ] docs/kjtcom-build-v10.54.md (promoted)
- [ ] docs/kjtcom-report-v10.54.md (promoted)
- [ ] docs/kjtcom-changelog.md (appended)
- [ ] docs/phase9-retrospective.md (NEW - major deliverable)
- [ ] app/web/claw3d.html (REBUILT - static, 46 nodes, tooltips)
- [ ] docs/evaluator-harness.md (VERIFIED/RESTORED >= 400 lines)
- [ ] README.md (Phase 10)
- [ ] CLAUDE.md + GEMINI.md (v10.54, >= 200 lines)

---

*Plan v10.54, April 6, 2026.*
