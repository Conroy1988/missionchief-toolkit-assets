#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue447-v5.0.1-menu-boot-hotfix.py"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue447-v501-hotfix-preflight-failure.txt"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

with tempfile.TemporaryDirectory(prefix="issue447-hotfix-diagnostic-") as temp_dir:
    temp_root = Path(temp_dir) / "repo"
    shutil.copytree(
        ROOT,
        temp_root,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"),
    )
    temp_package = temp_root / PACKAGE.relative_to(ROOT)
    result = subprocess.run(
        ["python3", str(temp_package)],
        cwd=temp_root,
        env=ENV,
        text=True,
        capture_output=True,
    )
    report = [
        "ISSUE447 V5.0.1 HOTFIX PREFLIGHT DIAGNOSTIC",
        f"returncode={result.returncode}",
        "",
        "===== STDOUT =====",
        result.stdout,
        "",
        "===== STDERR =====",
        result.stderr,
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(report), encoding="utf-8")

print(f"Published diagnostic to {OUTPUT.relative_to(ROOT)}")
