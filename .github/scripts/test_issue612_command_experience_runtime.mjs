#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import fs from "node:fs";
import vm from "node:vm";
import { JSDOM } from "jsdom";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const markers = ["    function " + name + "(", "    async function " + name + "("];
  const starts = markers.map(marker => source.indexOf(marker)).filter(index => index >= 0);
  assert.ok(starts.length, name + " is missing");
  const start = Math.min(...starts);
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

const fakeWebhook = ["https:", "", "discord.com", "api", "webhooks", "123456789", "THIS_IS_A_FAKE_SECRET_TOKEN"].join("/");
const privateBackup = {
  format: "MissionChief Map Command Toolkit Private Settings Backup",
  schema: 5,
  version: "9.3.0",
  state: {
    theme: "incident",
    tabletMode: "on",
    mobileMode: "off",
    interfaceDensity: { desktop: "compact", tablet: "command" },
    quickWheel: { enabled: true, actions: ["myMissions", "allianceMissions", "vehicles", "buildings", "pressureBoard", "fullscreen"] },
  },
  integrations: { discordWebhook: fakeWebhook },
  financialArchiveStore: { schema: 1, profiles: { test: { transactions: [1, 2, 3] } } },
};

const cryptoSandbox = {
  console,
  crypto: webcrypto,
  pageWindow: { crypto: webcrypto, btoa, atob },
  btoa,
  atob,
  Uint8Array,
  TextEncoder,
  TextDecoder,
  JSON,
  Date,
  SETTINGS_TRANSFER: {
    format: "MissionChief Map Command Toolkit Encrypted Settings Transfer",
    schema: 1,
    iterations: 310000,
    saltBytes: 16,
    ivBytes: 12,
  },
  SCRIPT: { version: "9.3.0" },
  buildToolkitSettingsBackup() {
    return JSON.parse(JSON.stringify(privateBackup));
  },
  extractImportedToolkitState(value) {
    return value?.state || null;
  },
};
vm.createContext(cryptoSandbox);
vm.runInContext(
  [
    "settingsTransferBytesToBase64",
    "settingsTransferBase64ToBytes",
    "settingsTransferCrypto",
    "settingsTransferAdditionalData",
    "settingsTransferKey",
    "validateSettingsTransferEnvelope",
    "encryptToolkitSettings",
    "decryptToolkitSettings",
  ].map(extractFunction).join("\n") +
  "\nthis.__probe = { encrypt: encryptToolkitSettings, decrypt: decryptToolkitSettings, validate: validateSettingsTransferEnvelope };",
  cryptoSandbox,
  { filename: "issue612-settings-transfer-runtime.js" },
);

const passphrase = "Correct Horse Battery Staple 2026";
const envelope = await cryptoSandbox.__probe.encrypt(passphrase, new Date("2026-07-31T10:00:00Z"));
assert.equal(envelope.format, cryptoSandbox.SETTINGS_TRANSFER.format);
assert.equal(envelope.crypto.cipher, "AES-GCM");
assert.equal(envelope.crypto.kdf, "PBKDF2-SHA-256");
assert.equal(envelope.crypto.iterations, 310000);
assert.equal(Buffer.from(envelope.crypto.salt, "base64").length, 16);
assert.equal(Buffer.from(envelope.crypto.iv, "base64").length, 12);
assert.doesNotMatch(JSON.stringify(envelope), /THIS_IS_A_FAKE_SECRET_TOKEN/u);
assert.doesNotMatch(JSON.stringify(envelope), /discord\.com\/api\/webhooks/u);
assert.doesNotMatch(JSON.stringify(envelope), /transactions/u);

