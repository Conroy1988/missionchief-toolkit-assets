#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src" / "data" / "mission-requirements-en_GB.json"
CROSS_SOURCE = ROOT / ".github" / "fixtures" / "mission-requirements-cross-source-en_GB.json"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
OLD_VERSION = "4.20.34"
NEW_VERSION = "4.20.35"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


# Canonical UK capability data.
data = json.loads(DATA.read_text(encoding="utf-8"))
vehicle_requirements = data["vehicleRequirements"]
if any(entry.get("key") == "rescue-support-vehicle" for entry in vehicle_requirements):
    raise RuntimeError("rescue-support-vehicle already exists in canonical capability data")
anchor_index = next(
    index for index, entry in enumerate(vehicle_requirements)
    if entry.get("key") == "rescue-support-unit-or-rescue-pump"
)
rescue_support = {
    "key": "rescue-support-vehicle",
    "aliases": ["Rescue Support Vehicle", "Rescue Support Vehicles"],
    "types": [4, 16, 38, 43],
}
vehicle_requirements.insert(anchor_index + 1, rescue_support)
DATA.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

# Runtime definition and version.
source = SOURCE.read_text(encoding="utf-8")
source = replace_once(
    source,
    f"// @version      {OLD_VERSION}",
    f"// @version      {NEW_VERSION}",
    "userscript metadata version",
)
source = replace_once(
    source,
    f"version: '{OLD_VERSION}'",
    f"version: '{NEW_VERSION}'",
    "runtime version",
)
runtime_anchor = '{"key":"rsu-or-rescue-pump","label":"Rescue Support Unit or Rescue Pump","aliases":["Rescue Support Unit or Rescue Pump","Rescue Support Units or Rescue Pumps"],"types":[4,16,38,43]},'
runtime_definition = '{"key":"rescue-support-vehicle","label":"Rescue Support Vehicle","aliases":["Rescue Support Vehicle","Rescue Support Vehicles"],"types":[4,16,38,43]},'
source = replace_once(
    source,
    runtime_anchor,
    runtime_anchor + runtime_definition,
    "standalone Rescue Support Vehicle runtime definition",
)
SOURCE.write_text(source, encoding="utf-8")
for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    path.write_text(source, encoding="utf-8")

# Cross-source review contract: current MissionChief catalogue label, intentionally
# ahead of the pinned LSSM alias catalogue.
cross_source = json.loads(CROSS_SOURCE.read_text(encoding="utf-8"))
authoritative = cross_source["authoritativeLabels"]
if any(item.get("capability") == "rescue-support-vehicle" for item in authoritative):
    raise RuntimeError("Rescue Support Vehicle authoritative label already exists")
authoritative.append({
    "canonicalLabel": "Rescue Support Vehicle",
    "capability": "rescue-support-vehicle",
    "labels": ["Rescue Support Vehicle", "Rescue Support Vehicles"],
    "pair": False,
    "sources": ["missionchief.missionInfo"],
    "types": [4, 16, 38, 43],
})
capabilities = cross_source["capabilities"]
if any(item.get("key") == "rescue-support-vehicle" for item in capabilities):
    raise RuntimeError("Rescue Support Vehicle cross-source capability already exists")
