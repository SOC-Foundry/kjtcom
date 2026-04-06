# kjtcom - Design Document v9.52

**Phase:** 9 - App Optimization
**Iteration:** 52
**Date:** April 5, 2026
**Recommended Agent:** Claude Code
**Focus:** Evaluator Harness Rebuild (400+ lines) + Claw3D Solar System Redesign + Phase 10 Systems Check

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Evaluator harness rebuild (400+ lines) | P1 | Rebuild docs/evaluator-harness.md from scratch as comprehensive operating manual with ADR, failure examples from all iterations, score calibration, evidence standards, complete templates. |
| W2 | Claw3D solar system redesign | P1 | Qwen=sun, agents/MCPs=inner planets, middleware/frontend/backend/pipeline=gas giants with component moons. Iteration toggle with active/inactive color fading. |
| W3 | Phase 10 systems check (all agents, MCPs, LLMs) | P2 | Dry run engaging all 5 MCPs, all 4 local LLMs, Gemini Flash, and Telegram bot. MCP checks in post-flight. |
| W4 | Post-flight + living docs + README cadence | P2 | Post-flight with MCP verification. Changelog append. README v9.52 (next overhaul v9.55). |

---

## W1: Evaluator Harness Rebuild (P1)

The current harness is 84 lines - a set of rules. What Qwen needs is a 400+ line comprehensive operating manual with ADR content, specific examples of every failure pattern from 11 iterations, score calibration, evidence standards, and complete templates.

### Target Structure (docs/evaluator-harness.md, 400+ lines)

```
# Qwen Evaluator Harness
## 1. Identity and Role (who you are, what you do)
## 2. Output Schema (eval_schema.json reference)
## 3. Architecture Decision Record (ADR)
   - ADR-001: IAO Methodology (10 pillars, Trident)
   - ADR-002: Thompson Schema (t_any_* fields)
   - ADR-003: Multi-Agent Orchestration (agent roles, MCP servers)
   - ADR-004: Middleware as Primary IP
   - ADR-005: Schema-Validated Evaluation (this harness)
   - Each ADR includes: context, decision, rationale, consequences
## 4. Scoring Rules (with calibration examples)
   - Score scale: 0-9 on 10-point scale, report as X/10
   - Calibration: what does a 9/10 look like vs 7/10 vs 3/10
   - Real examples from prior iterations
## 5. Failure Pattern Catalog (every bug from v9.41-v9.51)
   - Pattern 1: Hallucinated workstreams (v9.43, v9.46)
   - Pattern 2: All MCPs listed for every workstream (v9.49)
   - Pattern 3: Agent="Qwen" instead of executor (v9.49-v9.50)
   - Pattern 4: "TBD" or "Review..." in Trident (v9.42-v9.44)
   - Pattern 5: Score as X/9 instead of X/10 (v9.50)
   - Pattern 6: Raw JSON in narrative sections (v9.49-v9.50)
   - Pattern 7: Corporate fluff language (v9.42)
   - Pattern 8: Workstream renaming/reordering (v9.43)
   - Pattern 9: Fabricated MCP names (v9.42)
   - Pattern 10: Marking timed-out workstreams as "complete" (v9.41)
   - Pattern 11: Build log not found paradox (v9.46-v9.48)
   - Each pattern includes: what happened, why it was wrong, correct behavior
## 6. Evidence Quality Standards
   - GOOD: "scripts/cleanup_docs.py (36 lines) created, verified via ls -la"
   - BAD: "File exists" (too vague)
   - BAD: "Post-flight PASS confirms" (what specifically passed?)
   - Requirements: file path + line count or size, command + output, test + result count
## 7. MCP Usage Guide
   - Firebase MCP: used when Firestore queries are executed via MCP (NOT when Firebase Admin SDK is used in Python)
   - Context7 MCP: used when API documentation is looked up
   - Firecrawl MCP: used when web pages are scraped
   - Playwright MCP: used when browser automation runs
   - Dart MCP: used when Dart code analysis runs
   - "-": when no MCP server was invoked. Most workstreams use "-".
## 8. Agent Attribution Guide
   - The executor is in the design doc header. You (Qwen) are NEVER the executor.
   - claude-code: when Claude Code runs the iteration
   - gemini-cli: when Gemini CLI runs the iteration
   - LLMs: use exact Ollama names (qwen3.5:9b, not "qwen-max")
## 9. Trident Computation Rules (with example)
   - Cost: count llm_call events. Sum tokens if available. Never "0 tokens" when events exist.
   - Delivery: count complete/total from YOUR scorecard. "4/5 workstreams complete"
   - Performance: state the specific metric from the design doc Trident table. Include the number.
   - EXAMPLE: Cost: "2,400 tokens across 5 LLM calls" | Delivery: "4/5 workstreams complete" | Performance: "Qwen scores X/10, build log rendered as markdown"
## 10. Report Template (complete markdown structure)
   - Summary: 4-6 sentences, plain text, no JSON
   - Workstream Scorecard: exact W# from design doc, Evidence column, X/10 scores
   - Trident: actual values
   - Agent Utilization
   - Event Log Summary
   - Gotchas
   - What Could Be Better: 3+ items
   - Next Iteration Candidates: 3+ items
## 11. Build Log Template (complete markdown structure)
   - Pre-flight checklist
   - Execution log: per-workstream with outcome, evidence, improvements
   - Files changed
   - Test results (inline, not "see output")
   - Gotcha log
   - Event log summary
   - Post-flight verification
## 12. Changelog Template
   - NEW:/UPDATED:/FIXED: prefixes
   - Specific numbers
   - Agents, LLMs, MCPs, interventions
## 13. Banned Phrases (comprehensive list with replacements)
## 14. What Could Be Better (mandate)
   - Required even when all workstreams score 8+
   - Must be concrete, actionable, specific
   - Feeds into next iteration planning
## 15. Workstream Fidelity (absolute rule, with examples)
## 16. Living Document Notice
   - This harness grows every iteration
   - Each iteration adds to the ADR and failure catalog
   - Never remove content, only add
```

