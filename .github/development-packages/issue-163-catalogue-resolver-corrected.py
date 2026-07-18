#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github" / "development-packages" / "issue-163-catalogue-resolver.py"
TEMP = ROOT / ".github" / "development-packages" / "issue-163-catalogue-resolver-runtime.py"
PACKAGE_ERROR = ROOT / "docs" / "diagnostics" / "issue-163-package-error.txt"
SOURCE_EXTRACT = ROOT / "docs" / "diagnostics" / "issue-163-source-extract.txt"

text = ORIGINAL.read_text(encoding="utf-8")
old = """        const quantity = missionRequirementsOptionalNumber(rawValue);\n        if (quantity === null) return null;"""
new = """        const quantityMatch = rawValue.match(/^\\s*(\\d{1,3}(?:[\\s,.]\\d{3})*|\\d+)/u);\n        const quantity = quantityMatch ? missionRequirementsNumber(quantityMatch[1]) : null;\n        if (quantity === null) return null;"""
if text.count(old) != 1:
    raise AssertionError(f"quantity parser marker: expected one match, found {text.count(old)}")
TEMP.write_text(text.replace(old, new, 1), encoding="utf-8")
try:
    subprocess.run(["python3", str(TEMP)], cwd=ROOT, check=True)
finally:
    TEMP.unlink(missing_ok=True)

ORIGINAL.unlink(missing_ok=True)
PACKAGE_ERROR.unlink(missing_ok=True)
SOURCE_EXTRACT.unlink(missing_ok=True)
for directory in [ROOT / "docs" / "diagnostics"]:
    try:
        directory.rmdir()
    except OSError:
        pass
print("Issue #163 corrected catalogue resolver candidate completed")
