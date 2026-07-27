#!/usr/bin/env python3
"""Apply Toolkit v8.1.5 UI mount hardening and Alliance Member Manager correction."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
WORKFLOW = ROOT / ".github/workflows/validate-userscript.yml"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
PERFORMANCE = ROOT / ".github/performance-budget.json"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_MANIFEST = ROOT / "help/manifest.json"
HELP_INDEX = ROOT / "help/index.html"
DOC = ROOT / "docs/issue-553-alliance-member-manager-restoration.md"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)} expected one target, found {count}: {old[:120]!r}")
    write(path, text.replace(old, new, 1))


def function_span(text: str, name: str) -> tuple[int, int]:
    marker = f"    function {name}("
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Missing function {name}")
    brace = text.find("{", start)
    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    index = brace
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char == "/" and nxt == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and nxt == "*":
            block_comment = True
            index += 2
            continue
        if char in "'\"`":
            quote = char
            index += 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
        index += 1
    raise RuntimeError(f"Unterminated function {name}")


def replace_function(text: str, name: str, replacement: str) -> str:
    start, end = function_span(text, name)
    return text[:start] + replacement.rstrip() + text[end:]


source = SOURCE.read_text(encoding="utf-8")
source = source.replace("// @version      8.1.4", "// @version      8.1.5", 1)
source = source.replace("version: '8.1.4'", "version: '8.1.5'", 1)

state_pattern = re.compile(
    r"    let allianceMemberManagerPage = null;\n"
    r"    let allianceMemberManagerInstallTimer = 0;\n"
    r"    let allianceMemberManagerInstallAttempt = 0;\n"
    r"    const ALLIANCE_MEMBER_MANAGER_INSTALL_DELAYS = Object\.freeze\(\[\n"
    r".*?\n    \]\);",
    re.DOTALL,
)
state_replacement = """    let allianceMemberManagerPage = null;
    let allianceMemberManagerMountObserver = null;
    let allianceMemberManagerMountRoot = null;
    let allianceMemberManagerReconcileQueued = false;
    let allianceMemberManagerLastMountState = 'idle';"""
source, count = state_pattern.subn(state_replacement, source, count=1)
if count != 1:
    raise RuntimeError("Unable to replace Alliance Member Manager mount state")

source = replace_function(source, "allianceMemberManagerEnabled", r'''    function allianceMemberManagerEnabled() {
        try {
            if (typeof GM_getValue === 'function') {
                const value = GM_getValue(ALLIANCE_MEMBER_MANAGER.storageKey, null);
                if (typeof value === 'boolean') return value;
            }
        } catch (error) {}
        try {
            return localStorage.getItem(ALLIANCE_MEMBER_MANAGER.storageKey) === 'true';
        } catch (error) {
            return false;
        }
    }''')

source = replace_function(source, "setAllianceMemberManagerEnabled", r'''    function setAllianceMemberManagerEnabled(enabled) {
        const next = Boolean(enabled);
        try {
            if (typeof GM_setValue === 'function') GM_setValue(ALLIANCE_MEMBER_MANAGER.storageKey, next);
        } catch (error) {}
        try {
            localStorage.setItem(ALLIANCE_MEMBER_MANAGER.storageKey, next ? 'true' : 'false');
        } catch (error) {}
        updateAllianceMemberManagerMenuControl();
        reconcileAllianceMemberManager('setting-change');
    }''')

cancel_start, _ = function_span(source, "allianceMemberManagerCancelInstallRetry")
relocate_start, _ = function_span(source, "allianceMemberManagerRelocatePanel")
mount_helpers = r'''    function allianceMemberManagerMountReceipt() {
        const registry = pageWindow.__MCMS_UI_MOUNTS__ ||= {};
        return registry.allianceMemberManager || null;
    }

    function allianceMemberManagerRecordMountState(state, detail = '') {
        const nextState = String(state || 'unknown');
        const registry = pageWindow.__MCMS_UI_MOUNTS__ ||= {};
        const previous = registry.allianceMemberManager;
        if (!previous || previous.state !== nextState || previous.detail !== detail) {
            registry.allianceMemberManager = Object.freeze({
                state: nextState,
                detail: String(detail || ''),
                path: String(location.pathname || ''),
                version: SCRIPT.version,
                updatedAt: Date.now(),
            });
        }
        allianceMemberManagerLastMountState = nextState;
        document.documentElement?.setAttribute('data-mcms-alliance-member-manager-mount', nextState);
        updateAllianceMemberManagerMenuControl();
    }

    function allianceMemberManagerMutationRelevant(records) {
        const ownedSelector = '[data-mcms-ui-owned="alliance-member-manager"]';
        return records.some(record => Array.from(record.addedNodes || [])
            .concat(Array.from(record.removedNodes || []))
            .some(node => {
                if (!node || ![1, 11].includes(node.nodeType)) return false;
                if (node.nodeType === 1 && (node.matches?.(ownedSelector) || node.closest?.(ownedSelector))) return false;
                if (node.nodeType === 1 && node.matches?.('table, h1, h2, [data-member-page-summary], #mcms-alliance-member-manager')) return true;
                return Boolean(node.querySelector?.(
                    'table, h1, h2, a[href^="/profile/"], a[href*="/profile/"], #mcms-alliance-member-manager'
                ));
            }));
    }

    function allianceMemberManagerQueueReconcile(reason = 'dom-change') {
        if (allianceMemberManagerReconcileQueued) return;
        allianceMemberManagerReconcileQueued = true;
        queueMicrotask(() => {
            allianceMemberManagerReconcileQueued = false;
            reconcileAllianceMemberManager(reason);
        });
    }

    function allianceMemberManagerDisconnectMountObserver() {
        allianceMemberManagerMountObserver?.disconnect();
        allianceMemberManagerMountObserver = null;
        allianceMemberManagerMountRoot = null;
        allianceMemberManagerReconcileQueued = false;
    }

    function allianceMemberManagerEnsureMountObserver() {
        const root = document.body || document.documentElement;
        if (!root) return false;
        if (allianceMemberManagerMountObserver && allianceMemberManagerMountRoot === root) return true;
        allianceMemberManagerDisconnectMountObserver();
        const Observer = pageWindow.MutationObserver
            || (typeof MutationObserver === 'function' ? MutationObserver : null);
        if (typeof Observer !== 'function') return false;
        allianceMemberManagerMountRoot = root;
        allianceMemberManagerMountObserver = new Observer(records => {
            if (allianceMemberManagerMutationRelevant(records)) {
                allianceMemberManagerQueueReconcile('member-dom-mutation');
            }
        });
        allianceMemberManagerMountObserver.observe(root, { childList: true, subtree: true });
        return true;
    }

    function allianceMemberManagerClearMountNotice() {
        document.querySelector('[data-mcms-ui-owned="alliance-member-manager"]')?.remove();
    }

    function allianceMemberManagerShowMountNotice(error) {
        const table = allianceMemberManagerTable();
        const target = allianceMemberManagerMountTarget(table);
        if (!target?.parentElement) return;
        let notice = document.querySelector('[data-mcms-ui-owned="alliance-member-manager"]');
        if (!notice) {
            notice = document.createElement('div');
            notice.setAttribute('data-mcms-ui-owned', 'alliance-member-manager');
            notice.className = 'alert alert-danger';
            target.before(notice);
        }
        notice.textContent = 'Alliance Member Manager could not attach. The Toolkit retained a diagnostic mount receipt and will retry when the member view changes.';
        notice.title = String(error?.message || error || 'Unknown mount error');
    }

'''
source = source[:cancel_start] + mount_helpers + source[relocate_start:]

source = replace_function(source, "updateAllianceMemberManagerMenuControl", r'''    function updateAllianceMemberManagerMenuControl() {
        const panel = document.querySelector(`#${SCRIPT.panelId}`);
        const button = panel?.querySelector(`[${ALLIANCE_MEMBER_MANAGER.menuAttribute}]`);
        if (!button) return;
        const enabled = allianceMemberManagerEnabled();
        const mountState = allianceMemberManagerMountReceipt()?.state || allianceMemberManagerLastMountState;
        const mounted = mountState === 'mounted';
        const failed = mountState === 'error';
        button.classList.toggle('mcms-on', enabled);
        button.setAttribute('aria-pressed', String(enabled));
        button.setAttribute('data-mcms-mount-state', mountState || 'idle');
        const pill = button.querySelector('.mcms-pill');
        if (pill) pill.textContent = !enabled ? 'OFF' : failed ? 'ERR' : mounted ? 'ON' : 'WAIT';
        const stateText = !enabled
            ? 'disabled'
            : failed
                ? 'enabled, page controls failed to mount'
                : mounted
                    ? 'enabled and mounted'
                    : 'enabled, waiting for a compatible member view';
        button.title = `Alliance Member Manager: ${stateText}`;
        button.setAttribute('aria-label', `Alliance Member Manager ${stateText}`);
    }''')

source = replace_function(source, "reconcileAllianceMemberManager", r'''    function reconcileAllianceMemberManager(reason = 'reconcile') {
        const enabled = allianceMemberManagerEnabled();
        if (!enabled) {
            allianceMemberManagerDisconnectMountObserver();
            allianceMemberManagerClearMountNotice();
            disposeAllianceMemberManager();
            allianceMemberManagerRecordMountState('disabled', reason);
            return;
        }

        const observing = allianceMemberManagerEnsureMountObserver();
        const routeMatch = isAllianceMemberManagerRoute();
        const domMatch = allianceMemberManagerHasDomContext();
        if (!routeMatch && !domMatch) {
            allianceMemberManagerClearMountNotice();
            disposeAllianceMemberManager();
            allianceMemberManagerRecordMountState(
                observing ? 'watching' : 'waiting',
                'Enabled; waiting for an alliance member view'
            );
            return;
        }
        if (allianceMemberManagerOtherOwnerPresent()) {
            allianceMemberManagerClearMountNotice();
            disposeAllianceMemberManager();
            allianceMemberManagerRecordMountState('suppressed', 'Equivalent manager already owns this view');
            return;
        }

        const table = allianceMemberManagerTable();
        const panel = document.querySelector(`#${ALLIANCE_MEMBER_MANAGER.panelId}`);
        const panelConnected = Boolean(panel && panel.isConnected !== false);
        if (
            allianceMemberManagerPage
            && (!panelConnected || (table && allianceMemberManagerPage.table && allianceMemberManagerPage.table !== table))
        ) {
            disposeAllianceMemberManager();
        }
        if (!table) {
            allianceMemberManagerRecordMountState('waiting', 'Member view found; waiting for its table');
            return;
        }

        try {
            installAllianceMemberManager();
            if (!allianceMemberManagerPage) {
                allianceMemberManagerRecordMountState('waiting', 'Member table found; installer has not claimed it yet');
                return;
            }
            allianceMemberManagerRelocatePanel();
            allianceMemberManagerClearMountNotice();
            allianceMemberManagerRecordMountState('mounted', `Connected to ${allianceMemberManagerPage.members?.size || 0} members`);
        } catch (error) {
            try { disposeAllianceMemberManager(); } catch (disposeError) {}
            allianceMemberManagerRecordMountState('error', String(error?.message || error || 'Unknown mount error'));
            allianceMemberManagerShowMountNotice(error);
            console.error('[Toolkit] Alliance Member Manager mount failed', error);
        }
    }''')

if "teardownAllianceMemberManager" in source:
    raise RuntimeError("Undefined teardown lifecycle name remains in source")
write(SOURCE, source)

fixture_html = '''<!doctype html>
<html><head></head><body>
<main id="external-member-root">
  <h1>Members<br><small>Show 20 players of 1 (11,012,323,195) to 1 (1,267,484,428) of 568 pages</small></h1>
  <button>load previous page</button><button>load next page</button>
  <a href="/verband/mitglieder/123?online=true">Show only online players</a>
  <section id="external-member-component">
    <div class="head"><span>20 filtered players</span><label><input class="search_input_field" placeholder="Search in loaded players"></label></div>
    <table class="table table-striped">
      <thead><tr><th>player</th><th>Role(s)</th><th>total credits earned</th></tr></thead>
      <tbody>
        <tr><td><img src="/images/user_green.png"><a href="/profile/10">Evilian</a></td><td><span class="badge">Senior Admin</span><br><small>Alliance Admin</small></td><td>11,012,323,195 Credits</td></tr>
        <tr><td><img src="/images/user_gray.png"><a href="/profile/11">iCarnage</a></td><td></td><td>4,845,062,084 Credits</td></tr>
      </tbody>
    </table>
  </section>
</main>
</body></html>
'''
write(ROOT / ".github/fixtures/issue553-alliance-member-manager-rendered.html", fixture_html)

integration_test = r'''#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { parseHTML } from "linkedom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const rendered = fs.readFileSync(".github/fixtures/issue553-alliance-member-manager-rendered.html", "utf8");
const bodyMatch = rendered.match(/<body>([\s\S]*)<\/body>/iu);
assert.ok(bodyMatch, "rendered member fixture body missing");
const memberBody = bodyMatch[1];

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
  const brace = source.indexOf("{", start);
  let depth = 0, quote = "", escaped = false;
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

const blockStart = source.indexOf("    // <mcms-alliance-member-manager>");
const blockEnd = source.indexOf("    // </mcms-alliance-member-manager>", blockStart);
assert.notEqual(blockStart, -1);
assert.notEqual(blockEnd, -1);
const managerBlock = source.slice(blockStart, blockEnd + "    // </mcms-alliance-member-manager>".length);

function polyfillTables(document) {
  for (const table of document.querySelectorAll("table")) {
    if (!table.tBodies) Object.defineProperty(table, "tBodies", { configurable: true, value: Array.from(table.querySelectorAll("tbody")) });
    for (const body of table.tBodies) {
      if (!body.rows) Object.defineProperty(body, "rows", { configurable: true, value: Array.from(body.querySelectorAll(":scope > tr")) });
      for (const row of body.rows) {
        if (row.cells) continue;
        const cells = Array.from(row.querySelectorAll(":scope > th, :scope > td"));
        cells.item = index => cells[index] || null;
        Object.defineProperty(row, "cells", { configurable: true, value: cells });
      }
    }
  }
}

function createScenario({ pathname, initialMemberDom, gmEnabled, localEnabled }) {
  const html = `<!doctype html><html><head></head><body>${initialMemberDom ? memberBody : '<main id="map-root"></main>'}</body></html>`;
  const { window } = parseHTML(html);
  polyfillTables(window.document);
  const storage = new Map();
  if (localEnabled !== null) storage.set("mcms_alliance_member_manager_enabled_v1", String(localEnabled));
  const gm = { value: gmEnabled };
  const localStorage = {
    getItem(key) { return storage.has(key) ? storage.get(key) : null; },
    setItem(key, value) { storage.set(key, String(value)); },
    removeItem(key) { storage.delete(key); },
  };
  const sandbox = {
    console,
    window,
    document: window.document,
    Element: window.Element,
    Event: window.Event,
    MutationObserver: window.MutationObserver,
    DOMParser: window.DOMParser,
    URL,
    AbortController,
    queueMicrotask,
    pageWindow: window,
    localStorage,
    location: { pathname, href: `https://www.missionchief.co.uk${pathname}`, origin: "https://www.missionchief.co.uk" },
    SCRIPT: { panelId: "mc-map-command-toolkit-panel", version: "8.1.5" },
    GM_getValue: (_key, fallback) => typeof gm.value === "boolean" ? gm.value : fallback,
    GM_setValue: (_key, value) => { gm.value = Boolean(value); },
    fetch: async () => { throw new Error("fetch must not run during mount integration"); },
    showToast: () => undefined,
  };
  vm.createContext(sandbox);
  vm.runInContext(`${extractFunction("decodedPathname")}\n${managerBlock}\nthis.__probe = {
    enabled: allianceMemberManagerEnabled,
    setEnabled: setAllianceMemberManagerEnabled,
    table: allianceMemberManagerTable,
    page: () => allianceMemberManagerPage,
    observer: () => allianceMemberManagerMountObserver,
    receipt: () => pageWindow.__MCMS_UI_MOUNTS__?.allianceMemberManager || null,
  };`, sandbox, { filename: "alliance-member-manager-v8.1.5.js" });
  window.document.dispatchEvent(new window.Event("DOMContentLoaded"));
  return { window, sandbox, gm };
}

async function flush(rounds = 80) {
  for (let index = 0; index < rounds; index += 1) await Promise.resolve();
}

function assertMounted(label, scenario) {
  const panel = scenario.window.document.querySelector("#mcms-alliance-member-manager");
  assert.ok(scenario.sandbox.__probe.table(scenario.window.document), `${label}: table missing`);
  assert.ok(panel, `${label}: panel missing`);
  assert.ok(panel.querySelectorAll("select").length >= 3, `${label}: Role, Activity and Sort controls missing`);
  assert.match(panel.textContent, /Load All Member Pages/u, `${label}: load-all control missing`);
  assert.equal(scenario.sandbox.__probe.receipt()?.state, "mounted", `${label}: mount receipt not mounted`);
}

const direct = createScenario({ pathname: "/verband/mitglieder/123", initialMemberDom: true, gmEnabled: null, localEnabled: true });
await flush();
assertMounted("direct-route-static-dom", direct);

const delayed = createScenario({ pathname: "/", initialMemberDom: false, gmEnabled: true, localEnabled: null });
await flush();
assert.ok(delayed.sandbox.__probe.observer(), "enabled neutral route did not install mount observer");
delayed.window.document.body.insertAdjacentHTML("beforeend", memberBody);
polyfillTables(delayed.window.document);
await flush(160);
assertMounted("neutral-route-delayed-dom", delayed);

const oldPanel = delayed.window.document.querySelector("#mcms-alliance-member-manager");
delayed.window.document.querySelector("#external-member-root")?.remove();
oldPanel?.remove();
delayed.window.document.body.insertAdjacentHTML("beforeend", memberBody.replaceAll("/profile/10", "/profile/20").replaceAll("/profile/11", "/profile/21"));
polyfillTables(delayed.window.document);
await flush(160);
assertMounted("framework-rerender", delayed);
assert.notEqual(delayed.window.document.querySelector("#mcms-alliance-member-manager"), oldPanel, "rerender reused detached panel");

delayed.sandbox.__probe.setEnabled(false);
await flush();
assert.equal(delayed.gm.value, false, "userscript storage was not updated");
assert.equal(delayed.window.document.querySelector("#mcms-alliance-member-manager"), null, "disable did not remove panel");
assert.equal(delayed.sandbox.__probe.observer(), null, "disable did not disconnect mount observer");
assert.equal(delayed.sandbox.__probe.receipt()?.state, "disabled", "disable receipt missing");

console.log("Full UI mount integration passed: direct mount, neutral-route delayed mount, framework rerender, cross-origin setting persistence and deterministic disable teardown.");
'''
write(ROOT / ".github/scripts/test_ui_mount_integration.mjs", integration_test)

page_runtime = r'''#!/usr/bin/env node
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const start = source.indexOf("    // <mcms-alliance-member-manager>");
const end = source.indexOf("    // </mcms-alliance-member-manager>", start);
const block = source.slice(start, end);
assert.ok(start >= 0 && end > start);
assert.ok(block.includes("disposeAllianceMemberManager();"));
assert.ok(!block.includes("teardownAllianceMemberManager"));
assert.ok(block.includes("allianceMemberManagerEnsureMountObserver"));
assert.ok(block.includes("pageWindow.__MCMS_UI_MOUNTS__"));
assert.ok(block.includes("GM_getValue"));
assert.ok(block.includes("GM_setValue"));
assert.ok(!block.includes("installAllianceMemberManager() {"), "runtime contract must not mock the installer");
assert.ok(!block.includes("teardownAllianceMemberManager() {}"), "runtime contract must not fake lifecycle symbols");
console.log("Alliance Member Manager lifecycle symbols passed: real dispose path, enabled-only observer, userscript storage and mount receipts.");
'''
write(ROOT / ".github/scripts/test_issue553_alliance_member_manager_page_runtime.js", page_runtime)

ui_policy = {
    "schemaVersion": 1,
    "description": "Blocking policy for page-level Toolkit UI integration.",
    "requirements": [
        "Execute the real installer against a rendered DOM fixture.",
        "Cover delayed DOM insertion on a neutral top-level route.",
        "Cover host-framework rerender and deterministic disable teardown.",
        "Publish a structured mount receipt and a visible non-success control state.",
        "Do not substitute mocked installer or lifecycle functions.",
    ],
    "surfaces": {
        "allianceMemberManager": {
            "sourceMarker": "<mcms-alliance-member-manager>",
            "fixture": ".github/fixtures/issue553-alliance-member-manager-rendered.html",
            "integrationTest": ".github/scripts/test_ui_mount_integration.mjs",
            "mountReceipt": "window.__MCMS_UI_MOUNTS__.allianceMemberManager",
            "requiredScenarios": [
                "direct-route-static-dom",
                "neutral-route-delayed-dom",
                "framework-rerender",
            ],
        }
    },
}
write(ROOT / ".github/ui-mount-policy.json", json.dumps(ui_policy, indent=2) + "\n")

policy_test = r'''#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
policy = json.loads((ROOT / ".github/ui-mount-policy.json").read_text(encoding="utf-8"))
assert policy["schemaVersion"] == 1
source = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/validate-userscript.yml").read_text(encoding="utf-8")
legacy = (ROOT / ".github/scripts/test_issue553_alliance_member_manager_page_runtime.js").read_text(encoding="utf-8")
for name, surface in policy["surfaces"].items():
    fixture = ROOT / surface["fixture"]
    integration = ROOT / surface["integrationTest"]
    assert fixture.is_file(), fixture
    assert integration.is_file(), integration
    test = integration.read_text(encoding="utf-8")
    assert surface["sourceMarker"] in source
    assert "managerBlock" in test and "vm.runInContext" in test
    for scenario in surface["requiredScenarios"]:
        assert scenario in test, scenario
    assert "installAllianceMemberManager() {" not in test
    assert "teardownAllianceMemberManager() {}" not in test
assert "linkedom@0.18.12" in workflow
assert "node .github/scripts/test_ui_mount_integration.mjs" in workflow
assert "installAllianceMemberManager() {" not in legacy
assert "teardownAllianceMemberManager() {}" not in legacy
assert "window.__MCMS_UI_MOUNTS__" in source
assert "data-mcms-alliance-member-manager-mount" in source
print("UI mount policy passed: real installer execution, rendered fixture, delayed neutral-route mount, rerender recovery, mount receipt and no mocked lifecycle substitutions.")
'''
write(ROOT / ".github/scripts/test_ui_mount_policy.py", policy_test)

contract = r'''#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
start = source.index("    // <mcms-alliance-member-manager>")
end = source.index("    // </mcms-alliance-member-manager>", start)
block = source[start:end]
assert re.search(r"^// @version\s+8\.1\.5$", source, re.MULTILINE)
assert "version: '8.1.5'" in source
for marker in [
    "disposeAllianceMemberManager();",
    "allianceMemberManagerEnsureMountObserver",
    "allianceMemberManagerDisconnectMountObserver",
    "allianceMemberManagerMutationRelevant",
    "pageWindow.__MCMS_UI_MOUNTS__",
    "data-mcms-alliance-member-manager-mount",
    "GM_getValue",
    "GM_setValue",
    "'watching'",
    "'waiting'",
    "'mounted'",
    "'error'",
    "pill.textContent = !enabled ? 'OFF' : failed ? 'ERR' : mounted ? 'ON' : 'WAIT'",
    "Alliance Member Manager could not attach",
]: assert marker in block, marker
assert "teardownAllianceMemberManager" not in source
assert block.count("new Observer(") == 1
assert block.count("setInterval(") == 0
assert block.count("setTimeout(") == 0
assert "installAllianceMemberManager() {" not in (ROOT / ".github/scripts/test_ui_mount_integration.mjs").read_text(encoding="utf-8")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
assert "## [8.1.5] - 2026-07-27" in changelog
assert "### Hardened UI mounting and live member-page recovery" in changelog
performance = json.loads((ROOT / ".github/performance-budget.json").read_text(encoding="utf-8"))
assert performance["revision"] == "2026-07-27-issue-553-ui-mount-hardening"
assert performance["transitionApproval"]["version"] == "8.1.5"
assert performance["transitionApproval"]["approvedMutationObserverDelta"] == 1
preflight = (ROOT / ".github/scripts/run_userscript_preflight.sh").read_text(encoding="utf-8")
assert "test_ui_mount_policy.py" in preflight
workflow = (ROOT / ".github/workflows/validate-userscript.yml").read_text(encoding="utf-8")
assert "test_ui_mount_integration.mjs" in workflow
print("Alliance Member Manager contract passed: corrected lifecycle symbol, DOM-authoritative observation, cross-origin persistence, visible mount states, exception recovery and full rendered integration gate.")
'''
write(ROOT / ".github/scripts/test_alliance_member_manager_contract.py", contract)

policy_doc = '''# Toolkit UI Mount Policy

Page-level Toolkit UI is not considered implemented merely because selectors, labels or helper functions exist.

Every new or materially changed external-page UI surface must:

1. execute its real production installer against a rendered DOM fixture;
2. cover content present at startup and content inserted later without relying on the top-level route;
3. cover host-framework rerender or replacement;
4. prove deterministic teardown when disabled;
5. publish a structured mount receipt and expose a visible waiting or error state instead of failing silently;
6. avoid mocked installer and lifecycle substitutes in the blocking integration test.

The required Runtime lane installs a pinned, script-disabled DOM runtime and runs `.github/scripts/test_ui_mount_integration.mjs`. The aggregate Toolkit Hotfix Gate cannot pass if the production installer fails any registered scenario.
'''
write(ROOT / "docs/UI_MOUNT_POLICY.md", policy_doc)

workflow_text = WORKFLOW.read_text(encoding="utf-8")
marker = "      - name: Run deterministic runtime contracts\n"
insert = '''      - name: Install isolated UI integration runtime
        shell: bash
        run: |
          set -euo pipefail
          npm install --no-save --package-lock=false --ignore-scripts linkedom@0.18.12

      - name: Run full rendered UI mount integration
        shell: bash
        run: |
          set -euo pipefail
          node .github/scripts/test_ui_mount_integration.mjs 2>&1 | tee ui-mount-integration.log

'''
if workflow_text.count(marker) != 1:
    raise RuntimeError("Unable to insert UI integration workflow steps")
workflow_text = workflow_text.replace(marker, insert + marker, 1)
workflow_text = workflow_text.replace("            2>&1 | tee runtime-lane.log", "            2>&1 | tee runtime-contracts.log\n          cat ui-mount-integration.log runtime-contracts.log > runtime-lane.log", 1)
write(WORKFLOW, workflow_text)

preflight_text = PREFLIGHT.read_text(encoding="utf-8")
preflight_text = preflight_text.replace(
    ".github/scripts/test_alliance_member_manager_contract.py; do",
    ".github/scripts/test_alliance_member_manager_contract.py .github/scripts/test_ui_mount_policy.py; do",
    1,
)
write(PREFLIGHT, preflight_text)

performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
performance["revision"] = "2026-07-27-issue-553-ui-mount-hardening"
performance["rationale"] = "Issue #553 corrects a concealed lifecycle symbol failure and adds one enabled-only, child-list-only, coalesced observer so externally rendered member views mount without depending on the top-level route."
transition = performance.setdefault("transitionApproval", {})
transition.update({
    "issue": 553,
    "version": "8.1.5",
    "approvedMutationObserverDelta": 1,
    "scope": "Hardened Alliance Member Manager UI mount observation, structured receipts, visible mount states and full rendered integration gate.",
})
for key, delta in {
    "mutation_observers": 1,
    "mutation_observer_constructions": 1,
    "broad_subtree_observers": 1,
    "document_wide_subtree_observers": 1,
}.items():
    performance["absoluteLimits"][key] = int(performance["absoluteLimits"][key]) + delta
    performance["relativeLimits"][key]["warnDelta"] = 1
    performance["relativeLimits"][key]["failDelta"] = 1
write(PERFORMANCE, json.dumps(performance, indent=2) + "\n")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''# Changelog

## [8.1.5] - 2026-07-27

### Hardened UI mounting and live member-page recovery

- Corrected the undefined Alliance Member Manager teardown lifecycle call that stopped redesigned member views before installation.
- Replaced route-only retries with one enabled-only, child-list-only, coalesced mount observer that recognises delayed external page content.
- Mirrored the opt-in setting through userscript and local storage for supported-origin continuity.
- Added structured mount receipts plus `WAIT` and `ERR` control states so page UI can no longer fail silently while the menu claims success.
- Added exception recovery, framework-rerender rebinding and deterministic observer teardown.
- Added a permanent rendered-DOM integration gate that executes the real installer for direct, delayed neutral-route and rerender scenarios; mocked installer or lifecycle substitutes are prohibited.

'''
if not changelog.startswith("# Changelog\n"):
    raise RuntimeError("Unexpected changelog header")
write(CHANGELOG, entry + changelog[len("# Changelog\n\n"):])

for relative in [
    ".github/scripts/test_issue530_transport_sweep_discharge_confirmation.py",
    ".github/scripts/test_issue536_alliance_building_visibility.py",
    ".github/scripts/test_issue537_godfather_css_activation.py",
    ".github/scripts/test_issue539_godfather_layout_audio.py",
    ".github/scripts/test_issue541_godfather_duration_position.py",
    ".github/scripts/test_v8_godfather_contract.py",
]:
    path = ROOT / relative
    if path.exists():
        text = path.read_text(encoding="utf-8")
        text = text.replace("8.1.4", "8.1.5")
        write(path, text)

DOC.write_text(
    "# Issue #553 — hardened Alliance Member Manager UI mounting\n\n"
    "Toolkit v8.1.5 repairs the undefined lifecycle call proven by the full rendered-page diagnostic and replaces route-only retries with one enabled-only coalesced mount observer. The setting is mirrored through userscript storage, mount states are published under `window.__MCMS_UI_MOUNTS__`, the Toolkit control displays WAIT or ERR when appropriate, and the required Runtime lane executes the real installer against direct, delayed and rerendered member views.\n",
    encoding="utf-8",
)

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "8.1.5"
help_manifest["toolkitVersion"] = "8.1.5"
help_manifest["runtimeGuidePatch"] = "Toolkit v8.1.5 hardens page-level UI mounting with real rendered-DOM integration tests, enabled-only observation, mount receipts and visible waiting/error states."
write(HELP_MANIFEST, json.dumps(help_manifest, indent=2) + "\n")

help_index = HELP_INDEX.read_text(encoding="utf-8")
for old, new in [
    ("Toolkit v8.1.4", "Toolkit v8.1.5"),
    ("toolkitVersion: '8.1.4'", "toolkitVersion: '8.1.5'"),
    ('data-toolkit-version="8.1.4"', 'data-toolkit-version="8.1.5"'),
]:
    help_index = help_index.replace(old, new)
write(HELP_INDEX, help_index)

source_bytes = SOURCE.read_bytes()
sha = hashlib.sha256(source_bytes).hexdigest()
source_text = source_bytes.decode("utf-8")
lines = len(source_text.splitlines())
for relative in [
    "dist/MissionChief_Map_Command_Toolkit.user.js",
    "dist/MissionChief_Map_Command_Toolkit.txt",
]:
    (ROOT / relative).write_bytes(source_bytes)
write(
    ROOT / "dist/SHA256SUMS.txt",
    f"{sha}  MissionChief_Map_Command_Toolkit.user.js\n{sha}  MissionChief_Map_Command_Toolkit.txt\n",
)
manifest = json.loads((ROOT / "dist/release-manifest.json").read_text(encoding="utf-8"))
manifest.update({"version": "8.1.5", "sha256": sha, "bytes": len(source_bytes), "lines": lines})
manifest["metadata"]["runtimeVersion"] = "8.1.5"
write(ROOT / "dist/release-manifest.json", json.dumps(manifest, indent=2) + "\n")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
previous = headroom.get("v8Candidate", {})
previous_bytes = int(previous.get("sourceBytes", len(source_bytes)))
previous_lines = int(previous.get("sourceLines", lines))
headroom["v8Candidate"] = {
    **previous,
    "issue": 553,
    "version": "8.1.5",
    "sourceBytes": len(source_bytes),
    "sourceLines": lines,
    "sourceSha256": sha,
    "maxSourceBytes": max(int(previous.get("maxSourceBytes", 0)), len(source_bytes) + 20000),
    "maxSourceLines": max(int(previous.get("maxSourceLines", 0)), lines + 250),
    "baseline": "8.1.4",
    "approvedGrowth": {
        "sourceBytes": len(source_bytes) - previous_bytes,
        "sourceLines": lines - previous_lines,
        "templateBytes": 0,
        "templateLines": 0,
    },
    "scope": "Issue #553 lifecycle correction, enabled-only UI mount observer, cross-origin setting continuity, mount receipts and full rendered integration gate",
}
write(HEADROOM, json.dumps(headroom, indent=2) + "\n")

print(f"Toolkit v8.1.5 UI mount hardening package applied: {sha}, {len(source_bytes)} bytes, {lines} lines")
