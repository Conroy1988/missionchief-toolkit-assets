#!/usr/bin/env python3
"""Issue #565 contract for completion-aware sequential optional releases."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
PERFORMANCE = ROOT / ".github/performance-budget.json"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert re.search(r"(?m)^//\s*@version\s+8\.2\.5$", source)
    assert "version: '8.2.5'" in source
    for marker in [
        "function transportSweepOptionalReleasePatientCountFromRow(row)",
        "function transportSweepOptionalReleasePatientRows()",
        "function transportSweepOptionalReleaseRowVehicleId(row)",
        "function transportSweepOptionalReleaseMissionReady()",
        "function transportSweepOptionalReleaseState(missionId)",
        "missionReady: transportSweepOptionalReleaseMissionReady()",
        "TRANSPORT_SWEEP_OPTIONAL_RELEASE_INITIAL_WAIT_MS = 6000",
        "async function waitForTransportSweepOptionalReleaseState(missionId, options = {})",
        "function transportSweepOptionalReleaseKey(missionId, vehicleId, sequence)",
        "async function requestTransportSweepOptionalRelease(release)",
        "function transportSweepOptionalReleaseProgressed(before, afterState)",
        "async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance)",
        "credentials: 'same-origin'",
        "await response.text()",
        "did not reduce the patient count",
        "completed no-reward patient release",
    ]:
        assert marker in source, marker

    helper = section(
        source,
        "    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT",
        "    function transportSweepVisibleDischargeButtons()",
    )
    assert "release.control.click()" not in helper
    assert ".click();" not in helper
    assert "MutationObserver" not in helper
    assert "setInterval(" not in helper
    assert "AbortSignalCtor.timeout" in helper
    assert "runtimeSetTimeout(" not in helper
    assert "runtimeClearTimeout(" not in helper
    assert "pageWindow?.fetch" in helper
    assert "after.patientCount < before.patientCount" in helper
    assert "latest.eligibleVehicleIds.size === 0" not in helper
    assert "latest.missionReady" in helper
    assert "const patientRows = transportSweepOptionalReleasePatientRows();" in helper
    assert "td:first-child" not in helper
    assert "patientCells.find" in helper
    assert "patientTextSource" in helper
    assert "transportSweepOptionalReleaseTextWithBreaks" in helper
    assert "nodeName || '').toUpperCase() === 'BR'" in helper
    assert "collectTransportSweepVehicleCandidates()" not in helper
    assert "collectTransportSweepVehicleCandidatesForMission(missionId)" not in helper
    assert "releaseByVehicle" in helper
    assert "details.directRow" in helper
    assert "no-reward:${ordinal}" in helper

    processor = re.search(
        r"async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep",
        source,
    )
    assert processor
    body = processor.group(1)
    assert "processTransportSweepOptionalReleaseControls(" in body
    assert "optionalEligibleVehicleIds" not in body
    assert body.index("processTransportSweepOptionalReleaseControls(") < body.index("collectTransportSweepVehicleCandidatesForMission(missionId)")
    assert "openTransportSweepVehicle(candidate)" in body

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert ".github/scripts/test_issue565_transport_sweep_no_reward.py" in preflight
    assert ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs" in preflight
    assert "## [8.2.5] - 2026-07-28" in CHANGELOG.read_text(encoding="utf-8")
    assert "same vehicle" in HELP.read_text(encoding="utf-8").lower()

    performance = PERFORMANCE.read_text(encoding="utf-8")
    assert '"approvedNetworkRequestDelta": 1' in performance
    assert '"network_request_calls": 6' in performance
    print("Issue #565 v8.2.5 real multi-cell patient-row contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
