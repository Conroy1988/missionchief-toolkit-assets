#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ".github/development-packages/issue-171-final.py"
REPORT = ROOT / ".github" / "diagnostics" / "issue-171-final-result.txt"
with tempfile.TemporaryDirectory(prefix="issue-171-final-") as temp_dir:
    copy_root = Path(temp_dir) / "repository"
    shutil.copytree(ROOT, copy_root, ignore=shutil.ignore_patterns(".git"))
    result = subprocess.run(
        ["python3", str(copy_root / TARGET)],
        cwd=copy_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    f"exit_code={result.returncode}\n\n{result.stdout}",
    encoding="utf-8",
)
print(REPORT.relative_to(ROOT))
