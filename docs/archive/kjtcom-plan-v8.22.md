# kjtcom - Plan v8.22 (Phase 8 - Enrichment Hardening + Query Assessment)

**Pipeline:** kjtcom (cross-pipeline location intelligence platform)
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 22 (global counter)
**Executor:** Claude Code (enrichment scripts + Flutter assessment)
**Machine:** NZXTcos (primary) or tsP3-cos
**Date:** April 2026

---

## Section A: Pre-Flight (Human)

### IAO Pillar Pre-Flight Checklist

Before launching Claude Code, verify each pillar's prerequisites are satisfied:

| # | Pillar | Verification | Command/Check |
|---|--------|-------------|---------------|
| P1 | Trident | No paid APIs required for this iteration | Confirm: Google Places free tier, no Gemini calls needed |
| P2 | Artifact Loop | Previous iteration archived | `ls docs/archive/kjtcom-*v7.21*` -> 2 files (build + report) |
| P2 | Artifact Loop | Current design + plan in docs/ | `ls docs/kjtcom-{design,plan}-v8.22.md` -> 2 files |
| P3 | Diligence | Design doc reviewed by human | Kyle has read and approved design-v8.22.md |
| P4 | Pre-Flight | Git clean | `git status` -> clean working tree |
| P4 | Pre-Flight | CLAUDE.md updated | `head -5 CLAUDE.md` -> references v8.22 |
| P4 | Pre-Flight | SA credentials accessible | `test -f "$GOOGLE_APPLICATION_CREDENTIALS" && echo SET` |
| P5 | Harness | Agent instructions current | CLAUDE.md points to v8.22 design + plan |
| P6 | Zero-Intervention | All decision points pre-answered | No TBD or PLACEHOLDER in design doc |
| P7 | Self-Healing | Checkpoint mechanism available | Python scripts use batch writes with dry-run |
| P8 | Graduation | Phase 8 builds on Phase 7 data | `python3 -c "..." # verify 6,181 production entities` |
| P9 | Post-Flight | Success criteria defined | Design doc Section: Success Criteria |
| P10 | Improvement | Gotcha registry current | G34, G35 added for this iteration |

### A1: Archive v7.21 Docs

```fish
cd ~/dev/projects/kjtcom
mv docs/kjtcom-design-v7.21.md docs/archive/
mv docs/kjtcom-plan-v7.21.md docs/archive/
```

### A2: Stage v8.22 Docs

```fish
# Copy design + plan from Downloads (or wherever you saved them)
cp ~/Downloads/kjtcom-design-v8.22.md docs/
cp ~/Downloads/kjtcom-plan-v8.22.md docs/
```

### A3: Update CLAUDE.md

Replace CLAUDE.md contents with the v8.22 version (Section C of this document).

### A4: Verify Production State

```fish
python3 -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd')

calgold = ricksteves = tripledb = 0
v1 = v2 = v3 = 0
no_enrichment = 0
no_coords = 0

for doc in db.collection('locations').stream():
    d = doc.to_dict()
    lt = d.get('t_log_type', '')
    sv = d.get('t_schema_version', 0)
    if lt == 'calgold': calgold += 1
    elif lt == 'ricksteves': ricksteves += 1
    elif lt == 'tripledb': tripledb += 1
    if sv == 1: v1 += 1
    elif sv == 2: v2 += 1
    elif sv == 3: v3 += 1
    if not d.get('t_enrichment', {}).get('google_places'):
        if lt == 'tripledb': no_enrichment += 1
    if not d.get('t_any_coordinates'):
        if lt == 'tripledb': no_coords += 1

total = calgold + ricksteves + tripledb
print(f'=== PRODUCTION STATE (pre-v8.22) ===')
print(f'CalGold: {calgold}')
print(f'RickSteves: {ricksteves}')
print(f'TripleDB: {tripledb}')
print(f'Total: {total}')
print(f'Schema v1: {v1}, v2: {v2}, v3: {v3}')
print(f'Non-v3: {v1+v2} (target for backfill)')
print(f'TripleDB no enrichment: {no_enrichment}')
print(f'TripleDB no coords: {no_coords}')
"
```

Expected output: 6,181 total, ~323 non-v3, ~405 TripleDB without enrichment, ~96 TripleDB without coords.

### A5: Verify Flutter App State

```fish
# Visit kylejeromethompson.com in browser
# Test these queries manually and record results:
# 1. Type "t_any_keywords contains barbecue" -> does it return results?
# 2. Type "t_log_type == tripledb" -> does it return results?
# 3. Click a rotating example query -> does it populate results?
# 4. Are result counts displayed anywhere?
# Record observations for Claude Code to validate programmatically.
```

