#!/usr/bin/env python3
"""Verify the fixture-backed live mission requirements ownership, calculation and layout contract."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/mission-requirements-contract.json"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    for case in data["calculationCases"]:
        still_needed = max(0, case["missing"] - case["enRoute"])
        covered = case["selected"] >= still_needed
        assert still_needed == case["stillNeeded"], case["name"]
        assert covered is case["covered"], case["name"]

    required_markers = [
        "missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements'",
        "missionRequirements: true",
        "merged.missionRequirements = merged.missionRequirements !== false",
        "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([",
        "function missionRequirementsParseText(rawText, group = 'vehicles')",
        "function missionRequirementsResolve(candidate, parsed)",
        "function missionRequirementsOverallState(rows, unresolved)",
        "function missionRequirementsLssmActive(candidate, source)",
        "function missionRequirementsCollectUnits(candidate, mode)",
        "function missionRequirementsEnsureRecord(candidate, source)",
        "function observeMissionRequirementsDocument(doc)",
        "function installMissionRequirementsWindows()",
        "runtimeOnCleanup(() => {",
        "source.parentNode?.insertBefore(panel, source)",
        "missionRequirementsHideSource(source)",
        "missionRequirementsRestoreSource(record.source)",
        "#missing_text",
        "#mission_vehicle_driving",
        "#vehicle_show_table_body_all",
        "#occupied",
        ".vehicle_checkbox",
        ".alert-missing-vehicles",
        "scheduleMissionRequirementsScan(35)",
        "installMissionRequirementsWindows();",
        "${makeToggleButton('missionRequirements'",
        "missionRequirements: state.missionRequirements",
        "Mission Requirements on",
    ]
    missing = [marker for marker in required_markers if marker not in source]
    assert not missing, f"Missing mission requirements contract markers: {missing}"

    assert source.count("function installMissionRequirementsWindows()") == 1
    assert source.count("function scanMissionRequirementsWindows()") == 1
    assert source.count("source.parentNode?.insertBefore(panel, source)") == 1
    assert source.count("missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements'") == 1

    for alias in data["requiredAliases"]:
        assert alias in source, f"Required UK requirement alias missing: {alias}"
    for label, vehicle_types in data["requiredVehicleTypes"].items():
        for vehicle_type in vehicle_types:
            assert re.search(rf"types:\s*\[[^\]]*\b{vehicle_type}\b", source), f"{label}: vehicle type {vehicle_type} is absent"

    css = re.search(r"function missionRequirementsDocumentCss\(\) \{([\s\S]*?)\n    \}\n\n    function ensureMissionRequirementsDocumentStyle", source)
    assert css, "Mission requirements document CSS helper is missing"
    compact_css = re.sub(r"\s+", "", css.group(1)).lower()
    panel_rule = compact_css.split(".mcms-req-head", 1)[0]
    for forbidden in data["layout"]["forbiddenNormalPanelPositioning"]:
        assert forbidden not in panel_rule, f"normal requirements panel must not use {forbidden}"
    assert "position:relative!important" in panel_rule
    assert "clear:both!important" in panel_rule
    assert data["layout"]["mobileBreakpoint"].replace(" ", "") in compact_css
    assert "grid-template-columns:repeat(4,minmax(0,1fr))" in compact_css
    assert "table-layout:fixed!important" in compact_css
    assert "overflow-wrap:anywhere!important" in compact_css

    lssm = re.search(r"function missionRequirementsLssmActive\(candidate, source\) \{([\s\S]*?)\n    \}", source)
    assert lssm and ".alert-missing-vehicles" in lssm.group(1)
    assert "missionRequirementsRemoveRecord(source)" in source

    renderer = re.search(r"function missionRequirementsOverallState\(rows, unresolved\) \{([\s\S]*?)\n    \}", source)
    assert renderer
    assert "rows.some(row => !row.covered && row.selectedKnown)" in renderer.group(1)
    assert "rows.some(row => !row.selectedKnown) || unresolved.length" in renderer.group(1)

    print("Mission requirements contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
