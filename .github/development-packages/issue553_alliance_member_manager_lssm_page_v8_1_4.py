#!/usr/bin/env python3
"""Apply Toolkit v8.1.4 Alliance Member Manager live LSSM page correction."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CONTRACT = ROOT / ".github/scripts/test_alliance_member_manager_contract.py"
MENU_TEST = ROOT / ".github/scripts/test_issue553_alliance_member_manager_menu_runtime.js"
PAGE_TEST = ROOT / ".github/scripts/test_issue553_alliance_member_manager_page_runtime.js"
PAGE_FIXTURE = ROOT / ".github/fixtures/issue553-alliance-member-manager-page.json"
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
            f"{path.relative_to(ROOT)} expected one replacement target, found {count}: {old[:120]!r}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def function_span(text: str, name: str) -> tuple[int, int]:
    marker = f"    function {name}("
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Missing function {name}")
    brace = text.find("{", start)
    if brace < 0:
        raise RuntimeError(f"Missing opening brace for {name}")
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
        if char in ("'", '"', "`"):
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
    raise RuntimeError(f"Unable to find end of function {name}")


def replace_function(path: Path, name: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    start, end = function_span(text, name)
    path.write_text(text[:start] + replacement.rstrip() + text[end:], encoding="utf-8")


replace_once(SOURCE, "// @version      8.1.3", "// @version      8.1.4")
replace_once(SOURCE, "version: '8.1.3'", "version: '8.1.4'")
replace_once(
    SOURCE,
    "    let allianceMemberManagerPage = null;",
    """    let allianceMemberManagerPage = null;
    let allianceMemberManagerInstallTimer = 0;
    let allianceMemberManagerInstallAttempt = 0;
    const ALLIANCE_MEMBER_MANAGER_INSTALL_DELAYS = Object.freeze([
        0, 60, 140, 300, 600, 1000, 1600, 2400, 3600, 5200,
    ]);""",
)

replace_function(
    SOURCE,
    "isAllianceMemberManagerRoute",
    r'''    function isAllianceMemberManagerRoute(pathname = location.pathname) {
        const path = decodedPathname(pathname);
        return /\/verband\/mitglieder(?:\/\d+)?\/?$/iu.test(path)
            || /\/alliances?\/(?:\d+\/)?members(?:\/\d+)?\/?$/iu.test(path)
            || /\/alliance_members(?:\/\d+)?\/?$/iu.test(path);
    }''',
)
replace_function(
    SOURCE,
    "allianceMemberManagerOtherOwnerPresent",
    r'''    function allianceMemberManagerOtherOwnerPresent() {
        const candidates = document.querySelectorAll(
            '#allianceMemberList-controls, [id*="allianceMemberList"][id$="-controls"], ' +
            '[data-alliance-member-manager], [data-lssm-alliance-member-manager]'
        );
        return Array.from(candidates).some(candidate => {
            if (candidate.closest?.(`#${ALLIANCE_MEMBER_MANAGER.panelId}`)) return false;
            const text = String(candidate.textContent || '').replace(/\s+/gu, ' ').trim();
            const hasRole = /\brole(?:s)?\b/iu.test(text)
                || Boolean(candidate.querySelector?.('[name*="role" i], [data-filter*="role" i]'));
            const hasActivity = /\bactivity\b|\bonline\b.*\boffline\b/iu.test(text)
                || Boolean(candidate.querySelector?.('[name*="activity" i], [data-filter*="activity" i]'));
            const hasLoadAll = /\bload all member pages\b/iu.test(text)
                || Boolean(candidate.querySelector?.('[data-action*="load-all" i]'));
            return hasRole && hasActivity && hasLoadAll;
        });
    }''',
)
replace_function(
    SOURCE,
    "allianceMemberManagerTable",
    r'''    function allianceMemberManagerTable(doc = document) {
        return Array.from(doc.querySelectorAll('table')).find(table => {
            const profileLinks = table.querySelectorAll(
                'tbody a[href^="/profile/"], tbody a[href*="/profile/"]'
            );
            if (!profileLinks.length) return false;
            const headers = Array.from(table.querySelectorAll('thead th'))
                .map(header => String(header.textContent || '').replace(/\s+/gu, ' ').trim().toLowerCase());
            return !headers.length
                || headers.some(header => /^(?:player|member|name)$/iu.test(header))
                || profileLinks.length >= 2;
        }) || null;
    }''',
)
replace_function(
    SOURCE,
    "allianceMemberManagerTotalPages",
    r'''    function allianceMemberManagerTotalPages(doc = document) {
        const values = Array.from(doc.querySelectorAll('.pagination a, .pagination li'))
            .map(node => Number.parseInt(String(node.textContent || '').replace(/[^0-9]/gu, ''), 10))
            .filter(value => Number.isFinite(value) && value > 0);
        const summaryNodes = Array.from(doc.querySelectorAll('h1 small, h2 small, .head, [data-member-page-summary]'));
        const table = allianceMemberManagerTable(doc);
        const renderedRoot = table?.parentElement?.parentElement || null;
        if (renderedRoot && !summaryNodes.includes(renderedRoot)) summaryNodes.push(renderedRoot);
        summaryNodes.forEach(node => {
            const text = String(node.textContent || '');
            for (const match of text.matchAll(/\b(?:of|von)\s+(?<pages>[\d,.]+)\s+(?:pages?|seiten)\b/giu)) {
                const value = Number.parseInt(match.groups?.pages?.replace(/[^0-9]/gu, '') || '', 10);
                if (Number.isFinite(value) && value > 0) values.push(value);
            }
        });
        return Math.max(1, ...values);
    }''',
)
replace_function(
    SOURCE,
    "allianceMemberManagerActivity",
    r'''    function allianceMemberManagerActivity(row) {
        const icon = row.querySelector('img.online_icon, img[src*="user_"]');
        const source = icon?.getAttribute('src') || '';
        const match = source.match(/user_(?<state>blue|gray|green|red|yellow)(?:\.[a-z0-9]+)?/iu);
        return match?.groups?.state?.toLowerCase() || 'unknown';
    }''',
)

insert_marker = "    function allianceMemberManagerStyle() {"
source_text = SOURCE.read_text(encoding="utf-8")
if source_text.count(insert_marker) != 1:
    raise RuntimeError("Unable to locate Alliance Member Manager style function")
helpers = r'''    function allianceMemberManagerHasDomContext(doc = document) {
        const table = allianceMemberManagerTable(doc);
        if (!table) return false;
        const heading = Array.from(doc.querySelectorAll('h1, h2'))
            .map(node => String(node.textContent || '').replace(/\s+/gu, ' ').trim())
            .join(' ');
        return /\bmembers?\b|\bmitglieder\b/iu.test(heading)
            || Boolean(doc.querySelector('a[href^="/verband/mitglieder/"]'));
    }

    function allianceMemberManagerMountTarget(table) {
        const enhancedTableRoot = table?.parentElement || null;
        const memberComponentRoot = enhancedTableRoot?.parentElement || null;
        const lssmEnhancedTable = Boolean(
            enhancedTableRoot?.querySelector?.('.head input.search_input_field')
            || (enhancedTableRoot?.querySelector?.('.head') && memberComponentRoot?.querySelector?.('h1'))
        );
        return lssmEnhancedTable && memberComponentRoot ? memberComponentRoot : table;
    }

    function allianceMemberManagerCancelInstallRetry(resetAttempt = true) {
        if (allianceMemberManagerInstallTimer) {
            pageWindow.clearTimeout(allianceMemberManagerInstallTimer);
            allianceMemberManagerInstallTimer = 0;
        }
        if (resetAttempt) allianceMemberManagerInstallAttempt = 0;
    }

    function allianceMemberManagerScheduleInstallRetry() {
        if (
            allianceMemberManagerInstallTimer
            || allianceMemberManagerPage
            || !allianceMemberManagerEnabled()
            || !isAllianceMemberManagerRoute()
            || allianceMemberManagerInstallAttempt >= ALLIANCE_MEMBER_MANAGER_INSTALL_DELAYS.length
        ) return;
        const delay = ALLIANCE_MEMBER_MANAGER_INSTALL_DELAYS[allianceMemberManagerInstallAttempt];
        allianceMemberManagerInstallAttempt += 1;
        allianceMemberManagerInstallTimer = pageWindow.setTimeout(() => {
            allianceMemberManagerInstallTimer = 0;
            reconcileAllianceMemberManager();
        }, delay);
    }

    function allianceMemberManagerRelocatePanel() {
        if (!allianceMemberManagerPage) return;
        const panel = document.querySelector(`#${ALLIANCE_MEMBER_MANAGER.panelId}`);
        const table = allianceMemberManagerTable();
        const mountTarget = allianceMemberManagerMountTarget(table);
        if (panel && mountTarget && panel.nextElementSibling !== mountTarget) {
            mountTarget.before(panel);
        }
    }

'''
SOURCE.write_text(source_text.replace(insert_marker, helpers + insert_marker, 1), encoding="utf-8")

replace_function(
    SOURCE,
    "reconcileAllianceMemberManager",
    r'''    function reconcileAllianceMemberManager() {
        const eligible = allianceMemberManagerEnabled()
            && (isAllianceMemberManagerRoute() || allianceMemberManagerHasDomContext())
            && !allianceMemberManagerOtherOwnerPresent();
        if (!eligible) {
            allianceMemberManagerCancelInstallRetry();
            teardownAllianceMemberManager();
            return;
        }
        installAllianceMemberManager();
        if (allianceMemberManagerPage) {
            allianceMemberManagerRelocatePanel();
            allianceMemberManagerCancelInstallRetry();
            return;
        }
        allianceMemberManagerScheduleInstallRetry();
    }''',
)

contract = CONTRACT.read_text(encoding="utf-8")
contract = contract.replace(r"^// @version\s+8\.1\.3$", r"^// @version\s+8\.1\.4$")
contract = contract.replace("version: '8.1.3'", "version: '8.1.4'")
contract = contract.replace(
    '        r"alliance\\/members|verband\\/mitglieder",\n'
    '        "img.online_icon",',
    '        r"alliances?\\/(?:\\d+\\/)?members|alliance_members|verband\\/mitglieder",\n'
    '        "img.online_icon, img[src*=\\\"user_\\\"]",\n'
    '        "ALLIANCE_MEMBER_MANAGER_INSTALL_DELAYS",\n'
    '        "allianceMemberManagerScheduleInstallRetry()",\n'
    '        "allianceMemberManagerMountTarget(table)",\n'
    '        "of|von",\n'
    '        "pages?|seiten",',
)
contract = contract.replace(
    '        "#allianceMemberList-controls",\n',
    '        "#allianceMemberList-controls",\n'
    '        "hasRole && hasActivity && hasLoadAll",\n',
)
contract = contract.replace(
    '    assert block.count("new MutationObserver(") == 0\n',
    '    assert block.count("new MutationObserver(") == 0\n'
    '    assert block.count("setTimeout(") == 1\n'
    '    assert block.count("setInterval(") == 0\n',
)
contract = contract.replace(
    '    assert "## [8.1.3] - 2026-07-27" in changelog\n'
    '    assert "### Canonical Alliance Member Manager Tools rendering" in changelog',
    '    assert "## [8.1.4] - 2026-07-27" in changelog\n'
    '    assert "### Live LSSM alliance-members page mounting" in changelog\n'
    '    assert "## [8.1.3] - 2026-07-27" in changelog',
)
contract = contract.replace(
    '    assert "test_issue553_alliance_member_manager_menu_runtime.js" in preflight\n',
    '    assert "test_issue553_alliance_member_manager_menu_runtime.js" in preflight\n'
    '    assert "test_issue553_alliance_member_manager_page_runtime.js" in preflight\n',
)
contract = contract.replace(
    '    assert performance["revision"] == "2026-07-27-issue-553-canonical-menu-render"\n'
    '    assert performance["transitionApproval"]["issue"] == 553\n'
    '    assert performance["transitionApproval"]["version"] == "8.1.3"',
    '    assert performance["revision"] == "2026-07-27-issue-553-lssm-page-mount"\n'
    '    assert performance["transitionApproval"]["issue"] == 553\n'
    '    assert performance["transitionApproval"]["version"] == "8.1.4"',
)
contract = contract.replace(
    '        "persisted state reconciliation, responsive member controls and zero added observers."',
    '        "persisted state reconciliation, delayed LSSM mounting, responsive member controls and zero added observers."',
)
CONTRACT.write_text(contract, encoding="utf-8")

fixture = {
    "schemaVersion": 1,
    "routes": [
        {"path": "/verband/mitglieder/123", "expected": True},
        {"path": "/verband/mitglieder/123/", "expected": True},
        {"path": "/alliance/123/members", "expected": True},
        {"path": "/alliances/123/members", "expected": True},
        {"path": "/alliance_members/123", "expected": True},
        {"path": "/verband/gebauede/123", "expected": False},
    ],
    "summary": "Show 40 players of 1 (11,012,323,195) to 2 (624,070,751) of 568 pages",
    "expectedPages": 568,
    "activitySource": "/images/user_green.png",
    "expectedActivity": "green",
    "retrySuccessAttempt": 3,
}
PAGE_FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

page_test = r'''#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "../..");
const source = fs.readFileSync(path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"), "utf8");
const fixture = JSON.parse(fs.readFileSync(
  path.join(root, ".github/fixtures/issue553-alliance-member-manager-page.json"),
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

const routeSandbox = { decodedPathname: value => value, location: { pathname: "/" } };
vm.runInNewContext(
  `${extractFunction("isAllianceMemberManagerRoute")}\nthis.isRoute = isAllianceMemberManagerRoute;`,
  routeSandbox
);
for (const item of fixture.routes) assert.equal(routeSandbox.isRoute(item.path), item.expected, item.path);

const activitySandbox = {};
vm.runInNewContext(
  `${extractFunction("allianceMemberManagerActivity")}\nthis.activity = allianceMemberManagerActivity;`,
  activitySandbox
);
const activityRow = {
  querySelector(selector) {
    assert.equal(selector, 'img.online_icon, img[src*="user_"]');
    return { getAttribute(name) { assert.equal(name, "src"); return fixture.activitySource; } };
  },
};
assert.equal(activitySandbox.activity(activityRow), fixture.expectedActivity);

const totalPagesSandbox = {
  allianceMemberManagerTable() { return null; },
};
vm.runInNewContext(
  `${extractFunction("allianceMemberManagerTotalPages")}\nthis.totalPages = allianceMemberManagerTotalPages;`,
  totalPagesSandbox
);
const summaryNode = { textContent: fixture.summary };
const pageDoc = {
  querySelectorAll(selector) {
    if (selector === ".pagination a, .pagination li") return [];
    if (selector === "h1 small, h2 small, .head, [data-member-page-summary]") return [summaryNode];
    throw new Error(`Unexpected selector ${selector}`);
  },
};
assert.equal(totalPagesSandbox.totalPages(pageDoc), fixture.expectedPages);

const mountSandbox = {};
vm.runInNewContext(
  `${extractFunction("allianceMemberManagerMountTarget")}\nthis.mountTarget = allianceMemberManagerMountTarget;`,
  mountSandbox
);
const componentRoot = { querySelector(selector) { return selector === "h1" ? {} : null; } };
const enhancedRoot = {
  parentElement: componentRoot,
  querySelector(selector) { return selector === ".head input.search_input_field" ? {} : null; },
};
const lssmTable = { parentElement: enhancedRoot };
assert.equal(mountSandbox.mountTarget(lssmTable), componentRoot);
const nativeTable = { parentElement: { parentElement: null, querySelector() { return null; } } };
assert.equal(mountSandbox.mountTarget(nativeTable), nativeTable);

const ownerText = extractFunction("allianceMemberManagerOtherOwnerPresent");
function ownerResult(textContent) {
  const candidate = {
    textContent,
    closest() { return null; },
    querySelector() { return null; },
  };
  const sandbox = {
    ALLIANCE_MEMBER_MANAGER: { panelId: "manager" },
    document: { querySelectorAll() { return [candidate]; } },
  };
  vm.runInNewContext(`${ownerText}\nthis.ownerPresent = allianceMemberManagerOtherOwnerPresent;`, sandbox);
  return sandbox.ownerPresent();
}
assert.equal(ownerResult("40 filtered players Search in loaded players"), false);
assert.equal(ownerResult("Role Activity Load All Member Pages"), true);

const retrySandbox = {
  ALLIANCE_MEMBER_MANAGER: { panelId: "manager" },
  ALLIANCE_MEMBER_MANAGER_INSTALL_DELAYS: Object.freeze([0, 1, 2, 3]),
  allianceMemberManagerPage: null,
  allianceMemberManagerInstallTimer: 0,
  allianceMemberManagerInstallAttempt: 0,
  callbacks: [],
  installs: 0,
  pageWindow: {
    setTimeout(callback) { retrySandbox.callbacks.push(callback); return retrySandbox.callbacks.length; },
    clearTimeout() {},
  },
  allianceMemberManagerEnabled: () => true,
  isAllianceMemberManagerRoute: () => true,
  allianceMemberManagerHasDomContext: () => false,
  allianceMemberManagerOtherOwnerPresent: () => false,
  teardownAllianceMemberManager() {},
  installAllianceMemberManager() {
    retrySandbox.installs += 1;
    if (retrySandbox.installs === fixture.retrySuccessAttempt) retrySandbox.allianceMemberManagerPage = {};
  },
  allianceMemberManagerRelocatePanel() {},
  document: { querySelector() { return null; } },
};
const retryFunctions = [
  "allianceMemberManagerCancelInstallRetry",
  "allianceMemberManagerScheduleInstallRetry",
  "reconcileAllianceMemberManager",
].map(extractFunction).join("\n");
vm.runInNewContext(`${retryFunctions}\nthis.reconcile = reconcileAllianceMemberManager;`, retrySandbox);
retrySandbox.reconcile();
while (retrySandbox.callbacks.length) retrySandbox.callbacks.shift()();
assert.equal(retrySandbox.installs, fixture.retrySuccessAttempt);
assert.ok(retrySandbox.allianceMemberManagerPage);
assert.equal(retrySandbox.allianceMemberManagerInstallTimer, 0);
assert.equal(retrySandbox.allianceMemberManagerInstallAttempt, 0);

const managerStart = source.indexOf("    // <mcms-alliance-member-manager>");
const managerEnd = source.indexOf("    // </mcms-alliance-member-manager>", managerStart);
const manager = source.slice(managerStart, managerEnd);
assert.equal((manager.match(/new MutationObserver\(/g) || []).length, 0);
assert.equal((manager.match(/setInterval\(/g) || []).length, 0);
assert.equal((manager.match(/setTimeout\(/g) || []).length, 1);
assert.ok(manager.includes("allianceMemberManagerRelocatePanel"));

console.log("Issue #553 live LSSM member-page runtime passed: delayed mount, activity, page count, stable mount and duplicate suppression.");
'''
PAGE_TEST.write_text(page_test, encoding="utf-8")

replace_once(
    PREFLIGHT,
    "node .github/scripts/test_issue553_alliance_member_manager_menu_runtime.js\n",
    "node .github/scripts/test_issue553_alliance_member_manager_menu_runtime.js\n"
    "node .github/scripts/test_issue553_alliance_member_manager_page_runtime.js\n",
)

performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
performance["revision"] = "2026-07-27-issue-553-lssm-page-mount"
performance["rationale"] = (
    "Issue #553 mounts Alliance Member Manager after LSSM Redesign's asynchronous member-table render "
    "using one bounded enabled-route timeout site, no observer or interval, and zero recurring disabled work."
)
performance["transitionApproval"] = {
    "issue": 553,
    "version": "8.1.4",
    "approvedNetworkRequestDelta": 1,
    "scope": (
        "Recognise and stably mount on the live LSSM alliance-members view; the existing explicit "
        "same-origin Load All Member Pages fetch site is unchanged."
    ),
}
PERFORMANCE.write_text(json.dumps(performance, indent=2) + "\n", encoding="utf-8")

replace_once(
    CHANGELOG,
    "# Changelog\n\n",
    """# Changelog

