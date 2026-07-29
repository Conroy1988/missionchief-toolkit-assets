#!/usr/bin/env python3
"""Issue #255 / parent #247: suppress proven same-value updateUI writes in Toolkit v8.3.2."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
EXPECTED_SOURCE_SHA = "363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089"
BASELINE_PATH = ROOT / "docs/audits/issue-255/unchanged-update-ui.json"
OPTIMISED_DIR = ROOT / "docs/audits/issue-255"


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


def replace_count(text: str, old: str, new: str, expected: int, label: str) -> str:
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{label}: expected {expected} matches, found {count}")
    return text.replace(old, new)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(args: list[str], env: dict[str, str] | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, env=env, check=True)


source = read(SOURCE_PATH)
if sha256_text(source) != EXPECTED_SOURCE_SHA:
    raise RuntimeError("exact v8.3.1 source authority moved")
source = replace_once(source, "// @version      8.3.1", "// @version      8.3.2", "metadata version")
source = replace_once(source, "version: '8.3.1'", "version: '8.3.2'", "runtime version")

helpers = r'''    function updateUiToggleClass(element, className, enabled) {
        if (!element?.classList) return false;
        const next = Boolean(enabled);
        if (element.classList.contains(className) === next) return false;
        element.classList.toggle(className, next);
        return true;
    }

    function updateUiSetStyleProperty(style, name, value, priority = '') {
        if (!style || typeof style.getPropertyValue !== 'function' || typeof style.setProperty !== 'function') return false;
        const nextValue = String(value);
        const nextPriority = String(priority || '');
        if (style.getPropertyValue(name) === nextValue && style.getPropertyPriority(name) === nextPriority) return false;
        style.setProperty(name, nextValue, nextPriority);
        return true;
    }

    function updateUiSetAttribute(element, name, value) {
        if (!element || typeof element.getAttribute !== 'function' || typeof element.setAttribute !== 'function') return false;
        const next = String(value);
        if (element.getAttribute(name) === next) return false;
        element.setAttribute(name, next);
        return true;
    }

    function updateUiSetDataset(element, key, value) {
        if (!element?.dataset) return false;
        const next = String(value);
        if (element.dataset[key] === next) return false;
        element.dataset[key] = next;
        return true;
    }

    function updateUiSetProperty(element, property, value) {
        if (!element) return false;
        if (Object.is(element[property], value)) return false;
        element[property] = value;
        return true;
    }

    function updateUiSetText(element, value) {
        return updateUiSetProperty(element, 'textContent', String(value));
    }

'''
source = replace_once(source, "    function updateUI() {\n", helpers + "    function updateUI() {\n", "updateUI helper insertion")

start = source.index("    function updateUI() {")
end = source.index("    function ensureUi() {", start)
block = source[start:end]
block = replace_once(block, "            for (const pos of Object.keys(POSITIONS)) control.classList.toggle(`mcms-pos-${pos}`, state.position === pos);", "            for (const pos of Object.keys(POSITIONS)) updateUiToggleClass(control, `mcms-pos-${pos}`, state.position === pos);", "position class writes")
block = replace_once(block, "            control.style.setProperty('--mcms-nudge-x', `${state.nudge.x}px`);", "            updateUiSetStyleProperty(control.style, '--mcms-nudge-x', `${state.nudge.x}px`);", "nudge x write")
block = replace_once(block, "            control.style.setProperty('--mcms-nudge-y', `${state.nudge.y}px`);", "            updateUiSetStyleProperty(control.style, '--mcms-nudge-y', `${state.nudge.y}px`);", "nudge y write")
block = replace_count(block, "                btn.classList.toggle('mcms-on', on);", "                updateUiToggleClass(btn, 'mcms-on', on);", 2, "toggle button class writes")
block = replace_once(block, "                btn.setAttribute('aria-pressed', String(on));", "                updateUiSetAttribute(btn, 'aria-pressed', String(on));", "control aria pressed")
block = replace_once(block, "                btn.dataset.mcmsState = on ? 'on' : 'off';", "                updateUiSetDataset(btn, 'mcmsState', on ? 'on' : 'off');", "control dataset state")
block = replace_once(block, "                vehicleStatusButton.classList.toggle('mcms-on', open);", "                updateUiToggleClass(vehicleStatusButton, 'mcms-on', open);", "vehicle status class")
block = replace_once(block, "                vehicleStatusButton.setAttribute('aria-pressed', String(open));", "                updateUiSetAttribute(vehicleStatusButton, 'aria-pressed', String(open));", "vehicle status aria")
block = replace_once(block, "                vehicleStatusButton.dataset.mcmsState = open ? 'on' : 'off';", "                updateUiSetDataset(vehicleStatusButton, 'mcmsState', open ? 'on' : 'off');", "vehicle status dataset")
block = replace_once(block, "                economyButton.classList.toggle('mcms-on', on);", "                updateUiToggleClass(economyButton, 'mcms-on', on);", "economy class")
block = replace_once(block, "                economyButton.setAttribute('aria-pressed', String(on));", "                updateUiSetAttribute(economyButton, 'aria-pressed', String(on));", "economy aria pressed")
block = replace_once(block, "                economyButton.setAttribute('aria-label', label);", "                updateUiSetAttribute(economyButton, 'aria-label', label);", "economy aria label")
block = replace_once(block, "                economyButton.title = label;", "                updateUiSetProperty(economyButton, 'title', label);", "economy title")
block = replace_once(block, "                economyButton.dataset.mcmsState = on ? 'on' : 'off';", "                updateUiSetDataset(economyButton, 'mcmsState', on ? 'on' : 'off');", "economy dataset")
block = replace_once(block, "                dockToggleButton.classList.toggle('mcms-open', open);", "                updateUiToggleClass(dockToggleButton, 'mcms-open', open);", "dock class")
block = replace_once(block, "                dockToggleButton.setAttribute('aria-expanded', String(open));", "                updateUiSetAttribute(dockToggleButton, 'aria-expanded', String(open));", "dock aria expanded")
block = replace_once(block, "                dockToggleButton.setAttribute('aria-label', label);", "                updateUiSetAttribute(dockToggleButton, 'aria-label', label);", "dock aria label")
block = replace_once(block, "                dockToggleButton.title = label;", "                updateUiSetProperty(dockToggleButton, 'title', label);", "dock title")
block = replace_once(block, "                if (icon) icon.textContent = open ? '▴' : '▾';", "                updateUiSetText(icon, open ? '▴' : '▾');", "dock icon text")
block = replace_count(block, "            btn.classList.toggle('mcms-active', active);", "            updateUiToggleClass(btn, 'mcms-active', active);", 2, "active button classes")
block = replace_once(block, "            btn.setAttribute('aria-selected', String(active));", "            updateUiSetAttribute(btn, 'aria-selected', String(active));", "tab aria selected")
block = replace_once(block, "            btn.tabIndex = active ? 0 : -1;", "            updateUiSetProperty(btn, 'tabIndex', active ? 0 : -1);", "tab index")
block = replace_once(block, "            tabPanel.classList.toggle('mcms-active', active);", "            updateUiToggleClass(tabPanel, 'mcms-active', active);", "panel active class")
block = replace_once(block, "            tabPanel.hidden = !active;", "            updateUiSetProperty(tabPanel, 'hidden', !active);", "panel hidden")
block = replace_once(block, "        panel.setAttribute('aria-hidden', String(!panelOpen));", "        updateUiSetAttribute(panel, 'aria-hidden', String(!panelOpen));", "panel aria hidden")
block = replace_once(block, "        control?.querySelector('.mcms-menu-btn')?.setAttribute('aria-expanded', String(panelOpen));", "        updateUiSetAttribute(control?.querySelector('.mcms-menu-btn'), 'aria-expanded', String(panelOpen));", "menu aria expanded")
block = replace_once(block, "            btn.setAttribute('aria-pressed', String(active));", "            updateUiSetAttribute(btn, 'aria-pressed', String(active));", "theme aria pressed")
block = replace_once(block, "        panel.querySelectorAll('.mcms-theme-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.theme === state.theme));", "        panel.querySelectorAll('.mcms-theme-btn').forEach(btn => updateUiToggleClass(btn, 'mcms-active', btn.dataset.theme === state.theme));", "theme class writes")
block = replace_once(block, "        panel.querySelectorAll('.mcms-position-btn').forEach(btn => btn.classList.toggle('mcms-active', btn.dataset.position === state.position));", "        panel.querySelectorAll('.mcms-position-btn').forEach(btn => updateUiToggleClass(btn, 'mcms-active', btn.dataset.position === state.position));", "position class writes")
block = replace_once(block, "            if (pill) pill.textContent = key === 'coverage' ? (on ? `${state.coverage.radiusMi}mi` : 'OFF') : (on ? 'ON' : 'OFF');", "            updateUiSetText(pill, key === 'coverage' ? (on ? `${state.coverage.radiusMi}mi` : 'OFF') : (on ? 'ON' : 'OFF'));", "pill text")
value_pattern = re.compile(r"if \(([^)\n]+)\) ([A-Za-z_$][\w$]*)\.value = ([^;\n]+);")
block, value_count = value_pattern.subn(lambda match: f"if ({match.group(1)}) updateUiSetProperty({match.group(2)}, 'value', {match.group(3)});", block)
if value_count < 25:
    raise RuntimeError(f"input value writes: expected at least 25 matches, found {value_count}")
block = replace_once(block, "        if (economyStatus) economyStatus.textContent = state.economyMode\n            ? 'Economy Mode is ON: static visual effects, adaptive refresh intervals and off-screen vehicle/building layer culling are active.'\n            : 'Economy Mode is OFF. Use the leaf button beside the map-menu opener to reduce CPU, GPU and marker workload.';", "        updateUiSetText(economyStatus, state.economyMode\n            ? 'Economy Mode is ON: static visual effects, adaptive refresh intervals and off-screen vehicle/building layer culling are active.'\n            : 'Economy Mode is OFF. Use the leaf button beside the map-menu opener to reduce CPU, GPU and marker workload.');", "economy status text")
block = replace_once(block, "        if (nudge) nudge.textContent = `X ${state.nudge.x} / Y ${state.nudge.y}`;", "        updateUiSetText(nudge, `X ${state.nudge.x} / Y ${state.nudge.y}`);", "nudge text")
for pattern, label in [
    (r"\.classList\.toggle\(", "class toggle"),
    (r"\.style\.setProperty\(", "style write"),
    (r"\.setAttribute\(", "attribute write"),
    (r"\.textContent\s*=", "text write"),
    (r"\.title\s*=", "title write"),
    (r"\.tabIndex\s*=", "tab index write"),
    (r"\.hidden\s*=", "hidden write"),
    (r"\.value\s*=", "value write"),
    (r"\.dataset\.[A-Za-z_$][\w$]*\s*=", "dataset write"),
]:
    if re.search(pattern, block):
        raise RuntimeError(f"direct {label} remains in updateUI")
source = source[:start] + block + source[end:]
write(SOURCE_PATH, source)
new_source_sha = sha256_text(source)
new_source_bytes = len(source.encode("utf-8"))
new_source_lines = len(source.splitlines())

runtime_script = r'''#!/usr/bin/env node
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
const EXPECTED_VERSION = "8.3.2";
const EXPECTED_SHA = "__EXPECTED_SHA__";
const REPEATS = 25;
const HELPER_NAMES = ["updateUiToggleClass", "updateUiSetStyleProperty", "updateUiSetAttribute", "updateUiSetDataset", "updateUiSetProperty", "updateUiSetText"];

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
  const controlToggles = ["allianceMissions", "myMissions", "vehicles", "buildings", "allianceCredits", "missionAge", "transportWatcher", "unitCommitment"];
  const panelToggles = ["clean", "markerFocus", "missionPulse", "roadPriority", "coverage", "shortcuts", "autoLoadAllVehicles", "allianceBuildingsMapBlocker", "majorIncidentFeed", "missionLockAudio", "payoutFlash", "payoutSound", "missionValue", "customVehicleBadges", "stuckDetector", "missionSpawn", "resourceGap", "allianceMissions", "myMissions", "vehicles", "buildings", "allianceCredits", "missionAge", "transportWatcher", "unitCommitment"];
  const settings = ["major-incident-minimum", "coverage-radius", "alliance-credit-minimum", "transport-sweep-delay", "transport-sweep-max", "payout-template", "resource-gap-radius", "stuck-threshold", "payout-threshold", "payout-duration", "payout-volume", "discord-webhook", "discord-name", "discord-top-categories", "discord-period", "discord-custom-start", "discord-custom-end", "discord-comparison", "discord-chart", "discord-report-mode", "discord-risk", "discord-forecast", "finance-vault-enabled", "finance-vault-retention", "finance-rule-feed"];
  return `<!doctype html><html><body>
    <div id="mc-map-command-toolkit-control">
      ${controlToggles.map(key => `<button data-toggle="${key}"></button>`).join("")}
      <button data-action="open-vehicle-status"></button><button class="mcms-economy-btn"></button>
      <button class="mcms-dock-toggle-btn"><span class="mcms-dock-toggle-icon"></span></button><button class="mcms-menu-btn"></button>
    </div>
    <div id="mc-map-command-toolkit-panel">
      ${["map", "settings", "resources", "ops", "discord"].map(key => `<button class="mcms-tab-btn" data-tab="${key}"></button><section class="mcms-tab-panel" data-panel="${key}"></section>`).join("")}
      <button class="mcms-ui-theme-btn" data-ui-theme="mapCommand"></button><button class="mcms-ui-theme-btn" data-ui-theme="cyberpunk"></button>
      <button class="mcms-theme-btn" data-theme="classic"></button><button class="mcms-theme-btn" data-theme="dark"></button>
      <button class="mcms-position-btn" data-position="bottomRight"></button><button class="mcms-position-btn" data-position="topLeft"></button>
      ${panelToggles.map(key => `<button data-toggle="${key}"><span class="mcms-pill"></span></button>`).join("")}
      ${settings.map(key => `<input data-setting="${key}">`).join("")}
      <div class="mcms-economy-status"></div><div class="mcms-nudge-value"></div>
    </div>
    <div id="mc-map-command-toolkit-vehicle-status"></div>
  </body></html>`;
}

function baseState() {
  return {
    majorIncidentFeed: { enabled: false, minimumCredits: 25000 }, position: "bottomRight", nudge: { x: 0, y: 0 }, commandBarOpen: true,
    visibility: { allianceMissions: true, myMissions: true, vehicles: true, buildings: true }, allianceCredits: true, missionAge: true,
    transportWatcher: true, unitCommitment: true, economyMode: false, activeTab: "map", uiTheme: "mapCommand", theme: "classic",
    cleanMode: false, markerFocus: false, missionPulse: true, roadPriority: false, coverage: { enabled: true, radiusMi: 10 }, shortcuts: true,
    autoLoadAllVehicles: true, allianceBuildingsMap: true, missionLockAudio: true,
    payoutFlash: { enabled: true, soundEnabled: true, template: "command", threshold: 10000, durationMs: 5000, soundVolume: 0.35 },
    missionValue: true, customVehicleBadges: true, stuckDetector: { enabled: true, thresholdMin: 10 }, missionSpawn: { enabled: true },
    resourceGap: { enabled: true, radiusMi: 20 }, allianceCreditMinimum: 10000, transportSweep: { delayMs: 900, maxPerRun: 25 },
    discordReport: { webhookName: "Toolkit", topCategories: 5, period: "daily", customStart: "", customEnd: "", includeComparison: true, includeChart: true, reportMode: "summary", includeRisk: true, includeForecast: true },
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
    SCRIPT: { controlId: "mc-map-command-toolkit-control", panelId: "mc-map-command-toolkit-panel", vehicleStatusId: "mc-map-command-toolkit-vehicle-status" }, POSITIONS: { topLeft: {}, topRight: {}, bottomLeft: {}, bottomRight: {} },
    applyRootAttributes: () => countNested("applyRootAttributes"), scheduleMajorIncidentFeedRender: () => countNested("scheduleMajorIncidentFeedRender"), removeMajorIncidentFeed: () => countNested("removeMajorIncidentFeed"), toolkitApplyCommandBarState: () => countNested("toolkitApplyCommandBarState"), refreshTabletModeUi: () => countNested("refreshTabletModeUi"), updateAllianceMemberManagerMenuControl: () => countNested("updateAllianceMemberManagerMenuControl"), renderTransportSweepPanel: () => countNested("renderTransportSweepPanel"), getDiscordWebhookUrl: () => "https://discord.invalid/webhook", setDiscordStatus: () => countNested("setDiscordStatus"), discordFinanceStatus: "ready", discordFinanceStatusTone: "success", renderFinanceVaultStatus: () => countNested("renderFinanceVaultStatus"), renderProfiles: () => countNested("renderProfiles"), operationalVisible: false, operationalUiIsVisible: () => sandbox.operationalVisible, renderOperationalPanels: () => countNested("renderOperationalPanels"), __MCMS_PROFILER__: profiler };
  sandbox.globalThis = sandbox; vm.createContext(sandbox); vm.runInContext(`${functionSources.join("\n")}\nthis.__api={updateUI};`, sandbox, { filename: "update-ui-write-suppression-v8.3.2.js" });
  const panel = window.document.getElementById(sandbox.SCRIPT.panelId);
  async function resetEvidence() { await flush(window); mutationRecords.length = 0; observer.takeRecords(); counters.reset(); profiler.begins = 0; profiler.ends = 0; for (const key of Object.keys(nestedCalls)) delete nestedCalls[key]; }
  async function capture(call) { const started = performance.now(); call(); const elapsed = performance.now() - started; await flush(window); mutationRecords.push(...observer.takeRecords()); return { counters: counters.snapshot(), mutations: summariseMutations(mutationRecords), elapsed }; }
  const scenarios = [
    { name: "idle-panel-closed", open: false, tab: "map", operational: false }, { name: "settings-open", open: true, tab: "settings", operational: false },
    { name: "resources-open", open: true, tab: "resources", operational: false }, { name: "operations-open", open: true, tab: "ops", operational: true },
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
  state.activeTab = "resources"; state.economyMode = true; state.nudge = { x: 3, y: -2 };
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

function markdown(report) { return ["# Issue #255 — v8.3.2 `updateUI()` same-value write suppression", "", `- Before unchanged write attempts: ${report.before.writeAttempts.toLocaleString("en-GB")}`, `- After unchanged write attempts: ${report.after.writeAttempts}`, `- Before mutation records: ${report.before.mutationRecords.toLocaleString("en-GB")}`, `- After mutation records: ${report.after.mutationRecords}`, `- State transition changed writes: ${report.stateTransition.changed.counters.changedWriteAttempts}`, `- State transition mutation records: ${report.stateTransition.changed.mutations.records}`, `- Framework replacement changed writes: ${report.frameworkReplacement.changed.counters.changedWriteAttempts}`, `- Framework replacement mutation records: ${report.frameworkReplacement.changed.mutations.records}`, "", "The first changed-state and replacement-DOM passes still apply state. Their immediate stable repeats produce zero writes and zero mutation records.", "", `> ${report.interpretationBoundary}`, ""].join("\n"); }

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) { const options = parseArgs(process.argv.slice(2)); const report = await measureWriteSuppression(); if (options["json-output"]) { fs.mkdirSync(path.dirname(path.resolve(options["json-output"])), { recursive: true }); fs.writeFileSync(path.resolve(options["json-output"]), `${JSON.stringify(report, null, 2)}\n`); } if (options["markdown-output"]) { fs.mkdirSync(path.dirname(path.resolve(options["markdown-output"])), { recursive: true }); fs.writeFileSync(path.resolve(options["markdown-output"]), `${markdown(report)}\n`); } console.log(`Issue #255 v8.3.2 write suppression passed: ${report.before.writeAttempts} → ${report.after.writeAttempts} unchanged writes; ${report.before.mutationRecords} → ${report.after.mutationRecords} mutations.`); }
'''.replace("__EXPECTED_SHA__", new_source_sha)
write(".github/scripts/test_issue255_update_ui_write_suppression_runtime.mjs", runtime_script)

workflow_path = ROOT / ".github/workflows/validate-userscript.yml"
workflow = read(workflow_path)
workflow = replace_once(workflow, "          node .github/scripts/measure_issue255_unchanged_update_ui.mjs 2>&1 | tee issue255-update-ui-measurement.log\n", "          node .github/scripts/test_issue255_update_ui_write_suppression_runtime.mjs 2>&1 | tee issue255-update-ui-measurement.log\n", "runtime measurement command")
write(workflow_path, workflow)

preflight_path = ROOT / ".github/scripts/run_userscript_preflight.sh"
preflight = read(preflight_path)
preflight = replace_once(preflight, "python3 .github/scripts/test_issue255_unchanged_update_ui.py\n", "python3 .github/scripts/test_issue255_unchanged_update_ui.py\npython3 .github/scripts/test_issue255_update_ui_write_suppression.py\n", "static contract insertion")
preflight = replace_once(preflight, "node .github/scripts/test_issue564_incident_feed_attended_runtime.js\n", "node .github/scripts/test_issue564_incident_feed_attended_runtime.js\nnode .github/scripts/test_issue255_update_ui_write_suppression_runtime.mjs\n", "runtime contract insertion")
write(preflight_path, preflight)

node_modules = ROOT / "node_modules"
package_lock = ROOT / "package-lock.json"
try:
    run(["npm", "install", "--no-save", "--package-lock=false", "--ignore-scripts", "--no-audit", "--no-fund", "jsdom@26.1.0", "acorn@8.15.0"])
    run(["node", "--check", ".github/scripts/test_issue255_update_ui_write_suppression_runtime.mjs"])
    run(["node", ".github/scripts/test_issue255_update_ui_write_suppression_runtime.mjs", "--json-output", str(OPTIMISED_DIR / "write-suppression-v832.json"), "--markdown-output", str(OPTIMISED_DIR / "write-suppression-v832.md")])
finally:
    if node_modules.exists(): shutil.rmtree(node_modules)
    if package_lock.exists(): package_lock.unlink()

report = json.loads((OPTIMISED_DIR / "write-suppression-v832.json").read_text(encoding="utf-8"))
manifest_path = OPTIMISED_DIR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({
    "optimisedToolkitVersion": "8.3.2",
    "optimisedSourceSha256": new_source_sha,
    "optimisedEvidence": "write-suppression-v832.json",
    "beforeUnchangedWriteAttempts": report["before"]["writeAttempts"],
    "afterUnchangedWriteAttempts": report["after"]["writeAttempts"],
    "beforeMutationRecords": report["before"]["mutationRecords"],
    "afterMutationRecords": report["after"]["mutationRecords"],
    "productionOptimisationAuthorised": True,
    "stateTransitionVerified": True,
    "frameworkReplacementVerified": True,
    "interpretationBoundary": report["interpretationBoundary"],
})
write(manifest_path, json.dumps(manifest, indent=2) + "\n")
readme_path = OPTIMISED_DIR / "README.md"
readme = read(readme_path)
if "## v8.3.2 write suppression" not in readme:
    readme += "\n## v8.3.2 write suppression\n\n" + read(OPTIMISED_DIR / "write-suppression-v832.md") + "\n"
write(readme_path, readme)

static_contract = f'''#!/usr/bin/env python3
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'src/MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
metadata=re.search(r'(?m)^//\\s*@version\\s+([^\\s]+)$',source);runtime=re.search(r"version:\\s*'([^']+)'",source)
assert metadata and runtime and metadata.group(1)==runtime.group(1)=='8.3.2'
for name in ['updateUiToggleClass','updateUiSetStyleProperty','updateUiSetAttribute','updateUiSetDataset','updateUiSetProperty','updateUiSetText']:
    assert source.count(f'function {{name}}(')==1,name
start=source.index('    function updateUI() {{');end=source.index('    function ensureUi() {{',start);block=source[start:end]
for pattern in [r'\\.classList\\.toggle\\(',r'\\.style\\.setProperty\\(',r'\\.setAttribute\\(',r'\\.textContent\\s*=',r'\\.title\\s*=',r'\\.tabIndex\\s*=',r'\\.hidden\\s*=',r'\\.value\\s*=',r'\\.dataset\\.[A-Za-z_$][\\w$]*\\s*=']:
    assert not re.search(pattern,block),pattern
report=json.loads((ROOT/'docs/audits/issue-255/write-suppression-v832.json').read_text(encoding='utf-8'))
assert report['sourceSha256']=='{new_source_sha}'
assert report['before']['writeAttempts']==14500 and report['after']['writeAttempts']==0
assert report['before']['mutationRecords']==7100 and report['after']['mutationRecords']==0
assert report['stateTransition']['changed']['counters']['changedWriteAttempts']>0
assert report['stateTransition']['changed']['mutations']['records']>0
assert report['stateTransition']['stableRepeat']['counters']['writeAttempts']==0
assert report['stateTransition']['stableRepeat']['mutations']['records']==0
assert report['frameworkReplacement']['changed']['counters']['changedWriteAttempts']>0
assert report['frameworkReplacement']['changed']['mutations']['records']>0
assert report['frameworkReplacement']['stableRepeat']['counters']['writeAttempts']==0
assert report['frameworkReplacement']['stableRepeat']['mutations']['records']==0
print('Issue #255 v8.3.2 updateUI same-value write suppression contract passed.')
'''
write(".github/scripts/test_issue255_update_ui_write_suppression.py", static_contract)

changelog = read("CHANGELOG.md")
entry = """## [8.3.2] - 2026-07-29

