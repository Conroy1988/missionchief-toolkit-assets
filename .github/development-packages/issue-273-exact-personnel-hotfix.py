#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = "4.20.16"
NEW = "4.20.17"
SOURCE_PATH = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST_PATH = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CONTRACT_TEST_PATH = ROOT / ".github/scripts/test_mission_requirements_contract.py"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
HELP_PATH = ROOT / "help/index.html"
DOC_PATH = ROOT / "docs/issue-273-exact-personnel-hotfix.md"
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


def function_end(text: str, name: str) -> int:
    marker = f"function {name}("
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"{name}: function not found")
    brace = text.find("{", start)
    depth = 0
    quote = None
    escape = False
    for index in range(brace, len(text)):
        char = text[index]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    raise RuntimeError(f"{name}: unterminated function")


def main() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    source = required_replace(source, f"// @version      {OLD}", f"// @version      {NEW}", "metadata version")
    source = required_replace(source, f"version: '{OLD}'", f"version: '{NEW}'", "runtime version")

    source = required_replace(
        source,
        "            '[data-current-personnel]',\n            '[data-min-personnel]',",
        "            '[data-current-personnel]',\n            '[data-assigned-personnel-count]',\n            '[data-assigned_personnel_count]',\n            '[assigned_personnel_count]',\n            '[data-min-personnel]',",
        "assigned personnel semantic selectors",
    )
    source = required_replace(
        source,
        "const exactAttributes = ['data-personnel-count', 'data-current-personnel', 'data-personnel', 'data-staff', 'data-crew'];",
        "const exactAttributes = ['data-personnel-count', 'data-current-personnel', 'data-assigned-personnel-count', 'data-assigned_personnel_count', 'assigned_personnel_count', 'data-personnel', 'data-staff', 'data-crew'];",
        "assigned personnel exact attributes",
    )

    api_runtime = r'''
    const MISSION_REQUIREMENTS_VEHICLE_API_TTL_MS = 60 * 1000;
    const MISSION_REQUIREMENTS_VEHICLE_API_FAILURE_TTL_MS = 15 * 1000;
    const missionRequirementsVehicleApiCache = new Map();
    const missionRequirementsVehicleApiPending = new Map();
    function missionRequirementsVehicleApiRecord(vehicleId, now = Date.now()) { const id = Number(vehicleId); if (!Number.isFinite(id) || id < 0) return null; const cached = missionRequirementsVehicleApiCache.get(id); if (!cached) return null; if (Number(cached.expiresAt) <= now) { missionRequirementsVehicleApiCache.delete(id); return null; } return cached.record || null; }
    function missionRequirementsVehicleApiStaff(record) { const assigned = missionRequirementsOptionalNumber(record?.assigned_personnel_count ?? record?.assignedPersonnelCount ?? record?.personnel_count); if (assigned === null) return null; return missionRequirementsCapacity(assigned, assigned, true); }
    function missionRequirementsRequestVehicleApiRecord(vehicleId) { const id = Number(vehicleId); if (!Number.isFinite(id) || id < 0 || missionRequirementsVehicleApiPending.has(id) || missionRequirementsVehicleApiRecord(id)) return; const fetcher = typeof pageWindow?.fetch === 'function' ? pageWindow.fetch.bind(pageWindow) : (typeof fetch === 'function' ? fetch.bind(globalThis) : null); if (!fetcher) return; const request = Promise.resolve(fetcher(`/api/vehicles/${id}`, { credentials: 'same-origin', cache: 'no-cache', headers: { Accept: 'application/json' } })).then(response => { if (!response || response.ok === false) throw new Error(`Vehicle API ${response?.status || 'unavailable'}`); return response.json(); }).then(record => { if (!record || typeof record !== 'object') throw new Error('Vehicle API returned no record'); missionRequirementsVehicleApiCache.set(id, { record, expiresAt: Date.now() + MISSION_REQUIREMENTS_VEHICLE_API_TTL_MS }); }).catch(() => { missionRequirementsVehicleApiCache.set(id, { record: null, expiresAt: Date.now() + MISSION_REQUIREMENTS_VEHICLE_API_FAILURE_TTL_MS }); }).finally(() => { missionRequirementsVehicleApiPending.delete(id); if (!runtime.destroyed && state.missionRequirements) scheduleMissionRequirementsScan(0); }); missionRequirementsVehicleApiPending.set(id, request); }
    function missionRequirementsResolvedVehicleType(vehicleId, element) { const detected = missionRequirementsVehicleType(element); if (detected >= 0) return detected; const recordType = missionRequirementsOptionalNumber(missionRequirementsVehicleApiRecord(vehicleId)?.vehicle_type); return recordType === null ? -1 : recordType; }
    function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element) { const native = missionRequirementsStaffCapacity(element); if (native?.known) return native; const exact = missionRequirementsVehicleApiStaff(missionRequirementsVehicleApiRecord(vehicleId)); if (exact) return exact; missionRequirementsRequestVehicleApiRecord(vehicleId); return native || missionRequirementsDefaultStaffCapacity(typeId, element); }
'''
    insert_at = function_end(source, "missionRequirementsDefaultStaffCapacity")
    source = source[:insert_at] + api_runtime + source[insert_at:]

    source = required_replace(
        source,
        "const typeId = missionRequirementsVehicleType(vehicleElement); const vehicleId = missionRequirementsVehicleId(vehicleElement);",
        "const vehicleId = missionRequirementsVehicleId(vehicleElement); const typeId = missionRequirementsResolvedVehicleType(vehicleId, vehicleElement);",
        "API-backed vehicle type resolution",
    )
    source = required_replace(
        source,
        "staff: missionRequirementsStaffCapacity(vehicleElement) || missionRequirementsDefaultStaffCapacity(typeId, vehicleElement),",
        "staff: missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement),",
        "API-backed exact personnel resolution",
    )
    SOURCE_PATH.write_text(source, encoding="utf-8")

    test = RUNTIME_TEST_PATH.read_text(encoding="utf-8")
    test = required_replace(test, f"version: '{OLD}'", f"version: '{NEW}'", "runtime fixture version")
    test = required_replace(
        test,
        "    arrCapabilityState: missionRequirementsArrCapabilityState,\n    operationalSelectors: missionRequirementsOperationalSelectors,",
        "    arrCapabilityState: missionRequirementsArrCapabilityState,\n    vehicleApiCache: missionRequirementsVehicleApiCache,\n    vehicleApiRecord: missionRequirementsVehicleApiRecord,\n    vehicleApiStaff: missionRequirementsVehicleApiStaff,\n    resolvedStaffCapacity: missionRequirementsResolvedStaffCapacity,\n    operationalSelectors: missionRequirementsOperationalSelectors,",
        "runtime vehicle API exports",
    )
    marker = "// Issue #271: ARR specialist capabilities reconcile Search Advisor and SAR Commander personnel."
    checks = r'''
// Issue #273: exact assigned personnel clears trained and generic police requirements.
{
const issue273Doc = new FakeDocument();
issue273Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/273' } };
const issue273Candidate = makeMissionCandidate(issue273Doc, '18 Level 2 Public Order Officers');
const level2Definition = api.definitions.find(definition => definition.key === 'public-order-level-2');
const cacheVehicle = (id, type, personnel) => api.vehicleApiCache.set(id, { record: { id, vehicle_type: type, assigned_personnel_count: personnel }, expiresAt: Date.now() + 60000 });
const firstCarrier = makeVehicleElement(issue273Doc, 27301, 51, { typeOnRow: true });
const secondCarrier = makeVehicleElement(issue273Doc, 27302, 51, { typeOnRow: true });
for (const carrier of [firstCarrier, secondCarrier]) {
    carrier.vehicle.checked = true;
    carrier.vehicle.matchSet.add('.vehicle_checkbox');
    carrier.vehicle.classList.values.add('vehicle_checkbox');
    carrier.row.textContent = carrier.row.innerText = 'Police Support Unit Carrier [Level 2 Public Order Officer]';
}
cacheVehicle(27301, 51, 9);
cacheVehicle(27302, 51, 9);
issue273Candidate.root.selectedUnits = [firstCarrier.vehicle, secondCarrier.vehicle];
let issue273Units = api.collectUnits(issue273Candidate, 'selected');
let issue273Capacity = api.aggregate({ group: 'staff', definition: level2Definition }, issue273Units);
assert.strictEqual(issue273Capacity.min, 18, 'two exact nine-person public-order carriers contribute eighteen');
assert.strictEqual(issue273Capacity.max, 18, 'exact assigned personnel removes the 2–18 fallback range');
let issue273Rows = api.resolve(issue273Candidate, {
    requirements: [{ key: 'public-order-level-2', requirement: 'Level 2 Public Order Officer', missing: 18, group: 'staff', definition: level2Definition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'public-order-level-2', baseline: 18, missing: 18 }] });
let issue273Row = issue273Rows.find(row => row.key === 'public-order-level-2');
assert.strictEqual(issue273Row.selectedText, '18', 'Matrix displays exact selected public-order personnel');
assert.strictEqual(issue273Row.stillNeededText, '0', '9 + 9 clears the eighteen-person requirement');
assert.strictEqual(issue273Row.covered, true, 'fulfilled public-order row is marked covered');
issue273Candidate.root.selectedUnits = [firstCarrier.vehicle];
issue273Rows = api.resolve(issue273Candidate, {
    requirements: [{ key: 'public-order-level-2', requirement: 'Level 2 Public Order Officer', missing: 18, group: 'staff', definition: level2Definition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'public-order-level-2', baseline: 18, missing: 18 }] });
issue273Row = issue273Rows.find(row => row.key === 'public-order-level-2');
assert.strictEqual(issue273Row.selectedText, '9', 'deselecting one public-order carrier removes nine personnel');
assert.strictEqual(issue273Row.stillNeededText, '9', 'nine-person shortage returns after deselection');

const policeDefinition = api.definitions.find(definition => definition.key === 'police-officers');
const sceneUnits = [];
for (let index = 0; index < 11; index += 1) {
    const id = 273100 + index;
    const unit = makeVehicleElement(issue273Doc, id, 8, { typeOnRow: true });
    cacheVehicle(id, 8, 1);
    sceneUnits.push(unit.row);
}
issue273Candidate.root.selectedUnits = [];
issue273Candidate.root.onSiteRows = sceneUnits;
let policeRows = api.resolve(issue273Candidate, {
    requirements: [{ key: 'police-officers', requirement: 'Police Officers', missing: 2, group: 'staff', definition: policeDefinition, statedRequirement: true }],
    unresolved: []
});
let policeRow = policeRows.find(row => row.key === 'police-officers');
assert.strictEqual(policeRow.onSiteText, '11', 'eleven on-scene police personnel are exact rather than 7+');
assert.strictEqual(policeRow.requiredText, '13', 'live missing two plus exact on-scene eleven reconstructs required thirteen');
assert.strictEqual(policeRow.stillNeededText, '2', 'generic Police Officers shortage remains accurate');
const selectedTrafficCar = makeVehicleElement(issue273Doc, 273200, 24, { typeOnRow: true });
selectedTrafficCar.vehicle.checked = true;
selectedTrafficCar.vehicle.matchSet.add('.vehicle_checkbox');
selectedTrafficCar.vehicle.classList.values.add('vehicle_checkbox');
cacheVehicle(273200, 24, 2);
issue273Candidate.root.selectedUnits = [selectedTrafficCar.vehicle];
policeRows = api.resolve(issue273Candidate, {
    requirements: [{ key: 'police-officers', requirement: 'Police Officers', missing: 2, group: 'staff', definition: policeDefinition, statedRequirement: true }],
    unresolved: []
});
policeRow = policeRows.find(row => row.key === 'police-officers');
assert.strictEqual(policeRow.selectedText, '2', 'any eligible selected police vehicle contributes exact assigned officers');
assert.strictEqual(policeRow.stillNeededText, '0', 'selected police officers clear the remaining generic shortage');
assert.strictEqual(policeRow.covered, true, 'generic Police Officers row clears when exact total is met');

const nativeExact = makeVehicleElement(issue273Doc, 273300, 51, { staff: 4 });
cacheVehicle(273300, 51, 9);
assert.strictEqual(api.resolvedStaffCapacity(273300, 51, nativeExact.vehicle).min, 4, 'native exact crew metadata remains higher priority than cached API data');
assert.deepStrictEqual(JSON.parse(JSON.stringify(api.vehicleApiStaff({ assigned_personnel_count: 0 }))), { min: 0, max: 0, known: true, value: 0 }, 'zero assigned personnel remains exact');
}

'''
    test = required_replace(test, marker, checks + marker, "Issue 273 runtime regressions")
    RUNTIME_TEST_PATH.write_text(test, encoding="utf-8")

    contract = CONTRACT_TEST_PATH.read_text(encoding="utf-8")
    contract = required_replace(
        contract,
        '        "function missionRequirementsArrCapabilityState(element, candidate = null, vehicleId = -1)",\n        "data-personnel-training",',
        '        "function missionRequirementsArrCapabilityState(element, candidate = null, vehicleId = -1)",\n        "function missionRequirementsVehicleApiRecord(vehicleId, now = Date.now())",\n        "function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element)",\n        "assigned_personnel_count",\n        "/api/vehicles/",\n        "data-personnel-training",',
        "contract exact personnel markers",
    )
    contract = required_replace(
        contract,
        '    assert \'"key":"sar-commander-personnel"\' in source and \'"search_and_rescue_command"\' in source, "SAR Commander needs ARR capability evidence"\n',
        '    assert \'"key":"sar-commander-personnel"\' in source and \'"search_and_rescue_command"\' in source, "SAR Commander needs ARR capability evidence"\n'
        '    assert "assigned_personnel_count" in source and "missionRequirementsVehicleApiStaff" in source, "exact vehicle personnel API evidence is required"\n',
        "contract exact personnel assertion",
    )
    CONTRACT_TEST_PATH.write_text(contract, encoding="utf-8")

    changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
    entry = """## [4.20.17] - 2026-07-20

### Fixed
- Level 2 Public Order Officer ARR selections now use each vehicle's exact MissionChief `assigned_personnel_count` when available, so two nine-officer carriers clear an eighteen-officer requirement.
- Generic Police Officers now use exact assigned personnel across Selected, Responding and On Site units instead of remaining at vehicle-type minimum ranges such as `7+`.
- Live required totals reconstructed from current shortages now become exact as soon as on-scene personnel is known.
- Native exact crew metadata remains authoritative; inaccessible or alliance vehicles retain the reviewed fail-closed type range.

### Validation
- Added deterministic 9 + 9 public-order, deselection, eleven-on-scene police, selected traffic-car, native-priority and zero-personnel regressions.

"""
    changelog = required_replace(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog")
    CHANGELOG_PATH.write_text(changelog, encoding="utf-8")

    HELP_PATH.write_text(
        HELP_PATH.read_text(encoding="utf-8").replace(f"Guide for Toolkit v{OLD}", f"Guide for Toolkit v{NEW}"),
        encoding="utf-8",
    )
    DOC_PATH.write_text(
        """# Issue 273 — exact personnel reconciliation hotfix

Toolkit v4.20.17 resolves the exact assigned personnel count for each visible MissionChief vehicle by vehicle ID.

- Native exact DOM crew evidence remains first priority.
- The same-origin MissionChief `/api/vehicles/{id}` record supplies `assigned_personnel_count` when the dispatch table only exposes a type range.
- Results are cached for sixty seconds and failed lookups back off for fifteen seconds.
- Exact capacity is retained through Selected, Responding and On Site deduplication.
- Level 2 Public Order Officer and generic Police Officers therefore clear only when their real personnel total meets demand.
- Vehicles that cannot be read retain the reviewed minimum/maximum range rather than being guessed.
""",
        encoding="utf-8",
    )

    for path in [
        ROOT / "docs/issue-273-runtime-snippets.txt",
        ROOT / "docs/issue-273-resolve-wrapped.txt",
        ROOT / ".github/development-packages/issue-273-inspect.py",
        ROOT / ".github/development-packages/issue-273-resolve-inspect.py",
    ]:
        path.unlink(missing_ok=True)

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
    print(f"Prepared Toolkit {NEW} Issue #273 exact personnel hotfix candidate: {digest}")


if __name__ == "__main__":
    main()
