#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const marker = "    function " + name + "(";
  const start = source.indexOf(marker);
  assert.ok(start >= 0, name + " is missing");
  const opening = source.indexOf("{", start);
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = opening; index < source.length; index += 1) {
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
  throw new Error("Unable to extract " + name);
}

const values = new Map();
const rect = { left: 100, top: 120, width: 800, height: 600 };
const style = {
  setProperty(name, value) {
    values.set(name, String(value));
    if (name === "width") rect.width = Number.parseFloat(value);
    if (name === "height") rect.height = Number.parseFloat(value);
    if (name === "left") rect.left = Number.parseFloat(value);
    if (name === "top") rect.top = Number.parseFloat(value);
  },
  removeProperty(name) { values.delete(name); },
  getPropertyValue(name) { return values.get(name) || ""; },
};

function makeClassList(initial = []) {
  const items = new Set(initial);
  return {
    add(...names) { names.forEach(name => items.add(name)); },
    remove(...names) { names.forEach(name => items.delete(name)); },
    contains(name) { return items.has(name); },
    toggle(name, force) {
      const enabled = force === undefined ? !items.has(name) : Boolean(force);
      if (enabled) items.add(name); else items.delete(name);
      return enabled;
    },
  };
}

function makeControl() {
  return {
    hidden: false,
    textContent: "",
    title: "",
    attributes: new Map(),
    setAttribute(name, value) { this.attributes.set(name, String(value)); },
  };
}

const maximizeButton = makeControl();
const resizeHandle = makeControl();
resizeHandle.setPointerCapture = id => { resizeHandle.captured = id; };
resizeHandle.releasePointerCapture = id => { resizeHandle.released = id; };
const dragHandle = makeControl();
const panel = {
  id: "panel",
  style,
  dataset: {},
  classList: makeClassList(["mcms-open"]),
  get offsetWidth() { return rect.width; },
  get offsetHeight() { return rect.height; },
  getBoundingClientRect() { return { ...rect, right: rect.left + rect.width, bottom: rect.top + rect.height }; },
  querySelector(selector) {
    if (selector === ".mcms-workspace-maximize") return maximizeButton;
    if (selector === ".mcms-workspace-resize-handle") return resizeHandle;
    if (selector === ".mcms-drag-handle") return dragHandle;
    return null;
  },
  getElementsByClassName(className) {
    if (className === "mcms-workspace-maximize") return [maximizeButton];
    if (className === "mcms-workspace-resize-handle") return [resizeHandle];
    if (className === "mcms-drag-handle") return [dragHandle];
    return [];
  },
};

const bounds = { left: 12, right: 1500, top: 80, bottom: 980, maxHeight: 900 };
const preferences = { panelWidth: 800, panelHeight: 82, panelHeightPx: 600, panelPosition: { left: 100, top: 120 } };
let saveCalls = 0;
let sizingCalls = 0;
let styleCalls = 0;
const toasts = [];

const sandbox = {
  console,
  Math,
  SCRIPT: { panelId: "panel" },
  DESKTOP_WORKSPACE_MIN_WIDTH: 560,
  DESKTOP_WORKSPACE_MAX_WIDTH: 1440,
  DESKTOP_WORKSPACE_MIN_HEIGHT: 420,
  document: {
    getElementById(id) { return id === "panel" ? panel : null; },
    documentElement: { style: { cursor: "" } },
    body: { style: { userSelect: "" } },
  },
  commandExperienceElement(id) { return id === "panel" ? panel : null; },
  clamp(value, minimum, maximum, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.min(maximum, Math.max(minimum, number)) : fallback;
  },
  currentDesktopWorkspaceBounds() { return { ...bounds }; },
  activeLayoutPreferences() { return preferences; },
  clampDesktopPanelPoint(left, top, width, height, area) {
    return {
      left: Math.round(Math.max(area.left, Math.min(left, area.right - width))),
      top: Math.round(Math.max(area.top, Math.min(top, area.bottom - height))),
    };
  },
  setPanelCssPosition(left, top) { rect.left = left; rect.top = top; },
  saveAndApplyPersonalisation() { saveCalls += 1; },
  applyDesktopPanelSizing() { sizingCalls += 1; },
  applyPersonalisationStyle() { styleCalls += 1; },
  getDefaultPanelPosition() { return { left: 200, top: 150 }; },
  clampPanelPosition(left, top) { return { left, top }; },
  showToast(message) { toasts.push(message); },
};
vm.createContext(sandbox);

