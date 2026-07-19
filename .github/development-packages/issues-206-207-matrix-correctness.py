#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / ".github" / "development-packages"
parts = [
    PACKAGE_DIR / "issues-206-207-source-capabilities.py",
    PACKAGE_DIR / "issues-206-207-source-operational.py",
    PACKAGE_DIR / "issues-206-207-source-coverage.py",
    PACKAGE_DIR / "issues-206-207-source-shadow-removal.py",
    PACKAGE_DIR / "issues-206-207-source-authority.py",
    PACKAGE_DIR / "issues-206-207-source-authority-compat.py",
    PACKAGE_DIR / "issues-206-207-tests.py",
    PACKAGE_DIR / "issues-206-207-docs.py",
    PACKAGE_DIR / "issues-206-207-self-test.py"
]
for part in parts:
    runpy.run_path(str(part), run_name="__main__")
for part in parts:
    part.unlink(missing_ok=True)
(ROOT / ".github" / "workflows" / "issues-206-207-diagnostic.yml").unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
print("Prepared Toolkit 4.20.3 Matrix correctness hotfix for Issues #206 and #207")
