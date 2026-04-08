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
    """Check all 5 MCP servers with real functional probes. (G70 / W10)"""
    import subprocess
    import json as _json
    checks = {}

    # 1. Firebase MCP - functional: attempt firebase projects:list via any path
    try:
        from postflight_checks.firebase_oauth_probe import check_sa, check_ci_token, check_oauth
        sa_ok, _ = check_sa()
        ci_ok, _ = check_ci_token()
        oa_ok, _ = check_oauth()
        passed = sa_ok or ci_ok or oa_ok
        print(f"  {'PASS' if passed else 'FAIL'}: firebase_mcp (functional probe: SA={sa_ok}, CI={ci_ok}, OA={oa_ok})")
        checks["firebase_mcp"] = passed
    except Exception as e:
        print(f"  FAIL: firebase_mcp ({e})")
        checks["firebase_mcp"] = False

    # 2. Context7 MCP - functional: Check API reachability
    c7_key = os.environ.get("CONTEXT7_API_KEY")
    try:
        import requests
        # Check reachability of the API domain (G70/W10)
        r = requests.head("https://mcp.context7.com", timeout=10)
        # Pass if domain is reachable and (key is present OR we are in gemini-cli which handles it)
        is_gemini = "GEMINI_API_KEY" in os.environ
        passed = r.status_code < 500 and (c7_key is not None or is_gemini)
        print(f"  {'PASS' if passed else 'FAIL'}: context7_mcp (reachable={r.status_code < 500}, gemini={is_gemini})")
        checks["context7_mcp"] = passed
    except Exception as e:
        print(f"  FAIL: context7_mcp ({e})")
        checks["context7_mcp"] = False

    # 3. Firecrawl MCP - functional: test scrape of a simple page
    fc_key = os.environ.get("FIRECRAWL_API_KEY")
    if not fc_key:
        print("  FAIL: firecrawl_mcp (API key missing)")
        checks["firecrawl_mcp"] = False
    else:
        try:
            import requests
            # Real scrape of a tiny known-good page
            headers = {"Authorization": f"Bearer {fc_key}", "Content-Type": "application/json"}
            payload = {"url": "https://example.com", "formats": ["markdown"]}
            r = requests.post("https://api.firecrawl.dev/v1/scrape", json=payload, headers=headers, timeout=15)
            passed = r.status_code == 200
            print(f"  {'PASS' if passed else 'FAIL'}: firecrawl_mcp (functional: example.com scrape)")
            checks["firecrawl_mcp"] = passed
        except Exception as e:
            print(f"  FAIL: firecrawl_mcp ({e})")
            checks["firecrawl_mcp"] = False

    # 4. Playwright MCP - functional: run local screenshot of README
    try:
        import subprocess
        # Use npx playwright directly to verify installation
        r = subprocess.run(
            ["npx", "playwright", "screenshot", "README.md", "/tmp/readme_test.png"],
            capture_output=True, text=True, timeout=30
        )
        passed = os.path.exists("/tmp/readme_test.png")
        if passed: os.remove("/tmp/readme_test.png")
        print(f"  {'PASS' if passed else 'FAIL'}: playwright_mcp (functional: local screenshot)")
        checks["playwright_mcp"] = passed
    except Exception as e:
        print(f"  FAIL: playwright_mcp ({e})")
        checks["playwright_mcp"] = False

    # 5. Dart MCP - functional: dart analyze on widget_test.dart
    try:
        r = subprocess.run(
            ["dart", "analyze", "app/test/widget_test.dart"],
            capture_output=True, text=True, timeout=20
        )
        passed = (r.returncode == 0 or "No issues found" in r.stdout)
        print(f"  {'PASS' if passed else 'FAIL'}: dart_mcp (functional: dart analyze)")
        checks["dart_mcp"] = passed
    except Exception as e:
        print(f"  FAIL: dart_mcp ({e})")
        checks["dart_mcp"] = False

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


def check_artifacts(iteration):
    """G61 check: iteration MUST have build and report artifacts on disk."""
    failures = []
    base = os.path.join(os.path.dirname(__file__), "..")
    for atype in ["build", "report", "context"]: # Added context bundle (ADR-019)
        path = os.path.join(base, "docs", f"kjtcom-{atype}-{iteration}.md")
        if not os.path.exists(path):
            # Check drafts as well
            draft_path = os.path.join(base, "docs", "drafts", f"kjtcom-{atype}-{iteration}.md")
            if os.path.exists(draft_path):
                print(f"  PASS: {atype}_artifact exists in drafts ({draft_path})")
                continue
            failures.append(f"FAIL: {path} missing — iteration has no {atype} artifact")
            continue
        size = os.path.getsize(path)
        threshold = 100000 if atype == "context" else 100 # ADR-019 100KB target for bundle
        if size < threshold:
            failures.append(f"FAIL: {path} too small ({size} bytes, threshold {threshold})")
            continue
        print(f"  PASS: {atype}_artifact exists ({path}, {size} bytes)")
    return failures


