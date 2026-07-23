#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue456-v5.0.4-truth-state-dedupe.py"
REPORT = ROOT / ".github" / "diagnostics" / "issue456-v504-package-failure.txt"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

proc = subprocess.run(
    ["python3", str(PACKAGE)],
    cwd=ROOT,
    env=ENV,
    text=True,
    capture_output=True,
    timeout=240,
)
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    "ISSUE 456 V5.0.4 PACKAGE DIAGNOSTIC\n"
    f"returncode={proc.returncode}\n\n"
    "===== STDOUT =====\n"
    f"{proc.stdout}\n"
    "===== STDERR =====\n"
    f"{proc.stderr}\n",
    encoding="utf-8",
)
print(f"Captured v5.0.4 package return code {proc.returncode} without retaining attempted mutations.")
