#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
SHA_FILE = ROOT / "dist" / "SHA256SUMS.txt"
MANIFEST = ROOT / "dist" / "release-manifest.json"
CAPABILITIES = ROOT / "src" / "data" / "mission-requirements-en_GB.json"
FIXTURE = ROOT / ".github" / "fixtures" / "mission-requirements-contract.json"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
CONTRACT_DOC = ROOT / "docs" / "issue-257-combined-vehicle-capability-contract.md"

OLD_VERSION = "4.20.11"
NEW_VERSION = "4.20.12"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def folded(value: str) -> str:
    return " ".join(str(value).split()).casefold()


combined_definitions = [
    {
        "key": "police-helicopter-or-drone",
        "label": "Police Helicopter or Drone",
        "aliases": ["Police Helicopter or Drone", "Police Helicopters or Drones"],
        "types": [11, 89, 90, 91],
        "equipment": ["drone"],
    },
    {
        "key": "riv-or-major-foam",
        "label": "RIV or Major Foam Tender",
        "aliases": ["RIV or Major Foam Tender", "RIVs or Major Foam Tenders"],
        "types": [75, 76],
    },
    {
        "key": "fire-engine-or-major-foam",
        "label": "Fire Engine or Major Foam Tender",
        "aliases": ["Fire Engine or Major Foam Tender", "Fire Engines or Major Foam Tenders"],
        "types": [0, 1, 16, 17, 26, 37, 38, 47, 75],
    },
    {
        "key": "fire-engine-riv-or-major-foam",
        "label": "Fire Engine, RIV or Major Foam Tender",
        "aliases": ["Fire Engine, RIV or Major Foam Tender", "Fire Engines, RIVs or Major Foam Tenders"],
        "types": [0, 1, 16, 17, 26, 37, 38, 47, 75, 76],
    },
    {
        "key": "mountain-or-sar-4x4",
        "label": "Mountain Rescue 4x4 or SAR 4x4",
        "aliases": ["Mountain Rescue 4x4 or SAR 4x4", "Mountain Rescue 4x4s or SAR 4x4s"],
        "types": [93, 99],
    },
    {
        "key": "rrv-or-specialist-paramedic",
        "label": "RRV or Specialist Paramedic RRV",
        "aliases": ["RRV or Specialist Paramedic RRV", "RRVs or Specialist Paramedic RRVs"],
        "types": [10, 94, 96],
    },
]

fire_officer_aliases = [
    "Fire Officer or Airfield Firefighting Command Vehicle",
    "Fire Officers or Airfield Firefighting Command Vehicles",
]
command_aliases = [
    "ICCU or Ambulance Control Unit or Airfield Firefighting Command Vehicle",
    "ICCU or Ambulance Control Units or Airfield Firefighting Command Vehicles",
]

source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {OLD_VERSION}", f"// @version      {NEW_VERSION}", "metadata version")
source = replace_once(source, f"version: '{OLD_VERSION}',", f"version: '{NEW_VERSION}',", "runtime version")

prefix = "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze(["
if any(f'\"key\":\"{definition["key"]}\"' in source for definition in combined_definitions):
    raise AssertionError("Issue #257 combined runtime definitions already exist")
insert = "".join(json.dumps(definition, ensure_ascii=False, separators=(",", ":")) + "," for definition in combined_definitions)
source = replace_once(source, prefix, prefix + insert, "combined runtime definition insertion")

old_fire_officer = '{"key":"fire-officer","label":"Fire Officer","aliases":["Fire Officer","Fire Officers"],"types":[3,15,44,77]}'
new_fire_officer = json.dumps(
    {
        "key": "fire-officer",
        "label": "Fire Officer",
        "aliases": ["Fire Officer", "Fire Officers", *fire_officer_aliases],
        "types": [3, 15, 44, 77],
    },
    separators=(",", ":"),
)
source = replace_once(source, old_fire_officer, new_fire_officer, "Fire Officer combined aliases")

old_command = '{"key":"iccu-or-control","label":"ICCU or Ambulance Control Unit","aliases":["ICCU or Ambulance Control Unit","ICCU or Ambulance Control Units"],"types":[15,31,44,77]}'
new_command = json.dumps(
    {
        "key": "iccu-or-control",
        "label": "ICCU or Ambulance Control Unit",
        "aliases": ["ICCU or Ambulance Control Unit", "ICCU or Ambulance Control Units", *command_aliases],
        "types": [15, 31, 44, 77],
    },
    separators=(",", ":"),
)
source = replace_once(source, old_command, new_command, "command combined aliases")
SOURCE.write_text(source, encoding="utf-8")

