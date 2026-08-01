#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import { TextDecoder, TextEncoder } from "node:util";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const plain = value => JSON.parse(JSON.stringify(value));

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

const store = new Map();
const notifications = [];
class BrowserNotification {
  static permission = "granted";
  static async requestPermission() { return "granted"; }
  constructor(title, options) { notifications.push({ title, options }); }
}

const sandbox = {
  console,
  TextEncoder,
  TextDecoder,
  Date,
  Math,
  pageWindow: {
    btoa(value) { return Buffer.from(value, "binary").toString("base64"); },
    atob(value) { return Buffer.from(value, "base64").toString("binary"); },
    Notification: BrowserNotification,
  },
  globalThis: {},
  SCRIPT: { version: "10.2.0", settingsSnapshotsState: "snapshots" },
  POSITIONS: { bl: { label: "Bottom left" }, tr: { label: "Top right" } },
  LAYOUT_DEVICE_KEYS: ["desktop", "tablet", "mobile"],
  DEFAULT_LAYOUT_GROUP_ORDER: ["visibility", "intelligence", "dashboard", "performance"],
  LAYOUT_CONTROL_GROUPS: {
    visibility: { controls: ["clean", "myMissions"] },
    intelligence: { controls: ["missionAge", "stuckDetector"] },
    dashboard: { controls: ["open-pressure-board"] },
    performance: { controls: ["toggle-economy"] },
  },
  QUICK_WHEEL_ACTIONS: { menu: { label: "Menu" }, commandPalette: { label: "Palette" }, personalisation: { label: "Studio" } },
  DEFAULT_QUICK_WHEEL_ACTIONS: ["menu", "commandPalette", "personalisation"],
  QUICK_PLACES: [{ id: "wakefield", name: "Wakefield", label: "WKFD", lat: 1, lng: 2, zoom: 12 }],
  NOTIFICATION_PRESETS: { radio: { label: "Radio", wave: "square" }, soft: { label: "Soft", wave: "sine" } },
  NOTIFICATION_EVENT_META: {
    newMission: { label: "New mission", title: "New incident" },
    completion: { label: "Completion", title: "Incident complete" },
    patient: { label: "Patient", title: "Patient waiting" },
    stuck: { label: "Stuck", title: "Mission stalled" },
    warning: { label: "Warning", title: "Toolkit warning" },
  },
  SETTINGS_SNAPSHOT_LIMIT: 5,
  SETTINGS_SNAPSHOT_INTERVAL_MS: 6 * 60 * 60 * 1000,
  THEME_STUDIO_FORMAT: "mcms-theme",
  THEME_STUDIO_SCHEMA: 1,
  clamp(value, minimum, maximum, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.min(maximum, Math.max(minimum, number)) : fallback;
  },
  gmGetValueSafe(key, fallback) { return store.has(key) ? store.get(key) : fallback; },
  gmSetValueSafe(key, value) { store.set(key, value); return true; },
  clonePlainData(value) { return JSON.parse(JSON.stringify(value)); },
  saveAndApplyPersonalisation() { sandbox.saved = true; },
  closeTabletQuickWheel() { sandbox.closed = true; },
  executeQuickWheelCommand(id) { sandbox.command = id; },
  setMapView(lat, lng, zoom) { sandbox.mapView = [lat, lng, zoom]; return true; },
  showToast(message) { sandbox.toast = message; },
  goBookmark(index) { sandbox.bookmark = index; },
  openCommandPalette(options) { sandbox.palette = options; },
  playToolkitNotificationCue(key) { sandbox.cue = key; return true; },
};
vm.createContext(sandbox);
vm.runInContext(
  [
    "defaultLayoutDeviceState",
    "defaultLayoutBuilderState",
    "normaliseUniqueList",
    "normaliseLayoutBuilderState",
    "defaultThemeStudioState",
    "normaliseThemeColour",
    "normaliseThemeStudioState",
    "defaultQuickWheelSlots",
    "normaliseQuickWheelSlot",
    "defaultNotificationState",
    "normaliseNotificationState",
    "loadSettingsSnapshots",
    "saveSettingsSnapshots",
    "captureSettingsSnapshot",
    "settingsTransferBytesToBase64",
    "settingsTransferBase64ToBytes",
    "encodeThemeStudioCode",
    "importThemeStudioCode",
    "movePersonalisationItem",
    "executeQuickWheelSlot",
    "emitToolkitNotification",
  ].map(extractFunction).join("\n") +
  "\nlet state={themeStudio:defaultThemeStudioState(),quickWheel:{slots:[]},bookmarks:[{name:'One'}],notifications:defaultNotificationState()};" +
  "const notificationEventSeen=new Map();" +
  "this.__probe={layout:normaliseLayoutBuilderState,theme:normaliseThemeStudioState,wheel:normaliseQuickWheelSlot,defaults:defaultQuickWheelSlots,move:movePersonalisationItem,capture:captureSettingsSnapshot,load:loadSettingsSnapshots,themeCode:encodeThemeStudioCode,importTheme:importThemeStudioCode,slot:executeQuickWheelSlot,notify:emitToolkitNotification,getState(){return state},setState(value){state=value}};",
  sandbox,
  { filename: "issue620-personalisation-runtime.js" },
);

