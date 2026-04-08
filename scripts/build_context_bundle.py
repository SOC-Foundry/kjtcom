#!/usr/bin/env python3
"""DEPRECATED: use scripts/build_bundle.py instead. Renamed in 10.68.1 W7."""
import sys
print("DEPRECATION: scripts/build_context_bundle.py renamed to scripts/build_bundle.py", file=sys.stderr)
from iao.bundle import main
if __name__ == "__main__":
    main()
