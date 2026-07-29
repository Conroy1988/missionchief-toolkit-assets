#!/usr/bin/env python3
"""Issue #255 / parent #247: measure unchanged v8.3.1 updateUI work without changing production."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DIST_JS = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
EXPECTED_SHA = "363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089"
AUDIT_DIR = ROOT / "docs/audits/issue-255"


def read(path: str | Path) -> str:
    target = path if isinstance(path, Path) else ROOT / path
    return target.read_text(encoding="utf-8")


def write(path: str | Path, text: str) -> None:
    target = path if isinstance(path, Path) else ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[str], env: dict[str, str] | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, env=env, check=True)


source_before = SOURCE.read_bytes()
dist_js_before = DIST_JS.read_bytes()
dist_txt_before = DIST_TXT.read_bytes()
if not (source_before == dist_js_before == dist_txt_before):
    raise RuntimeError("source/distribution parity was not exact before measurement")
for path in (SOURCE, DIST_JS, DIST_TXT):
    if sha256(path) != EXPECTED_SHA:
        raise RuntimeError(f"v8.3.1 production authority moved for {path.relative_to(ROOT)}")

measurement = r'''#!/usr/bin/env node
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
'''
write(".github/scripts/measure_issue255_unchanged_update_ui.mjs", measurement)

workflow_path = ROOT / ".github/workflows/validate-userscript.yml"
workflow = read(workflow_path)
workflow = replace_once(
    workflow,
    "          npm install --no-save --package-lock=false --ignore-scripts jsdom@26.1.0\n",
    "          npm install --no-save --package-lock=false --ignore-scripts jsdom@26.1.0 acorn@8.15.0\n",
    "runtime dependency installation",
)
workflow = replace_once(
    workflow,
    "          node .github/scripts/test_ui_mount_integration.mjs 2>&1 | tee ui-mount-integration.log\n",
    "          node .github/scripts/test_ui_mount_integration.mjs 2>&1 | tee ui-mount-integration.log\n          node .github/scripts/measure_issue255_unchanged_update_ui.mjs 2>&1 | tee issue255-update-ui-measurement.log\n",
    "render measurement execution",
)
workflow = replace_once(
    workflow,
    "          cat ui-mount-integration.log runtime-contracts.log > runtime-lane.log\n",
    "          cat ui-mount-integration.log issue255-update-ui-measurement.log runtime-contracts.log > runtime-lane.log\n",
    "runtime diagnostic aggregation",
)
write(workflow_path, workflow)

AUDIT_DIR.mkdir(parents=True, exist_ok=True)
for child in AUDIT_DIR.iterdir():
    if child.is_dir(): shutil.rmtree(child)
    else: child.unlink()
node_modules = ROOT / "node_modules"
package_lock = ROOT / "package-lock.json"
try:
    run(["npm", "install", "--no-save", "--package-lock=false", "--ignore-scripts", "--no-audit", "--no-fund", "jsdom@26.1.0", "acorn@8.15.0"])
    run(["node", "--check", ".github/scripts/measure_issue255_unchanged_update_ui.mjs"])
    run([
        "node", ".github/scripts/measure_issue255_unchanged_update_ui.mjs",
        "--json-output", str(AUDIT_DIR / "unchanged-update-ui.json"),
        "--markdown-output", str(AUDIT_DIR / "unchanged-update-ui.md"),
    ])
finally:
    if node_modules.exists(): shutil.rmtree(node_modules)
    if package_lock.exists(): package_lock.unlink()

if SOURCE.read_bytes() != source_before or DIST_JS.read_bytes() != dist_js_before or DIST_TXT.read_bytes() != dist_txt_before:
    raise RuntimeError("measurement package changed production source or distribution")
for path in (SOURCE, DIST_JS, DIST_TXT):
    if sha256(path) != EXPECTED_SHA:
        raise RuntimeError(f"production hash changed after measurement: {path.relative_to(ROOT)}")

report = json.loads((AUDIT_DIR / "unchanged-update-ui.json").read_text(encoding="utf-8"))
manifest = {
    "schemaVersion": 1,
    "issue": 255,
    "parentIssue": 247,
    "measurementOnly": True,
    "toolkitVersion": "8.3.1",
    "sourceSha256": EXPECTED_SHA,
    "sourceDistributionParity": True,
    "scenarios": [item["name"] for item in report["scenarios"]],
    "repeatsPerScenario": 25,
    "selectorReads": report["summary"]["selectorReads"],
    "writeAttempts": report["summary"]["writeAttempts"],
    "provenUnchangedWriteAttempts": report["summary"]["redundantWriteAttempts"],
    "actualMutationRecords": report["summary"]["mutationRecords"],
    "sameValueAttributeRecords": report["summary"]["sameValueAttributeRecords"],
    "productionOptimisationAuthorised": False,
    "nextGate": "Isolated before/after suppression helper with identical rendered state and lifecycle invalidation coverage.",
}
write(AUDIT_DIR / "manifest.json", json.dumps(manifest, indent=2) + "\n")
write(AUDIT_DIR / "README.md", read(AUDIT_DIR / "unchanged-update-ui.md") + "\n## Production status\n\nThis baseline changes no production source or distribution. It proves a candidate optimisation area but does not itself authorise a release.\n")

contract = r'''#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'docs/audits/issue-255/manifest.json').read_text(encoding='utf-8'))
report=json.loads((ROOT/'docs/audits/issue-255/unchanged-update-ui.json').read_text(encoding='utf-8'))
assert manifest['issue']==255 and manifest['parentIssue']==247
assert manifest['measurementOnly'] is True
assert manifest['toolkitVersion']=='8.3.1'
assert manifest['sourceSha256']=='363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089'
assert manifest['sourceDistributionParity'] is True
assert manifest['productionOptimisationAuthorised'] is False
assert manifest['scenarios']==['idle-panel-closed','settings-open','resources-open','operations-open']
assert report['instrumentation']['generator']=='tools/build-render-probe-userscript.mjs'
assert report['instrumentation']['productionSourceModified'] is False
assert report['summary']['changedWriteAttempts']==0
assert report['summary']['redundantWriteAttempts']>0
assert report['summary']['mutationRecords']>0
for scenario in report['scenarios']:
    assert scenario['repeats']==25
    assert scenario['renderProbeBegins']==25 and scenario['renderProbeEnds']==25
    assert scenario['selectorReads']>0 and scenario['writeAttempts']>0
    assert scenario['changedWriteAttempts']==0
source=(ROOT/'src/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
dist=(ROOT/'dist/MissionChief_Map_Command_Toolkit.user.js').read_bytes()
txt=(ROOT/'dist/MissionChief_Map_Command_Toolkit.txt').read_bytes()
assert source==dist==txt
print('Issue #255 v8.3.1 unchanged updateUI measurement contract passed.')
'''
write(".github/scripts/test_issue255_unchanged_update_ui.py", contract)
preflight_path = ROOT / ".github/scripts/run_userscript_preflight.sh"
preflight = read(preflight_path)
preflight = replace_once(
    preflight,
    "python3 .github/scripts/test_issue588_v831_performance_baseline.py\n",
    "python3 .github/scripts/test_issue588_v831_performance_baseline.py\npython3 .github/scripts/test_issue255_unchanged_update_ui.py\n",
    "Issue #255 retained evidence contract insertion",
)
write(preflight_path, preflight)
print(json.dumps(manifest, indent=2))