const functions = [
  "desktopWorkspaceWindowActive",
  "updateDesktopWorkspaceChrome",
  "applyDesktopWorkspaceDimensions",
  "startPanelResize",
  "movePanelResize",
  "endPanelResize",
  "resizePanelFromKeyboard",
  "toggleDesktopWorkspaceMaximize",
].map(extractFunction).join("\n\n");

vm.runInContext(
  `let activeDeviceLayout='desktop';
   let tabletModeActive=false;
   let mobileModeActive=false;
   let dragState=null;
   let panelResizeState=null;
   let panelWorkspaceMaximized=false;
   let panelWorkspaceRestoreGeometry=null;
   let state={panelPosition:null};
   function isTouchLayoutActive(){return tabletModeActive||mobileModeActive;}
   ${functions}
   this.__probe={
     update:updateDesktopWorkspaceChrome,
     start:startPanelResize,
     move:movePanelResize,
     end:endPanelResize,
     keyboard:resizePanelFromKeyboard,
     maximize:toggleDesktopWorkspaceMaximize,
     resizeState(){return panelResizeState;},
     maximized(){return panelWorkspaceMaximized;},
     setLayout(layout){activeDeviceLayout=layout;tabletModeActive=layout==='tablet';mobileModeActive=layout==='mobile';}
   };`,
  sandbox,
  { filename: "desktop-toolkit-workspace-runtime.js" },
);

sandbox.__probe.update(panel);
assert.equal(panel.classList.contains("mcms-workspace-window"), true, "Desktop must opt into window geometry");
assert.equal(maximizeButton.hidden, false);
assert.equal(resizeHandle.hidden, false);

sandbox.__probe.setLayout("tablet");
sandbox.__probe.update(panel);
assert.equal(panel.classList.contains("mcms-workspace-window"), false, "Tablet must not inherit the Desktop window");
assert.equal(maximizeButton.hidden, true);
assert.equal(resizeHandle.hidden, true);
sandbox.__probe.setLayout("desktop");
sandbox.__probe.update(panel);

const pointer = (overrides = {}) => ({
  pointerId: 7,
  button: 0,
  isPrimary: true,
  clientX: 900,
  clientY: 720,
  currentTarget: resizeHandle,
  preventDefault() {},
  stopPropagation() {},
  ...overrides,
});
sandbox.__probe.start(pointer());
assert.ok(sandbox.__probe.resizeState(), "resize must start on a primary left pointer");
assert.equal(resizeHandle.captured, 7, "resize grip must capture its pointer");
sandbox.__probe.move(pointer({ clientX: 1300, clientY: 1000 }));
assert.equal(values.get("width"), "1200px");
assert.equal(values.get("height"), "860px", "resize must clamp to the visible workspace bottom");
assert.equal(saveCalls, 0, "pointer movement must not write settings");
sandbox.__probe.end(pointer({ clientX: 1300, clientY: 1000 }));
assert.equal(saveCalls, 1, "resize completion must persist exactly once");
assert.equal(preferences.panelWidth, 1200);
assert.equal(preferences.panelHeightPx, 860);
assert.deepEqual(JSON.parse(JSON.stringify(preferences.panelPosition)), { left: 100, top: 120 });
assert.equal(resizeHandle.released, 7);

sandbox.__probe.keyboard({ key: "ArrowLeft", shiftKey: false, preventDefault() {}, stopPropagation() {} });
assert.equal(preferences.panelWidth, 1176, "keyboard resizing must use a precise normal step");
sandbox.__probe.keyboard({ key: "ArrowUp", shiftKey: true, preventDefault() {}, stopPropagation() {} });
assert.equal(preferences.panelHeightPx, 780, "Shift plus an arrow must use the larger accessible step");
assert.equal(saveCalls, 3, "each completed keyboard resize must persist once");

sandbox.__probe.maximize();
assert.equal(sandbox.__probe.maximized(), true);
assert.equal(sizingCalls, 1);
sandbox.__probe.maximize();
assert.equal(sandbox.__probe.maximized(), false);
assert.equal(saveCalls, 3, "maximise and restore must not overwrite saved geometry");
assert.ok(styleCalls >= 1);
assert.deepEqual(toasts.slice(-2), ["Toolkit Workspace maximised", "Toolkit Workspace restored"]);

console.log("Desktop Toolkit Workspace runtime passed: touch isolation, pointer and keyboard resizing, viewport clamping, single-write persistence and temporary maximise/restore.");
