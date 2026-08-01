#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { performance } from "node:perf_hooks";
import { fileURLToPath } from "node:url";
import * as acorn from "acorn";
import { JSDOM } from "jsdom";
import { instrumentSource } from "../../tools/build-render-probe-userscript.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const SOURCE_PATH = path.join(ROOT, "src/MissionChief_Map_Command_Toolkit.user.js");
const BASELINE_PATH = path.join(ROOT, "docs/audits/issue-255/unchanged-update-ui.json");
const EXPECTED_VERSION = "10.2.2";
const EXPECTED_SHA = "d09df85749a2f28ccdbfc7b9e628d87375422cdc87cf270f7448e42afeb4bf84";
const REPEATS = 25;
const HELPER_NAMES = ["normaliseDiscordReportComplexity", "discordReportComplexityAtLeast", "updateUiToggleClass", "updateUiSetStyleProperty", "updateUiSetAttribute", "updateUiSetDataset", "updateUiSetProperty", "updateUiSetText", "commandInterfaceApplySearch", "updateCommandInterfaceHeader"];

function walk(node, visit) {
  if (!node || typeof node !== "object") return;
  visit(node);
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) value.forEach(item => walk(item, visit));
    else if (value && typeof value === "object" && typeof value.type === "string") walk(value, visit);
  }
}

function extractFunctions(source, names) {
  const ast = acorn.parse(source, { ecmaVersion: "latest", sourceType: "script", allowHashBang: true });
  const found = new Map();
  walk(ast, node => {
    if (node.type === "FunctionDeclaration" && node.id?.name && names.includes(node.id.name)) {
      if (found.has(node.id.name)) throw new Error(`Duplicate function declaration: ${node.id.name}`);
      found.set(node.id.name, source.slice(node.start, node.end));
    }
  });
  for (const name of names) assert.ok(found.has(name), `${name} is missing`);
  return names.map(name => found.get(name));
}

function fixtureHtml() {
  const controlToggles = ["allianceMissions", "myMissions", "vehicles", "buildings", "allianceCredits", "missionAge", "transportWatcher", "unitCommitment", "stuckDetector"];
  const panelToggles = ["clean", "markerFocus", "missionPulse", "roadPriority", "coverage", "shortcuts", "quickWheel", "autoLoadAllVehicles", "allianceBuildingsMapBlocker", "majorIncidentFeed", "missionLockAudio", "payoutFlash", "payoutSound", "missionValue", "customVehicleBadges", "stuckDetector", "missionSpawn", "resourceGap", "allianceMissions", "myMissions", "vehicles", "buildings", "allianceCredits", "missionAge", "transportWatcher", "unitCommitment"];
  const settings = ["density-desktop", "density-tablet", ...Array.from({ length: 6 }, (_, index) => `quick-wheel-slot-${index}`), "major-incident-minimum", "coverage-radius", "alliance-credit-minimum", "transport-sweep-delay", "transport-sweep-max", "payout-template", "resource-gap-radius", "stuck-threshold", "payout-threshold", "payout-duration", "payout-volume", "discord-webhook", "discord-name", "discord-top-categories", "discord-period", "discord-custom-start", "discord-custom-end", "discord-comparison", "discord-chart", "discord-complexity", "discord-risk", "discord-forecast", "finance-vault-enabled", "finance-vault-retention", "finance-rule-feed"];
  return `<!doctype html><html><body>
    <div id="mc-map-command-toolkit-control">
      ${controlToggles.map(key => `<button data-toggle="${key}"><span class="mcms-float-label-desktop">${key}</span><span class="mcms-control-state"></span></button>`).join("")}
      <button data-action="open-vehicle-status"><span class="mcms-control-state"></span></button><button data-action="open-pressure-board"><span class="mcms-control-state"></span></button><button class="mcms-economy-btn"><span class="mcms-control-state"></span></button>
      <button class="mcms-menu-btn"></button>
    </div>
    <div id="mc-map-command-toolkit-panel">
      <div class="mcms-title"></div><div class="mcms-subtitle"></div><input data-command-search><div class="mcms-command-search-empty" hidden></div>
      <div class="mcms-tabs">${["map", "missions", "finance", "locations", "appearance", "settings"].map(key => `<button class="mcms-tab-btn" data-tab="${key}"></button>`).join("")}</div>
      ${["map", "missions", "finance", "locations", "appearance", "settings"].map(key => `<section class="mcms-tab-panel" data-panel="${key}"><article class="mcms-command-card" data-command-search="${key}">${key}</article></section>`).join("")}
      <button class="mcms-ui-theme-btn" data-ui-theme="mapCommand"></button><button class="mcms-ui-theme-btn" data-ui-theme="cyberpunk"></button>
      <button class="mcms-theme-btn" data-theme="classic"></button><button class="mcms-theme-btn" data-theme="dark"></button>
      <button class="mcms-position-btn" data-position="bottomRight"></button><button class="mcms-position-btn" data-position="topLeft"></button>
      ${panelToggles.map(key => `<button data-toggle="${key}"><span class="mcms-pill"></span></button>`).join("")}
      <button class="mcms-action-toggle mcms-command-bar-setting"><span class="mcms-pill"></span></button>
      <button class="mcms-action-toggle mcms-economy-setting"><span class="mcms-pill"></span></button>
      <button class="mcms-action-toggle mcms-fullscreen-setting"><span class="mcms-pill"></span></button>
      <button class="mcms-action-toggle mcms-pressure-board-toggle"><span class="mcms-pill"></span></button>
      ${settings.map(key => `<input data-setting="${key}">`).join("")}
      <div data-discord-complexity-help></div>
      <div data-discord-min-complexity="informative"></div><div data-discord-min-complexity="wolf"></div>
      <div class="mcms-economy-status"></div><div class="mcms-nudge-value"></div>
    </div>
    <div id="mc-map-command-toolkit-vehicle-status"></div>
  </body></html>`;
}

