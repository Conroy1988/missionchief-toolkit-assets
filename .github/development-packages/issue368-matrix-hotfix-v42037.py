#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
DATA = ROOT / "src" / "data" / "mission-requirements-en_GB.json"
CROSS_SOURCE = ROOT / ".github" / "fixtures" / "mission-requirements-cross-source-en_GB.json"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.20.36", "// @version      4.20.37", "userscript metadata version")
source = replace_once(source, "version: '4.20.36'", "version: '4.20.37'", "runtime version")

source = replace_once(
    source,
    '{"key":"public-order-level-1","label":"Level 1 Public Order Officer","aliases":["Level 1 Public Order Officer","Level 1 Public Order Officers"],"group":"staff","types":[],"countable":false}',
    '{"key":"public-order-level-1","label":"Level 1 Public Order Officer","aliases":["Level 1 Public Order Officer","Level 1 Public Order Officers"],"group":"staff","types":[],"training":["Level 1 Public Order Officer","Level 1 Public Order","Level 1 Public Order Training","level_1_public_order"],"countable":true,"arrAttributes":["level_1_public_order"]}',
    "Level 1 Public Order capability",
)

source = replace_once(
    source,
    "function missionRequirementsReconcileCatalogue(parsed, catalogue, state = 'unavailable', expected = false) { const requirements",
    "function missionRequirementsReconcileCatalogue(parsed, catalogue, state = 'unavailable', expected = false) { const authoritativeSatisfied = parsed?.authoritativeSatisfied === true; const requirements",
    "authoritative reconciliation flag",
)
source = replace_once(
    source,
    "catalogueAvailabilityOnly: availabilityOnly, catalogueConditional: conditional }; continue;",
    "catalogueAvailabilityOnly: availabilityOnly, catalogueConditional: conditional, authoritativeSatisfied }; continue;",
    "existing catalogue requirement authority",
)
source = replace_once(
    source,
    "catalogueAvailabilityOnly: availabilityOnly, catalogueConditional: conditional, requirementSource:",
    "catalogueAvailabilityOnly: availabilityOnly, catalogueConditional: conditional, authoritativeSatisfied, requirementSource:",
    "new catalogue requirement authority",
)
source = replace_once(
    source,
    "for (const item of catalogue?.unresolved || []) {",
    "for (const item of authoritativeSatisfied ? [] : (catalogue?.unresolved || [])) {",
    "authoritative catalogue unresolved suppression",
)
source = replace_once(
    source,
    "if (!catalogue && expected) {",
    "if (!authoritativeSatisfied && !catalogue && expected) {",
    "authoritative catalogue loading suppression",
)
source = replace_once(
    source,
    "else if (catalogue?.stale) unresolved.push",
    "else if (!authoritativeSatisfied && catalogue?.stale) unresolved.push",
    "authoritative stale warning suppression",
)

authoritative_row = (
    "if (requirement.authoritativeSatisfied === true) { "
    "const requiredValue = Math.max(0, Number(requirement.baseline ?? requirement.missing) || 0); "
    "const zero = missionRequirementsCapacity(0, 0, true); const unknownOnSite = missionRequirementsCapacity(0, null, false); "
    "const row = missionRequirementsCoverageRow(requirement, zero, zero, unknownOnSite, missionRequirementsCapacity(requiredValue, requiredValue, true)); "
    "row.covered = true; row.definitelyOpen = false; row.uncertain = false; row.partial = false; row.coverageKnown = true; "
    "row.stillNeeded = 0; row.stillNeededMin = 0; row.stillNeededMax = 0; row.stillNeededKnown = true; row.stillNeededText = '0'; "
    "return { ...row, requirementAuthority: 'live-satisfied+mission-info' }; } "
)
source = replace_once(
    source,
    "if (requirement.definition?.countable === false) return missionRequirementsUnknownCoverageRow(requirement);",
    authoritative_row + "if (requirement.definition?.countable === false) return missionRequirementsUnknownCoverageRow(requirement);",
    "authoritatively covered row",
)
source = replace_once(
    source,
    "const raw = missionRequirementsElementText(record.source); if (!raw) { if (presentLive({ requirements: [], unresolved: [] })) return;",
    "const raw = missionRequirementsElementText(record.source); if (!raw) { const authoritativeSatisfied = (record.catalogueState === 'ready' || record.catalogueState === 'stale') && (record.source.id === 'missing_text' || record.source.matches?.('#missing_text')); if (presentLive({ requirements: [], unresolved: [], authoritativeSatisfied })) return;",
    "native empty live source authority",
)
SOURCE.write_text(source, encoding="utf-8")

