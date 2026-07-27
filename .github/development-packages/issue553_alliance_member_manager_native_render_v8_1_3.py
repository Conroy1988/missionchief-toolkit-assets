#!/usr/bin/env python3
"""Apply Toolkit v8.1.3 Alliance Member Manager native-render correction."""
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
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
PERFORMANCE = ROOT / ".github/performance-budget.json"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"
HELP_MANIFEST = ROOT / "help/manifest.json"
HELP_INDEX = ROOT / "help/index.html"
CHANGELOG = ROOT / "CHANGELOG.md"
VALIDATOR = ROOT / ".github/scripts/validate_userscript.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{path.relative_to(ROOT)} expected one replacement target, found {count}: {old[:100]!r}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_region(path: Path, start_marker: str, end_marker: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError(f"Missing start marker in {path.relative_to(ROOT)}: {start_marker!r}")
    end = text.find(end_marker, start)
    if end < 0:
        raise RuntimeError(f"Missing end marker in {path.relative_to(ROOT)}: {end_marker!r}")
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


replace_once(SOURCE, "// @version      8.1.2", "// @version      8.1.3")
replace_once(SOURCE, "version: '8.1.2'", "version: '8.1.3'")
replace_once(
    SOURCE,
    "    let allianceMemberManagerPage = null;\n    let allianceMemberManagerMenuQueued = false;",
    """    let allianceMemberManagerPage = null;
    let allianceMemberManagerMenuQueued = false;
    let allianceMemberManagerMenuObserver = null;
    let allianceMemberManagerMenuPanel = null;
    let allianceMemberManagerMenuFrame = 0;""",
)

