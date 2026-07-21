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
CUSTOM_VEHICLE_BADGES_CONTRACT = ROOT / ".github/scripts/test_custom_vehicle_badges_contract.py"
LSSM_COMPATIBILITY_AUDIT = ROOT / ".github/scripts/audit_lssm_requirement_compatibility.py"
CATALOGUE_FIXTURE = ROOT / ".github/fixtures/mission-catalogue-pages.json"
UK_CAPABILITY_FIXTURE = ROOT / "src/data/mission-requirements-en_GB.json"
CROSS_SOURCE_FIXTURE = ROOT / ".github/fixtures/mission-requirements-cross-source-en_GB.json"
REPORT_FORM = ROOT / ".github/ISSUE_TEMPLATE/mission-info-missing.yml"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    catalogue_fixture = json.loads(CATALOGUE_FIXTURE.read_text(encoding="utf-8"))
    uk_capabilities = json.loads(UK_CAPABILITY_FIXTURE.read_text(encoding="utf-8"))
    cross_source = json.loads(CROSS_SOURCE_FIXTURE.read_text(encoding="utf-8"))
    assert uk_capabilities["schemaVersion"] == 1
    assert uk_capabilities["locale"] == "en_GB"
    assert len(uk_capabilities["vehicleRequirements"]) >= 68
    assert len(uk_capabilities["staffRequirements"]) >= 2
    assert cross_source["schemaVersion"] == 1
    assert cross_source["locale"] == "en_GB"
    assert cross_source["pinnedLssmCommit"] == "4f731e1d6d009cbf2129530fb31d10177b21a52a"
    assert any(group["canonicalLabel"] == "Inland Rescue Boat (Trailer)" for group in cross_source["authoritativeLabels"])
    assert any(group["canonicalLabel"] == "Seagoing Vessel" for group in cross_source["authoritativeLabels"])
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

    custom_badges = subprocess.run(["python3", str(CUSTOM_VEHICLE_BADGES_CONTRACT)], cwd=ROOT, text=True, capture_output=True)
    if custom_badges.stdout:
        print(custom_badges.stdout, end="")
    if custom_badges.returncode != 0:
        if custom_badges.stderr:
            print(custom_badges.stderr, end="")
        raise SystemExit("Custom Vehicle Badges contract failed")

    lssm_audit = subprocess.run(["python3", str(LSSM_COMPATIBILITY_AUDIT), "--skip-runtime"], cwd=ROOT, text=True, capture_output=True)
    if lssm_audit.stdout:
        print(lssm_audit.stdout, end="")
    if lssm_audit.returncode != 0:
        if lssm_audit.stderr:
            print(lssm_audit.stderr, end="")
        raise SystemExit("LSSM compatibility audit failed")

    required_markers = [
        "missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements'",
        "missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style'",
        "missionRequirements: true",
        "merged.missionRequirements = merged.missionRequirements !== false",
        "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([",
        "const MISSION_REQUIREMENT_PARSE_DEFINITIONS = Object.freeze(",
        "function missionRequirementsParseText(rawText, group = 'vehicles')",
        "function missionRequirementsParseSource(source)",
        "function missionRequirementsPatientContext(candidate)",
        "function missionRequirementsPatientCount(candidate)",
        "function missionRequirementsPatientDetails(candidate)",
        "function missionRequirementsPatientState(record, now = Date.now())",
        "function missionRequirementsReconcilePatientDemand(parsed, patientState)",
        "function missionRequirementsReconcileCatalogue(parsed, catalogue, state = 'unavailable', expected = false)",
        "MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400",
        "function missionRequirementsCapacity(min = 0, max = min, known = null)",
        "function missionRequirementsCoverageRow(requirement, selectedCapacity, respondingCapacity, onSiteCapacity = null, requiredCapacity = null)",
        "function missionRequirementsDefinitionCondition(definition, candidate)",
        "function missionRequirementsResolve(candidate, parsed, catalogue = null)",
        "function missionRequirementsOverallState(rows, unresolved)",
        "function missionRequirementsLssmActive(candidate, source)",
        "function missionRequirementsCollectUnits(candidate, mode)",
        "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
        "definition.pair !== true && compatibleTractiveTypes.length > 0",
        "Inland Rescue Boat (Trailer)",
        "Seagoing Vessel",
        "missionRequirementsProgressValue(candidate, requirement.definition.bar, 'missing')",
        "function missionRequirementsOperationalSelectors(mode)",
        "function missionRequirementsOperationalWindowScopes(candidate, context = missionRequirementsPatientContext(candidate))",
        "function missionRequirementsOperationalCanonicalStateContainer(element, mode)",
        "const canonicalContainer = missionRequirementsOperationalCanonicalStateContainer(row, mode)",
        "mode !== 'selected' && !canonicalOwned && !isVisible(element)",
        "missionRequirementsOperationalElementActive(element, candidate, operationalContext, mode)",
        "tbody#mission_vehicle_driving > tr",
        "function missionRequirementsMetadataValues(element, kind = 'labels')",
        "function missionRequirementsArrCapabilityState(element, candidate = null, vehicleId = -1)",
        "function missionRequirementsVehicleApiRecord(vehicleId)",
        "function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element, mode = '')",
        "function missionRequirementsLinkedTrainingValues(candidate, vehicleId, element)",
        "function missionRequirementsRespondingCrewCapacity(element)",
        "personalVehicleApiCache",
        "refreshPersonalVehicleData",
        "assigned_personnel_count",
        "data-personnel-training",
        "data-education-key",
        "data-filterable-by",
        "td:nth-of-type(5)[sortvalue]",
        "function missionRequirementsCataloguePersonnelRequirements(label, value, kind = null)",
        "function missionRequirementsCatalogueModifier(label, value = '', resolveCapability = true)",
        "function missionRequirementsStripNonDemandMetadata(rawText, resolveCapability = false)",
        "additive_overlays",
        "function missionRequirementsPrimaryRuntime()",
        "function missionRequirementsMissionIdentity(candidate, source)",
        "function missionRequirementsSourceForCandidate(candidate)",
        "function missionRequirementsPlacement(candidate, source = null)",
        "function missionRequirementsPlacementHostUnsafe(node, boundary = null)",
        "function missionRequirementsPlacementBlock(root, node)",
        "function missionRequirementsPlacePanel(candidate, source, panel)",
        "function missionRequirementsWidthMode(rows = [], unresolved = [])",
        "function missionRequirementsAnchorForCandidate(candidate)",
        "function missionRequirementsFallbackHtml(kind)",
        "function missionRequirementsReportUrl(record, reason = 'unknown')",
        "function missionRequirementsCatalogueDescriptor(candidate)",
        "function missionRequirementsCatalogueParseDocument(doc, descriptor = {})",
        "function missionRequirementsCatalogueEnsure(record)",
        "Loading Requirements for this Mission",
        "Mission info",
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
        "missionRequirementsPlacePanel(scopedCandidate, source, panel)",
        "missionRequirementsHideSource(source)",
        "missionRequirementsRestoreSource(record.source)",
        "#missing_text",
        "#patient_button_form",
        "#patient_button_text",
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
    assert compact_source.count("missionRequirementsPlacePanel(scopedCandidate,source,panel)") == 2
    assert source.count("missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements'") == 1
    assert "return { root, parent: operational.parentNode, before: operational };" not in source
    assert "v4.lss-manager.de" not in source
    assert "const rowText = missionRequirementsCapabilityLabel" not in source, "whole-row captions must not prove personnel training"
    assert "<small class=\"mcms-req-source\">" not in source, "Matrix provenance badges must be structurally absent"
    assert "class=\"mcms-matrix-requirement-name\"" in source, "Matrix requirement label needs a clean parser-facing element"
    assert "data-requirement-source=\"${escapeHtml(sourceKey)}\"" in source, "Matrix provenance must remain outside label text"
    assert "classification: 'spawn-prerequisite'" in source, "Mission Info spawn prerequisites need typed exclusion"
    assert "item?.classification === 'operational'" in source, "operational catalogue unresolved text must be prefix-free"
    assert '"key":"public-order-level-2"' in source and '"level_2_public_order"' in source, "Level 2 Public Order needs native training evidence"
    assert '"key":"police-sergeant-personnel"' in source and '"police_sergeant"' in source, "Police Sergeant needs native training evidence"
    assert '"key":"search-advisor-personnel"' in source and '"search_and_rescue"' in source and '"countable":true' in source, "Search Advisor needs ARR capability evidence"
    assert '"key":"sar-commander-personnel"' in source and '"search_and_rescue_command"' in source, "SAR Commander needs ARR capability evidence"
    assert "assigned_personnel_count" in source and "missionRequirementsVehicleApiStaff" in source, "exact vehicle personnel API evidence is required"
    assert "personalVehicleApiCache" in source and "refreshPersonalVehicleData(false)" in source, "Matrix must reuse the shared vehicle API cache"
    assert "LSS-Manager" not in source
    aliases_seen = set()
    for group_name in ("vehicleRequirements", "staffRequirements"):
        for entry in uk_capabilities[group_name]:
            assert entry["aliases"] and (entry["types"] or entry.get("training"))
            for training in entry.get("training", []):
                assert isinstance(training, str) and training.strip()
            for alias in entry["aliases"]:
                folded = re.sub(r"\s+", " ", alias).strip().casefold()
                assert folded not in aliases_seen, f"duplicate UK capability alias: {alias}"
                aliases_seen.add(folded)
                assert alias in source, f"UK capability alias missing from source: {alias}"
            for vehicle_type in entry["types"]:
                assert isinstance(vehicle_type, int) and vehicle_type >= 0
    assert "missionRequirementsPlacementBlock(root, operational)" not in source
    assert "const operational = root.querySelector?." not in source
    assert source.count("function missionRequirementsPatientContext(candidate)") == 1
    assert "const visibleRows = rows.filter(row => !row.covered);" in source, "fulfilled Matrix rows must be presentation-filtered"
    assert "All currently known requirements are covered." in source, "all-covered Matrix state must remain explicit"
    assert "missionRequirementsWidthMode(visibleRows, unresolved)" in source, "fulfilled rows must not inflate rendered width"
    assert source.count("function missionRequirementsPatientCount(candidate)") == 1
    assert source.count("function missionRequirementsPatientDetails(candidate)") == 1
    assert source.count("function missionRequirementsReconcilePatientDemand(parsed, patientState)") == 1
    assert "patientConditionFulfilledKnown" in source
    assert "critical-care-patient" in source
    assert "patient-transport" in source
    assert source.count("function missionRequirementsReconcileCatalogue(parsed, catalogue, state = 'unavailable', expected = false)") == 1
    assert "return parsed.requirements.map(requirement =>" in source, "resolver must retain one pass over the reconciled union"
    assert "catalogueOnly && catalogueProbability < 100" in source, "probabilistic authoritative requirements must remain uncertain"
    assert "if (conditional && index === undefined) continue" in source, "catalogue-only conditional demand must remain dormant"
    assert "classification: 'probability'" in source and "classification: 'availability'" in source, "probability and availability metadata need typed separation"
    assert "missionRequirementsStripNonDemandMetadata(rawText, false)" in source, "live parser must classify metadata before requirement matching"
    assert re.search(r"(?:key|['\"]key['\"])\s*:\s*['\"]railway-police-officer['\"][^\n]*(?:training|['\"]training['\"])\s*:\s*\[[^\]]*Railway Police", source), "Railway Police personnel must require explicit training evidence"
    assert '"key":"railway-police-officer"' in source and '"railway_police"' in source, "Railway Police must use the native education key"
    assert '"requireExplicitTraining":true' in source, "Railway Police carrier type must not prove specialist qualification"
    assert "if ((definition?.group || 'vehicles') === 'staff') continue" in source, "vehicle labels must not prove specialist personnel roles"
    assert "missionRequirementsLinkedTrainingValues(candidate, vehicleId, vehicleElement)" in source, "responding units must resolve linked specialist metadata"
    assert "missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement, mode)" in source, "responding mode must reach the crew resolver"
    assert "missionRequirementsOperationalCrewCapacity(element, mode)" in source, "canonical responding and on-site crew must be acquired explicitly"
    assert "td:nth-of-type(5)[sortvalue]" in source, "canonical operational crew must use the fifth-cell sortvalue"
    assert '"key":"police-inspector-personnel"' in source and '"police_inspector"' in source, "Police Inspector must be a countable explicit qualification"
    assert "missionRequirementsQualifiedStaffCounts(candidate, vehicleId, vehicleElement, arrCapabilityState)" in source, "specialist personnel must use qualification-specific counts"
    assert r"Required\s+minimum" in source and "missionRequirementsRangeMetadataKey" in source, "range-only mission metadata must be suppressible beside exact demand"
    assert 'Breathing Apparatus Support Unit (BASU)' in source and 'BASU Pod and OSU Pod' in source, "BASU must expose its canonical label and eligible vehicle detail"
    assert "!reconciled.requirements.length && !reconciled.unresolved.length" in source, "unresolved authority must not collapse to an empty success state"
    assert "#mission_vehicle_driving > tr" in source and "tbody#mission_vehicle_driving > tr" in source
    assert "#vehicle_show_table_body_all, #occupied, .vehicle_checkbox" in source, "selected-unit scope must locate the Available Units container"
    assert "missionRequirementsOperationalWindowScopes(candidate, context)" in source, "selected-unit acquisition must expand beyond the narrow mission root"
    assert "missionRequirementsOperationalCanonicalStateContainer" in source, "canonical operational tables must bypass collapse-only visibility"
    assert "documentCanonical === canonicalContainer || documentCanonical.contains?.(row)" in source, "standalone canonical-table ownership must be proven"
    assert "setInterval(" not in re.search(r"// Issue #181: patient-derived ambulance demand\.([\s\S]*?)function missionRequirementsVehicleType", source).group(1)
    assert re.search(r"(?:key|['\"]key['\"])\s*:\s*['\"]ambulance['\"][^\n]*(?:types|['\"]types['\"])\s*:\s*\[5,\s*9\]", source), "Ambulance capability must include road Ambulance and HEMS vehicle types"
    assert re.search(r"(?:key|['\"]key['\"])\s*:\s*['\"]hems['\"][^\n]*(?:types|['\"]types['\"])\s*:\s*\[9\]", source), "HEMS must retain its dedicated capability mapping"

    for alias in data["requiredAliases"]:
        assert alias in source, f"Required UK requirement alias missing: {alias}"
    for label, vehicle_types in data["requiredVehicleTypes"].items():
        for vehicle_type in vehicle_types:
            assert re.search(rf"(?:types|['\"]types['\"])\s*:\s*\[[^\]]*\b{vehicle_type}\b", source), f"{label}: vehicle type {vehicle_type} is absent"

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
    assert f"width:min(100%,{data['layout']['standardDesktopWidth']})!important" in compact_css
    assert f'data-width-mode="wide"]{{width:min(100%,{data["layout"]["wideDesktopWidth"]})!important' in compact_css
    assert 'data-width-mode="fluid"]{width:100%!important' in compact_css

    lssm = re.search(r"function missionRequirementsLssmActive\(candidate, source\) \{([\s\S]*?)\n    \}", source)
    assert lssm and ".alert-missing-vehicles" in lssm.group(1)
    assert "table.table-striped.table-condensed" not in lssm.group(1)

    print("Mission requirements contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
