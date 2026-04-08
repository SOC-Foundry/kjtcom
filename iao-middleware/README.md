# iao-middleware

Iterative Agentic Orchestration middleware. Shared harness components for IAO projects, consumed by [kjtcom](https://github.com/SOC-Foundry/kjtcom) and future IAO-pattern projects.

**Version:** 0.1.0 (Phase A — authored inside kjtcom, extraction to standalone repo planned for v10.68)

---

## What this is

iao-middleware provides:

- **Path-agnostic project root resolution** — find_project_root() works from any cwd
- **Context bundle generator** — consolidated operational state in 11 sections
- **Script + gotcha registry queries** — first-action diligence tool
- **Compatibility checker** — data-driven environment validation
- **Doctor module** — shared pre/post-flight health checks
- **iao CLI** — project, init, status, check config subcommands
- **Post-flight checks** — deploy gap detection, build gatekeeper, artifacts verification

---

## Install

### Via install.fish (recommended)

```fish
cd iao-middleware
fish install.fish
```

The installer copies the package to ~/iao-middleware/, puts bin/iao on PATH via a fish config marker block, and runs compatibility checks.

### Via pip (development)

```fish
pip install -e kjtcom/iao-middleware/ --break-system-packages
```

---

## Quickstart

```fish
iao status                  # Current project, iteration, harness state
iao check config            # Resolution map + config integrity
iao check config --strict   # Promote warns to failures for CI
iao project list            # List known IAO projects
iao init                    # Initialize .iao.json in current project
```

---

## Python API

```python
from iao_middleware import find_project_root, __version__
from iao_middleware.doctor import run_all
from iao_middleware.registry import query

root = find_project_root()
results = run_all(level="quick")
hits = query("post-flight")
```

---

## Compatibility

See [COMPATIBILITY.md](COMPATIBILITY.md) for the full matrix. v0.1.0 targets Linux + fish + Python 3.11+.

---

## Contributing

This package is currently authored inside kjtcom/iao-middleware/ and will be extracted to SOC-Foundry/iao-middleware as a standalone repo in v10.68. Contributions welcome after extraction.

---

## License

License to be determined before v0.2.0 release.

---

*iao-middleware v0.1.0 — April 2026*
