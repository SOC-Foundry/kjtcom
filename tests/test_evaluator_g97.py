"""G97 unit test: improvements_padded must not count as improvements (v10.66 W7)."""


def _is_core(field, core_fields):
    base = field.split("(", 1)[0]
    return base in core_fields


def test_improvements_padded_not_counted():
    core_fields = ["priority", "outcome", "score", "evidence", "improvements", "agents"]
    ws_synthesized = ["improvements_padded", "mcps", "llms"]
    core = [f for f in ws_synthesized if _is_core(f, core_fields)]
    assert core == [], f"expected [], got {core}"
    print("PASS: improvements_padded not counted as improvements")


def test_real_improvements_counted():
    core_fields = ["priority", "outcome", "score", "evidence", "improvements", "agents"]
    ws_synthesized = ["improvements", "score(malformed:x->5)"]
    core = [f for f in ws_synthesized if _is_core(f, core_fields)]
    assert set(core) == {"improvements", "score(malformed:x->5)"}, core
    print("PASS: real improvements + coerced score counted")


if __name__ == "__main__":
    test_improvements_padded_not_counted()
    test_real_improvements_counted()
    print("ALL PASS: G97")
