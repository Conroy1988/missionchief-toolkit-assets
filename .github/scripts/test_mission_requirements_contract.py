#!/usr/bin/env python3
"""Verify the executable and structural live mission requirements contract."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/mission-requirements-contract.json"
RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CATALOGUE_FIXTURE = ROOT / ".github/fixtures/mission-catalogue-pages.json"
REPORT_FORM = ROOT / ".github/ISSUE_TEMPLATE/mission-info-missing.yml"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    catalogue_fixture = json.loads(CATALOGUE_FIXTURE.read_text(encoding="utf-8"))
    assert len(catalogue_fixture["pages"]) >= 3
    assert any(page.get("variations") for page in catalogue_fixture["pages"])
    assert any(page.get("conditional") for page in catalogue_fixture["pages"])

    runtime = subprocess.run(["node", str(RUNTIME_TEST)], cwd=ROOT, text=True, capture_output=True)
    if runtime.stdout:
        print(runtime.stdout, end="")
    if runtime.returncode != 0:
        if runtime.stderr:
            print(runtime.stderr, end="")
        raise SystemExit("Mission requirements runtime fixtures failed")

    required_markers = [
        "missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements'",
        "missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style'",
        "missionRequirements: true",
        "merged.missionRequirements = merged.missionRequirements !== false",
        "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([",
        "function missionRequirementsParseText(rawText, group = 'vehicles')",
        "function missionRequirementsCapacity(min = 0, max = min, known = null)",
        "function missionRequirementsCoverageRow(requirement, selectedCapacity, respondingCapacity, onSiteCapacity = null, requiredCapacity = null)",
        "function missionRequirementsDefinitionCondition(definition, candidate)",
        "function missionRequirementsResolve(candidate, parsed, catalogue = null)",
        "function missionRequirementsOverallState(rows, unresolved)",
        "function missionRequirementsLssmActive(candidate, source)",
        "function missionRequirementsCollectUnits(candidate, mode)",
        "function missionRequirementsPrimaryRuntime()",
        "function missionRequirementsMissionIdentity(candidate, source)",
        "function missionRequirementsAnchorForCandidate(candidate)",
        "function missionRequirementsFallbackHtml(kind)",
        "function missionRequirementsReportUrl(record, reason = 'unknown')",
        "function missionRequirementsCatalogueDescriptor(candidate)",
        "function missionRequirementsCatalogueParseDocument(doc, descriptor = {})",
        "function missionRequirementsCatalogueEnsure(record)",
        "function missionRequirementsCataloguePanelHtml(catalogue)",
        "function missionRequirementsCatalogueCompare(parsed, catalogue)",
        "Official MissionChief catalogue baseline only",
        "/einsaetze/",
        "Unable to pull mission requirements",
        "data-mcms-report-mission",
        "mission-info-missing.yml",
        "diagnostic",
        "issues/new",
        "function missionRequirementsEnsureRecord(candidate, source)",
        "data-mcms-requirements-panel",
        "function observeMissionRequirementsDocument(doc)",
        "function installMissionRequirementsWindows()",
        "runtimeOnCleanup(() => {",
        "source.parentNode?.insertBefore(p, source)",
        "missionRequirementsHideSource(source)",
        "missionRequirementsRestoreSource(record.source)",
        "#missing_text",
        "#mission_vehicle_driving",
        "#mission_vehicle_at_mission",
        "#vehicle_show_table_body_all",
        "#occupied",
        ".vehicle_checkbox",
        ".alert-missing-vehicles",
        "scheduleMissionRequirementsScan(35)",
        "installMissionRequirementsWindows();",
        "${makeToggleButton('missionRequirements'",
        "missionRequirements: state.missionRequirements",
        "Mission Requirements on",
        "if (state.missionRequirements) scheduleMissionRequirementsScan(0);",
        "const activeDocuments = new WeakSet();",
    ]
    compact_source = re.sub(r"\s+", "", source)
    missing = [marker for marker in required_markers if marker not in source and re.sub(r"\s+", "", marker) not in compact_source]
    assert not missing, f"Missing mission requirements contract markers: {missing}"

    report_form = REPORT_FORM.read_text(encoding="utf-8")
    assert "labels:\n  - Mission Info Missing" in report_form
    assert "id: diagnostic" in report_form
    assert "required: true" in report_form

    assert source.count("function installMissionRequirementsWindows()") == 1
    assert source.count("function scanMissionRequirementsWindows()") == 1
    assert compact_source.count("source.parentNode?.insertBefore(p,source)") == 1
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
    assert "grid-template-columns:repeat(5,minmax(0,1fr))" in compact_css
    assert "table-layout:fixed!important" in compact_css
    assert "overflow-wrap:anywhere!important" in compact_css

    lssm = re.search(r"function missionRequirementsLssmActive\(candidate, source\) \{([\s\S]*?)\n    \}", source)
    assert lssm and ".alert-missing-vehicles" in lssm.group(1)
    assert "table.table-striped.table-condensed" not in lssm.group(1)

    print("Mission requirements contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
