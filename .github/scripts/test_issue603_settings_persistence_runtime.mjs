#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
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
    if (char === "'" || char === '"' || char === "`") {
      quote = char;
      continue;
    }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const persistenceFunctions = [
  "looksLikeToolkitState",
  "settingsLocalStorageGet",
  "settingsLocalStorageSet",
  "settingsLocalStorageRemove",
  "parseSettingsPersistenceCandidate",
  "settingsPersistenceCandidates",
  "persistSettingsState",
  "loadState",
  "saveState",
].map(extractFunction).join("\n");

const stateLoadIndex = source.indexOf("    state = loadState();");
assert.ok(stateLoadIndex > source.indexOf("    const COMMAND_SECTION_ORDER"), "saved settings load before command-section constants initialise");
assert.ok(stateLoadIndex > source.indexOf("    const LEGACY_COMMAND_SECTION_MAP"), "saved legacy tabs load before their migration map initialises");

const SCRIPT = Object.freeze({
  version: "9.1.1-test",
  storageState: "mc_map_command_toolkit_state_v150",
  settingsVaultState: "mc_map_command_toolkit_settings_v1",
  settingsRecoveryState: "mc_map_command_toolkit_settings_recovery_v1",
  oldStorageKeys: [
    "mc_map_command_toolkit_state_v149",
    "mc_map_command_toolkit_state_v148",
  ],
  legacyTheme: "mc_map_command_skins_theme_v2",
  legacyPosition: "mc_map_command_skins_position_v1",
});

const defaults = Object.freeze({
  uiTheme: "mapCommand",
  theme: "default",
  position: "bl",
  tabletMode: "auto",
  mobileMode: "auto",
  visibility: { allianceMissions: true, myMissions: true, vehicles: true, buildings: true },
  bookmarks: [null, null, null, null, null],
  profiles: [null, null, null],
  payoutFlash: { enabled: true, threshold: 10000 },
  stuckDetector: { enabled: true, thresholdMin: 20 },
});

const clone = value => JSON.parse(JSON.stringify(value));

function createRuntime({ pageStore = new Map(), gmStore = new Map(), pageWritable = true, gmWritable = true } = {}) {
  const localStorage = {
    getItem(key) {
      return pageStore.has(key) ? pageStore.get(key) : null;
    },
    setItem(key, value) {
      if (!pageWritable) throw new Error("page storage unavailable");
      pageStore.set(key, String(value));
    },
    removeItem(key) {
      if (!pageWritable) throw new Error("page storage unavailable");
      pageStore.delete(key);
    },
  };
  const sandbox = {
    console,
    SCRIPT,
    pageWindow: { localStorage },
    localStorage,
    Date,
    JSON,
    gmGetValueSafe(key, fallback) {
      return gmStore.has(key) ? gmStore.get(key) : fallback;
    },
    gmSetValueSafe(key, value) {
      if (!gmWritable) return false;
      gmStore.set(key, value);
      return true;
    },
    gmDeleteValueSafe(key) {
      if (!gmWritable) return false;
      gmStore.delete(key);
      return true;
    },
    captureSettingsSnapshot() { return false; },
    defaultState() {
      return clone(defaults);
    },
    normaliseLoadedState(parsed, base) {
      return {
        ...clone(base),
        ...clone(parsed),
        visibility: { ...base.visibility, ...(parsed.visibility || {}) },
        stuckDetector: { ...base.stuckDetector, ...(parsed.stuckDetector || {}) },
        payoutFlash: { ...base.payoutFlash, ...(parsed.payoutFlash || {}) },
      };
    },
  };
  vm.createContext(sandbox);
  vm.runInContext(`
let settingsPersistenceMeta = { revision: 0, savedAt: 0, source: "defaults" };
let state = null;
${persistenceFunctions}
this.__probe = {
  load() { state = loadState(); return JSON.parse(JSON.stringify(state)); },
  save(value, options = {}) { state = JSON.parse(JSON.stringify(value)); return saveState(options); },
  metadata() { return { ...settingsPersistenceMeta }; },
};
`, sandbox, { filename: "issue603-settings-persistence-runtime.js" });
  return { probe: sandbox.__probe, pageStore, gmStore };
}

