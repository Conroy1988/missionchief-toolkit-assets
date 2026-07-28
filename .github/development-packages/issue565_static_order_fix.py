#!/usr/bin/env python3
"""Make the Issue #565 ordering contract locate the second collection after the fast path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward.py"
text = CONTRACT.read_text(encoding="utf-8")
old = '    second_collection = processor.index("candidates = collectTransportSweepVehicleCandidatesForMission(missionId)", first_collection + 1)\n'
new = '    second_collection = processor.index("candidates = collectTransportSweepVehicleCandidatesForMission(missionId)", fast_path + 1)\n'
if text.count(old) != 1:
    raise RuntimeError(f"Expected one Issue #565 second-collection assertion, found {text.count(old)}")
CONTRACT.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Issue #565 ordering contract locates recollection after the fast path.")
