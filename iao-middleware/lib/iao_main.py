"""iao CLI dispatcher (v10.66 W6)."""
import argparse
import json
import os
import sys
from pathlib import Path

VERSION = "iao 0.1.0"
CONFIG_DIR = Path.home() / ".config" / "iao"
PROJECTS_FILE = CONFIG_DIR / "projects.json"
ACTIVE_FILE = CONFIG_DIR / "active.fish"


def _load_projects():
    if PROJECTS_FILE.exists():
        return json.loads(PROJECTS_FILE.read_text())
    return {"projects": {}, "active": None}


def _save_projects(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_FILE.write_text(json.dumps(data, indent=2))


def cmd_project(args):
    data = _load_projects()
    sub = args.project_cmd
    if sub == "add":
        data["projects"][args.name] = {
            "gcp_project": args.gcp_project,
            "prefix": args.prefix,
            "path": str(Path(args.path).resolve()),
        }
        _save_projects(data)
        print(f"Added project: {args.name}")
    elif sub == "list":
        if not data["projects"]:
            print("(no projects registered)")
            return
        active = data.get("active")
        for name, info in data["projects"].items():
            mark = " *" if name == active else "  "
            print(f"{mark} {name}  path={info['path']}")
    elif sub == "switch":
        if args.name not in data["projects"]:
            print(f"ERROR: unknown project: {args.name}")
            sys.exit(1)
        data["active"] = args.name
        _save_projects(data)
        info = data["projects"][args.name]
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        ACTIVE_FILE.write_text(
            f"set -gx IAO_PROJECT_ROOT {info['path']}\n"
            f"set -gx IAO_PROJECT_NAME {args.name}\n"
        )
        print(f"Switched to: {args.name}")
    elif sub == "current":
        print(data.get("active") or "(none)")
    elif sub == "remove":
        data["projects"].pop(args.name, None)
        if data.get("active") == args.name:
            data["active"] = None
        _save_projects(data)
        print(f"Removed: {args.name}")


def cmd_init(args):
    target = Path(args.path).resolve() if args.path else Path.cwd()
    iao = target / ".iao.json"
    if iao.exists() and not args.force:
        print(f"ERROR: {iao} exists. Use --force to overwrite.")
        sys.exit(1)
    iao.write_text(json.dumps({
        "iao_version": "0.1",
        "name": args.name or target.name,
        "artifact_prefix": args.name or target.name,
        "gcp_project": args.gcp_project or "",
        "env_prefix": (args.prefix or target.name).upper(),
        "current_iteration": "v0.1",
        "phase": 0,
    }, indent=2))
    (target / "docs").mkdir(exist_ok=True)
    (target / "data").mkdir(exist_ok=True)
    print(f"Initialized iao project at {target}")


def cmd_status(args):
    data = _load_projects()
    print(f"Active project: {data.get('active') or '(none)'}")
    cwd_iao = None
    cur = Path.cwd()
    while cur != cur.parent:
        if (cur / ".iao.json").exists():
            cwd_iao = cur
            break
        cur = cur.parent
    print(f"Cwd project root: {cwd_iao or '(none)'}")
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        print("Ollama: ok")
    except Exception:
        print("Ollama: down")


def cmd_stub(args):
    print(f"iao {args.cmd}: deferred to v10.67")
    sys.exit(2)


def main():
    p = argparse.ArgumentParser(prog="iao")
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd")

    pp = sub.add_parser("project")
    pps = pp.add_subparsers(dest="project_cmd")
    add = pps.add_parser("add")
    add.add_argument("name")
    add.add_argument("--gcp-project", default="")
    add.add_argument("--prefix", default="")
    add.add_argument("--path", required=True)
    add.add_argument("--no-shell-edit", action="store_true")
    pps.add_parser("list")
    sw = pps.add_parser("switch")
    sw.add_argument("name")
    pps.add_parser("current")
    rm = pps.add_parser("remove")
    rm.add_argument("name")

    pi = sub.add_parser("init")
    pi.add_argument("--path", default=None)
    pi.add_argument("--name", default=None)
    pi.add_argument("--gcp-project", default=None)
    pi.add_argument("--prefix", default=None)
    pi.add_argument("--force", action="store_true")

    sub.add_parser("status")
    sub.add_parser("eval")
    sub.add_parser("registry")

    args = p.parse_args()
    if args.cmd == "project":
        cmd_project(args)
    elif args.cmd == "init":
        cmd_init(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd in ("eval", "registry"):
        cmd_stub(args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