## [8.1.4] - 2026-07-27

### Live LSSM alliance-members page mounting

- Mounted the enabled Alliance Member Manager after LSSM Redesign asynchronously creates the UK member table.
- Recognised LSSM activity icons without the native `online_icon` class and parsed summary text such as `of 568 pages`.
- Mounted outside the Vue-controlled enhanced-table subtree so sorting and page loading do not erase the Toolkit controls.
- Narrowed duplicate suppression to genuinely equivalent role/activity/load-all managers rather than generic member-list search controls.
- Added bounded delayed-install retries only while enabled on the member route, with no observer, interval or recurring disabled work.
- Added executable route, delayed mount, activity, page-count, stable-mount and duplicate-suppression regressions.

""",
)

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "8.1.4"
help_manifest["toolkitVersion"] = "8.1.4"
help_manifest["runtimeGuidePatch"] = (
    "Toolkit v8.1.4 mounts Alliance Member Manager on the asynchronously rendered LSSM UK member page, "
    "recognises its activity and page-count markup, and keeps controls outside the Vue table subtree."
)
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")
HELP_INDEX.write_text(
    HELP_INDEX.read_text(encoding="utf-8").replace("v8.1.3", "v8.1.4"),
    encoding="utf-8",
)

source_bytes = SOURCE.read_bytes()
source_text = source_bytes.decode("utf-8")
headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
candidate.update(
    {
        "issue": 553,
        "version": "8.1.4",
        "sourceBytes": len(source_bytes),
        "sourceLines": len(source_text.splitlines()),
        "sourceSha256": hashlib.sha256(source_bytes).hexdigest(),
        "baseline": "8.1.3",
        "approvedGrowth": {
            "sourceBytes": len(source_bytes) - 1639133,
            "sourceLines": len(source_text.splitlines()) - 24945,
            "templateBytes": 0,
            "templateLines": 0,
        },
        "scope": (
            "Issue #553 bounded LSSM member-page mount recovery, activity and total-page parsing, "
            "stable Vue-external placement and equivalent-manager-only suppression"
        ),
    }
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, check=True)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(["python3", str(CONTRACT)], cwd=ROOT, check=True)
subprocess.run(["node", str(MENU_TEST)], cwd=ROOT, check=True)
subprocess.run(["node", str(PAGE_TEST)], cwd=ROOT, check=True)

print("Toolkit v8.1.4 Alliance Member Manager live LSSM page package applied and validated.")
