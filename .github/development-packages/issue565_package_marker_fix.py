#!/usr/bin/env python3
"""Make the Issue #565 package locate a split candidate declaration safely."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue565_transport_sweep_no_reward_v8_2_0.py"
text = PACKAGE.read_text(encoding="utf-8")
old = '''candidate_line = "        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId);\\n"
if source.count(candidate_line) != 1:
    raise RuntimeError("Transport Sweep candidate collection marker changed")
fast_path = '''
new = '''candidate_call = "collectTransportSweepVehicleCandidatesForMission(missionId)"
candidate_call_index = source.find(candidate_call)
if candidate_call_index < 0 or source.find(candidate_call, candidate_call_index + 1) >= 0:
    raise RuntimeError("Expected one Transport Sweep candidate collection call")
candidate_declaration_index = source.rfind("const candidates", 0, candidate_call_index)
if candidate_declaration_index < 0:
    raise RuntimeError("Transport Sweep candidate declaration missing")
candidate_statement_start = source.rfind("\\n", 0, candidate_declaration_index) + 1
candidate_statement_end = source.find(";", candidate_call_index)
if candidate_statement_end < 0:
    raise RuntimeError("Transport Sweep candidate declaration terminator missing")
candidate_statement_end += 1
fast_path = '''
if text.count(old) != 1:
    raise RuntimeError("Unable to locate package candidate marker block")
text = text.replace(old, new, 1)
old = '''source = source.replace(candidate_line, fast_path + candidate_line, 1)
SOURCE.write_text(source, encoding="utf-8")
'''
new = '''source = (
    source[:candidate_statement_start]
    + fast_path.rstrip("\\n")
    + "\\n        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId);"
    + source[candidate_statement_end:]
)
SOURCE.write_text(source, encoding="utf-8")
'''
if text.count(old) != 1:
    raise RuntimeError("Unable to locate package candidate replacement")
PACKAGE.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Issue #565 package locates split candidate declaration by source offsets.")
