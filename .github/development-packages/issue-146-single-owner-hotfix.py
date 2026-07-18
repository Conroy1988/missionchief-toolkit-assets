#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
OLD_VERSION = "4.15.2"
NEW_VERSION = "4.15.3"


def replace_function(text: str, signature: str, next_signature: str, replacement: str) -> str:
    start_token = f"    function {signature}"
    end_token = f"    function {next_signature}"
    start = text.find(start_token)
    end = text.find(end_token, start + len(start_token))
    if start < 0 or end < 0:
        raise AssertionError(f"missing function boundary: {signature} -> {next_signature}")
    return text[:start] + replacement.rstrip() + "\n\n" + text[end:]


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


source = SOURCE.read_text(encoding="utf-8")
if f"// @version      {OLD_VERSION}" not in source or f"version: '{OLD_VERSION}'" not in source:
    raise AssertionError(f"Issue #146 expects Toolkit v{OLD_VERSION}")

source = source.replace(f"// @version      {OLD_VERSION}", f"// @version      {NEW_VERSION}", 1)
source = source.replace(f"version: '{OLD_VERSION}'", f"version: '{NEW_VERSION}'", 1)

candidate_block = r'''    function missionRequirementsPrimaryRuntime() {
    try { return !pageWindow.top || pageWindow.top === pageWindow; } catch (err) { return true; }
    }

    function missionRequirementsMissionIdentity(candidate, source) {
    const root = candidate?.root;
    const linked = root?.querySelector?.('a[href*="/missions/"], form[action*="/missions/"]');
    const values = [candidate?.missionId, candidate?.mission_id, root?.dataset?.missionId, root?.getAttribute?.('data-mission-id'), root?.getAttribute?.('mission_id'), root?.getAttribute?.('action'), linked?.getAttribute?.('href'), linked?.getAttribute?.('action'), source?.ownerDocument?.defaultView?.location?.pathname];
    for (const value of values) {
    const raw = String(value ?? '').trim();
    const match = raw.match(/(?:\/missions\/|mission[_-]?)(\d+)/i);
    const id = normaliseMissionId(match?.[1] ?? (/^\d+$/.test(raw) ? raw : null));
    if (id !== null) return `mission:${id}`;
    }
    return null;
    }

    function missionRequirementsWindowCandidates() {
    const candidates = [];
    const seenSources = new Set();
    const add = candidate => {
    const source = missionRequirementsSourceForCandidate(candidate);
    if (!source || source.isConnected === false || seenSources.has(source)) return;
    seenSources.add(source);
    candidates.push({ ...candidate, source });
    };
    for (const candidate of missionValueWindowCandidates()) add(candidate);
    for (const context of transportSweepDocumentContexts()) {
    const doc = context?.doc;
    if (!doc?.querySelectorAll) continue;
    for (const source of Array.from(doc.querySelectorAll('#missing_text'))) add(missionRequirementsCandidateFromSource(source));
    }
    const seenMissions = new Set();
    return candidates.sort((a, b) => {
    const aScore = (missionRequirementsRecords.has(a.source) ? 2 : 0) + (isVisible(a.source) ? 1 : 0);
    const bScore = (missionRequirementsRecords.has(b.source) ? 2 : 0) + (isVisible(b.source) ? 1 : 0);
    return bScore - aScore;
    }).filter(candidate => {
    const identity = missionRequirementsMissionIdentity(candidate, candidate.source);
    if (!identity) return true;
    if (seenMissions.has(identity)) return false;
    seenMissions.add(identity);
    return true;
    });
    }'''
source = replace_function(source, "missionRequirementsWindowCandidates()", "missionRequirementsDocumentCss()", candidate_block)

