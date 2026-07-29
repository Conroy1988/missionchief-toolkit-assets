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
const EXPECTED_VERSION = "8.3.1";
const EXPECTED_SHA = "363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089";
const DEFAULT_REPEATS = 25;

function walk(node, visit) {
  if (!node || typeof node !== "object") return;
  visit(node);
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) value.forEach(item => walk(item, visit));
    else if (value && typeof value === "object" && typeof value.type === "string") walk(value, visit);
  }
}

function extractFunction(source, name) {
  const ast = acorn.parse(source, { ecmaVersion: "latest", sourceType: "script", allowHashBang: true });
  let found = null;
  walk(ast, node => {
    if (node.type === "FunctionDeclaration" && node.id?.name === name) {
      if (found) throw new Error(`Duplicate function declaration: ${name}`);
      found = node;
    }
  });
  if (!found) throw new Error(`Missing function declaration: ${name}`);
  return source.slice(found.start, found.end);
}

function fixtureHtml() {
  const controlToggles = ["allianceMissions", "myMissions", "vehicles", "buildings", "allianceCredits", "missionAge", "transportWatcher", "unitCommitment"];
  const panelToggles = [
    "clean", "markerFocus", "missionPulse", "roadPriority", "coverage", "shortcuts", "autoLoadAllVehicles",
    "allianceBuildingsMapBlocker", "majorIncidentFeed", "missionLockAudio", "payoutFlash", "payoutSound",
    "missionValue", "customVehicleBadges", "stuckDetector", "missionSpawn", "resourceGap", "allianceMissions",
    "myMissions", "vehicles", "buildings", "allianceCredits", "missionAge", "transportWatcher", "unitCommitment",
  ];
  const settings = [
    "major-incident-minimum", "coverage-radius", "alliance-credit-minimum", "transport-sweep-delay", "transport-sweep-max",
    "payout-template", "resource-gap-radius", "stuck-threshold", "payout-threshold", "payout-duration", "payout-volume",
    "discord-webhook", "discord-name", "discord-top-categories", "discord-period", "discord-custom-start", "discord-custom-end",
    "discord-comparison", "discord-chart", "discord-report-mode", "discord-risk", "discord-forecast", "finance-vault-enabled",
    "finance-vault-retention", "finance-rule-feed",
  ];
  return `<!doctype html><html><body>
    <div id="mc-map-command-toolkit-control">
      ${controlToggles.map(key => `<button data-toggle="${key}"></button>`).join("")}
      <button data-action="open-vehicle-status"></button>
      <button class="mcms-economy-btn"></button>
      <button class="mcms-dock-toggle-btn"><span class="mcms-dock-toggle-icon"></span></button>
      <button class="mcms-menu-btn"></button>
    </div>
    <div id="mc-map-command-toolkit-panel">
      ${["map", "settings", "resources", "ops", "discord"].map(key => `<button class="mcms-tab-btn" data-tab="${key}"></button><section class="mcms-tab-panel" data-panel="${key}"></section>`).join("")}
      <button class="mcms-ui-theme-btn" data-ui-theme="mapCommand"></button>
      <button class="mcms-ui-theme-btn" data-ui-theme="cyberpunk"></button>
      <button class="mcms-theme-btn" data-theme="classic"></button>
      <button class="mcms-theme-btn" data-theme="dark"></button>
      <button class="mcms-position-btn" data-position="bottomRight"></button>
      <button class="mcms-position-btn" data-position="topLeft"></button>
      ${panelToggles.map(key => `<button data-toggle="${key}"><span class="mcms-pill"></span></button>`).join("")}
      ${settings.map(key => `<input data-setting="${key}">`).join("")}
      <div class="mcms-economy-status"></div>
      <div class="mcms-nudge-value"></div>
    </div>
    <div id="mc-map-command-toolkit-vehicle-status"></div>
  </body></html>`;
}

