# kjtcom - Design Document v9.53

**Phase:** 9 - App Optimization (FINAL)
**Iteration:** 53
**Date:** April 5, 2026
**Recommended Agent:** Claude Code
**Focus:** Claw3D Orbital Mechanics Fix + Final Qwen Harness Tuning

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Claw3D orbital mechanics fix | P1 | Slow orbits, tighten spread, add connectors, tidal lock (no axis spin). |
| W2 | Final Qwen harness tuning | P1 | Address v9.52 "What Could Be Better" items. Fix schema retry logic. One more validation pass. |
| W3 | Post-flight + Phase 9 close-out | P2 | Post-flight with MCP checks. If all passes, Phase 9 is formally complete. |

---

## W1: Claw3D Orbital Mechanics Fix (P1)

Four specific fixes to app/web/claw3d.html:

### 1. Slow Down Orbits
Current orbital speed is too fast. Reduce all orbit speeds by 60-80%:
```javascript
// Current (too fast):
planet.angle += planet.orbitSpeed;
// Fixed (slower):
planet.angle += planet.orbitSpeed * 0.25;  // 75% slower
```

Apply to both planet orbits around sun AND moon orbits around planets. Moons should orbit slightly faster than planets (they're closer to their parent) but still visually comfortable.

### 2. Tighten Spread
Planets are too far apart. Reduce orbital radii by ~40%:
```javascript
// Current inner planet radius might be 200-300
// Reduce to 120-180
// Current outer planet (gas giant) radius might be 400-600
// Reduce to 250-400
```

The goal: all planets visible in the initial viewport without scrolling/zooming. The solar system should feel compact and readable, not sprawling.

### 3. Add Connectors
Draw subtle lines between:
- Sun (Qwen) to each planet (agents, gas giants)
- Each gas giant to its moons (components)

Use Three.js Line or LineBasicMaterial:
```javascript
const lineMaterial = new THREE.LineBasicMaterial({
    color: 0x4ADE80,  // kjtcom green
    transparent: true,
    opacity: 0.15  // very subtle
});
```

Lines should stretch/follow as planets orbit (update endpoints each frame). These represent data flow and relationships.

### 4. Tidal Lock (No Axis Spin)
Planets should NOT rotate on their own axis. They orbit the sun but always face the same direction - like our Moon faces Earth.

```javascript
// Remove any:
planet.mesh.rotation.y += spinSpeed;
// Or set rotation to face sun:
// planet.mesh.lookAt(sun.position);  // if you want them to face the sun
// Or simply don't rotate the mesh at all - just update orbital position
```

Same for moons orbiting planets - they orbit but don't spin.

---

## W2: Final Qwen Harness Tuning (P1)

### Items from v9.52 "What Could Be Better"

1. **Schema retry logic** - "The Qwen evaluator failed to conform to the schema within 3 attempts." The retry prompt corrections need to be more specific. Currently the error feedback is generic. Fix: include the exact field path and expected vs actual value in the retry prompt. Example: "Field 'workstreams[0].score' must be integer 0-9 but got '10'. Field 'workstreams[2].mcps[0]' must be one of [Firebase, Context7, ...] but got 'telegram'."

2. **Claw3D missing iteration fallback** - If an iteration isn't in claw3d_iterations.json, show all nodes at 50% opacity instead of logging to console. Add a fallback clause.

3. **MCP functional checks** - post_flight.py currently checks MCP version flags. Upgrade to functional checks where possible (e.g., Firebase MCP: attempt a read query; Context7: attempt a doc lookup). Some MCPs may not support functional testing without side effects - document which ones.

### Harness Review

Read docs/evaluator-harness.md (528 lines) end-to-end. Look for:
- Any contradictions between sections
- Any rules that are too vague (need examples)
- Any failure patterns from v9.52 not yet documented
- Verify ADR section is comprehensive (9 ADRs from v9.52)

Add any new patterns observed in v9.52 evaluation to the failure catalog.

### Validation

Run retroactive evaluation on v9.52:
```fish
python3 -u scripts/run_evaluator.py --iteration v9.52 --workstreams --retroactive
```

Compare with actual v9.52 report. The scores and outcomes should be similar (not identical - Qwen is probabilistic - but in the same ballpark). If wildly different, investigate which harness rules are being ignored.

---

## W3: Post-Flight + Phase 9 Close-Out (P2)

### Post-Flight
```fish
python3 scripts/post_flight.py
```

All checks must pass including MCP verification.

### Phase 9 Close-Out Criteria

| Criterion | Status |
|-----------|--------|
| All living docs current | Verify |
| Qwen produces valid scorecards | Confirmed v9.52 |
| File management clean | Verify docs/ and archive/ |
| Post-flight passes (8/8+) | Verify |
| Harness files >= 200 lines | Confirmed |
| Evaluator harness >= 400 lines | Confirmed (528) |
| Bot operational | Verify |
| Pipeline review complete | Confirmed v9.47 |
| Middleware registry complete | Verify |
| All systems verified | Confirmed v9.52 (5 MCPs, 5 LLMs, 8/8 post-flight) |

If ALL checked, add to build log: "Phase 9 (v9.27-v9.53, 27 iterations) is formally COMPLETE. Phase 10 begins next iteration."

### Deploy

```fish
cd ~/dev/projects/kjtcom/app
flutter analyze && flutter test && flutter build web
cd ~/dev/projects/kjtcom && firebase deploy --only hosting
```

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K tokens. |
| Delivery | 3 workstreams. Claw3D polished. Qwen tuned. Phase 9 closed. |
| Performance | Claw3D orbits visually comfortable. All planets visible without zoom. Connectors between sun/planets/moons. Qwen schema retry produces valid output. |

---

*Design document v9.53, April 5, 2026.*