host_and_ensure_block = r'''    function missionRequirementsHostPanels(source) {
    return Array.from(source?.parentNode?.children || []).filter(panel => panel?.id === SCRIPT.missionRequirementsPanelId || panel?.getAttribute?.('data-mcms-requirements-panel') === '1');
    }

    function missionRequirementsCanonicalPanel(source, preferred = null) {
    const panels = missionRequirementsHostPanels(source);
    if (!panels.length) return null;
    const canonical = preferred && panels.includes(preferred) ? preferred : panels[0];
    canonical.id = SCRIPT.missionRequirementsPanelId;
    canonical.setAttribute?.('data-mcms-requirements-panel', '1');
    for (const panel of panels) if (panel !== canonical) try { panel.remove(); } catch (err) {}
    return canonical;
    }

    function missionRequirementsBindPanel(panel) {
    if (!panel || panel.getAttribute?.('data-mcms-requirements-collapse-bound') === '1') return;
    panel.setAttribute?.('data-mcms-requirements-collapse-bound', '1');
    panel.addEventListener('click', event => {
    const button = event.target?.closest?.('[data-mcms-requirements-collapse]');
    if (!button) return;
    const collapsed = panel.classList.toggle('mcms-collapsed');
    button.setAttribute('aria-expanded', String(!collapsed));
    button.setAttribute('aria-label', collapsed ? 'Expand mission requirements' : 'Collapse mission requirements');
    button.textContent = collapsed ? '⌄' : '⌃';
    });
    }

    function missionRequirementsEnsureRecord(candidate, source) {
    let record = missionRequirementsRecords.get(source);
    const connectedPanel = record?.panel?.isConnected ? record.panel : null;
    const canonical = missionRequirementsCanonicalPanel(source, connectedPanel);
    if (record && canonical) {
    record.panel = canonical;
    record.candidate = candidate;
    missionRequirementsBindPanel(canonical);
    missionRequirementsHideSource(source);
    missionRequirementsScheduleRecord(record);
    return record;
    }
    if (record) missionRequirementsRemoveRecord(source);
    const doc = source.ownerDocument || document;
    for (const [otherSource, otherRecord] of Array.from(missionRequirementsRecords.entries())) {
    if (otherSource !== source && otherRecord?.source?.ownerDocument === doc) missionRequirementsRemoveRecord(otherSource);
    }
    ensureMissionRequirementsDocumentStyle(doc);
    let panel = missionRequirementsCanonicalPanel(source);
    if (!panel) {
    panel = doc.createElement('section');
    panel.id = SCRIPT.missionRequirementsPanelId;
    panel.setAttribute('data-mcms-requirements-panel', '1');
    panel.setAttribute('aria-label', 'Live mission requirements');
    source.parentNode?.insertBefore(panel, source);
    }
    panel.dataset.mcmsTheme = state.uiTheme;
    missionRequirementsBindPanel(panel);
    missionRequirementsHideSource(source);
    record = { candidate, source, panel, observer: null, frame: null };
    const observeRoot = candidate.root?.isConnected ? candidate.root : candidate.mount;
    const view = doc.defaultView || pageWindow;
    const MutationObserverCtor = view?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
    if (observeRoot && typeof MutationObserverCtor === 'function') {
    record.observer = runtimeTrackObserver(new MutationObserverCtor(mutations => {
    if (mutations.some(mutation => missionRequirementsMutationRelevant(record, mutation))) missionRequirementsScheduleRecord(record);
    }));
    record.observer.observe(observeRoot, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: ['checked', 'class', 'style', 'vehicle_type_id', 'data-vehicle-type-id', 'data-vehicle_type_id', 'data-equipment-types', 'data-equipment-type', 'data-current-personnel', 'data-min-personnel', 'data-max-personnel', 'tractive_vehicle_id', 'data-tractive-vehicle-id', 'trailer_id', 'data-trailer-id', 'sortvalue']
    });
    }
    missionRequirementsRecords.set(source, record);
    missionRequirementsScheduleRecord(record);
    return record;
    }'''
source = replace_function(source, "missionRequirementsEnsureRecord(candidate, source)", "missionRequirementsRemoveRecord(source)", host_and_ensure_block)

old_render_guard = "if (!record?.source?.isConnected || !record?.candidate?.mount?.isConnected) {"
new_render_guard = "if (!record?.source?.isConnected || !record?.candidate?.mount?.isConnected || !record?.panel?.isConnected) {"
if source.count(old_render_guard) != 1:
    raise AssertionError("missionRequirementsRenderRecord guard missing or duplicated")
source = source.replace(old_render_guard, new_render_guard, 1)

scan_anchor = "    function scanMissionRequirementsWindows() {\n        if (runtime.destroyed) return;"
scan_replacement = "    function scanMissionRequirementsWindows() {\n        if (runtime.destroyed || !missionRequirementsPrimaryRuntime()) return;"
if source.count(scan_anchor) != 1:
    raise AssertionError("scanMissionRequirementsWindows guard anchor missing or duplicated")
