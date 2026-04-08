#!/usr/bin/env python3
"""Map tab and visual rendering post-flight checks. (ADR-018, v10.63)
Combines screenshot size heuristics and pHash-based visual baseline diffing.
"""
import os
import sys
import time
from pathlib import Path
from PIL import Image
try:
    import imagehash
except ImportError:
    imagehash = None

def check_render_size(page_name, screenshot_path, min_bytes=20_000):
    """Assert screenshot is non-trivial in size."""
    if not os.path.exists(screenshot_path):
        return ("fail", f"{page_name} screenshot not written")
    size = os.path.getsize(screenshot_path)
    if size < min_bytes:
        return ("fail", f"{page_name} screenshot too small ({size} bytes < {min_bytes})")
    return ("ok", f"{page_name} render size ok ({size} bytes)")

def check_visual_diff(page_name, current_path, threshold=8):
    """Compare screenshot to blessed baseline using pHash."""
    if not imagehash:
        return ("warn", "imagehash not installed, skipping diff")
        
    from iao_middleware.paths import find_project_root
    try:
        base_dir = find_project_root()
    except Exception:
        base_dir = Path.cwd()
        
    baseline_path = base_dir / "data" / "postflight-baselines" / f"{page_name}.png"
    if not baseline_path.exists():
        return ("ok", f"{page_name} baseline missing, skipping diff")

    try:
        hash_baseline = imagehash.phash(Image.open(baseline_path))
        hash_current = imagehash.phash(Image.open(current_path))
        distance = hash_baseline - hash_current
        
        if distance <= threshold:
            return ("ok", f"{page_name} visual diff ok (dist={distance})")
        else:
            return ("fail", f"{page_name} visual drift detected (dist={distance} > {threshold})")
    except Exception as e:
        return ("warn", f"{page_name} diff error: {e}")

def run_all_renders():
    """Main entry point for doctor.py."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return ("fail", "playwright not installed")

    from iao_middleware.paths import find_project_root
    try:
        base_dir = find_project_root()
    except Exception:
        base_dir = Path.cwd()

    iteration = os.environ.get("IAO_ITERATION", "unknown")
    out_dir = base_dir / "data" / "postflight-screenshots" / iteration
    out_dir.mkdir(parents=True, exist_ok=True)
    
    pages = {
        "root": "https://kylejeromethompson.com",
        "claw3d": "https://kylejeromethompson.com/claw3d.html",
        "architecture": "https://kylejeromethompson.com/architecture.html"
    }
    
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            for name, url in pages.items():
                print(f"  Screenshotting {name}...")
                screenshot_path = out_dir / f"{name}.png"
                try:
                    page.goto(url, wait_until="networkidle", timeout=30_000)
                    time.sleep(3)
                    page.screenshot(path=str(screenshot_path))
                    
                    # Size check
                    s_status, s_msg = check_render_size(name, screenshot_path)
                    results.append((s_status, s_msg))
                    
                    # Diff check
                    d_status, d_msg = check_visual_diff(name, screenshot_path)
                    results.append((d_status, d_msg))
                except Exception as e:
                    results.append(("fail", f"{name} failed: {e}"))
            
            browser.close()
    except Exception as e:
        return ("fail", f"playwright error: {e}")

    # Aggregate results
    fails = [r[1] for r in results if r[0] == "fail"]
    warns = [r[1] for r in results if r[0] == "warn"]
    
    if fails:
        return ("fail", "; ".join(fails))
    if warns:
        return ("warn", "; ".join(warns))
    return ("ok", f"{len(pages)} pages rendered and verified")

if __name__ == "__main__":
    status, msg = run_all_renders()
    print(f"  {status.upper()}: map_tab_renders ({msg})")
    sys.exit(0 if status == "ok" else 1)
