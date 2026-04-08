# iao-middleware changelog

## 0.1.0 — 2026-04-08 (kjtcom v10.67)

First versioned release. Authored inside kjtcom/iao-middleware/ as the template for the future SOC-Foundry/iao-middleware standalone repo (v10.68 extraction target).

### Added
- iao_middleware.paths — path-agnostic project root resolution (find_project_root)
- iao_middleware.registry — script and gotcha registry queries
- iao_middleware.context_bundle — context bundle generator with §1–§11 spec
- iao_middleware.compatibility — data-driven compatibility checker
- iao_middleware.doctor — shared pre/post-flight health check module (quick/preflight/postflight levels)
- iao_middleware.cli — iao CLI with project, init, status, check config subcommands
- iao_middleware.postflight — 7 post-flight checks including dual deploy gap detection
- install.fish — idempotent fish installer with marker block
- COMPATIBILITY.md — 11 compatibility entries, data-driven checker
- pyproject.toml — pip-installable package with iao entry point
- docs/adrs/0001-phase-a-externalization.md — first middleware-internal ADR

### Notes
- LICENSE file intentionally absent; license decision deferred to v0.2.0 (v10.68 extraction)
- iao eval and iao registry subcommands stubbed, deferred to v0.2.0
- Macintosh and Windows compatibility not yet targeted