source = source.replace(scan_anchor, scan_replacement, 1)

install_anchor = "    function installMissionRequirementsWindows() {\n        if (!missionRequirementsFeatureInstalled) {"
install_replacement = "    function installMissionRequirementsWindows() {\n        if (!missionRequirementsPrimaryRuntime()) return;\n        if (!missionRequirementsFeatureInstalled) {"
if source.count(install_anchor) != 1:
    raise AssertionError("installMissionRequirementsWindows anchor missing or duplicated")
source = source.replace(install_anchor, install_replacement, 1)

css_start = source.find("    function missionRequirementsDocumentCss() {")
css_return = source.find("return `", css_start) + len("return `")
css_end = source.find("`;", css_return)
if css_start < 0 or css_return < len("return `") or css_end < 0:
    raise AssertionError("Mission Requirements CSS template boundary missing")
css_payload = source[css_return:css_end]
css_compact = "".join(line.strip() for line in css_payload.splitlines())
source = source[:css_return] + css_compact + source[css_end:]

SOURCE.write_text(source, encoding="utf-8")

runtime_test = RUNTIME_TEST.read_text(encoding="utf-8")
remove_attr_anchor = "    getAttribute(name) {\n        if (name === 'data-raw-html' && this._lssmActive) {"
remove_attr_replacement = "    removeAttribute(name) {\n        this.attributes.delete(name);\n        if (name === 'id') this.id = '';\n    }\n    getAttribute(name) {\n        if (name === 'data-raw-html' && this._lssmActive) {"
if runtime_test.count(remove_attr_anchor) != 1:
    raise AssertionError("FakeElement removeAttribute anchor missing")
runtime_test = runtime_test.replace(remove_attr_anchor, remove_attr_replacement, 1)

api_anchor = "    windowCandidates: missionRequirementsWindowCandidates,\n    scan: scanMissionRequirementsWindows,"
api_replacement = "    windowCandidates: missionRequirementsWindowCandidates,\n    primaryRuntime: missionRequirementsPrimaryRuntime,\n    canonicalPanel: missionRequirementsCanonicalPanel,\n    scan: scanMissionRequirementsWindows,"
if runtime_test.count(api_anchor) != 1:
    raise AssertionError("runtime API anchor missing")
runtime_test = runtime_test.replace(api_anchor, api_replacement, 1)

lifecycle_anchor = "const lifecycleDoc = new FakeDocument();\nlifecycleDoc.defaultView = { MutationObserver: FakeMutationObserver };"
new_fixtures = r'''const canonicalDoc = new FakeDocument();
canonicalDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/7001' } };
const canonicalCandidate = makeMissionCandidate(canonicalDoc, '1 Ambulance');
canonicalCandidate.missionId = 7001;
const stalePanelA = canonicalDoc.createElement('section');
stalePanelA.id = 'mc-map-command-toolkit-mission-requirements';
canonicalCandidate.root.insertBefore(stalePanelA, canonicalCandidate.source);
const stalePanelB = canonicalDoc.createElement('section');
stalePanelB.id = 'mc-map-command-toolkit-mission-requirements';
canonicalCandidate.root.insertBefore(stalePanelB, canonicalCandidate.source);
candidates = [canonicalCandidate];
api.scan();
flushAnimationFrames();
const canonicalPanels = canonicalCandidate.root.children.filter(child => child.id === 'mc-map-command-toolkit-mission-requirements');
assert.strictEqual(canonicalPanels.length, 1, 'pre-existing Toolkit duplicates collapse to one canonical host panel');
assert.strictEqual(api.records.get(canonicalCandidate.source).panel, stalePanelA, 'the first connected host panel is adopted rather than recreated');
api.clear();

const mirrorDocA = new FakeDocument();
const mirrorDocB = new FakeDocument();
mirrorDocA.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/8001' } };
mirrorDocB.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/8001' } };
const mirrorCandidateA = makeMissionCandidate(mirrorDocA, '1 Police Sergeant');
const mirrorCandidateB = makeMissionCandidate(mirrorDocB, '1 Police Sergeant');
mirrorCandidateA.missionId = 8001;
mirrorCandidateB.missionId = 8001;
candidates = [mirrorCandidateA, mirrorCandidateB];
documentContexts = [mirrorDocA, mirrorDocB];
assert.strictEqual(api.windowCandidates().length, 1, 'parent and frame mirrors of one MissionChief mission deduplicate by mission identity');
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'mirrored MissionChief documents create one requirements record');
assert.strictEqual(
    mirrorCandidateA.root.children.filter(child => child.id === 'mc-map-command-toolkit-mission-requirements').length
    + mirrorCandidateB.root.children.filter(child => child.id === 'mc-map-command-toolkit-mission-requirements').length,
    1,
    'mirrored MissionChief documents render one visible requirements panel'
);
api.clear();
documentContexts = [];

const childDoc = new FakeDocument();
childDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9001' } };
const childCandidate = makeMissionCandidate(childDoc, '1 Ambulance');
candidates = [childCandidate];
context.pageWindow.top = {};
assert.strictEqual(api.primaryRuntime(), false, 'child-frame Toolkit runtime is not the Mission Requirements owner');
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'child-frame runtime does not mount a competing requirements panel');
delete context.pageWindow.top;

const lifecycleDoc = new FakeDocument();
lifecycleDoc.defaultView = { MutationObserver: FakeMutationObserver };'''
if runtime_test.count(lifecycle_anchor) != 1:
    raise AssertionError("lifecycle fixture anchor missing")