menu_functions = r'''    function allianceMemberManagerRenderedLabel(node) {
        return String(node?.textContent || '').replace(/\s+/gu, ' ').trim();
    }

    function allianceMemberManagerMapBlockerButton(panel) {
        const attributed = panel.querySelector(
            '[data-feature="allianceBuildingsMapBlocker"], ' +
            '[data-toggle-feature="allianceBuildingsMapBlocker"], ' +
            '[data-mcms-feature="allianceBuildingsMapBlocker"]'
        );
        if (attributed) return attributed;
        const renderedLabel = Array.from(panel.querySelectorAll('.mcms-label')).find(label =>
            allianceMemberManagerRenderedLabel(label) === 'Alliance Map Blocker'
        );
        return renderedLabel?.closest?.('button, a, [role="button"], [tabindex]')
            || renderedLabel?.parentElement?.parentElement
            || null;
    }

    function updateAllianceMemberManagerMenuControl() {
        const panel = document.querySelector(`#${SCRIPT.panelId}`);
        const button = panel?.querySelector(`[${ALLIANCE_MEMBER_MANAGER.menuAttribute}]`);
        if (!button) return;
        const enabled = allianceMemberManagerEnabled();
        button.classList.toggle('mcms-on', enabled);
        if (button.getAttribute('aria-pressed') !== String(enabled)) {
            button.setAttribute('aria-pressed', String(enabled));
        }
        const pill = button.querySelector('.mcms-pill');
        const nextPill = enabled ? 'ON' : 'OFF';
        if (pill && pill.textContent !== nextPill) pill.textContent = nextPill;
    }

    function bindAllianceMemberManagerMenuObserver(panel) {
        if (allianceMemberManagerMenuPanel === panel && allianceMemberManagerMenuObserver) return;
        allianceMemberManagerMenuObserver?.disconnect();
        allianceMemberManagerMenuObserver = null;
        allianceMemberManagerMenuPanel = panel;
        if (typeof MutationObserver !== 'function') return;
        allianceMemberManagerMenuObserver = new MutationObserver(() => {
            if (!panel.isConnected) return;
            if (
                !panel.querySelector(`[${ALLIANCE_MEMBER_MANAGER.menuAttribute}]`) &&
                allianceMemberManagerMapBlockerButton(panel)
            ) {
                queueAllianceMemberManagerMenuControl();
            }
        });
        allianceMemberManagerMenuObserver.observe(panel, { childList: true, subtree: true });
    }

    function ensureAllianceMemberManagerMenuControl() {
        allianceMemberManagerMenuQueued = false;
        const panel = document.querySelector(`#${SCRIPT.panelId}`);
        if (!panel) return false;
        bindAllianceMemberManagerMenuObserver(panel);
        const blocker = allianceMemberManagerMapBlockerButton(panel);
        if (!blocker) return false;

        let group = panel.querySelector(`[${ALLIANCE_MEMBER_MANAGER.operationsAttribute}="controls"]`);
        if (!group) {
            group = blocker.parentElement;
            if (!group) return false;
            group.setAttribute(ALLIANCE_MEMBER_MANAGER.operationsAttribute, 'controls');
        }

        const sectionLabels = Array.from(panel.querySelectorAll('.mcms-section-label'));
        const sectionLabel = sectionLabels.find(label => label.nextElementSibling === group)
            || sectionLabels.find(label =>
                allianceMemberManagerRenderedLabel(label).toUpperCase() === 'MAP PERFORMANCE'
            );
        if (sectionLabel) {
            if (allianceMemberManagerRenderedLabel(sectionLabel) !== 'Alliance Operations') {
                sectionLabel.textContent = 'Alliance Operations';
            }
            sectionLabel.setAttribute(ALLIANCE_MEMBER_MANAGER.operationsAttribute, 'label');
        }

        let button = group.querySelector(`[${ALLIANCE_MEMBER_MANAGER.menuAttribute}]`);
        if (!button) {
            button = blocker.cloneNode(true);
            for (const attribute of Array.from(button.getAttributeNames?.() || [])) {
                if (
                    attribute === 'id' ||
                    attribute === 'name' ||
                    attribute === 'value' ||
                    attribute === 'onclick' ||
                    attribute.startsWith('data-')
                ) {
                    button.removeAttribute(attribute);
                }
            }
            button.querySelectorAll?.('[id]').forEach(node => node.removeAttribute('id'));
            if ('type' in button) button.type = 'button';
            button.setAttribute(ALLIANCE_MEMBER_MANAGER.menuAttribute, 'true');
            button.setAttribute('aria-pressed', 'false');
            button.setAttribute('aria-label', 'Alliance Member Manager');
            button.title = 'Alliance Member Manager';
            button.classList?.remove('mcms-on');

            const icon = button.querySelector('.mcms-iconbox');
            if (icon) icon.textContent = 'AM';
            const label = button.querySelector('.mcms-label');
            if (label) label.textContent = 'Alliance Member Manager';
            const pill = button.querySelector('.mcms-pill');
            if (pill) pill.textContent = 'OFF';
            group.append(button);
        }
        updateAllianceMemberManagerMenuControl();
        return true;
    }

    function queueAllianceMemberManagerMenuControl() {
        if (allianceMemberManagerMenuQueued) return;
        allianceMemberManagerMenuQueued = true;
        const reconcile = () => {
            const panel = document.querySelector(`#${SCRIPT.panelId}`);
            if (panel) {
                bindAllianceMemberManagerMenuObserver(panel);
                ensureAllianceMemberManagerMenuControl();
            }
        };
        queueMicrotask(() => {
            allianceMemberManagerMenuQueued = false;
            reconcile();
            if (typeof requestAnimationFrame !== 'function') return;
            if (allianceMemberManagerMenuFrame) cancelAnimationFrame(allianceMemberManagerMenuFrame);
            allianceMemberManagerMenuFrame = requestAnimationFrame(() => {
                reconcile();
                allianceMemberManagerMenuFrame = requestAnimationFrame(() => {
                    allianceMemberManagerMenuFrame = 0;
                    reconcile();
                });
            });
        });
    }

'''
replace_region(
    SOURCE,
    "    function allianceMemberManagerMapBlockerButton(panel) {",
    "    if (typeof document.addEventListener === 'function') {",
    menu_functions,
)

