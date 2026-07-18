#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DOC = ROOT / "docs" / "issue-171-ajax-dispatch-root-contract.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
DIST_SUMS = ROOT / "dist" / "SHA256SUMS.txt"
DIST_MANIFEST = ROOT / "dist" / "release-manifest.json"
VERSION = "4.16.4"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.16.3", "// @version      4.16.4", "metadata version")
source = replace_once(source, "        version: '4.16.3',", "        version: '4.16.4',", "runtime version")
source = replace_once(
    source,
    """        const operational = root.querySelector?.('#vehicle_show_table_body_all, #mission_vehicle_driving, #mission_vehicle_at_mission, #mission_reply_content, .mission_reply_content');
        if (operational?.parentNode) return missionRequirementsPlacementBlock(root, operational);
        return { root, parent: root, before: root.firstChild || null };""",
    """        // Operational regions may load before the mission header during AJAX dispatch.
        // They remain data sources only and are never valid panel hosts.
        return null;""",
    "remove operational placement fallback",
)
source = replace_once(
    source,
    """        if (native && native.isConnected !== false) return native;
        if (supplied?.getAttribute?.('data-mcms-requirements-anchor') === '1' && supplied.isConnected !== false) return supplied;
        return missionRequirementsExplicitSource(supplied) ? supplied : null;""",
    """        if (native && native.isConnected !== false) return native;
        if (supplied?.getAttribute?.('data-mcms-requirements-anchor') === '1' && supplied.isConnected !== false) {
            const placement = missionRequirementsPlacement({ ...candidate, root, mount: root }, supplied);
            if (placement?.parent) return supplied;
            supplied.remove?.();
        }
        return missionRequirementsExplicitSource(supplied) ? supplied : null;""",
    "reject premature anchor",
)
source = replace_once(
    source,
    """        if (!anchor || anchor.isConnected === false) {
            anchor = root.ownerDocument.createElement('span');
            anchor.hidden = true;
            anchor.setAttribute('aria-hidden', 'true');
            anchor.setAttribute('data-mcms-requirements-anchor', '1');
        }
        const placement = missionRequirementsPlacement({ ...candidate, root, mount: root });
        placement?.parent?.insertBefore?.(anchor, placement.before || null);
        return anchor;""",
    """        const placement = missionRequirementsPlacement({ ...candidate, root, mount: root });
        if (!placement?.parent) {
            anchor?.remove?.();
            return null;
        }
        if (!anchor || anchor.isConnected === false) {
            anchor = root.ownerDocument.createElement('span');
            anchor.hidden = true;
            anchor.setAttribute('aria-hidden', 'true');
            anchor.setAttribute('data-mcms-requirements-anchor', '1');
        }
        placement.parent.insertBefore?.(anchor, placement.before || null);
        return anchor;""",
    "defer anchor until header",
)
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "        version: '4.16.3'", "        version: '4.16.4'", "runtime fixture version")
runtime = replace_once(
    runtime,
    """const issue171FallbackDoc = new FakeDocument();
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

const delayedDoc = new FakeDocument();""",
    """const issue171FallbackDoc = new FakeDocument();
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
let issue171HeaderReady = false;
const issue171LateTitle = new FakeElement('h1', issue171FallbackDoc);
issue171LateTitle.id = 'mission_caption';
const issue171LateAddress = new FakeElement('div', issue171FallbackDoc);
issue171LateAddress.id = 'mission_address';
const issue171LateSource = new FakeElement('div', issue171FallbackDoc);
issue171LateSource.id = 'missing_text';
issue171LateSource.textContent = issue171LateSource.innerText = 'Missing Vehicles: 1 Police car';
issue171LateSource.queryAllHandler = () => [];
issue171FallbackRoot.queryHandler = selector => {
    if (selector.includes('#vehicle_show_table_body_all')) return issue171FallbackBody;
    if (!issue171HeaderReady) return null;
    if (selector === '#missing_text') return issue171LateSource;
    if (selector.includes('#mission_address')) return issue171LateAddress;
    if (selector.includes('#mission_caption')) return issue171LateTitle;
    if (selector === '[data-mcms-requirements-anchor="1"]') return issue171FallbackRoot.children.find(child => child.getAttribute?.('data-mcms-requirements-anchor') === '1') || null;
    return null;
};
issue171FallbackRoot.queryAllHandler = () => [];
const issue171FallbackCandidate = { root: issue171FallbackRoot, mount: issue171FallbackRoot, missionId: 255577321 };
assert.strictEqual(api.placement(issue171FallbackCandidate, null), null, 'vehicle-only AJAX state has no valid panel placement');
assert.strictEqual(api.anchorForCandidate(issue171FallbackCandidate), null, 'vehicle-only AJAX state creates no placeholder');
candidates = [issue171FallbackCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'vehicle-only AJAX state creates no record');
issue171HeaderReady = true;
issue171FallbackRoot.insertBefore(issue171LateTitle, issue171FallbackArea);
issue171FallbackRoot.insertBefore(issue171LateAddress, issue171FallbackArea);
issue171FallbackRoot.insertBefore(issue171LateSource, issue171FallbackArea);
api.scan();
flushAnimationFrames();
const issue171LateRecord = Array.from(api.records.values())[0];
assert(issue171LateRecord, 'header-ready AJAX state creates a record');
assert.strictEqual(issue171LateRecord.panel.parentNode, issue171FallbackRoot, 'header-ready panel mounts in mission root');
const issue171LatePanelIndex = issue171FallbackRoot.children.indexOf(issue171LateRecord.panel);
assert(issue171FallbackRoot.children.indexOf(issue171LateAddress) < issue171LatePanelIndex, 'late panel mounts below address');
assert(issue171LatePanelIndex < issue171FallbackRoot.children.indexOf(issue171LateSource), 'late panel mounts before missing_text');
api.clear();
candidates = [];

const delayedDoc = new FakeDocument();""",
    "staged AJAX fixture",
)
runtime = replace_once(
    runtime,
    """const missingDoc = new FakeDocument();
missingDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9901' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const missingCandidate = makeMissionCandidateWithoutSource(missingDoc);
candidates = [missingCandidate];
api.scan();
flushAnimationFrames();
let missingRecord = Array.from(api.records.values())[0];
assert(missingRecord.panel.innerHTML.includes('Loading mission requirements'), 'source-less mission initially shows a bounded loading state');
missingRecord.startedAt = Date.now() - 2000;
api.scan();
flushAnimationFrames();
missingRecord = Array.from(api.records.values())[0];
assert(missingRecord.panel.innerHTML.includes('Unable to pull mission requirements'), 'source-less mission shows an explicit failure state');
assert(missingRecord.panel.innerHTML.includes('Report Mission'), 'failure state exposes Report Mission');

const unsafeSource = new FakeElement('div', missingDoc);""",
    """const missingDoc = new FakeDocument();
missingDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9901' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const missingCandidate = makeMissionCandidateWithoutSource(missingDoc);
candidates = [missingCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'source-less mission waits for a valid header or native source');

const unsafeSource = new FakeElement('div', missingDoc);""",
    "source-less wait fixture",
)
runtime = replace_once(
    runtime,
    "missingRecord.candidate.source = unsafeSource;",
    """api.scan();
flushAnimationFrames();
let missingRecord = Array.from(api.records.values())[0];
assert(missingRecord, 'native source creates a record after source-less wait');""",
    "source-less recovery fixture",
)
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    """    assert \"return { root, parent: operational.parentNode, before: operational };\" not in source
    assert \"missionRequirementsPlacementBlock(root, operational)\" in source
""",
    """    assert \"return { root, parent: operational.parentNode, before: operational };\" not in source
    assert \"missionRequirementsPlacementBlock(root, operational)\" not in source
    assert \"const operational = root.querySelector?.\" not in source
""",
    "header-only contract",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
