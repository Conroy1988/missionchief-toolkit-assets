#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { parseHTML } from "linkedom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

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

const start = source.indexOf("    // <mcms-alliance-member-manager>");
const end = source.indexOf("    // </mcms-alliance-member-manager>", start);
assert.notEqual(start, -1, "manager block start missing");
assert.notEqual(end, -1, "manager block end missing");
const managerBlock = source.slice(start, end + "    // </mcms-alliance-member-manager>".length);

const html = `<!doctype html><html><head></head><body>
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
</body></html>`;

const { window } = parseHTML(html);
const storage = new Map([["mcms_alliance_member_manager_enabled_v1", "true"]]);
const localStorage = {
  getItem(key) { return storage.has(key) ? storage.get(key) : null; },
  setItem(key, value) { storage.set(key, String(value)); },
  removeItem(key) { storage.delete(key); },
};

const timers = new Map();
let timerId = 0;
function schedule(callback) {
  const id = ++timerId;
  timers.set(id, callback);
  queueMicrotask(() => {
    const pending = timers.get(id);
    if (!pending) return;
    timers.delete(id);
    pending();
  });
  return id;
}
function clearScheduled(id) { timers.delete(id); }
window.setTimeout = schedule;
window.clearTimeout = clearScheduled;

const sandbox = {
  console,
  window,
  document: window.document,
  Element: window.Element,
  Event: window.Event,
  DOMParser: window.DOMParser,
  URL,
  AbortController,
  queueMicrotask,
  pageWindow: window,
  localStorage,
  location: {
    pathname: "/verband/mitglieder/123",
    href: "https://www.missionchief.co.uk/verband/mitglieder/123",
    origin: "https://www.missionchief.co.uk",
  },
  SCRIPT: { panelId: "mc-map-command-toolkit-panel", version: "8.1.4" },
  GM_getValue: (_key, fallback) => fallback,
  GM_setValue: () => undefined,
  fetch: async () => { throw new Error("fetch must not run during initial mount"); },
  showToast: () => undefined,
};
vm.createContext(sandbox);

const bootstrap = `${extractFunction("decodedPathname")}\n${managerBlock}\nthis.__managerProbe = {
  enabled: allianceMemberManagerEnabled,
  route: isAllianceMemberManagerRoute,
  table: allianceMemberManagerTable,
  reconcile: reconcileAllianceMemberManager,
  install: installAllianceMemberManager,
  page: () => allianceMemberManagerPage,
};`;

try {
  vm.runInContext(bootstrap, sandbox, { filename: "alliance-member-manager-v8.1.4.js" });
  window.document.dispatchEvent(new window.Event("DOMContentLoaded"));
  for (let i = 0; i < 20; i += 1) await Promise.resolve();

  const probe = sandbox.__managerProbe;
  const table = probe.table(window.document);
  const panel = window.document.querySelector("#mcms-alliance-member-manager");
  const report = {
    enabled: probe.enabled(),
    route: probe.route(),
    tableFound: Boolean(table),
    panelFound: Boolean(panel),
    pageContext: Boolean(probe.page()),
    bodyHtml: window.document.body.innerHTML.slice(0, 2000),
  };
  console.log(JSON.stringify(report, null, 2));
  assert.ok(table, "released installer did not discover the realistic member table");
  assert.ok(panel, "released installer did not render the Alliance Member Manager panel");
  assert.ok(panel.querySelector("select"), "manager panel rendered without filter controls");
  assert.match(panel.textContent, /Load All Member Pages/u);
} catch (error) {
  console.error("FULL_MOUNT_DIAGNOSTIC_FAILURE");
  console.error(error?.stack || error);
  console.error(window.document.body.innerHTML.slice(0, 4000));
  process.exitCode = 1;
}