function baseState() {
  return {
    majorIncidentFeed: { enabled: false, minimumCredits: 25000 }, position: "bottomRight", nudge: { x: 0, y: 0 }, commandBarOpen: true,
    visibility: { allianceMissions: true, myMissions: true, vehicles: true, buildings: true }, allianceCredits: true, missionAge: true,
    transportWatcher: true, unitCommitment: true, economyMode: false, fullscreenMap: false, activeTab: "map", uiTheme: "mapCommand", theme: "classic",
    interfaceDensity: { desktop: "standard", tablet: "compact" },
    inputStudio: { hotkeys: { menu: "M", palette: "K", myMissions: "1", allianceMissions: "2", vehicles: "3", buildings: "4", allianceCredits: "5", missionAge: "6", transportWatcher: "7", unitCommitment: "8", vehicleCodes: "V", pressureBoard: "B", clean: "C", markerFocus: "F", missionPulse: "P", roadPriority: "R", safeMode: "Shift+S" }, gestures: { enabled: false } },
    updateBriefing: { enabled: true, seenVersion: "", seenFeatures: [] }, safeMode: { enabled: false },
    quickWheel: { enabled: true, slotCount: 6, slots: ["myMissions", "allianceMissions", "vehicles", "buildings", "pressureBoard", "fullscreen"].map(id => ({ kind: "action", id })) },
    cleanMode: false, markerFocus: false, missionPulse: true, roadPriority: false, coverage: { enabled: true, radiusMi: 10 }, shortcuts: true,
    autoLoadAllVehicles: true, allianceBuildingsMap: true, missionLockAudio: true,
    payoutFlash: { enabled: true, soundEnabled: true, template: "command", threshold: 10000, durationMs: 5000, soundVolume: 0.35 },
    missionValue: true, customVehicleBadges: true, stuckDetector: { enabled: true, thresholdMin: 10 }, missionSpawn: { enabled: true },
    resourceGap: { enabled: true, radiusMi: 20 }, allianceCreditMinimum: 10000, transportSweep: { delayMs: 900, maxPerRun: 25 },
    discordReport: { webhookName: "Toolkit", topCategories: 5, period: "daily", customStart: "", customEnd: "", includeComparison: true, includeChart: true, complexity: "informative", includeRisk: true, includeForecast: true },
    financialVault: { enabled: true, retentionDays: 90, ruleFeedEnabled: true },
  };
}

