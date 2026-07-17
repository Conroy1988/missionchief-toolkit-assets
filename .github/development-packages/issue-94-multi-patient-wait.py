#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"

text = SOURCE.read_text(encoding="utf-8")
old = "const lssmCandidates = await waitForTransportSweepLssmCandidates(attemptedVehicleIds, lssmSeen ? 8000 : 18000);"
new = "const lssmCandidates = await waitForTransportSweepLssmCandidates(attemptedVehicleIds, 18000);"
if text.count(old) != 1:
    raise RuntimeError(f"Expected one staged LSSM wait call, found {text.count(old)}")
SOURCE.write_text(text.replace(old, new, 1), encoding="utf-8")

subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_transport_sweep_lssm_contract.py"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Issue #94 multi-patient LSSM wait correction applied")
