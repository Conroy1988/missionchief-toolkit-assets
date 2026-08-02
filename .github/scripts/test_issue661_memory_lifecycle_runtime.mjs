#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const pattern = new RegExp(`\\bfunction\\s+${name}\\s*\\(`, "u");
  const match = pattern.exec(source);
  assert.ok(match, `${name} is missing`);
  const start = match.index;
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
  assert.notEqual(brace, -1, `${name} body is missing`);
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
  throw new Error(`Unable to extract ${name}`);
}

for (const required of [
  "const missionValueDocumentObservers = new Map()",
  "const missionValueFrameListeners = new Map()",
  "const customVehicleBadgeDocumentObservers = new Map()",
  "const customVehicleBadgeFrameListeners = new Map()",
  "runtimeUnlistenTarget(overlay, true)",
  "runtimeUnlistenTarget(button, true)",
  "runtimeUntrackObserver(record?.resizeObserver)",
  "runtimeUntrackObserver(record?.mutationObserver)",
]) assert.ok(source.includes(required), `Missing lifecycle contract: ${required}`);

for (const retired of [
  "missionValueObservedDocuments",
  "missionValueObservedFrames",
  "customVehicleBadgeObservedDocuments",
  "customVehicleBadgeObservedFrames",
]) assert.equal(source.includes(retired), false, `${retired} must not return`);

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "https://www.missionchief.co.uk/",
  pretendToBeVisual: true,
});

const sandbox = {
  console,
  document: dom.window.document,
  pageWindow: dom.window,
  HTMLElement: dom.window.HTMLElement,
  SCRIPT: { commandPaletteId: "mcms-test-command-palette" },
  runtime: {
    destroyed: false,
    listeners: [],
    observers: new Set(),
  },
  commandPaletteEntries: [],
  commandPaletteResults: [],
  commandPaletteSelectedIndex: 0,
  commandPaletteReturnFocus: null,
  missionValueHostObservers: new Map(),
  missionValueDocumentObservers: new Map(),
  missionValueFrameListeners: new Map(),
  customVehicleBadgeDocumentObservers: new Map(),
  customVehicleBadgeFrameListeners: new Map(),
  commandExperienceElement(id) { return dom.window.document.getElementById(id); },
  setInnerHtmlIfChanged(element, html) { element.innerHTML = html; return true; },
  updateUI() {},
};

vm.createContext(sandbox);
vm.runInContext([
  "runtimeListen",
  "runtimeUnlisten",
  "runtimeUnlistenTarget",
  "runtimeDocumentConnected",
  "runtimePruneDisconnectedListeners",
  "runtimeTrackObserver",
  "runtimeUntrackObserver",
  "pruneMissionValueHostObservers",
  "pruneMissionValueTracking",
  "pruneCustomVehicleBadgeTracking",
  "createCommandPalette",
  "closeCommandPalette",
].map(extractFunction).join("\n\n") + `
this.__probe = {
  createCommandPalette,
  closeCommandPalette,
  pruneMissionValueHostObservers,
  pruneMissionValueTracking,
  pruneCustomVehicleBadgeTracking,
  runtimeListen,
  runtimeTrackObserver,
};`, sandbox, { filename: "issue661-memory-lifecycle.js" });

for (let cycle = 0; cycle < 250; cycle += 1) {
  const overlay = sandbox.__probe.createCommandPalette();
  assert.ok(overlay.isConnected, `palette ${cycle} did not open`);
  assert.equal(sandbox.runtime.listeners.length, 3, `palette ${cycle} did not own exactly three listeners`);
  assert.equal(sandbox.__probe.closeCommandPalette({ restoreFocus: false }), true);
  assert.equal(sandbox.runtime.listeners.length, 0, `palette ${cycle} retained listeners`);
  assert.equal(dom.window.document.getElementById(sandbox.SCRIPT.commandPaletteId), null, `palette ${cycle} retained its overlay`);
}

function observer() {
  return { disconnected: false, disconnect() { this.disconnected = true; } };
}

for (let cycle = 0; cycle < 250; cycle += 1) {
  const spacer = { isConnected: true };
  const toolbar = { isConnected: true };
  const resizeObserver = sandbox.__probe.runtimeTrackObserver(observer());
  const mutationObserver = sandbox.__probe.runtimeTrackObserver(observer());
  sandbox.missionValueHostObservers.set(spacer, { toolbar, resizeObserver, mutationObserver });
  spacer.isConnected = false;
  toolbar.isConnected = false;
  sandbox.__probe.pruneMissionValueHostObservers(new Set());
  assert.equal(sandbox.missionValueHostObservers.size, 0, `mission host ${cycle} remained tracked`);
  assert.equal(sandbox.runtime.observers.size, 0, `mission host ${cycle} retained observers`);
}

function trackedFrameContext(kind) {
  const listeners = new Map();
  const frame = {
    nodeType: 1,
    isConnected: true,
    contentDocument: null,
    addEventListener(type, listener) { listeners.set(type, listener); },
    removeEventListener(type, listener) { if (listeners.get(type) === listener) listeners.delete(type); },
  };
  const doc = { nodeType: 9, defaultView: { frameElement: frame } };
  frame.contentDocument = doc;
  const listener = () => {};
  const trackedObserver = sandbox.__probe.runtimeTrackObserver(observer());
  sandbox.__probe.runtimeListen(frame, "load", listener);
  sandbox[`${kind}DocumentObservers`].set(doc, trackedObserver);
  sandbox[`${kind}FrameListeners`].set(frame, listener);
  return { doc, frame };
}

for (let cycle = 0; cycle < 250; cycle += 1) {
  const mission = trackedFrameContext("missionValue");
  mission.frame.isConnected = false;
  sandbox.__probe.pruneMissionValueTracking(new Set(), new Set());
  assert.equal(sandbox.missionValueDocumentObservers.size, 0, `mission document ${cycle} remained tracked`);
  assert.equal(sandbox.missionValueFrameListeners.size, 0, `mission frame ${cycle} remained tracked`);
  assert.equal(sandbox.runtime.listeners.length, 0, `mission frame ${cycle} retained its load listener`);
  assert.equal(sandbox.runtime.observers.size, 0, `mission document ${cycle} retained its observer`);

  const badges = trackedFrameContext("customVehicleBadge");
  badges.frame.isConnected = false;
  sandbox.__probe.pruneCustomVehicleBadgeTracking(new Set(), new Set());
  assert.equal(sandbox.customVehicleBadgeDocumentObservers.size, 0, `badge document ${cycle} remained tracked`);
  assert.equal(sandbox.customVehicleBadgeFrameListeners.size, 0, `badge frame ${cycle} remained tracked`);
  assert.equal(sandbox.runtime.listeners.length, 0, `badge frame ${cycle} retained its load listener`);
  assert.equal(sandbox.runtime.observers.size, 0, `badge document ${cycle} retained its observer`);
}

dom.window.close();
console.log("Issue #661 memory lifecycle passed: 250 palette, mission-host, mission-frame and badge-frame churn cycles returned to a zero-retention baseline.");
