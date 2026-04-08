# iao changelog

## 0.1.0-alpha - 2026-04-08

First versioned release. Extracted from POC project to live as iao the project.

### Added
- iao.paths - path-agnostic project root resolution (find_project_root)
- iao.registry - script and gotcha registry queries
- iao.bundle - bundle generator with 10-item minimum spec
- iao.compatibility - data-driven compatibility checker
- iao.doctor - shared pre/post-flight health check module (quick/preflight/postflight levels)
- iao.cli - iao CLI with project, init, status, check config, check harness, push subcommands
- iao.harness - two-harness alignment tool (base + project, extension-only enforcement)
- iao.push - continuous-improvement skeleton (scans universal-candidates, emits PR draft)
- install.fish - idempotent fish installer with marker block
- COMPATIBILITY.md - compatibility entries, data-driven checker
- pyproject.toml - pip-installable package with iao entry point
- projects.json - 5-character project code registry (iaomw, kjtco, intra)
- docs/harness/base.md - inviolable iaomw base harness (Pillars + ADRs + Patterns)

### Notes
- LICENSE file deferred until v0.2.0
- iao eval and iao registry subcommands stubbed
- Linux + fish + Python 3.11+ targeted; macOS / Windows not yet
