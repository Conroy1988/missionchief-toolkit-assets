#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs" / "diagnostics" / "issue-169-package-error.txt"
ASSEMBLER = Path(".github/development-packages/issue-169-lightbox-context.py")

with tempfile.TemporaryDirectory(prefix="issue-169-diagnostic-") as temporary:
    sandbox = Path(temporary) / "repository"
    shutil.copytree(
        ROOT,
        sandbox,
        ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"),
    )
    command = ["python3", str(ASSEMBLER)]
    try:
        result = subprocess.run(
            command,
            cwd=sandbox,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=240,
            check=False,
        )
        output = result.stdout or ""
        status = f"exit_code={result.returncode}"
    except Exception:
        output = traceback.format_exc()
        status = "diagnostic_runner_exception"

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    "ISSUE #169 ISOLATED PACKAGE DIAGNOSTIC\n"
    f"{status}\n\n"
    "COMMAND\n"
    f"{' '.join(command)}\n\n"
    "OUTPUT\n"
    f"{output}\n",
    encoding="utf-8",
)
print(f"Wrote {REPORT.relative_to(ROOT)} ({status})")