### A6: Check MCP Server Availability

```fish
# In Claude Code, after launch, check available MCP servers:
# Playwright MCP should be available from Phase 6
# Check if Firebase MCP exists in the registry
```

---

## Section B: Claude Code Execution

**Launch:** `claude --dangerously-skip-permissions`
**First message:** See Section D (Launch Prompt).

### Step 1: Read Design Doc

Read `docs/kjtcom-design-v8.22.md` for the complete specification.

### Step 2: Workstream A - Schema v3 Backfill Script

Create `pipeline/scripts/backfill_schema_v3.py`:

The script must:
1. Read all entities from production where t_schema_version < 3
2. Apply backfill rules per t_log_type (CalGold, RickSteves) from design doc Section A1
3. Write updated entities back to production using batch writes (500 per batch)
4. Flags: --dry-run (print first 5 without writing), --limit N

### Step 3: Dry Run Schema v3 Backfill

```fish
python3 -u pipeline/scripts/backfill_schema_v3.py --dry-run --limit 5
```

Review output. Verify t_any_actors, t_any_shows, t_any_continents are populated correctly per pipeline.

### Step 4: Full Schema v3 Backfill

```fish
python3 -u pipeline/scripts/backfill_schema_v3.py
```

Expected: 323 entities updated to schema v3. All 6,181 entities now at v3.

### Step 5: Workstream A - TripleDB Enrichment Backfill Script

Create `pipeline/scripts/backfill_tripledb_enrichment.py`:

The script must:
1. Read TripleDB entities from production where t_enrichment.google_places is null/empty
2. For each entity: Google Places text search (name + city + state)
3. Write enrichment data to t_enrichment.google_places
4. Simultaneously backfill t_any_coordinates and t_any_cities where missing
5. Compute t_any_geohashes for newly-coordinated entities
6. Flags: --dry-run, --limit N
7. Rate limit: 1 request per second (Google Places free tier)

### Step 6: Dry Run TripleDB Enrichment

```fish
python3 -u pipeline/scripts/backfill_tripledb_enrichment.py --dry-run --limit 5
```

### Step 7: Full TripleDB Enrichment Backfill

```fish
python3 -u pipeline/scripts/backfill_tripledb_enrichment.py
```

Expected: ~405 entities enriched. Enrichment rate rises from 63% to 85%+. Coordinate rate rises from 91% to 95%+.

### Step 8: Post-Enrichment Verification

```fish
python3 -u -c "
from google.cloud import firestore
import os
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gcloud/kjtcom-sa.json'))
db = firestore.Client(project='kjtcom-c78cd')

total = v3 = 0
tripledb_total = tripledb_enriched = tripledb_coords = tripledb_cities = 0

for doc in db.collection('locations').stream():
    d = doc.to_dict()
    total += 1
    if d.get('t_schema_version') == 3: v3 += 1
    if d.get('t_log_type') == 'tripledb':
        tripledb_total += 1
        if d.get('t_enrichment', {}).get('google_places'): tripledb_enriched += 1
        if d.get('t_any_coordinates'): tripledb_coords += 1
        if d.get('t_any_cities'): tripledb_cities += 1

print(f'=== POST-ENRICHMENT VERIFICATION ===')
print(f'Total: {total}')
print(f'Schema v3: {v3}/{total} ({v3*100//total}%) - target: 100%')
print(f'TripleDB enriched: {tripledb_enriched}/{tripledb_total} ({tripledb_enriched*100//tripledb_total}%) - target: >85%')
print(f'TripleDB coords: {tripledb_coords}/{tripledb_total} ({tripledb_coords*100//tripledb_total}%) - target: >95%')
print(f'TripleDB cities: {tripledb_cities}/{tripledb_total} ({tripledb_cities*100//tripledb_total}%) - target: >95%')
"
```

### Step 9: Workstream B - NoSQL Query Assessment

Using Playwright MCP (if available) or manual Python Firestore queries, test every query category from the design doc Section B2:

**Test methodology:**
1. For each query pattern, execute against production Firestore directly via Python
2. Record: query string, expected behavior, actual result count, pass/fail
3. Then test the same query through the Flutter app's query editor (via Playwright or documented manual steps)
4. Record: does the UI parse it correctly? Does it send the right Firestore query? Does it display results? Does it show a count?

**Produce a structured defect table:**

| # | Category | Query | Firestore Direct | Flutter App | Severity | Root Cause | v8.23 Fix |
|---|----------|-------|-------------------|-------------|----------|------------|-----------|

### Step 10: Assess Composite Index Gaps

