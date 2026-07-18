#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / ".github" / "diagnostics" / "issue-171-package-result.txt"
PACKAGE = Path(".github/development-packages/issue-171-ajax-dispatch-root.py")

with tempfile.TemporaryDirectory(prefix="issue-171-diagnostic-") as temp_dir:
    copy_root = Path(temp_dir) / "repository"
    shutil.copytree(ROOT, copy_root, ignore=shutil.ignore_patterns(".git"))
    result = subprocess.run(
        ["python3", str(copy_root / PACKAGE)],
        cwd=copy_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    diff = subprocess.run(
        ["git", "diff", "--no-index", "--stat", str(ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"), str(copy_root / "src" / "MissionChief_Map_Command_Toolkit.user.js")],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    "ISSUE #171 ISOLATED PACKAGE DIAGNOSTIC\n"
    f"exit_code={result.returncode}\n\n"
    "OUTPUT\n"
    f"{result.stdout}\n"
    "SOURCE DIFF STAT\n"
    f"{diff.stdout}\n",
    encoding="utf-8",
)
print(f"Wrote {REPORT.relative_to(ROOT)}")