# Keep canonical source and both installable files byte-identical.
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")

digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
SHA_FILE.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n"
    f"{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
manifest["version"] = NEW_VERSION
manifest["sha256"] = digest
manifest["bytes"] = len(source.encode("utf-8"))
manifest["lines"] = len(source.splitlines())
manifest.setdefault("metadata", {})["runtimeVersion"] = NEW_VERSION
manifest["baselineHashMatch"] = None
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

capability_data = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
vehicle_requirements = capability_data["vehicleRequirements"]
by_key = {entry["key"]: entry for entry in vehicle_requirements}

def add_aliases(key: str, aliases: list[str]) -> None:
    entry = by_key.get(key)
    if not entry:
        raise AssertionError(f"UK capability entry not found: {key}")
    existing = {folded(alias) for alias in entry.get("aliases", [])}
    for alias in aliases:
        if folded(alias) not in existing:
            entry.setdefault("aliases", []).append(alias)
            existing.add(folded(alias))

add_aliases("fire-officer", fire_officer_aliases)
add_aliases("iccu-or-ambulance-control-unit", command_aliases)

new_data_entries = [
    {
        "key": "police-helicopter-or-drone",
        "aliases": ["Police Helicopter or Drone", "Police Helicopters or Drones"],
        "types": [11, 89, 90, 91],
        "equipment": ["drone"],
    },
    {
        "key": "riv-or-major-foam-tender",
        "aliases": ["RIV or Major Foam Tender", "RIVs or Major Foam Tenders"],
        "types": [75, 76],
    },
    {
        "key": "fire-engine-or-major-foam-tender",
        "aliases": ["Fire Engine or Major Foam Tender", "Fire Engines or Major Foam Tenders"],
        "types": [0, 1, 16, 17, 26, 37, 38, 47, 75],
    },
    {
        "key": "fire-engine-riv-or-major-foam-tender",
        "aliases": ["Fire Engine, RIV or Major Foam Tender", "Fire Engines, RIVs or Major Foam Tenders"],
        "types": [0, 1, 16, 17, 26, 37, 38, 47, 75, 76],
    },
    {
        "key": "mountain-rescue-4x4-or-sar-4x4",
        "aliases": ["Mountain Rescue 4x4 or SAR 4x4", "Mountain Rescue 4x4s or SAR 4x4s"],
        "types": [93, 99],
    },
    {
        "key": "rrv-or-specialist-paramedic-rrv",
        "aliases": ["RRV or Specialist Paramedic RRV", "RRVs or Specialist Paramedic RRVs"],
        "types": [10, 94, 96],
    },
]
if any(entry["key"] in by_key for entry in new_data_entries):
    raise AssertionError("Issue #257 combined UK capability entries already exist")
vehicle_requirements.extend(new_data_entries)

aliases_seen: dict[str, str] = {}
for group_name in ("vehicleRequirements", "staffRequirements"):
    for entry in capability_data[group_name]:
        for alias in entry.get("aliases", []):
            key = folded(alias)
            if key in aliases_seen:
                raise AssertionError(f"duplicate UK capability alias: {alias} ({aliases_seen[key]} and {entry['key']})")
            aliases_seen[key] = entry["key"]
