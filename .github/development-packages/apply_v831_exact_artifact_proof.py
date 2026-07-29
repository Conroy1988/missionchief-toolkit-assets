#!/usr/bin/env python3
"""Execute the immutable reviewed v8.3.1 package with a corrected policy block."""
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
replacement = r"""candidate_path = ".github/scripts/test_validation_candidate_pipeline.py"
candidate = read(candidate_path)
candidate = replace_once(
    candidate,
    '''        "types:\\n      - closed",
''',
    '''        "types:\\n      - closed",
        "workflows:\\n      - Toolkit Hotfix Gate",
''',
    "candidate fallback trigger marker",
)
candidate = replace_once(
    candidate,
    '''        'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"',
''',
    '''        'ARTIFACT_NAME="missionchief-toolkit-validation-candidate-${PR_HEAD_SHA}"',
        "workflows:\\n      - Validate Canonical Userscript",
''',
    "candidate stale trigger prohibition",
)
write(candidate_path, candidate)"""
corrected = reviewed[:segment_start] + replacement + reviewed[segment_end:]
runtime = ROOT / ".github/development-packages/.apply_v831_exact_artifact_runtime.py"
runtime.write_text(corrected, encoding="utf-8")
try:
    subprocess.run([sys.executable, str(runtime)], cwd=ROOT, check=True)
finally:
    runtime.unlink(missing_ok=True)
