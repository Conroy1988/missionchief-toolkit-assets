#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
cache = root / ".github/scripts/__pycache__"
for name in ["build_pages_site.cpython-312.pyc", "check_documentation_drift.cpython-312.pyc"]:
    (cache / name).unlink(missing_ok=True)
try:
    cache.rmdir()
except OSError:
    pass
print("Removed generated documentation-audit bytecode")
