# kjtcom - Agent Instructions (Gemini CLI)

## Read Order

1. docs/kjtcom-design-v6.15.md
2. docs/kjtcom-plan-v6.15.md (execute Section C)

## Context

Phase 6a Discovery. Scrape 8 public competitor sites via Playwright MCP.

PRIMARY DESIGN REFERENCE: Panther SIEM (tachtech.runpanther.net).
Pre-staged in app/design-brief/panther/ with 3 screenshots + 1 HTML mockup.
Do NOT attempt to scrape Panther (Okta MFA, wrong landing page). Review the
pre-staged materials and use them as the #1 comparison point for all scrapes.

This is the first kjtcom run on tsP3-cos (P3 Ultra).

## Shell - MANDATORY

- All commands in fish shell via fish -c wrappers
- NEVER cat config.fish (G20)

## Security

- grep -rnI "AIzaSy" . before completion
- Print only SET/NOT SET for key checks

## MCP Tools

- Playwright: screenshots + accessibility snapshots
- Do NOT use Firecrawl (cert issues - G28)
- Do NOT scrape Panther (G29)

## Scraping Parameters

- Desktop: 1440x900 viewport
- Mobile: 375x812 viewport
- Timeout: 10s per page (networkidle)
- Max 3 min per blocked site before moving on

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v6.15.md
2. docs/kjtcom-report-v6.15.md
3. docs/kjtcom-changelog.md (append v6.15)
4. README.md (Phase 6a DONE)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
