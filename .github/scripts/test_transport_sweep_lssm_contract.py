#!/usr/bin/env python3
"""Verify LSSM ownership, delayed controls and explicit same-mission multi-ambulance returns."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/transport-sweep-lssm-contract.json"


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    own_ids = set(data["current_player_vehicle_ids"])
    for row in data["rows"]:
        html = row["html"]
        action = re.search(r'href="/vehicles/(\d+)/patient/-1"', html)
        owner = re.search(r'href="/profile/(\d+)"', html)
        fms5 = "building_list_fms_5" in html
        assert action and action.group(1) == row["vehicle_id"], row["name"]
        assert owner and owner.group(1) == row["owner_profile_id"], row["name"]
        eligible = bool(fms5 and action.group(1) not in own_ids and owner.group(1))
        assert eligible is row["eligible"], row["name"]

    eligible_rows = [row for row in data["rows"] if row["eligible"]]
    assert len(eligible_rows) >= 3, "multi-ambulance fixture must contain at least three eligible alliance rows"
    assert len({row["vehicle_id"] for row in eligible_rows}) == len(eligible_rows), "eligible alliance vehicle IDs must be unique"

    source = SOURCE.read_text(encoding="utf-8")
    required = [
        "function transportSweepReleaseVehicleIdFromHref(href)",
        "/patient\/-1",
        "function transportSweepOwnerProfileId(row)",
        "function collectTransportSweepLssmCandidates(excludedVehicleIds = null)",
        "function waitForTransportSweepLssmCandidates(excludedVehicleIds = null, timeoutMs = 18000)",
        "waitForTransportSweepLssmCandidates(attemptedVehicleIds, 18000)",
        "function activateTransportSweepLssmRelease(candidate)",
        "LSSM mission release controls",
        "rejectedAmbiguousOwner",
        "ownIds.has(String(vehicleId))",
        "attemptedVehicleIds.add(String(lssmCandidate.vehicleId))",
        "await collectTransportSweepVehicleCandidatesForMission(missionId)",
        "existing vehicle-window route remains available as a fallback",
        "Returning to ${item.caption} for remaining alliance ambulances",
        "missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');",
        "if (transportSweepReleaseConfirmationVisible()) return true;",
        "async function closeTransportSweepWindows(reason = 'navigation')",
        "const closed = await closeTransportSweepWindows(mode === 'mission' ? 'opening a mission' : 'opening a vehicle')",
        "const opened = await openTransportSweepPath(candidate.href, 'vehicle')",
        "await closeTransportSweepWindows('finishing the mission')",
    ]
    processor = re.search(r"async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep", source)
    assert processor, "transport sweep mission processor is missing"
    processor_text = processor.group(1)
    release_index = processor_text.index("transportSweepRuntime.cleared += 1")
    return_index = processor_text.index("Returning to ${item.caption} for remaining alliance ambulances", release_index)
    reopen_index = processor_text.index("missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');", return_index)
    assert release_index < return_index < reopen_index, "successful releases must explicitly return to the same mission before the next scan"
    assert "waitForTransportSweepLssmCandidates(attemptedVehicleIds, 18000)" in processor_text, "every direct-control scan must allow the full LSSM delay"

    missing = [item for item in required if item not in source]
    assert not missing, f"Missing LSSM transport sweep contract markers: {missing}"
    assert "lssmSeen ? 8000 : 18000" not in source, "A repeated mission load must not use an eight-second LSSM timeout"
    vehicle_processor = re.search(r"async function openTransportSweepVehicle\(candidate\) \{([\s\S]*?)\n    \}", source)
    assert vehicle_processor, "transport sweep vehicle opener is missing"
    assert "anchor.click()" not in vehicle_processor.group(1), "fallback vehicles must not stack over the mission via an in-window click"
    assert "pageWindow.lightboxOpen(candidate.href)" not in vehicle_processor.group(1), "fallback vehicles must use the managed single-window opener"
    opener = re.search(r"async function openTransportSweepPath\(path, mode\) \{([\s\S]*?)\n    \}", source)
    assert opener, "transport sweep path opener is missing"
    close_index = opener.group(1).index("await closeTransportSweepWindows")
    open_index = opener.group(1).index("pageWindow.lightboxOpen(path)")
    assert close_index < open_index, "the current MissionChief window must close before another opens"
    print("LSSM transport sweep contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
