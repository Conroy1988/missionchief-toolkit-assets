#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
DIST_SUMS = ROOT / "dist" / "SHA256SUMS.txt"
DIST_MANIFEST = ROOT / "dist" / "release-manifest.json"
DIAGNOSTIC = ROOT / ".github" / "diagnostics" / "issue-171-source-inspection.txt"
DOC = ROOT / "docs" / "issue-171-ajax-dispatch-root-contract.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.16.2", "// @version      4.16.3", "metadata version")
source = replace_once(source, "        version: '4.16.2',", "        version: '4.16.3',", "runtime version")

old_helpers = '''    function missionRequirementsDirectChild(root, node) {
        let current = node;
        while (current?.parentNode && current.parentNode !== root) current = current.parentNode;
        return current?.parentNode === root ? current : node;
    }

    function missionRequirementsPlacement(candidate, source = null) {'''
new_helpers = '''    function missionRequirementsDirectChild(root, node) {
        let current = node;
        while (current?.parentNode && current.parentNode !== root) current = current.parentNode;
        return current?.parentNode === root ? current : node;
    }

    function missionRequirementsPlacementHostUnsafe(node, boundary = null) {
        const unsafeTags = new Set(['TABLE', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TD', 'TH', 'COLGROUP']);
        let current = node;
        while (current && current !== boundary) {
            if (unsafeTags.has(String(current.tagName || '').toUpperCase())) return true;
            current = current.parentNode;
        }
        return false;
    }

    function missionRequirementsPlacementBlock(root, node) {
        if (!root || !node) return null;
        let target = node;
        let current = node;
        while (current && current !== root) {
            if (String(current.tagName || '').toUpperCase() === 'TABLE') target = current;
            current = current.parentNode;
        }
        const block = missionRequirementsDirectChild(root, target);
        const parent = block?.parentNode || root;
        if (!parent || missionRequirementsPlacementHostUnsafe(parent, root?.parentNode || null)) {
            return { root, parent: root, before: root.firstChild || null };
        }
        return { root, parent, before: block };
    }

    function missionRequirementsPlacement(candidate, source = null) {'''
source = replace_once(source, old_helpers, new_helpers, "placement helpers")

source = replace_once(
    source,
    "        if (explicit?.parentNode) return { root, parent: explicit.parentNode, before: explicit };",
    "        if (explicit?.parentNode) return missionRequirementsPlacementHostUnsafe(explicit.parentNode, root?.parentNode || null)\n            ? missionRequirementsPlacementBlock(root, explicit)\n            : { root, parent: explicit.parentNode, before: explicit };",
    "explicit source placement safety",
)
source = replace_once(
    source,
    "        if (operational?.parentNode) return { root, parent: operational.parentNode, before: operational };",
    "        if (operational?.parentNode) return missionRequirementsPlacementBlock(root, operational);",
    "operational placement safety",
)

old_root = '''    function missionRequirementsCandidateRoot(candidate) {
        const root = candidate?.root || candidate?.mount;
        if (!root) return null;
        if (root.matches?.('#mission_form, form[action*="/missions/"], #mission_content')) return root;
        return root.querySelector?.('#mission_form, form[action*="/missions/"], #mission_content') || root;
    }'''
new_root = '''    function missionRequirementsCandidateRoot(candidate) {
        const missionSelector = '#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]';
        const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
        const nodes = [candidate?.source, candidate?.root, candidate?.mount].filter(Boolean);
        const missionWithin = node => {
            if (!node) return null;
            if (node.matches?.(missionSelector)) return node;
            const closest = node.closest?.(missionSelector);
            if (closest) return closest;
            return node.querySelector?.(missionSelector) || null;
        };
        for (const node of nodes) {
            const mission = missionWithin(node);
            if (mission) return mission;
        }
        for (const node of nodes) {
            const windowRoot = node.matches?.(windowSelector) ? node : node.closest?.(windowSelector);
            if (windowRoot) return missionWithin(windowRoot) || windowRoot;
        }
        for (const node of nodes) {
            try {
                const frame = node.ownerDocument?.defaultView?.frameElement || null;
                if (!frame) continue;
                const frameMission = missionWithin(frame);
                if (frameMission) return frameMission;
                const frameWindow = frame.matches?.(windowSelector) ? frame : frame.closest?.(windowSelector);
                if (frameWindow) return missionWithin(frameWindow) || frameWindow;
            } catch (err) {}
        }
        return candidate?.root || candidate?.mount || candidate?.source || null;
    }'''
source = replace_once(source, old_root, new_root, "candidate root promotion")
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME_TEST.read_text(encoding="utf-8")
runtime = replace_once(runtime, "        version: '4.16.2'", "        version: '4.16.3'", "runtime fixture version")
old_insert = '''    insertBefore(child, reference) {
        child.parentNode = this;
        child.ownerDocument ||= this.ownerDocument;
        child.isConnected = true;
        const index = this.children.indexOf(reference);
        if (index >= 0) this.children.splice(index, 0, child);
        else this.children.push(child);
        child.ownerDocument?.nodes.add(child);
        return child;
    }'''
