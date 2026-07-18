#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / ".github" / "development-packages" / "issue-141-v4152-wrapper.py"
OUTPUT = ROOT / ".github" / "development-packages" / "issue-141-v4152-diagnostic.txt"

result = subprocess.run(
    [sys.executable, str(RUNNER)],
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
lines = [line if len(line) <= 900 else "[oversized generated line omitted]" for line in result.stdout.splitlines()]
bounded = "\n".join(lines[-260:])[-30000:]
subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT, check=True)
subprocess.run(["git", "clean", "-fd"], cwd=ROOT, check=True)
OUTPUT.write_text(f"returncode={result.returncode}\n\n{bounded}\n", encoding="utf-8")
print(f"Captured Issue #141 v4.15.2 runner result: {result.returncode}")
