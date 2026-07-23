#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_NAME = "issue391-retire-matrix.py"
PACKAGE = ROOT / ".github" / "development-packages" / PACKAGE_NAME
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-retirement-preflight-failure.txt"

with tempfile.TemporaryDirectory(prefix="issue391-retirement-diagnostic-") as temp_dir:
    sandbox = Path(temp_dir) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    result = subprocess.run(
        [sys.executable, str(sandbox / ".github" / "development-packages" / PACKAGE_NAME)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    payload = (
        "ISSUE391_RETIREMENT_PREFLIGHT_FAILURE_V1\n"
        f"returncode={result.returncode}\n"
        "\n=== STDOUT ===\n"
        + result.stdout
        + "\n=== STDERR ===\n"
        + result.stderr
    )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(payload, encoding="utf-8")
print(f"Captured Issue #391 retirement package result with return code {result.returncode}.")
