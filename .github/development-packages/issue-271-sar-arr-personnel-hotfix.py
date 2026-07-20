#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = "4.20.15"
NEW = "4.20.16"
SOURCE_PATH = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA_PATH = ROOT / "src/data/mission-requirements-en_GB.json"
RUNTIME_TEST_PATH = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CONTRACT_TEST_PATH = ROOT / ".github/scripts/test_mission_requirements_contract.py"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
HELP_PATH = ROOT / "help/index.html"
DOC_PATH = ROOT / "docs/issue-271-sar-arr-personnel-hotfix.md"
INSPECTION_PATH = ROOT / "docs/issue-271-runtime-snippets.txt"
DIST_USER_PATH = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT_PATH = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
SHA_PATH = ROOT / "dist/SHA256SUMS.txt"
MANIFEST_PATH = ROOT / "dist/release-manifest.json"


def required_replace(text: str, old: str, new: str, label: str, *, all_matches: bool = False) -> str:
    count = text.count(old)
    if count < 1:
        raise RuntimeError(f"{label}: marker not found")
    print(f"{label}: {count} match(es)")
    return text.replace(old, new) if all_matches else text.replace(old, new, 1)


def main() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    source = required_replace(source, f"// @version      {OLD}", f"// @version      {NEW}", "metadata version")
    source = required_replace(source, f"version: '{OLD}'", f"version: '{NEW}'", "runtime version")

    source = required_replace(
        source,
        '{"key":"search-advisor-personnel","label":"Search Advisor","aliases":["Search Advisor","Search Advisors"],"group":"staff","types":[],"countable":false}',
        '{"key":"search-advisor-personnel","label":"Search Advisor","aliases":["Search Advisor","Search Advisors"],"group":"staff","types":[],"training":["Search Advisor","Search Advisor Training","Police Search Advisor Training","Coastguard Search Advisor Training","search_and_rescue"],"arrAttributes":["search_and_rescue"],"countable":true}',
        "Search Advisor definition",
    )
    source = required_replace(
        source,
        '{"key":"sar-commander-personnel","label":"SAR Commander","aliases":["SAR Commander","SAR Commanders"],"group":"staff","types":[],"countable":false}',
        '{"key":"sar-commander-personnel","label":"SAR Commander","aliases":["SAR Commander","SAR Commanders"],"group":"staff","types":[85,100],"training":["SAR Commander","Search Management Training","search_and_rescue_command"],"arrAttributes":["search_and_rescue_command"],"countable":true}',
        "SAR Commander definition",
    )

    source = required_replace(
        source,
        '"83":[1,1],"86":[1,3]',
        '"83":[1,1],"85":[1,3],"86":[1,3]',
        "Control Van staff range",
    )
    source = required_replace(
        source,
        '"99":[1,4],"101":[1,1]',
        '"99":[1,4],"100":[1,3],"101":[1,1]',
        "Mountain Control Van staff range",
    )

    known_keys_marker = "function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }"
    arr_runtime = r"""
function missionRequirementsPositiveCapabilityValue(raw) { if (raw === null || raw === undefined) return false; const value = String(raw).trim().toLowerCase(); if (!value || ['0', 'false', 'no', 'off', 'null', 'undefined'].includes(value)) return false; const numeric = Number(value.replace(/,/gu, '')); return Number.isFinite(numeric) ? numeric > 0 : true; }
function missionRequirementsArrCapabilityState(element, candidate = null, vehicleId = -1) { const values = new Set(); let authoritative = false; const attributes = Array.from(new Set(MISSION_REQUIREMENT_DEFINITIONS.flatMap(definition => Array.from(definition?.arrAttributes || [])).map(attribute => String(attribute || '').trim()).filter(attribute => /^[a-z0-9_:-]+$/iu.test(attribute)))); if (!attributes.length) return { values, authoritative }; const inspect = scope => { if (!scope?.getAttribute) return; let present = false; for (const attribute of attributes) { const raw = scope.getAttribute(attribute); if (raw === null || raw === undefined) continue; present = true; if (missionRequirementsPositiveCapabilityValue(raw)) values.add(missionRequirementsCapabilityLabel(attribute)); } if (present) authoritative = true; }; const inspectTree = scope => { if (!scope) return; inspect(scope); const selector = attributes.map(attribute => `[${attribute}]`).join(', '); for (const node of Array.from(scope.querySelectorAll?.(selector) || [])) inspect(node); }; const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || null; inspectTree(element); if (row && row !== element) inspectTree(row); const numericVehicleId = Number(vehicleId); if (Number.isFinite(numericVehicleId) && numericVehicleId >= 0) { const selector = `.vehicle_checkbox[value="${numericVehicleId}"], input[value="${numericVehicleId}"][vehicle_type_id], [data-vehicle-id="${numericVehicleId}"], [vehicle_id="${numericVehicleId}"]`; const scopes = Array.from(new Set([candidate?.root, candidate?.mount, candidate?.source?.ownerDocument, row?.ownerDocument, element?.ownerDocument].filter(scope => scope?.querySelectorAll))); for (const scope of scopes) for (const node of Array.from(scope.querySelectorAll(selector) || [])) inspectTree(node); } if (element?.matches?.('.vehicle_checkbox') || element?.classList?.contains?.('vehicle_checkbox') || (typeof element?.checked === 'boolean' && element?.getAttribute?.('vehicle_type_id') !== null)) authoritative = true; return { values, authoritative }; }
"""
    source = required_replace(source, known_keys_marker, known_keys_marker + arr_runtime, "ARR capability runtime")

    collect_marker = "const labels = missionRequirementsMetadataValues(vehicleElement, 'labels'); const training = missionRequirementsMetadataValues(vehicleElement, 'training'); const knownDefinitionKeys = missionRequirementsKnownDefinitionKeys(labels); const badgeTexts"
    collect_replacement = "const labels = missionRequirementsMetadataValues(vehicleElement, 'labels'); const training = missionRequirementsMetadataValues(vehicleElement, 'training'); const knownDefinitionKeys = missionRequirementsKnownDefinitionKeys(labels); const arrCapabilityState = missionRequirementsArrCapabilityState(vehicleElement, candidate, vehicleId); for (const capability of arrCapabilityState.values) { training.add(capability); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { const attributes = Array.from(definition?.arrAttributes || []).map(missionRequirementsCapabilityLabel).filter(Boolean); if (attributes.includes(capability)) knownDefinitionKeys.add(definition.key); } } const badgeTexts"
    source = required_replace(source, collect_marker, collect_replacement, "unit ARR capability collection")
    source = required_replace(
        source,
        "staff: missionRequirementsStaffCapacity(vehicleElement) || missionRequirementsDefaultStaffCapacity(typeId, vehicleElement), labels, training, knownDefinitionKeys, contributionKey",
        "staff: missionRequirementsStaffCapacity(vehicleElement) || missionRequirementsDefaultStaffCapacity(typeId, vehicleElement), labels, training, arrCapabilities: arrCapabilityState.values, arrCapabilityKnown: arrCapabilityState.authoritative, knownDefinitionKeys, contributionKey",
        "unit ARR capability state",
    )
    source = required_replace(
        source,
        "for (const qualification of unit.training) existing.training.add(qualification); for (const key of unit.knownDefinitionKeys) existing.knownDefinitionKeys.add(key);",
        "for (const qualification of unit.training) existing.training.add(qualification); for (const capability of unit.arrCapabilities || []) existing.arrCapabilities.add(capability); existing.arrCapabilityKnown = existing.arrCapabilityKnown || unit.arrCapabilityKnown; for (const key of unit.knownDefinitionKeys) existing.knownDefinitionKeys.add(key);",
        "merged ARR capability state",
    )

    old_contribution = "function missionRequirementsUnitContribution(requirement, unit) { const definition = requirement.definition || {}; const definitionTypes = Array.from(definition.types || []); const typeEligible = definitionTypes.includes(unit.typeId); const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase())); const labelEligible = unit.knownDefinitionKeys?.has?.(definition.key) || missionRequirementsDefinitionMatchesValues(definition, unit.labels); const compatibleTractiveTypes = Array.from(unit.compatibleTractiveTypes || []).map(Number).filter(Number.isFinite); const tractiveEligible = compatibleTractiveTypes.length > 0 && compatibleTractiveTypes.every(type => definitionTypes.includes(type)); const trainingRequired = Array.from(definition.training || []).length > 0; const trainingEligible = trainingRequired && missionRequirementsDefinitionMatchesValues(definition, unit.training, 'training'); const eligible = requirement.group === 'staff' && trainingRequired ? trainingEligible : typeEligible || equipmentEligible || labelEligible || tractiveEligible; const classificationUnknown = requirement.group === 'staff' && trainingRequired ? Boolean(unit.staff && !unit.training?.size) : unit.typeId < 0 && !unit.knownDefinitionKeys?.size && !unit.equipment?.size && !compatibleTractiveTypes.length; if (!eligible) return { eligible: false, unknown: classificationUnknown, capacity: missionRequirementsCapacity(0, classificationUnknown ? null : 0, !classificationUnknown) }; if (requirement.group === 'staff') { const capacity = unit.staff ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known) : missionRequirementsCapacity(0, null, false); return { eligible: true, unknown: capacity.max === null, capacity }; } const factor = tractiveEligible && !typeEligible ? 1 : Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1); const value = Number.isFinite(factor) && factor > 0 ? factor : 1; return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) }; }"
    new_contribution = "function missionRequirementsUnitContribution(requirement, unit) { const definition = requirement.definition || {}; const definitionTypes = Array.from(definition.types || []); const typeEligible = definitionTypes.includes(unit.typeId); const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase())); const labelEligible = unit.knownDefinitionKeys?.has?.(definition.key) || missionRequirementsDefinitionMatchesValues(definition, unit.labels); const compatibleTractiveTypes = Array.from(unit.compatibleTractiveTypes || []).map(Number).filter(Number.isFinite); const tractiveEligible = compatibleTractiveTypes.length > 0 && compatibleTractiveTypes.every(type => definitionTypes.includes(type)); const trainingRequired = Array.from(definition.training || []).length > 0; const trainingEligible = trainingRequired && missionRequirementsDefinitionMatchesValues(definition, unit.training, 'training'); const arrTokens = new Set(Array.from(definition.arrAttributes || []).map(missionRequirementsCapabilityLabel).filter(Boolean)); const arrEligible = arrTokens.size > 0 && Array.from(unit.arrCapabilities || []).some(capability => arrTokens.has(missionRequirementsCapabilityLabel(capability))); const arrClassificationKnown = arrTokens.size === 0 || unit.arrCapabilityKnown === true; const eligible = requirement.group === 'staff' && trainingRequired ? trainingEligible || arrEligible || typeEligible : typeEligible || equipmentEligible || labelEligible || tractiveEligible; const classificationUnknown = requirement.group === 'staff' && trainingRequired ? Boolean(unit.staff && !eligible && !arrClassificationKnown && !unit.training?.size) : unit.typeId < 0 && !unit.knownDefinitionKeys?.size && !unit.equipment?.size && !compatibleTractiveTypes.length; if (!eligible) return { eligible: false, unknown: classificationUnknown, capacity: missionRequirementsCapacity(0, classificationUnknown ? null : 0, !classificationUnknown) }; if (requirement.group === 'staff') { const capacity = unit.staff ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known) : missionRequirementsCapacity(0, null, false); return { eligible: true, unknown: capacity.max === null, capacity }; } const factor = tractiveEligible && !typeEligible ? 1 : Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1); const value = Number.isFinite(factor) && factor > 0 ? factor : 1; return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) }; }"
    source = required_replace(source, old_contribution, new_contribution, "ARR-aware specialist contribution")
    SOURCE_PATH.write_text(source, encoding="utf-8")

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    staff = data.setdefault("staffRequirements", [])
    keys = {entry.get("key") for entry in staff}
    if "search-advisor-personnel" not in keys:
        staff.append({
            "key": "search-advisor-personnel",
            "aliases": ["Search Advisor", "Search Advisors"],
            "types": [],
            "training": ["Search Advisor", "Search Advisor Training", "Police Search Advisor Training", "Coastguard Search Advisor Training", "search_and_rescue"],
            "arrAttributes": ["search_and_rescue"],
        })
    if "sar-commander-personnel" not in keys:
        staff.append({
            "key": "sar-commander-personnel",
            "aliases": ["SAR Commander", "SAR Commanders"],
            "types": [85, 100],
            "training": ["SAR Commander", "Search Management Training", "search_and_rescue_command"],
            "arrAttributes": ["search_and_rescue_command"],
        })
    DATA_PATH.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    test = RUNTIME_TEST_PATH.read_text(encoding="utf-8")
    test = required_replace(test, f"version: '{OLD}'", f"version: '{NEW}'", "runtime fixture version")
    test = required_replace(
        test,
        "    metadataValues: missionRequirementsMetadataValues,\n    operationalSelectors: missionRequirementsOperationalSelectors,",
        "    metadataValues: missionRequirementsMetadataValues,\n    arrCapabilityState: missionRequirementsArrCapabilityState,\n    operationalSelectors: missionRequirementsOperationalSelectors,",
        "runtime ARR API export",
    )
    test = required_replace(
        test,
        "            for (const equipment of entry.equipment || []) {\n                assert.ok((definition.equipment || []).includes(equipment), `${group}:${entry.key}: ${alias} supports equipment ${equipment}`);\n            }",
        "            for (const equipment of entry.equipment || []) {\n                assert.ok((definition.equipment || []).includes(equipment), `${group}:${entry.key}: ${alias} supports equipment ${equipment}`);\n            }\n            for (const training of entry.training || []) {\n                assert.ok((definition.training || []).includes(training), `${group}:${entry.key}: ${alias} supports training ${training}`);\n            }\n            for (const attribute of entry.arrAttributes || []) {\n                assert.ok((definition.arrAttributes || []).includes(attribute), `${group}:${entry.key}: ${alias} supports ARR attribute ${attribute}`);\n            }",
        "UK capability metadata tests",
    )
    marker = "const factorRequirement = { group: 'vehicles', definition: { types: [5], equipment: [], factors: { 5: 2 } } };"
    checks = r"""
// Issue #271: ARR specialist capabilities reconcile Search Advisor and SAR Commander personnel.
{
const issue271Doc = new FakeDocument();
issue271Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/271' } };
const issue271Candidate = makeMissionCandidate(issue271Doc, '1 Search Advisor, 2 SAR Commanders');
const searchAdvisorDefinition = api.definitions.find(definition => definition.key === 'search-advisor-personnel');
const sarCommanderDefinition = api.definitions.find(definition => definition.key === 'sar-commander-personnel');
assert(searchAdvisorDefinition?.countable, 'Search Advisor is countable');
assert(sarCommanderDefinition?.countable, 'SAR Commander is countable');

const advisor = makeVehicleElement(issue271Doc, 27101, 86, { staff: 1 });
advisor.vehicle.checked = true;
advisor.vehicle.matchSet.add('.vehicle_checkbox');
advisor.vehicle.classList.values.add('vehicle_checkbox');
advisor.vehicle.setAttribute('search_and_rescue', '1');
issue271Candidate.root.selectedUnits = [advisor.vehicle];
let issue271Units = api.collectUnits(issue271Candidate, 'selected');
let issue271Capacity = api.aggregate({ group: 'staff', definition: searchAdvisorDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 1, 'ARR-selected Search Advisor contributes confirmed personnel');
assert.strictEqual(issue271Capacity.max, 1, 'semantic selected crew keeps Search Advisor exact');
let issue271Rows = api.resolve(issue271Candidate, {
    requirements: [{ key: 'search-advisor-personnel', requirement: 'Search Advisor', missing: 1, group: 'staff', definition: searchAdvisorDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'search-advisor-personnel', baseline: 1, missing: 1 }] });
let issue271Row = issue271Rows.find(row => row.key === 'search-advisor-personnel');
assert.strictEqual(issue271Row.selectedMin, 1, 'selected ARR Search Advisor appears in Matrix Selected');
assert.strictEqual(issue271Row.stillNeededText, '0', 'selected ARR Search Advisor clears shortage');

const explicitState = api.arrCapabilityState(advisor.vehicle, issue271Candidate, 27101);
assert.strictEqual(explicitState.authoritative, true, 'vehicle checkbox is an authoritative ARR capability source');
assert.strictEqual(explicitState.values.size, 1, 'positive ARR attribute is captured');

const nonAdvisor = makeVehicleElement(issue271Doc, 27102, 86, { staff: 1 });
nonAdvisor.vehicle.checked = true;
nonAdvisor.vehicle.matchSet.add('.vehicle_checkbox');
nonAdvisor.vehicle.classList.values.add('vehicle_checkbox');
nonAdvisor.vehicle.setAttribute('search_and_rescue', '0');
issue271Candidate.root.selectedUnits = [nonAdvisor.vehicle];
issue271Units = api.collectUnits(issue271Candidate, 'selected');
issue271Capacity = api.aggregate({ group: 'staff', definition: searchAdvisorDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 0, 'zero ARR Search Advisor attribute contributes nothing');
assert.strictEqual(issue271Capacity.max, 0, 'authoritative zero ARR attribute remains known rather than unknown');

const commander = makeVehicleElement(issue271Doc, 27103, 85);
commander.vehicle.checked = true;
commander.vehicle.matchSet.add('.vehicle_checkbox');
commander.vehicle.classList.values.add('vehicle_checkbox');
issue271Candidate.root.selectedUnits = [commander.vehicle];
issue271Units = api.collectUnits(issue271Candidate, 'selected');
issue271Capacity = api.aggregate({ group: 'staff', definition: sarCommanderDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 1, 'Control Van guarantees at least one SAR Commander');
assert.strictEqual(issue271Capacity.max, 3, 'Control Van preserves reviewed SAR Commander staff range');

const respondingAdvisor = makeVehicleElement(issue271Doc, 27104, 86, { typeOnRow: true });
respondingAdvisor.row.setAttribute('search_and_rescue', '1');
issue271Candidate.root.selectedUnits = [];
issue271Candidate.root.enRouteRows = [respondingAdvisor.row];
issue271Units = api.collectUnits(issue271Candidate, 'responding');
issue271Capacity = api.aggregate({ group: 'staff', definition: searchAdvisorDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 1, 'responding row ARR capability contributes Search Advisor');
assert.strictEqual(issue271Capacity.max, 3, 'responding Search Advisor preserves vehicle staff range');

const onsiteCommander = makeVehicleElement(issue271Doc, 27105, 100, { typeOnRow: true });
issue271Candidate.root.enRouteRows = [];
issue271Candidate.root.onSiteRows = [onsiteCommander.row];
issue271Units = api.collectUnits(issue271Candidate, 'onsite');
issue271Capacity = api.aggregate({ group: 'staff', definition: sarCommanderDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 1, 'Mountain Rescue Control Van contributes on-site SAR Commander');
assert.strictEqual(issue271Capacity.max, 3, 'on-site SAR Commander retains reviewed staff range');

issue271Candidate.root.selectedUnits = [];
issue271Candidate.root.onSiteRows = [];
issue271Rows = api.resolve(issue271Candidate, {
    requirements: [{ key: 'search-advisor-personnel', requirement: 'Search Advisor', missing: 1, group: 'staff', definition: searchAdvisorDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'search-advisor-personnel', baseline: 1, missing: 1 }] });
issue271Row = issue271Rows.find(row => row.key === 'search-advisor-personnel');
assert.strictEqual(issue271Row.selectedMin, 0, 'deselection removes Search Advisor selected capacity');
assert.strictEqual(issue271Row.stillNeededText, '1', 'Search Advisor shortage returns after deselection');
}

"""
    test = required_replace(test, marker, checks + marker, "Issue 271 runtime regressions")
    RUNTIME_TEST_PATH.write_text(test, encoding="utf-8")

    contract = CONTRACT_TEST_PATH.read_text(encoding="utf-8")
    contract = required_replace(
        contract,
        '        "function missionRequirementsMetadataValues(element, kind = \'labels\')",\n        "data-personnel-training",',
        '        "function missionRequirementsMetadataValues(element, kind = \'labels\')",\n        "function missionRequirementsArrCapabilityState(element, candidate = null, vehicleId = -1)",\n        "data-personnel-training",',
        "contract ARR helper marker",
    )
    contract = required_replace(
        contract,
        '    assert \'"key":"police-sergeant-personnel"\' in source and \'"police_sergeant"\' in source, "Police Sergeant needs native training evidence"\n',
        '    assert \'"key":"police-sergeant-personnel"\' in source and \'"police_sergeant"\' in source, "Police Sergeant needs native training evidence"\n'
        '    assert \'"key":"search-advisor-personnel"\' in source and \'"search_and_rescue"\' in source and \'"countable":true\' in source, "Search Advisor needs ARR capability evidence"\n'
        '    assert \'"key":"sar-commander-personnel"\' in source and \'"search_and_rescue_command"\' in source, "SAR Commander needs ARR capability evidence"\n',
        "contract specialist ARR assertions",
    )
    CONTRACT_TEST_PATH.write_text(contract, encoding="utf-8")

    changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
    entry = """## [4.20.16] - 2026-07-20

### Fixed
- Search Advisor personnel selected through MissionChief ARR capability `search_and_rescue` now update the Matrix immediately.
- SAR Commander personnel selected through `search_and_rescue_command` now update Selected, Responding and On Site capacity.
- Control Van vehicle types 85 and 100 now provide their reviewed 1–3 SAR Commander personnel range when explicit crew metadata is unavailable.
- Explicit zero or absent ARR capability evidence no longer turns unrelated selected vehicles into unresolved specialist personnel.

### Validation
- Added deterministic selected, responding, on-site, ARR-positive, ARR-zero, Control Van fallback and deselection regressions.

"""
    changelog = required_replace(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog")
    CHANGELOG_PATH.write_text(changelog, encoding="utf-8")

    HELP_PATH.write_text(
        HELP_PATH.read_text(encoding="utf-8").replace(f"Guide for Toolkit v{OLD}", f"Guide for Toolkit v{NEW}"),
        encoding="utf-8",
    )
    DOC_PATH.write_text(
        """# Issue 271 — Search Advisor and SAR Commander ARR personnel hotfix

Toolkit v4.20.16 bridges MissionChief's native ARR capability attributes into the live Mission Requirements Matrix.

- `search_and_rescue` proves Search Advisor capability for the specific selected vehicle.
- `search_and_rescue_command` proves SAR Commander capability.
- Control Van types 85 and 100 remain guaranteed SAR Commander carriers.
- Native personnel/training metadata remains authoritative.
- Unrelated specialist requirements remain fail-closed.
- The capability is retained through selected, responding and on-site unit reconciliation when MissionChief exposes the ARR attribute or a guaranteed vehicle type.
""",
        encoding="utf-8",
    )
    INSPECTION_PATH.unlink(missing_ok=True)

    final = SOURCE_PATH.read_text(encoding="utf-8")
    DIST_USER_PATH.write_text(final, encoding="utf-8")
    DIST_TEXT_PATH.write_text(final, encoding="utf-8")
    digest = hashlib.sha256(final.encode("utf-8")).hexdigest()
    SHA_PATH.write_text(
        f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
        encoding="utf-8",
    )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest.update({
        "version": NEW,
        "sha256": digest,
        "bytes": len(final.encode("utf-8")),
        "lines": len(final.splitlines()),
    })
    manifest.setdefault("metadata", {})["runtimeVersion"] = NEW
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Prepared Toolkit {NEW} Issue #271 hotfix candidate: {digest}")


if __name__ == "__main__":
    main()