runtime_test = runtime_test.replace(lifecycle_anchor, new_fixtures, 1)
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

contract = CONTRACT_TEST.read_text(encoding="utf-8")
marker_anchor = '        "function missionRequirementsEnsureRecord(candidate, source)",\n'
marker_replacement = '        "function missionRequirementsPrimaryRuntime()",\n        "function missionRequirementsMissionIdentity(candidate, source)",\n        "function missionRequirementsEnsureRecord(candidate, source)",\n        "data-mcms-requirements-panel",\n'
if contract.count(marker_anchor) != 1:
    raise AssertionError("Mission Requirements contract marker anchor missing")
contract = contract.replace(marker_anchor, marker_replacement, 1)
CONTRACT_TEST.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
heading = "## [Unreleased]\n"
entry = """## [4.15.3] - 2026-07-18

### Fixed
- Mission Requirements now has one primary top-level runtime owner, preventing same-origin mission frames from mounting a second identical panel.
- Parent and frame representations of the same MissionChief mission are deduplicated by stable mission identity before panel creation.
- Existing Toolkit panels are adopted at the concrete MissionChief host and any stale duplicate panels are removed before observers are attached.

### Compatibility
- MissionChief remains the sole mission-window, requirements, selection and en-route authority; LSSM remains optional and is used only for explicit duplicate-equivalent detection.
- Desktop, Tablet and iOS normal-flow layouts and the seven equal interface systems are unchanged.

"""
if changelog.count(heading) != 1:
    raise AssertionError("CHANGELOG Unreleased heading missing")
changelog = changelog.replace(heading, heading + "\n" + entry, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

help_index = HELP_INDEX.read_text(encoding="utf-8")
help_index = help_index.replace("Guide for Toolkit v4.15.2", "Guide for Toolkit v4.15.3", 1)
HELP_INDEX.write_text(help_index, encoding="utf-8")

manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
manifest["guideVersion"] = NEW_VERSION
manifest["toolkitVersion"] = NEW_VERSION
manifest["updated"] = "2026-07-18"
manifest["runtimeGuidePatch"] = "Toolkit v4.15.3 documents single-owner Mission Requirements mounting while retaining Financial Command and all seven interface-system guide patches."
HELP_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

for relative in [
    ".github/development-packages/.keep-146",
    ".github/diagnostics/issue-146-mission-requirements-ownership.txt",
    ".github/diagnostics/issue-146-mission-requirements-candidates.txt",
]:
    path = ROOT / relative
    if path.exists():
        path.unlink()

run("node", "--check", str(SOURCE))
run("node", str(RUNTIME_TEST))
run(sys.executable, str(CONTRACT_TEST))
run(sys.executable, str(ROOT / ".github" / "scripts" / "validate_userscript.py"))

final = SOURCE.read_text(encoding="utf-8")
final_bytes = len(final.encode("utf-8"))
final_lines = final.count("\n") + 1
if final_bytes > 1_900_000 or final_lines > 31_000:
    raise AssertionError(f"v4.15.3 exceeds source budget: {final_bytes} bytes / {final_lines} lines")
print(f"Issue #146 hotfix validated: Toolkit v{NEW_VERSION}, {final_bytes} bytes, {final_lines} lines")
