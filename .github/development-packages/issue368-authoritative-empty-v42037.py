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

# Exact Rival Fans Mass Disorder (Medium) reconciliation regression.
test = TEST.read_text(encoding="utf-8")
marker = "for (const group of crossSourceFixture.authoritativeLabels) {"
issue368_test = r'''
// Issue #368: MissionChief's connected, empty live missing-requirements source
// is authoritative after catalogue readiness. Catalogue-only specialist rows
// remain available for the coverage total but must not appear as shortages.
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
const issue368Html = api.panelHtml(issue368Rows, []);
assert(issue368Html.includes('4/4 covered'), 'Issue #368 panel reports full catalogue coverage');
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

'''
test = replace_once(test, marker, issue368_test + marker, "Issue 368 runtime regression insertion")
TEST.write_text(test, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
release_notes = """## [4.20.37] - 2026-07-22

### Critical Mission Requirements fix
- Distinguished an authoritative empty MissionChief `#missing_text` source from an absent or unavailable requirements source.
- Marked catalogue-only requirements covered when MissionChief confirms that no live requirements remain.
- Preserved unknown specialist on-site counts instead of fabricating personnel composition.
- Added an exact Rival Fans Mass Disorder (Medium) regression for Level 2 Public Order Officers, Police Medics, Police Sergeants and Police Inspectors.

### Benefit
- Fully satisfied missions no longer show false specialist shortages or `need confirmation` warnings after all required units are on scene.

### Compatibility
- Non-empty live requirements, unavailable sources, loading states, explicit specialist training, patients, prisoners and transports retain their existing authority and tracking behaviour.

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
    "authoritative empty MissionChief requirement sources clear catalogue-only shortages without inventing specialist personnel counts."
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

if source_lines != 31653:
    raise RuntimeError(f"source line count changed unexpectedly: {source_lines}")
if headroom["recoveredSourceLines"] != 504:
    raise RuntimeError(f"source-headroom recovery changed unexpectedly: {headroom['recoveredSourceLines']}")

env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
subprocess.check_call(["node", "--check", str(SOURCE)], cwd=ROOT, env=env)
subprocess.check_call(["node", str(TEST)], cwd=ROOT, env=env)
subprocess.check_call(["python3", str(ROOT / ".github" / "scripts" / "audit_lssm_requirement_compatibility.py")], cwd=ROOT, env=env)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

print("Prepared Toolkit v4.20.37 authoritative-empty Mission Requirements hotfix")
