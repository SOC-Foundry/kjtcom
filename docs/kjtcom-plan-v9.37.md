# kjtcom - Execution Plan v9.37

**Phase:** 9 - App Optimization
**Iteration:** 37
**Date:** April 5, 2026
**Executing Agent:** Claude Code (Opus 4.6)
**Estimated Duration:** 3-4 hours

---

## PRE-FLIGHT CHECKLIST

- [ ] Ollama running with 3 models
- [ ] .mcp.json present with 4+ servers
- [ ] v9.36 docs archived
- [ ] Git clean
- [ ] Working directory: ~/dev/projects/kjtcom

---

## STEP 1: Firebase Reauth - Fix G53 (5 min)

```fish
firebase login --reauth
# Complete browser auth
firebase projects:list
# Verify kjtcom-c78cd appears
```

Test Firebase MCP: "Get 3 documents from locations collection"

---

## STEP 2: Debug Firecrawl MCP - Fix G52 (15 min)

```fish
# Check API key
test -n "$FIRECRAWL_API_KEY"; and echo "SET"; or echo "NOT SET"

# Test npx directly
npx firecrawl-mcp --help

# If package fails, try explicit version
npx firecrawl-mcp@3.11.0 --help

# Check .mcp.json firecrawl entry syntax
cat .mcp.json | python3 -m json.tool

# If still failing, try alternate config format
# Some MCP servers need env vars passed differently
```

If unresolvable, document and move on. Firecrawl is P2.

---

## STEP 3: Dart SDK + Dependency Upgrade (45 min)

```fish
# 3a. Check current versions
dart --version
flutter --version

# 3b. Upgrade Flutter SDK if Dart < 3.9
# CachyOS/Arch:
yay -S flutter-bin
# OR if using flutter-bin from AUR, check latest version first:
yay -Si flutter-bin | grep Version

# 3c. Verify Dart 3.9+
dart --version
# Must show >= 3.9.0

# 3d. Upgrade all dependencies
cd ~/dev/projects/kjtcom/app
flutter pub upgrade --major-versions

# 3e. Check what changed
flutter pub outdated

# 3f. Run analysis
flutter analyze
# Fix any issues introduced by upgrades

# 3g. Run tests
flutter test
# All 15 must pass. If failures, fix before proceeding.

# 3h. Build web
flutter build web
# Must complete without errors

# 3i. Update pubspec.yaml SDK constraint if needed
# Ensure: sdk: '^3.9.0' or whatever the new minimum is
```

**Self-healing:** If a dep upgrade breaks build:
1. Identify breaking dep via `flutter analyze` errors
2. Pin to last working version in pubspec.yaml
3. Re-run `flutter pub get`, `flutter analyze`, `flutter build web`
4. Document the pin and reason in build log

---

## STEP 4: Install Dart MCP Server (15 min)

Requires Dart 3.9+ from Step 3.

```fish
# 4a. Add to Claude Code
claude mcp add --transport stdio dart -- dart mcp-server

# 4b. Add to .mcp.json
# Add this entry:
# "dart": {
#   "command": "dart",
#   "args": ["mcp-server"]
# }

# 4c. Add to .gemini/settings.json
# Same entry as above in mcpServers section

# 4d. Verify
# In Claude Code: "Analyze app/lib/widgets/query_editor.dart for issues"
# Expected: Returns analysis results from Dart analyzer
```

---

## STEP 5: Comprehensive Functionality Review (30 min)

After successful build, verify ALL functionality:

### 5a. Query System
```
| where t_any_cuisines contains "french"
| where t_log_type == "tripledb"
| where t_any_countries != "us"
| where t_any_cities contains-any ["paris", "london", "rome"]
```
- Verify syntax highlighting (red pipes, purple operators, cyan fields, blue values)
- Verify autocomplete (field mode with t_, value mode after operator)
- Verify results render with pagination (20/50/100)
- Verify detail panel opens on row click
- Verify +filter/-exclude buttons work correctly
- Verify clear button resets query and results
- Verify copy JSON copies entity to clipboard

### 5b. All 6 Tabs
| Tab | Test | Pass Criteria |
|-----|------|---------------|
| Results | Execute query, paginate, click row | Results render, detail panel shows |
| Map | View markers, click marker | OSM tiles load, pipeline colors correct |
| Globe | View stats | Continent cards, country grid render |
| IAO | View methodology | Trident, 10 pillars display |
| Gotcha | View registry | 47 patterns show, filter toggle works |
| Schema | Click "+ Add to query" | Query editor updates with field clause |

