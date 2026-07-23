#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github" / "development-packages" / "issue454-runtime-diagnostic.py"
REPORT = ROOT / ".github" / "diagnostics" / "issue454-runtime-diagnostic.txt"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

proc = subprocess.run(
    ["python3", str(ORIGINAL)],
    cwd=ROOT,
    env=ENV,
    text=True,
    capture_output=True,
    timeout=180,
)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    "ISSUE 454 FULL RUNTIME DIAGNOSTIC\n"
    f"returncode={proc.returncode}\n\n"
    "===== STDOUT =====\n"
    f"{proc.stdout}\n\n"
    "===== STDERR =====\n"
    f"{proc.stderr}\n",
    encoding="utf-8",
)
print(f"Persisted Issue #454 runtime report with diagnostic return code {proc.returncode}.")
