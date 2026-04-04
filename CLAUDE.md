# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v9.31.md (DIAGNOSTIC-FIRST approach for persistent bugs)
2. docs/kjtcom-plan-v9.31.md (execute Section B)

## Context

Phase 9 bug fix iteration. FOUR PERSISTENT BUGS that failed 2-3 previous fix attempts:
- W1: 1000-result limit (attempt #4) - grep EVERY file, not just firestore_provider
- W2: Quote cursor (attempt #4) - trace ref.listen behavior, add debugPrint
- W3: Autocomplete not showing - verify asset registration, overlay creation, detection logic
- W4: TripleDB results not populating - verify data exists, query dispatches correctly

Plus: W5 clear button, W6 dependency update (pre-flight only)

## CRITICAL RULE: DIAGNOSTIC FIRST

For EACH persistent bug:
1. Read the ENTIRE relevant file (cat it, not just grep)
2. grep ALL files in app/lib/ for related patterns
3. Add debugPrint at decision points
4. THEN write the fix based on what you found
5. If you cannot verify the fix works on live site, mark it FAIL not PASS

## CRITICAL RULE: POST-FLIGHT VERIFICATION

After deploy, use Playwright MCP to navigate to kylejeromethompson.com and capture screenshots.
If CanvasKit blocks DOM interaction (G47), document the limitation honestly.
NEVER mark a fix as confirmed without live evidence (G48).

## Shell - MANDATORY

- All commands in fish shell
- NEVER cat config.fish or SA JSON files (G20, G11)

## Security

- grep -rnI "AIzaSy" . before completion

## Flutter Requirements

- flutter analyze + flutter test after every change
- Build: cd app && flutter build web
- Deploy: cd ~/dev/projects/kjtcom && firebase deploy --only hosting

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v9.31.md (MUST include diagnostic grep output + Playwright screenshots)
2. docs/kjtcom-report-v9.31.md (MUST honestly mark PASS/FAIL per bug)
3. docs/kjtcom-changelog.md (append v9.31)
4. README.md (update if needed)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