function installCounters(window) {
  const counters = { selectorReads: 0, writeAttempts: 0, changedWriteAttempts: 0, byKind: {} };
  const restores = [];
  const record = (kind, before, after) => {
    counters.writeAttempts += 1;
    const changed = before !== after;
    if (changed) counters.changedWriteAttempts += 1;
    const entry = counters.byKind[kind] ||= { attempts: 0, changed: 0 };
    entry.attempts += 1;
    if (changed) entry.changed += 1;
  };
  const wrapRead = (prototype, name) => {
    const original = prototype?.[name]; if (typeof original !== "function") return;
    prototype[name] = function (...args) { counters.selectorReads += 1; return original.apply(this, args); };
    restores.push(() => { prototype[name] = original; });
  };
  const wrapMethod = (prototype, name, kind, beforeValue, afterValue) => {
    const original = prototype?.[name]; if (typeof original !== "function") return;
    prototype[name] = function (...args) { const before = beforeValue.call(this, args); const result = original.apply(this, args); record(kind, before, afterValue.call(this, args)); return result; };
    restores.push(() => { prototype[name] = original; });
  };
  const wrapSetter = (prototype, property, kind) => {
    const descriptor = Object.getOwnPropertyDescriptor(prototype, property);
    if (!descriptor?.get || !descriptor?.set || descriptor.configurable !== true) return;
    Object.defineProperty(prototype, property, { ...descriptor, set(value) { const before = descriptor.get.call(this); descriptor.set.call(this, value); record(kind, before, descriptor.get.call(this)); } });
    restores.push(() => Object.defineProperty(prototype, property, descriptor));
  };
  wrapRead(window.Document.prototype, "getElementById"); wrapRead(window.Element.prototype, "querySelector"); wrapRead(window.Element.prototype, "querySelectorAll");
  wrapMethod(window.Element.prototype, "setAttribute", "setAttribute", function ([name]) { return this.getAttribute(name); }, function ([name]) { return this.getAttribute(name); });
  wrapMethod(window.DOMTokenList.prototype, "toggle", "classToggle", function ([token]) { return this.contains(token); }, function ([token]) { return this.contains(token); });
  wrapMethod(window.CSSStyleDeclaration.prototype, "setProperty", "styleSetProperty", function ([name]) { return `${this.getPropertyValue(name)}|${this.getPropertyPriority(name)}`; }, function ([name]) { return `${this.getPropertyValue(name)}|${this.getPropertyPriority(name)}`; });
  wrapSetter(window.HTMLInputElement.prototype, "value", "inputValue"); wrapSetter(window.Node.prototype, "textContent", "textContent");
  wrapSetter(window.HTMLElement.prototype, "title", "title"); wrapSetter(window.HTMLElement.prototype, "hidden", "hidden"); wrapSetter(window.HTMLElement.prototype, "tabIndex", "tabIndex");
  return { reset() { counters.selectorReads = 0; counters.writeAttempts = 0; counters.changedWriteAttempts = 0; counters.byKind = {}; }, snapshot() { return JSON.parse(JSON.stringify(counters)); }, restore() { restores.reverse().forEach(fn => fn()); } };
}

function summariseMutations(records) {
  const summary = { records: records.length, attributes: 0, childList: 0, characterData: 0, sameValueAttributes: 0 };
  for (const record of records) {
    if (record.type === "attributes") { summary.attributes += 1; if (record.oldValue === record.target.getAttribute(record.attributeName)) summary.sameValueAttributes += 1; }
    else if (record.type === "childList") summary.childList += 1; else if (record.type === "characterData") summary.characterData += 1;
  }
  return summary;
}

async function flush(window) { await Promise.resolve(); await new Promise(resolve => window.setTimeout(resolve, 0)); await Promise.resolve(); }
function median(values) { const sorted = [...values].sort((a, b) => a - b); const index = Math.floor(sorted.length / 2); return sorted.length % 2 ? sorted[index] : (sorted[index - 1] + sorted[index]) / 2; }

