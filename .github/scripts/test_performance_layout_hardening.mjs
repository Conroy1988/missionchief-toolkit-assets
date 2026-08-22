#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const stressAudit = fs.readFileSync(".github/scripts/audit_runtime_stress.mjs", "utf8");

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
  const brace = source.indexOf("{", start);
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = brace; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
      else if (character === quote) quote = "";
      continue;
    }
    if (character === "'" || character === '"' || character === "`") { quote = character; continue; }
    if (character === "{") depth += 1;
    if (character === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const dom = new JSDOM("<!doctype html><html><body></body></html>");
const sandbox = { DIRECT_MISSION_ENTRY_MUTATION_SELECTOR: ".missionSideBarEntry, .mission-side-bar-entry" };
vm.createContext(sandbox);
vm.runInContext(`${extractFunction("mutationIsDirectMissionEntryBatch")}\nthis.audit = mutationIsDirectMissionEntryBatch;`, sandbox);

const missionEntries = Array.from({ length: 250 }, (_, index) => {
  const element = dom.window.document.createElement("div");
  element.className = index % 2 ? "missionSideBarEntry" : "mission-side-bar-entry";
  element.dataset.missionId = String(index + 1);
  return element;
});
assert.equal(sandbox.audit({ type: "childList", addedNodes: missionEntries, removedNodes: [] }), true);
assert.equal(sandbox.audit({ type: "childList", addedNodes: [], removedNodes: missionEntries }), true);
assert.equal(sandbox.audit({ type: "attributes", addedNodes: missionEntries, removedNodes: [] }), false);
const mixed = dom.window.document.createElement("div");
mixed.className = "modal";
assert.equal(sandbox.audit({ type: "childList", addedNodes: [missionEntries[0], mixed], removedNodes: [] }), false);
const nested = dom.window.document.createElement("div");
nested.appendChild(missionEntries[0].cloneNode());
assert.equal(sandbox.audit({ type: "childList", addedNodes: [nested], removedNodes: [] }), false);

const nativeVisibilityBody = extractFunction("mutationTouchesNativeVisibilityControls");
assert.ok(nativeVisibilityBody.indexOf("mutationIsDirectMissionEntryBatch(mutation)") < nativeVisibilityBody.indexOf("querySelector"), "mission fast path must precede generic descendant scans");
const customVehicleMutationBody = extractFunction("customVehicleBadgeMutationRelevant");
assert.ok(customVehicleMutationBody.indexOf("mutationIsDirectMissionEntryBatch(mutation)") < customVehicleMutationBody.indexOf("querySelector"), "vehicle badge observer must ignore direct mission-list batches before descendant scans");
assert.ok(source.includes("mutations.some(mutation => !mutationIsDirectMissionEntryBatch(mutation)"), "mission-value observer must ignore direct mission-list batches before descendant scans");
const observerStart = source.indexOf("const observer = runtimeTrackObserver(new MutationObserver(mutations =>", source.indexOf("function boot()"));
const observerEnd = source.indexOf("mainMutationObserver = observer;", observerStart);
assert.notEqual(observerStart, -1);
assert.notEqual(observerEnd, -1);
const observerBody = source.slice(observerStart, observerEnd);
assert.ok(observerBody.indexOf("mutationIsDirectMissionEntryBatch(mutation)") < observerBody.indexOf("mutationRemovesToolkitUi(mutation)"), "mission fast path must precede generic mutation classifiers");

for (const contract of [
  'grid-template-columns:180px minmax(0,1fr)',
  'grid-template-rows:repeat(8,minmax(58px,auto))',
  '.mcms-ui-theme-grid { grid-template-columns:1fr !important; }',
  '.mcms-bookmark-name{grid-column:1/-1!important',
  '.mcms-profile-main{grid-column:1/-1!important',
  '.mcms-tab-panel.mcms-active{grid-template-columns:1fr!important}',
  '.mcms-tabs{position:static!important;top:auto!important;grid-template-rows:repeat(3,44px)!important}',
  '.mcms-ui-theme-copy strong {\n            font-size:12.5px !important;',
  '.mcms-building-launcher > strong {\n            flex:1 1 100% !important;',
  'applyMobileDockLayout(mapEl);\n                applyTabletPanelPosition({ sizeOnly: true });',
  'applyTabletDockLayout(mapEl);\n                applyTabletPanelPosition({ sizeOnly: true });',
  'font-size:clamp(9px,2.35vw,10px)',
  'const panelSettings = new Map(',
  'const controlActionButtons = new Map(',
]) assert.ok(source.includes(contract), `performance/layout contract missing: ${contract}`);

assert.equal(stressAudit.includes('"/usr/bin/time"'), false, "runtime stress must not require a platform-specific GNU time path");
assert.ok(stressAudit.includes("process.resourceUsage"), "portable child RSS probe is missing");

dom.window.close();
console.log("Performance and layout hardening contract passed: bulk mission fast path, indexed UI reads, responsive text geometry and portable runtime stress metrics are retained.");