function baseState() {
  return {
    majorIncidentFeed: { enabled: false, minimumCredits: 25000 },
    position: "bottomRight",
    nudge: { x: 0, y: 0 },
    commandBarOpen: true,
    visibility: { allianceMissions: true, myMissions: true, vehicles: true, buildings: true },
    allianceCredits: true,
    missionAge: true,
    transportWatcher: true,
    unitCommitment: true,
    economyMode: false,
    activeTab: "map",
    uiTheme: "mapCommand",
    theme: "classic",
    cleanMode: false,
    markerFocus: false,
    missionPulse: true,
    roadPriority: false,
    coverage: { enabled: true, radiusMi: 10 },
    shortcuts: true,
    autoLoadAllVehicles: true,
    allianceBuildingsMap: true,
    missionLockAudio: true,
    payoutFlash: { enabled: true, soundEnabled: true, template: "command", threshold: 10000, durationMs: 5000, soundVolume: 0.35 },
    missionValue: true,
    customVehicleBadges: true,
    stuckDetector: { enabled: true, thresholdMin: 10 },
    missionSpawn: { enabled: true },
    resourceGap: { enabled: true, radiusMi: 20 },
    allianceCreditMinimum: 10000,
    transportSweep: { delayMs: 900, maxPerRun: 25 },
    discordReport: {
      webhookName: "Toolkit", topCategories: 5, period: "daily", customStart: "", customEnd: "",
      includeComparison: true, includeChart: true, reportMode: "summary", includeRisk: true, includeForecast: true,
    },
    financialVault: { enabled: true, retentionDays: 90, ruleFeedEnabled: true },
  };
}

function installCounters(window) {
  const counters = { selectorReads: 0, writeAttempts: 0, changedWriteAttempts: 0, byKind: {} };
  const restores = [];
  const recordWrite = (kind, before, after) => {
    counters.writeAttempts += 1;
    const changed = before !== after;
    if (changed) counters.changedWriteAttempts += 1;
    const entry = counters.byKind[kind] ||= { attempts: 0, changed: 0 };
    entry.attempts += 1;
    if (changed) entry.changed += 1;
  };
  const wrapReadMethod = (prototype, name) => {
    const original = prototype?.[name];
    if (typeof original !== "function") return;
    prototype[name] = function (...args) { counters.selectorReads += 1; return original.apply(this, args); };
    restores.push(() => { prototype[name] = original; });
  };
  const wrapWriteMethod = (prototype, name, kind, beforeValue, afterValue) => {
    const original = prototype?.[name];
    if (typeof original !== "function") return;
    prototype[name] = function (...args) {
      const before = beforeValue.call(this, args);
      const result = original.apply(this, args);
      const after = afterValue.call(this, args);
      recordWrite(kind, before, after);
      return result;
    };
    restores.push(() => { prototype[name] = original; });
  };
  const wrapSetter = (prototype, property, kind) => {
    const descriptor = Object.getOwnPropertyDescriptor(prototype, property);
    if (!descriptor?.get || !descriptor?.set || descriptor.configurable !== true) return;
    Object.defineProperty(prototype, property, {
      ...descriptor,
      set(value) {
        const before = descriptor.get.call(this);
        descriptor.set.call(this, value);
        const after = descriptor.get.call(this);
        recordWrite(kind, before, after);
      },
    });
    restores.push(() => Object.defineProperty(prototype, property, descriptor));
  };

  wrapReadMethod(window.Document.prototype, "getElementById");
  wrapReadMethod(window.Element.prototype, "querySelector");
  wrapReadMethod(window.Element.prototype, "querySelectorAll");
  wrapWriteMethod(window.Element.prototype, "setAttribute", "setAttribute", function ([name]) { return this.getAttribute(name); }, function ([name]) { return this.getAttribute(name); });
  wrapWriteMethod(window.DOMTokenList.prototype, "toggle", "classToggle", function ([token]) { return this.contains(token); }, function ([token]) { return this.contains(token); });
  wrapWriteMethod(window.CSSStyleDeclaration.prototype, "setProperty", "styleSetProperty", function ([name]) { return `${this.getPropertyValue(name)}|${this.getPropertyPriority(name)}`; }, function ([name]) { return `${this.getPropertyValue(name)}|${this.getPropertyPriority(name)}`; });
  wrapSetter(window.HTMLInputElement.prototype, "value", "inputValue");
  wrapSetter(window.Node.prototype, "textContent", "textContent");
  wrapSetter(window.HTMLElement.prototype, "title", "title");
  wrapSetter(window.HTMLElement.prototype, "hidden", "hidden");
  wrapSetter(window.HTMLElement.prototype, "tabIndex", "tabIndex");

  return {
    reset() { counters.selectorReads = 0; counters.writeAttempts = 0; counters.changedWriteAttempts = 0; counters.byKind = {}; },
    snapshot() { return JSON.parse(JSON.stringify(counters)); },
    restore() { restores.reverse().forEach(restore => restore()); },
  };
}

