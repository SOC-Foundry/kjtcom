# kjtcom - Design Document v9.49

**Phase:** 9 - App Optimization
**Iteration:** 49
**Date:** April 5, 2026
**Recommended Agent:** Claude Code (but artifacts are agent-agnostic - Gemini can execute from GEMINI.md)
**Focus:** Qwen Harness Architectural Overhaul + Middleware Tab + Execution Order Fix

---

## RESEARCH CONTEXT

The Typia/AutoBe presentation at Qwen Meetup Korea (2025) demonstrated that Qwen3.5's structured output success rate went from 6.75% to 99.8% - not through better prompts, but through a deterministic harness: type schemas that constrain outputs, validators that verify results, and structured feedback that tells the LLM exactly what was wrong so it can self-correct.

Our current Qwen harness is mostly prompt-based: "don't hallucinate workstreams," "don't use banned phrases," "require evidence." The results show this approach produces ~60% compliance. The fix is architectural: strict JSON schema -> programmatic validation -> specific error feedback -> retry with corrections.

This iteration implements that pattern.

---

## AMENDMENTS (all prior amendments remain in effect)

### Agent-Agnostic Artifacts - NEW (v9.49+)

Design docs, plans, and harness files must work for EITHER Claude Code or Gemini CLI. The design doc specifies a "Recommended Agent" but both CLAUDE.md and GEMINI.md contain sufficient context for either to execute. The launch prompt is always "Read [CLAUDE/GEMINI].md and execute."

### Execution Order Fix - NEW (v9.49+)

The evaluator (run_evaluator.py) has been trying to read the build log for the CURRENT iteration, which doesn't exist yet because it IS being created. The correct execution order is:

1. Execute workstreams (Steps 1-N in plan)
2. Run post_flight.py (verification)
3. Run run_evaluator.py (scores workstreams based on execution context, NOT build log)
4. Run generate_artifacts.py (produces build log and report from execution context + scores)
5. Validate and promote drafts

The evaluator NEVER reads the current iteration's build log. It evaluates based on: event log, file existence checks, exit codes, and the design doc workstream list. The build log is an OUTPUT of the process, not an INPUT.

### Qwen Schema-Validated Harness - NEW (v9.49+)

All Qwen evaluation calls use a strict JSON schema. The validator rejects non-conforming output and provides specific error feedback for retry. This replaces the prompt-only approach.

### README Overhaul Cadence Check

v9.49 = every-3 checkpoint (v9.46 was last). Full README review required this iteration.

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Qwen schema-validated harness | P1 | Define strict JSON schema for evaluation output. Build validator. Implement retry-with-feedback loop. Replace prompt-only approach with structural enforcement. |
| W2 | Fix execution order (build log paradox) | P1 | Evaluator stops reading current build log. Evaluation based on execution context only. Build log generated AFTER evaluation. |
| W3 | Middleware tab in Flutter app | P2 | Replace Gotcha tab with MW (Middleware) tab. Display registries, components, files, overview. |
| W4 | README overhaul (3-iteration cadence) | P2 | Full review. Update stale content. Verify all links. Add MW tab documentation. |
| W5 | Post-flight + living docs | P3 | Post-flight pass. Update middleware_registry.json, architecture.mmd, changelog. |

---

## W1: Qwen Schema-Validated Harness (P1)

This is the primary deliverable. The research shows that prompt-based constraints on LLM structured output produce ~6-28% compliance. Schema + validation + feedback loops produce 99%+.

### JSON Schema for Evaluation Output