const selectedSettings = {
  ...clone(defaults),
  uiTheme: "cyberpunk",
  theme: "incident",
  position: "tr",
  tabletMode: "on",
  mobileMode: "off",
  visibility: { allianceMissions: false, myMissions: true, vehicles: false, buildings: true },
  bookmarks: [{ name: "Edinburgh HQ", pinned: true }, null, null, null, null],
  profiles: [{ name: "Night Ops", theme: "nightshift" }, null, null],
  payoutFlash: { enabled: false, threshold: 75000 },
  stuckDetector: { enabled: false, thresholdMin: 45 },
  panelPosition: { left: 230, top: 96 },
};

const pageStore = new Map([[SCRIPT.storageState, JSON.stringify(selectedSettings)]]);
const gmStore = new Map();
const firstLoad = createRuntime({ pageStore, gmStore });
assert.deepEqual(firstLoad.probe.load(), selectedSettings, "existing page settings were not loaded");
assert.ok(gmStore.has(SCRIPT.settingsVaultState), "existing settings were not migrated into Tampermonkey storage");
assert.ok(firstLoad.probe.metadata().revision >= 1, "migration did not create a durable revision");

const changedSettings = {
  ...selectedSettings,
  uiTheme: "hyrule",
  visibility: { ...selectedSettings.visibility, vehicles: true },
  stuckDetector: { enabled: true, thresholdMin: 60 },
};
assert.equal(firstLoad.probe.save(changedSettings, { requireWrite: true }), true);

const refreshed = createRuntime({ pageStore, gmStore });
assert.deepEqual(refreshed.probe.load(), changedSettings, "ordinary page refresh lost saved settings");

const otherOriginPageStore = new Map();
const upgraded = createRuntime({ pageStore: otherOriginPageStore, gmStore });
assert.deepEqual(upgraded.probe.load(), changedSettings, "userscript update or hostname change lost durable settings");
assert.ok(otherOriginPageStore.has(SCRIPT.storageState), "durable settings did not repair the page compatibility copy");

const legacyPageStore = new Map([[SCRIPT.oldStorageKeys[0], JSON.stringify(selectedSettings)]]);
const legacyGmStore = new Map();
const legacy = createRuntime({ pageStore: legacyPageStore, gmStore: legacyGmStore });
assert.deepEqual(legacy.probe.load(), selectedSettings, "legacy settings were not migrated");
assert.ok(legacyGmStore.has(SCRIPT.settingsVaultState), "legacy migration did not create a durable copy");

const recoveryPageStore = new Map();
const recoveryGmStore = new Map(gmStore);
const lastGoodPrimary = recoveryGmStore.get(SCRIPT.settingsVaultState);
recoveryGmStore.set(SCRIPT.settingsRecoveryState, lastGoodPrimary);
recoveryGmStore.set(SCRIPT.settingsVaultState, "{corrupt");
const recovered = createRuntime({ pageStore: recoveryPageStore, gmStore: recoveryGmStore });
assert.deepEqual(recovered.probe.load(), changedSettings, "recovery copy was not used after primary corruption");
assert.doesNotThrow(
  () => JSON.parse(recoveryGmStore.get(SCRIPT.settingsVaultState)),
  "corrupt durable primary was not repaired",
);

const unavailable = createRuntime({
  pageStore: new Map(),
  gmStore: new Map(),
  pageWritable: false,
  gmWritable: false,
});
assert.throws(
  () => unavailable.probe.save(selectedSettings, { requireWrite: true }),
  /storage is unavailable/u,
  "explicit settings writes did not fail closed when both stores were unavailable",
);

console.log("Issue #603 settings persistence passed: refresh, upgrade/origin migration, legacy recovery, corruption recovery and unavailable-storage failure.");
