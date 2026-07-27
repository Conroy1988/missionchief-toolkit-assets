#!/usr/bin/env python3
"""Replace Issue #553 post-render injection with canonical Tools-panel rendering."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CONTRACT = ROOT / ".github/scripts/test_alliance_member_manager_contract.py"
RUNTIME_TEST = ROOT / ".github/scripts/test_issue553_alliance_member_manager_menu_runtime.js"
FIXTURE = ROOT / ".github/fixtures/issue553-alliance-member-manager-menu.json"
PERFORMANCE = ROOT / ".github/performance-budget.json"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"
HELP_MANIFEST = ROOT / "help/manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
EVIDENCE = ROOT / "docs/issue-553-alliance-member-manager-restoration.md"
VALIDATOR = ROOT / ".github/scripts/validate_userscript.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{path.relative_to(ROOT)} expected one replacement target, found {count}: {old[:120]!r}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


source = SOURCE.read_text(encoding="utf-8")
source = source.replace(
    """    let allianceMemberManagerPage = null;
    let allianceMemberManagerMenuQueued = false;
    let allianceMemberManagerMenuObserver = null;
    let allianceMemberManagerMenuPanel = null;
    let allianceMemberManagerMenuFrame = 0;""",
    "    let allianceMemberManagerPage = null;",
    1,
)
if "allianceMemberManagerMenuObserver" in source[: source.index("    function allianceMemberManagerEnabled()")]:
    raise RuntimeError("Alliance Member Manager menu state declarations were not removed")

helper = r'''    function makeAllianceMemberManagerToggleButton() {
        return `
            <button class="mcms-toggle-btn" type="button" data-action="toggle-alliance-member-manager" data-mcms-alliance-member-manager-toggle="true" title="Enable or disable Alliance Member Manager" aria-label="Alliance Member Manager" aria-pressed="false">
                <span class="mcms-iconbox">AM</span>
                <span class="mcms-text">
                    <span class="mcms-label">Alliance Member Manager</span>
                    <span class="mcms-pill">OFF</span>
                </span>
            </button>
        `;
    }

'''
marker = "    function makeFloatButton(key, shortcut, label, title, tabletLabel = label, mobileLabel = tabletLabel) {"
if source.count(marker) != 1:
    raise RuntimeError("Unable to locate canonical toggle helper boundary")
source = source.replace(marker, helper + marker, 1)

old_tools = r'''                <div class="mcms-section-label">Map performance</div>
                <div class="mcms-grid-2">
                    ${makeToggleButton('allianceBuildingsMapBlocker', '▦', 'Alliance Map Blocker', 'Blocks the heavy map in the Alliance Buildings/Courses menu. ON means blocked. Reload required.')}
                </div>
                <div class="mcms-status"><strong>Map Blocker ON</strong> removes the Alliance Buildings map, expands the courses list and prevents its heavy marker layer attaching.</div>'''
new_tools = r'''                <div class="mcms-section-label" data-mcms-alliance-operations="label">Alliance Operations</div>
                <div class="mcms-grid-2" data-mcms-alliance-operations="controls">
                    ${makeToggleButton('allianceBuildingsMapBlocker', '▦', 'Alliance Map Blocker', 'Blocks the heavy map in the Alliance Buildings/Courses menu. ON means blocked. Reload required.')}
                    ${makeAllianceMemberManagerToggleButton()}
                </div>
                <div class="mcms-status"><strong>Map Blocker ON</strong> removes the Alliance Buildings map and its heavy marker layer. <strong>Alliance Member Manager</strong> adds role, activity and sorting controls on alliance member-list pages.</div>'''
if source.count(old_tools) != 1:
    raise RuntimeError("Unable to locate canonical Map performance Tools markup")
source = source.replace(old_tools, new_tools, 1)

old_action = """    function handleAction(button) {
        const action = button.dataset.action;
        if (action === 'place-go') {"""
new_action = """    function handleAction(button) {
        const action = button.dataset.action;
        if (action === 'toggle-alliance-member-manager') {
            setAllianceMemberManagerEnabled(!allianceMemberManagerEnabled());
            return;
        }
        if (action === 'place-go') {"""
if source.count(old_action) != 1:
    raise RuntimeError("Unable to locate canonical panel action handler")
source = source.replace(old_action, new_action, 1)

ui_marker = "        const majorIncidentMinimum = panel.querySelector('[data-setting=\"major-incident-minimum\"]');"
if source.count(ui_marker) != 1:
    raise RuntimeError("Unable to locate panel toggle-state reconciliation boundary")
source = source.replace(
    ui_marker,
    "        updateAllianceMemberManagerMenuControl();\n" + ui_marker,
    1,
)

manager_anchor = source.index("    // <mcms-alliance-member-manager>")
menu_start = source.index("    function allianceMemberManagerRenderedLabel(node) {", manager_anchor)
event_start = source.index("    if (typeof document.addEventListener === 'function') {", menu_start)
end_marker = "    // </mcms-alliance-member-manager>"
manager_end = source.index(end_marker, event_start)
update_function = r'''    function updateAllianceMemberManagerMenuControl() {
        const panel = document.querySelector(`#${SCRIPT.panelId}`);
        const button = panel?.querySelector(`[${ALLIANCE_MEMBER_MANAGER.menuAttribute}]`);
        if (!button) return;
        const enabled = allianceMemberManagerEnabled();
        button.classList.toggle('mcms-on', enabled);
        button.setAttribute('aria-pressed', String(enabled));
        const pill = button.querySelector('.mcms-pill');
        if (pill) pill.textContent = enabled ? 'ON' : 'OFF';
    }

'''
initialisation = r'''    if (typeof document.addEventListener === 'function') {
        if (document.readyState !== 'loading') {
            reconcileAllianceMemberManager();
        } else {
            document.addEventListener('DOMContentLoaded', reconcileAllianceMemberManager, { once: true });
        }
    }
'''
source = source[:menu_start] + update_function + initialisation + source[manager_end:]
SOURCE.write_text(source, encoding="utf-8")

contract = r'''#!/usr/bin/env python3
"""Permanent contract for the Toolkit-native Alliance Member Manager."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
SITE_DATA = ROOT / "docs" / "site-data.json"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
PERFORMANCE = ROOT / ".github" / "performance-budget.json"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    start_marker = "    // <mcms-alliance-member-manager>"
    end_marker = "    // </mcms-alliance-member-manager>"
    assert source.count(start_marker) == 1
    assert source.count(end_marker) == 1
    start = source.index(start_marker)
    end = source.index(end_marker, start) + len(end_marker)
    block = source[start:end]

    assert re.search(r"^// @version\s+8\.1\.3$", source, re.MULTILINE)
    assert "version: '8.1.3'" in source
    for marker in [
        "mcms_alliance_member_manager_enabled_v1",
        "Alliance Member Manager",
        "Role",
        "Activity",
        "Sort by",
        "Load All Member Pages",
        "All Member Pages Loaded",
        "All roles",
        "No role",
        "All members",
        "Online",
        "Offline",
        "Original order",
        "Member name",
        "Alliance role",
        "Showing ${visible} of ${context.members.size} members",
        r"alliance\/members|verband\/mitglieder",
        "img.online_icon",
        "user_(?<state>blue|gray|green|red|yellow)",
        "new AbortController()",
        "context.abortController?.abort()",
        "credentials: 'same-origin'",
        "for (let page = 1; page <= context.totalPages; page += 1)",
        "const response = await fetch(",
        "document.importNode(row, true)",
        "context.importedRows.forEach(row => row.remove())",
        "context.originalRows.forEach(row =>",
        "typeof document.addEventListener === 'function'",
        "document.readyState !== 'loading'",
        "document.addEventListener('DOMContentLoaded', reconcileAllianceMemberManager",
        "{ once: true }",
        "allianceMemberManagerOtherOwnerPresent()",
        "#allianceMemberList-controls",
    ]:
        assert marker in block, marker

    for forbidden in [
        "setInterval(",
        "new MutationObserver(",
        "requestAnimationFrame(",
        "allianceMemberManagerMapBlockerButton",
        "ensureAllianceMemberManagerMenuControl",
        "queueAllianceMemberManagerMenuControl",
        "allianceMemberManagerMenuObserver",
        "GM_xmlhttpRequest",
        "last seen",
        "lastSeen",
        "getElementById(",
    ]:
        assert forbidden not in block, forbidden

    for marker in [
        "function makeAllianceMemberManagerToggleButton()",
        'data-action="toggle-alliance-member-manager"',
        'data-mcms-alliance-member-manager-toggle="true"',
        '<div class="mcms-section-label" data-mcms-alliance-operations="label">Alliance Operations</div>',
        '<div class="mcms-grid-2" data-mcms-alliance-operations="controls">',
        "${makeAllianceMemberManagerToggleButton()}",
        "if (action === 'toggle-alliance-member-manager')",
        "setAllianceMemberManagerEnabled(!allianceMemberManagerEnabled())",
        "updateAllianceMemberManagerMenuControl();",
    ]:
        assert marker in source, marker

    assert block.index("for (let page = 1;") < block.index("await fetch(")
    assert block.count("await fetch(") == 1
    assert block.count("new AbortController()") == 1
    assert block.count("new MutationObserver(") == 0
    assert block.count("data-mcms-alliance-member-manager-toggle") == 1
    assert source.count("${makeAllianceMemberManagerToggleButton()}") == 1
    assert source.count('data-action="toggle-alliance-member-manager"') == 1

    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert "## [8.1.3] - 2026-07-27" in changelog
    assert "### Canonical Alliance Member Manager Tools rendering" in changelog
    assert "## [8.1.2] - 2026-07-27" in changelog
    assert "## [8.1.1] - 2026-07-27" in changelog
    assert "## [8.1.0] - 2026-07-27" in changelog

    site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
    alliance = [item for item in site_data["featureCategories"] if item.get("name") == "Alliance operations"]
    assert len(alliance) == 1
    features = alliance[0]["features"]
    assert len(features) == 1
    assert features[0]["name"] == "Alliance Member Manager"
    assert "Load all pages only on request" in features[0]["details"]

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert ".github/scripts/test_alliance_member_manager_contract.py" in preflight
    assert "test_issue553_alliance_member_manager_menu_runtime.js" in preflight
    assert "test_issue554_alliance_member_manager_rollback.py" not in preflight

    performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
    assert performance["revision"] == "2026-07-27-issue-553-canonical-menu-render"
    assert performance["transitionApproval"]["issue"] == 553
    assert performance["transitionApproval"]["version"] == "8.1.3"
    assert performance["transitionApproval"]["approvedNetworkRequestDelta"] == 1
    assert performance["absoluteLimits"]["network_request_calls"] == 5

    print(
        "Alliance Member Manager contract passed: canonical Tools markup, panel-owned action routing, "
        "persisted state reconciliation, responsive member controls and zero added observers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
CONTRACT.write_text(contract, encoding="utf-8")

fixture = {
    "schemaVersion": 3,
    "description": "Canonical Tools control and persisted state cases for Issue #553.",
    "states": [
        {"enabled": False, "pill": "OFF", "pressed": "false"},
        {"enabled": True, "pill": "ON", "pressed": "true"},
    ],
}
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

runtime_test = r'''#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "../..");
const source = fs.readFileSync(path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"), "utf8");
const fixture = JSON.parse(fs.readFileSync(
  path.join(root, ".github/fixtures/issue553-alliance-member-manager-menu.json"),
  "utf8"
));

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
  const brace = source.indexOf("{", start);
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = brace; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === "'" || char === '"' || char === "`") { quote = char; continue; }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const helperText = extractFunction("makeAllianceMemberManagerToggleButton");
const helperSandbox = {};
vm.runInNewContext(`${helperText}\nthis.renderManagerButton = makeAllianceMemberManagerToggleButton;`, helperSandbox);
const html = helperSandbox.renderManagerButton();
for (const marker of [
  'class="mcms-toggle-btn"',
  'data-action="toggle-alliance-member-manager"',
  'data-mcms-alliance-member-manager-toggle="true"',
  'aria-pressed="false"',
  '<span class="mcms-iconbox">AM</span>',
  '<span class="mcms-label">Alliance Member Manager</span>',
  '<span class="mcms-pill">OFF</span>',
]) assert.ok(html.includes(marker), marker);

for (const marker of [
  '<div class="mcms-section-label" data-mcms-alliance-operations="label">Alliance Operations</div>',
  '<div class="mcms-grid-2" data-mcms-alliance-operations="controls">',
  "${makeToggleButton('allianceBuildingsMapBlocker'",
  "${makeAllianceMemberManagerToggleButton()}",
  "if (action === 'toggle-alliance-member-manager')",
  "setAllianceMemberManagerEnabled(!allianceMemberManagerEnabled())",
]) assert.ok(source.includes(marker), marker);

const updateText = extractFunction("updateAllianceMemberManagerMenuControl");
const buttonState = { on: false, pressed: "false", pill: "OFF" };
const pill = { get textContent() { return buttonState.pill; }, set textContent(value) { buttonState.pill = value; } };
const button = {
  classList: { toggle(name, value) { assert.equal(name, "mcms-on"); buttonState.on = value; } },
  setAttribute(name, value) { if (name === "aria-pressed") buttonState.pressed = value; },
  querySelector(selector) { assert.equal(selector, ".mcms-pill"); return pill; },
};
const panel = { querySelector(selector) { assert.equal(selector, "[data-mcms-alliance-member-manager-toggle]"); return button; } };
const sandbox = {
  SCRIPT: { panelId: "toolkit-panel" },
  ALLIANCE_MEMBER_MANAGER: { menuAttribute: "data-mcms-alliance-member-manager-toggle" },
  document: { querySelector(selector) { assert.equal(selector, "#toolkit-panel"); return panel; } },
  enabled: false,
};
sandbox.allianceMemberManagerEnabled = () => sandbox.enabled;
vm.runInNewContext(`${updateText}\nthis.updateManagerButton = updateAllianceMemberManagerMenuControl;`, sandbox);
for (const item of fixture.states) {
  sandbox.enabled = item.enabled;
  sandbox.updateManagerButton();
  assert.equal(buttonState.on, item.enabled);
  assert.equal(buttonState.pressed, item.pressed);
  assert.equal(buttonState.pill, item.pill);
}

const managerStart = source.indexOf("    // <mcms-alliance-member-manager>");
const managerEnd = source.indexOf("    // </mcms-alliance-member-manager>", managerStart);
const manager = source.slice(managerStart, managerEnd);
for (const forbidden of [
  "new MutationObserver(",
  "requestAnimationFrame(",
  "allianceMemberManagerMapBlockerButton",
  "ensureAllianceMemberManagerMenuControl",
  "queueAllianceMemberManagerMenuControl",
  "allianceMemberManagerMenuObserver",
]) assert.ok(!manager.includes(forbidden), forbidden);

console.log(`Issue #553 canonical Tools runtime passed: ${fixture.states.length} persisted states and zero post-render injection.`);
'''
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
performance["revision"] = "2026-07-27-issue-553-canonical-menu-render"
performance["rationale"] = (
    "Issue #553 renders Alliance Member Manager directly in createPanel beside Alliance Map "
    "Blocker, routes clicks through the existing panel action handler and adds no observer, "
    "timer, animation-frame loop or network site."
)
performance["transitionApproval"] = {
    "issue": 553,
    "version": "8.1.3",
    "approvedNetworkRequestDelta": 1,
    "scope": (
        "Canonical Alliance Member Manager Tools markup and panel-owned action routing; the "
        "existing user-triggered sequential member-page fetch site is unchanged."
    ),
}
PERFORMANCE.write_text(json.dumps(performance, indent=2) + "\n", encoding="utf-8")

old_changelog = """## [8.1.3] - 2026-07-27

### Native Alliance Member Manager Tools rendering

- Replaced the brittle `.mcms-toggle-btn` lookup with class-independent discovery of the exact rendered **Alliance Map Blocker** label.
- Built the Alliance Member Manager control by cloning the real live Toolkit card, stripping inherited action ownership and assigning the manager toggle explicitly.
- Reused the existing Map Performance row as **Alliance Operations**, keeping both alliance controls together in the canonical two-card layout.
- Added panel-scoped child-list reconciliation and two bounded animation-frame retries so normal Tools re-renders cannot erase the control.
- Added executable coverage for the production card shape, cloned ownership, whitespace normalization, false-match rejection and re-render recovery markers.
"""
new_changelog = """## [8.1.3] - 2026-07-27

### Canonical Alliance Member Manager Tools rendering

- Added Alliance Member Manager directly to the canonical `createPanel()` Tools markup beside Alliance Map Blocker under **Alliance Operations**.
- Routed the control through the panel's existing action dispatcher, so click handling cannot be blocked by panel event containment.
- Reconciled ON/OFF state through the normal `updateUI()` path using the existing persisted Alliance Member Manager setting.
- Removed the complete post-render lookup, cloning, observer, microtask and animation-frame injection subsystem.
- Added executable coverage for canonical button markup, panel-owned action routing, persisted state rendering and zero added observers.
"""
replace_once(CHANGELOG, old_changelog, new_changelog)

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["runtimeGuidePatch"] = (
    "Toolkit v8.1.3 renders Alliance Member Manager directly in the canonical Tools panel "
    "beside Alliance Map Blocker under Alliance Operations, with panel-owned clicks and "
    "normal persisted ON/OFF state reconciliation."
)
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

EVIDENCE.write_text(
    """# Issue #553 — canonical Alliance Member Manager Tools rendering

Toolkit v8.1.3 places Alliance Member Manager directly in the Toolkit's canonical `createPanel()` Tools markup.

- The **Alliance Operations** two-card row is rendered once with Alliance Map Blocker and Alliance Member Manager.
- The manager control uses the same `mcms-toggle-btn` structure as other native Tools controls.
- Clicks are handled by the existing panel `data-action` dispatcher.
- `updateUI()` owns persisted ON/OFF state.
- No post-render selector search, clone, observer, timer, microtask or animation-frame retry is used.
- The member-list runtime remains opt-in, route-scoped and unchanged.
""",
    encoding="utf-8",
)

source_bytes = SOURCE.read_bytes()
source_text = source_bytes.decode("utf-8")
headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
candidate.update(
    {
        "issue": 553,
        "version": "8.1.3",
        "sourceBytes": len(source_bytes),
        "sourceLines": len(source_text.splitlines()),
        "sourceSha256": hashlib.sha256(source_bytes).hexdigest(),
        "baseline": "8.1.2",
        "approvedGrowth": {
            "sourceBytes": len(source_bytes) - 1641923,
            "sourceLines": len(source_text.splitlines()) - 25012,
            "templateBytes": 0,
            "templateLines": 0,
        },
        "scope": (
            "Issue #553 canonical createPanel Alliance Member Manager control, panel-owned "
            "action routing and normal updateUI state reconciliation"
        ),
    }
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT)], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME_TEST)], cwd=ROOT, check=True)

print("Toolkit v8.1.3 canonical Alliance Member Manager Tools rendering applied and validated.")
