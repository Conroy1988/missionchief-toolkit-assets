#!/usr/bin/env python3
"""Make the Issue #565 package tolerant of current candidate-line formatting."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue565_transport_sweep_no_reward_v8_2_0.py"
text = PACKAGE.read_text(encoding="utf-8")
old = '''candidate_line = "        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId);\\n"
if source.count(candidate_line) != 1:
    raise RuntimeError("Transport Sweep candidate collection marker changed")
fast_path = '''
new = '''candidate_pattern = re.compile(
    r"(?m)^[ \\t]+const candidates\\s*=\\s*collectTransportSweepVehicleCandidatesForMission\\(missionId\\)\\s*;?\\s*$"
)
candidate_matches = list(candidate_pattern.finditer(source))
if len(candidate_matches) != 1:
    raise RuntimeError(f"Expected one Transport Sweep candidate collection line, found {len(candidate_matches)}")
fast_path = '''
if text.count(old) != 1:
    raise RuntimeError("Unable to locate package candidate marker block")
text = text.replace(old, new, 1)
old = '''source = source.replace(candidate_line, fast_path + candidate_line, 1)
SOURCE.write_text(source, encoding="utf-8")
'''
new = '''source = candidate_pattern.sub(
    fast_path.rstrip("\\n") + "\\n        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId);",
    source,
    count=1,
)
SOURCE.write_text(source, encoding="utf-8")
'''
if text.count(old) != 1:
    raise RuntimeError("Unable to locate package candidate replacement")
PACKAGE.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Issue #565 package candidate marker made format tolerant.")
