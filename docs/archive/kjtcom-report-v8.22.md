# kjtcom - Report v8.22 (Phase 8 - Enrichment Hardening + Query Assessment)

**Pipeline:** kjtcom
**Phase:** 8 (Enrichment Hardening)
**Iteration:** 22 (global counter)
**Date:** 2026-04-03

---

## Success Criteria Matrix

| Criteria | Target | Actual | Status |
|----------|--------|--------|--------|
| Schema v3 rate | 100% (all 6,181) | 100% (6,181/6,181) | PASS |
| TripleDB enrichment rate | >85% (up from 63%) | 98% (1,086/1,100) | PASS |
| TripleDB coordinate rate | >95% (up from 91%) | 99% (1,092/1,100) | PASS |
| TripleDB city rate | >95% (up from 88%) | 93% (1,027/1,100) | NEAR MISS |
| Query defect inventory | Complete (all 6 categories) | 12 defects across 6 categories | PASS |
| Composite index gaps | Identified and documented | No gaps found | PASS |
| v8.23 remediation spec | In report | See Section 3 below | PASS |
| Interventions | 0 | 0 | PASS |
| Artifacts | 4 mandatory | 4 produced | PASS |

**TripleDB city rate (93%):** 73 entities still missing `t_any_cities`. These are entities where neither the existing data nor Nominatim reverse geocoding could resolve a city name. Most are in rural/unincorporated areas. Further improvement would require manual review or alternative geocoding providers.

---

## Section 1: Complete Query Defect Table

| # | Category | Defect | Severity | Root Cause | Flutter File | Firestore Behavior | v8.23 Fix |
|---|----------|--------|----------|------------|-------------|-------------------|-----------|
| D1 | Cat 1 | Case-sensitive array-contains: "French" returns 0, "french" returns 80 | P0 - Critical | Firestore `arrayContains` is case-sensitive. All `t_any_*` data is lowercased, but query input is passed raw. | `firestore_provider.dart:25` | By design | Lowercase all query values before sending to Firestore |
| D2 | Cat 1 | CalGold `t_any_shows` stored in title case ("California's Gold") while other pipelines use lowercase | P1 - High | v5.14 CalGold backfill used title case for `t_any_shows`. RickSteves uses lowercase. | N/A (data issue) | Inconsistent data | One-time data fix: lowercase all `t_any_shows` values in CalGold entities |
| D3 | Cat 1 | Example query "French" cuisine returns 0 results | P0 - Critical | Consequence of D1. First example query the user sees produces empty results. | `query_editor.dart:9` | N/A | Fix D1 (lowercase input) AND update example queries to use lowercase values |
| D4 | Cat 1 | Example query "Huell Howser" actors returns 0 results | P0 - Critical | Consequence of D1. Second example query produces empty results. | `query_editor.dart:10` | N/A | Fix D1 AND update example queries |
| D5 | Cat 3 | Two array-contains clauses fail server-side | P2 - Medium | Firestore limit: max 1 `array-contains` per query. App pushes second to client-side, but this is correct behavior. | `firestore_provider.dart:24-33` | By design | Document in UI that multi-array queries are filtered client-side from a 200-result window |
| D6 | Cat 3 | 200-result limit silently truncates compound queries | P1 - High | `query.limit(200)` at `firestore_provider.dart:37` caps results before client-side filtering. "medieval" query has 653 matches but only 200 fetched, then filtered to 11. | `firestore_provider.dart:37` | N/A | Increase limit for compound queries or remove limit and paginate |
| D7 | Cat 4 | `contains-any` operator not supported in parser | P1 - High | `query_clause.dart:27` regex only matches `contains`, `==`, `!=`. Firestore natively supports `array-contains-any` (up to 30 values). | `query_clause.dart:27` | Firestore supports it | Add `contains-any` to parser regex, implement in `firestore_provider.dart` |
| D8 | Cat 5 | No result count displayed in UI | P1 - High | No count widget exists. `resultsProvider` returns a list but count is never rendered. | No file (missing widget) | N/A | Add result count badge showing "N results" (or "200+ results" when limit hit) |
| D9 | Cat 5 | No indication when 200-result limit is reached | P1 - High | User cannot tell if they are seeing all results or a truncated subset. | `firestore_provider.dart:37` | N/A | Show "showing 200 of 650+" indicator when limit is hit |
| D10 | Cat 6 | Invalid field name silently returns empty results | P2 - Medium | Firestore returns empty for non-existent fields. No field name validation in parser. | `query_clause.dart` | By design | Add field name validation against known `t_any_*` fields, show error for invalid fields |
| D11 | Cat 6 | No error feedback for malformed queries | P2 - Medium | Parser returns empty clause list for unparseable input. No user-visible error. | `query_clause.dart:30` | N/A | Show parse error message when query text doesn't match expected syntax |
| D12 | Cat 6 | `==` operator on `t_any_*` fields uses client-side comparison | P3 - Low | `firestore_provider.dart:28` only sends `==` server-side for non-`t_any_` fields. For arrays, `==` means "array equals exactly" in Firestore, but the app treats it as "array contains" client-side. Semantically confusing but functionally correct. | `firestore_provider.dart:28` | By design | Document `==` behavior or replace with `contains` in example queries for `t_any_*` fields |

