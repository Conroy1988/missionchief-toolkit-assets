#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "status" / "v4203-performance-diagnostic.txt"

with tempfile.TemporaryDirectory(prefix="v4203-performance-") as temporary:
    clone = Path(temporary) / "repo"
    shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns(".git"))
    package = clone / ".github" / "development-packages" / "v4203-performance-budget.py"
    result = subprocess.run(
        ["python3", str(package)],
        cwd=clone,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = result.stdout or ""
    lines = output.splitlines()
    important = []
    for index, line in enumerate(lines):
        if any(token in line for token in ("AssertionError", "SyntaxError", "TypeError", "ReferenceError", "VALIDATION ERROR", "CalledProcessError")):
            important = lines[max(0, index - 3):index + 16]
            break
    if not important:
        important = lines[-40:]
    REPORT.write_text(
        "v4.20.3 performance optimisation diagnostic\n"
        f"exit_status={result.returncode}\n\n"
        + "\n".join(important)
        + "\n",
        encoding="utf-8",
    )

Path(__file__).unlink(missing_ok=True)
print("Wrote isolated v4.20.3 performance diagnostic report")
