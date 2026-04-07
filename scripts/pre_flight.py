#!/usr/bin/env python3
"""Pre-flight environment verification (ADR-011 / G71).
Automates the checklist from GEMINI.md.
Follows Pillar 6: Notes discrepancies and proceeds unless a BLOCKER fails.
"""
import os, sys, subprocess, shutil, socket
from datetime import datetime

def check(name, cmd=None, func=None, is_blocker=False):
    print(f"Checking {name}...", end=" ", flush=True)
    success = False
    details = ""
    try:
        if cmd:
            r = subprocess.run(cmd, capture_output=True, text=True, shell=isinstance(cmd, str))
            success = (r.returncode == 0)
            details = r.stdout.strip() or r.stderr.strip()
        elif func:
            success, details = func()
    except Exception as e:
        success = False
        details = str(e)

    if success:
        print("PASS")
        return True
    else:
        if is_blocker:
            print(f"BLOCKER FAIL: {details}")
            sys.exit(1)
        else:
            print(f"NOTE (Discrepancy): {details}")
            return False

def check_gpu():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], 
                          capture_output=True, text=True)
        if r.returncode != 0: return False, "nvidia-smi failed"
        free = int(r.stdout.strip().split("\n")[0])
        if free < 4000: return False, f"Low VRAM: {free}MB free (need 4000MB for W1)"
        return True, f"{free}MB free"
    except:
        return False, "nvidia-smi not found"

def check_site():
    try:
        # Simple socket check to avoid heavy dependencies in pre-flight if possible
        # but requests is already used in post-flight
        import requests
        r = requests.get("https://kylejeromethompson.com", timeout=5)
        return r.status_code == 200, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    print(f"--- PRE-FLIGHT v10.64 ({datetime.now().isoformat()}) ---")
    
    # 0. Env
    check("IAO_ITERATION env", func=lambda: (os.environ.get("IAO_ITERATION") == "v10.64", os.environ.get("IAO_ITERATION", "unset")), is_blocker=False)
    
    # 1. Inputs
    for f in ["docs/kjtcom-design-v10.64.md", "docs/kjtcom-plan-v10.64.md", "GEMINI.md", "CLAUDE.md"]:
        check(f"Input {f}", cmd=["ls", f], is_blocker=True)
        
    # 2. Ollama
    check("Ollama API", cmd="curl -s http://localhost:11434/api/tags", is_blocker=True)
    check("Qwen model", cmd="ollama list | grep qwen", is_blocker=False)
    check("Ollama load state (must be empty for W1)", 
          func=lambda: (subprocess.run(["ollama", "ps"], capture_output=True, text=True).stdout.count("\n") <= 1, "Model loaded"),
          is_blocker=False)

    # 3. GPU
    check("GPU VRAM", func=check_gpu, is_blocker=False)

    # 4. Deps
    check("Python deps", cmd=["python3", "-c", "import litellm, jsonschema, playwright; print('ok')"], is_blocker=True)
    check("Flutter", cmd="flutter --version", is_blocker=False)
    check("tmux", cmd="tmux -V", is_blocker=True)

    # 5. Network
    check("Site liveness", func=check_site, is_blocker=False)

    # 6. System
    check("Sleep Masked", cmd="systemctl status sleep.target | grep masked", is_blocker=False)

    print("--- PRE-FLIGHT COMPLETE: PROCEEDING ---")

if __name__ == "__main__":
    main()