### Proven unchanged-state UI write suppression

- Adds live-value guards to the central `updateUI()` control synchronisation path so identical classes, attributes, styles, text, input values, visibility and tab state are not written again.
- Preserves fresh DOM discovery on every update; no MissionChief element is cached across framework replacement.
- The exact rendered fixture reduces 100 warmed unchanged calls from 14,500 write attempts and 7,100 mutation records to zero.
- First state transitions and complete command-bar/panel replacement still apply the full current state; their immediate stable repeats return to zero writes and zero mutations.
- Adds no request, observer, interval, listener, scheduler or Toolkit-managed timer.
- Synchronous jsdom timings remain diagnostic only; this release does not claim a live browser frame-rate increase without authenticated browser traces.

"""
if "## [8.3.2] - 2026-07-29" not in changelog:
    changelog = replace_once(changelog, "# Changelog\n\n", "# Changelog\n\n" + entry, "changelog insertion")
write("CHANGELOG.md", changelog)

write("docs/issue-255-update-ui-write-suppression.md", f"""# Issue #255 — `updateUI()` same-value write suppression

Toolkit v8.3.2 applies a narrowly scoped optimisation to the central UI state synchroniser.

## Evidence

The exact v8.3.1 rendered baseline measured 100 warmed unchanged calls at 14,500 attempted writes and 7,100 mutation records. The v8.3.2 fixture records zero writes and zero mutations for the same four scenarios.

