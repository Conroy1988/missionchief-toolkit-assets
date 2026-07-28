#!/usr/bin/env python3
"""Align the native Transport Sweep contract with verified vehicle scoping."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / ".github/scripts/test_transport_sweep_native_contract.py"
text = CONTRACT.read_text(encoding="utf-8")
old = "'async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance)'"
new = "'async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance, eligibleVehicleIds)'"
if text.count(old) != 1:
    raise RuntimeError(f"Expected one native contract signature, found {text.count(old)}")
CONTRACT.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Native Transport Sweep contract requires verified vehicle scoping.")
