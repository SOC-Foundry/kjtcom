# kjtcom - Execution Plan v9.45

**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 3 hours
**Token Target:** <50K

---

## PRE-FLIGHT

- [ ] CLAUDE.md saved (v9.45)
- [ ] GEMINI.md saved (v9.45)
- [ ] docs/kjtcom-design-v9.45.md saved
- [ ] docs/kjtcom-plan-v9.45.md saved
- [ ] v9.44 docs archived: mv docs/kjtcom-*-v9.44.md docs/archive/
- [ ] Archive integrity: ls docs/archive/ | wc -l (should be >= 169)
- [ ] Ollama running, 4 models
- [ ] sudo systemctl restart kjtcom-telegram-bot
- [ ] set -gx IAO_ITERATION v9.45
- [ ] Firebase SA accessible

---

## STEP 1: Research Breaking Changes (W1 prep) - 15 min

Before touching pubspec.yaml, understand what's changing.

```fish
cd ~/dev/projects/kjtcom/app

# Find all files that import geospatial packages
grep -r "mgrs_dart\|proj4dart" lib/ --include="*.dart" -l
grep -r "mgrs_dart\|proj4dart" lib/ --include="*.dart"

# Check current pubspec constraints
grep -A1 "mgrs_dart\|proj4dart" pubspec.yaml

# Use Context7 MCP for migration docs
# Or read changelogs directly
```

Document: which files import these packages, which APIs are used, what the 3.x migration guide says.

---

## STEP 2: Upgrade proj4dart 2->3 (W1) - 20 min

proj4dart first because mgrs_dart may depend on it.

```fish
cd ~/dev/projects/kjtcom/app

# Update pubspec.yaml constraint
# proj4dart: ^3.0.0

flutter pub get
flutter analyze
# Fix any breaking changes
flutter test
```

If breaking changes found:
- Read the error messages carefully
- Check if class names changed
- Check if method signatures changed
- Fix each file, re-run analyze after each fix
- Document every change in build log

---

## STEP 3: Upgrade mgrs_dart 2->3 (W1) - 20 min

```fish
# Update pubspec.yaml constraint
# mgrs_dart: ^3.0.0

flutter pub get
flutter analyze
# Fix breaking changes
flutter test
```

After both geospatial packages upgraded:

```fish
flutter build web
```

If build succeeds, run locally and check Map tab:

```fish
flutter run -d chrome
# Navigate to Map tab, click markers, verify coordinates
```

---

## STEP 4: Upgrade analyzer + _fe_analyzer_shared (W2) - 15 min

```fish
# These may be transitive - check if direct deps
grep "analyzer\|_fe_analyzer_shared" pubspec.yaml

# If direct:
# analyzer: ^12.0.0
# If transitive, upgrading other packages may pull them in

flutter pub upgrade
flutter analyze
flutter test
```

If blocked by SDK constraint or other package constraints, log which package is blocking and whether the SDK constraint needs updating.

---

## STEP 5: Batch Minor Upgrades (W3) - 10 min

```fish
cd ~/dev/projects/kjtcom/app

# Update constraints in pubspec.yaml for:
# meta: ^1.18.0
# vector_math: ^2.3.0
# unicode: ^1.1.0
# test packages auto-update with flutter pub upgrade

flutter pub upgrade
flutter analyze
flutter test
flutter build web
```

---

## STEP 6: Full Post-Upgrade Verification (W4) - 20 min

```fish
cd ~/dev/projects/kjtcom/app

# 1. Clean build
flutter clean
flutter pub get
flutter analyze
echo "Analyze: $status"

flutter test
echo "Tests: $status"

flutter build web
echo "Build: $status"

# 2. Check outdated
flutter pub outdated
# Target: 0 packages with newer incompatible versions
```

### Manual Verification (local)

```fish
flutter run -d chrome
```

