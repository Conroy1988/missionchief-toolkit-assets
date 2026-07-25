#!/usr/bin/env python3
"""Validate the typed v6 Operational Window settings surface against current LSSM V.4."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
LSSM_HEAD = "88e41646e59a7d620624f90f1d9a0a62320c2775"


def require(source: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in source]
    assert not missing, f"{label} is missing: {missing}"


def forbid(source: str, markers: list[str], label: str) -> None:
    present = [marker for marker in markers if marker in source]
    assert not present, f"{label} contains forbidden markers: {present}"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    require(source, [
        f"commit: '{LSSM_HEAD}'",
        "const OPERATIONAL_SUITE_SETTINGS_VERSION = 2;",
        "const OPERATIONAL_SETTINGS_SCHEMA = Object.freeze([",
        "operationalWindowSettingsInnerMarkup()",
        "data-operational-settings-root",
        "section.id === 'requirements' ? ' open' : ''",
        "Array.isArray(def.o)?def.o:operationalVehicleSettingsOptions()",
        "Array.isArray(field.o)?field.o:operationalVehicleSettingsOptions()",
        "{p:'callWindow.generationDate',t:'boolean'",
        "{p:'callWindow.yellowBorderHours',t:'number'",
        "{p:'callWindow.arrClickHighlightColor',t:'color'",
        "{p:'callWindow.vehicleCounterColor',t:'select'",
        "{p:'callWindow.selectedVehicleCounterVehicleTypes',t:'multiselect'",
        "{p:'missionList.shareMissionTypes',t:'multiselect'",
        "{p:'missionList.shareMissionsMinCredits',t:'number'",
        "{p:'missionList.sortMissionsButtonColor',t:'select'",
        "{p:'missionList.eventMissions',l:'Fixed event missions'",
        "{p:'transport.autoClickSuccessButtons',t:'boolean'",
        "{p:'transport.autoOpenTransportRequest',t:'boolean'",
        "function operationalWindowApplyDependencies(",
        "data-operational-requires",
        "data-operational-forbids",
    ], "Typed Operational Window settings")

    forbid(source, [
        "function operationalWindowSettingsMarkup(",
        "Extended Mission List",
        "{p:'missionList.sortMissionsType',t:'select'",
        "{p:'missionList.sortMissionsDirection',t:'select'",
        "{p:'missionList.remainingPumpingTime',t:'boolean'",
        "{p:'missionList.eventMissions',t:'csv'",
        "updateUI(); showToast(message); }",
    ], "Operational Window settings")

    assert source.count("data-operational-settings-root") >= 2
    assert "OPERATIONAL_SETTINGS_SCHEMA.map(operationalWindowSectionMarkup).join('')" in source
    assert "mcms-op-section mcms-op-editors" in source
    print("v6 Operational Window settings passed: typed controls, current LSSM dependencies and hidden-state suppression.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
