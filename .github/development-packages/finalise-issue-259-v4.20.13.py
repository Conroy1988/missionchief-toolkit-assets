#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CONTRACT_TEST = ROOT / ".github/scripts/test_mission_requirements_contract.py"
TOOLKIT_DATA = ROOT / "src/data/mission-requirements-en_GB.json"
BASELINE = ROOT / ".github/fixtures/lssm-v4-en_GB-emv-baseline.json"
AUDIT = ROOT / ".github/scripts/audit_lssm_requirement_compatibility.py"
REPORT = ROOT / "docs/issue-259-lssm-parity-audit.md"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
DIST_JS = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
SUMS = ROOT / "dist/SHA256SUMS.txt"
MANIFEST = ROOT / "dist/release-manifest.json"

PIN = "4f731e1d6d009cbf2129530fb31d10177b21a52a"
RAW = "https://raw.githubusercontent.com/LSS-Manager/LSSM-V.4/" + PIN + "/"
UPSTREAM_FILES = {
    "catalogue": "src/modules/extendedCallWindow/i18n/en_GB.json",
    "requirements": "src/modules/extendedCallWindow/assets/emv/getMissingRequirements.ts",
    "selection": "src/modules/extendedCallWindow/assets/emv/getVehicleListObserveHandler.ts",
    "vehicles": "src/i18n/en_GB/vehicles.ts",
}


