#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue454-v5.0.3-preboot-tdz-recovery.py"
REPORT = ROOT / ".github" / "diagnostics" / "issue454-v5.0.3-preflight.txt"
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
    "ISSUE 454 V5.0.3 PREFLIGHT DIAGNOSTIC\n"
    f"returncode={proc.returncode}\n\n"
    "===== STDOUT =====\n"
    f"{proc.stdout}\n\n"
    "===== STDERR =====\n"
    f"{proc.stderr}\n",
    encoding="utf-8",
)
print(f"Persisted v5.0.3 preflight diagnostic with package return code {proc.returncode}.")
