#!/usr/bin/env python3
"""Bless a visual baseline for post-flight verification (ADR-018).
Captures a screenshot of a URL and saves it as the "blessed" baseline.
"""
import os, sys, time, argparse

def bless(page_name, url, viewport=(1440, 900)):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed")
        return False

    out_dir = "data/postflight-baselines"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{page_name}.png")

    print(f"Blessing {page_name} from {url}...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]})
            page = context.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(5) # Wait for CanvasKit/ThreeJS
            page.screenshot(path=out_path)
            browser.close()
        print(f"DONE: {out_path} ({os.path.getsize(out_path)} bytes)")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("page", help="Page name (root, claw3d, architecture)")
    args = parser.parse_args()

    urls = {
        "root": "https://kylejeromethompson.com",
        "claw3d": "https://kylejeromethompson.com/claw3d.html",
        "architecture": "https://kylejeromethompson.com/architecture.html"
    }

    if args.page not in urls:
        print(f"ERROR: Unknown page {args.page}. Use {list(urls.keys())}")
        sys.exit(1)

    if bless(args.page, urls[args.page]):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
