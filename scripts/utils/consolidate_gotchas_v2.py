import json
import os
import re

GOTCHA_PATH = "data/gotcha_archive.json"
GEMINI_PATH = "GEMINI.md"
CLAUDE_PATH = "CLAUDE.md"
HARNESS_PATH = "docs/evaluator-harness.md"

def extract_gotchas(path):
    gotchas = []
    if not os.path.exists(path): return gotchas
    with open(path) as f:
        content = f.read()
    
    # Support both | Gxx | and | **Gxx** |
    matches = re.finditer(r"\| \*?\*?(G\d+)\*?\*? \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", content)
    for m in matches:
        gid, title, status, action = [x.strip() for x in m.groups()]
        gotchas.append({
            "id": gid,
            "title": title,
            "status": status,
            "action": action,
            "source": os.path.basename(path)
        })
    return gotchas

def main():
    # 1. Start with the ones in GEMINI.md as the current authority
    all_gotchas = extract_gotchas(GEMINI_PATH)
    seen_ids = {g["id"] for g in all_gotchas}
    
    # 2. Add from CLAUDE.md if not seen
    for g in extract_gotchas(CLAUDE_PATH):
        if g["id"] not in seen_ids:
            all_gotchas.append(g)
            seen_ids.add(g["id"])
            
    # 3. Add from Harness if not seen
    for g in extract_gotchas(HARNESS_PATH):
        if g["id"] not in seen_ids:
            all_gotchas.append(g)
            seen_ids.add(g["id"])

    # 4. Load from current archive, renumber collisions
    with open(GOTCHA_PATH) as f:
        old_data = json.load(f)
        old_list = old_data.get("resolved_gotchas", [])
        if "registry" in old_data: old_list = old_data["registry"]

    next_id = 72
    for g in old_list:
        current_id = g.get("id")
        if current_id in seen_ids:
            new_id = f"G{next_id}"
            print(f"Renumbering collision {current_id} -> {new_id}")
            g["id"] = new_id
            next_id += 1
        
        if "description" in g and "title" not in g: g["title"] = g["description"]
        if "resolution" in g and "action" not in g: g["action"] = g["resolution"]
        if "source" not in g: g["source"] = "gotcha_archive.json (pre-v10.64)"
        
        all_gotchas.append(g)
        seen_ids.add(g["id"])

    def sort_key(g):
        m = re.match(r"G(\d+)", g["id"])
        return int(m.group(1)) if m else 999
        
    all_gotchas.sort(key=sort_key)

    consolidated = {
        "schema_version": 2,
        "last_updated": "2026-04-06",
        "registry": all_gotchas
    }
    
    with open(GOTCHA_PATH, "w") as f:
        json.dump(consolidated, f, indent=2)
    
    print(f"Consolidated {len(all_gotchas)} gotchas to {GOTCHA_PATH}")

if __name__ == "__main__":
    main()