### ADR Content (embedded in harness)

The ADR section makes the harness self-documenting. Qwen reads the architectural decisions and can evaluate whether the iteration's work aligns with them. Each ADR follows:

```
### ADR-001: IAO Methodology
**Context:** kjtcom is built using Iterative Agentic Orchestration, a plan-report loop methodology distilled from 48+ TripleDB iterations.
**Decision:** Every iteration produces 4 artifacts (design, plan, build, report) + updated harness files + changelog entry.
**Pillars:** P1-Trident (Cost/Delivery/Performance), P2-Artifact Loop, P3-Diligence (event logging), P4-Pre-Flight, P5-Agentic Harness, P6-Zero-Intervention, P7-Self-Healing, P8-Phase Graduation, P9-Post-Flight Testing, P10-Continuous Improvement.
**Consequences:** Artifact discipline is non-negotiable. Skipping artifacts is a failure.
```

Each iteration adds new ADR entries as architectural decisions are made. This builds institutional memory directly into the evaluator's context.

---

## W2: Claw3D Solar System Redesign (P1)

### Design: Solar System Model

**Qwen (Sun):** Central glowing sphere. All objects orbit around evaluation.

**Inner Ring (Agents/LLMs/MCPs) - Rocky Planets:**
| Planet | Object | Color | Size |
|--------|--------|-------|------|
| Mercury | Nemotron Mini 4B | orange | small |
| Venus | GLM-4.6V-Flash | amber | small |
| Earth | Claude Code | green | medium |
| Mars | Gemini CLI | blue | medium |
| (Asteroid Belt) | 5 MCP Servers | pink cubes | tiny |
| (Asteroid Belt) | nomic-embed-text | teal cube | tiny |

**Outer Ring (System Components) - Gas Giants:**
| Planet | System | Color | Moons (components) |
|--------|--------|-------|-------------------|
| Jupiter | Middleware | cyan | intent_router, firestore_query, artifact_generator, evaluator_harness, gotcha_archive, middleware_registry, event_logging, post_flight, cleanup_docs, ollama_config |
| Saturn | Frontend | green (rings) | Results tab, Map tab, Globe tab, IAO tab, MW tab, Schema tab, query_editor, detail_panel |
| Uranus | Pipeline | orange | yt-dlp (input), faster-whisper, Gemini Extract, normalize, geocode, enrich, load |
| Neptune | Backend/Data | yellow | Firestore, Cloud Functions, Firebase Hosting, ChromaDB, schema_reference, eval_schema |

**Iteration Toggle:**
- Dropdown or slider at top: select iteration (v9.41 through v9.52)
- When iteration selected:
  - Nodes that were ACTIVE in that iteration glow with full color + opacity 1.0
  - Nodes that were INACTIVE (not yet built or not used) show as outline/wireframe + opacity 0.3
  - Data source: a JSON array mapping iteration -> active node IDs
  - New file: data/claw3d_iterations.json