function verifyState(window, state) {
  const control = window.document.getElementById("mc-map-command-toolkit-control");
  const panel = window.document.getElementById("mc-map-command-toolkit-panel");
  const economy = control.querySelector(".mcms-economy-btn");
  assert.equal(economy.classList.contains("mcms-on"), state.economyMode);
  assert.equal(economy.getAttribute("aria-pressed"), String(state.economyMode));
  assert.equal(control.style.getPropertyValue("--mcms-nudge-x"), `${state.nudge.x}px`);
  assert.equal(control.style.getPropertyValue("--mcms-nudge-y"), `${state.nudge.y}px`);
  for (const button of panel.querySelectorAll(".mcms-tab-btn")) {
    const active = button.dataset.tab === state.activeTab;
    assert.equal(button.classList.contains("mcms-active"), active);
    assert.equal(button.getAttribute("aria-selected"), String(active));
    assert.equal(button.tabIndex, active ? 0 : -1);
  }
  for (const section of panel.querySelectorAll(".mcms-tab-panel")) {
    const active = section.dataset.panel === state.activeTab;
    assert.equal(section.classList.contains("mcms-active"), active);
    assert.equal(section.hidden, !active);
  }
  assert.equal(panel.querySelector(".mcms-nudge-value").textContent, `X ${state.nudge.x} / Y ${state.nudge.y}`);
  assert.equal(panel.querySelector('[data-discord-complexity-help]').textContent.length > 0, true);
  assert.equal(panel.querySelector('[data-discord-min-complexity="informative"]').hidden, false);
  assert.equal(panel.querySelector('[data-discord-min-complexity="wolf"]').hidden, true);
}

function parseArgs(argv) { const result = {}; for (let i = 0; i < argv.length; i += 2) { const key = argv[i], value = argv[i + 1]; if (!key?.startsWith("--") || !value) throw new Error("Expected --key value arguments"); result[key.slice(2)] = value; } return result; }

