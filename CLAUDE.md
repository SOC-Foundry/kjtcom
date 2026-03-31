# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-design-v6.15.md
2. docs/kjtcom-plan-v6.15.md
3. All scrape.md files in app/scrape-archive/*/scrape.md
4. app/design-brief/panther/kjtcom-query-mockup.html
5. app/scrape-archive/ux-analysis.md

## Context

Phase 6b Design Contract. Synthesize the Phase 6a scrape archive into a
three-file design contract. No code changes to the Flutter app yet.

PRIMARY DESIGN REFERENCE: Panther SIEM query UX.
Pre-staged in app/design-brief/panther/ (3 screenshots + 1 HTML mockup).
The NoSQL query box is a live, real-time frontend to the entire production
Firestore locations collection. No local copy, no cached subset.

## Shell - MANDATORY

- claude config set preferredShell fish (one-time)
- All commands in fish shell
- NEVER cat config.fish (G20)

## Security

- grep -rnI "AIzaSy" . before completion
- Print only SET/NOT SET for key checks

## Deliverables

Produce the three-file design contract in app/design-brief/:

1. app/design-brief/design-tokens.json (colors, typography, spacing, elevation, breakpoints)
2. app/design-brief/design-brief.md (aesthetic direction, color rules, imagery strategy, tone)
3. app/design-brief/component-patterns.md (widget blueprints with token references)

Then produce all 4 mandatory artifacts:

1. docs/kjtcom-build-v6.16.md
2. docs/kjtcom-report-v6.16.md
3. docs/kjtcom-changelog.md (append v6.16)
4. README.md (Phase 6b DONE)

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

**Launch prompt:**
```
Read CLAUDE.md, then read ALL scrape.md files in app/scrape-archive/ and the Panther reference in app/design-brief/panther/. Synthesize everything into the three-file design contract (design-tokens.json, design-brief.md, component-patterns.md) in app/design-brief/. Then produce all 4 mandatory artifacts. Start with reading the scrape archive.
