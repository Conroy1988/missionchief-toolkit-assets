#!/usr/bin/env python3
"""Execute the immutable reviewed v8.3.1 package with escaped policy anchors."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ".github/development-packages/apply_v831_exact_artifact_proof.py"
REVIEWED_PACKAGE_COMMIT = "d7e4fe9671c0885407a248d0df38758169beffec"
reviewed = subprocess.check_output(
    ["git", "show", f"{REVIEWED_PACKAGE_COMMIT}:{PACKAGE}"],
    cwd=ROOT,
    text=True,
)
corrections = (
    ("types:\\n      - closed", "types:\\\\n      - closed"),
    ("workflows:\\n      - Toolkit Hotfix Gate", "workflows:\\\\n      - Toolkit Hotfix Gate"),
    ("workflows:\\n      - Validate Canonical Userscript", "workflows:\\\\n      - Validate Canonical Userscript"),
)
corrected = reviewed
for old, new in corrections:
    if corrected.count(old) != 1:
        raise RuntimeError(f"reviewed v8.3.1 policy anchor count changed for {old!r}: {corrected.count(old)}")
    corrected = corrected.replace(old, new, 1)
runtime = ROOT / ".github/development-packages/.apply_v831_exact_artifact_runtime.py"
runtime.write_text(corrected, encoding="utf-8")
try:
    subprocess.run([sys.executable, str(runtime)], cwd=ROOT, check=True)
finally:
    runtime.unlink(missing_ok=True)
