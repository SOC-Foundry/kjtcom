"""iao_paths.py - Shared path resolution for iao-middleware components.

Resolution order:
  1. IAO_PROJECT_ROOT environment variable
  2. Walk up from start (or cwd) looking for .iao.json
  3. Walk up from this file's location looking for .iao.json
  4. Raise IaoProjectNotFound
"""
import os
from pathlib import Path


class IaoProjectNotFound(Exception):
    """Raised when the project root cannot be resolved."""
    pass


def find_project_root(start: Path | None = None) -> Path:
    env_root = os.environ.get("IAO_PROJECT_ROOT")
    if env_root:
        p = Path(env_root).resolve()
        if (p / ".iao.json").exists():
            return p

    cur = (start or Path.cwd()).resolve()
    while cur != cur.parent:
        if (cur / ".iao.json").exists():
            return cur
        cur = cur.parent

    cur = Path(__file__).resolve().parent
    while cur != cur.parent:
        if (cur / ".iao.json").exists():
            return cur
        cur = cur.parent

    raise IaoProjectNotFound(
        "Could not resolve IAO project root. Set IAO_PROJECT_ROOT, "
        "run `iao project switch <name>`, or cd into a project directory "
        "containing .iao.json."
    )