const decrypted = await cryptoSandbox.__probe.decrypt(envelope, passphrase);
assert.equal(decrypted.integrations.discordWebhook, fakeWebhook);
assert.equal(decrypted.state.interfaceDensity.tablet, "command");
await assert.rejects(
  cryptoSandbox.__probe.decrypt(envelope, "wrong passphrase"),
  /wrong or the encrypted file has been altered/u,
);
const tampered = JSON.parse(JSON.stringify(envelope));
tampered.ciphertext = (tampered.ciphertext[0] === "A" ? "B" : "A") + tampered.ciphertext.slice(1);
await assert.rejects(
  cryptoSandbox.__probe.decrypt(tampered, passphrase),
  /wrong or the encrypted file has been altered/u,
);
assert.throws(
  () => cryptoSandbox.__probe.validate({ ...envelope, crypto: { ...envelope.crypto, iterations: 1000 } }),
  /key settings are invalid/u,
);
const secondEnvelope = await cryptoSandbox.__probe.encrypt(passphrase, new Date("2026-07-31T10:00:00Z"));
assert.notEqual(secondEnvelope.crypto.salt, envelope.crypto.salt);
assert.notEqual(secondEnvelope.crypto.iv, envelope.crypto.iv);
assert.notEqual(secondEnvelope.ciphertext, envelope.ciphertext);

const dom = new JSDOM("<!doctype html><html><body><div id='map'></div><button id='return-focus'>Return</button></body></html>", {
  url: "https://www.missionchief.co.uk/",
  pretendToBeVisual: true,
});
let draggingEnabled = true;
let invalidateCount = 0;
const mockMap = {
  dragging: {
    enabled: () => draggingEnabled,
    disable: () => { draggingEnabled = false; },
    enable: () => { draggingEnabled = true; },
  },
  invalidateSize: () => { invalidateCount += 1; },
};
const uiSandbox = {
  console,
  document: dom.window.document,
  HTMLElement: dom.window.HTMLElement,
  SCRIPT: {
    quickWheelId: "mc-map-command-toolkit-quick-wheel",
    fullscreenExitId: "mc-map-command-toolkit-fullscreen-exit",
  },
  QUICK_WHEEL_ACTIONS: {
    myMissions: { label: "My Missions", icon: "1" },
    allianceMissions: { label: "Alliance", icon: "2" },
    vehicles: { label: "Vehicles", icon: "3" },
    buildings: { label: "Buildings", icon: "4" },
    pressureBoard: { label: "Pressure", icon: "P" },
    fullscreen: { label: "Full Screen", icon: "F" },
  },
  state: {
    fullscreenMap: false,
    safeMode: { enabled: false },
    quickWheel: {
      enabled: true,
      slotCount: 6,
      slots: ["myMissions", "allianceMissions", "vehicles", "buildings", "pressureBoard", "fullscreen"].map(id => ({ kind: "action", id })),
    },
    interfaceDensity: { desktop: "compact", tablet: "command" },
  },
  activeDeviceLayout: "tablet",
  quickWheelRestoreDragging: false,
  quickWheelReturnFocus: null,
  fullscreenMapTarget: null,
  findLeafletMapInstance: () => mockMap,
  getViewportMetrics: () => ({ width: 730, height: 1200, offsetLeft: 0, offsetTop: 0 }),
  toolkitCommandShellContextActive: () => true,
  toolkitPrimaryMapElement: () => dom.window.document.getElementById("map"),
  getLargestLeafletMap: () => dom.window.document.getElementById("map"),
  saveState() {},
  setInnerHtmlIfChanged(element, html) { element.innerHTML = html; },
  applyRootAttributes() {},
  fitControlToMap() {},
  positionPanelOverlay() {},
  showToast() {},
  quickWheelSlotMeta(slot) { return { ...slot, ...uiSandbox.QUICK_WHEEL_ACTIONS[slot.id] }; },
  toggleFeature(command) { uiSandbox.lastToggle = command; },
  toggleOperationalPressureBoard() { uiSandbox.pressureToggled = true; },
  openPanel() { uiSandbox.panelOpened = true; },
};
vm.createContext(uiSandbox);
vm.runInContext(
  [
    "escapeHtml",
    "clamp",
    "setAttributeIfChanged",
    "commandExperienceElement",
    "interfaceDensityForLayout",
    "findFullscreenMapTarget",
    "applyMapFullscreenState",
    "setMapFullscreen",
    "closeTabletQuickWheel",
    "openTabletQuickWheel",
    "executeQuickWheelCommand",
  ].map(extractFunction).join("\n") +
  "\nthis.__probe = {" +
  "density: interfaceDensityForLayout, openWheel: openTabletQuickWheel, closeWheel: closeTabletQuickWheel," +
  "wheelCommand: executeQuickWheelCommand, fullscreen: setMapFullscreen" +
  "};",
  uiSandbox,
  { filename: "issue612-responsive-runtime.js" },
);