new_insert = '''    insertBefore(child, reference) {
        if (child.parentNode) child.parentNode.children = child.parentNode.children.filter(item => item !== child);
        child.parentNode = this;
        child.ownerDocument ||= this.ownerDocument;
        child.isConnected = true;
        const index = this.children.indexOf(reference);
        if (index >= 0) this.children.splice(index, 0, child);
        else this.children.push(child);
        child.ownerDocument?.nodes.add(child);
        return child;
    }'''
runtime = replace_once(runtime, old_insert, new_insert, "fixture reparenting")
runtime = replace_once(
    runtime,
    "    sourceForCandidate: missionRequirementsSourceForCandidate,\n    anchorForCandidate: missionRequirementsAnchorForCandidate,",
    "    sourceForCandidate: missionRequirementsSourceForCandidate,\n    candidateRoot: missionRequirementsCandidateRoot,\n    placement: missionRequirementsPlacement,\n    anchorForCandidate: missionRequirementsAnchorForCandidate,",
    "fixture API exports",
)

fixture_block = '''api.clear();

const issue171Doc = new FakeDocument();
issue171Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/' }, navigator: context.pageWindow.navigator, innerWidth: 1600, innerHeight: 900 };
const issue171Root = new FakeElement('form', issue171Doc);
const issue171MissionSelector = '#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]';
issue171Root.matchSet.add(issue171MissionSelector);
issue171Root.setAttribute('action', '/missions/255577320');
const issue171Title = new FakeElement('h1', issue171Doc);
issue171Title.id = 'mission_caption';
const issue171Address = new FakeElement('div', issue171Doc);
issue171Address.id = 'mission_address';
const issue171Source = new FakeElement('div', issue171Doc);
issue171Source.id = 'missing_text';
issue171Source.textContent = issue171Source.innerText = 'Missing Vehicles: 3 Police cars';
issue171Source.queryAllHandler = () => [];
const issue171VehicleArea = new FakeElement('div', issue171Doc);
issue171VehicleArea.id = 'available_units';
const issue171Table = new FakeElement('table', issue171Doc);
const issue171Body = new FakeElement('tbody', issue171Doc);
issue171Body.id = 'vehicle_show_table_body_all';
issue171Root.appendChild(issue171Title);
issue171Root.appendChild(issue171Address);
issue171Root.appendChild(issue171Source);
issue171Root.appendChild(issue171VehicleArea);
issue171VehicleArea.appendChild(issue171Table);
issue171Table.appendChild(issue171Body);
issue171Body.closestMap.set(issue171MissionSelector, issue171Root);
issue171Root.queryHandler = selector => {
    if (selector === '#missing_text') return issue171Source;
    if (selector.includes('#mission_address')) return issue171Address;
    if (selector.includes('#mission_caption')) return issue171Title;
    if (selector.includes('#vehicle_show_table_body_all')) return issue171Body;
    if (selector === issue171MissionSelector) return issue171Root;
    if (selector === '[data-mcms-requirements-anchor="1"]') return issue171Root.children.find(child => child.getAttribute?.('data-mcms-requirements-anchor') === '1') || null;
    return null;
};
issue171Root.queryAllHandler = selector => selector.includes('.vehicle_checkbox') || selector.includes('#mission_vehicle_') ? [] : [];
const issue171NestedCandidate = { root: issue171Body, mount: issue171Body, missionId: 255577320 };
assert.strictEqual(api.candidateRoot(issue171NestedCandidate), issue171Root, 'nested AJAX vehicle candidate promotes to mission root');
const issue171Placement = api.placement(issue171NestedCandidate, null);
assert.strictEqual(issue171Placement.parent, issue171Root, 'nested AJAX placement uses mission root');
assert.strictEqual(issue171Placement.before, issue171Source, 'nested AJAX placement remains before native requirements');
candidates = [issue171NestedCandidate];
api.scan();
flushAnimationFrames();
const issue171Record = Array.from(api.records.values())[0];
assert.strictEqual(issue171Record.panel.parentNode, issue171Root, 'normal dispatch panel mounts beneath mission header');
issue171Table.insertBefore(issue171Record.panel, issue171Body);
assert.strictEqual(issue171Record.panel.parentNode, issue171Table, 'fixture reproduces invalid table mounting');
api.scan();
flushAnimationFrames();
assert.strictEqual(issue171Record.panel.parentNode, issue171Root, 'subsequent scan re-homes a mis-mounted panel');
assert(!['TABLE', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TD', 'TH'].includes(issue171Record.panel.parentNode.tagName), 'panel host is never table structure');
api.clear();
candidates = [];

const issue171FallbackDoc = new FakeDocument();
issue171FallbackDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/255577321' } };
const issue171FallbackRoot = new FakeElement('div', issue171FallbackDoc);
const issue171WindowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
issue171FallbackRoot.matchSet.add(issue171WindowSelector);
const issue171FallbackArea = new FakeElement('div', issue171FallbackDoc);
const issue171FallbackTable = new FakeElement('table', issue171FallbackDoc);
const issue171FallbackBody = new FakeElement('tbody', issue171FallbackDoc);
issue171FallbackBody.id = 'vehicle_show_table_body_all';
issue171FallbackRoot.appendChild(issue171FallbackArea);
issue171FallbackArea.appendChild(issue171FallbackTable);
issue171FallbackTable.appendChild(issue171FallbackBody);
issue171FallbackRoot.queryHandler = selector => selector.includes('#vehicle_show_table_body_all') ? issue171FallbackBody : null;
const issue171FallbackPlacement = api.placement({ root: issue171FallbackRoot, mount: issue171FallbackRoot }, null);
assert.strictEqual(issue171FallbackPlacement.parent, issue171FallbackRoot, 'operational fallback remains block-level');
assert.strictEqual(issue171FallbackPlacement.before, issue171FallbackArea, 'operational fallback inserts before vehicle area rather than tbody');

const delayedDoc = new FakeDocument();'''
runtime = replace_once(runtime, "api.clear();\n\nconst delayedDoc = new FakeDocument();", fixture_block, "Issue 171 runtime fixture")
RUNTIME_TEST.write_text(runtime, encoding="utf-8")