contract = CONTRACT.read_text(encoding="utf-8")
contract = contract.replace(r'^// @version\s+8\.1\.2$', r'^// @version\s+8\.1\.3$')
contract = contract.replace("version: '8.1.2'", "version: '8.1.3'")
contract = contract.replace(
    '        "panel.querySelectorAll(\'.mcms-toggle-btn\')",\n'
    '        "button.querySelector(\'.mcms-label\')?.textContent?.trim() === \'Alliance Map Blocker\'",',
    '        "panel.querySelectorAll(\'.mcms-label\')",\n'
    '        "allianceMemberManagerRenderedLabel(label) === \'Alliance Map Blocker\'",\n'
    '        "button = blocker.cloneNode(true)",\n'
    '        "attribute.startsWith(\'data-\')",\n'
    '        "Alliance Operations",\n'
    '        "allianceMemberManagerMenuObserver.observe(panel, { childList: true, subtree: true })",\n'
    '        "requestAnimationFrame",',
)
contract = contract.replace('        "new MutationObserver(",\n', '')
contract = contract.replace(
    '    assert block.count("new AbortController()") == 1\n',
    '    assert block.count("new AbortController()") == 1\n'
    '    assert block.count("new MutationObserver(") == 1\n'
    '    assert ".mcms-toggle-btn" not in block\n'
    '    assert "setInterval(" not in block\n',
)
contract = contract.replace(
    '    assert "## [8.1.2] - 2026-07-27" in changelog\n'
    '    assert "### Alliance Member Manager restoration and menu hotfix" in changelog',
    '    assert "## [8.1.3] - 2026-07-27" in changelog\n'
    '    assert "### Native Alliance Member Manager Tools rendering" in changelog\n'
    '    assert "## [8.1.2] - 2026-07-27" in changelog',
)
contract = contract.replace(
    '    assert performance["revision"] == "2026-07-27-issue-553-alliance-member-manager-restoration"\n'
    '    assert performance["transitionApproval"]["issue"] == 553\n'
    '    assert performance["transitionApproval"]["version"] == "8.1.2"',
    '    assert performance["revision"] == "2026-07-27-issue-553-native-menu-render"\n'
    '    assert performance["transitionApproval"]["issue"] == 553\n'
    '    assert performance["transitionApproval"]["version"] == "8.1.3"',
)
contract = contract.replace(
    '        "current-state filtering, deterministic teardown, responsive UI and no recurring work."',
    '        "current-state filtering, cloned native Tools control, panel-scoped render reconciliation and deterministic teardown."',
)
CONTRACT.write_text(contract, encoding="utf-8")