changelog = replace_once(
    changelog,
    "## [Unreleased]\n\n",
    """## [Unreleased]

## [4.16.4] - 2026-07-18

### Fixed
- Mission Requirements now waits for the active mission's native requirements source or confirmed title/address before mounting in an AJAX dispatch window.
- Available Units, vehicle/response tables and incident-note regions remain data sources only and can no longer become emergency panel hosts.
- Premature placeholder anchors are removed until a valid header placement exists.

### Validation
- Added staged-AJAX coverage proving vehicle-only loading creates no panel and the completed mission header mounts the panel beneath the address and before `#missing_text`.

""",
    "changelog",
)
CHANGELOG.write_text(changelog, encoding="utf-8")
DOC.write_text(
    "# Issue #171 / #173 — AJAX dispatch header placement contract\n\n"
    "Mission Requirements may mount only when the active mission root exposes native `#missing_text` or a confirmed mission title/address.\n\n"
    "Available Units, vehicle tables, responding/on-site tables and incident-note regions are data sources only. If they load first, the Toolkit waits without creating a panel or placeholder. Once the header or native requirements source appears, the panel mounts beneath the address/title and before `#missing_text`.\n",
    encoding="utf-8",
)
HELP_INDEX.write_text(HELP_INDEX.read_text(encoding="utf-8").replace("Toolkit v4.16.3", "Toolkit v4.16.4"), encoding="utf-8")
help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-18"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.16.4 waits for the mission header or native requirements source before mounting during AJAX dispatch loading."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")
digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
DIST_SUMS.write_text(f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n", encoding="utf-8")
manifest = json.loads(DIST_MANIFEST.read_text(encoding="utf-8"))
manifest["version"] = VERSION
manifest["sha256"] = digest
manifest["bytes"] = len(source.encode("utf-8"))
manifest["lines"] = len(source.splitlines())
manifest["metadata"]["runtimeVersion"] = VERSION
manifest["metadata"]["warnings"] = []
manifest["baselineHashMatch"] = None
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
DIST_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

assert SOURCE.read_bytes() == DIST_USER.read_bytes() == DIST_TEXT.read_bytes()
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME)], cwd=ROOT, check=True)
subprocess.run(["python3", str(CONTRACT)], cwd=ROOT, check=True)
subprocess.run(["bash", str(ROOT / ".github" / "scripts" / "run_userscript_preflight.sh")], cwd=ROOT, check=True)
subprocess.run(["python3", str(ROOT / ".github" / "scripts" / "validate_userscript.py")], cwd=ROOT, check=True)
print(f"Issue #173 v{VERSION} candidate SHA-256: {digest}")
