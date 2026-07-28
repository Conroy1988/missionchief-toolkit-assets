#!/usr/bin/env python3
"""Issue #565 contract for sequential optional no-reward releases."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert re.search(r"(?m)^//\s*@version\s+8\.2\.0$", source)
    assert "version: '8.2.0'" in source
    for marker in [
        "TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT = 'release patient (no reward)'",
        "TRANSPORT_SWEEP_OPTIONAL_RELEASE_PATH",
        "function transportSweepOptionalReleaseDetails(control)",
        "function transportSweepOptionalReleaseControls()",
        "function transportSweepOptionalReleaseControlForVehicle(vehicleId)",
        "function findTransportSweepOptionalReleaseControl(missionId, eligibleVehicleIds, excludedReleaseKeys = null)",
        "async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance, eligibleVehicleIds)",
        "Release patient (No reward) remained available",
        "await closeTransportSweepWindows('reopening mission after no-reward patient release')",
        "await openTransportSweepPath(`/missions/${missionId}`, 'mission')",
        "recordTransportSweepConfirmedRelease(",
    ]:
        assert marker in source, marker

    helper = section(
        source,
        "    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT",
        "    function transportSweepVisibleDischargeButtons()",
    )
    assert r"^\/vehicles\/(?<vehicleId>\d+)\/patient\/-1" in helper
    for forbidden in [
        "GM_xmlhttpRequest",
        "fetch(",
        "setInterval(",
        "setTimeout(",
        "MutationObserver",
        "missionIndex",
        "setTransportSweepMissionProgress",
        "completeTransportSweepMissionProgress",
        "finaliseTransportSweepMissionProgress",
    ]:
        assert forbidden not in helper, forbidden

    processor_match = re.search(
        r"async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep",
        source,
    )
    assert processor_match
    processor = processor_match.group(1)
    assert "processTransportSweepOptionalReleaseControls(" in processor
    assert "collectTransportSweepVehicleCandidatesForMission(missionId)" in processor
    first_collection = processor.index("let candidates = collectTransportSweepVehicleCandidatesForMission(missionId)")
    fast_path = processor.index("processTransportSweepOptionalReleaseControls(")
    second_collection = processor.index("candidates = collectTransportSweepVehicleCandidatesForMission(missionId)", fast_path + 1)
    assert first_collection < fast_path < second_collection
    assert "optionalEligibleVehicleIds" in processor
    assert "clearedHere += optionalReleaseResult.cleared" in processor
    assert "eligibleVehicleIds.has(details.vehicleId)" in helper
    assert "!optionalReleaseResult.missionAvailable" in processor
    assert "openTransportSweepVehicle(candidate)" in processor

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert ".github/scripts/test_issue565_transport_sweep_no_reward.py" in preflight
    assert ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs" in preflight
    assert "## [8.2.0] - 2026-07-28" in CHANGELOG.read_text(encoding="utf-8")
    assert "Release patient (No reward)" in HELP.read_text(encoding="utf-8")
    print("Issue #565 optional no-reward Transport Sweep contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
