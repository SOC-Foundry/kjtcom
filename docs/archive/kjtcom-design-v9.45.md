# kjtcom - Design Document v9.45

**Phase:** 9 - App Optimization
**Iteration:** 45
**Date:** April 5, 2026
**Focus:** Flutter Dependency Upgrade (10 packages) + Phase 10 Readiness Assessment

---

## AMENDMENTS (all prior amendments remain in effect)

### Dependency Upgrade Protocol - NEW (v9.45+)

Major version dependency upgrades follow this protocol:
1. Read the package CHANGELOG/migration guide BEFORE upgrading (use Context7 MCP)
2. Upgrade ONE package at a time for major versions (2->3). Minor versions can batch.
3. After each major upgrade: `flutter analyze`, `flutter test`, `flutter build web`
4. If analyze shows breaking changes, fix them before proceeding to next package
5. If tests fail, fix before proceeding
6. Document every breaking change encountered and fix applied in build log
7. Do NOT upgrade all 10 at once - that's the v9.37 OOM pattern

### Phase 10 Preparation - NEW (v9.45+)

Phase 10 (IAO Retrospective + Pipeline Template + Bourdain Dry Run) requires:
- All Flutter deps current (no major version gaps)
- Dart MCP fully functional (requires mgrs_dart 3.x + proj4dart 3.x)
- All middleware components documented in middleware_registry.json
- Gotcha archive complete with all resolved issues
- install.fish current with all dependencies
- Architecture HTML rendering latest state
- README reflecting final Phase 9 state

Phase 10 scope (NOT this iteration, 2-3 iterations away):
- Bourdain pipeline: 114 YouTube videos, full 7-phase dry run from scratch
- IaC packaging: all components into GCP project (tachnet-intranet)
- Middleware stamping: portable template validated on intranet
- IAO methodology publication

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Major dep upgrade: mgrs_dart 2->3 + proj4dart 2->3 | P1 | These block Dart MCP functionality. Breaking API changes expected. Map tab likely affected. |
| W2 | Major dep upgrade: analyzer + _fe_analyzer_shared | P1 | analyzer 10->12, _fe_analyzer_shared 93->98. Dev dependencies. May affect flutter analyze behavior. |
| W3 | Minor dep upgrades: meta, test, test_api, test_core, unicode, vector_math | P1 | Batch upgrade. Lower risk. |
| W4 | Post-upgrade verification | P1 | flutter analyze (0 issues), flutter test (15/15), flutter build web (success), manual Map tab verification. |
| W5 | Phase 10 readiness checklist | P2 | Audit all middleware components, verify install.fish, update architecture HTML, assess what's needed before Phase 10. |
| W6 | Post-flight + Qwen Trident fix | P2 | Run post_flight.py. Fix Qwen evaluator to fill Trident from event log (still says "Review..."). |

---

## W1: mgrs_dart 2->3 + proj4dart 2->3 (P1)

These are the critical upgrades. Both are geospatial libraries used in the Map tab for coordinate transformations.

### Migration Research

Before upgrading, read migration docs:
- Context7 MCP: look up mgrs_dart 3.0.0 changelog
- Context7 MCP: look up proj4dart 3.0.0 changelog
- Check pubspec.yaml for current version constraints
- grep the codebase for import usage:

```fish
cd ~/dev/projects/kjtcom/app
grep -r "mgrs_dart\|proj4dart" lib/ --include="*.dart" -l
grep -r "mgrs_dart\|proj4dart" lib/ --include="*.dart"
```

### Upgrade Sequence

```fish
cd ~/dev/projects/kjtcom/app
# 1. Upgrade proj4dart first (mgrs_dart may depend on it)
flutter pub upgrade proj4dart
flutter analyze
flutter test
# Fix any breaking changes
# 2. Then mgrs_dart
flutter pub upgrade mgrs_dart
flutter analyze
flutter test
# Fix any breaking changes
# 3. Build
flutter build web
```

### Expected Breaking Changes

Major version bumps typically change:
- Class/method names or signatures
- Coordinate system conventions
- Null safety adjustments
- Return type changes

