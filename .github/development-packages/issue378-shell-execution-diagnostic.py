#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SHELL_PACKAGE = ROOT / ".github" / "development-packages" / "issue378-operational-suite-shell.py"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue378-shell-execution-traceback.txt"

if not SHELL_PACKAGE.is_file() or SHELL_PACKAGE.is_symlink():
    raise RuntimeError("Issue #378 shell package is missing or invalid")

result = subprocess.run(
    [sys.executable, str(SHELL_PACKAGE)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    env={**os.environ, "PYTHONUNBUFFERED": "1"},
)

report = [
    "ISSUE378_SHELL_EXECUTION_DIAGNOSTIC",
    f"returncode={result.returncode}",
    "--- stdout ---",
    result.stdout,
    "--- stderr ---",
    result.stderr,
]

# Restore the exact reviewed branch state. The diagnostic is observational only.
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True)
subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
print(f"Persisted Issue #378 shell execution traceback to {OUTPUT.relative_to(ROOT)}")
