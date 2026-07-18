#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
GENERATED = ".github/scripts/__pycache__/full_userscript_audit.cpython-312.pyc"
subprocess.run(["git", "checkout", "origin/main", "--", GENERATED], cwd=ROOT, check=True)
SELF.unlink(missing_ok=True)
print("Restored unrelated generated audit bytecode from main")