The Map tab (app/lib/widgets/map_tab.dart) is the primary consumer. Detail panel coordinate display may also be affected.

---

## W2: analyzer + _fe_analyzer_shared (P1)

These are dev/transitive dependencies. analyzer 10->12 is two major versions. _fe_analyzer_shared 93->98 is also a jump.

```fish
# These are typically pulled in by flutter_lints or custom_lint
flutter pub upgrade analyzer
flutter analyze
flutter test
```

If blocked by dependency constraints in other packages, may need to update flutter_lints or the SDK constraint first.

---

## W3: Minor Dep Upgrades (P1)

Lower risk. Batch upgrade:

```fish
cd ~/dev/projects/kjtcom/app
flutter pub upgrade meta test test_api test_core unicode vector_math
flutter analyze
flutter test
flutter build web
```

These should be straightforward. meta 1.17->1.18 and vector_math 2.2->2.3 are minor bumps. test packages are test-only.

---

## W4: Post-Upgrade Verification (P1)

After ALL upgrades complete:

1. `flutter analyze` - must show 0 issues
2. `flutter test` - must show 15/15 (or more if new tests added)
3. `flutter build web` - must succeed
4. Manual verification:
   - Load kylejeromethompson.com locally (flutter run -d chrome)
   - Navigate to Map tab
   - Click an entity marker - verify coordinates display correctly
   - Verify map tiles render (G43 CORS may still apply)
   - Navigate to all 6 tabs - verify no runtime errors in console
5. Deploy: `firebase deploy --only hosting`
6. Verify live site loads

### Dart MCP Verification

After mgrs_dart 3.x and proj4dart 3.x are installed:

```fish
# Verify Dart MCP can analyze the project
# The Dart MCP server requires compatible analyzer versions
```

---

## W5: Phase 10 Readiness Checklist (P2)

Audit and document what's ready vs. what needs work before Phase 10.

### Checklist

| Component | Status | Notes |
|-----------|--------|-------|
| Flutter deps | ? | After W1-W3, should be all current |
| Dart MCP | ? | Verify after mgrs_dart/proj4dart upgrade |
| All 5 MCPs operational | ? | Test each one |
| install.fish current | ? | Verify all pip/npm/pacman packages listed |
| architecture.mmd current | ? | Check v9.44 state |
| architecture.html deployed | ? | Verify at kylejeromethompson.com/architecture.html |
| middleware_registry.json complete | ? | All components listed with versions |
| gotcha_archive.json complete | ? | All resolved gotchas documented |
| agent_scores.json accurate | ? | Workstream data from v9.41-v9.44 |
| README current | ? | Phase 9 v9.45 state |
| CLAUDE.md comprehensive | ? | All amendments through v9.44 |
| GEMINI.md comprehensive | ? | All amendments through v9.44 |
| ChromaDB index current | ? | All docs through v9.44 embedded |
| Telegram bot stable | ? | systemd, session memory, 3-route, rating sort |
| Schema reference complete | ? | All fields, sortable_fields, per-pipeline coverage |
| Template directory portable | ? | Can stamp onto new project |

### Phase 10 Blockers (identify any)

If any component is not ready, log it as a v9.46 or v9.47 workstream. Phase 10 should start clean.

---

## W6: Post-Flight + Qwen Trident Fix (P2)

### Post-Flight

Run post_flight.py. All checks pass.

### Qwen Trident Fix

The Trident evaluation in every Qwen-generated report still says "Review token usage in event log" / "Review workstream scorecard above" instead of actual values. This has persisted through v9.42, v9.43, and v9.44.

Fix: update the evaluator prompt in run_evaluator.py to explicitly instruct:
- Cost: state actual token count from event log or "within target" / "exceeded target"
- Delivery: state "X/Y workstreams complete" (count from scorecard)
- Performance: state the specific performance metric result (entity count, sort result, etc.)

"Review..." is equivalent to "TBD" and is banned.

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K Claude tokens. |
| Delivery | 6 workstreams. All 10 deps current. Dart MCP functional. |
| Performance | flutter pub outdated shows 0 packages with newer incompatible versions. Map tab renders correctly with updated geospatial libs. |

---

*Design document v9.45, April 5, 2026.*
