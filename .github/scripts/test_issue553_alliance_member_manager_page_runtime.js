#!/usr/bin/env node
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
const externalTable = { parentElement: enhancedRoot };
assert.equal(mountSandbox.mountTarget(externalTable), componentRoot);
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

console.log("Issue #553 live external redesigned member-page runtime passed: delayed mount, activity, page count, stable mount and duplicate suppression.");