export async function measureWriteSuppression() {
  const source = fs.readFileSync(SOURCE_PATH, "utf8");
  const sourceHash = crypto.createHash("sha256").update(source, "utf8").digest("hex");
  const version = source.match(/^\/\/\s*@version\s+([^\s]+)/mu)?.[1] || "unknown";
  assert.equal(version, EXPECTED_VERSION); assert.equal(sourceHash, EXPECTED_SHA);
  const baseline = JSON.parse(fs.readFileSync(BASELINE_PATH, "utf8"));
  const instrumented = instrumentSource(source);
  const functionSources = extractFunctions(instrumented.generated, [...HELPER_NAMES, "updateUI"]);
  const dom = new JSDOM(fixtureHtml(), { url: "https://www.missionchief.co.uk/", pretendToBeVisual: true });
  const { window } = dom; const counters = installCounters(window); const mutationRecords = [];
  const observer = new window.MutationObserver(records => mutationRecords.push(...records));
  observer.observe(window.document.documentElement, { subtree: true, childList: true, attributes: true, characterData: true, attributeOldValue: true, characterDataOldValue: true });
  const profiler = { begins: 0, ends: 0, beginRender(name) { assert.equal(name, "updateUI"); this.begins += 1; return this.begins; }, endRender(token) { assert.ok(token); this.ends += 1; } };
  const nestedCalls = {}; const countNested = name => { nestedCalls[name] = (nestedCalls[name] || 0) + 1; };
  const state = baseState();
  const sandbox = { console, globalThis: null, document: window.document, state, operationalStartupComplete: true,
    SCRIPT: { name: "MissionChief Map Command Toolkit", controlId: "mc-map-command-toolkit-control", panelId: "mc-map-command-toolkit-panel", vehicleStatusId: "mc-map-command-toolkit-vehicle-status", pressureBoardId: "mc-map-command-toolkit-pressure-board" }, POSITIONS: { topLeft: {}, topRight: {}, bottomLeft: {}, bottomRight: {} },
    FINANCE_REPORT_COMPLEXITIES: Object.freeze(["simple", "informative", "wolf"]), FINANCE_REPORT_COMPLEXITY_RANK: Object.freeze({ simple: 0, informative: 1, wolf: 2 }), FINANCE_REPORT_COMPLEXITY_COPY: Object.freeze({ simple: "simple", informative: "informative", wolf: "wolf" }),
    COMMAND_SECTION_META: Object.freeze({ map: { label: "Map", title: "Map Controls" }, missions: { label: "Missions", title: "Mission Operations" }, finance: { label: "Finance", title: "Finance Command" }, locations: { label: "Locations", title: "Saved Locations" }, appearance: { label: "Appearance", title: "Appearance" }, settings: { label: "Settings", title: "Toolkit Settings" } }),
    commandSearchQuery: "", mobileModeActive: false,
    activeDockPosition: () => state.position, quickWheelSlotValue: slot => `${slot.kind}:${slot.id}`,
    applyRootAttributes: () => countNested("applyRootAttributes"), scheduleMajorIncidentFeedRender: () => countNested("scheduleMajorIncidentFeedRender"), removeMajorIncidentFeed: () => countNested("removeMajorIncidentFeed"), toolkitApplyCommandBarState: () => countNested("toolkitApplyCommandBarState"), refreshTabletModeUi: () => countNested("refreshTabletModeUi"), updateAllianceMemberManagerMenuControl: () => countNested("updateAllianceMemberManagerMenuControl"), renderTransportSweepPanel: () => countNested("renderTransportSweepPanel"), getDiscordWebhookUrl: () => "https://discord.invalid/webhook", setDiscordStatus: () => countNested("setDiscordStatus"), discordFinanceStatus: "ready", discordFinanceStatusTone: "success", setOperationalSitrepStatus: () => countNested("setOperationalSitrepStatus"), operationalSitrepStatus: "ready", operationalSitrepStatusTone: "neutral", operationalPressureBoardOpen: () => false, renderFinanceVaultStatus: () => countNested("renderFinanceVaultStatus"), renderProfiles: () => countNested("renderProfiles"), operationalVisible: false, operationalUiIsVisible: () => sandbox.operationalVisible, renderOperationalPanels: () => countNested("renderOperationalPanels"), __MCMS_PROFILER__: profiler };
  sandbox.globalThis = sandbox; vm.createContext(sandbox); vm.runInContext(`${functionSources.join("\n")}\nthis.__api={updateUI};`, sandbox, { filename: "update-ui-write-suppression-v9.0.1.js" });
  const panel = window.document.getElementById(sandbox.SCRIPT.panelId);
  async function resetEvidence() { await flush(window); mutationRecords.length = 0; observer.takeRecords(); counters.reset(); profiler.begins = 0; profiler.ends = 0; for (const key of Object.keys(nestedCalls)) delete nestedCalls[key]; }
  async function capture(call) { const started = performance.now(); call(); const elapsed = performance.now() - started; await flush(window); mutationRecords.push(...observer.takeRecords()); return { counters: counters.snapshot(), mutations: summariseMutations(mutationRecords), elapsed }; }
  const scenarios = [
    { name: "idle-panel-closed", open: false, tab: "map", operational: false }, { name: "settings-open", open: true, tab: "settings", operational: false },
    { name: "missions-open", open: true, tab: "missions", operational: true }, { name: "finance-open", open: true, tab: "finance", operational: false },
  ];
  const unchanged = [];
  for (const scenario of scenarios) {
    panel.classList.toggle("mcms-open", scenario.open); state.activeTab = scenario.tab; sandbox.operationalVisible = scenario.operational; sandbox.__api.updateUI(); await resetEvidence();
    const durations = []; for (let i = 0; i < REPEATS; i += 1) { const started = performance.now(); sandbox.__api.updateUI(); durations.push(performance.now() - started); }
    await flush(window); mutationRecords.push(...observer.takeRecords()); const counts = counters.snapshot(); const mutations = summariseMutations(mutationRecords);
    assert.equal(counts.writeAttempts, 0, `${scenario.name}: unchanged writes remain`); assert.equal(mutations.records, 0, `${scenario.name}: unchanged mutations remain`);
    assert.equal(profiler.begins, REPEATS); assert.equal(profiler.ends, REPEATS);
    unchanged.push({ name: scenario.name, repeats: REPEATS, selectorReads: counts.selectorReads, writeAttempts: counts.writeAttempts, changedWriteAttempts: counts.changedWriteAttempts, mutations, medianSynchronousMs: median(durations), maximumSynchronousMs: Math.max(...durations) });
  }

  panel.classList.add("mcms-open"); state.activeTab = "settings"; state.economyMode = false; state.nudge = { x: 0, y: 0 }; sandbox.operationalVisible = false; sandbox.__api.updateUI(); await resetEvidence();
  state.activeTab = "missions"; state.economyMode = true; state.nudge = { x: 3, y: -2 };
  const transitionChanged = await capture(() => sandbox.__api.updateUI()); verifyState(window, state);
  assert.ok(transitionChanged.counters.changedWriteAttempts > 0); assert.ok(transitionChanged.mutations.records > 0);
  await resetEvidence(); const transitionStable = await capture(() => sandbox.__api.updateUI());
  assert.equal(transitionStable.counters.writeAttempts, 0); assert.equal(transitionStable.mutations.records, 0);

  const replacementDom = new JSDOM(fixtureHtml(), { url: "https://www.missionchief.co.uk/", pretendToBeVisual: true });
  for (const id of [sandbox.SCRIPT.controlId, sandbox.SCRIPT.panelId, sandbox.SCRIPT.vehicleStatusId]) {
    const fresh = window.document.importNode(replacementDom.window.document.getElementById(id), true);
    window.document.getElementById(id).replaceWith(fresh);
  }
  replacementDom.window.close(); await resetEvidence();
  const replacementChanged = await capture(() => sandbox.__api.updateUI()); verifyState(window, state);
  assert.ok(replacementChanged.counters.changedWriteAttempts > 0); assert.ok(replacementChanged.mutations.records > 0);
  await resetEvidence(); const replacementStable = await capture(() => sandbox.__api.updateUI());
  assert.equal(replacementStable.counters.writeAttempts, 0); assert.equal(replacementStable.mutations.records, 0);

  observer.disconnect(); counters.restore(); dom.window.close();
  const report = { schemaVersion: 1, issue: 255, parentIssue: 247, toolkitVersion: version, sourceSha256: sourceHash, measurement: "rendered-jsdom-disposable-render-probe", productionSourceModifiedByMeasurement: false,
    before: { toolkitVersion: baseline.source.version, sourceSha256: baseline.source.sha256, calls: baseline.scenarios.reduce((sum, item) => sum + item.repeats, 0), selectorReads: baseline.summary.selectorReads, writeAttempts: baseline.summary.writeAttempts, mutationRecords: baseline.summary.mutationRecords },
    after: { calls: unchanged.reduce((sum, item) => sum + item.repeats, 0), selectorReads: unchanged.reduce((sum, item) => sum + item.selectorReads, 0), writeAttempts: unchanged.reduce((sum, item) => sum + item.writeAttempts, 0), mutationRecords: unchanged.reduce((sum, item) => sum + item.mutations.records, 0), scenarios: unchanged },
    stateTransition: { changed: transitionChanged, stableRepeat: transitionStable }, frameworkReplacement: { changed: replacementChanged, stableRepeat: replacementStable },
    reductions: { unchangedWriteAttempts: baseline.summary.writeAttempts, unchangedMutationRecords: baseline.summary.mutationRecords, writeAttemptPercent: 100, mutationRecordPercent: 100 },
    interpretationBoundary: "Exact rendered fixture proof for the direct updateUI shell. Synchronous jsdom timings are diagnostic only and are not a live browser frame-rate claim." };
  assert.equal(report.after.writeAttempts, 0); assert.equal(report.after.mutationRecords, 0); assert.equal(report.before.writeAttempts, 14500); assert.equal(report.before.mutationRecords, 7100);
  return report;
}

