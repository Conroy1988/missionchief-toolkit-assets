#!/usr/bin/env python3
from __future__ import annotations

import runpy
import subprocess
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/repository-documentation-accuracy-audit.py"
TARGETS = [
    "README.md",
    "help/index.html",
    "docs/site-data.json",
    "docs/greasyfork-description.md",
    "docs/SITE.md",
    "ROADMAP.md",
    ".github/documentation-contract.json",
    ".github/scripts/check_documentation_drift.py",
]
DIAGNOSTIC = ROOT / ".github/diagnostics/repository-documentation-package.txt"
DIAGNOSTIC.parent.mkdir(parents=True, exist_ok=True)

try:
    runpy.run_path(str(PACKAGE), run_name="__main__")
except BaseException:
    result = "FAILED\n\n" + traceback.format_exc()
else:
    result = "SUCCEEDED\n"
finally:
    subprocess.run(["git", "checkout", "--", *TARGETS], cwd=ROOT, check=True)
    PACKAGE.unlink(missing_ok=True)
    DIAGNOSTIC.write_text(result, encoding="utf-8")

print(result)
