# iao

Iterative Agentic Orchestration middleware. Shared harness components for IAO-pattern projects.

**Version:** 0.1.0-alpha (Phase B - extracted to live as iao the project)

---

## What this is

iao provides:

- **Path-agnostic project root resolution** - find_project_root() works from any cwd
- **Bundle generator** - consolidated operational state per the 10-item minimum spec
- **Script + gotcha registry queries** - first-action diligence tool
- **Compatibility checker** - data-driven environment validation
- **Doctor module** - shared pre/post-flight health checks
- **iao CLI** - project, init, status, check config, check harness, push subcommands
- **Harness alignment tool** - enforces two-harness extension-only model

---

## Install

### Via install.fish (recommended)

```fish
cd iao
fish install.fish
```

The installer copies the package to ~/iao/, puts bin/iao on PATH via a fish config marker block, and runs compatibility checks.

### Via pip (development)

```fish
pip install -e iao/ --break-system-packages
```

---

## Quickstart

```fish
iao status                  # Current project, iteration, harness state
iao check config            # Resolution map + config integrity
iao check harness           # Two-harness alignment (base + project)
iao push                    # Scan for universal-candidate entries (skeleton)
iao project list            # List known IAO projects
iao init                    # Initialize .iao.json in current project
```

---

## Python API

```python
from iao import find_project_root, __version__
from iao.doctor import run_all
from iao.registry import query

root = find_project_root()
results = run_all(level="quick")
hits = query("post-flight")
```

---

## Compatibility

See [COMPATIBILITY.md](COMPATIBILITY.md) for the full matrix. v0.1.0 targets Linux + fish + Python 3.11+.

---

## License

License to be determined before v0.2.0 release.

---

*iao v0.1.0-alpha - April 2026*
