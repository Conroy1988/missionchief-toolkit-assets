#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
ORIGINAL = ROOT / ".github" / "development-packages" / "issue-133-documentation-sync.py"
STAGE = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "development-package-stage"

result = subprocess.run([sys.executable, str(ORIGINAL)], cwd=ROOT, text=True, capture_output=True)
if result.stdout:
    print(result.stdout, end="")
if result.stderr:
    print(result.stderr, end="", file=sys.stderr)
if result.returncode != 0:
    combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
    diagnostic = " ".join(combined.strip().split())[-1100:] or "unknown documentation synchronization failure"
    diagnostic = diagnostic.replace("**", "").replace("`", "'")
    STAGE.write_text(f"documentation-sync: {diagnostic}", encoding="utf-8")
    raise SystemExit(result.returncode)

if ORIGINAL.exists():
    ORIGINAL.unlink()
print("Applied Issue #133 documentation synchronization v2")
