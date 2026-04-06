# kjtcom - Design Document v9.51

**Phase:** 9 - App Optimization
**Iteration:** 51
**Date:** April 5, 2026
**Recommended Agent:** Claude Code
**Focus:** UI Polish + Qwen Score Scale Fix + Build Log Rendering + Harness Hardening

---

## WORKSTREAMS

| # | Workstream | Priority | Description |
|---|-----------|----------|-------------|
| W1 | Fix Search button layout + add 3D button | P1 | Search button scrunched on MW tab view. Add "3D" button/link on index.html linking to claw3d.html. |
| W2 | Fix Qwen score scale (8/9 -> 8/10) | P1 | Qwen interprets max=9 as "out of 9" not "0-9 on 10-point scale." Clarify in schema and harness. |
| W3 | Fix build log raw JSON rendering | P1 | Build logs still contain raw JSON dumps in execution section. generate_artifacts.py must render build logs as markdown prose, same as reports. |
| W4 | Qwen harness hardening (continued) | P1 | Review v9.50 output for remaining patterns. Tighten harness rules. Add test cases for schema validation. |
| W5 | Post-flight + living docs | P2 | Post-flight pass. Changelog append. README version bump. |

---

## W1: UI Fixes (P1)

### Search Button Fix
The Search button is scrunched/overlapping on the MW tab viewport. Likely a layout constraint issue in the query editor or tab bar area when the MW tab is active. Check:
- app/lib/widgets/query_editor.dart - button layout
- app/lib/widgets/app_shell.dart - tab bar spacing
- Ensure the search button has proper padding/margin regardless of active tab

### 3D Button
Add a "3D" button or icon link in the app header/nav area that opens claw3d.html. Options:
- IconButton with a 3D cube icon (Icons.view_in_ar or Icons.hub) in the app bar
- Links to /claw3d.html (same domain, opens in browser)
- Consistent with the gothic/SIEM visual identity

---

## W2: Fix Score Scale (P1)

### The Bug
eval_schema.json says `"maximum": 9` for score. Qwen reads this as "scores are 0-9, out of 9" and reports "8/9". The intended meaning is "scores are 0-9, on a 10-point scale where 10 is prohibited" and should be reported as "8/10."

### Fix

In data/eval_schema.json, update the score description:
```json
"score": {
  "type": "integer",
  "minimum": 0,
  "maximum": 9,
  "description": "Score on a 10-point scale (0-10) where 10 is prohibited. Maximum allowed is 9. Report as X/10, not X/9. Example: 8/10, not 8/9."
}
```

In docs/evaluator-harness.md, add:
```
## Score Reporting
Scores are on a 10-POINT scale (0-10) where 10 is prohibited. The maximum you can give is 9/10.
Report scores as X/10 (e.g., 8/10, 7/10, 9/10). NEVER report as X/9.
```

In scripts/generate_artifacts.py, when rendering the scorecard table, format scores as `{score}/10` regardless of what Qwen returns.

---

## W3: Fix Build Log Raw JSON (P1)

### The Bug
Build logs from generate_artifacts.py contain raw JSON in the execution section:
```
{"iteration":"v9.50","summary":"This iteration consolidated...","workstreams":[...
```
This should be rendered as markdown prose with proper sections.

### Fix

Add `render_build_markdown(evaluation_json)` to generate_artifacts.py:
```python
def render_build_markdown(eval_data):
    """Convert evaluation JSON into markdown build log format."""
    lines = []
    lines.append(f"## EXECUTION LOG\n")
    lines.append(eval_data.get("summary", "No summary available."))
    lines.append("")

    for ws in eval_data.get("workstreams", []):
        outcome_label = ws["outcome"].upper()
        lines.append(f"**{ws['id']} ({ws.get('priority', 'P2')}): {ws['name']} - {outcome_label}**")
        lines.append(f"- Evidence: {ws.get('evidence', 'None')}")
        for imp in ws.get("improvements", []):
            lines.append(f"- Improvement: {imp}")
        lines.append("")

    return "\n".join(lines)
```

Apply this renderer in the build template generation path, same way render_report_markdown() works for reports.

---

## W4: Qwen Harness Hardening (P1)

### Review v9.50 Output

Patterns that improved (keep reinforcing):
- MCPs: "-" for non-MCP workstreams (correct)
- Agent: "claude-code" (correct)
- Summary: plain text prose (correct)
- Workstream count: 4/4 matching design doc (correct)

Patterns still needing work:
- Score reported as X/9 instead of X/10 (fix in W2)
- Build log raw JSON (fix in W3)
- LLMs column says "qwen-max" - should be "qwen3.5:9b" (the actual model name)
- "file_op" event type in event log - not a standard type (should be command or api_call)
- Trident cost says "0 tokens (no LLM calls recorded)" but event log shows 3-4 llm_calls

### Additional Harness Rules

Add to evaluator-harness.md:
```
## LLM Names
Use exact Ollama model names: qwen3.5:9b, nemotron-mini:4b, haervwe/GLM-4.6V-Flash-9B, nomic-embed-text.
For API models: gemini-2.5-flash (via litellm), claude-opus-4-6.
Do NOT use "qwen-max" or other aliases.

## Score Format
Always X/10. Never X/9. Maximum is 9/10.

## Trident Cost
Count the llm_call events in the event log. If tokens field is populated, sum them.
If tokens field is null, report "N LLM calls (tokens not tracked)."
Do NOT say "0 tokens" if llm_call events exist.
```

### Schema Validation Test Cases

Create scripts/test_eval_schema.py with valid and invalid test payloads:
- Valid: 4 workstreams, scores 0-9, MCPs from whitelist
- Invalid: score=10 (should reject)
- Invalid: 6 workstreams when design doc has 4 (should reject)
- Invalid: MCPs=["telegram"] (should reject)
- Invalid: empty evidence (should reject)

---

## W5: Post-Flight + Living Docs (P2)

1. post_flight.py - all checks pass
2. Verify 3D button works on live site
3. Verify search button not scrunched after fix
4. Append changelog to single file
5. README version bump to v9.51
6. Deploy

---

## TRIDENT

| Prong | Target |
|-------|--------|
| Cost | $0. <50K tokens. |
| Delivery | 5 workstreams. UI polished. Score scale fixed. Build logs readable. |
| Performance | Qwen scores reported as X/10. Build log has markdown prose, not JSON. Search button properly sized. 3D button accessible. |

---

*Design document v9.51, April 5, 2026.*
