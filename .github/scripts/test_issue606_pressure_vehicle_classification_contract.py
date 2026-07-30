#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CATALOGUE = ROOT / "src" / "data" / "mission-requirements-en_GB.json"
FIXTURE = ROOT / ".github" / "fixtures" / "issue606-pressure-vehicle-classification.json"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "9.1.2"
    assert catalogue["schemaVersion"] == 1 and catalogue["locale"] == "en_GB"
    assert fixture["schemaVersion"] == 1

    vehicle_rows = catalogue["vehicleRequirements"]
    assert len(vehicle_rows) == 76
    by_key = {row["key"]: row for row in vehicle_rows}
    assert 116 in by_key["police-car"]["types"]
    assert 5 in by_key["ambulance"]["types"]
    assert 0 in by_key["fire-engine"]["types"]
    assert "Armed Response Vehicle (ARV)" in by_key["armed-response"]["aliases"]
    assert "Police helicopter" in by_key["policehelicopter"]["aliases"]

    matching = section(source, "    const UK_VEHICLE_REQUIREMENT_CATALOGUE", "    function vehicleCoordinates(")
    for required in [
        "UK_VEHICLE_REQUIREMENT_ALIAS_INDEX",
        "resolveUkVehicleRequirement",
        "vehicleTypeIdFromRecord",
        "parts.capability.typeIds.has(typeId)",
        "classificationSignal",
        "byTypeId",
    ]:
        assert required in source or required in matching, required

    model = section(source, "    function calculateOperationalPressureModel(", "    function invalidateOperationalPressureSnapshot(")
    for required in [
        "recognisedCandidates",
        "unlocatedCandidates",
        "outsideRadiusCandidates",
        "provisionalVehicleIds",
        "unverifiedLocation",
        "confirmedAvailable",
        "outsideRadius",
    ]:
        assert required in model, required
    assert model.count("allocatedVehicleIds.add(") == 1
    assert "dispatch" not in model.lower()
    for forbidden in ["setInterval", "MutationObserver", "runtimeFetch(", "fetch("]:
        assert forbidden not in model

    board = section(source, "    function operationalPressureCapacityHtml(", "    function createOperationalPressureBoard(")
    assert "recognised" in board
    assert "confirmed in radius" in board
    assert "location unknown" in board
    sitrep = section(source, "    function operationalSitrepCapacityField(", "    async function postOperationalSitrep(")
    assert "Location-unverified slots" in sitrep
    assert "confirmed in radius" in sitrep
    assert "recognised" in sitrep

    print("Issue #606 Pressure Board classification static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