Run each compound query pattern from the design doc. If Firestore returns "requires an index" errors, record the missing index and the link Firestore provides.

### Step 11: MCP Server Registry Check

Search the MCP registry for Firebase/Firestore-related servers that could aid v8.23 development. Document findings in report.

### Step 12: Security Scan + Artifacts

```
CHECKLIST:
[ ] Security: grep -rnI "AIzaSy" . -> only expected references
[ ] Schema v3: 100% (6,181/6,181)
[ ] TripleDB enrichment: >85%
[ ] TripleDB coordinates: >95%
[ ] Query defect inventory: complete
[ ] v8.23 remediation spec: in report
```

Produce all 4 mandatory artifacts:

1. **docs/kjtcom-build-v8.22.md** - Script details, enrichment metrics, query test results
2. **docs/kjtcom-report-v8.22.md** - Success criteria matrix, query defect table, v8.23 remediation spec, MCP server recommendations
3. **docs/kjtcom-changelog.md** - Append v8.22 at top
4. **README.md** - Phase 8 status updated, entity counts refreshed if changed

Do NOT git commit or push.

---

## Section C: CLAUDE.md for v8.22

```markdown
# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v8.22.md (enrichment spec + query assessment methodology)
2. docs/kjtcom-plan-v8.22.md (execute Section B)

## Context

Phase 8 Enrichment Hardening. Two workstreams:
1. Backfill 323 non-v3 entities to schema v3 + enrich 405 under-enriched TripleDB entities
2. Comprehensive assessment of Flutter app NoSQL query functionality - document defects for v8.23

kjtcom project ID: kjtcom-c78cd
SA credentials: $GOOGLE_APPLICATION_CREDENTIALS
Production database: (default)
Production collection: locations
Total entities: 6,181 (899 CalGold + 4,182 RickSteves + 1,100 TripleDB)

## Shell - MANDATORY

- All commands in fish shell
- Use python3 -u for unbuffered stdout
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion
- NEVER print SA credentials or API keys
- Print only SET/NOT SET for key checks

## Enrichment Script Requirements

- backfill_schema_v3.py: --dry-run, --limit flags. Batch writes (500 per batch).
- backfill_tripledb_enrichment.py: --dry-run, --limit flags. Google Places + Nominatim. Rate limit 1 req/sec.
- All production writes use dry-run first (G35)

## Query Assessment Requirements

- Test all 6 query categories from design doc against production Firestore
- Test same queries through Flutter app UI (Playwright MCP or documented manual)
- Produce structured defect table with severity, root cause, and v8.23 fix recommendation
- Check MCP registry for Firebase-related servers
- Assess composite index gaps

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v8.22.md
2. docs/kjtcom-report-v8.22.md (MUST include query defect table + v8.23 remediation spec)
3. docs/kjtcom-changelog.md (append v8.22)
4. README.md (Phase 8 status, updated enrichment rates)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

---

## Section D: Launch Prompt

```
Read CLAUDE.md, then read the full design doc at docs/kjtcom-design-v8.22.md and the plan at docs/kjtcom-plan-v8.22.md.

Execute Section B in order:
1. Create and run the schema v3 backfill script (dry-run first, then full run)
2. Create and run the TripleDB enrichment backfill script (dry-run first, then full run)
3. Verify post-enrichment production state
4. Perform the comprehensive NoSQL query assessment (all 6 categories from the design doc)
5. Check MCP registry for Firebase-related servers
6. Produce all 4 mandatory artifacts, with the report containing:
   - Complete query defect table
   - v8.23 remediation spec with scoped work items
   - MCP server and tool recommendations for v8.23
   - Assessment of whether HyperAgents or external search (Algolia/Typesense) should be evaluated
```

---

## Timing Estimate

| Step | Est. Duration |
|------|---------------|
| Section A (pre-flight, human) | ~15 min |
| Steps 1-4 (schema v3 backfill) | ~15 min |
| Steps 5-7 (TripleDB enrichment) | ~30-45 min (rate limited) |
| Step 8 (verification) | ~5 min |
| Steps 9-11 (query assessment) | ~30-45 min |
| Step 12 (security + artifacts) | ~15 min |
| **Total** | **~2-2.5 hours** |

---

## After v8.22

1. Commit: `git add . && git commit -m "KT 8.22 Phase 8 enrichment hardening + query assessment" && git push`
2. Review the query defect table in the report
3. Draft v8.23 design + plan based on the remediation spec
4. v8.23 scope: implement all query fixes, add result counts, provision composite indexes, deploy updated Flutter app
5. After v8.23: all queries operational, result counts displayed, production-ready search experience
