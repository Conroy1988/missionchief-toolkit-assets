#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const marker = "    function " + name + "(";
  const start = source.indexOf(marker);
  assert.ok(start >= 0, name + " is missing");
  const parameters = source.indexOf("(", start);
  let parameterDepth = 0;
  let brace = -1;
  for (let index = parameters; index < source.length; index += 1) {
    if (source[index] === "(") parameterDepth += 1;
    if (source[index] === ")" && --parameterDepth === 0) {
      brace = source.indexOf("{", index);
      break;
    }
  }
  assert.notEqual(brace, -1, name + " body is missing");
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
    if (char === "'" || char === '"' || char === String.fromCharCode(96)) {
      quote = char;
      continue;
    }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error("Unable to extract " + name);
}

const dom = new JSDOM(`<!doctype html><html><body>
  <div id="palette"><input data-command-palette-input><button id="result-0" data-command-palette-result="0"></button><button id="result-1" data-command-palette-result="1"></button><button id="close"></button></div>
  <div id="panel"><section class="mcms-tab-panel" data-panel="settings"><article class="mcms-command-card" data-command-card="input"><h3>Input</h3></article></section></div>
</body></html>`, { url: "https://www.missionchief.co.uk/", pretendToBeVisual: true });

for (const element of dom.window.document.querySelectorAll("*")) element.scrollIntoView = () => { element.dataset.scrolled = "true"; };

const sandbox = {
  console,
  document: dom.window.document,
  SCRIPT: { panelId: "panel", commandPaletteId: "palette" },
  COMMAND_SECTION_ORDER: ["map", "incidents", "fleet", "administration", "finance", "status", "settings"],
  COMMAND_PALETTE_SCOPES: [
    { key: "all", label: "All", kind: "" },
    { key: "commands", label: "Commands", kind: "action" },
    { key: "missions", label: "Missions", kind: "mission" },
  ],
  COMMAND_PALETTE_KIND_META: {
    action: { label: "Action", icon: "A", priority: 60 },
    mission: { label: "Mission", icon: "M", priority: 50 },
    vehicle: { label: "Vehicle", icon: "V", priority: 40 },
    building: { label: "Building", icon: "B", priority: 30 },
    location: { label: "Location", icon: "L", priority: 20 },
    setting: { label: "Setting", icon: "S", priority: 10 },
  },
  COMMAND_PALETTE_RESULT_LIMIT: 30,
  isVisible: () => true,
  commandExperienceElement(id) { return dom.window.document.getElementById(id); },
  openPanel() { sandbox.panelOpened = true; },
  setActiveTab(tab) { sandbox.activeTab = tab; },
};
vm.createContext(sandbox);
vm.runInContext(
  "let commandPaletteEntries=[]; let commandPaletteResults=[]; let commandPaletteSelectedIndex=0; let commandPaletteScope='all'; let commandPaletteRecentIds=[];\n" +
  [
    "commandPaletteNormalise",
    "commandPaletteAddEntry",
    "commandPaletteEntryScore",
    "commandPaletteSearch",
    "commandPaletteUpdateSelection",
    "commandPaletteTrapFocus",
    "commandPaletteOpenSetting",
  ].map(extractFunction).join("\n") +
  "\nthis.__probe={" +
  "add:commandPaletteAddEntry,search:commandPaletteSearch,select:commandPaletteUpdateSelection,trap:commandPaletteTrapFocus,setting:commandPaletteOpenSetting," +
  "setEntries(value){commandPaletteEntries=value},setResults(value){commandPaletteResults=value},setScope(value){commandPaletteScope=value},setRecent(value){commandPaletteRecentIds=value},selected(){return commandPaletteSelectedIndex}" +
  "};",
  sandbox,
  { filename: "issue618-command-palette-runtime.js" },
);