## Safety boundary

- Every call still queries the current MissionChief control and panel nodes.
- No element reference is cached across framework replacement.
- First render, state transitions and complete control/panel replacement remain covered and apply state correctly.
- Nested operational renderers, scheduling, observers, requests and teardown semantics are unchanged.
- The evidence proves eliminated rendered-fixture writes and mutation records; it is not a live frame-rate claim.

Source evidence: `docs/audits/issue-255/write-suppression-v832.json`.
Source SHA-256: `{new_source_sha}`.
""")

help_manifest = json.loads(read("help/manifest.json"))
help_manifest.update({"guideVersion": "8.3.2", "toolkitVersion": "8.3.2", "updated": "2026-07-29", "sections": max(22, int(help_manifest.get("sections", 21)) + 1), "runtimeGuidePatch": "Toolkit v8.3.2 suppresses proven same-value updateUI writes while preserving live DOM discovery, state transitions and framework replacement recovery."})
write("help/manifest.json", json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n")
help_index = read("help/index.html").replace("v8.3.1", "v8.3.2")
help_index, notice_count = re.subn(r'<section class="notice">.*?</section>', '<section class="notice"><h2>What changes in v8.3.2</h2><p>The central Toolkit UI synchroniser now checks the live element value before writing. Repeated unchanged updates no longer create redundant classes, attributes, text replacements or input assignments, while first render and MissionChief framework replacement remain fully supported.</p></section>', help_index, count=1, flags=re.S)
if notice_count != 1: raise RuntimeError(f"help notice matches: {notice_count}
")
section = '<section id="update-ui-write-suppression"><h2>Same-value UI write suppression</h2><p>Toolkit v8.3.2 continues to locate the current live command bar and settings panel on every update, but writes a class, attribute, style, text value or form value only when it differs. This avoids repeated DOM mutation traffic without caching stale MissionChief elements.</p></section>'
if 'id="update-ui-write-suppression"' not in help_index:
    help_index = help_index.replace("</main>", section + "\n</main>")
help_index = re.sub(r'<footer>.*?</footer>', '<footer>MissionChief Map Command Toolkit · v8.3.2 · The One We Knew Before</footer>', help_index, count=1, flags=re.S)
write("help/index.html", help_index)

site_data = json.loads(read("docs/site-data.json"))
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Economy Mode":
            feature["summary"] = "Suppresses non-essential effects and avoids repeated same-state UI writes while retaining live MissionChief lifecycle recovery."
            details = list(feature.get("details", []))
            if "Same-value UI write suppression" not in details: details.append("Same-value UI write suppression")
            feature["details"] = details
write("docs/site-data.json", json.dumps(site_data, indent=2, ensure_ascii=False) + "\n")

budget = json.loads(read(".github/performance-budget.json"))
budget["revision"] = "2026-07-29-issue-255-update-ui-write-suppression"
budget["rationale"] = "Suppress only proven same-value writes in updateUI while preserving live element discovery and framework replacement recovery."
transition = {"issue": 255, "version": "8.3.2", "approvedNetworkRequestDelta": 0, "scope": "Live-value guards for central updateUI classes, attributes, styles, text and form properties with state-transition and DOM-replacement proof.", "approvedMutationObserverDelta": 0}
budget["transitionApproval"] = transition
if not any(item.get("version") == "8.3.2" for item in budget.setdefault("approvalHistory", [])):
    budget["approvalHistory"].append(dict(transition))
write(".github/performance-budget.json", json.dumps(budget, indent=2) + "\n")

headroom = json.loads(read(".github/fixtures/main-style-source-headroom.json"))
text = read(SOURCE_PATH)
a = text.index("function installMainStyles()")
b = text.index("addStyle(`", a) + len("addStyle(`")
m = text.index("recordStartupMetric('stylesheetInstallMs'", b)
z = text.rfind("`);", b, m)
css = text[b:z]
lines = css.split("\n")
canonical = re.sub(r"\n[\t ]*}", "}", "\n".join(line for index, line in enumerate(lines) if not (0 < index < len(lines) - 1 and not line.strip())))
v8 = headroom["v8Candidate"]
previous_bytes = int(v8["sourceBytes"]); previous_lines = int(v8["sourceLines"])
previous_growth_bytes = int(v8["approvedGrowth"]["sourceBytes"]); previous_growth_lines = int(v8["approvedGrowth"]["sourceLines"])
v8.update({"issue": 255, "version": "8.3.2", "sourceBytes": new_source_bytes, "sourceLines": new_source_lines, "sourceSha256": new_source_sha, "templateBytes": len(css.encode("utf-8")), "templateLines": len(lines), "templateSha256": hashlib.sha256(css.encode("utf-8")).hexdigest(), "canonicalCssSha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(), "maxSourceBytes": new_source_bytes + 20000, "maxSourceLines": new_source_lines + 250, "baseline": "8.3.1", "scope": "Issue #255 same-value updateUI write suppression with rendered state-transition and framework-replacement proof"})
v8["approvedGrowth"] = {"sourceBytes": previous_growth_bytes + new_source_bytes - previous_bytes, "sourceLines": previous_growth_lines + new_source_lines - previous_lines, "templateBytes": 0, "templateLines": 0}
write(".github/fixtures/main-style-source-headroom.json", json.dumps(headroom, indent=2) + "\n")

print(json.dumps({"version": "8.3.2", "sourceSha256": new_source_sha, "sourceBytes": new_source_bytes, "sourceLines": new_source_lines, "beforeWrites": report["before"]["writeAttempts"], "afterWrites": report["after"]["writeAttempts"], "beforeMutations": report["before"]["mutationRecords"], "afterMutations": report["after"]["mutationRecords"]}, indent=2))
