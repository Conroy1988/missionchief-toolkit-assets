#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

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
    if (char === "'" || char === '"' || char === "`") {
      quote = char;
      continue;
    }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const constantsStart = source.indexOf("    const COMMAND_SECTION_ORDER");
const constantsEnd = source.indexOf("\n    state = loadState();", constantsStart);
assert.notEqual(constantsStart, -1);
assert.notEqual(constantsEnd, -1);
const commandConstants = source.slice(constantsStart, constantsEnd);
const commandFunctions = [
  "commandSectionSlug",
  "commandSectionNavigationMarkup",
  "wrapCommandSectionCards",
  "upgradeCommandInterface",
  "commandInterfaceApplySearch",
].map(extractFunction).join("\n");

const legacySections = [
  ["skins", "Interface themes", "theme-control"],
  ["tools", "Map visibility", "map-control"],
  ["resources", "Resource planning", "resource-control"],
  ["ops", "Vehicle operations", "vehicle-control"],
  ["alliance", "Alliance Courses", "alliance-control"],
  ["dispatch", "Dispatch Recruitment", "dispatch-control"],
  ["payouts", "Payout flash", "payout-control"],
  ["discord", "Discord reporting", "discord-control"],
  ["places", "Bookmarks", "location-control"],
  ["settings", "Device layout", "settings-control"],
].map(([panel, label, control]) => `
  <section class="mcms-tab-panel" data-panel="${panel}">
    <div class="mcms-section-label">${label}</div>
    <button id="${control}">${label}</button>
  </section>
`).join("");

const dom = new JSDOM(`<!doctype html><html><body>
  <div id="panel">
    <div class="mcms-panel-sticky-stack"><div class="mcms-tabs"></div></div>
    ${legacySections}
    <div class="mcms-footer">Footer</div>
  </div>
</body></html>`, { url: "https://www.missionchief.co.uk/", pretendToBeVisual: true });

const sandbox = {
  document: dom.window.document,
  window: dom.window,
  console,
  state: { activeTab: "incidents" },
  escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  },
  updateUiToggleClass(element, className, enabled) {
    if (!element) return false;
    element.classList.toggle(className, Boolean(enabled));
    return true;
  },
  updateUiSetProperty(element, property, value) {
    if (!element) return false;
    element[property] = value;
    return true;
  },
  createStatusCentreSection() {
    const section = dom.window.document.createElement("section");
    section.className = "mcms-tab-panel";
    section.dataset.panel = "status";
    section.innerHTML = '<div class="mcms-section-label">Operations Status Centre</div><div data-operations-status-centre></div>';
    return section;
  },
  enhanceAdministrationWorkflow() {},
  enhanceProgressiveGuidance() {},
};
vm.createContext(sandbox);
vm.runInContext(`${commandConstants}
${commandFunctions}
this.__probe = {
  upgrade: upgradeCommandInterface,
  search: commandInterfaceApplySearch,
  setQuery(value) { commandSearchQuery = String(value || ""); },
  order: COMMAND_SECTION_ORDER,
};`, sandbox, { filename: "issue597-command-interface-runtime.js" });

const panel = dom.window.document.querySelector("#panel");
sandbox.__probe.upgrade(panel);

const expectedSections = ["map", "incidents", "fleet", "administration", "finance", "status", "settings"];
assert.deepEqual(Array.from(sandbox.__probe.order), expectedSections);
assert.deepEqual(
  Array.from(panel.querySelectorAll(".mcms-tabs > .mcms-tab-btn"), button => button.dataset.tab),
  expectedSections,
  "seven-section navigation order drifted",
);
assert.deepEqual(
  Array.from(panel.querySelectorAll(".mcms-command-content > .mcms-tab-panel"), section => section.dataset.panel),
  expectedSections,
  "runtime panel order drifted",
);
assert.equal(panel.querySelectorAll(".mcms-tab-btn").length, 7, "navigation did not consolidate to seven task sections");
assert.equal(panel.querySelectorAll(".mcms-tab-panel").length, 7, "content did not consolidate to seven task sections");
assert.equal(panel.dataset.mcmsCommandInterface, "v10");

const incidents = panel.querySelector('[data-panel="incidents"]');
const fleet = panel.querySelector('[data-panel="fleet"]');
const administration = panel.querySelector('[data-panel="administration"]');
const map = panel.querySelector('[data-panel="map"]');
const settings = panel.querySelector('[data-panel="settings"]');
assert.ok(incidents.querySelector("#vehicle-control"), "Ops were not routed into Incidents");
assert.ok(fleet.querySelector("#resource-control"), "Resources were not routed into Fleet");
assert.ok(administration.querySelector("#alliance-control") && administration.querySelector("#dispatch-control"), "Administration sources were not merged");
assert.ok(map.querySelector("#map-control") && map.querySelector("#location-control"), "Map and saved locations were not merged");
assert.ok(settings.querySelector("#settings-control") && settings.querySelector("#theme-control"), "Appearance was not merged into Settings");
const finance = panel.querySelector('[data-panel="finance"]');
assert.ok(finance.querySelector("#discord-control"), "Discord reporting was not routed into Finance");
assert.ok(finance.querySelector("#payout-control"), "Payouts were not routed into Finance");
for (const id of [
  "theme-control",
  "map-control",
  "resource-control",
  "vehicle-control",
  "alliance-control",
  "dispatch-control",
  "payout-control",
  "discord-control",
  "location-control",
  "settings-control",
]) {
  assert.equal(panel.querySelectorAll(`#${id}`).length, 1, `${id} was duplicated or lost`);
}

sandbox.__probe.setQuery("vehicle");
assert.equal(sandbox.__probe.search(panel), 1, "current-section search returned the wrong match count");
assert.equal(
  incidents.querySelector("#vehicle-control").closest(".mcms-command-card").classList.contains("mcms-search-hidden"),
  false,
);
assert.equal(
  incidents.querySelector("#vehicle-control").closest(".mcms-command-card").classList.contains("mcms-search-hidden"),
  false,
);
assert.equal(panel.querySelector(".mcms-command-search-empty").hidden, true);

sandbox.__probe.setQuery("no such command");
assert.equal(sandbox.__probe.search(panel), 0);
assert.equal(panel.querySelector(".mcms-command-search-empty").hidden, false, "empty search state was not shown");

sandbox.__probe.setQuery("");
assert.equal(sandbox.__probe.search(panel), 1);
assert.equal(incidents.querySelectorAll(".mcms-search-hidden").length, 0, "clearing search did not restore cards");

sandbox.__probe.upgrade(panel);
assert.equal(panel.querySelectorAll(".mcms-tab-btn").length, 7, "upgrade was not idempotent");
assert.equal(panel.querySelectorAll(".mcms-tab-panel").length, 7, "idempotent upgrade changed panel count");

dom.window.close();
console.log("Issue #597 command-interface runtime passed: seven task sections, deterministic migration, card grouping and idempotence.");
