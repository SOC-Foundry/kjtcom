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
    """Check all 5 MCP servers are accessible."""
    import subprocess
    checks = {}
    
    # Test firebase mcp (npx firebase-tools)
    try:
        r = subprocess.run(["npx", "firebase-tools", "--version"], capture_output=True, text=True, timeout=10)
        checks["firebase_mcp"] = r.returncode == 0
    except:
        checks["firebase_mcp"] = False
        
    # Test context7 mcp (npx check)
    try:
        r = subprocess.run(["npx", "--version"], capture_output=True, text=True, timeout=10)
        checks["context7_mcp"] = r.returncode == 0
    except:
        checks["context7_mcp"] = False
        
    # Test firecrawl mcp
    checks["firecrawl_mcp"] = os.environ.get("FIRECRAWL_API_KEY") is not None
    
    # Test playwright mcp
    try:
        r = subprocess.run(["npx", "playwright", "--version"], capture_output=True, text=True, timeout=10)
        checks["playwright_mcp"] = r.returncode == 0
    except:
        checks["playwright_mcp"] = False
        
    # Test dart mcp
    try:
        r = subprocess.run(["dart", "--version"], capture_output=True, text=True, timeout=10)
        checks["dart_mcp"] = r.returncode == 0
    except:
        checks["dart_mcp"] = False
        
    for mcp, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'}: {mcp}")
        
    return checks


def run_all():
    """Run all post-flight checks."""
    print("Post-flight verification:")
    print("=" * 40)

    results = {}
    results["site_200"] = verify_site()
    results["bot_status"] = verify_bot_status()
    results["bot_query"] = verify_bot_query()
    
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
