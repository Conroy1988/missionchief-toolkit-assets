#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REL = Path(".github/development-packages/issue391-fix-migration-cleanup-token.py")
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-migration-cleanup-failure.txt"

with tempfile.TemporaryDirectory(prefix="issue391-migration-cleanup-diagnostic-") as temporary:
    sandbox = Path(temporary) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    result = subprocess.run(
        ["python3", str(sandbox / PACKAGE_REL)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )

payload = [
    "ISSUE391_MIGRATION_CLEANUP_FAILURE_V1",
    f"returncode={result.returncode}",
    "",
    "=== STDOUT ===",
    result.stdout.rstrip(),
    "",
    "=== STDERR ===",
    result.stderr.rstrip(),
    "",
]
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(payload), encoding="utf-8")
print(f"Captured migration-cleanup result code {result.returncode} in {OUTPUT.relative_to(ROOT)}")