fixture = {
    "schemaVersion": 2,
    "description": "Issue #553 production menu labels independent of rendered card CSS classes.",
    "cases": [
        {
            "name": "live rendered card with unrelated class",
            "attributeIndex": None,
            "labels": ["Clean", "Alliance Map Blocker", "Personal Missions"],
            "expectedIndex": 1,
        },
        {
            "name": "feature attribute remains authoritative",
            "attributeIndex": 0,
            "labels": ["Legacy attributed blocker", "Alliance Map Blocker"],
            "expectedIndex": 0,
        },
        {
            "name": "rendered whitespace is normalized",
            "attributeIndex": None,
            "labels": ["  Alliance   Map\nBlocker  "],
            "expectedIndex": 0,
        },
        {
            "name": "similar labels do not false-match",
            "attributeIndex": None,
            "labels": ["Alliance Map Block", "Alliance Member Manager"],
            "expectedIndex": None,
        },
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

const functionText = [
  extractFunction("allianceMemberManagerRenderedLabel"),
  extractFunction("allianceMemberManagerMapBlockerButton"),
].join("\n");
const sandbox = {};
vm.runInNewContext(
  `${functionText}\nthis.resolveBlocker = allianceMemberManagerMapBlockerButton;`,
  sandbox
);

for (const item of fixture.cases) {
  const cards = item.labels.map((textContent, index) => ({ index, kind: "canonical-live-card" }));
  const labels = item.labels.map((textContent, index) => ({
    textContent,
    closest(selector) {
      assert.equal(selector, 'button, a, [role="button"], [tabindex]');
      return cards[index];
    },
    parentElement: null,
  }));
  const panel = {
    querySelector(selector) {
      assert.match(selector, /allianceBuildingsMapBlocker/);
      return item.attributeIndex === null ? null : cards[item.attributeIndex];
    },
    querySelectorAll(selector) {
      assert.equal(selector, ".mcms-label");
      return labels;
    },
  };
  const result = sandbox.resolveBlocker(panel);
  if (item.expectedIndex === null) assert.equal(result, null, item.name);
  else assert.equal(result, cards[item.expectedIndex], item.name);
}

const managerStart = source.indexOf("    // <mcms-alliance-member-manager>");
const managerEnd = source.indexOf("    // </mcms-alliance-member-manager>", managerStart);
const manager = source.slice(managerStart, managerEnd);
for (const marker of [
  "button = blocker.cloneNode(true)",
  "attribute.startsWith('data-')",
  "sectionLabel.textContent = 'Alliance Operations'",
  "allianceMemberManagerMenuObserver.observe(panel, { childList: true, subtree: true })",
  "requestAnimationFrame",
  "group.append(button)",
]) assert.ok(manager.includes(marker), marker);
assert.equal((manager.match(/new MutationObserver\(/g) || []).length, 1);
assert.ok(!manager.includes("panel.querySelectorAll('.mcms-toggle-btn')"));

console.log(`Issue #553 native menu runtime passed: ${fixture.cases.length} class-independent cases plus clone and re-render ownership.`);
'''
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
performance["revision"] = "2026-07-27-issue-553-native-menu-render"
performance["rationale"] = (
    "Issue #553 renders the Alliance Member Manager from the canonical live Tools card and "
    "adds one panel-scoped child-list observer with coalesced bounded frame reconciliation; "
    "the member-page network and runtime budgets remain unchanged."
)
performance["transitionApproval"] = {
    "issue": 553,
    "version": "8.1.3",
    "approvedNetworkRequestDelta": 1,
    "scope": (
        "Native Alliance Member Manager Tools rendering with one panel-scoped observer, "
        "no timer loop and unchanged user-triggered sequential fetch ownership."
    ),
}
PERFORMANCE.write_text(json.dumps(performance, indent=2) + "\n", encoding="utf-8")

replace_once(
    CHANGELOG,
    "# Changelog\n\n",
    """# Changelog

## [8.1.3] - 2026-07-27

### Native Alliance Member Manager Tools rendering

- Replaced the brittle `.mcms-toggle-btn` lookup with class-independent discovery of the exact rendered **Alliance Map Blocker** label.
- Built the Alliance Member Manager control by cloning the real live Toolkit card, stripping inherited action ownership and assigning the manager toggle explicitly.
- Reused the existing Map Performance row as **Alliance Operations**, keeping both alliance controls together in the canonical two-card layout.
- Added panel-scoped child-list reconciliation and two bounded animation-frame retries so normal Tools re-renders cannot erase the control.
- Added executable coverage for the production card shape, cloned ownership, whitespace normalization, false-match rejection and re-render recovery markers.

""",
)

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "8.1.3"
help_manifest["toolkitVersion"] = "8.1.3"
help_manifest["runtimeGuidePatch"] = (
    "Toolkit v8.1.3 renders the Alliance Member Manager from the real live Tools card, "
    "keeps it beside Alliance Map Blocker under Alliance Operations and restores it after "
    "normal panel re-renders."
)
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")
HELP_INDEX.write_text(
    HELP_INDEX.read_text(encoding="utf-8").replace("v8.1.2", "v8.1.3"),
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
            "Issue #553 native Alliance Member Manager Tools card cloning, class-independent "
            "lookup and panel-scoped re-render recovery"
        ),
    }
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT)], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME_TEST)], cwd=ROOT, check=True)

print("Toolkit v8.1.3 native Alliance Member Manager render correction applied and validated.")