Check each tab:
- [ ] Results tab: query works, results display
- [ ] Map tab: tiles render, markers display, click works (coordinate display correct)
- [ ] Globe tab: continent cards, country grid
- [ ] IAO tab: trident graphic, pillar cards
- [ ] Gotcha tab: filter toggle works
- [ ] Schema tab: field cards, click-to-query

### Dart MCP Verification

```fish
# Verify Dart MCP can analyze with new deps
# Check .mcp.json for Dart server config
```

### Deploy

```fish
cd ~/dev/projects/kjtcom/app
flutter build web
cd ~/dev/projects/kjtcom
firebase deploy --only hosting
```

---

## STEP 7: Phase 10 Readiness Audit (W5) - 20 min

Go through the checklist in the design doc. For each component:
1. Check current state
2. Mark ready/not-ready
3. If not ready, log what's needed as a v9.46/v9.47 workstream

Output: Phase 10 Readiness Assessment section in build log.

Key checks:
```fish
# install.fish completeness
wc -l docs/install.fish

# middleware_registry.json
python3 -c "import json; r=json.load(open('data/middleware_registry.json')); print(f'Components: {sum(len(v) for v in r.values())}')"

# gotcha_archive.json
python3 -c "import json; g=json.load(open('data/gotcha_archive.json')); print(f'Resolved: {len(g.get(\"resolved_gotchas\", []))}')"

# ChromaDB
python3 -c "import chromadb; c=chromadb.PersistentClient('data/chromadb'); col=c.get_or_create_collection('archive'); print(f'Chunks: {col.count()}')"

# All MCPs
# Test each in .mcp.json
```

---

## STEP 8: Qwen Trident Fix + Living Docs (W6) - 15 min

1. Update scripts/run_evaluator.py:
   - Trident prompt: "State the actual result, not 'Review...' or 'TBD'"
   - Cost: count tokens from event log
   - Delivery: count complete/total from scorecard
   - Performance: state the measured metric

2. Re-embed archive:

```fish
python3 -u scripts/embed_archive.py
```

3. Rebuild architecture HTML:

```fish
python3 scripts/build_architecture_html.py
```

4. Update README.md: Phase 9 v9.45, dep status

---

## STEP 9: Post-Flight Verification (MANDATORY) - 10 min

```fish
python3 scripts/post_flight.py
```

All checks must pass. Additionally verify:
- [ ] Map tab works with upgraded geospatial libs (live site)
- [ ] architecture.html loads
- [ ] Bot responds to /ask

---

## STEP 10: Workstream Evaluation + Artifacts - 15 min

```fish
python3 -u scripts/run_evaluator.py --iteration v9.45 --workstreams
python3 -u scripts/generate_artifacts.py
python3 -u scripts/generate_artifacts.py --validate-only
python3 -u scripts/generate_artifacts.py --promote
```

Verify: Evidence column populated, W# names match design doc, Trident has actual values (not "Review..."), changelog has NEW/UPDATED/FIXED prefixes.

Artifacts:
- [ ] docs/kjtcom-design-v9.45.md (pre-staged)
- [ ] docs/kjtcom-plan-v9.45.md (pre-staged)
- [ ] docs/kjtcom-build-v9.45.md (with Phase 10 Readiness Assessment)
- [ ] docs/kjtcom-report-v9.45.md (Trident filled, Evidence column)
- [ ] docs/kjtcom-changelog.md (append)
- [ ] agent_scores.json (append)
- [ ] pubspec.yaml (MODIFIED - 10 deps updated)
- [ ] Any Dart files modified for breaking changes
- [ ] scripts/run_evaluator.py (MODIFIED - Trident fix)
- [ ] data/middleware_registry.json (MODIFIED - version updates)
- [ ] README.md (MODIFIED)
- [ ] CLAUDE.md (v9.45)
- [ ] GEMINI.md (v9.45)

---

## INTERVENTIONS

Target: 0.

If mgrs_dart 3.x or proj4dart 3.x have incompatible peer dependency requirements, may need to evaluate whether to pin at an intermediate version. Log as gotcha if so.

---

*Plan v9.45, April 5, 2026.*