capability_anchor = next(
    index for index, item in enumerate(capabilities)
    if item.get("key") == "rescue-support-unit-or-rescue-pump"
)
capabilities.insert(capability_anchor + 1, {
    "aliases": ["Rescue Support Vehicle", "Rescue Support Vehicles"],
    "arrAttributes": [],
    "conditionalVehicles": {},
    "equipment": [],
    "factors": {},
    "key": "rescue-support-vehicle",
    "pair": False,
    "training": [],
    "types": [4, 16, 38, 43],
})
CROSS_SOURCE.write_text(json.dumps(cross_source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Exact Issue #349 regression: catalogue parsing, reconciliation, alias separation,
# eligibility and all operational buckets.
runtime_test = RUNTIME_TEST.read_text(encoding="utf-8")
issue349_test = r'''
// Issue #349: the official railway-station mission lists Rescue Support Vehicles,
// PRVs and SRVs as three independent requirement families.
const issue349Catalogue = [
    api.catalogueRequirement('Required Rescue Support Vehicles', '3'),
    api.catalogueRequirement('Required PRVs', '1'),
    api.catalogueRequirement('Required SRVs', '1')
];
assert(issue349Catalogue.every(Boolean), 'Issue #349 catalogue rows all parse');
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(issue349Catalogue.map(item => ({ key: item.key, label: item.requirement, missing: item.missing })))),
    [
        { key: 'rescue-support-vehicle', label: 'Rescue Support Vehicle', missing: 3 },
        { key: 'primary-response', label: 'Primary Response Vehicle', missing: 1 },
        { key: 'secondary-response', label: 'Secondary Response Vehicle', missing: 1 }
    ],
    'Issue #349 keeps Rescue Support Vehicle, PRV and SRV separate'
);
const issue349Reconciled = api.reconcileCatalogue(
    { requirements: [], unresolved: [] },
    { requirements: issue349Catalogue },
    'ready',
    true
);
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(issue349Reconciled.requirements.map(item => item.key))),
    ['rescue-support-vehicle', 'primary-response', 'secondary-response'],
    'Issue #349 catalogue reconciliation retains all three requirement rows'
);
const issue349Definition = api.definitions.find(item => item.key === 'rescue-support-vehicle');
assert(issue349Definition, 'Issue #349 Rescue Support Vehicle definition exists');
assert.deepStrictEqual(JSON.parse(JSON.stringify(issue349Definition.types)), [4, 16, 38, 43]);
const issue349Unit = typeId => ({
    typeId,
    vehicleId: 349000 + typeId,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(),
    arrCapabilities: new Set(),
    arrCapabilityKnown: true,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set(),
    staff: null,
    contributionKey: `vehicle:349-${typeId}`
});
const issue349Requirement = {
    key: issue349Definition.key,
    requirement: issue349Definition.label,
    missing: 1,
    group: 'vehicles',
    definition: issue349Definition
};
for (const typeId of [4, 16, 38, 43]) {
    const capacity = api.aggregate(issue349Requirement, [issue349Unit(typeId)]);
    assert.strictEqual(capacity.min, 1, `Issue #349 type ${typeId} contributes to Rescue Support Vehicle`);
    assert.strictEqual(capacity.max, 1, `Issue #349 type ${typeId} contribution is exact`);
    const zero = api.capacity(0, 0, true);
    const required = api.capacity(1, 1, true);
    for (const [bucket, selected, responding, onSite] of [
        ['selected', capacity, zero, zero],
        ['responding', zero, capacity, zero],
        ['on-site', zero, zero, capacity]
    ]) {
        const row = api.coverageRow(issue349Requirement, selected, responding, onSite, required);
        assert.strictEqual(row.covered, true, `Issue #349 ${bucket} Rescue Support Vehicle covers the row`);
        assert.strictEqual(row.stillNeededText, '0', `Issue #349 ${bucket} Rescue Support Vehicle clears still needed`);
    }
}
for (const typeId of [0, 1, 27, 28, 47]) {
    const capacity = api.aggregate(issue349Requirement, [issue349Unit(typeId)]);
    assert.strictEqual(capacity.min, 0, `Issue #349 type ${typeId} is not a standalone Rescue Support Vehicle`);
    assert.strictEqual(capacity.max, 0, `Issue #349 type ${typeId} is definitively excluded`);
}

'''
runtime_test = replace_once(
    runtime_test,
    "for (const group of crossSourceFixture.authoritativeLabels) {",
    issue349_test + "for (const group of crossSourceFixture.authoritativeLabels) {",
    "Issue #349 runtime regression insertion",
)
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

# Release documentation.
changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = f"""## [{NEW_VERSION}] - 2026-07-22

### Critical Mission Requirements fix
- Added standalone `Rescue Support Vehicle` and `Rescue Support Vehicles` requirement aliases.
- Mapped the requirement to the reviewed rescue-support vehicle types `4`, `16`, `38`, and `43`.
- Preserved PRV type `27` and SRV type `28` as independent requirement families.
- Added an exact railway-station mission regression covering catalogue parsing, reconciliation, selected, responding, on-site and still-needed counts.

### Benefit
- Rescue Support Vehicle requirements now receive complete Matrix tracking instead of unresolved `?` values.

### Compatibility
- Existing composite rescue-support requirements, covered-row visibility, vehicle selection, dispatch, themes, layout and unrelated mission logic are unchanged.

"""
changelog_path.write_text(
    replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog insertion"),
    encoding="utf-8",
)

help_path = ROOT / "help" / "index.html"
help_text = help_path.read_text(encoding="utf-8")
if OLD_VERSION not in help_text:
    raise RuntimeError("help page does not contain the current version")
help_path.write_text(help_text.replace(OLD_VERSION, NEW_VERSION), encoding="utf-8")

# Preserve the permanent main-style source-headroom arithmetic. The runtime
# definition is inserted on the existing single-line definition inventory.
headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
source_lines = len(source.splitlines())
headroom["candidateVersion"] = NEW_VERSION
headroom["candidateSourceLines"] = source_lines
headroom["recoveredSourceLines"] = headroom["originalSourceLines"] - source_lines
headroom["candidateSourceSha256"] = hashlib.sha256(source.encode()).hexdigest()
headroom["invariant"] = (
    f'The reviewed compact stylesheet retains {headroom["recoveredSourceLines"]} recovered source lines '
    "while standalone Rescue Support Vehicle tracking remains fixture-backed and managed runtime budgets remain unchanged."
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

# Focused contracts before the repository-wide validator executes.
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
subprocess.check_call(["node", str(RUNTIME_TEST)], cwd=ROOT, env=env)
subprocess.check_call([sys.executable, str(ROOT / ".github" / "scripts" / "audit_lssm_requirement_compatibility.py")], cwd=ROOT, env=env)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

print(
    f"Prepared Toolkit {NEW_VERSION}; Rescue Support Vehicle types=[4,16,38,43]; "
    f"source lines={source_lines}; recovered={headroom['recoveredSourceLines']}"
)
