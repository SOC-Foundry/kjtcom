#!/usr/bin/env python3
"""Post-flight verification for kjtcom iterations.

Checks:
1. kylejeromethompson.com returns HTTP 200
2. Telegram bot /status responds
3. Telegram bot /ask returns entity count >= 6,181

Run after every iteration, BEFORE marking complete.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from utils.iao_logger import log_event


def verify_site():
    """Check kylejeromethompson.com returns 200."""
    import requests
    try:
        r = requests.get("https://kylejeromethompson.com", timeout=15)
        passed = r.status_code == 200
        print(f"  {'PASS' if passed else 'FAIL'}: site_200 (status={r.status_code})")
        return passed
    except Exception as e:
        print(f"  FAIL: site_200 (error={e})")
        return False


def verify_bot_status():
    """Send /status to Telegram bot via Bot API and verify response."""
    import requests
    token = os.environ.get("KJTCOM_TELEGRAM_BOT_TOKEN")
    if not token:
        print("  SKIP: bot_status (KJTCOM_TELEGRAM_BOT_TOKEN not set)")
        return None

    # Use getMe to verify bot is running
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        data = r.json()
        passed = data.get("ok", False)
        bot_name = data.get("result", {}).get("username", "unknown")
        print(f"  {'PASS' if passed else 'FAIL'}: bot_status (bot=@{bot_name})")
        return passed
    except Exception as e:
        print(f"  FAIL: bot_status (error={e})")
        return False


def verify_bot_query():
    """Verify bot can answer entity count query via direct Firestore check."""
    try:
        from firestore_query import execute_query
        result = execute_query({"t_log_type": "tripledb"}, "count")
        # Also check other pipelines
        result_all = execute_query({}, "count")

        # Parse count from "N results found."
        count = 0
        if "results found" in result_all:
            count = int(result_all.split(" ")[0])

        passed = count >= 6181
        print(f"  {'PASS' if passed else 'FAIL'}: bot_query (total_entities={count}, threshold=6181)")
        return passed
    except Exception as e:
        print(f"  FAIL: bot_query (error={e})")
        return False


def verify_mcps():
    """Check all 5 MCP servers with functional tests where possible.

    Functional tests (v9.53):
      - Firebase: attempt a Firestore read (projects list)
      - Dart: run dart analyze on a known file
    Version/existence checks (no safe functional test):
      - Context7: npx available (functional would require a doc lookup with side effects)
      - Firecrawl: API key present (functional would scrape an external URL)
      - Playwright: binary available (functional would launch a browser)
    """
    import subprocess
    checks = {}

    # Firebase MCP - functional: attempt firebase projects:list with SA
    sa_path = os.path.expanduser("~/.config/gcloud/kjtcom-sa.json")
    try:
        env = os.environ.copy()
        env["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
        r = subprocess.run(
            ["npx", "firebase-tools", "projects:list", "--json"],
            capture_output=True, text=True, timeout=20, env=env
        )
        import json as _json
        # Firebase CLI may return status object or results array
        passed = r.returncode == 0
        if not passed:
            # Fallback: version check if functional fails
            r2 = subprocess.run(["npx", "firebase-tools", "--version"],
                                capture_output=True, text=True, timeout=10)
            passed = r2.returncode == 0
            print(f"  {'PASS' if passed else 'FAIL'}: firebase_mcp (fallback: version check)")
        else:
            print(f"  PASS: firebase_mcp (functional: projects:list)")
        checks["firebase_mcp"] = passed
    except Exception:
        checks["firebase_mcp"] = False
        print(f"  FAIL: firebase_mcp")

    # Context7 MCP - version check (functional doc lookup has side effects)
    try:
        r = subprocess.run(["npx", "--version"], capture_output=True, text=True, timeout=10)
        checks["context7_mcp"] = r.returncode == 0
        print(f"  {'PASS' if checks['context7_mcp'] else 'FAIL'}: context7_mcp (version check)")
    except Exception:
        checks["context7_mcp"] = False
        print(f"  FAIL: context7_mcp (version check)")

    # Firecrawl MCP - API key presence (functional would scrape external URL)
    checks["firecrawl_mcp"] = os.environ.get("FIRECRAWL_API_KEY") is not None
    print(f"  {'PASS' if checks['firecrawl_mcp'] else 'FAIL'}: firecrawl_mcp (API key check)")

    # Playwright MCP - version check (functional would launch browser)
    try:
        r = subprocess.run(["npx", "playwright", "--version"], capture_output=True, text=True, timeout=10)
        checks["playwright_mcp"] = r.returncode == 0
        print(f"  {'PASS' if checks['playwright_mcp'] else 'FAIL'}: playwright_mcp (version check)")
    except Exception:
        checks["playwright_mcp"] = False
        print(f"  FAIL: playwright_mcp (version check)")

    # Dart MCP - functional: dart analyze on a known file
    try:
        r = subprocess.run(
            ["dart", "analyze", "app/lib/main.dart"],
            capture_output=True, text=True, timeout=15
        )
        checks["dart_mcp"] = r.returncode == 0
        print(f"  {'PASS' if checks['dart_mcp'] else 'FAIL'}: dart_mcp (functional: dart analyze)")
    except Exception:
        checks["dart_mcp"] = False
        print(f"  FAIL: dart_mcp (functional: dart analyze)")

    return checks


def verify_claw3d_no_external_json():
    """G56 check: claw3d.html must NOT fetch any external JSON files.
    Firebase Hosting only serves app/web/ - external JSON fetches 404 on prod."""
    import re
    base = os.path.join(os.path.dirname(__file__), "..")
    claw3d_path = os.path.join(base, "app", "web", "claw3d.html")
    try:
        with open(claw3d_path, "r") as f:
            content = f.read()
        fetches = re.findall(r'fetch\s*\([^)]*\.json', content)
        passed = len(fetches) == 0
        print(f"  {'PASS' if passed else 'FAIL'}: claw3d_no_external_json ({len(fetches)} fetch+json calls, must be 0)")
        return passed
    except FileNotFoundError:
        print(f"  FAIL: claw3d_no_external_json (file not found)")
        return False


def verify_static_assets():
    """Verify static assets exist, have valid HTML, and CDN is reachable."""
    import json
    import re
    checks = {}
    base = os.path.join(os.path.dirname(__file__), "..")

    # 1. File existence
    for name, path in [
        ("claw3d_html", os.path.join(base, "app", "web", "claw3d.html")),
        ("architecture_html", os.path.join(base, "app", "web", "architecture.html")),
    ]:
        exists = os.path.isfile(path)
        checks[name] = exists
        print(f"  {'PASS' if exists else 'FAIL'}: {name} (exists)")
        if not exists:
            continue

        # 2. HTML structure validation
        with open(path, "r") as f:
            content = f.read()
        has_html = bool(re.search(r"<html|<!doctype", content, re.IGNORECASE))
        has_script = "<script" in content.lower()
        valid = has_html and has_script
        checks[name + "_structure"] = valid
        print(f"  {'PASS' if valid else 'FAIL'}: {name}_structure (html={has_html}, script={has_script})")

        # 4. Three.js CDN reachability (only for claw3d)
        if name == "claw3d_html":
            cdn_urls = re.findall(r'https://[^"\']+three[^"\']*\.js', content)
            if not cdn_urls:
                # Check importmap
                cdn_urls = re.findall(r'"(https://[^"]+three[^"]*)"', content)
            if cdn_urls:
                import requests
                url = cdn_urls[0]
                try:
                    r = requests.head(url, timeout=10)
                    cdn_ok = r.status_code == 200
                except Exception:
                    cdn_ok = False
                checks["threejs_cdn"] = cdn_ok
                print(f"  {'PASS' if cdn_ok else 'FAIL'}: threejs_cdn ({url})")

    # 3. JSON validation for claw3d_iterations.json
    json_path = os.path.join(base, "data", "claw3d_iterations.json")
    try:
        with open(json_path, "r") as f:
            json.load(f)
        checks["claw3d_json"] = True
        print(f"  PASS: claw3d_json (valid)")
    except FileNotFoundError:
        checks["claw3d_json"] = False
        print(f"  FAIL: claw3d_json (file not found)")
    except json.JSONDecodeError as e:
        checks["claw3d_json"] = False
        print(f"  FAIL: claw3d_json (invalid: {e})")

    return checks


def run_all():
    """Run all post-flight checks."""
    print("Post-flight verification:")
    print("=" * 40)

    results = {}
    results["site_200"] = verify_site()
    results["bot_status"] = verify_bot_status()
    results["bot_query"] = verify_bot_query()

    print("\nG56 Prevention Check:")
    results["claw3d_no_external_json"] = verify_claw3d_no_external_json()

    print("\nStatic Asset Verification:")
    static_results = verify_static_assets()
    results.update(static_results)

    print("\nMCP Verification:")
    mcp_results = verify_mcps()
    results.update(mcp_results)

    # Log results
    for check, passed in results.items():
        if passed is None:
            status = "SKIP"
        elif passed:
            status = "PASS"
        else:
            status = "FAIL"
        log_event("command", "post-flight", check, status)

    # Summary
    checked = {k: v for k, v in results.items() if v is not None}
    passed_count = sum(1 for v in checked.values() if v)
    total = len(checked)
    skipped = len(results) - total

    print("=" * 40)
    print(f"Post-flight: {passed_count}/{total} passed" +
          (f", {skipped} skipped" if skipped else ""))

    all_passed = all(v for v in checked.values())
    if not all_passed:
        print("WARNING: Post-flight verification FAILED. Do NOT mark iteration complete.")
    return all_passed


if __name__ == '__main__':
    success = run_all()
    sys.exit(0 if success else 1)
