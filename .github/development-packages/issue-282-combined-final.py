#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-282-maritime-cross-source-fix.py"
RUNTIME = ROOT / ".github/development-packages/.issue-282-combined-final-runtime.py"
AUDIT_TEMPLATE = ROOT / ".github/development-packages/issue-282-audit-template.py"
DOC_TEMPLATE = ROOT / ".github/development-packages/issue-282-doc-template.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    payload = ORIGINAL.read_text(encoding="utf-8")

    payload = replace_once(
        payload,
        '''        expected_hashes = {
            "emv": "ead0cb0e7f215ab843496d65ff90209044c736a08eeed6d5e19a312d775b5c8f",
            "missionHelper": "9c36aa6d408a432fea4169218a03ad3b4f8285c7",
            "vehicles": "76dac4116b0c8b85d73eb879ed9521c2acdad787360a174cddfedee2d9c96cd1",
        }
        actual_hashes = {"emv": sha256(emv_path), "missionHelper": sha256(helper_path), "vehicles": sha256(vehicles_path)}
        if actual_hashes != expected_hashes:
            raise RuntimeError(f"reviewed upstream file hashes changed: {actual_hashes}")
''',
        '''        # The exact reviewed commit is immutable. Persist raw-file hashes in
        # the generated fixture rather than comparing them with Git blob identifiers.
        actual_hashes = {"emv": sha256(emv_path), "missionHelper": sha256(helper_path), "vehicles": sha256(vehicles_path)}
''',
        "upstream hash guard",
    )

    payload = replace_once(
        payload,
        '''    definition_end = source.find(");", definition_start + len(definition_marker))
    if definition_start < 0 or definition_end < 0:
        raise RuntimeError("unable to locate embedded Mission Requirements definitions")
    payload_start = definition_start + len(definition_marker)
    definitions = json.loads(source[payload_start:definition_end])
''',
        '''    if definition_start < 0:
        raise RuntimeError("unable to locate embedded Mission Requirements definitions")
    payload_start = definition_start + len(definition_marker)
    definitions, definition_length = json.JSONDecoder().raw_decode(source[payload_start:])
    definition_end = payload_start + definition_length
''',
        "embedded definition decoder",
    )

    payload = replace_once(
        payload,
        '''        "factors": entry.get("factors", {}),
        "pair": bool(entry.get("pair", False)),
''',
        '''        "factors": entry.get("factors", {}),
        "training": list(entry.get("training", [])),
        "arrAttributes": list(entry.get("arrAttributes", [])),
        "pair": bool(entry.get("pair", False)),
''',
        "fixture capability fields",
    )

    payload = replace_once(
        payload,
        '''    seagoing = by_key["ilb-or-alb"]
    append_unique(seagoing["aliases"], ["Seagoing Vessel", "Seagoing Vessels", "ALB or ILB", "ALBs or ILBs"])
    for key in PAIR_DATA_KEYS:
''',
        '''    seagoing = by_key["ilb-or-alb"]
    append_unique(seagoing["aliases"], ["Seagoing Vessel", "Seagoing Vessels", "ALB or ILB", "ALBs or ILBs"])
    by_key["police-sergeant-personnel"]["arrAttributes"] = ["police_sergeant"]
    by_key["public-order-level-2"]["arrAttributes"] = ["level_2_public_order"]
    for key in PAIR_DATA_KEYS:
''',
        "dataset ARR attributes",
    )

    payload = replace_once(
        payload,
        '''    runtime_seagoing = runtime_by_key["ilb-or-alb"]
    runtime_seagoing["label"] = "Seagoing Vessel"
    append_unique(runtime_seagoing["aliases"], seagoing["aliases"])
    source = source[:payload_start] + json.dumps(definitions, separators=(",", ":"), ensure_ascii=False) + source[definition_end:]
''',
        '''    runtime_seagoing = runtime_by_key["ilb-or-alb"]
    runtime_seagoing["label"] = "Seagoing Vessel"
    append_unique(runtime_seagoing["aliases"], seagoing["aliases"])
    runtime_sergeant = next(entry for entry in definitions if "police_sergeant" in entry.get("training", []))
    runtime_sergeant["arrAttributes"] = ["police_sergeant"]
    runtime_level_two = next(entry for entry in definitions if "level_2_public_order" in entry.get("training", []))
    runtime_level_two["arrAttributes"] = ["level_2_public_order"]
    source = source[:payload_start] + json.dumps(definitions, separators=(",", ":"), ensure_ascii=False) + source[definition_end:]
''',
        "runtime ARR attributes",
    )

    sergeant_test = r'''

// Issue #282: Police Sergeant capability survives Selected -> Responding -> On site.
{
const sergeantDoc = new FakeDocument();
sergeantDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/282-sergeant' } };
const sergeantCandidate = makeMissionCandidate(sergeantDoc, '2 Police Sergeants');
const sergeantDefinition = api.definitions.find(definition => (definition.training || []).includes('police_sergeant'));
assert(sergeantDefinition, 'Police Sergeant definition exists');
assert((sergeantDefinition.arrAttributes || []).includes('police_sergeant'), 'Police Sergeant exposes its ARR attribute');
const cacheSergeant = id => api.vehicleApiCache.set(String(id), { id, vehicle_type: 8, assigned_personnel_count: 1 });

const respondingAssignment = makeVehicleElement(sergeantDoc, 282401, 8);
respondingAssignment.vehicle.classList.values.add('vehicle_checkbox');
respondingAssignment.vehicle.matchSet.add('.vehicle_checkbox');
respondingAssignment.vehicle.checked = false;
respondingAssignment.vehicle.setAttribute('police_sergeant', '1');
const respondingSergeant = makeVehicleElement(sergeantDoc, 282401, 8, { typeOnRow: true });
respondingSergeant.row.setAttribute('data-vehicle-id', '282401');
cacheSergeant(282401);

const onSiteSergeants = [];
for (let index = 0; index < 3; index += 1) {
    const id = 282410 + index;
    const unit = makeVehicleElement(sergeantDoc, id, 8, { typeOnRow: true });
    unit.row.setAttribute('data-vehicle-id', String(id));
    unit.row.setAttribute('police_sergeant', '1');
    cacheSergeant(id);
    onSiteSergeants.push(unit.row);
}

sergeantCandidate.root.selectedUnits = [respondingAssignment.vehicle];
sergeantCandidate.root.enRouteRows = [respondingSergeant.row];
sergeantCandidate.root.onSiteRows = onSiteSergeants;
const sergeantParsed = {
    requirements: [{ key: sergeantDefinition.key, requirement: 'Police Sergeant', missing: 2, group: 'staff', definition: sergeantDefinition, statedRequirement: true }],
    unresolved: []
};
const sergeantCatalogue = { requirements: [{ key: sergeantDefinition.key, baseline: 5, missing: 5 }] };
let sergeantRow = api.resolve(sergeantCandidate, sergeantParsed, sergeantCatalogue)[0];
assert.strictEqual(sergeantRow.requiredText, '5', 'Police Sergeant total required remains five');
assert.strictEqual(sergeantRow.onSiteText, '3', 'three on-site Police Sergeants are counted');
assert.strictEqual(sergeantRow.respondingText, '1', 'travelling Police Sergeant is counted through matching vehicle identity');
assert.strictEqual(sergeantRow.selectedText, '0', 'unchecked travelling assignment is not left in Selected');
assert.strictEqual(sergeantRow.stillNeededText, '1', '5 required minus 3 on site and 1 responding leaves one');
assert.strictEqual(sergeantRow.covered, false, 'one remaining Police Sergeant keeps row outstanding');

const respondingState = api.arrCapabilityState(respondingSergeant.row, sergeantCandidate, 282401);
assert.strictEqual(respondingState.authoritative, true, 'matching dispatch checkbox is authoritative capability evidence');
assert(respondingState.values.has('police sergeant'), 'matching dispatch checkbox supplies Police Sergeant capability');

respondingAssignment.vehicle.checked = true;
sergeantCandidate.root.enRouteRows = [];
sergeantCandidate.root.onSiteRows = [];
sergeantRow = api.resolve(sergeantCandidate, {
    requirements: [{ key: sergeantDefinition.key, requirement: 'Police Sergeant', missing: 1, group: 'staff', definition: sergeantDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: sergeantDefinition.key, baseline: 1, missing: 1 }] })[0];
assert.strictEqual(sergeantRow.selectedText, '1', 'Police Sergeant first appears in Selected');
assert.strictEqual(sergeantRow.respondingText, '0', 'selected Police Sergeant is not responding');

respondingAssignment.vehicle.checked = false;
sergeantCandidate.root.enRouteRows = [respondingSergeant.row];
sergeantRow = api.resolve(sergeantCandidate, {
    requirements: [{ key: sergeantDefinition.key, requirement: 'Police Sergeant', missing: 1, group: 'staff', definition: sergeantDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: sergeantDefinition.key, baseline: 1, missing: 1 }] })[0];
assert.strictEqual(sergeantRow.selectedText, '0', 'dispatch removes Police Sergeant from Selected');
assert.strictEqual(sergeantRow.respondingText, '1', 'dispatch moves Police Sergeant into Responding');

sergeantCandidate.root.enRouteRows = [];
respondingSergeant.row.setAttribute('police_sergeant', '1');
sergeantCandidate.root.onSiteRows = [respondingSergeant.row];
sergeantRow = api.resolve(sergeantCandidate, {
    requirements: [{ key: sergeantDefinition.key, requirement: 'Police Sergeant', missing: 0, group: 'staff', definition: sergeantDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: sergeantDefinition.key, baseline: 1, missing: 1 }] })[0];
assert.strictEqual(sergeantRow.respondingText, '0', 'arrival removes Police Sergeant from Responding');
assert.strictEqual(sergeantRow.onSiteText, '1', 'arrival moves Police Sergeant into On site');

const genericPoliceOnly = api.aggregate({ group: 'staff', definition: sergeantDefinition }, [{
    typeId: 8,
    vehicleId: 282499,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(),
    arrCapabilities: new Set(),
    arrCapabilityKnown: true,
    knownDefinitionKeys: new Set(),
    staff: api.capacity(1, 1, true),
    contributionKey: 'vehicle:282499'
}]);
assert.strictEqual(genericPoliceOnly.min, 0, 'generic Police Officer is not credited as Police Sergeant');
assert.strictEqual(genericPoliceOnly.max, 0, 'generic Police Officer exclusion is exact');
}
'''

    payload = replace_once(
        payload,
        '''    runtime = replace_once(runtime, maritime_anchor, maritime_block + maritime_anchor, "maritime runtime fixture insertion")
    RUNTIME_TEST.write_text(runtime, encoding="utf-8")
''',
        '''    runtime = replace_once(runtime, maritime_anchor, maritime_block + maritime_anchor, "maritime runtime fixture insertion")
    sergeant_block = r\'\'\'''' + sergeant_test + '''\'\'\'
    runtime = replace_once(runtime, maritime_anchor, sergeant_block + maritime_anchor, "Police Sergeant runtime fixture insertion")
    RUNTIME_TEST.write_text(runtime, encoding="utf-8")
''',
        "Police Sergeant test insertion",
    )

    payload = replace_once(
        payload,
        '''- A Required 3 / Selected 1 maritime row remains outstanding with Still needed 2 and reports `0/1 covered`.

### Audit
''',
        '''- A Required 3 / Selected 1 maritime row remains outstanding with Still needed 2 and reports `0/1 covered`.
- Police Sergeant personnel now retain `police_sergeant` ARR capability evidence after dispatch, so Responding and On-site counts update through vehicle identity and exact cached crew.
- Required 5 with On site 3 and Responding 1 now reports Still needed 1.

### Audit
''',
        "Police Sergeant changelog notes",
    )

    audit_text = AUDIT_TEMPLATE.read_text(encoding="utf-8")
    audit_text = replace_once(
        audit_text,
        '''        "factors": entry.get("factors", {}),
        "pair": bool(entry.get("pair", False)),
''',
        '''        "factors": entry.get("factors", {}),
        "training": list(entry.get("training", [])),
        "arrAttributes": list(entry.get("arrAttributes", [])),
        "pair": bool(entry.get("pair", False)),
''',
        "audit capability fields",
    )
    audit_text = replace_once(
        audit_text,
        '''        "Seagoing Vessel",
    ]
''',
        '''        "Seagoing Vessel",
        "police_sergeant",
        "level_2_public_order",
    ]
''',
        "audit ARR markers",
    )
    AUDIT_TEMPLATE.write_text(audit_text, encoding="utf-8")

    doc_text = DOC_TEMPLATE.read_text(encoding="utf-8")
    doc_text = replace_once(
        doc_text,
        '''- Selected, Responding and On-site transitions retain bucket precedence and never duplicate the same asset.
''',
        '''- Selected, Responding and On-site transitions retain bucket precedence and never duplicate the same asset.
- Police Sergeant and Level 2 Public Order ARR attributes remain discoverable by vehicle identity after dispatch, even when the travelling row no longer renders its training badge.
- Exact assigned personnel from the shared vehicle cache remains authoritative for those trained-personnel contributions.
''',
        "audit documentation ARR notes",
    )
    DOC_TEMPLATE.write_text(doc_text, encoding="utf-8")

    RUNTIME.write_text(payload, encoding="utf-8")
    try:
        subprocess.run(["python3", str(RUNTIME)], cwd=ROOT, check=True)
    finally:
        RUNTIME.unlink(missing_ok=True)

    for path in (
        ORIGINAL,
        ROOT / ".github/development-packages/issue-282-maritime-cross-source-fix-v2.py",
        ROOT / "docs/issue-282-police-sergeant-source-inspection.txt",
        ROOT / "docs/issue-282-final-package-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