for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    path.write_text(source, encoding="utf-8")

# Keep the canonical UK capability dataset aligned with the executable runtime.
data = json.loads(DATA.read_text(encoding="utf-8"))
staff = data.setdefault("staffRequirements", [])
level1_data = {
    "key": "public-order-level-1",
    "aliases": ["Level 1 Public Order Officer", "Level 1 Public Order Officers"],
    "types": [],
    "training": ["Level 1 Public Order Officer", "Level 1 Public Order", "Level 1 Public Order Training", "level_1_public_order"],
    "arrAttributes": ["level_1_public_order"],
}
existing = next((index for index, item in enumerate(staff) if item.get("key") == "public-order-level-1"), None)
if existing is None:
    level2_index = next((index for index, item in enumerate(staff) if item.get("key") == "public-order-level-2"), len(staff))
    staff.insert(level2_index, level1_data)
else:
    staff[existing] = level1_data
DATA.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

cross = json.loads(CROSS_SOURCE.read_text(encoding="utf-8"))
capabilities = cross.setdefault("capabilities", [])
level1_cross = {
    "aliases": ["Level 1 Public Order Officer", "Level 1 Public Order Officers"],
    "arrAttributes": ["level_1_public_order"],
    "conditionalVehicles": {},
    "equipment": [],
    "factors": {},
    "key": "public-order-level-1",
    "pair": False,
    "training": ["Level 1 Public Order Officer", "Level 1 Public Order", "Level 1 Public Order Training", "level_1_public_order"],
    "types": [],
}
existing = next((index for index, item in enumerate(capabilities) if item.get("key") == "public-order-level-1"), None)
if existing is None:
    level2_index = next((index for index, item in enumerate(capabilities) if item.get("key") == "public-order-level-2"), len(capabilities))
    capabilities.insert(level2_index, level1_cross)
else:
    capabilities[existing] = level1_cross
