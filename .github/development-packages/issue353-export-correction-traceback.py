#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue353-performance-safe-selection-refresh.py"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue353-performance-correction.txt"

with tempfile.TemporaryDirectory(prefix="issue353-diagnostic-") as directory:
    temp_root = Path(directory) / "repo"
    shutil.copytree(
        ROOT,
        temp_root,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )
    temp_package = temp_root / PACKAGE.relative_to(ROOT)
    result = subprocess.run(
        [sys.executable, str(temp_package)],
        cwd=temp_root,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    "Issue #353 correction diagnostic\n"
    f"exit_code={result.returncode}\n\n"
    f"{result.stdout}",
    encoding="utf-8",
)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)
print(f"Exported Issue #353 correction diagnostic to {OUTPUT.relative_to(ROOT)}")
