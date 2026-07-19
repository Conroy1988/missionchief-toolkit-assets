#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
commands = [
    ["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"],
    ["node", ".github/scripts/test_mission_requirements_runtime.js"],
    [sys.executable, ".github/scripts/test_mission_requirements_contract.py"],
    [sys.executable, ".github/scripts/validate_userscript.py"],
]
for command in commands:
    subprocess.run(command, cwd=ROOT, check=True)
print("v4.20.3 Matrix package passed syntax, runtime, contract and canonical validation")
