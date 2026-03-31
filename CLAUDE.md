# kjtcom - Agent Instructions (Claude Code)

## Read Order

1. docs/kjtcom-report-v6.18.md (QA results)
2. docs/kjtcom-design-v6.15.md (Architecture Decisions)

## Context

Phase 6e Deploy. Deploy the Flutter Web app to Firebase Hosting at
kylejeromethompson.com. Domain is already verified (A record + TXT record
confirmed in Firebase Console).

## Tasks

1. flutter build web --release
2. firebase deploy --only hosting (project: kjtcom-c78cd)
3. Verify deployment at kylejeromethompson.com
4. Add Google Analytics (GA4) - Firebase console integration or gtag.js in index.html
5. Cross-browser smoke test (Chrome, Firefox)

## Shell - MANDATORY

- All commands in fish shell
- NEVER cat config.fish (G20)

## Security

- grep -rnI "AIzaSy" . before completion
- Print only SET/NOT SET for key checks

## Permissions

- CANNOT: git add / commit / push
- CANNOT: sudo

## Artifact Rules - MANDATORY

1. docs/kjtcom-build-v6.19.md
2. docs/kjtcom-report-v6.19.md
3. docs/kjtcom-changelog.md (append v6.19)
4. README.md (Phase 6e DONE)

## Formatting

- No em-dashes. Use " - " instead.
- Use "->" for arrows.
```

**Prompt:**
```
Read CLAUDE.md. Build the Flutter web release, deploy to Firebase Hosting (project kjtcom-c78cd), verify at kylejeromethompson.com, add Google Analytics (GA4), and produce all 4 mandatory artifacts for v6.19.
