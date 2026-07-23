#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue378-compact-engine-source.py"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue378-engine-compaction-final-failure.txt"

if not PACKAGE.is_file() or PACKAGE.is_symlink():
    raise RuntimeError("Issue #378 compactor is missing or invalid")
result = subprocess.run(
    [sys.executable, str(PACKAGE)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1"},
)
report = [
    "ISSUE378_ENGINE_COMPACTION_DIAGNOSTIC_V3",
    f"returncode={result.returncode}",
    "--- stdout ---",
    result.stdout,
    "--- stderr ---",
    result.stderr,
]
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True)
subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
print(f"Persisted final Issue #378 compactor traceback to {OUTPUT.relative_to(ROOT)}")