function markdown(report) { return [`# Issue #255 — Toolkit ${report.toolkitVersion} \`updateUI()\` same-value write suppression`, "", `- Before unchanged write attempts: ${report.before.writeAttempts.toLocaleString("en-GB")}`, `- After unchanged write attempts: ${report.after.writeAttempts}`, `- Before mutation records: ${report.before.mutationRecords.toLocaleString("en-GB")}`, `- After mutation records: ${report.after.mutationRecords}`, `- State transition changed writes: ${report.stateTransition.changed.counters.changedWriteAttempts}`, `- State transition mutation records: ${report.stateTransition.changed.mutations.records}`, `- Framework replacement changed writes: ${report.frameworkReplacement.changed.counters.changedWriteAttempts}`, `- Framework replacement mutation records: ${report.frameworkReplacement.changed.mutations.records}`, "", "The first changed-state and replacement-DOM passes still apply state. Their immediate stable repeats produce zero writes and zero mutation records.", "", `> ${report.interpretationBoundary}`, ""].join("\n"); }

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) { const options = parseArgs(process.argv.slice(2)); const report = await measureWriteSuppression(); if (options["json-output"]) { fs.mkdirSync(path.dirname(path.resolve(options["json-output"])), { recursive: true }); fs.writeFileSync(path.resolve(options["json-output"]), `${JSON.stringify(report, null, 2)}\n`); } if (options["markdown-output"]) { fs.mkdirSync(path.dirname(path.resolve(options["markdown-output"])), { recursive: true }); fs.writeFileSync(path.resolve(options["markdown-output"]), `${markdown(report)}\n`); } console.log(`Issue #255 write suppression retained by Toolkit ${report.toolkitVersion}: ${report.before.writeAttempts} → ${report.after.writeAttempts} unchanged writes; ${report.before.mutationRecords} → ${report.after.mutationRecords} mutations.`); }
