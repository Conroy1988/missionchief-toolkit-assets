#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DIST_FILES = [
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
]
DIAGNOSTIC_PACKAGE = ROOT / ".github" / "development-packages" / "issue-226-operational-diagnostic.py"
DIAGNOSTIC_OUTPUT = ROOT / "status" / "issue-226-operational-diagnostic.txt"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_function(text: str, name: str, replacement: str) -> str:
    marker = f"function {name}"
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"{marker} not found")
    brace = text.find("{", start)
    if brace < 0:
        raise AssertionError(f"{marker} opening brace not found")
    depth = 0
    quote = None
    escaped = False
    for index in range(brace, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"', "`"):
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[:start] + replacement + text[index + 1:]
    raise AssertionError(f"{marker} closing brace not found")


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.20.8", "// @version      4.20.9", "metadata version")
source = replace_once(source, "version: '4.20.8'", "version: '4.20.9'", "runtime version")

operational_active = r'''function missionRequirementsOperationalCanonicalStateContainer(element, mode) {
        if (mode === 'selected') return null;
        const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || element;
        if (!row) return null;
        const selectors = mode === 'onsite'
            ? ['#mission_vehicle_at_mission', 'tbody#mission_vehicle_at_mission']
            : ['#mission_vehicle_driving', 'tbody#mission_vehicle_driving'];
        for (const selector of selectors) {
            if (row.matches?.(selector)) return row;
            const container = row.closest?.(selector);
            if (container) return container;
        }
        return null;
    }

    function missionRequirementsOperationalElementActive(element, candidate, context = missionRequirementsPatientContext(candidate), mode = '') {
        if (!element || element.isConnected === false) return false;
        if (mode === 'selected' && typeof element.checked === 'boolean' && !element.checked) return false;
        const row = element.matches?.('tr') ? element : element.closest?.('tr') || element;
        const expectedMission = missionRequirementsMissionIdentity(candidate, candidate?.source);
        const canonicalContainer = missionRequirementsOperationalCanonicalStateContainer(row, mode);
        const candidateRoot = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount;
        const canonicalId = mode === 'onsite' ? 'mission_vehicle_at_mission' : 'mission_vehicle_driving';
        const documentCanonical = mode === 'selected' ? null : context?.doc?.getElementById?.(canonicalId);
        const pathname = String(context?.doc?.defaultView?.location?.pathname || '');
        const pathMission = missionRequirementsOptionalNumber(pathname.match(/\/missions\/(\d+)/u)?.[1]);
        const canonicalOwned = Boolean(canonicalContainer && (
            context?.activeWindow?.contains?.(row)
            || candidateRoot?.contains?.(row)
            || candidate?.root?.contains?.(row)
            || candidate?.mount?.contains?.(row)
            || (
                expectedMission > 0
                && pathMission === expectedMission
                && documentCanonical
                && (documentCanonical === canonicalContainer || documentCanonical.contains?.(row))
            )
        ));
        if (mode !== 'selected' && !canonicalOwned && !isVisible(element)) return false;
        if (context.activeWindow && !(
            context.activeWindow === row
            || context.activeWindow.contains?.(row)
            || row.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog') === context.activeWindow
        )) return false;
        const explicitMission = missionRequirementsOptionalNumber(row?.getAttribute?.('data-mission-id') ?? row?.dataset?.missionId);
        if (expectedMission > 0 && explicitMission !== null && explicitMission !== expectedMission) return false;
        const missionRoot = row.closest?.('#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]');
        if (expectedMission > 0 && missionRoot) {
            const actualMission = missionRequirementsMissionIdentity({ root: missionRoot, mount: missionRoot }, null);
            if (actualMission > 0 && actualMission !== expectedMission) return false;
        }
        return true;
    }'''
source = replace_function(source, "missionRequirementsOperationalElementActive", operational_active)
SOURCE.write_text(source, encoding="utf-8")
for distribution in DIST_FILES:
    distribution.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.8'", "version: '4.20.9'", "runtime fixture version")
issue226_tests = r'''
// Issue #226: collapsed or relocated canonical operational tables remain authoritative.
{
const issue226WindowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
const issue226Doc = new FakeDocument();
issue226Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const issue226Candidate = makeMissionCandidate(issue226Doc, '1 Police car');
issue226Candidate.missionId = 6226;
const issue226Window = new FakeElement('div', issue226Doc);
issue226Candidate.root.closestMap.set(issue226WindowSelector, issue226Window);
issue226Candidate.source.closestMap.set(issue226WindowSelector, issue226Window);
issue226Window.appendChild(issue226Candidate.root);
const issue226PoliceDefinition = api.definitions.find(definition => definition.key === 'police-car');
const issue226Parsed = { requirements: [{ key: 'police-car', requirement: 'Police Car', missing: 1, group: 'vehicles', definition: issue226PoliceDefinition }], unresolved: [] };
const issue226Catalogue = { requirements: [{ key: 'police-car', baseline: 1, missing: 1 }] };

const issue226RespondingBody = new FakeElement('tbody', issue226Doc);
issue226RespondingBody.id = 'mission_vehicle_driving';
issue226Window.appendChild(issue226RespondingBody);
const issue226Responding = makeVehicleElement(issue226Doc, 622601, 8, { typeOnRow: true });
issue226Responding.row.setAttribute('data-vehicle-id', '622601');
issue226Responding.row._visible = false;
issue226Responding.row.closestMap.set('#mission_vehicle_driving', issue226RespondingBody);
issue226Responding.row.closestMap.set('tbody#mission_vehicle_driving', issue226RespondingBody);
issue226Responding.row.closestMap.set(issue226WindowSelector, issue226Window);
issue226RespondingBody.appendChild(issue226Responding.row);
issue226Window.queryAllHandler = selector => selector === 'tbody#mission_vehicle_driving > tr' || selector === '#mission_vehicle_driving > tr' ? [issue226Responding.row] : [];
let issue226Row = api.resolve(issue226Candidate, issue226Parsed, issue226Catalogue)[0];
assert.strictEqual(issue226Row.respondingMin, 1, 'collapsed canonical Units Responding row contributes capacity');
assert.strictEqual(issue226Row.stillNeededText, '0', 'responding capacity fulfils the requirement');
assert.strictEqual(issue226Row.covered, true, 'collapsed responding capacity produces a covered row');
let issue226Panel = api.panelHtml([issue226Row], []);
assert(!issue226Panel.html.includes('Police Car'), 'responding-covered requirement is hidden from the Matrix list');
assert(issue226Panel.html.includes('All currently known requirements are covered.'), 'responding-covered mission retains explicit success state');

const issue226OnSiteBody = new FakeElement('tbody', issue226Doc);
issue226OnSiteBody.id = 'mission_vehicle_at_mission';
issue226Window.appendChild(issue226OnSiteBody);
const issue226OnSite = makeVehicleElement(issue226Doc, 622601, 8, { typeOnRow: true });
issue226OnSite.row.setAttribute('data-vehicle-id', '622601');
issue226OnSite.row._visible = false;
issue226OnSite.row.closestMap.set('#mission_vehicle_at_mission', issue226OnSiteBody);
issue226OnSite.row.closestMap.set('tbody#mission_vehicle_at_mission', issue226OnSiteBody);
issue226OnSite.row.closestMap.set(issue226WindowSelector, issue226Window);
issue226OnSiteBody.appendChild(issue226OnSite.row);
issue226Window.queryAllHandler = selector => selector === 'tbody#mission_vehicle_at_mission > tr' || selector === '#mission_vehicle_at_mission > tr' ? [issue226OnSite.row] : [];
issue226Row = api.resolve(issue226Candidate, issue226Parsed, issue226Catalogue)[0];
assert.strictEqual(issue226Row.onSiteMin, 1, 'collapsed canonical Vehicles on Scene row contributes capacity');
assert.strictEqual(issue226Row.respondingMin, 0, 'on-site state supersedes responding after arrival');
assert.strictEqual(issue226Row.stillNeededText, '0', 'on-site capacity fulfils the requirement');
issue226Panel = api.panelHtml([issue226Row], []);
assert(!issue226Panel.html.includes('Police Car'), 'on-site-covered requirement is hidden from the Matrix list');

issue226Window.queryAllHandler = () => [];
issue226Row = api.resolve(issue226Candidate, issue226Parsed, issue226Catalogue)[0];
assert.strictEqual(issue226Row.stillNeededText, '1', 'shortage returns when committed capacity is removed');
assert(api.panelHtml([issue226Row], []).html.includes('Police Car'), 'hidden row returns after cancellation or departure');

const issue226StaleWindow = new FakeElement('div', issue226Doc);
const issue226StaleBody = new FakeElement('tbody', issue226Doc);
issue226StaleBody.id = 'mission_vehicle_driving_stale';
issue226StaleWindow.appendChild(issue226StaleBody);
const issue226Stale = makeVehicleElement(issue226Doc, 622699, 8, { typeOnRow: true });
issue226Stale.row.setAttribute('data-vehicle-id', '622699');
issue226Stale.row.setAttribute('data-mission-id', '9999');
issue226Stale.row._visible = false;
issue226Stale.row.closestMap.set('#mission_vehicle_driving', issue226StaleBody);
issue226Stale.row.closestMap.set(issue226WindowSelector, issue226StaleWindow);
issue226StaleBody.appendChild(issue226Stale.row);
assert.strictEqual(
    api.operationalActive(issue226Stale.row, issue226Candidate, { doc: issue226Doc, activeWindow: issue226Window }, 'responding'),
    false,
    'hidden stale operational table from another mission remains excluded'
);
}

'''
runtime = replace_once(
    runtime,
    "const personnelDoc = new FakeDocument();\n",
    issue226_tests + "const personnelDoc = new FakeDocument();\n",
    "Issue 226 operational fixtures",
)
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '        "mode !== \'selected\' && !isVisible(element)",\n',
    '        "function missionRequirementsOperationalCanonicalStateContainer(element, mode)",\n'
    '        "const canonicalContainer = missionRequirementsOperationalCanonicalStateContainer(row, mode)",\n'
    '        "mode !== \'selected\' && !canonicalOwned && !isVisible(element)",\n',
    "operational visibility contract markers",
)
contract = replace_once(
    contract,
    '    assert "missionRequirementsOperationalWindowScopes(candidate, context)" in source, "selected-unit acquisition must expand beyond the narrow mission root"\n',
    '    assert "missionRequirementsOperationalWindowScopes(candidate, context)" in source, "selected-unit acquisition must expand beyond the narrow mission root"\n'
    '    assert "missionRequirementsOperationalCanonicalStateContainer" in source, "canonical operational tables must bypass collapse-only visibility"\n'
    '    assert "documentCanonical === canonicalContainer || documentCanonical.contains?.(row)" in source, "standalone canonical-table ownership must be proven"\n',
    "Issue 226 contract assertions",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [4.20.9] - 2026-07-20

### Fixed
- Restored Mission Requirements Matrix capacity from active **Units Responding** and **Vehicles on Scene** tables when those MissionChief sections are collapsed or relocated within the active mission window.
- Responding and on-site vehicles now fulfil and hide completed requirement rows exactly as selected vehicles do.
- Hidden rows return immediately when a unit is cancelled, redirected, removed from scene or no longer satisfies the requirement.

### Safety
- Visibility is bypassed only for canonical MissionChief operational tables proven to belong to the active mission.
- Hidden stale lightboxes, mismatched mission IDs, template rows and unrelated operational content remain excluded.
- On site, Responding and Selected de-duplication and precedence remain unchanged.

### Validation
- Added deterministic collapsed-table, relocated-lightbox, fulfilled-row, renewed-shortage and stale-mission regression fixtures.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog release entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

for path in (DIAGNOSTIC_PACKAGE, DIAGNOSTIC_OUTPUT):
    if path.exists():
        path.unlink()

subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", str(DIST_FILES[0].relative_to(ROOT)), str(DIST_FILES[1].relative_to(ROOT))], cwd=ROOT, check=True)
print("Issue #226 operational capacity hotfix validated")
