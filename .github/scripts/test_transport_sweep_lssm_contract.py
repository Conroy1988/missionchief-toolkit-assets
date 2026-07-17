#!/usr/bin/env python3
"""Verify the LSSM alliance-patient release contract and source wiring."""
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

    source = SOURCE.read_text(encoding="utf-8")
    required = [
        "function transportSweepReleaseVehicleIdFromHref(href)",
        "/patient\/-1",
        "function transportSweepOwnerProfileId(row)",
        "function collectTransportSweepLssmCandidates(excludedVehicleIds = null)",
        "function waitForTransportSweepLssmCandidates(excludedVehicleIds = null, timeoutMs = 18000)",
        "function activateTransportSweepLssmRelease(candidate)",
        "LSSM mission release controls",
        "rejectedAmbiguousOwner",
        "ownIds.has(String(vehicleId))",
        "attemptedVehicleIds.add(String(lssmCandidate.vehicleId))",
        "await collectTransportSweepVehicleCandidatesForMission(missionId)",
        "existing vehicle-window route remains available as a fallback",
    ]
    missing = [item for item in required if item not in source]
    assert not missing, f"Missing LSSM transport sweep contract markers: {missing}"
    print("LSSM transport sweep contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
