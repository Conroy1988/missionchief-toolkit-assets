#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
PAYLOAD = ROOT / ".github" / "development-packages" / "issue-141-source-budget-compaction.payload.py"
REPORT = ROOT / ".github" / "diagnostics" / "issue-144-source-budget.txt"

original_source = SOURCE.read_bytes()
try:
    result = subprocess.run(
        [sys.executable, str(PAYLOAD)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
finally:
    SOURCE.write_bytes(original_source)

output = result.stdout[-12000:]
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    "Issue #144 source-budget diagnostic\n"
    "===================================\n\n"
    f"Payload return code: {result.returncode}\n\n"
    "Bounded output:\n\n"
    + output
    + "\n",
    encoding="utf-8",
)
print(f"Recorded bounded Issue #144 diagnostic with return code {result.returncode}")