def fetch_text(path: str) -> str:
    with urllib.request.urlopen(RAW + path, timeout=30) as response:
        return response.read().decode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def vehicle_blocks(source: str) -> dict[int, str]:
    matches = list(re.finditer(r"(?m)^\s{4}(\d+):\s*\{", source))
    result: dict[int, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        result[int(match.group(1))] = source[match.start():end]
    return result


def tractive_map(vehicle_source: str) -> dict[int, list[int]]:
    result: dict[int, list[int]] = {}
    for type_id, block in vehicle_blocks(vehicle_source).items():
        match = re.search(r"tractiveVehicles\s*:\s*\[([^\]]*)\]", block, re.S)
        if not match:
            continue
        values = [int(value) for value in re.findall(r"\d+", match.group(1))]
        if values:
            result[type_id] = values
    return result


def normalise_group(entries: list[dict]) -> list[dict]:
    result = []
    for entry in entries:
        result.append({
            "texts": list(entry.get("texts", [])),
            "vehicles": [int(value) for value in entry.get("vehicles", [])],
            "equipment": list(entry.get("equipment", [])),
            "conditionalVehicles": entry.get("conditionalVehicles", {}),
            "factors": entry.get("factors", {}),
        })
    return result


def write_upstream_baseline() -> dict:
    fetched = {name: fetch_text(path) for name, path in UPSTREAM_FILES.items()}
    catalogue = json.loads(fetched["catalogue"])["enhancedMissingVehicles"]
    snapshot = {
        "schemaVersion": 1,
        "locale": "en_GB",
        "pinnedCommit": PIN,
        "files": {
            name: {
                "path": UPSTREAM_FILES[name],
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
            for name, content in fetched.items()
        },
        "vehicleRequirements": normalise_group(catalogue.get("vehiclesByRequirement", [])),
        "staffRequirements": normalise_group(catalogue.get("staff", [])),
        "tractiveVehicles": {str(key): value for key, value in sorted(tractive_map(fetched["vehicles"]).items())},
        "contracts": {
            "requirementSelectors": ["[data-requirement-type=\"vehicles\"]", "[data-requirement-type=\"personnel\"]", "[data-requirement-type=\"other\"]"],
            "selectedRoots": ["vehicle_show_table_body_all", "occupied"],
            "respondingRoot": "#mission_vehicle_driving tbody tr",
            "selectedAttributes": ["vehicle_type_id", "value", "data-equipment-types", "tractive_vehicle_id", "tractive_random"],
            "nestedEquipment": "[data-equipment-type]",
            "resourceMetrics": ["driving", "missing", "selected"],
        },
    }
    if not snapshot["vehicleRequirements"] or not snapshot["tractiveVehicles"]:
        raise RuntimeError("Pinned LSSM snapshot is incomplete")
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return snapshot


def write_audit_script() -> None:
    AUDIT.write_text(r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".github/fixtures/lssm-v4-en_GB-emv-baseline.json"
TOOLKIT = ROOT / "src/data/mission-requirements-en_GB.json"
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"


def fold(value: str) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().casefold()


def normalise_group(entries: list[dict]) -> list[dict]:
    return [{
        "texts": list(entry.get("texts", [])),
        "vehicles": [int(value) for value in entry.get("vehicles", [])],
        "equipment": list(entry.get("equipment", [])),
        "conditionalVehicles": entry.get("conditionalVehicles", {}),
        "factors": entry.get("factors", {}),
    } for entry in entries]


def compare_toolkit(snapshot: dict) -> list[str]:
    toolkit = json.loads(TOOLKIT.read_text(encoding="utf-8"))
    errors: list[str] = []
    for upstream_name, toolkit_name in (("vehicleRequirements", "vehicleRequirements"), ("staffRequirements", "staffRequirements")):
        toolkit_entries = toolkit.get(toolkit_name, [])
        by_alias = {}
        for entry in toolkit_entries:
            for alias in entry.get("aliases", []):
                by_alias[fold(alias)] = entry
        for upstream in snapshot.get(upstream_name, []):
            for text in upstream.get("texts", []):
                match = by_alias.get(fold(text))
                if not match:
                    errors.append(f"missing Toolkit alias: {text}")
                    continue
                missing_types = sorted(set(upstream.get("vehicles", [])) - set(match.get("types", [])))
                missing_equipment = sorted(set(upstream.get("equipment", [])) - set(match.get("equipment", [])))
                if missing_types:
                    errors.append(f"{text}: missing vehicle types {missing_types}")
                if missing_equipment:
                    errors.append(f"{text}: missing equipment {missing_equipment}")
    source = SOURCE.read_text(encoding="utf-8")
    required = [
        "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
        "missionRequirementsProgressValue(candidate, requirement.definition.bar, 'missing')",
        "[data-equipment-type], [data-equipment-types]",
        "tractive_random",
        "data-min-personnel",
        "data-max-personnel",
    ]
    for marker in required:
        if marker not in source:
            errors.append(f"missing runtime contract marker: {marker}")
    if "const rowText = missionRequirementsCapabilityLabel" in source:
        errors.append("whole-row text is still accepted as personnel-training proof")
    if "v4.lss-manager.de" in source or "max_personnel_override" in source:
        errors.append("Toolkit source contains an LSSM runtime dependency")
    return errors


def compare_upstream(snapshot: dict, upstream_root: Path) -> list[str]:
    catalogue_path = upstream_root / snapshot["files"]["catalogue"]["path"]
    if not catalogue_path.exists():
        return [f"upstream catalogue not found: {catalogue_path}"]
    current = json.loads(catalogue_path.read_text(encoding="utf-8"))["enhancedMissingVehicles"]
    errors = []
    for key, current_entries in (("vehicleRequirements", current.get("vehiclesByRequirement", [])), ("staffRequirements", current.get("staff", []))):
        expected = snapshot.get(key, [])
        actual = normalise_group(current_entries)
        if actual != expected:
            expected_aliases = {fold(text) for entry in expected for text in entry.get("texts", [])}
            actual_aliases = {fold(text) for entry in actual for text in entry.get("texts", [])}
            added = sorted(actual_aliases - expected_aliases)
            removed = sorted(expected_aliases - actual_aliases)
            errors.append(f"{key} drift: added={added}, removed={removed}; inspect types/equipment/factors/conditions")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path)
    args = parser.parse_args()
    snapshot = json.loads(BASELINE.read_text(encoding="utf-8"))
    errors = compare_toolkit(snapshot)
    if args.upstream_root:
        errors.extend(compare_upstream(snapshot, args.upstream_root))
    if errors:
        print("LSSM compatibility audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"LSSM compatibility audit passed against {snapshot['pinnedCommit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")


def update_source(snapshot: dict) -> None:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, "// @version      4.20.12", "// @version      4.20.13", "metadata version")
    source = replace_once(source, "version: '4.20.12'", "version: '4.20.13'", "runtime version")

    tractive_json = json.dumps(snapshot["tractiveVehicles"], separators=(",", ":"))
    marker = "function missionRequirementsCollectUnits(candidate, mode)"
    source = replace_once(source, marker, f"const MISSION_REQUIREMENTS_TRACTIVE_TYPES = Object.freeze({tractive_json});\n{marker}", "tractive map insertion")

    collect_start = source.index(marker)
    collect_end = source.index("function missionRequirementsMissionTypeId", collect_start)
    collect = source[collect_start:collect_end]
    pair_pattern = re.compile(r"(const tractiveId = .*?; const trailerId = .*?;)( let contributionKey)")
    match = pair_pattern.search(collect)
    if not match:
        raise RuntimeError("collectUnits tractive anchor missing")
    extra = " const tractiveRandom = String(vehicleElement?.getAttribute?.('tractive_random') ?? vehicleElement?.getAttribute?.('data-tractive-random') ?? row?.getAttribute?.('tractive_random') ?? row?.getAttribute?.('data-tractive-random') ?? row?.dataset?.tractiveRandom ?? '') === '1'; const explicitTractiveType = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('tractive_vehicle_type_id') ?? vehicleElement?.getAttribute?.('data-tractive-vehicle-type-id') ?? row?.getAttribute?.('tractive_vehicle_type_id') ?? row?.getAttribute?.('data-tractive-vehicle-type-id') ?? row?.dataset?.tractiveVehicleTypeId); const compatibleTractiveTypes = explicitTractiveType !== null ? [explicitTractiveType] : (tractiveRandom ? Array.from(MISSION_REQUIREMENTS_TRACTIVE_TYPES[typeId] || MISSION_REQUIREMENTS_TRACTIVE_TYPES[String(typeId)] || []) : []);"
    collect = collect[:match.start()] + match.group(1) + extra + match.group(2) + collect[match.end():]
    collect = replace_once(collect, "const rowText = missionRequirementsCapabilityLabel(`${row?.textContent || ''} ${row?.innerText || ''}`); if (rowText) { for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { const aliases = Array.from(definition?.training || []).map(missionRequirementsCapabilityLabel).filter(Boolean); if (!aliases.some(alias => rowText.includes(alias))) continue; aliases.forEach(alias => training.add(alias)); knownDefinitionKeys.add(definition.key); } } ", "", "remove whole-row training inference")
    collect = replace_once(collect, "const unit = { typeId, vehicleId, tractiveId, equipment:", "const unit = { typeId, vehicleId, tractiveId, tractiveRandom, compatibleTractiveTypes: new Set(compatibleTractiveTypes), equipment:", "unit tractive metadata")
    collect = replace_once(collect, "for (const equipment of unit.equipment) existing.equipment.add(equipment);", "for (const equipment of unit.equipment) existing.equipment.add(equipment); for (const tractiveType of unit.compatibleTractiveTypes) existing.compatibleTractiveTypes.add(tractiveType);", "merge tractive metadata")
    source = source[:collect_start] + collect + source[collect_end:]

    contribution_start = source.index("function missionRequirementsUnitContribution")
    contribution_end = source.index("function missionRequirementsAggregate", contribution_start)
    new_contribution = "function missionRequirementsUnitContribution(requirement, unit) { const definition = requirement.definition || {}; const definitionTypes = Array.from(definition.types || []); const typeEligible = definitionTypes.includes(unit.typeId); const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase())); const labelEligible = unit.knownDefinitionKeys?.has?.(definition.key) || missionRequirementsDefinitionMatchesValues(definition, unit.labels); const compatibleTractiveTypes = Array.from(unit.compatibleTractiveTypes || []).map(Number).filter(Number.isFinite); const tractiveEligible = compatibleTractiveTypes.length > 0 && compatibleTractiveTypes.every(type => definitionTypes.includes(type)); const trainingRequired = Array.from(definition.training || []).length > 0; const trainingEligible = trainingRequired && missionRequirementsDefinitionMatchesValues(definition, unit.training, 'training'); const eligible = requirement.group === 'staff' && trainingRequired ? trainingEligible : typeEligible || equipmentEligible || labelEligible || tractiveEligible; const classificationUnknown = requirement.group === 'staff' && trainingRequired ? Boolean(unit.staff && !unit.training?.size) : unit.typeId < 0 && !unit.knownDefinitionKeys?.size && !unit.equipment?.size && !compatibleTractiveTypes.length; if (!eligible) return { eligible: false, unknown: classificationUnknown, capacity: missionRequirementsCapacity(0, classificationUnknown ? null : 0, !classificationUnknown) }; if (requirement.group === 'staff') { const capacity = unit.staff ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known) : missionRequirementsCapacity(0, null, false); return { eligible: true, unknown: !capacity.known, capacity }; } const factor = tractiveEligible && !typeEligible ? 1 : Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1); const value = Number.isFinite(factor) && factor > 0 ? factor : 1; return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) }; }\n\n"
    source = source[:contribution_start] + new_contribution + source[contribution_end:]

    resolve_start = source.index("function missionRequirementsResolve")
    resolve_end = source.index("function missionRequirementsOverallState", resolve_start)
    resolve = source[resolve_start:resolve_end]
    resolve = replace_once(resolve, "return parsed.requirements.map(requirement => {", "return parsed.requirements.map(requirement => { let effectiveMissing = Math.max(0, Number(requirement.missing) || 0);", "effective missing")
    bar_pattern = re.compile(r"if \(requirement\.definition\?\.bar\) \{.*?\} else \{ selected = missionRequirementsAggregate\(requirement, buckets\.selected\); responding = missionRequirementsAggregate\(requirement, buckets\.responding\); onSite = missionRequirementsAggregate\(requirement, buckets\.onSite\); \}")
    match = bar_pattern.search(resolve)
    if not match:
        raise RuntimeError("resource bar resolver block missing")
    replacement = "if (requirement.definition?.bar) { const selectedValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'selected'); const respondingValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'driving'); const missingValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'missing'); const onSiteMetrics = ['at_mission', 'on_site', 'onsite', 'arrived', 'actual']; const onSiteValue = onSiteMetrics.map(metric => missionRequirementsProgressValue(candidate, requirement.definition.bar, metric)).find(value => value !== null); if (selectedValue === null || respondingValue === null || missingValue === null) { const unknown = missionRequirementsCapacity(0, null, false); const row = missionRequirementsCoverageRow(requirement, unknown, unknown, unknown, unknown); row.covered = false; row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; return { ...row, conditionKnown: true, conditionMatched: true, requirementAuthority: 'mission-progress' }; } effectiveMissing = Math.max(0, missingValue + respondingValue); selected = missionRequirementsCapacity(selectedValue, selectedValue, true); responding = missionRequirementsCapacity(respondingValue, respondingValue, true); onSite = onSiteValue === undefined ? missionRequirementsCapacity(0, 0, true) : missionRequirementsCapacity(onSiteValue, onSiteValue, true); } else { selected = missionRequirementsAggregate(requirement, buckets.selected); responding = missionRequirementsAggregate(requirement, buckets.responding); onSite = missionRequirementsAggregate(requirement, buckets.onSite); }"
    resolve = resolve[:match.start()] + replacement + resolve[match.end():]
    resolve = replace_once(resolve, "baseline - Math.max(0, Number(requirement.missing) || 0)", "baseline - effectiveMissing", "committed resource demand")
    resolve = replace_once(resolve, "Math.max(0, Number(requirement.missing) || 0) + onSite.min", "effectiveMissing + onSite.min", "required minimum")
    resolve = replace_once(resolve, "Math.max(0, Number(requirement.missing) || 0) + onSite.max", "effectiveMissing + onSite.max", "required maximum")
    source = source[:resolve_start] + resolve + source[resolve_end:]
    SOURCE.write_text(source, encoding="utf-8")


def update_runtime_tests(snapshot: dict) -> None:
    test = RUNTIME_TEST.read_text(encoding="utf-8")
    test = replace_once(test, "equipmentTypes: missionRequirementsEquipmentTypes,", "equipmentTypes: missionRequirementsEquipmentTypes,\n    progressValue: missionRequirementsProgressValue,", "progress API export")
    trailer_type, tractive_types = next((int(key), values) for key, values in snapshot["tractiveVehicles"].items() if values)
    partial_types = tractive_types[:1]
    block = f'''

// Issue #259: pinned LSSM parity for resources, equipment, tractive units and training evidence.
{{
const resourceDoc = new FakeDocument();
resourceDoc.defaultView = {{ MutationObserver: FakeMutationObserver, location: {{ pathname: '/missions/25901' }} }};
const resourceCandidate = makeMissionCandidate(resourceDoc, '2,000 litres of water');
resourceCandidate.missionId = 25901;
const holder = new FakeElement('div', resourceDoc);
const metricNodes = {{ selected: new FakeElement('span', resourceDoc), driving: new FakeElement('span', resourceDoc), missing: new FakeElement('span', resourceDoc) }};
metricNodes.selected.textContent = metricNodes.selected.innerText = '250';
metricNodes.driving.textContent = metricNodes.driving.innerText = '500';
metricNodes.missing.textContent = metricNodes.missing.innerText = '2,000';
holder.queryHandler = selector => Object.entries(metricNodes).find(([metric, node]) => node && selector.includes(`_${{metric}}_`))?.[1] || null;
const originalResourceQuery = resourceCandidate.root.queryHandler;
resourceCandidate.root.queryHandler = selector => selector.includes('[id^="mission_water_holder"]') ? holder : originalResourceQuery(selector);
const resourceParsed = api.parseText('2,000 litres of water', 'other');
let resourceRow = api.resolve(resourceCandidate, resourceParsed)[0];
assert.strictEqual(resourceRow.requiredText, '2,500', 'resource required total reconstructs missing plus driving');
assert.strictEqual(resourceRow.respondingText, '500', 'resource driving progress is Responding');
assert.strictEqual(resourceRow.selectedText, '250', 'resource selected progress is Selected');
assert.strictEqual(resourceRow.onSiteText, '0', 'resource bar remains exact without a separate on-site metric');
assert.strictEqual(resourceRow.stillNeededText, '1,750', 'resource missing value is not double-subtracted');
assert.strictEqual(api.progressValue(resourceCandidate, 'foam', 'selected'), 250, 'generic foam progress selector accepts MissionChief water-bar class contract');
assert.strictEqual(api.progressValue(resourceCandidate, 'pump', 'driving'), 500, 'generic pump progress selector accepts MissionChief water-bar class contract');
metricNodes.missing = null;
resourceRow = api.resolve(resourceCandidate, resourceParsed)[0];
assert.strictEqual(resourceRow.stillNeededText, '?', 'malformed resource holder fails closed');
assert.strictEqual(resourceRow.covered, false, 'malformed resource holder cannot become covered');

const equipmentDoc = new FakeDocument();
equipmentDoc.defaultView = {{ MutationObserver: FakeMutationObserver, location: {{ pathname: '/missions/25902' }} }};
const equipmentCandidate = makeMissionCandidate(equipmentDoc, '1 Drone');
equipmentCandidate.missionId = 25902;
const droneDefinition = api.definitions.find(item => item.key === 'drone');
const droneParsed = {{ requirements: [{{ key: 'drone', requirement: 'Drone', missing: 1, group: 'vehicles', definition: droneDefinition }}], unresolved: [] }};
const nestedUnit = makeVehicleElement(equipmentDoc, 2590201, -1);
const nestedMarker = new FakeElement('span', equipmentDoc);
nestedMarker.setAttribute('data-equipment-type', 'drone');
const originalNestedQueryAll = nestedUnit.row.queryAllHandler;
nestedUnit.row.queryAllHandler = selector => selector.includes('[data-equipment-type]') ? [nestedMarker] : originalNestedQueryAll(selector);
equipmentCandidate.root.selectedUnits = [nestedUnit.vehicle];
let nestedRow = api.resolve(equipmentCandidate, droneParsed)[0];
assert.strictEqual(nestedRow.selectedMin, 1, 'nested equipment marker counts in Selected');
equipmentCandidate.root.selectedUnits = [];
nestedUnit.row.matchSet.add('tr');
nestedUnit.row.setAttribute('data-vehicle-id', '2590201');
equipmentCandidate.root.enRouteRows = [nestedUnit.row];
nestedRow = api.resolve(equipmentCandidate, droneParsed)[0];
assert.strictEqual(nestedRow.respondingMin, 1, 'nested equipment marker counts in Responding');
equipmentCandidate.root.enRouteRows = [];
equipmentCandidate.root.onSiteRows = [nestedUnit.row];
nestedRow = api.resolve(equipmentCandidate, droneParsed)[0];
assert.strictEqual(nestedRow.onSiteMin, 1, 'nested equipment marker counts On site');
const dualNestedUnit = makeVehicleElement(equipmentDoc, 2590291, 91);
const dualMarker = new FakeElement('span', equipmentDoc);
dualMarker.setAttribute('data-equipment-type', 'drone');
dualNestedUnit.row.queryAllHandler = selector => selector.includes('[data-equipment-type]') ? [dualMarker] : [];
equipmentCandidate.root.onSiteRows = [];
equipmentCandidate.root.selectedUnits = [dualNestedUnit.vehicle];
nestedRow = api.resolve(equipmentCandidate, droneParsed)[0];
assert.strictEqual(nestedRow.selectedMin, 1, 'type and nested equipment evidence from one unit count once');

const guaranteedTractive = api.aggregate(
    {{ group: 'vehicles', definition: {{ types: {json.dumps(tractive_types)}, equipment: [], factors: {{}} }} }},
    [{{ typeId: {trailer_type}, compatibleTractiveTypes: new Set({json.dumps(tractive_types)}), equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), staff: null, contributionKey: 'vehicle:random-tractive' }}]
);
assert.strictEqual(guaranteedTractive.min, 1, 'random trailer contributes when every compatible tractive type satisfies the requirement');
const partialTractive = api.aggregate(
    {{ group: 'vehicles', definition: {{ types: {json.dumps(partial_types)}, equipment: [], factors: {{}} }} }},
    [{{ typeId: {trailer_type}, compatibleTractiveTypes: new Set({json.dumps(tractive_types)}), equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), staff: null, contributionKey: 'vehicle:random-tractive-partial' }}]
);
assert.strictEqual(partialTractive.min, {1 if len(tractive_types) == 1 else 0}, 'random trailer never guesses a capability not shared by every compatible tractive type');

const unqualifiedRow = new FakeElement('tr', equipmentDoc);
unqualifiedRow.textContent = unqualifiedRow.innerText = 'Railway Police Officer';
unqualifiedRow.setAttribute('data-current-personnel', '4');
const unqualifiedElement = new FakeElement('input', equipmentDoc);
unqualifiedElement.closestMap.set('tr', unqualifiedRow);
const unqualifiedTraining = api.metadataValues(unqualifiedElement, 'training');
assert.strictEqual(unqualifiedTraining.size, 0, 'whole-row caption text is not semantic training evidence');
const explicitTraining = new FakeElement('input', equipmentDoc);
explicitTraining.setAttribute('data-personnel-training', 'Railway Police Officer');
assert(api.metadataValues(explicitTraining, 'training').has('railway police officer'), 'explicit native personnel training remains recognised');
}}
'''
    test = replace_once(test, "\n// Issue #257: official combined Mission Info labels use capability unions.", block + "\n// Issue #257: official combined Mission Info labels use capability unions.", "Issue 259 runtime fixtures")
    RUNTIME_TEST.write_text(test, encoding="utf-8")


def update_contract_test() -> None:
    text = CONTRACT_TEST.read_text(encoding="utf-8")
    text = replace_once(text, "CUSTOM_VEHICLE_BADGES_CONTRACT = ROOT / \".github/scripts/test_custom_vehicle_badges_contract.py\"", "CUSTOM_VEHICLE_BADGES_CONTRACT = ROOT / \".github/scripts/test_custom_vehicle_badges_contract.py\"\nLSSM_COMPATIBILITY_AUDIT = ROOT / \".github/scripts/audit_lssm_requirement_compatibility.py\"", "audit script constant")
    anchor = "    required_markers = ["
    audit_run = '''    lssm_audit = subprocess.run(["python3", str(LSSM_COMPATIBILITY_AUDIT)], cwd=ROOT, text=True, capture_output=True)
    if lssm_audit.stdout:
        print(lssm_audit.stdout, end="")
    if lssm_audit.returncode != 0:
        if lssm_audit.stderr:
            print(lssm_audit.stderr, end="")
        raise SystemExit("LSSM compatibility audit failed")

'''
    text = replace_once(text, anchor, audit_run + anchor, "audit execution")
    text = replace_once(text, '        "function missionRequirementsCollectUnits(candidate, mode)",', '        "function missionRequirementsCollectUnits(candidate, mode)",\n        "MISSION_REQUIREMENTS_TRACTIVE_TYPES",\n        "missionRequirementsProgressValue(candidate, requirement.definition.bar, \'missing\')",', "contract markers")
    text = replace_once(text, '    assert "v4.lss-manager.de" not in source\n', '    assert "v4.lss-manager.de" not in source\n    assert "const rowText = missionRequirementsCapabilityLabel" not in source, "whole-row captions must not prove personnel training"\n', "training contract")
    CONTRACT_TEST.write_text(text, encoding="utf-8")


def write_report(snapshot: dict) -> None:
    REPORT.write_text(f'''# Issue #259 — LSSM Mission Requirements parity audit

## Audited baselines

- Toolkit: `8619c79b794ad7241e0a37a0c91a6176daee7911` — v4.20.12.
- LSSM V.4: `{PIN}` — 4.7.12+20260720.0722.

## Result

The Toolkit already matched or exceeded LSSM for requirement parsing, reverse vehicle/equipment capability maps, normal and occupied selected lists, responding and on-site acquisition, factors, conditional requirements, bounded personnel, explicit trailer pairing, de-duplication, patient demand and fail-closed unknown states.

The audit found one incomplete integration and two hardening opportunities.

### Corrected in v4.20.13

1. **Resource progress bars:** water, foam and pumping already had definitions, selectors and observers, but the resolver ignored MissionChief's authoritative `missing` progress value. Required capacity is now reconstructed as `missing + driving + optional on-site`, so driving and selected values are subtracted exactly once.
2. **Random tractive vehicles:** LSSM's reviewed UK `tractiveVehicles` metadata is compiled into a local static map. A trailer contributes an implicit tractive capability only when every compatible tractive type satisfies that requirement.
3. **Personnel reliability:** whole-row visible text is no longer accepted as proof of specialist training. Explicit MissionChief training attributes remain supported; absent evidence remains bounded or unknown.

### Already implemented and now fixture-locked

- nested `data-equipment-type` and `data-equipment-types` markers;
- Selected, Responding and On-site equipment reconciliation;
- one contribution for type-plus-equipment evidence;
- native exact/minimum/maximum personnel attributes;
- explicit tractive/trailer pair de-duplication;
- progress-holder mutation observation;
- LSSM coexistence without a runtime dependency.

## Drift control

`.github/fixtures/lssm-v4-en_GB-emv-baseline.json` records the reviewed upstream aliases, vehicle types, equipment, factors, conditional mappings, tractive compatibility and file hashes. `.github/scripts/audit_lssm_requirement_compatibility.py` checks that every pinned LSSM UK capability remains covered by the Toolkit. Passing `--upstream-root` compares a future local LSSM checkout against the pinned snapshot and reports added or removed aliases and structural changes for human review.

The audit never imports or executes LSSM runtime code and cannot modify Toolkit production data.

## Deliberate differences retained

- Toolkit has a separate On-site bucket; LSSM EMV exposes En-route and Selected only.
- Toolkit keeps Mission Info, patients and uncertainty ranges authoritative.
- Toolkit does not depend on LSSM stores or `max_personnel_override`; it uses stable MissionChief-native personnel evidence and fails closed when exact qualification capacity is unavailable.

## Pinned snapshot

- Vehicle requirements: {len(snapshot['vehicleRequirements'])}
- Staff requirements: {len(snapshot['staffRequirements'])}
- Random-tractive vehicle types: {len(snapshot['tractiveVehicles'])}
''', encoding="utf-8")


def update_release_files() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    DIST_JS.write_text(source, encoding="utf-8")
    DIST_TXT.write_text(source, encoding="utf-8")
    SUMS.write_text(f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n", encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["version"] = "4.20.13"
    manifest["sha256"] = digest
    manifest["bytes"] = len(source.encode("utf-8"))
    manifest["lines"] = len(source.splitlines())
    manifest["metadata"]["runtimeVersion"] = "4.20.13"
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    changelog = CHANGELOG.read_text(encoding="utf-8")
    entry = '''## [4.20.13] - 2026-07-20

### Fixed
- Reconciled water, foam and pumping requirements from MissionChief's authoritative missing, driving and selected progress values without double subtraction.
- Added locally compiled random-tractive capability intersection for trailer selections.
- Removed whole-row caption text as evidence of specialist personnel training.

### Audit
- Completed the pinned LSSM V.4 Enhanced Missing Vehicles compatibility audit.
- Added an offline upstream capability snapshot and drift checker.
- Added resource, nested-equipment, tractive and personnel reliability fixtures.

'''
    changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog")
    CHANGELOG.write_text(changelog, encoding="utf-8")
    help_text = HELP.read_text(encoding="utf-8")
    help_text = replace_once(help_text, "Guide for Toolkit v4.20.12", "Guide for Toolkit v4.20.13", "help version")
    HELP.write_text(help_text, encoding="utf-8")


def run_checks() -> None:
    commands = [
        ["node", "--check", str(SOURCE)],
        ["node", str(RUNTIME_TEST)],
        ["python3", str(AUDIT)],
        ["python3", str(CONTRACT_TEST)],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    source = SOURCE.read_bytes()
    if DIST_JS.read_bytes() != source or DIST_TXT.read_bytes() != source:
        raise RuntimeError("distribution parity failed")


def main() -> None:
    snapshot = write_upstream_baseline()
    write_audit_script()
    update_source(snapshot)
    update_runtime_tests(snapshot)
    update_contract_test()
    write_report(snapshot)
    update_release_files()
    run_checks()


if __name__ == "__main__":
    main()
