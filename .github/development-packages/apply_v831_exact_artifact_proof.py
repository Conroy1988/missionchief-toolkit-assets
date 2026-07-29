#!/usr/bin/env python3
"""Execute the immutable reviewed v8.3.1 package with scoped policy anchors."""
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
segment_start = reviewed.index('candidate_path = ".github/scripts/test_validation_candidate_pipeline.py"')
segment_end = reviewed.index('write(candidate_path, candidate)', segment_start) + len('write(candidate_path, candidate)')
segment = reviewed[segment_start:segment_end]
corrections = (
    ("types:\\n      - closed", "types:\\\\n      - closed"),
    ("workflows:\\n      - Toolkit Hotfix Gate", "workflows:\\\\n      - Toolkit Hotfix Gate"),
    ("workflows:\\n      - Validate Canonical Userscript", "workflows:\\\\n      - Validate Canonical Userscript"),
)
for old, new in corrections:
    if segment.count(old) != 1:
        raise RuntimeError(f"scoped v8.3.1 policy anchor count changed for {old!r}: {segment.count(old)}")
    segment = segment.replace(old, new, 1)
corrected = reviewed[:segment_start] + segment + reviewed[segment_end:]
runtime = ROOT / ".github/development-packages/.apply_v831_exact_artifact_runtime.py"
runtime.write_text(corrected, encoding="utf-8")
try:
    subprocess.run([sys.executable, str(runtime)], cwd=ROOT, check=True)
finally:
    runtime.unlink(missing_ok=True)
