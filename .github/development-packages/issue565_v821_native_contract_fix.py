#!/usr/bin/env python3
"""Advance the retained native Transport Sweep contract to v8.2.1."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / ".github/scripts/test_transport_sweep_native_contract.py"

text = CONTRACT.read_text(encoding="utf-8")
old = "async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance, eligibleVehicleIds)"
new = "async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance)"
if text.count(old) != 1:
    raise RuntimeError(f"Expected one retained old optional-release signature, found {text.count(old)}")
text = text.replace(old, new, 1)
marker = "function transportSweepOptionalReleaseControls()"
addition = "async function requestTransportSweepOptionalRelease(release)"
if addition not in text:
    if text.count(marker) != 1:
        raise RuntimeError("Unable to add completion-aware request helper contract")
    text = text.replace(marker, marker + "','" + addition, 1)
CONTRACT.write_text(text, encoding="utf-8")
print("Native Transport Sweep contract advanced to v8.2.1 completion-aware release helper.")