CAPABILITIES.write_text(json.dumps(capability_data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
if "combinedVehicleCapabilities" in fixture:
    raise AssertionError("Issue #257 combined capability fixture already exists")
fixture["combinedVehicleCapabilities"] = [
    *combined_definitions,
    {
        "key": "fire-officer",
        "aliases": fire_officer_aliases,
        "types": [3, 15, 44, 77],
    },
    {
        "key": "iccu-or-control",
        "aliases": command_aliases,
        "types": [15, 31, 44, 77],
    },
]
FIXTURE.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

runtime_test = RUNTIME_TEST.read_text(encoding="utf-8")
runtime_test = replace_once(
    runtime_test,
    f"version: '{OLD_VERSION}'",
    f"version: '{NEW_VERSION}'",
    "Mission Requirements runtime fixture version",
)
runtime_test = replace_once(
    runtime_test,
    "    cataloguePersonnel: missionRequirementsCataloguePersonnelRequirements,\n",
    "    cataloguePersonnel: missionRequirementsCataloguePersonnelRequirements,\n"
    "    catalogueRequirement: missionRequirementsCatalogueRequirement,\n",
    "catalogue requirement test export",
)
issue257_tests = r'''

// Issue #257: official combined Mission Info labels use capability unions.
{
const combinedCapabilities = fixture.combinedVehicleCapabilities;
for (const capability of combinedCapabilities) {
    const definition = api.definitions.find(item => item.key === capability.key);
    assert(definition, `${capability.key}: runtime definition exists`);
    assert.deepStrictEqual(
        Array.from(definition.types || []).sort((a, b) => a - b),
        Array.from(capability.types || []).sort((a, b) => a - b),
        `${capability.key}: accepted vehicle types`
    );
    assert.deepStrictEqual(
        Array.from(definition.equipment || []).sort(),
        Array.from(capability.equipment || []).sort(),
        `${capability.key}: accepted equipment`
    );
    for (const alias of capability.aliases) {
        const parsed = api.parseText(`1 ${alias}`, 'vehicles');
        assert.strictEqual(parsed.remaining, '', `${capability.key}: parser consumes ${alias}`);
        assert.strictEqual(parsed.requirements.length, 1, `${capability.key}: parser creates one row for ${alias}`);
        assert.strictEqual(parsed.requirements[0].key, capability.key, `${capability.key}: parser selects the capability union for ${alias}`);
        const catalogueRequirement = api.catalogueRequirement(alias, '1');
        assert(catalogueRequirement, `${capability.key}: catalogue requirement exists for ${alias}`);
        assert.strictEqual(catalogueRequirement.key, capability.key, `${capability.key}: catalogue requirement uses capability union for ${alias}`);
        assert.strictEqual(catalogueRequirement.catalogueKnown, true, `${capability.key}: catalogue requirement is countable for ${alias}`);
        assert.notStrictEqual(catalogueRequirement.definition.countable, false, `${capability.key}: catalogue requirement is not forced unknown for ${alias}`);
    }
    for (const typeId of capability.types || []) {
        const capacity = api.aggregate(
            { group: 'vehicles', definition },
            [{ typeId, equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), staff: null, contributionKey: `vehicle:${capability.key}:${typeId}` }]
        );
        assert.strictEqual(capacity.min, 1, `${capability.key}: vehicle type ${typeId} contributes one`);
        assert.strictEqual(capacity.max, 1, `${capability.key}: vehicle type ${typeId} remains exact`);
    }
    for (const equipment of capability.equipment || []) {
        const capacity = api.aggregate(
            { group: 'vehicles', definition },
            [{ typeId: -1, equipment: new Set([equipment]), labels: new Set(), knownDefinitionKeys: new Set(), staff: null, contributionKey: `equipment:${capability.key}:${equipment}` }]
        );
        assert.strictEqual(capacity.min, 1, `${capability.key}: equipment ${equipment} contributes one`);
        assert.strictEqual(capacity.max, 1, `${capability.key}: equipment ${equipment} remains exact`);
    }
}

const doc = new FakeDocument();
doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/25701' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const candidate = makeMissionCandidate(doc, '');
candidate.missionId = 25701;
const definition = api.definitions.find(item => item.key === 'police-helicopter-or-drone');
const requirement = { ...api.catalogueRequirement('Police Helicopters or Drones', '1'), statedRequirement: true };
const parsed = { requirements: [requirement], unresolved: [] };
const catalogue = { requirements: [{ key: requirement.key, baseline: 1, missing: 1 }] };
const resolveRow = () => api.resolve(candidate, parsed, catalogue).find(item => item.key === requirement.key);

for (const typeId of [11, 89, 90, 91]) {
    const selected = makeVehicleElement(doc, 2570100 + typeId, typeId);
    candidate.root.selectedUnits = [selected.vehicle];
    const row = resolveRow();
    assert.strictEqual(row.selectedMin, 1, `selected vehicle type ${typeId} fulfils the combined row`);
    assert.strictEqual(row.selectedMax, 1, `selected vehicle type ${typeId} remains exact`);
    assert.strictEqual(row.stillNeededText, '0', `selected vehicle type ${typeId} clears the shortage`);
}

const equipmentOnly = makeVehicleElement(doc, 2570198, -1, { equipment: ['drone'] });
candidate.root.selectedUnits = [equipmentOnly.vehicle];
let row = resolveRow();
assert.strictEqual(row.selectedMin, 1, 'selected drone equipment fulfils the combined row without a known vehicle type');
assert.strictEqual(row.stillNeededText, '0', 'selected drone equipment clears the shortage');

const dualEvidence = makeVehicleElement(doc, 2570191, 91, { equipment: ['drone'] });
candidate.root.selectedUnits = [dualEvidence.vehicle];
row = resolveRow();
assert.strictEqual(row.selectedMin, 1, 'one police drone with both type and equipment evidence counts once');
assert.strictEqual(row.selectedMax, 1, 'dual police-drone evidence does not widen or double-count capacity');

candidate.root.selectedUnits = [];
row = resolveRow();
assert.strictEqual(row.selectedMin, 0, 'deselecting the combined-capability unit removes Selected capacity');
assert.strictEqual(row.stillNeededText, '1', 'deselecting restores the shortage');

const responding = makeVehicleElement(doc, 2570211, 11, { typeOnRow: true });
responding.row.matchSet.add('tr');
responding.row.setAttribute('data-vehicle-id', '2570211');
candidate.root.enRouteRows = [responding.row];
row = resolveRow();
assert.strictEqual(row.respondingMin, 1, 'responding Police Helicopter fulfils the combined row');
assert.strictEqual(row.stillNeededText, '0', 'responding Police Helicopter clears the shortage');

candidate.root.enRouteRows = [];
const onSite = makeVehicleElement(doc, 2570291, 91, { typeOnRow: true, equipment: ['drone'] });
onSite.row.matchSet.add('tr');
onSite.row.setAttribute('data-vehicle-id', '2570291');
candidate.root.onSiteRows = [onSite.row];
row = resolveRow();
assert.strictEqual(row.onSiteMin, 1, 'on-site Police Drone fulfils the combined row');
assert.strictEqual(row.onSiteMax, 1, 'on-site Police Drone remains exact');
assert.strictEqual(row.stillNeededText, '0', 'on-site Police Drone clears the shortage');

candidate.root.onSiteRows = [];
row = resolveRow();
assert.strictEqual(row.stillNeededText, '1', 'removing the on-site unit restores the shortage');
assert.strictEqual(definition.equipment.includes('drone'), true, 'combined Police Helicopter or Drone definition retains drone equipment capability');
}
'''
runtime_test = replace_once(
    runtime_test,
    "\nconsole.log('Mission requirements runtime fixtures passed');",
    issue257_tests + "\nconsole.log('Mission requirements runtime fixtures passed');",
    "Issue #257 runtime regression anchor",
)
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
section = f'''## [{NEW_VERSION}] - 2026-07-20

### Fixed
- Resolved official combined Mission Info vehicle requirements through explicit capability unions instead of rendering unknown `?` coverage.
- Police Helicopters or Drones now accepts Police Helicopter type 11, drone vehicle types 89–91 and `drone` equipment across Selected, Responding and On site.
- Added the remaining verified UK combined Fire, Airfield, Mountain/SAR and paramedic vehicle labels so any accepted constituent vehicle updates the same Matrix row.

### Safety
- Existing vehicle-type, equipment, factor and trailer de-duplication remains unchanged.
- Unsupported or probabilistic Mission Info metadata continues to fail closed as unknown rather than being guessed.

### Validation
- Added fixture-backed parser, catalogue, selected, responding, on-site, deselection and dual-evidence de-duplication regressions.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + section, "v4.20.12 changelog section")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
if OLD_VERSION not in help_text:
    raise AssertionError("Help Centre current-version marker was not found")
HELP.write_text(help_text.replace(OLD_VERSION, NEW_VERSION), encoding="utf-8")

CONTRACT_DOC.write_text(
    """# Issue #257 — combined Mission Info vehicle capability contract

Official Mission Info labels that describe alternatives are represented as one requirement with a union of accepted MissionChief vehicle type IDs and equipment capabilities.

The Matrix uses the same resolver for Selected, Responding and On site. A unit contributes once when any accepted type, equipment capability or proven label matches. Multiple pieces of evidence on the same vehicle do not create multiple contributions, and vehicle identity or trailer-pair keys continue to prevent duplicate representations from being counted twice.

The UK combined capability fixture covers Police Helicopters or Drones, RIVs or Major Foam Tenders, Fire Engines or Major Foam Tenders, Fire Engines/RIVs/Major Foam Tenders, Fire Officers or Airfield Firefighting Command Vehicles, ICCU/Ambulance Control Units or Airfield Firefighting Command Vehicles, Mountain Rescue 4x4 or SAR 4x4, and RRV or Specialist Paramedic RRV.

Unknown labels remain non-countable. Probabilistic catalogue requirements remain uncertain until live evidence proves coverage.
""",
    encoding="utf-8",
)

print(f"Issue #257 v{NEW_VERSION} package applied; sha256={digest}")
