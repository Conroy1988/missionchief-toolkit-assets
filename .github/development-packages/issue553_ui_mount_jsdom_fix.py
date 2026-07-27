#!/usr/bin/env python3
"""Use a browser-faithful jsdom runtime for the generated full UI mount integration gate."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEST = ROOT / ".github/scripts/test_ui_mount_integration.mjs"
WORKFLOW = ROOT / ".github/workflows/validate-userscript.yml"
POLICY_TEST = ROOT / ".github/scripts/test_ui_mount_policy.py"

integration = r'''#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

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

function createScenario({ pathname, initialMemberDom, gmEnabled, localEnabled }) {
  const url = `https://www.missionchief.co.uk${pathname}`;
  const dom = new JSDOM(
    `<!doctype html><html><head></head><body>${initialMemberDom ? memberBody : '<main id="map-root"></main>'}</body></html>`,
    { url, pretendToBeVisual: true }
  );
  const { window } = dom;
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
    URL: window.URL,
    AbortController: window.AbortController,
    queueMicrotask,
    pageWindow: window,
    localStorage,
    location: window.location,
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
  window.document.dispatchEvent(new window.Event("DOMContentLoaded", { bubbles: true }));
  return { window, sandbox, gm, dom };
}

async function flush(rounds = 12) {
  for (let index = 0; index < rounds; index += 1) {
    await Promise.resolve();
    await new Promise(resolve => setTimeout(resolve, 0));
  }
}

function appendMemberBody(document, html) {
  const template = document.createElement("template");
  template.innerHTML = html;
  document.body.append(...Array.from(template.content.childNodes));
}

function assertMounted(label, scenario) {
  const panel = scenario.window.document.querySelector("#mcms-alliance-member-manager");
  assert.ok(scenario.sandbox.__probe.table(scenario.window.document), `${label}: table missing`);
  assert.ok(panel, `${label}: panel missing; receipt=${JSON.stringify(scenario.sandbox.__probe.receipt())}`);
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
assert.equal(delayed.sandbox.__probe.receipt()?.state, "watching", "neutral route did not publish watching receipt");
appendMemberBody(delayed.window.document, memberBody);
await flush(24);
assertMounted("neutral-route-delayed-dom", delayed);

const oldPanel = delayed.window.document.querySelector("#mcms-alliance-member-manager");
delayed.window.document.querySelector("#external-member-root")?.remove();
oldPanel?.remove();
appendMemberBody(
  delayed.window.document,
  memberBody.replaceAll("/profile/10", "/profile/20").replaceAll("/profile/11", "/profile/21")
);
await flush(24);
assertMounted("framework-rerender", delayed);
assert.notEqual(delayed.window.document.querySelector("#mcms-alliance-member-manager"), oldPanel, "rerender reused detached panel");

delayed.sandbox.__probe.setEnabled(false);
await flush();
assert.equal(delayed.gm.value, false, "userscript storage was not updated");
assert.equal(delayed.window.document.querySelector("#mcms-alliance-member-manager"), null, "disable did not remove panel");
assert.equal(delayed.sandbox.__probe.observer(), null, "disable did not disconnect mount observer");
assert.equal(delayed.sandbox.__probe.receipt()?.state, "disabled", "disable receipt missing");

direct.dom.window.close();
delayed.dom.window.close();
console.log("Full UI mount integration passed: direct mount, neutral-route delayed mount, framework rerender, cross-origin setting persistence and deterministic disable teardown.");
'''
TEST.write_text(integration, encoding="utf-8")

workflow = WORKFLOW.read_text(encoding="utf-8")
workflow = workflow.replace("linkedom@0.18.12", "jsdom@26.1.0")
WORKFLOW.write_text(workflow, encoding="utf-8")

policy = POLICY_TEST.read_text(encoding="utf-8")
policy = policy.replace('assert "linkedom@0.18.12" in workflow', 'assert "jsdom@26.1.0" in workflow')
POLICY_TEST.write_text(policy, encoding="utf-8")

print("Full UI mount integration now uses jsdom browser semantics.")