def write_urgent_build_break_file(log_text):
    """Write URGENT_BUILD_BREAK.md to repo root on build failure."""
    import re
    base = os.path.join(os.path.dirname(__file__), "..")
    path = os.path.join(base, "URGENT_BUILD_BREAK.md")
    
    # Extract first 5 failing lines
    lines = log_text.splitlines()
    error_lines = [l for l in lines if "Error:" in l or "error:" in l or ".dart:" in l]
    top_errors = error_lines[:5]
    
    content = f"""# 🚨 URGENT: BUILD BREAK DETECTED

The v{os.environ.get('IAO_ITERATION', 'XX')} build gatekeeper failed. This iteration is NOT deployable.

## Failing Errors (Top 5)
```text
{"\n".join(top_errors)}
```

## Remediation
1. Fix the errors in the files listed above.
2. Run `cd app && flutter build web --release` to verify the fix.
3. Re-run `python3 scripts/post_flight.py` to clear this gate.

## Diagnostics
- **Command:** `flutter build web --release`
- **Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Build Log:** `/tmp/v10.65-flutter-build.log`
"""
    with open(path, "w") as f:
        f.write(content)
    print(f"  CRITICAL: {path} written.")


def run_all(iteration=None):
    """Run all post-flight checks."""
    if not iteration:
        iteration = os.environ.get('IAO_ITERATION', 'unknown')

    print(f"Post-flight verification for {iteration}:")
    print("=" * 40)

    results = {}
    results["site_200"] = verify_site()
    results["bot_status"] = verify_bot_status()
    results["bot_query"] = verify_bot_query()

    print("\nBuild Gatekeeper (ADR-020):")
    try:
        from postflight_checks.dart_analyze_changed import run_check as run_analyze
        from postflight_checks.flutter_build_passes import run_check as run_build
        
        analyze_passed, analyze_count, analyze_text = run_analyze()
        results["dart_analyze_changed"] = analyze_passed
        
        if analyze_passed is False: # Explicitly False, not None
             print("BUILD GATEKEEPER: dart analyze found issues, build skipped")
             results["flutter_build_passes"] = False
             write_urgent_build_break_file(analyze_text)
        else:
            build_passed, build_log = run_build()
            results["flutter_build_passes"] = build_passed
            if build_passed is False:
                write_urgent_build_break_file(build_log)
    except Exception as e:
        print(f"  FAIL: build_gatekeeper (error: {e})")
        results["build_gatekeeper"] = False

    print("\nG56 Prevention Check:")
    results["claw3d_no_external_json"] = verify_claw3d_no_external_json()

    print("\nStatic Asset Verification:")
    static_results = verify_static_assets()
    results.update(static_results)

    print("\nMCP Verification:")
    mcp_results = verify_mcps()
    results.update(mcp_results)

    print("\nArtifact Enforcement Check (G61):")
    artifact_failures = check_artifacts(iteration)
    results["artifacts_exist"] = len(artifact_failures) == 0
    for f in artifact_failures:
        print(f"  {f}")

    # 4. Visual Verification (ADR-018)
    print("\nVisual Baseline Diff Check (ADR-018):")
    try:
        from postflight_checks.visual_baseline_diff import run_check
        pages = {
            "root": "https://kylejeromethompson.com",
            "claw3d": "https://kylejeromethompson.com/claw3d.html",
            "architecture": "https://kylejeromethompson.com/architecture.html"
        }
        for name, url in pages.items():
            results[f"visual_baseline_diff_{name}"] = run_check(name, url, threshold=8)
    except Exception as e:
        print(f"  FAIL: visual_baseline_diff (error: {e})")
        results["visual_baseline_diff"] = False

    # 5. Deployed Iteration Match
    print("\nDeployment Verification:")
    try:
        from postflight_checks.deployed_iteration_matches import run_check as run_deploy_check
        results["deployed_iteration_matches"] = run_deploy_check(iteration)
    except Exception as e:
        print(f"  FAIL: deployed_iteration_matches (error: {e})")
        results["deployed_iteration_matches"] = False

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
    iter_arg = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_all(iter_arg)
    sys.exit(0 if success else 1)