```json
{
  "v9.41": ["claude_code", "gemini_flash", "qwen", "firestore", "chromadb", "intent_router", "firestore_query", "telegram_bot"],
  "v9.42": ["claude_code", "gemini_flash", "qwen", "firestore", "chromadb", "intent_router", "firestore_query", "telegram_bot", "brave_search", "gotcha_archive", "middleware_registry", "systemd_bot", "county_enrichment"],
  ...
  "v9.52": ["ALL"]
}
```

### Implementation

- Rebuild app/web/claw3d.html from scratch (current version is v9.38 prototype)
- Use Three.js OrbitControls for navigation (drag to orbit, scroll to zoom)
- Sun: SphereGeometry with emissive material (Qwen purple/magenta)
- Planets: SphereGeometry with orbit rings (TorusGeometry)
- Moons: smaller spheres orbiting their parent planet
- Asteroid belt: BufferGeometry with random positions for MCPs
- Animated: planets orbit sun, moons orbit planets (at different speeds)
- Legend: updated with solar system metaphor
- Header: "Claw3D - IAO Solar System | kjtcom v9.52 | Iteration: [dropdown]"
- Data flow lines: connect sun to planets, planets to moons (subtle, animated)

### Iteration Data File

Create data/claw3d_iterations.json with active node lists for v9.41 through v9.52. The claw3d.html loads this file and uses it to toggle opacity/glow per node.

---

## W3: Phase 10 Systems Check (P2)

Dry run all systems to verify Phase 10 readiness.

### MCP Checks (add to post_flight.py)

```python
def verify_mcps():
    """Check all 5 MCP servers are accessible."""
    checks = {}
    # Firebase MCP
    checks["firebase_mcp"] = test_firebase_mcp()
    # Context7 MCP
    checks["context7_mcp"] = test_context7_mcp()
    # Firecrawl MCP
    checks["firecrawl_mcp"] = test_firecrawl_mcp()
    # Playwright MCP
    checks["playwright_mcp"] = test_playwright_mcp()
    # Dart MCP
    checks["dart_mcp"] = test_dart_mcp()
    return checks
```

### LLM Checks

```fish
# Test all 4 Ollama models respond
for model in qwen3.5:9b nemotron-mini:4b haervwe/GLM-4.6V-Flash-9B nomic-embed-text
    echo "Testing $model..."
    ollama run $model "respond with 'OK'" --format json 2>/dev/null | head -1
end

# Test Gemini Flash via litellm
python3 -c "
from scripts.utils.ollama_config import GEMINI_MODEL
import litellm
r = litellm.completion(model=GEMINI_MODEL, messages=[{'role':'user','content':'respond OK'}], thinking={'type':'disabled'})
print(f'Gemini Flash: {r.choices[0].message.content}')
"
```

### Bot Check

```fish
# Verify systemd bot is running
sudo systemctl status kjtcom-telegram-bot --no-pager
# Send test queries
python3 -c "
from scripts.intent_router import route_question
import json
tests = [
    'how many entities',
    'what caused the G45 cursor bug',
    'does anthropic have a free tier'
]
for t in tests:
    r = route_question(t)
    print(f'{t[:30]}... -> {r.get(\"route\", \"unknown\")}')
"
```

### Pipeline Script Check

```fish
# Verify all 7 pipeline scripts exist and are syntactically valid
for phase in 1 2 3 4 5 6 7
    set script "scripts/phase${phase}_*.py"
    if test -f $script
        python3 -c "import py_compile; py_compile.compile('$script')" 2>/dev/null
        and echo "PASS: Phase $phase"
        or echo "FAIL: Phase $phase (syntax error)"
    else
        echo "MISSING: Phase $phase script"
    end
end
```

---

## W4: Post-Flight + Living Docs + README (P2)

1. Enhanced post_flight.py with MCP verification
2. Changelog append (single file)
3. README version v9.52
4. Middleware registry update (harness rebuild, claw3d redesign)
5. Architecture.mmd update if needed
6. Re-embed archive (new harness will be the largest doc)
7. Deploy + verify

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K tokens. |
| Delivery | 4 workstreams. Harness 400+ lines. Claw3D solar system. All systems verified. |
| Performance | Evaluator harness passes wc -l >= 400. Claw3D renders solar system with iteration toggle. All 5 MCPs, 4 LLMs, and bot respond in systems check. |

---

*Design document v9.52, April 5, 2026.*
