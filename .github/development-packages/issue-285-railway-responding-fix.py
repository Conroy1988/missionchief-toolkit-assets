#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src/data/mission-requirements-en_GB.json"
RUNTIME = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github/scripts/test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DOC = ROOT / "docs/issue-285-railway-police-responding-contract.md"
DIST_JS = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
SUMS = ROOT / "dist/SHA256SUMS.txt"
DIAGNOSTIC_PACKAGE = ROOT / ".github/development-packages/issue-285-railway-responding-diagnostic.py"
DIAGNOSTIC_DOC = ROOT / "docs/issue-285-railway-responding-diagnostic.txt"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def append_unique(values: list[str], additions: list[str]) -> None:
    folded = {str(value).strip().casefold() for value in values}
    for addition in additions:
        key = addition.strip().casefold()
        if key not in folded:
            values.append(addition)
            folded.add(key)


def main() -> int:
    # Keep the standalone UK contract aligned with the embedded runtime definition.
    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    staff = dataset.setdefault("staffRequirements", [])
    railway = next((entry for entry in staff if entry.get("key") == "railway-police-officer"), None)
    if railway is None:
        railway = {
            "key": "railway-police-officer",
            "aliases": ["Railway Police Officer", "Railway Police Officers"],
            "types": [],
            "training": ["Railway Police Officer", "Railway Police", "railway_police"],
        }
        staff.append(railway)
    else:
        append_unique(railway.setdefault("aliases", []), ["Railway Police Officer", "Railway Police Officers"])
        append_unique(railway.setdefault("training", []), ["Railway Police Officer", "Railway Police", "railway_police"])
    DATA.write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    source = SOURCE.read_text(encoding="utf-8")

    # Update the embedded runtime definition without reformatting the full userscript.
    marker = "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze("
    start = source.find(marker)
    end = source.find(");", start + len(marker))
    if start < 0 or end < 0:
        raise RuntimeError("unable to locate embedded Mission Requirements definitions")
    payload_start = start + len(marker)
    definitions = json.loads(source[payload_start:end])
    runtime_railway = next((entry for entry in definitions if entry.get("key") == "railway-police-officer"), None)
    if runtime_railway is None:
        raise RuntimeError("embedded Railway Police Officer definition is missing")
    append_unique(runtime_railway.setdefault("training", []), ["Railway Police Officer", "Railway Police", "railway_police"])
    runtime_railway["countable"] = True
    source = source[:payload_start] + json.dumps(definitions, separators=(",", ":"), ensure_ascii=False) + source[end:]

    source = replace_once(
        source,
        "const attributes = kind === 'training' ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name'] :",
        "const attributes = kind === 'training' ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name', 'data-education-key', 'data-filterable-by'] :",
        "specialist education metadata attributes",
    )
    source = replace_once(
        source,
        "function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }",
        "function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if ((definition?.group || 'vehicles') === 'staff') continue; if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }",
        "vehicle labels cannot prove specialist personnel training",
    )

    helper_anchor = "function missionRequirementsStaffCapacity(element) {"
    helper = r'''function missionRequirementsLinkedTrainingValues(candidate, vehicleId, element) {
        const values = missionRequirementsMetadataValues(element, 'training');
        const numericVehicleId = Number(vehicleId);
        if (!Number.isFinite(numericVehicleId) || numericVehicleId < 0) return values;
        const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || null;
        const selector = `.vehicle_checkbox[value="${numericVehicleId}"], input[value="${numericVehicleId}"][vehicle_type_id], [data-vehicle-id="${numericVehicleId}"], [vehicle_id="${numericVehicleId}"]`;
        const scopes = Array.from(new Set([
            candidate?.root,
            candidate?.mount,
            candidate?.source?.ownerDocument,
            row?.ownerDocument,
            element?.ownerDocument
        ].filter(scope => scope?.querySelectorAll)));
        for (const scope of scopes) {
            for (const node of Array.from(scope.querySelectorAll(selector) || [])) {
                for (const qualification of missionRequirementsMetadataValues(node, 'training')) values.add(qualification);
                const linkedRow = node?.matches?.('tr') ? node : node?.closest?.('tr') || null;
                const badges = Array.from(String(linkedRow?.textContent || linkedRow?.innerText || '').matchAll(/\[([^\]]+)\]/gu))
                    .map(match => missionRequirementsCapabilityLabel(match[1]))
                    .filter(Boolean);
                for (const badge of badges) values.add(badge);
            }
        }
        return values;
    }

    function missionRequirementsRespondingCrewCapacity(element) {
        const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || null;
        if (!row) return null;
        const container = row.closest?.('#mission_vehicle_driving, tbody#mission_vehicle_driving');
        if (!container) return null;
        const crewCell = row.querySelector?.('td:nth-of-type(5)[sortvalue]');
        const value = missionRequirementsOptionalNumber(crewCell?.getAttribute?.('sortvalue'));
        if (value === null) return null;
        return missionRequirementsCapacity(value, value, true);
    }

    '''
    if source.count(helper_anchor) != 1:
        raise RuntimeError("staff-capacity helper anchor is not unique")
    source = source.replace(helper_anchor, helper + helper_anchor, 1)

    old_resolved = "function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element) { const native = missionRequirementsStaffCapacity(element); if (native?.known) return native; const exact = missionRequirementsVehicleApiStaff(missionRequirementsVehicleApiRecord(vehicleId)); if (exact) return exact; missionRequirementsEnsureSharedVehicleData(); return native || missionRequirementsDefaultStaffCapacity(typeId, element); }"
    new_resolved = "function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element, mode = '') { const native = missionRequirementsStaffCapacity(element); if (native?.known) return native; const responding = mode === 'responding' ? missionRequirementsRespondingCrewCapacity(element) : null; if (responding) return responding; const exact = missionRequirementsVehicleApiStaff(missionRequirementsVehicleApiRecord(vehicleId)); if (exact) return exact; missionRequirementsEnsureSharedVehicleData(); return native || missionRequirementsDefaultStaffCapacity(typeId, element); }"
    source = replace_once(source, old_resolved, new_resolved, "responding crew resolution")
    source = replace_once(
        source,
        "const training = missionRequirementsMetadataValues(vehicleElement, 'training');",
        "const training = missionRequirementsLinkedTrainingValues(candidate, vehicleId, vehicleElement);",
        "linked specialist training acquisition",
    )
    source = replace_once(
        source,
        "staff: missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement),",
        "staff: missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement, mode),",
        "operational mode passed to staff resolver",
    )
    SOURCE.write_text(source, encoding="utf-8")

    runtime = RUNTIME.read_text(encoding="utf-8")
    runtime = replace_once(
        runtime,
        "    staffCapacity: missionRequirementsStaffCapacity,\n",
        "    staffCapacity: missionRequirementsStaffCapacity,\n    respondingCrewCapacity: missionRequirementsRespondingCrewCapacity,\n    linkedTrainingValues: missionRequirementsLinkedTrainingValues,\n",
        "runtime helper exports",
    )
    railway_anchor = "assert.strictEqual(railwaySelectedCapacity.max, 1, 'one selected Railway Police Officer remains exact');\n"
    railway_tests = r'''

// Issue #285: canonical Units Responding crew and exact Railway Policing evidence.
{
const issue285CrewCell = {
    textContent: '4',
    getAttribute(name) { return name === 'sortvalue' ? '4' : null; }
};
const issue285DrivingContainer = {};
const issue285RespondingRow = {
    textContent: '',
    innerText: '',
    ownerDocument: null,
    matches(selector) { return selector === 'tr'; },
    closest(selector) {
        if (selector === '#mission_vehicle_driving, tbody#mission_vehicle_driving') return issue285DrivingContainer;
        return null;
    },
    querySelector(selector) {
        if (selector === 'td:nth-of-type(5)[sortvalue]') return issue285CrewCell;
        return null;
    },
    querySelectorAll() { return []; },
    getAttribute() { return null; }
};
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(api.respondingCrewCapacity(issue285RespondingRow))),
    { min: 4, max: 4, known: true, value: 4 },
    'canonical responding fifth-cell sortvalue provides exact crew capacity'
);
const issue285NonRespondingRow = { ...issue285RespondingRow, closest() { return null; } };
assert.strictEqual(api.respondingCrewCapacity(issue285NonRespondingRow), null, 'positional sortvalue is rejected outside the canonical responding table');

const issue285Local = new FakeElement('a');
const issue285Linked = new FakeElement('input');
issue285Linked.setAttribute('data-education-key', 'railway_police');
const issue285LinkedRow = new FakeElement('tr');
issue285Linked.closestMap.set('tr', issue285LinkedRow);
const issue285Candidate = {
    root: {
        querySelectorAll(selector) { return selector.includes('28501') ? [issue285Linked] : []; }
    },
    mount: null,
    source: null
};
const issue285Training = api.linkedTrainingValues(issue285Candidate, 28501, issue285Local);
assert(issue285Training.has('railway police'), 'linked data-education-key railway_police is recognised');
const issue285Command = new FakeElement('span');
issue285Command.setAttribute('data-education-key', 'railway_police_command');
const issue285CommandValues = api.metadataValues(issue285Command, 'training');
assert(issue285CommandValues.has('railway police command'), 'railway_police_command is preserved exactly');
assert(!issue285CommandValues.has('railway police'), 'Mobile Operations Management does not collapse into Railway Policing');
assert(railwayPoliceDefinition.training.includes('railway_police'), 'runtime Railway Police definition contains the native education key');

const issue285RespondingUnit = {
    typeId: 108,
    vehicleId: 28501,
    equipment: new Set(),
    labels: new Set(),
    training: issue285Training,
    arrCapabilities: new Set(),
    arrCapabilityKnown: false,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set(),
    staff: api.respondingCrewCapacity(issue285RespondingRow),
    contributionKey: 'vehicle:28501'
};
const issue285RespondingCapacity = api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [issue285RespondingUnit]);
assert.strictEqual(issue285RespondingCapacity.min, 4, 'four proven Railway Police Officers count as Responding');
assert.strictEqual(issue285RespondingCapacity.max, 4, 'responding Railway Police capacity remains exact');
const issue285Coverage = api.coverageRow(
    { key: 'railway-police-officer', requirement: 'Railway Police Officer', missing: 4, group: 'staff', definition: railwayPoliceDefinition },
    api.capacity(0, 0, true),
    issue285RespondingCapacity,
    api.capacity(0, 0, true),
    api.capacity(4, 4, true)
);
assert.strictEqual(issue285Coverage.stillNeededText, '0', 'four responding Railway Police Officers clear a requirement of four');
assert.strictEqual(issue285Coverage.covered, true, 'responding specialist personnel cover the requirement');

const issue285CommandUnit = {
    ...issue285RespondingUnit,
    training: new Set(['railway police command']),
    contributionKey: 'vehicle:28502'
};
assert.strictEqual(api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [issue285CommandUnit]).min, 0, 'Mobile Operations Managers do not satisfy Railway Police Officer demand');
const issue285UnknownUnit = {
    ...issue285RespondingUnit,
    training: new Set(),
    arrCapabilityKnown: false,
    contributionKey: 'vehicle:28503'
};
const issue285Unknown = api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [issue285UnknownUnit]);
assert.strictEqual(issue285Unknown.min, 0, 'unproven responding specialist crew contributes no confirmed capacity');
assert.strictEqual(issue285Unknown.max, null, 'unproven responding specialist crew remains fail-closed rather than confident zero');
}
'''
    runtime = replace_once(runtime, railway_anchor, railway_anchor + railway_tests, "Issue 285 runtime fixtures")
    RUNTIME.write_text(runtime, encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    contract = replace_once(
        contract,
        '        "function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element)",\n',
        '        "function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element, mode = \'\')",\n        "function missionRequirementsLinkedTrainingValues(candidate, vehicleId, element)",\n        "function missionRequirementsRespondingCrewCapacity(element)",\n',
        "Issue 285 structural markers",
    )
    contract = replace_once(
        contract,
        '        "data-personnel-training",\n',
        '        "data-personnel-training",\n        "data-education-key",\n        "data-filterable-by",\n        "td:nth-of-type(5)[sortvalue]",\n',
        "Issue 285 metadata markers",
    )
    railway_contract_anchor = '    assert re.search(r"(?:key|[\'\"]key[\'\"])\\s*:\\s*[\'\"]railway-police-officer[\'\"][^\\n]*(?:training|[\'\"]training[\'\"])\\s*:\\s*\\[[^\\]]*Railway Police", source), "Railway Police personnel must require explicit training evidence"\n'
    railway_contract = '''    assert '"key":"railway-police-officer"' in source and '"railway_police"' in source, "Railway Police must use the native education key"\n    assert "if ((definition?.group || 'vehicles') === 'staff') continue" in source, "vehicle labels must not prove specialist personnel roles"\n    assert "missionRequirementsLinkedTrainingValues(candidate, vehicleId, vehicleElement)" in source, "responding units must resolve linked specialist metadata"\n    assert "missionRequirementsResolvedStaffCapacity(vehicleId, typeId, vehicleElement, mode)" in source, "responding mode must reach the crew resolver"\n    assert "mode === 'responding' ? missionRequirementsRespondingCrewCapacity(element) : null" in source, "canonical responding crew must be acquired explicitly"\n'''
    contract = replace_once(contract, railway_contract_anchor, railway_contract_anchor + railway_contract, "Issue 285 contract assertions")
    CONTRACT.write_text(contract, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    changelog_anchor = "- Police Sergeant personnel now retain `police_sergeant` ARR capability evidence after dispatch, so Responding and On-site counts update through vehicle identity and exact cached crew.\n"
    changelog_addition = (
        "- Railway Police Officer personnel now retain the native `railway_police` qualification across linked vehicle rows and Units Responding.\n"
        "- Canonical responding crew `sortvalue` is accepted only inside `#mission_vehicle_driving`; positional numeric cells elsewhere remain rejected.\n"
        "- `railway_police_command` remains a distinct Mobile Operations Manager qualification and cannot satisfy Railway Police Officer demand.\n"
    )
    changelog = replace_once(changelog, changelog_anchor, changelog_anchor + changelog_addition, "v4.20.19 Railway Police changelog")
    CHANGELOG.write_text(changelog, encoding="utf-8")

    DOC.write_text(
        """# Issue #285 — Railway Police Responding contract\n\n"
        "MissionChief Railway Police Officers use the native education key `railway_police`. "
        "The separate key `railway_police_command` represents Mobile Operations Managers and does not satisfy this requirement.\n\n"
        "The Matrix reads Units Responding from the canonical `#mission_vehicle_driving` table, resolves the stable vehicle identity, "
        "uses the responding crew cell `sortvalue` only within that canonical table, and combines it with explicit or linked qualification evidence.\n\n"
        "Accepted specialist evidence includes MissionChief-native education attributes, compatible filter payloads, and existing discrete bracketed badges. "
        "Generic vehicle captions, custom categories, vehicle type alone and total crew without qualification evidence do not prove Railway Police capacity.\n\n"
        "If crew is known but the specialist qualification cannot be proven, capacity remains bounded/unknown instead of being reported as a confident zero.\n",
        encoding="utf-8",
    )

    DIAGNOSTIC_PACKAGE.unlink(missing_ok=True)
    DIAGNOSTIC_DOC.unlink(missing_ok=True)

    raw = SOURCE.read_bytes()
    DIST_JS.write_bytes(raw)
    DIST_TXT.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    SUMS.write_text(f"{digest}  {DIST_JS.name}\n{digest}  {DIST_TXT.name}\n", encoding="utf-8")

    subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
    subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
    subprocess.run(["bash", ".github/scripts/run_userscript_preflight.sh", "--contracts"], cwd=ROOT, check=True)
    print("Issues #282 and #285 validated Toolkit 4.20.19 candidate prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
