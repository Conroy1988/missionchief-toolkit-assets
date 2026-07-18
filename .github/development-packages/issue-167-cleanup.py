#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTIC = ROOT / "docs" / "diagnostics" / "issue-167-approved-error.txt"

if not DIAGNOSTIC.exists():
    raise AssertionError("Issue #167 diagnostic is already absent")
DIAGNOSTIC.unlink()
try:
    DIAGNOSTIC.parent.rmdir()
except OSError:
    pass

subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["node", ".github/scripts/test_mission_requirements_runtime.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_mission_requirements_contract.py"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
print("Issue #167 diagnostic residue removed; runtime, contract and canonical validation passed")
