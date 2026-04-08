"""W3 post-flight check (v10.63): claw3d label legibility screenshot capture.

Loads /claw3d.html headless via Playwright and captures a screenshot. Visual
verification of label legibility is still manual; this check guarantees the
screenshot exists for review and that the page renders without crashing.
"""
import os
import sys
import time

URL = "https://kylejeromethompson.com/claw3d.html"
ITERATION = os.environ.get("IAO_ITERATION", "v10.63")
OUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "postflight-screenshots", ITERATION
)
MIN_SCREENSHOT_BYTES = 5_000


def run():
    """Capture claw3d screenshot and assert non-trivial size."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  FAIL: claw3d_label_legibility (playwright not installed)")
        return False

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "claw3d.png")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1000})
            page = context.new_page()
            page.goto(URL, wait_until="domcontentloaded", timeout=30_000)
            try:
                page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception:
                pass
            # Three.js scene takes a moment to populate canvas textures
            time.sleep(4)
            page.screenshot(path=out_path, full_page=False)
            browser.close()
    except Exception as e:
        print(f"  FAIL: claw3d_label_legibility (playwright error: {e})")
        return False

    if not os.path.exists(out_path):
        print("  FAIL: claw3d_label_legibility (screenshot not written)")
        return False
    size = os.path.getsize(out_path)
    if size < MIN_SCREENSHOT_BYTES:
        print(
            f"  FAIL: claw3d_label_legibility "
            f"(screenshot {size} bytes, expected >= {MIN_SCREENSHOT_BYTES})"
        )
        return False
    print(f"  PASS: claw3d_label_legibility (screenshot {size} bytes -> {out_path})")
    return True


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
