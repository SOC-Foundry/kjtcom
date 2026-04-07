import json
import os
import re

GOTCHA_PATH = "data/gotcha_archive.json"
GEMINI_PATH = "GEMINI.md"
CLAUDE_PATH = "CLAUDE.md"
HARNESS_PATH = "docs/evaluator-harness.md"

def extract_from_markdown(path):
    gotchas = {}
    if not os.path.exists(path): return gotchas
    with open(path) as f:
        content = f.read()
    
    matches = re.finditer(r"\| (G\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", content)
    for m in matches:
        gid, title, status, action = [x.strip() for x in m.groups()]
        gotchas[gid] = {
            "id": gid,
            "title": title,
            "status": status,
            "action": action,
            "source": os.path.basename(path)
        }
    return gotchas

def main():
    with open(GOTCHA_PATH) as f:
        data = json.load(f)
        existing = data.get("resolved_gotchas", [])
    
    registry = {g["id"]: g for g in existing}
    for gid in registry:
        registry[gid]["status"] = "Resolved"
        registry[gid]["source"] = "gotcha_archive.json"

    registry.update(extract_from_markdown(GEMINI_PATH))
    registry.update(extract_from_markdown(CLAUDE_PATH))
    registry.update(extract_from_markdown(HARNESS_PATH))

    sorted_gids = sorted(registry.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 999)
    
    consolidated = {
        "schema_version": 2,
        "last_updated": "2026-04-06",
        "registry": [registry[gid] for gid in sorted_gids]
    }
    
    with open(GOTCHA_PATH, "w") as f:
        json.dump(consolidated, f, indent=2)
    
    print(f"Consolidated {len(registry)} gotchas to {GOTCHA_PATH}")

if __name__ == "__main__":
    main()
