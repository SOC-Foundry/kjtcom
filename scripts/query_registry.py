"""Shim: moved to iao-middleware/lib/query_registry.py in v10.66 W3."""
import sys
from pathlib import Path
_iao_lib = Path(__file__).resolve().parent.parent / "iao-middleware" / "lib"
if str(_iao_lib) not in sys.path:
    sys.path.insert(0, str(_iao_lib))
from query_registry import main  # noqa: E402,F401

if __name__ == "__main__":
    main()