assert.equal(uiSandbox.__probe.density("desktop"), "compact");
assert.equal(uiSandbox.__probe.density("tablet"), "command");
assert.equal(uiSandbox.__probe.density("mobile"), "standard");
assert.equal(uiSandbox.__probe.openWheel({ x: 2, y: 2 }), true);
const wheel = dom.window.document.getElementById(uiSandbox.SCRIPT.quickWheelId);
assert.ok(wheel);
assert.equal(wheel.querySelectorAll("[role='menuitem']").length, 6);
assert.equal(wheel.style.getPropertyValue("--mcms-wheel-x"), "128px");
assert.equal(wheel.style.getPropertyValue("--mcms-wheel-y"), "128px");
assert.equal(draggingEnabled, false);
uiSandbox.__probe.closeWheel();
assert.equal(draggingEnabled, true);
assert.equal(dom.window.document.getElementById(uiSandbox.SCRIPT.quickWheelId), null);
uiSandbox.activeDeviceLayout = "desktop";
assert.equal(uiSandbox.__probe.openWheel({ x: 400, y: 400 }), false);
uiSandbox.activeDeviceLayout = "tablet";
uiSandbox.__probe.wheelCommand("myMissions");
assert.equal(uiSandbox.lastToggle, "myMissions");

uiSandbox.__probe.fullscreen(true);
assert.equal(uiSandbox.state.fullscreenMap, true);
assert.ok(dom.window.document.getElementById("map").classList.contains("mcms-map-fullscreen-target"));
assert.ok(dom.window.document.getElementById(uiSandbox.SCRIPT.fullscreenExitId));
assert.equal(dom.window.document.documentElement.getAttribute("data-mcms-map-fullscreen"), "true");
uiSandbox.__probe.fullscreen(false);
assert.equal(uiSandbox.state.fullscreenMap, false);
assert.equal(dom.window.document.getElementById(uiSandbox.SCRIPT.fullscreenExitId), null);
assert.ok(invalidateCount >= 2);

const briefingDom = new JSDOM("<!doctype html><html><body></body></html>", { pretendToBeVisual: true });
let briefingOpened = 0;
const briefingSandbox = {
  document: briefingDom.window.document,
  state: { setupWizard: { completed: true }, updateBriefing: { enabled: true, seenVersion: "9.2.0" } },
  SCRIPT: { version: "9.3.0", commandExperienceModalId: "command-modal" },
  bootStartedAt: Date.now() - 5000,
  transportSweepRuntime: { running: true },
  isVisible: () => true,
  openUpdateBriefing: () => { briefingOpened += 1; return true; },
  Date,
};
Object.defineProperty(briefingDom.window.document, "hidden", { value: false, configurable: true });
vm.createContext(briefingSandbox);
vm.runInContext(
  extractFunction("commandExperienceElement") + "\n" +
    extractFunction("maybeShowUpdateBriefing") + "\nthis.__probe = maybeShowUpdateBriefing;",
  briefingSandbox,
);
assert.equal(briefingSandbox.__probe(), false);
assert.equal(briefingOpened, 0);
briefingSandbox.transportSweepRuntime.running = false;
assert.equal(briefingSandbox.__probe(), true);
assert.equal(briefingOpened, 1);
briefingSandbox.state.updateBriefing.seenVersion = "9.3.0";
assert.equal(briefingSandbox.__probe(), false);

console.log("Issue #612 runtime passed: authenticated settings transfer, secret redaction, tamper rejection, Tablet wheel geometry, density, fullscreen recovery and deferred update briefing.");