function summariseMutations(records) {
  const summary = { records: records.length, attributes: 0, childList: 0, characterData: 0, sameValueAttributes: 0 };
  for (const record of records) {
    if (record.type === "attributes") {
      summary.attributes += 1;
      if (record.oldValue === record.target.getAttribute(record.attributeName)) summary.sameValueAttributes += 1;
    } else if (record.type === "childList") summary.childList += 1;
    else if (record.type === "characterData") summary.characterData += 1;
  }
  return summary;
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const index = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[index] : (sorted[index - 1] + sorted[index]) / 2;
}

async function flush(window) {
  await Promise.resolve();
  await new Promise(resolve => window.setTimeout(resolve, 0));
  await Promise.resolve();
}

function validateReport(report) {
  assert.equal(report.measurementOnly, true);
  assert.equal(report.source.version, EXPECTED_VERSION);
  assert.equal(report.source.sha256, EXPECTED_SHA);
  assert.deepEqual(report.scenarios.map(item => item.name), ["idle-panel-closed", "settings-open", "resources-open", "operations-open"]);
  for (const scenario of report.scenarios) {
    assert.equal(scenario.repeats, DEFAULT_REPEATS);
    assert.equal(scenario.renderProbeBegins, DEFAULT_REPEATS);
    assert.equal(scenario.renderProbeEnds, DEFAULT_REPEATS);
    assert.ok(scenario.selectorReads > 0, `${scenario.name}: selector reads missing`);
    assert.ok(scenario.writeAttempts > 0, `${scenario.name}: write attempts missing`);
    assert.equal(scenario.changedWriteAttempts, 0, `${scenario.name}: warm unchanged state was not stable`);
    assert.equal(scenario.redundantWriteAttempts, scenario.writeAttempts);
    assert.ok(scenario.mutations.records > 0, `${scenario.name}: no actual mutation records captured`);
  }
  assert.ok(report.summary.redundantWriteAttempts > 0);
  assert.ok(report.summary.mutationRecords > 0);
  return report;
}

