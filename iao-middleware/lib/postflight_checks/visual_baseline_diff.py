#!/usr/bin/env python3
"""Visual baseline diff check (ADR-018).
Captures a screenshot and compares it to a blessed baseline using pHash.
"""
import os, sys, time, json
from PIL import Image
import imagehash

def run_check(page_name, url, threshold=8, viewport=(1440, 900)):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(f"  FAIL: visual_baseline_diff_{page_name} (playwright missing)")
        return False

    baseline_path = os.path.join("data", "postflight-baselines", f"{page_name}.png")
    if not os.path.exists(baseline_path):
        print(f"  SKIP: visual_baseline_diff_{page_name} (baseline missing)")
        return True # Don't fail if baseline not yet established

    iteration = os.environ.get("IAO_ITERATION", "unknown")
    temp_dir = os.path.join("data", "postflight-screenshots", iteration)
    os.makedirs(temp_dir, exist_ok=True)
    current_path = os.path.join(temp_dir, f"{page_name}_current.png")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]})
            page = context.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(5)
            page.screenshot(path=current_path)
            browser.close()
        
        # Compare
        hash_baseline = imagehash.phash(Image.open(baseline_path))
        hash_current = imagehash.phash(Image.open(current_path))
        distance = hash_baseline - hash_current
        
        passed = distance <= threshold
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: visual_baseline_diff_{page_name} (distance={distance}, threshold={threshold})")
        return passed
    except Exception as e:
        print(f"  FAIL: visual_baseline_diff_{page_name} (error={e})")
        return False

def main():
    # This check is meant to be called from post_flight.py
    # but can be run standalone for testing.
    pages = {
        "root": "https://kylejeromethompson.com",
        "claw3d": "https://kylejeromethompson.com/claw3d.html",
        "architecture": "https://kylejeromethompson.com/architecture.html"
    }
    all_passed = True
    for name, url in pages.items():
        if not run_check(name, url):
            all_passed = False
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
