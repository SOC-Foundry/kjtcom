# kjtcom - Agent Instructions

## Read Order
1. docs/ricksteves-design-v1.7.md
2. docs/ricksteves-plan-v1.7.md

## Security - ABSOLUTE RULES
- NEVER write API keys, tokens, or credentials into ANY file in the repo
- NEVER include API keys in build logs, reports, or changelog artifacts
- NEVER echo or print API key values in commands that get logged
- Read keys from environment variables ONLY
- If a key needs to be tested, print only "SET" or "NOT SET", never the value
- Violation of these rules is a BLOCKING failure - stop and alert Kyle

## Permissions
- CAN: flutter build web, firebase deploy --only hosting/firestore/functions
- CAN: pip install, npm install (project-level)
- CANNOT: git add / commit / push
- CANNOT: sudo (ask Kyle)

## Database Rules
- Load to "staging" database only
- NEVER write to "(default)" without Kyle approval

## Formatting
- No em-dashes. Use " - " instead.
- Use "->" for arrows.