Define a strict schema that Qwen MUST conform to:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["iteration", "workstreams", "trident", "what_could_be_better"],
  "properties": {
    "iteration": {"type": "string", "pattern": "^v[0-9]+\\.[0-9]+$"},
    "workstreams": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "priority", "outcome", "evidence", "agents", "llms", "mcps", "score", "improvements"],
        "properties": {
          "id": {"type": "string", "pattern": "^W[0-9]+$"},
          "name": {"type": "string", "minLength": 5},
          "priority": {"type": "string", "enum": ["P1", "P2", "P3"]},
          "outcome": {"type": "string", "enum": ["complete", "partial", "failed", "deferred"]},
          "evidence": {"type": "string", "minLength": 10},
          "agents": {"type": "array", "items": {"type": "string"}},
          "llms": {"type": "array", "items": {"type": "string"}},
          "mcps": {
            "type": "array",
            "items": {"type": "string", "enum": ["Firebase", "Context7", "Firecrawl", "Playwright", "Dart", "-"]}
          },
          "score": {"type": "integer", "minimum": 0, "maximum": 9},
          "improvements": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2
          }
        }
      }
    },
    "trident": {
      "type": "object",
      "required": ["cost", "delivery", "performance"],
      "properties": {
        "cost": {"type": "string", "minLength": 5},
        "delivery": {"type": "string", "pattern": "^[0-9]+/[0-9]+ workstreams"},
        "performance": {"type": "string", "minLength": 10}
      }
    },
    "what_could_be_better": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 3
    }
  }
}
```

Key constraints enforced by schema:
- score maximum is 9 (never 10)
- mcps only allows the 5 valid server names + "-"
- outcome only allows 4 valid values
- improvements requires minimum 2 items per workstream
- what_could_be_better requires minimum 3 items
- delivery must match pattern "X/Y workstreams"
- iteration must match version pattern
- evidence must be at least 10 characters (not empty)

### Validation + Feedback Loop

```python
import jsonschema

EVAL_SCHEMA = json.load(open("data/eval_schema.json"))

def validate_qwen_output(output, expected_workstreams):
    """Validate Qwen's JSON against schema and workstream count."""
    errors = []

    # 1. JSON schema validation
    try:
        jsonschema.validate(output, EVAL_SCHEMA)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema error at {e.json_path}: {e.message}")

    # 2. Workstream count validation
    if len(output.get("workstreams", [])) != len(expected_workstreams):
        errors.append(
            f"Workstream count: got {len(output.get('workstreams', []))}, "
            f"expected {len(expected_workstreams)}"
        )

    # 3. Workstream name validation
    for i, ws in enumerate(output.get("workstreams", [])):
        if i < len(expected_workstreams):
            expected_name = expected_workstreams[i]
            if ws.get("name", "").lower() != expected_name.lower():
                errors.append(
                    f"W{i+1} name mismatch: got '{ws.get('name')}', "
                    f"expected '{expected_name}'"
                )

    # 4. Banned phrase check
    text = json.dumps(output)
    banned = ["successfully deployed", "robust validation", "clean release",
              "strategic shift", "healthy system", "Review...", "TBD"]
    for phrase in banned:
        if phrase.lower() in text.lower():
            errors.append(f"Banned phrase found: '{phrase}'")

    return errors

def evaluate_with_retry(qwen_prompt, expected_workstreams, max_retries=3):
    """Call Qwen, validate, retry with specific feedback on failure."""
    for attempt in range(max_retries):
        response = call_qwen(qwen_prompt)
        parsed = parse_json(response)

        if parsed is None:
            qwen_prompt += "\n\nERROR: Your response was not valid JSON. Return ONLY a JSON object."
            continue

        errors = validate_qwen_output(parsed, expected_workstreams)

        if not errors:
            return parsed  # Success

        # Build specific feedback
        feedback = "\n\nVALIDATION ERRORS (fix all before retrying):\n"
        for err in errors:
            feedback += f"  - {err}\n"
        feedback += "\nReturn the corrected JSON object."

        qwen_prompt += feedback

    # Fallback after max retries
    return build_fallback(expected_workstreams)