const layout = sandbox.__probe.layout({ layouts: {
  desktop: { position: "tr", groupOrder: ["dashboard"], controlOrder: { dashboard: ["open-pressure-board"] }, hiddenControls: ["myMissions"], panelWidth: 2000, panelHeight: 20 },
  tablet: { position: "bl", groupOrder: ["visibility"], controlOrder: {}, panelWidth: 640, panelHeight: 90 },
  mobile: { position: "tr", groupOrder: [], controlOrder: {}, panelWidth: 800, panelHeight: 75 },
} }, "bl");
assert.equal(layout.layouts.desktop.position, "tr");
assert.equal(layout.layouts.desktop.panelWidth, 960, "desktop width must clamp");
assert.equal(layout.layouts.desktop.panelHeight, 60, "desktop height must clamp");
assert.equal(layout.layouts.tablet.panelWidth, 640);
assert.equal(layout.layouts.mobile.panelWidth, 100, "iOS width remains fixed");
assert.deepEqual(plain(layout.layouts.desktop.groupOrder), ["dashboard", "visibility", "intelligence", "performance"], "missing groups must be restored once");
assert.ok(layout.layouts.desktop.hiddenControls.includes("myMissions"));
layout.layouts.desktop.hiddenControls.push("clean");
assert.equal(layout.layouts.tablet.hiddenControls.includes("clean"), false, "device layouts must not share arrays");

const theme = sandbox.__probe.theme({ enabled: true, name: "x".repeat(100), accent: "red;display:none", surface: "#ABCDEF", text: "#123456", radius: 100, opacity: 1, blur: -8 });
assert.equal(theme.accent, "#68cfff", "invalid CSS input must be rejected");
assert.equal(theme.surface, "#abcdef");
assert.equal(theme.name.length, 40);
assert.equal(theme.radius, 28);
assert.equal(theme.opacity, 72);
assert.equal(theme.blur, 0);

assert.deepEqual(plain(sandbox.__probe.wheel("menu")), { kind: "action", id: "menu" });
assert.deepEqual(plain(sandbox.__probe.wheel("place:wakefield")), { kind: "place", id: "wakefield" });
assert.equal(sandbox.__probe.wheel("bookmark:8"), null);
assert.deepEqual([...sandbox.__probe.move(["a", "b", "c"], "b", 1)], ["a", "c", "b"]);

for (let index = 0; index < 7; index += 1) {
  sandbox.__probe.capture({ uiTheme: "mapCommand", revision: index }, { reason: "Snapshot " + index, force: true });
}
assert.equal(sandbox.__probe.load().length, 5, "snapshot history must remain bounded");
assert.equal(sandbox.__probe.load()[0].state.revision, 6);

sandbox.__probe.setState({
  themeStudio: { enabled: true, name: "Safe", accent: "#112233", surface: "#223344", text: "#ffffff", radius: 9, opacity: 91, blur: 7 },
  quickWheel: { slots: [] }, bookmarks: [], notifications: { enabled: false, browserEnabled: false, preset: "radio", volume: 0.3, events: {} },
});
const themeCode = sandbox.__probe.themeCode();
const decodedTheme = JSON.parse(Buffer.from(themeCode, "base64").toString("utf8"));
assert.deepEqual(Object.keys(decodedTheme).sort(), ["format", "schema", "theme", "version"]);
assert.equal(JSON.stringify(decodedTheme).includes("webhook"), false);
decodedTheme.theme.accent = "#fff};body{display:none";
sandbox.__probe.importTheme(Buffer.from(JSON.stringify(decodedTheme)).toString("base64"));
assert.equal(sandbox.__probe.getState().themeStudio.accent, "#68cfff", "imported theme input must be normalized");

const runtimeState = sandbox.__probe.getState();
runtimeState.quickWheel.slots = [
  { kind: "action", id: "personalisation" },
  { kind: "place", id: "wakefield" },
  { kind: "bookmark", id: "0" },
  { kind: "palette", id: "vehicle" },
];
sandbox.__probe.slot(0); assert.equal(sandbox.command, "personalisation");
sandbox.__probe.slot(1); assert.deepEqual(sandbox.mapView, [1, 2, 12]);
sandbox.__probe.slot(2); assert.equal(sandbox.bookmark, 0);
sandbox.__probe.slot(3); assert.equal(sandbox.palette.initialQuery, "vehicle");

runtimeState.notifications = { enabled: false, browserEnabled: true, preset: "radio", volume: 0.3, events: { warning: true } };
assert.equal(sandbox.__probe.notify("warning", "Hidden"), false, "master off must suppress alerts");
runtimeState.notifications.enabled = true;
assert.equal(sandbox.__probe.notify("warning", "Visible", { dedupeKey: "same" }), true);
assert.equal(sandbox.__probe.notify("warning", "Visible", { dedupeKey: "same" }), false, "duplicate event must be suppressed");
assert.equal(notifications.length, 1);
assert.equal(notifications[0].options.silent, true, "browser notification must not duplicate the local cue");

console.log("Issue #620 Personalisation Studio runtime passed: isolated layouts, bounded normalization, safe theme codes, configurable wheel routes, bounded snapshots and opt-in deduplicated alerts.");