### Defect Severity Summary

| Severity | Count | Impact |
|----------|-------|--------|
| P0 - Critical | 3 (D1, D3, D4) | Example queries broken on load - first impression is a non-functional app |
| P1 - High | 4 (D2, D6, D7, D8, D9) | Missing features and data truncation that mislead users |
| P2 - Medium | 3 (D5, D10, D11) | Missing validation and documentation |
| P3 - Low | 1 (D12) | Semantic confusion, functionally correct |

---

## Section 2: v8.23 Remediation Spec

### Scope

v8.23 implements all P0 and P1 fixes from the defect table. P2 fixes are included if time permits. P3 is deferred.

### Work Items

| # | Work Item | Files | Complexity | Priority |
|---|-----------|-------|-----------|----------|
| W1 | Lowercase all query values before Firestore dispatch | `firestore_provider.dart` | Low | P0 |
| W2 | Update example queries to use lowercase values | `query_editor.dart` | Low | P0 |
| W3 | Data fix: lowercase all CalGold `t_any_shows` values | Python script (one-time) | Low | P1 |
| W4 | Add `contains-any` operator to parser and provider | `query_clause.dart`, `firestore_provider.dart` | Medium | P1 |
| W5 | Add result count badge to UI | New widget or existing results panel | Medium | P1 |
| W6 | Add "200+ results" truncation indicator | `firestore_provider.dart`, results panel | Medium | P1 |
| W7 | Increase or remove 200-result limit with pagination | `firestore_provider.dart` | High | P1 |
| W8 | Add field name validation to parser | `query_clause.dart` | Low | P2 |
| W9 | Add parse error feedback to UI | `query_editor.dart` | Medium | P2 |
| W10 | Document `==` vs `contains` semantics for array fields | `query_editor.dart` (help text) | Low | P3 |

### Implementation Order

1. **W1 + W2** (P0, ~15 min): Immediate case sensitivity fix. Changes 2 files, fixes D1/D3/D4 simultaneously. Deploy immediately.
2. **W3** (P1, ~10 min): Data fix script. Similar to `backfill_schema_v3.py` pattern. Fixes D2.
3. **W5 + W6** (P1, ~30 min): Result count and truncation indicator. Improves user understanding.
4. **W4** (P1, ~45 min): `contains-any` parser + provider implementation. New Firestore operator support.
5. **W7** (P1, ~60 min): Pagination. Most complex change - requires cursor-based Firestore pagination and UI scroll handling.
6. **W8 + W9** (P2, ~30 min): Validation and error feedback. Polish items.

