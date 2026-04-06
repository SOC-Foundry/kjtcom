#!/usr/bin/env python3
"""Schema validation test cases for eval_schema.json (v9.51).

Tests valid and invalid payloads against the evaluation schema to ensure
Qwen output enforcement catches common errors.
"""
import json
import os
import sys

import jsonschema

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'eval_schema.json')

with open(SCHEMA_PATH) as f:
    SCHEMA = json.load(f)


def make_valid_payload(num_workstreams=4):
    """Return a minimal valid evaluation payload."""
    workstreams = []
    for i in range(1, num_workstreams + 1):
        workstreams.append({
            "id": f"W{i}",
            "name": f"Workstream {i} description here",
            "priority": "P1",
            "outcome": "complete",
            "evidence": "File created at scripts/foo.py, verified via flutter analyze",
            "agents": ["claude-code"],
            "llms": ["qwen3.5:9b"],
            "mcps": ["-"],
            "score": 7,
            "improvements": [
                "Could add more test coverage",
                "Could improve error messages"
            ]
        })
    return {
        "iteration": "v9.51",
        "summary": "This iteration focused on UI polish and Qwen harness hardening. All five workstreams completed with schema validation tests added.",
        "workstreams": workstreams,
        "trident": {
            "cost": "3 LLM calls (tokens not tracked)",
            "delivery": f"{num_workstreams}/{num_workstreams} workstreams complete",
            "performance": "All schema tests pass, search button fixed, 3D button accessible"
        },
        "what_could_be_better": [
            "Add integration tests for build log rendering",
            "Automate score format validation in CI",
            "Track token usage per LLM call"
        ]
    }


def validate(payload):
    """Validate payload against schema. Returns list of error messages."""
    errors = []
    validator = jsonschema.Draft7Validator(SCHEMA)
    for error in validator.iter_errors(payload):
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
        errors.append(f"{path}: {error.message}")
    return errors


def test_valid_payload():
    payload = make_valid_payload(4)
    errors = validate(payload)
    assert not errors, f"Valid payload rejected: {errors}"
    print("PASS: valid payload with 4 workstreams")


def test_valid_5_workstreams():
    payload = make_valid_payload(5)
    errors = validate(payload)
    assert not errors, f"Valid 5-workstream payload rejected: {errors}"
    print("PASS: valid payload with 5 workstreams")


def test_score_10_rejected():
    payload = make_valid_payload(1)
    payload["workstreams"][0]["score"] = 10
    errors = validate(payload)
    assert any("score" in e or "maximum" in e for e in errors), f"Score=10 not rejected: {errors}"
    print("PASS: score=10 rejected")


def test_score_negative_rejected():
    payload = make_valid_payload(1)
    payload["workstreams"][0]["score"] = -1
    errors = validate(payload)
    assert any("score" in e or "minimum" in e for e in errors), f"Score=-1 not rejected: {errors}"
    print("PASS: score=-1 rejected")


def test_invalid_mcp_rejected():
    payload = make_valid_payload(1)
    payload["workstreams"][0]["mcps"] = ["telegram"]
    errors = validate(payload)
    assert errors, f"Invalid MCP 'telegram' not rejected"
    print("PASS: invalid MCP 'telegram' rejected")


def test_empty_evidence_rejected():
    payload = make_valid_payload(1)
    payload["workstreams"][0]["evidence"] = "short"
    errors = validate(payload)
    assert any("evidence" in e or "minLength" in e for e in errors), f"Short evidence not rejected: {errors}"
    print("PASS: evidence under 10 chars rejected")


def test_invalid_outcome_rejected():
    payload = make_valid_payload(1)
    payload["workstreams"][0]["outcome"] = "success"
    errors = validate(payload)
    assert errors, f"Invalid outcome 'success' not rejected"
    print("PASS: invalid outcome 'success' rejected")


def test_missing_improvements_rejected():
    payload = make_valid_payload(1)
    payload["workstreams"][0]["improvements"] = ["only one"]
    errors = validate(payload)
    assert errors, f"Single improvement not rejected"
    print("PASS: fewer than 2 improvements rejected")


def test_missing_what_could_be_better():
    payload = make_valid_payload(1)
    payload["what_could_be_better"] = ["one", "two"]
    errors = validate(payload)
    assert errors, f"Fewer than 3 what_could_be_better not rejected"
    print("PASS: fewer than 3 what_could_be_better items rejected")


def test_summary_too_short():
    payload = make_valid_payload(1)
    payload["summary"] = "Too short."
    errors = validate(payload)
    assert any("summary" in e or "minLength" in e for e in errors), f"Short summary not rejected: {errors}"
    print("PASS: summary under 50 chars rejected")


def test_bad_delivery_format():
    payload = make_valid_payload(1)
    payload["trident"]["delivery"] = "all done"
    errors = validate(payload)
    assert errors, f"Bad delivery format not rejected"
    print("PASS: delivery without 'X/Y workstreams' pattern rejected")


def main():
    tests = [
        test_valid_payload,
        test_valid_5_workstreams,
        test_score_10_rejected,
        test_score_negative_rejected,
        test_invalid_mcp_rejected,
        test_empty_evidence_rejected,
        test_invalid_outcome_rejected,
        test_missing_improvements_rejected,
        test_missing_what_could_be_better,
        test_summary_too_short,
        test_bad_delivery_format,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__} - {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__} - {e}")
            failed += 1

    print(f"\n{passed}/{passed + failed} tests passed.")
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
