import re
import json
import os

HTML_PATH = "app/web/claw3d.html"
COMPONENTS_PATH = "data/claw3d_components.json"
ITERATIONS_PATH = "data/claw3d_iterations.json"

def main():
    if not os.path.exists(HTML_PATH): return
    with open(HTML_PATH) as f: content = f.read()
    
    boards = []
    # Match board blocks more broadly
    board_blocks = re.findall(r"id: \"(.*?)\", label: \"(.*?)\", color: (.*?),.*?chips: \[(.*?)\]", content, re.DOTALL)
    for bid, blabel, bcolor, chips_content in board_blocks:
        chips = []
        # Match chips
        chip_matches = re.findall(r"\{id:\"(.*?)\", status:\"(.*?)\", detail:\"(.*?)\"(?:, color:(.*?))?\}", chips_content)
        for cid, cstatus, cdetail, ccolor in chip_matches:
            chip = {"id": cid, "label": cid, "status": cstatus, "detail": cdetail}
            if ccolor: chip["color"] = ccolor.strip()
            chips.append(chip)
        boards.append({"id": bid, "label": blabel, "color": bcolor.strip(), "components": chips})
    
    with open(COMPONENTS_PATH, "w") as f: 
        json.dump({"boards": boards}, f, indent=2)
    print(f"Revived {COMPONENTS_PATH} with {len(boards)} boards.")

    iters_match = re.search(r"var ITERATIONS = (\{.*?\});", content, re.DOTALL)
    if iters_match:
        iters_str = iters_match.group(1)
        # Fix JS to JSON
        iters_str = re.sub(r",(\s*[\]}])", r"\1", iters_str)
        # Quote keys
        iters_str = re.sub(r"([{\s])(\w+):", r'\1"\2":', iters_str)
        # Standardize quotes to double
        iters_str = iters_str.replace("'", '"')
        try:
            iters_data = json.loads(iters_str)
            with open(ITERATIONS_PATH, "w") as f: 
                json.dump(iters_data, f, indent=2)
            print(f"Revived {ITERATIONS_PATH} with {len(iters_data)} iterations.")
        except Exception as e:
            print(f"Failed to parse iterations: {e}\nString was: {iters_str[:200]}...")

if __name__ == "__main__": 
    main()