```

### Installation

```fish
pip install jsonschema --break-system-packages
```

### Files

- data/eval_schema.json (NEW) - strict JSON schema
- scripts/run_evaluator.py (MODIFIED) - schema validation + retry loop
- scripts/generate_artifacts.py (MODIFIED) - consumes validated JSON, not raw Qwen text
- docs/evaluator-harness.md (MODIFIED) - updated to reference schema, explain feedback loop

---

## W2: Fix Execution Order (P1)

### The Problem

run_evaluator.py tries to read docs/kjtcom-build-v{X}.md for the current iteration. But the build log IS the artifact being generated. It doesn't exist yet during evaluation. This causes "Build log not found" errors every iteration.

### The Fix

Evaluation inputs (what run_evaluator.py reads):
1. Design doc (docs/kjtcom-design-v{X}.md) - for workstream list
2. Event log (data/iao_event_log.jsonl) - for execution events
3. File system checks (key_files list) - for evidence
4. Exit codes / error counts from event log

Evaluation does NOT read:
- Build log (doesn't exist yet)
- Report (doesn't exist yet)
- Changelog (not yet updated)

Artifact generation (what generate_artifacts.py produces AFTER evaluation):
1. Build log - from event log + execution context + evaluation scores
2. Report - from evaluation JSON + scorecard + Trident
3. Changelog entry - from build log summary

### Execution Sequence (corrected)

```
1. Execute workstreams (plan Steps 1-N)
2. python3 scripts/post_flight.py (verification)
3. python3 scripts/run_evaluator.py --iteration v9.49 --workstreams
   -> Reads design doc + event log + file checks
   -> Produces validated JSON scores
   -> Saves to agent_scores.json
4. python3 scripts/generate_artifacts.py
   -> Reads agent_scores.json + event log + execution context
   -> Produces build log, report, changelog entry in docs/drafts/
5. python3 scripts/generate_artifacts.py --validate-only
   -> Cross-checks drafts against scores
6. python3 scripts/generate_artifacts.py --promote
   -> Moves validated drafts to docs/
```

---

## W3: Middleware Tab in Flutter App (P2)

Replace the Gotcha tab (tab 5) with a Middleware (MW) tab. The gotcha data moves to a section within MW or to the Gotcha Archive accessible via the bot.

### MW Tab Content

1. **Overview Card:** "kjtcom Middleware - Portable IAO Infrastructure" with component count, version, and last updated date
2. **Component Registry:** Table/list from middleware_registry.json showing:
   - Component name
   - Type (harness, script, data_store, template)
   - Version
   - Dependencies
3. **Resolved Gotchas:** Expandable list from gotcha_archive.json showing:
   - ID, description, resolution, root cause category
   - Filterable by category (environment, llm_config, dependency, etc.)
4. **Agent Roster:** Current agent list with roles (from CLAUDE.md)
5. **Pipeline Status:** 7-phase pipeline overview with last run dates

### Implementation

- New file: app/lib/widgets/mw_tab.dart
- Data source: load middleware_registry.json and gotcha_archive.json as Flutter assets
- Add to app/assets/: middleware_registry.json, gotcha_archive.json
- Update tab bar in main app scaffold: rename tab 5 from "Gotcha" to "MW"
- Keep the Gotcha tab functionality as a section within MW

---

## W4: README Overhaul (P2)

3-iteration cadence check. Full review:

1. Version/phase: v9.49
2. Entity count: verify 6,181
3. Tab list: update to include MW tab (replacing Gotcha)
4. Architecture description: current state
5. Telegram Bot section: verify commands, session memory, rating sort documented
6. Middleware section: update component count
7. Changelog: append v9.48 + v9.49 entries
8. All links: verify working
9. Claw3D link: verify documented
10. Phase 10 roadmap: update timeline

---

## W5: Post-Flight + Living Docs (P3)

1. post_flight.py - all checks pass
2. Update middleware_registry.json: add eval_schema.json, update run_evaluator.py version
3. Update architecture.mmd if MW tab changes the frontend subgraph
4. Append changelog (single file, no separate artifact)
5. Re-embed archive if significant new docs added

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K tokens. |
| Delivery | 5 workstreams. Schema-validated harness operational. Execution order fixed. MW tab live. |
| Performance | Qwen evaluation produces schema-valid JSON on first or second attempt. Zero hallucinated workstreams. Build log paradox eliminated. |

---

*Design document v9.49, April 5, 2026.*