export async function measureUnchangedUpdateUi() {
  const source = fs.readFileSync(SOURCE_PATH, "utf8");
  const sourceHash = crypto.createHash("sha256").update(source, "utf8").digest("hex");
  const version = source.match(/^\/\/\s*@version\s+([^\s]+)/mu)?.[1] || "unknown";
  assert.equal(sourceHash, EXPECTED_SHA);
  assert.equal(version, EXPECTED_VERSION);
  const instrumented = instrumentSource(source);
  const updateUiSource = extractFunction(instrumented.generated, "updateUI");
  const dom = new JSDOM(fixtureHtml(), { url: "https://www.missionchief.co.uk/", pretendToBeVisual: true });
  const { window } = dom;
  const counters = installCounters(window);
  const mutationRecords = [];
  const observer = new window.MutationObserver(records => mutationRecords.push(...records));
  observer.observe(window.document.documentElement, { subtree: true, childList: true, attributes: true, characterData: true, attributeOldValue: true, characterDataOldValue: true });
  const profiler = { begins: 0, ends: 0, beginRender(name) { assert.equal(name, "updateUI"); this.begins += 1; return this.begins; }, endRender(token) { assert.ok(token); this.ends += 1; } };
  const nestedCalls = {};
  const countNested = name => { nestedCalls[name] = (nestedCalls[name] || 0) + 1; };
  const state = baseState();
  const sandbox = {
    console,
    globalThis: null,
    document: window.document,
    state,
    operationalStartupComplete: true,
    SCRIPT: {
      controlId: "mc-map-command-toolkit-control",
      panelId: "mc-map-command-toolkit-panel",
      vehicleStatusId: "mc-map-command-toolkit-vehicle-status",
    },
    POSITIONS: { topLeft: {}, topRight: {}, bottomLeft: {}, bottomRight: {} },
    applyRootAttributes: () => countNested("applyRootAttributes"),
    scheduleMajorIncidentFeedRender: () => countNested("scheduleMajorIncidentFeedRender"),
    removeMajorIncidentFeed: () => countNested("removeMajorIncidentFeed"),
    toolkitApplyCommandBarState: () => countNested("toolkitApplyCommandBarState"),
    refreshTabletModeUi: () => countNested("refreshTabletModeUi"),
    updateAllianceMemberManagerMenuControl: () => countNested("updateAllianceMemberManagerMenuControl"),
    renderTransportSweepPanel: () => countNested("renderTransportSweepPanel"),
    getDiscordWebhookUrl: () => "https://discord.invalid/webhook",
    setDiscordStatus: () => countNested("setDiscordStatus"),
    discordFinanceStatus: "ready",
    discordFinanceStatusTone: "success",
    renderFinanceVaultStatus: () => countNested("renderFinanceVaultStatus"),
    renderProfiles: () => countNested("renderProfiles"),
    operationalVisible: false,
    operationalUiIsVisible: () => sandbox.operationalVisible,
    renderOperationalPanels: () => countNested("renderOperationalPanels"),
    __MCMS_PROFILER__: profiler,
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(`${updateUiSource}\nthis.__api = { updateUI };`, sandbox, { filename: "update-ui-render-probe-v8.3.1.js" });
  const panel = window.document.getElementById(sandbox.SCRIPT.panelId);
  const scenarios = [
    { name: "idle-panel-closed", open: false, tab: "map", operational: false },
    { name: "settings-open", open: true, tab: "settings", operational: false },
    { name: "resources-open", open: true, tab: "resources", operational: false },
    { name: "operations-open", open: true, tab: "ops", operational: true },
  ];
  const results = [];
  for (const scenario of scenarios) {
    panel.classList.toggle("mcms-open", scenario.open);
    state.activeTab = scenario.tab;
    sandbox.operationalVisible = scenario.operational;
    sandbox.__api.updateUI();
    await flush(window);
    mutationRecords.length = 0;
    observer.takeRecords();
    counters.reset();
    profiler.begins = 0;
    profiler.ends = 0;
    for (const key of Object.keys(nestedCalls)) delete nestedCalls[key];
    const durations = [];
    for (let iteration = 0; iteration < DEFAULT_REPEATS; iteration += 1) {
      const started = performance.now();
      sandbox.__api.updateUI();
      durations.push(performance.now() - started);
    }
    await flush(window);
    mutationRecords.push(...observer.takeRecords());
    const counts = counters.snapshot();
    results.push({
      name: scenario.name,
      scope: "direct updateUI shell; nested renderers and root-attribute reconciliation stubbed",
      repeats: DEFAULT_REPEATS,
      selectorReads: counts.selectorReads,
      selectorReadsPerCall: counts.selectorReads / DEFAULT_REPEATS,
      writeAttempts: counts.writeAttempts,
      writeAttemptsPerCall: counts.writeAttempts / DEFAULT_REPEATS,
      changedWriteAttempts: counts.changedWriteAttempts,
      redundantWriteAttempts: counts.writeAttempts - counts.changedWriteAttempts,
      writeAttemptsByKind: counts.byKind,
      mutations: summariseMutations(mutationRecords),
      renderProbeBegins: profiler.begins,
      renderProbeEnds: profiler.ends,
      nestedCalls: { ...nestedCalls },
      medianSynchronousMs: median(durations),
      maximumSynchronousMs: Math.max(...durations),
    });
    mutationRecords.length = 0;
  }
  observer.disconnect();
  counters.restore();
  dom.window.close();
  const report = {
    schemaVersion: 1,
    issue: 255,
    parentIssue: 247,
    measurementOnly: true,
    source: { version, sha256: sourceHash, bytes: Buffer.byteLength(source), lines: source.split(/\r?\n/u).length - (source.endsWith("\n") ? 1 : 0) },
    instrumentation: {
      generator: "tools/build-render-probe-userscript.mjs",
      instrumentedFunctions: instrumented.targets,
      productionSourceModified: false,
    },
    scenarios: results,
    summary: {
      selectorReads: results.reduce((sum, item) => sum + item.selectorReads, 0),
      writeAttempts: results.reduce((sum, item) => sum + item.writeAttempts, 0),
      changedWriteAttempts: results.reduce((sum, item) => sum + item.changedWriteAttempts, 0),
      redundantWriteAttempts: results.reduce((sum, item) => sum + item.redundantWriteAttempts, 0),
      mutationRecords: results.reduce((sum, item) => sum + item.mutations.records, 0),
      sameValueAttributeRecords: results.reduce((sum, item) => sum + item.mutations.sameValueAttributes, 0),
    },
    decisionBoundary: "The fixture proves repeated unchanged updateUI shell work only. Production suppression requires an isolated helper, before/after evidence, lifecycle invalidation fixtures and an independently revertible release.",
  };
  return validateReport(report);
}

function markdown(report) {
  const rows = report.scenarios.map(item => `| ${item.name} | ${item.repeats} | ${item.selectorReads} | ${item.writeAttempts} | ${item.redundantWriteAttempts} | ${item.mutations.records} | ${item.mutations.sameValueAttributes} | ${item.medianSynchronousMs.toFixed(3)} ms |`);
  return [
    "# Issue #255 — v8.3.1 unchanged `updateUI()` baseline",
    "",
    "> Disposable render-probe and jsdom evidence. Nested renderers and root-attribute reconciliation are deliberately stubbed so the figures isolate the direct `updateUI()` shell.",
    "",
    `- Toolkit: \`${report.source.version}\``,
    `- Source SHA-256: \`${report.source.sha256}\``,
    `- Production source modified: \`${report.instrumentation.productionSourceModified}\``,
    `- Total selector reads: ${report.summary.selectorReads}`,
    `- Total write attempts: ${report.summary.writeAttempts}`,
    `- Proven unchanged write attempts: ${report.summary.redundantWriteAttempts}`,
    `- Actual mutation records: ${report.summary.mutationRecords}`,
    `- Same-value attribute mutation records: ${report.summary.sameValueAttributeRecords}`,
    "",
    "| Scenario | Repeats | Selector reads | Write attempts | Unchanged attempts | Mutation records | Same-value attributes | Median synchronous time |",
    "|---|---:|---:|---:|---:|---:|---:|---:|",
    ...rows,
    "",
    "## Decision boundary",
    "",
    report.decisionBoundary,
    "",
  ].join("\n");
}

function args(argv) {
  const output = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) throw new Error(`Unexpected argument: ${key}`);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${key}`);
    output[key.slice(2)] = value;
    index += 1;
  }
  return output;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const options = args(process.argv.slice(2));
  const report = await measureUnchangedUpdateUi();
  if (options["json-output"]) {
    fs.mkdirSync(path.dirname(path.resolve(options["json-output"])), { recursive: true });
    fs.writeFileSync(path.resolve(options["json-output"]), `${JSON.stringify(report, null, 2)}\n`);
  }
  if (options["markdown-output"]) {
    fs.mkdirSync(path.dirname(path.resolve(options["markdown-output"])), { recursive: true });
    fs.writeFileSync(path.resolve(options["markdown-output"]), `${markdown(report)}\n`);
  }
  console.log(`Issue #255 unchanged updateUI measurement passed: ${report.summary.redundantWriteAttempts} unchanged write attempts and ${report.summary.mutationRecords} mutation records.`);
}