CROSS_SOURCE.write_text(json.dumps(cross, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Replace the obsolete contract that deliberately required Level 1 to remain unknown.
test = TEST.read_text(encoding="utf-8")
test = replace_once(
    test,
    "assert(level1PublicOrderRow.uncertain && level1PublicOrderRow.selectedText === '?' && level1PublicOrderRow.enRouteText === '?', 'unverified Level 1 Public Order capacity remains safely uncertain');",
    "assert.strictEqual(level1PublicOrderRow.uncertain, false, 'Level 1 Public Order has an executable explicit-training model');\nassert.strictEqual(level1PublicOrderRow.selectedText, '0', 'Level 1 Public Order selected capacity starts at zero');\nassert.strictEqual(level1PublicOrderRow.respondingText, '0', 'Level 1 Public Order responding capacity starts at zero');\nassert.strictEqual(level1PublicOrderRow.onSiteText, '0', 'Level 1 Public Order on-site capacity starts at zero');",
    "obsolete Level 1 uncertainty contract",
)

marker = "for (const group of crossSourceFixture.authoritativeLabels) {"
issue368_test = r'''
// Issue #368: authoritative empty live requirements and executable Level 1
// Public Order personnel tracking.
{
const issue368Specs = [
    ['24 Level 2 Public Order Officers', 24],
    ['3 Police Medics', 3],
    ['3 Police Sergeants', 3],
    ['1 Police Inspector', 1]
];
const issue368CatalogueRequirements = issue368Specs.map(([text, baseline]) => {
    const parsed = api.parseText(text, 'staff');
    assert.strictEqual(parsed.remaining, '', `Issue #368 parses ${text}`);
    assert.strictEqual(parsed.requirements.length, 1, `Issue #368 resolves one requirement for ${text}`);
    return { ...parsed.requirements[0], missing: baseline, baseline, statedRequirement: false };
});
const issue368Catalogue = {
    requirements: issue368CatalogueRequirements,
    unresolved: [{ group: 'staff', classification: 'operational', label: 'Unmapped catalogue specialist', value: '1' }]
};
const issue368Authoritative = api.reconcileCatalogue(
    { requirements: [], unresolved: [], authoritativeSatisfied: true },
    issue368Catalogue,
    'ready',
    true
);
assert.strictEqual(issue368Authoritative.requirements.length, 4, 'Issue #368 retains four catalogue rows for coverage accounting');
assert(issue368Authoritative.requirements.every(item => item.authoritativeSatisfied === true), 'Issue #368 marks every catalogue row authoritatively satisfied');
assert.strictEqual(issue368Authoritative.unresolved.length, 0, 'Issue #368 suppresses catalogue-only unresolved warnings after live satisfaction');
const issue368Doc = new FakeDocument();
const issue368Root = new FakeElement('div', issue368Doc);
issue368Doc.body.appendChild(issue368Root);
const issue368Candidate = { root: issue368Root, mount: issue368Root, source: null };
const issue368Rows = api.resolve(issue368Candidate, issue368Authoritative, issue368Catalogue);
assert.strictEqual(issue368Rows.length, 4, 'Issue #368 resolves all specialist rows');
for (const row of issue368Rows) {
    assert.strictEqual(row.covered, true, `${row.requirement}: authoritative live satisfaction covers the row`);
    assert.strictEqual(row.uncertain, false, `${row.requirement}: no confirmation warning remains`);
    assert.strictEqual(row.definitelyOpen, false, `${row.requirement}: no false shortage remains`);
    assert.strictEqual(row.stillNeededText, '0', `${row.requirement}: still needed is zero`);
    assert.strictEqual(row.onSiteText, '?', `${row.requirement}: specialist on-site count is not fabricated`);
    assert.strictEqual(row.requirementAuthority, 'live-satisfied+mission-info', `${row.requirement}: authority is explicit`);
}
assert.strictEqual(api.overallState(issue368Rows, []), 'success', 'Issue #368 overall state is successful');
const issue368Presentation = api.panelHtml(issue368Rows, []);
const issue368Html = issue368Presentation?.html ?? String(issue368Presentation ?? '');
assert(issue368Html.includes('All 4 covered'), 'Issue #368 panel reports full catalogue coverage');
assert(issue368Html.includes('All currently known requirements are covered.'), 'Issue #368 panel replaces false requirement rows with the all-covered state');
assert(!issue368Html.includes('need confirmation'), 'Issue #368 panel removes false confirmation warning');

const issue368OrdinaryEmpty = api.reconcileCatalogue(
    { requirements: [], unresolved: [] },
    issue368Catalogue,
    'ready',
    true
);
const issue368OrdinaryRows = api.resolve(issue368Candidate, issue368OrdinaryEmpty, issue368Catalogue);
assert(issue368OrdinaryRows.some(row => !row.covered && row.uncertain), 'ordinary empty data is not treated as authoritative satisfaction');
const issue368LiveSergeant = api.parseText('1 Police Sergeant', 'staff');
const issue368LiveMissing = api.reconcileCatalogue(issue368LiveSergeant, issue368Catalogue, 'ready', true);
const issue368LiveRows = api.resolve(issue368Candidate, issue368LiveMissing, issue368Catalogue);
const issue368SergeantRow = issue368LiveRows.find(row => row.key === 'police-sergeant-personnel');
assert(issue368SergeantRow && !issue368SergeantRow.covered, 'a non-empty live Police Sergeant requirement remains outstanding');
assert(!issue368LiveMissing.requirements.some(item => item.authoritativeSatisfied === true), 'non-empty live requirements never inherit authoritative satisfaction');
assert(source.includes("record.source.id === 'missing_text' || record.source.matches?.('#missing_text')"), 'Issue #368 limits empty-source authority to the native missing_text source');

const issue368Level1Doc = new FakeDocument();
issue368Level1Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/368-level1' } };
const issue368Level1Candidate = makeMissionCandidate(issue368Level1Doc, '21 Level 1 Public Order Officers');
const issue368Level1Definition = api.definitions.find(definition => definition.key === 'public-order-level-1');
assert(issue368Level1Definition, 'Issue #368 Level 1 definition exists');
assert.strictEqual(issue368Level1Definition.countable, true, 'Issue #368 Level 1 is countable');
assert(issue368Level1Definition.training.includes('level_1_public_order'), 'Issue #368 contains the native Level 1 schooling key');
assert(issue368Level1Definition.training.includes('Level 1 Public Order Training'), 'Issue #368 contains the visible Level 1 training caption');
assert(issue368Level1Definition.arrAttributes.includes('level_1_public_order'), 'Issue #368 contains the Level 1 ARR capability');
const issue368CacheLevel1 = (id, personnel) => api.vehicleApiCache.set(String(id), { id, vehicle_type: 51, assigned_personnel_count: personnel });
const issue368Level1Carriers = [36801, 36802, 36803].map(id => {
    const carrier = makeVehicleElement(issue368Level1Doc, id, 51, { typeOnRow: true });
    carrier.vehicle.checked = true;
    carrier.vehicle.matchSet.add('.vehicle_checkbox');
    carrier.vehicle.classList.values.add('vehicle_checkbox');
    carrier.row.textContent = carrier.row.innerText = 'Police Support Unit Carrier [Level 1 Public Order Officer]';
    issue368CacheLevel1(id, 7);
    return carrier;
});
issue368Level1Candidate.root.selectedUnits = issue368Level1Carriers.map(carrier => carrier.vehicle);
let issue368Level1Units = api.collectUnits(issue368Level1Candidate, 'selected');
let issue368Level1Capacity = api.aggregate({ group: 'staff', definition: issue368Level1Definition }, issue368Level1Units);
assert.strictEqual(issue368Level1Capacity.min, 21, 'three exact seven-person Level 1 carriers contribute twenty-one');
assert.strictEqual(issue368Level1Capacity.max, 21, 'Level 1 selected capacity is exact');
let issue368Level1Rows = api.resolve(issue368Level1Candidate, {
    requirements: [{ key: 'public-order-level-1', requirement: 'Level 1 Public Order Officer', missing: 21, group: 'staff', definition: issue368Level1Definition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'public-order-level-1', baseline: 21, missing: 21 }] });
let issue368Level1Row = issue368Level1Rows.find(row => row.key === 'public-order-level-1');
assert.strictEqual(issue368Level1Row.selectedText, '21', 'Matrix displays twenty-one selected Level 1 officers');
assert.strictEqual(issue368Level1Row.respondingText, '0', 'Level 1 responding bucket is numeric when empty');
assert.strictEqual(issue368Level1Row.onSiteText, '0', 'Level 1 on-site bucket is numeric when empty');
assert.strictEqual(issue368Level1Row.stillNeededText, '0', 'twenty-one selected Level 1 officers clear demand');
assert.strictEqual(issue368Level1Row.covered, true, 'Level 1 row is covered');

issue368Level1Carriers[2].vehicle.checked = false;
issue368Level1Candidate.root.selectedUnits = issue368Level1Carriers.slice(0, 2).map(carrier => carrier.vehicle);
issue368Level1Rows = api.resolve(issue368Level1Candidate, {
    requirements: [{ key: 'public-order-level-1', requirement: 'Level 1 Public Order Officer', missing: 21, group: 'staff', definition: issue368Level1Definition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'public-order-level-1', baseline: 21, missing: 21 }] });
issue368Level1Row = issue368Level1Rows.find(row => row.key === 'public-order-level-1');
assert.strictEqual(issue368Level1Row.selectedText, '14', 'deselecting one Level 1 carrier removes seven personnel');
assert.strictEqual(issue368Level1Row.stillNeededText, '7', 'seven-person Level 1 shortage returns after deselection');

const issue368Untrained = makeVehicleElement(issue368Level1Doc, 36810, 8, { typeOnRow: true });
issue368Untrained.vehicle.checked = true;
issue368Untrained.vehicle.matchSet.add('.vehicle_checkbox');
issue368Untrained.vehicle.classList.values.add('vehicle_checkbox');
issue368Untrained.row.textContent = issue368Untrained.row.innerText = 'Generic Police Car';
issue368CacheLevel1(36810, 7);
issue368Level1Candidate.root.selectedUnits = [issue368Untrained.vehicle];
issue368Level1Units = api.collectUnits(issue368Level1Candidate, 'selected');
issue368Level1Capacity = api.aggregate({ group: 'staff', definition: issue368Level1Definition }, issue368Level1Units);
assert.strictEqual(issue368Level1Capacity.min, 0, 'untrained police personnel do not satisfy Level 1 demand');

const issue368Linked = new FakeElement('input');
issue368Linked.setAttribute('data-education-key', 'level_1_public_order');
const issue368LinkedRow = new FakeElement('tr');
issue368Linked.closestMap.set('tr', issue368LinkedRow);
const issue368Level1Training = api.linkedTrainingValues({
    root: { querySelectorAll(selector) { return selector.includes('36820') ? [issue368Linked] : []; } },
    mount: null,
    source: null
}, 36820, new FakeElement('a'));
assert(issue368Level1Training.has('level 1 public order'), 'native level_1_public_order metadata is recognised');
const issue368OperationalUnit = {
    typeId: 51,
    vehicleId: 36820,
    equipment: new Set(),
    labels: new Set(),
    training: issue368Level1Training,
    arrCapabilities: new Set(['level 1 public order']),
    arrCapabilityKnown: true,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set(),
    staff: api.capacity(7, 7, true),
    contributionKey: 'vehicle:36820'
};
const issue368RespondingCapacity = api.aggregate({ group: 'staff', definition: issue368Level1Definition }, [issue368OperationalUnit]);
assert.strictEqual(issue368RespondingCapacity.min, 7, 'seven explicitly trained Level 1 officers count as Responding');
const issue368RespondingRow = api.coverageRow(
    { key: 'public-order-level-1', requirement: 'Level 1 Public Order Officer', missing: 7, group: 'staff', definition: issue368Level1Definition },
    api.capacity(0, 0, true),
    issue368RespondingCapacity,
    api.capacity(0, 0, true),
    api.capacity(7, 7, true)
);
assert.strictEqual(issue368RespondingRow.respondingText, '7', 'Level 1 responding count is numeric');
assert.strictEqual(issue368RespondingRow.stillNeededText, '0', 'responding Level 1 officers clear demand');
const issue368OnSiteRow = api.coverageRow(
    { key: 'public-order-level-1', requirement: 'Level 1 Public Order Officer', missing: 7, group: 'staff', definition: issue368Level1Definition },
    api.capacity(0, 0, true),
    api.capacity(0, 0, true),
    issue368RespondingCapacity,
    api.capacity(7, 7, true)
);
assert.strictEqual(issue368OnSiteRow.onSiteText, '7', 'Level 1 on-site count is numeric');
assert.strictEqual(issue368OnSiteRow.stillNeededText, '0', 'on-site Level 1 officers clear demand');
}

'''
test = replace_once(test, marker, issue368_test + marker, "Issue 368 combined runtime regression insertion")
TEST.write_text(test, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
release_notes = """## [4.20.37] - 2026-07-22

### Critical Mission Requirements fixes
- Distinguished an authoritative empty MissionChief `#missing_text` source from an absent or unavailable source.
- Marked catalogue-only requirements covered when MissionChief confirms that no live requirements remain.
- Enabled exact Level 1 Public Order Officer tracking using the canonical `level_1_public_order` schooling and ARR capability.
- Preserved unknown specialist on-site composition instead of fabricating personnel counts.
- Added exact regressions for Rival Fans Mass Disorder (Medium) and a twenty-one-officer Level 1 Public Order selection.

### Benefit
- Fully satisfied missions no longer retain false specialist shortages or `need confirmation` warnings.
- Selecting qualified Level 1 Public Order units now updates Selected and Still Needed immediately; qualified responding and on-site crews also render numeric totals.

### Compatibility
- Non-empty live requirements, unavailable sources, loading states, explicit specialist training, deselection, patients, prisoners and transports retain their existing authority and tracking behaviour.
- Generic police vehicles and untrained personnel do not satisfy Level 1 Public Order demand.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + release_notes, "v4.20.37 changelog")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_html = HELP.read_text(encoding="utf-8")
help_html = replace_once(help_html, "Guide for Toolkit v4.20.36", "Guide for Toolkit v4.20.37", "help version")
HELP.write_text(help_html, encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
source_lines = len(source.splitlines())
headroom["candidateVersion"] = "4.20.37"
headroom["candidateSourceLines"] = source_lines
headroom["recoveredSourceLines"] = headroom["originalSourceLines"] - source_lines
headroom["candidateSourceSha256"] = hashlib.sha256(source.encode()).hexdigest()
headroom["invariant"] = (
    f'The reviewed compact stylesheet retains {headroom["recoveredSourceLines"]} recovered source lines while '
    "authoritative empty live requirements clear false shortages and explicit Level 1 Public Order evidence contributes exact personnel."
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

if source_lines != 31653:
    raise RuntimeError(f"source line count changed unexpectedly: {source_lines}")
if headroom["recoveredSourceLines"] != 504:
    raise RuntimeError(f"source-headroom recovery changed unexpectedly: {headroom['recoveredSourceLines']}")

env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
subprocess.check_call(["node", "--check", str(SOURCE)], cwd=ROOT, env=env)
subprocess.check_call(["node", str(TEST)], cwd=ROOT, env=env)
subprocess.check_call(["python3", str(ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py")], cwd=ROOT, env=env)
subprocess.check_call(["python3", str(ROOT / ".github" / "scripts" / "audit_lssm_requirement_compatibility.py")], cwd=ROOT, env=env)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

print("Prepared Toolkit v4.20.37 combined Mission Requirements hotfix")
