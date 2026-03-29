# kjtcom - Agent Instructions
# kylejeromethompson.com - Multi-Pipeline Location Intelligence Platform

## Read Order
1. docs/calgold-design-v0.5.md (architecture + Thompson Schema)
2. docs/calgold-plan-v0.5.md (current execution plan)

## Project Identity
- Repo: git@github.com:SOC-Foundry/kjtcom.git
- Firebase: kjtcom (kjtcom-c78cd) under socfoundry.com
- Domain: kylejeromethompson.com

## Permissions
- CAN: flutter build web, firebase deploy --only hosting, firebase deploy --only firestore:rules
- CAN: firebase deploy --only functions
- CAN: pip install, npm install (project-level)
- CANNOT: git add / commit / push (Kyle commits at phase boundaries)
- CANNOT: sudo (ask Kyle - sudo exception)

## Database Rules
- Development loads go to the "staging" database
- Production loads go to "(default)" database ONLY after Kyle approves
- NEVER delete documents in "(default)" without explicit Kyle approval

## Formatting
- No em-dashes. Use " - " instead.
- Use "->" for arrows.