### 5c. Use Dart MCP
Ask Dart MCP to analyze the app and report any issues the upgrade introduced.

---

## STEP 6: Panther SIEM Scrape (30 min)

### 6a. Kyle launches Chrome with debug port
```fish
google-chrome-stable --remote-debugging-port=9222
# Navigate to tachtech.runpanther.net -> Investigate -> Search
# MFA if cookie session expired
```

### 6b. Verify CDP connection
```fish
curl -s http://localhost:9222/json/list | python3 -c "
import sys, json
for t in json.load(sys.stdin):
    print(f'{t[\"id\"]} | {t.get(\"title\",\"?\")} | {t.get(\"url\",\"?\")}')"
```

### 6c. Run scrape script
```fish
python3 scripts/panther_scrape.py
```

### 6d. Create mapping notes
Create docs/panther-reference/panther-scrape-notes.md comparing Panther UI elements to kjtcom equivalents.

---

## STEP 7: Qwen Middleware Registry (60 min)

### 7a. Create batch processor script

```fish
# scripts/build_registry.py
# Groups docs/archive/ files by iteration
# Extracts 4 files per iteration (design, plan, build, report)
# Concatenates each iteration's files
# Feeds to Qwen3.5-9B via Ollama API with extraction prompt
# Outputs structured JSON per iteration
# Merges into iteration_registry.json
```

### 7b. Create registry extraction prompt

```
/no_think
You are analyzing an IAO iteration. Extract the following from these artifacts:

1. Version, date, phase, focus
2. Agents used (primary executor, consulted LLMs, MCP servers)
3. Outcomes (interventions, gotchas created/resolved, analyze/test results, deploys)
4. Failures and root causes
5. Successes and key achievements
6. Areas for improvement

Output ONLY valid JSON matching the iteration_registry schema.
```

### 7c. Process archive in batches

```fish
# Process iterations in chronological order
# Each batch: 1 iteration (4 files, ~5-15K tokens)
# Qwen processes with /no_think prefix for clean JSON
python3 scripts/build_registry.py
```

### 7d. Integrate gotcha registry

Merge the gotcha_tab.dart patterns into the registry JSON. Cross-reference which iterations created and resolved each gotcha.

### 7e. Validate output

```fish
python3 -c "import json; json.load(open('iteration_registry.json'))"
# Must parse without error
```

---

## STEP 8: Qwen Evaluation + Artifacts (20 min)

### 8a. Run evaluator against v9.37

```fish
python3 scripts/run_evaluator.py --version v9.37 \
  --build-log docs/kjtcom-build-v9.37.md \
  --active-gotchas "G47,G51,G52,G53"
```

### 8b. Produce all artifacts

- [ ] docs/kjtcom-build-v9.37.md
- [ ] docs/kjtcom-report-v9.37.md (with Agent Scorecard, scores folded in)
- [ ] docs/kjtcom-changelog.md (append v9.37)
- [ ] agent_scores.json (append v9.37 scores)
- [ ] iteration_registry.json (new - all iterations)
- [ ] scripts/build_registry.py (new)
- [ ] docs/install.fish (update with Dart MCP + any new deps)
- [ ] .mcp.json (add dart entry)
- [ ] .gemini/settings.json (add dart entry)
- [ ] CLAUDE.md (update read order to v9.37)
- [ ] GEMINI.md (update read order to v9.37)

---

## POST-FLIGHT CHECKLIST

- [ ] Dart SDK >= 3.9
- [ ] All deps upgraded, flutter analyze clean, flutter test 15/15
- [ ] flutter build web succeeds
- [ ] All 6 tabs functional
- [ ] Dart MCP server responds to queries
- [ ] Firebase MCP authenticated and querying (G53 fixed)
- [ ] Firecrawl MCP investigated (G52 fixed or documented)
- [ ] Panther scrape captures saved to docs/panther-reference/
- [ ] iteration_registry.json created with historical data
- [ ] agent_scores.json updated with v9.37
- [ ] install.fish updated
- [ ] All IAO artifacts produced

---

## INTERVENTION POINTS

| # | Trigger | Resolution |
|---|---------|------------|
| 1 | Firebase reauth | Kyle completes browser auth flow |
| 2 | Chrome debug port | Kyle relaunches Chrome with --remote-debugging-port=9222, MFA if needed |
| 3 | Dart SDK < 3.9 after yay update | Kyle runs: sudo pacman -S dart (or installs from flutter.dev) |

Zero-intervention target: 2-3 (auth flows require human).

---

*Plan document generated from claude.ai Opus 4.6 session, April 4, 2026.*
