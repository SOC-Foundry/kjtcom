# kjtcom Maintenance Guide

**Status:** steady-state (as of iteration 10.69.1)
**Project code:** kjtco
**Primary IP:** iaomw v0.1.0

## Overview

kjtcom has graduated from active daily development to steady-state production reference. It continues to run at kylejeromethompson.com serving location intelligence data. Future development happens at a reduced cadence.

## Maintenance Workstreams

### 1. Entity Refresh (Monthly)
- Run RickSteves and CalGold acquisition phases.
- Target: keep entities > 6,700.
- `iao status` to check baseline.

### 2. Schema Migrations (As needed)
- Follow ADR-002 and ADR-011 for `t_any_*` fields.
- Coordinate with TachTech intranet schema alignment.

### 3. Middleware Sync (Quarterly)
- Pull universal updates from `~/dev/projects/iao/` (authoring repo).
- Run `iao doctor postflight` to verify integrity.

### 4. Hosting Management
- Monitor Firebase Hosting costs and limits.
- Deploy only when visual or data changes are significant.

## Graduation Artifacts

- **Phase 10 Charter:** `docs/phase-charters/kjtcom-phase-10.md`
- **Gotcha Archive:** `data/gotcha_archive.json`
- **Script Registry:** `data/script_registry.json`
- **ADR Stream:** `kjtco/docs/harness/project.md`

## Emergency Contacts

- IAO Methodology: @iao-planning-chat
- Site Infrastructure: Kyle Thompson
- Middleware Authoring: `~/dev/projects/iao/`
