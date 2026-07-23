#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET_REL = Path(".github/development-packages/issue391-update-post-retirement-settings-contract.py")
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-post-retirement-settings-failure-v4.txt"

with tempfile.TemporaryDirectory(prefix="issue391-post-retirement-settings-diagnostic-v4-") as temporary:
    sandbox = Path(temporary) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    result = subprocess.run(
        ["python3", str(sandbox / TARGET_REL)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    "ISSUE391_POST_RETIREMENT_SETTINGS_FAILURE_V4\n"
    f"returncode={result.returncode}\n\n"
    "=== STDOUT ===\n"
    f"{result.stdout}\n"
    "=== STDERR ===\n"
    f"{result.stderr}",
    encoding="utf-8",
)
print(f"Captured Issue #391 post-retirement settings diagnostic v4: returncode={result.returncode}")