### Composite Index Requirements

No new composite indexes needed. All tested compound queries (array-contains + equality on `t_log_type`) executed successfully with auto-created indexes. If `contains-any` + equality compounds are added in W4, monitor for index creation errors at deploy time.

---

## Section 3: MCP Server and Tool Recommendations for v8.23

### Firebase MCP Servers

| Server | Source | Transport | Key Features | Recommendation |
|--------|--------|-----------|-------------|----------------|
| [firebase-mcp](https://github.com/gannonh/firebase-mcp) (gannonh) | Community | stdio | Firestore CRUD, Auth, Storage. 3.4k+ stars. | **Recommended for v8.23.** Direct Firestore reads during development without throwaway Python scripts. |
| [Official Firebase MCP](https://firebase.google.com/docs/ai-assistance/mcp-server) | Google | stdio/HTTP | Natural language Firestore exploration, IAM-based auth, pre-built prompts. | **Evaluate.** Official server from Firebase team. Uses CLI credentials. May be overkill for query testing but valuable for ongoing development. |
| [Google Cloud Firestore Remote MCP](https://docs.cloud.google.com/firestore/native/docs/use-firestore-mcp) | Google Cloud | Remote (SSE) | Remote MCP endpoint, OAuth 2.0 auth, all GCP identities supported. | **Defer.** Remote MCP adds network dependency. Local stdio servers are faster for dev workflows. |
| [mcp-firebase-server](https://github.com/davo20019/mcp-firebase-server) (davo20019) | Community | stdio | Python-based, Firebase Admin SDK, Firestore + Auth operations. | **Alternative.** Python-native, easier to extend. Consider if gannonh/firebase-mcp doesn't fit. |

### Recommended v8.23 MCP Configuration

```json
{
  "mcpServers": {
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-mcp"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "~/.config/gcloud/kjtcom-sa.json"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-playwright"]
    }
  }
}
```

### Playwright MCP (already available)

Continue using for v8.23 regression testing. The query defect table from this iteration produces structured test cases:
- 5 example queries with expected result counts
- 6 edge case scenarios
- Case sensitivity assertions

These can be automated as Playwright test scripts that run against the deployed app after each v8.23 change.

---

## Section 4: HyperAgents and External Search Assessment

### HyperAgents (Meta FAIR)

**What it is:** HyperAgents are self-referential AI systems that can analyze and modify their own source code, creating iterative self-improvement loops. They use fitness signals to evolve code toward measurable goals.

**Applicability to kjtcom query system:** The v8.22 defect table provides natural fitness signals:
- Input query -> expected result count -> actual result count
- Parser coverage: % of valid syntax patterns recognized
- Case sensitivity: % of queries returning correct results regardless of input case

**Assessment: Premature for v8.23.**
- The defect inventory contains 10 well-scoped fixes with clear implementations. A human (or standard Claude Code) can implement all of them in a single iteration.
- HyperAgents shine when the optimization surface is large, ambiguous, or continuously evolving. The kjtcom query system has ~4 source files totaling ~500 lines. The problem space is fully mapped.
- HyperAgents would be more valuable post-v9 (App Optimization) when optimizing extraction prompts, schema mappings, or multi-LLM pipeline stages - domains where the fitness landscape is high-dimensional and iterative improvement is ongoing.

**Recommendation:** Defer HyperAgents to Phase 10 (Retrospective) for evaluation against extraction prompt optimization. Not needed for v8.23 query fixes.

### External Search (Algolia / Typesense)

**The core question:** Are Firestore's native query limitations a fundamental blocker for the kjtcom search experience?

**Analysis of current limitations:**

| Limitation | Impact on kjtcom | Workaround Available? |
|-----------|-----------------|----------------------|
| No full-text search | Cannot search across all `t_any_*` fields simultaneously | `t_any_keywords` array covers tokenized terms |
| Max 1 `array-contains` per query | Compound array queries require client-side filtering | Client-side filter from 200-result window (lossy) |
| No fuzzy/typo-tolerant search | "barb" doesn't match "barbecue" | None within Firestore |
| No relevance ranking | Results ordered by document ID, not relevance | None within Firestore |
| Case-sensitive matching | Fixed by lowercasing input (W1) | Yes - W1 resolves this |

**Assessment:**

The v8.23 fixes (W1-W9) resolve all P0 and P1 issues using Firestore-native capabilities. After v8.23:
- Single-field array queries: fully functional
- Compound queries: functional with improved pagination (W7)
- `contains-any`: functional (W4)
- Result counts: visible (W5, W6)

**Remaining gaps that only external search solves:**
1. **Fuzzy/typo-tolerant search** - users must type exact terms
2. **Cross-field search** - cannot search "french restaurant in paris" as a single query
3. **Relevance ranking** - no way to order results by match quality

**Recommendation: Defer external search evaluation to Phase 9 (App Optimization).**

Rationale:
- v8.23 fixes make the existing query system functional and honest (shows counts, doesn't silently truncate)
- kjtcom has 6,181 entities - well within Firestore's capabilities for structured queries
- Algolia adds $0-29/month cost and a sync pipeline (Cloud Functions trigger on document write)
- Typesense requires self-hosting infrastructure
- The cost/complexity tradeoff is not justified until Phase 9 evaluates actual user search patterns

If Phase 9 user testing reveals that fuzzy search or cross-field queries are needed, the recommended path is:
1. **Algolia Firebase Extension** (managed, lowest setup cost, pay-per-operation)
2. Not Typesense (self-hosting adds ops burden for a single-developer project)

---

## Enrichment Metrics Summary

### Before v8.22

| Metric | CalGold | RickSteves | TripleDB | Total |
|--------|---------|-----------|----------|-------|
| Entities | 899 | 4,182 | 1,100 | 6,181 |
| Schema v3 | 778 (87%) | 3,980 (95%) | 1,100 (100%) | 5,858 (95%) |
| Enrichment | 100% | 100% | 63% | - |
| Coordinates | 100% | 100% | 91% | - |
| Cities | 100% | 100% | 89% | - |

### After v8.22

| Metric | CalGold | RickSteves | TripleDB | Total |
|--------|---------|-----------|----------|-------|
| Entities | 899 | 4,182 | 1,100 | 6,181 |
| Schema v3 | 899 (100%) | 4,182 (100%) | 1,100 (100%) | 6,181 (100%) |
| Enrichment | 100% | 100% | 98% | - |
| Coordinates | 100% | 100% | 99% | - |
| Cities | 100% | 100% | 93% | - |

### Enrichment Improvement

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Schema v3 rate | 95% | **100%** | +5% |
| TripleDB enrichment | 63% | **98%** | +35% |
| TripleDB coordinates | 91% | **99%** | +8% |
| TripleDB cities | 89% | **93%** | +4% |

---

## Gotcha Registry Updates

| ID | Gotcha | Status |
|----|--------|--------|
| G34 | Firestore single array-contains limit | CONFIRMED - tested in Cat 3. Client-side fallback works but is limited by 200-result cap. |
| G35 | Production write safety (dry-run first) | CONFIRMED - both scripts ran dry-run before full execution. Zero data corruption. |
| G36 (NEW) | Case-sensitive arrayContains | All `t_any_*` data MUST be lowercased. All query input MUST be lowercased before dispatch. Mixed-case data from earlier phases causes silent query failures. |
| G37 (NEW) | t_any_shows inconsistent casing | CalGold entities have title case "California's Gold" from v5.14 backfill. Must lowercase in v8.23 data fix. |

---

## Recommendation

**Proceed to v8.23** with the remediation spec from Section 2. Priority order: W1+W2 (P0 case fix), W3 (data fix), W5+W6 (counts), W4 (contains-any), W7 (pagination). Deploy after W1+W2 for immediate user-facing improvement.