const entries = [];
const seen = new Set();
const add = entry => sandbox.__probe.add(entries, seen, { ...entry, execute() {} });
add({ id: "action:fullscreen", kind: "action", title: "Enter Full-Screen Map", detail: "Map full-screen mode", terms: "full screen fullscreen maximise restore", featured: true });
add({ id: "action:stuck", kind: "action", title: "Enable Stuck Mission Detection", detail: "Currently off", terms: "stuck vehicles stalled incidents" });
add({ id: "location:wakefield", kind: "location", title: "Wakefield", detail: "Quick Place", terms: "WKFD map jump" });
add({ id: "building:wakefield-fire", kind: "building", title: "Wakefield Central Fire Station", detail: "Personal building", terms: "station" });
add({ id: "mission:77", kind: "mission", title: "Public Order Incident", detail: "Alliance mission", terms: "police Newcastle" });
add({ id: "vehicle:12", kind: "vehicle", title: "ARV 12", detail: "FMS 2 · armed response", terms: "vehicle available" });
add({ id: "setting:input", kind: "setting", title: "Input", detail: "Settings · open exact control group", terms: "keyboard shortcuts" });
add({ id: "location:wakefield", kind: "location", title: "Duplicate", detail: "Must not be added", terms: "duplicate" });

assert.equal(entries.length, 7, "duplicate entry IDs must be rejected");
sandbox.__probe.setEntries(entries);
assert.equal(sandbox.__probe.search("Wakefield")[0].id, "location:wakefield", "an exact location must outrank a building containing the same place name");
assert.equal(sandbox.__probe.search("stuck vehicles")[0].id, "action:stuck");
assert.equal(sandbox.__probe.search("full screen")[0].id, "action:fullscreen");
assert.equal(sandbox.__probe.search("public Newcastle")[0].id, "mission:77");
assert.equal(sandbox.__probe.search("armed response")[0].id, "vehicle:12");
assert.equal(sandbox.__probe.search("keyboard shortcuts")[0].id, "setting:input");
assert.equal(sandbox.__probe.search("missing result").length, 0);
assert.ok(sandbox.__probe.search("").every(entry => entry.featured), "empty search must show featured quick access only");
sandbox.__probe.setScope("missions");
assert.deepEqual(sandbox.__probe.search("").map(entry => entry.id), [], "mission scope must not leak featured commands");
sandbox.__probe.setRecent(["mission:77"]);
assert.deepEqual(sandbox.__probe.search("").map(entry => entry.id), ["mission:77"], "empty scoped search must surface matching session recents");
sandbox.__probe.setScope("all");
sandbox.__probe.setRecent([]);

const overlay = dom.window.document.getElementById("palette");
sandbox.__probe.setResults(entries.slice(0, 2));
assert.equal(sandbox.__probe.select(overlay, -1), true);
assert.equal(sandbox.__probe.selected(), 1, "ArrowUp-style selection must wrap to the final result");
assert.equal(overlay.querySelector("[data-command-palette-input]").getAttribute("aria-activedescendant"), "result-1");
assert.equal(overlay.querySelector("#result-1").getAttribute("aria-selected"), "true");
sandbox.__probe.select(overlay, 2);
assert.equal(sandbox.__probe.selected(), 0, "ArrowDown-style selection must wrap to the first result");

const input = overlay.querySelector("input");
const close = overlay.querySelector("#close");
close.focus();
let prevented = false;
assert.equal(sandbox.__probe.trap({ key: "Tab", shiftKey: false, preventDefault() { prevented = true; } }, overlay), true);
assert.equal(prevented, true);
assert.equal(dom.window.document.activeElement, input, "forward Tab must wrap inside the dialog");

const card = dom.window.document.querySelector('[data-command-card="input"]');
assert.equal(sandbox.__probe.setting("settings", "input"), true);
assert.equal(sandbox.panelOpened, true);
assert.equal(sandbox.activeTab, "settings");
assert.equal(card.classList.contains("mcms-command-palette-target"), true);
assert.equal(card.dataset.scrolled, "true");

dom.window.close();
console.log("Issue #618 Command Palette runtime passed: ranked local search, deduplication, keyboard wrapping, focus containment and exact Settings targeting.");