contract = CONTRACT_TEST.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '        "function missionRequirementsPlacement(candidate, source = null)",\n        "function missionRequirementsPlacePanel(candidate, source, panel)",',
    '        "function missionRequirementsPlacement(candidate, source = null)",\n        "function missionRequirementsPlacementHostUnsafe(node, boundary = null)",\n        "function missionRequirementsPlacementBlock(root, node)",\n        "function missionRequirementsPlacePanel(candidate, source, panel)",',
    "contract markers",
)
contract = replace_once(
    contract,
    '    assert source.count("missionRequirementsPanelId: \'mc-map-command-toolkit-mission-requirements\'") == 1\n',
    '    assert source.count("missionRequirementsPanelId: \'mc-map-command-toolkit-mission-requirements\'") == 1\n    assert "return { root, parent: operational.parentNode, before: operational };" not in source\n    assert "missionRequirementsPlacementBlock(root, operational)" in source\n',
    "contract table-host assertions",
)
CONTRACT_TEST.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [Unreleased]

## [4.16.3] - 2026-07-18

### Fixed
- Prevented the normal AJAX dispatch window from inserting Mission Requirements inside the Available Units vehicle table.
- Nested vehicle and table candidates now resolve upward to the enclosing mission form or lightbox before source lookup and placement.
- Existing panels that were temporarily mounted in table structure are re-homed beneath the mission header on the next scan.

### Validation
- Added a deterministic normal-dispatch fixture covering nested `tbody` discovery, safe block placement and active panel re-homing.

'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_html = HELP_INDEX.read_text(encoding="utf-8").replace("Toolkit v4.16.2", "Toolkit v4.16.3")
HELP_INDEX.write_text(help_html, encoding="utf-8")
help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "4.16.3"
help_manifest["toolkitVersion"] = "4.16.3"
help_manifest["updated"] = "2026-07-18"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.16.3 keeps normal AJAX dispatch Mission Requirements outside vehicle tables and re-homes nested candidates beneath the mission header."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

DOC.write_text(
    "# Issue #171 — AJAX dispatch Mission Requirements root contract\n\n"
    "Mission Requirements candidates discovered inside Available Units, vehicle tables, table sections, rows or cells must resolve upward to the enclosing active mission form/content or visible lightbox root.\n\n"
    "The panel must never be inserted into `table`, `thead`, `tbody`, `tfoot`, `tr`, `td`, `th` or `colgroup`. Operational fallbacks insert before the top-level block containing the vehicle table.\n\n"
    "Normal dispatch-button AJAX opening and standalone mission tabs use the same mission source and header placement. A subsequent scan re-homes any panel temporarily mounted by incomplete AJAX markup.\n",
    encoding="utf-8",
)

if DIAGNOSTIC.exists():
    DIAGNOSTIC.unlink()

DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")
digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
DIST_SUMS.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest = json.loads(DIST_MANIFEST.read_text(encoding="utf-8"))
manifest["version"] = "4.16.3"
manifest["sha256"] = digest
manifest["bytes"] = len(source.encode("utf-8"))
manifest["lines"] = len(source.splitlines())
manifest["metadata"]["runtimeVersion"] = "4.16.3"
manifest["metadata"]["warnings"] = []
manifest["baselineHashMatch"] = None
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
DIST_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

assert SOURCE.read_bytes() == DIST_USER.read_bytes() == DIST_TEXT.read_bytes()
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME_TEST)], cwd=ROOT, check=True)
subprocess.run(["python3", str(CONTRACT_TEST)], cwd=ROOT, check=True)
print(f"Issue 171 candidate v4.16.3 SHA-256: {digest}")
