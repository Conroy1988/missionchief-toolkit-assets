#!/usr/bin/env python3
"""Run fixture-backed contracts against the real settings and UI routing functions.

The contract extracts exact declarations from the canonical userscript. It does
not copy production logic or modify runtime code.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURES = ROOT / ".github" / "fixtures" / "settings-ui-contract.json"

FUNCTION_NAMES = [
    "defaultState",
    "loadState",
    "saveState",
    "getLegacyTheme",
    "getLegacyPosition",
    "normaliseUiTheme",
    "normaliseTheme",
    "clamp",
    "normalisePayoutFlashDuration",
    "looksLikeToolkitState",
    "extractImportedToolkitState",
    "extractImportedDiscordWebhook",
    "extractImportedFinancialVaultCredential",
    "extractImportedFinancialVaultStore",
    "describePrivateImport",
    "applyImportedToolkitSettings",
    "toggleFeature",
    "handleAction",
    "handleSettingChange",
]


def extract_function(source: str, masked: str, name: str) -> str:
    pattern = re.compile(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    match = matches[0]
    open_pos = masked.find("{", match.start())
    if open_pos < 0:
        raise AssertionError(f"Opening brace not found for {name}")
    close_pos = audit.matching_brace(masked, open_pos)
    if close_pos is None:
        raise AssertionError(f"Closing brace not found for {name}")
    return source[match.start():close_pos + 1]


def values(pattern: str, text: str) -> list[str]:
    return sorted(set(re.findall(pattern, text)))


def assert_static_routes(source: str, fixtures: dict) -> None:
    masked = audit.mask_non_code(source)
    create_panel = extract_function(source, masked, "createPanel")
    handle_action = extract_function(source, masked, "handleAction")
    handle_setting = extract_function(source, masked, "handleSettingChange")
    toggle_feature = extract_function(source, masked, "toggleFeature")

    actions = values(r'data-action\s*=\s*["\']([^"\']+)["\']', create_panel)
    settings = values(r'data-setting\s*=\s*["\']([^"\']+)["\']', create_panel)
    tabs = values(r'data-tab\s*=\s*["\']([^"\']+)["\']', create_panel)
    rendered_toggles = sorted(set(
        re.findall(r'makeToggleButton\(\s*["\']([^"\']+)["\']', create_panel)
        + re.findall(r'data-toggle\s*=\s*["\']([^"\']+)["\']', create_panel)
    ))
    handled_actions = values(r'action\s*===\s*["\']([^"\']+)["\']', handle_action)
    handled_settings = values(r'setting\s*===\s*["\']([^"\']+)["\']', handle_setting)
    toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', toggle_feature)
    setting_families = values(r'setting\.startsWith\(\s*["\']([^"\']+)["\']\s*\)', handle_setting)

    assert actions == sorted(fixtures["actions"]), "Visible data-action inventory changed"
    assert settings == sorted(fixtures["settings"]), "Visible data-setting inventory changed"
    assert tabs == sorted(fixtures["tabs"]), "Panel tab inventory changed"
    assert handled_actions == sorted(fixtures["actions"] + fixtures["dynamicActions"]), "Action routing inventory changed"
    assert toggle_routes == sorted(fixtures["toggleRoutes"]), "Feature toggle routing inventory changed"
    assert setting_families == sorted(fixtures["settingFamilies"]), "Setting-family routing changed"

    missing_toggle_routes = sorted(set(rendered_toggles) - set(toggle_routes))
    assert not missing_toggle_routes, f"Rendered toggles without routes: {missing_toggle_routes}"
    unrendered_routes = sorted(set(toggle_routes) - set(rendered_toggles))
    assert unrendered_routes == sorted(fixtures["routeOnlyToggles"]), f"Unexpected route-only toggles: {unrendered_routes}"

    explicit_settings = set(handled_settings)
    families = tuple(fixtures["settingFamilies"])
    noops = set(fixtures["intentionalNoopSettings"])
    uncovered = sorted(setting for setting in settings if setting not in explicit_settings and setting not in noops and not setting.startswith(families))
    assert not uncovered, f"Rendered settings without change routing: {uncovered}"


def build_harness(source: str, fixtures: dict) -> str:
    masked = audit.mask_non_code(source)
    functions = "\n\n".join(extract_function(source, masked, name) for name in FUNCTION_NAMES)
    fixture_json = json.dumps(fixtures, ensure_ascii=False)
    return f'''"use strict";
const assert = require("node:assert/strict");
const fixtures = {fixture_json};

const FIXED_NOW = Number(fixtures.fixedNow);
Date.now = () => FIXED_NOW;

const MAP_PROFILE_LIMIT = 4;
const QUICK_PLACES = [{{ id: "edinburgh", name: "Edinburgh", lat: 55.95, lng: -3.19, zoom: 11 }}];
const POSITIONS = {{ bl: {{}}, br: {{}}, tl: {{}}, tr: {{}} }};
const UI_THEMES = {{ mapCommand: {{ label: "Map Command" }}, hyrule: {{ label: "Hyrule Command" }}, bond007: {{ label: "007 Intelligence" }} }};
const THEMES = {{ default: {{}}, nightshift: {{}}, fire: {{}}, police: {{}} }};
const PAYOUT_TEMPLATES = {{ gta5: {{}}, hyruleQuest: {{}}, bond007: {{}} }};
const PAYOUT_MEDIA_SOUNDS = {{}};
const PAYOUT_FLASH_DURATION_OPTIONS = [2000, 4000, 6000, 8000, 10000];
const MAJOR_INCIDENT_FEED_MINIMUM_OPTIONS = [10000, 25000, 50000, 100000];
const CRITICAL_AGE_FILTER_KEYS = ["2h", "4h", "8h", "12h", "24h"];
const CRITICAL_SORT_KEYS = ["age", "credits", "distance"];
const CRITICAL_OWNERSHIP_FILTER_KEYS = ["personal", "alliance", "all"];
const CRITICAL_CATEGORY_FILTER_KEYS = ["all", "fire", "police", "ambulance"];
const CRITICAL_PRIMARY_STATUS_KEYS = ["all", "waiting", "active", "clearing"];
const CRITICAL_VALUE_MODE_KEYS = ["total", "remaining"];
const STUCK_MIN_MINUTES = 5;
const STUCK_MAX_MINUTES = 120;
const RESOURCE_GAP_RADIUS_OPTIONS = [10, 25, 50];
const TRANSPORT_SWEEP_DELAY_OPTIONS = [1000, 2000, 3000, 5000];
const TRANSPORT_SWEEP_MAX_REQUESTS = 100;

const SCRIPT = {{
    storageState: "current-state",
    oldStorageKeys: ["legacy-state-1", "legacy-state-2"],
    legacyTheme: "legacy-theme",
    legacyPosition: "legacy-position",
    financeVaultCredentialState: "finance-credential",
    financeVaultState: "finance-state",
    panelId: "mcms-panel",
    criticalDrawerId: "critical-drawer",
    vehicleStatusId: "vehicle-status"
}};

const storage = new Map();
const localStorage = {{
    getItem(key) {{ return storage.has(String(key)) ? storage.get(String(key)) : null; }},
    setItem(key, value) {{ storage.set(String(key), String(value)); }},
    removeItem(key) {{ storage.delete(String(key)); }},
    clear() {{ storage.clear(); }}
}};
const gmStorage = new Map();
const calls = [];
function record(name, ...args) {{ calls.push({{ name, args }}); }}
function clearCalls() {{ calls.length = 0; }}
function wasCalled(name) {{ return calls.some(call => call.name === name); }}
function callFor(name) {{ return calls.find(call => call.name === name); }}
function pathValue(object, path) {{ return path.split(".").reduce((value, key) => value?.[key], object); }}
function localIsoDate(value = new Date(Date.now())) {{ return new Date(value).toISOString().slice(0, 10); }}
function sanitiseBookmarkShortLabel(value) {{ return String(value || "").trim().toUpperCase().slice(0, 4); }}

const document = {{
    querySelector(selector) {{
        if (String(selector).includes('payout-test-amount')) return {{ value: "25000" }};
        return {{ click() {{ record("file-click", selector); }} }};
    }},
    querySelectorAll() {{ return []; }},
    getElementById() {{ return null; }}
}};
const pageWindow = {{ confirm: () => true }};
const location = {{ reload: () => record("reload") }};

let state;
let criticalViewActive = false;
let criticalViewSnapshot = null;
let activeDeviceLayout = "desktop";
let operationalStartupComplete = true;
let missionSpawnArmed = false;
let missionSpawnPrimeTimer = null;
let payoutMediaAudio = null;
let applyLoadedConfiguration = () => record("applyLoadedConfiguration");
const knownMissionIds = new Set();
const resourceGapAnalysisCache = {{ clear: () => record("resourceGapAnalysisCache.clear") }};

function getLegacyThemeFallback() {{ return "default"; }}
function updateUI() {{ record("updateUI"); }}
function applyRootAttributes() {{
    activeDeviceLayout = state?.mobileMode === "on" ? "mobile" : state?.tabletMode === "on" ? "tablet" : "desktop";
    record("applyRootAttributes");
}}
function saveDiscordWebhookUrl(value) {{ gmStorage.set("webhook", String(value || "")); record("saveDiscordWebhookUrl", value); }}
function getDiscordWebhookUrl() {{ return gmStorage.get("webhook") || ""; }}
function normaliseDiscordWebhookUrl(value) {{ return String(value || "").trim(); }}
function gmGetValueSafe(key, fallback) {{ return gmStorage.has(key) ? gmStorage.get(key) : fallback; }}
function gmSetValueSafe(key, value) {{ gmStorage.set(key, value); }}
function gmDeleteValueSafe(key) {{ gmStorage.delete(key); }}
function normaliseImportedFinanceVaultCredential(value) {{ return value; }}
function normaliseImportedFinanceVaultStore(value) {{ return value; }}
function saveFinanceVaultCredential(value) {{ gmStorage.set(SCRIPT.financeVaultCredentialState, value); }}
function saveFinanceVaultStore(value) {{ gmStorage.set(SCRIPT.financeVaultState, value); }}
function invalidateFinanceVaultMemory() {{ record("invalidateFinanceVaultMemory"); }}
function loadCachedFinancialRules() {{ record("loadCachedFinancialRules"); }}
function loadCachedFinancialPolicy() {{ record("loadCachedFinancialPolicy"); }}

function closePanel() {{ record("closePanel"); }}
function installAutoLoadAllVehicles() {{ record("installAutoLoadAllVehicles"); }}
function stopAutoLoadAllVehicles() {{ record("stopAutoLoadAllVehicles"); }}
function unlockPayoutAudio(value) {{ record("unlockPayoutAudio", value); }}
function disposePayoutMediaAudio() {{ record("disposePayoutMediaAudio"); }}
function runtimeClearTimeout(value) {{ record("runtimeClearTimeout", value); }}
function primeMissionSpawnDetector() {{ record("primeMissionSpawnDetector"); }}
function toggleCriticalView() {{ record("toggleCriticalView"); }}
function missionSnapshotsNeeded() {{ return false; }}
function reconcileFeatureRefreshes(value) {{ record("reconcileFeatureRefreshes", value); }}
function synchroniseVehicleMarkerClasses() {{ record("synchroniseVehicleMarkerClasses"); }}
function synchronisePersonalBuildingVisibility() {{ record("synchronisePersonalBuildingVisibility"); }}
function scheduleEconomyLayerSync(value) {{ record("scheduleEconomyLayerSync", value); }}
function showToast(value) {{ record("showToast", value); }}
function refreshPersonalVehicleData(value) {{ record("refreshPersonalVehicleData", value); return Promise.resolve(true); }}
function scheduleUnitCommitmentRefresh(value) {{ record("scheduleUnitCommitmentRefresh", value); }}
function refreshMissionSnapshots() {{ record("refreshMissionSnapshots"); }}
function scheduleMajorIncidentFeedRender(value) {{ record("scheduleMajorIncidentFeedRender", value); }}
function removeMajorIncidentFeed() {{ record("removeMajorIncidentFeed"); }}
function installAllianceBuildingsEarlyStyle() {{ record("installAllianceBuildingsEarlyStyle"); }}
function installAllianceBuildingsLeafletAssignmentGuard() {{ record("installAllianceBuildingsLeafletAssignmentGuard"); }}
function installAllianceBuildingsContextWatcherEarly() {{ record("installAllianceBuildingsContextWatcherEarly"); }}
function clearAllianceBuildingsEarlyContext() {{ record("clearAllianceBuildingsEarlyContext"); }}
function isAllianceBuildingsContext() {{ return false; }}
function runtimeSetTimeout(callback, delay) {{ record("runtimeSetTimeout", delay); return 1; }}
function scheduleResourceGapRefresh(value) {{ record("scheduleResourceGapRefresh", value); }}
function refreshVisibleMissionInspector() {{ record("refreshVisibleMissionInspector"); }}
function runAutoNight(value) {{ record("runAutoNight", value); }}

function setMapView(...args) {{ record("setMapView", ...args); return true; }}
function toggleQuickPin(...args) {{ record("toggleQuickPin", ...args); }}
function saveBookmark(...args) {{ record("saveBookmark", ...args); }}
function editBookmarkLabel(...args) {{ record("editBookmarkLabel", ...args); }}
function goBookmark(...args) {{ record("goBookmark", ...args); }}
function deleteBookmark(...args) {{ record("deleteBookmark", ...args); }}
function toggleBookmarkPin(...args) {{ record("toggleBookmarkPin", ...args); }}
function nudgeControl(...args) {{ record("nudgeControl", ...args); }}
function resetNudge(...args) {{ record("resetNudge", ...args); }}
function nudgePanel(...args) {{ record("nudgePanel", ...args); }}
function openHelpCenter(...args) {{ record("openHelpCenter", ...args); }}
function setEconomyMode(...args) {{ record("setEconomyMode", ...args); }}
function toggleCriticalDrawer(...args) {{ record("toggleCriticalDrawer", ...args); }}
function toggleVehicleCodeStatus(...args) {{ record("toggleVehicleCodeStatus", ...args); }}
function fitCriticalMissions(...args) {{ record("fitCriticalMissions", ...args); }}
function buildTransportSweepQueue() {{ record("buildTransportSweepQueue"); return [1, 2]; }}
function startTransportSweep(...args) {{ record("startTransportSweep", ...args); }}
function stopTransportSweep(...args) {{ record("stopTransportSweep", ...args); }}
function resetSessionPerformance(...args) {{ record("resetSessionPerformance", ...args); }}
function clearPayoutHistory(...args) {{ record("clearPayoutHistory", ...args); }}
function focusMissionById(...args) {{ record("focusMissionById", ...args); }}
function saveMapProfile(...args) {{ record("saveMapProfile", ...args); }}
function loadMapProfile(...args) {{ record("loadMapProfile", ...args); }}
function deleteMapProfile(...args) {{ record("deleteMapProfile", ...args); }}
function exportToolkitConfig(...args) {{ record("exportToolkitConfig", ...args); }}
function resetToolkitConfiguration(...args) {{ record("resetToolkitConfiguration", ...args); }}
function testDiscordWebhook(...args) {{ record("testDiscordWebhook", ...args); }}
function postDiscordFinancialReport(...args) {{ record("postDiscordFinancialReport", ...args); }}
function clearDiscordWebhook(...args) {{ record("clearDiscordWebhook", ...args); }}
function scanFinancialArchive(...args) {{ record("scanFinancialArchive", ...args); }}
function cancelFinancialArchiveScan(...args) {{ record("cancelFinancialArchiveScan", ...args); }}
function exportFinancialArchive(...args) {{ record("exportFinancialArchive", ...args); }}
function clearFinancialArchive(...args) {{ record("clearFinancialArchive", ...args); }}
function refreshFinancialIntelligenceFeeds(...args) {{ record("refreshFinancialIntelligenceFeeds", ...args); return Promise.resolve(true); }}
function renderFinanceVaultStatus(...args) {{ record("renderFinanceVaultStatus", ...args); }}
function triggerPayoutFlash(...args) {{ record("triggerPayoutFlash", ...args); return true; }}
function resetPanelPosition(...args) {{ record("resetPanelPosition", ...args); }}

function refreshTabletModeUi() {{ record("refreshTabletModeUi"); }}
function isTouchLayoutActive() {{ return activeDeviceLayout === "mobile" || activeDeviceLayout === "tablet"; }}
function clearTabletPanelSizing() {{ record("clearTabletPanelSizing"); }}
function clearTabletDockSizing() {{ record("clearTabletDockSizing"); }}
function fitControlToMap() {{ record("fitControlToMap"); }}
function positionPanelOverlay(value) {{ record("positionPanelOverlay", value); }}
function formatOperationalCompactCredits(value) {{ return String(value); }}
function scheduleCoverageRefresh() {{ record("scheduleCoverageRefresh"); }}
function scheduleHeatmapRefresh() {{ record("scheduleHeatmapRefresh"); }}
function scheduleStuckMissionRefresh(value) {{ record("scheduleStuckMissionRefresh", value); }}
function scheduleAllianceCreditRefresh(value) {{ record("scheduleAllianceCreditRefresh", value); }}
function setDiscordStatus(...args) {{ record("setDiscordStatus", ...args); }}
function invalidateDiscordFinancialPreview() {{ record("invalidateDiscordFinancialPreview"); }}
function setFinanceVaultStatus(...args) {{ record("setFinanceVaultStatus", ...args); }}
function payoutTemplateMeta(key) {{ return {{ label: key }}; }}

{functions}

function resetEnvironment() {{
    storage.clear();
    gmStorage.clear();
    clearCalls();
    criticalViewActive = false;
    activeDeviceLayout = "desktop";
    missionSpawnArmed = false;
    missionSpawnPrimeTimer = null;
    knownMissionIds.clear();
    payoutMediaAudio = null;
    applyLoadedConfiguration = () => record("applyLoadedConfiguration");
    state = defaultState();
}}

function assertDefaultShape(value) {{
    assert.equal(value.uiTheme, "mapCommand");
    assert.equal(value.theme, "default");
    assert.equal(value.position, "bl");
    assert.equal(value.activeTab, "skins");
    assert.equal(value.tabletMode, "auto");
    assert.equal(value.mobileMode, "auto");
    assert.equal(value.profiles.length, MAP_PROFILE_LIMIT);
    assert.equal(value.bookmarks.length, 5);
    assert.equal(value.visibility.vehicles, true);
    assert.equal(value.payoutFlash.template, "gta5");
}}

function testStateMigration() {{
    resetEnvironment();
    assertDefaultShape(loadState());

    localStorage.setItem(SCRIPT.storageState, "{{not-json");
    localStorage.setItem(SCRIPT.oldStorageKeys[0], JSON.stringify(fixtures.modernState));
    assertDefaultShape(loadState());

    resetEnvironment();
    localStorage.setItem(SCRIPT.oldStorageKeys[0], JSON.stringify(fixtures.legacyMigration));
    const migrated = loadState();
    assert.equal(migrated.uiTheme, "mapCommand");
    assert.equal(migrated.theme, "default");
    assert.equal(migrated.position, "bl");
    assert.equal(migrated.activeTab, "resources");
    assert.equal(Object.hasOwn(migrated, "fleetFilter"), false);
    assert.equal(Object.hasOwn(migrated, "requiresAttention"), false);
    assert.deepEqual(migrated.nudge, {{ x: 220, y: -220 }});
    assert.equal(migrated.visibility.vehicles, false);
    assert.equal(migrated.visibility.buildings, true);
    assert.equal(migrated.coverage.radiusMi, 25);
    assert.equal(migrated.heatmap.radiusMi, 10);
    assert.equal(migrated.heatmap.opacity, 0.55);
    assert.equal(migrated.allianceCreditMinimum, 0);
    assert.equal(migrated.autoLoadAllVehicles, true);
    assert.equal(migrated.allianceBuildingsMap, false);
    assert.equal(migrated.majorIncidentFeed.enabled, false);
    assert.equal(migrated.majorIncidentFeed.minimumCredits, 25000);
    assert.equal(migrated.tabletMode, "auto");
    assert.equal(migrated.mobileMode, "auto");
    assert.equal(migrated.stuckDetector.enabled, false);
    assert.equal(migrated.stuckDetector.thresholdMin, 120);
    assert.equal(migrated.resourceGap.enabled, true);
    assert.equal(migrated.resourceGap.radiusMi, 25);
    assert.equal(migrated.transportSweep.delayMs, 2000);
    assert.equal(migrated.transportSweep.maxPerRun, 100);
    assert.equal(migrated.payoutFlash.template, "gta5");
    assert.equal(migrated.payoutFlash.soundVolume, 1);
    assert.equal(migrated.discordReport.webhookName, "MissionChief Finance");
    assert.equal(migrated.discordReport.topCategories, 5);
    assert.equal(migrated.discordReport.period, "today");
    assert.equal(migrated.discordReport.reportMode, "fullAudit");
    assert.equal(migrated.financialVault.retentionDays, "all");
    assert.equal(Object.hasOwn(migrated.financialVault, "autoSync"), false);
    assert.equal(Object.hasOwn(migrated.financialVault, "benchmarkOptIn"), false);
    assert.equal(Object.hasOwn(migrated.financialVault, "gatewayUrl"), false);
    assert.equal(migrated.profiles.length, MAP_PROFILE_LIMIT);
    assert.equal(migrated.profiles[1], null);
    assert.equal(migrated.bookmarks.length, 5);
    assert.equal(migrated.bookmarks[0].name, "Edinburgh Operations");
    assert.equal(migrated.bookmarks[0].pinned, true);
    assert.deepEqual(migrated.panelPosition, {{ left: 12, top: 34 }});

    resetEnvironment();
    localStorage.setItem(SCRIPT.oldStorageKeys[0], JSON.stringify(fixtures.legacyMigration));
    localStorage.setItem(SCRIPT.storageState, JSON.stringify(fixtures.modernState));
    const modern = loadState();
    assert.equal(modern.uiTheme, "hyrule");
    assert.equal(modern.theme, "nightshift");
    assert.equal(modern.position, "tr");
    assert.equal(modern.activeTab, "discord");
    assert.equal(modern.mobileMode, "on");
    assert.equal(modern.tabletMode, "off");
    assert.equal(modern.visibility.vehicles, false);
    assert.equal(modern.visibility.buildings, true);
    assert.equal(modern.payoutFlash.template, "hyruleQuest");
    assert.equal(modern.discordReport.reportMode, "executive");

    state = modern;
    saveState();
    assert.deepEqual(JSON.parse(localStorage.getItem(SCRIPT.storageState)), modern);
    assert.equal(localStorage.getItem(SCRIPT.legacyTheme), "nightshift");
    assert.equal(localStorage.getItem(SCRIPT.legacyPosition), "tr");
}}

function testImportContracts() {{
    const candidate = {{ theme: "nightshift", position: "tr" }};
    assert.equal(looksLikeToolkitState(candidate), true);
    assert.equal(looksLikeToolkitState([]), false);
    assert.deepEqual(extractImportedToolkitState({{ state: candidate }}), candidate);
    assert.deepEqual(extractImportedToolkitState({{ settings: {{ state: candidate }} }}), candidate);
    assert.deepEqual(extractImportedToolkitState({{ configuration: {{ state: candidate }} }}), candidate);
    assert.deepEqual(extractImportedToolkitState({{ configuration: candidate }}), candidate);
    assert.deepEqual(extractImportedToolkitState(candidate), candidate);
    assert.equal(extractImportedToolkitState({{ unrelated: true }}), null);

    assert.deepEqual(extractImportedDiscordWebhook({{ integrations: {{ discordWebhook: "value" }} }}), {{ present: true, value: "value" }});
    assert.deepEqual(extractImportedDiscordWebhook({{ settings: {{ integrations: {{ discordWebhookUrl: "alias" }} }} }}), {{ present: true, value: "alias" }});
    assert.equal(extractImportedFinancialVaultCredential({{ financialArchiveIdentity: {{ deviceId: "d" }} }}).present, true);
    assert.equal(extractImportedFinancialVaultStore({{ financialArchiveStore: {{ profiles: {{}} }} }}).present, true);
    const privateInfo = describePrivateImport({{ integrations: {{ discordWebhook: "value" }}, financialArchiveStore: {{ profiles: {{ one: {{}} }} }} }});
    assert.equal(privateInfo.privateItems.length, 2);

    resetEnvironment();
    localStorage.setItem(SCRIPT.storageState, JSON.stringify({{ theme: "default", position: "bl" }}));
    state = loadState();
    const result = applyImportedToolkitSettings({{ state: fixtures.modernState }});
    assert.deepEqual(result, {{ webhook: false, credential: false, vaultHistory: false }});
    assert.equal(state.theme, "nightshift");
    assert.equal(state.position, "tr");
    assert.equal(wasCalled("applyLoadedConfiguration"), true);

    resetEnvironment();
    const previousRaw = JSON.stringify({{ theme: "default", position: "br" }});
    localStorage.setItem(SCRIPT.storageState, previousRaw);
    state = loadState();
    let applyAttempts = 0;
    applyLoadedConfiguration = () => {{
        applyAttempts += 1;
        if (applyAttempts === 1) throw new Error("fixture apply failure");
        record("applyLoadedConfigurationRollback");
    }};
    assert.throws(() => applyImportedToolkitSettings({{ state: fixtures.modernState }}), /fixture apply failure/);
    assert.equal(localStorage.getItem(SCRIPT.storageState), previousRaw);
    assert.equal(state.position, "br");
    assert.equal(applyAttempts, 2);
}}

async function testToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.toggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        toggleFeature(feature);
        await Promise.resolve();
        await Promise.resolve();
        const after = pathValue(state, path);
        assert.notEqual(after, before, `${{feature}} did not toggle ${{path}}`);
        assert.equal(localStorage.getItem(SCRIPT.storageState) !== null, true, `${{feature}} did not persist state`);
        assert.equal(wasCalled("updateUI"), true, `${{feature}} did not request UI synchronization`);
    }}

    resetEnvironment();
    toggleFeature("criticalView");
    assert.equal(wasCalled("toggleCriticalView"), true);
    assert.equal(localStorage.getItem(SCRIPT.storageState), null);
}}

async function testActionContracts() {{
    resetEnvironment();
    handleAction({{ dataset: {{ action: "nudge-left" }} }});
    assert.deepEqual(callFor("nudgeControl").args, [-4, 0]);

    clearCalls();
    handleAction({{ dataset: {{ action: "import-config" }} }});
    assert.equal(wasCalled("file-click"), true);

    clearCalls();
    handleAction({{ dataset: {{ action: "finance-rules-refresh" }} }});
    await Promise.resolve();
    await Promise.resolve();
    assert.equal(wasCalled("refreshFinancialIntelligenceFeeds"), true);
    assert.equal(wasCalled("renderFinanceVaultStatus"), true);

    clearCalls();
    state.payoutFlash.threshold = 10000;
    handleAction({{ dataset: {{ action: "test-payout-flash" }} }});
    assert.equal(callFor("triggerPayoutFlash").args[0], 25000);

    clearCalls();
    handleAction({{ dataset: {{ action: "place-go", place: "edinburgh" }} }});
    assert.equal(wasCalled("setMapView"), true);

    clearCalls();
    handleAction({{ dataset: {{ action: "profile-save", slot: "2" }} }});
    assert.deepEqual(callFor("saveMapProfile").args, [2]);

    clearCalls();
    handleAction({{ dataset: {{ action: "panel-reset" }} }});
    assert.equal(wasCalled("resetPanelPosition"), true);
}}

async function testSettingContracts() {{
    resetEnvironment();
    state.tabletMode = "on";
    handleSettingChange({{ dataset: {{ setting: "mobile-mode" }}, value: "on" }});
    assert.equal(state.mobileMode, "on");
    assert.equal(state.tabletMode, "off");
    assert.equal(activeDeviceLayout, "mobile");

    handleSettingChange({{ dataset: {{ setting: "tablet-mode" }}, value: "on" }});
    assert.equal(state.tabletMode, "on");
    assert.equal(state.mobileMode, "off");
    assert.equal(activeDeviceLayout, "tablet");

    handleSettingChange({{ dataset: {{ setting: "major-incident-minimum" }}, value: "999" }});
    assert.equal(state.majorIncidentFeed.minimumCredits, 25000);
    handleSettingChange({{ dataset: {{ setting: "coverage-radius" }}, value: "50" }});
    assert.equal(state.coverage.radiusMi, 50);
    handleSettingChange({{ dataset: {{ setting: "heatmap-source" }}, value: "invalid" }});
    assert.equal(state.heatmap.source, "stations");
    handleSettingChange({{ dataset: {{ setting: "heatmap-service" }}, value: "police" }});
    assert.equal(state.heatmap.service, "police");
    handleSettingChange({{ dataset: {{ setting: "heatmap-opacity" }}, value: "0.42" }});
    assert.equal(state.heatmap.opacity, 0.42);

    handleSettingChange({{ dataset: {{ setting: "transport-sweep-delay" }}, value: "5000" }});
    assert.equal(state.transportSweep.delayMs, 5000);
    handleSettingChange({{ dataset: {{ setting: "transport-sweep-max" }}, value: "999" }});
    assert.equal(state.transportSweep.maxPerRun, 100);
    handleSettingChange({{ dataset: {{ setting: "resource-gap-radius" }}, value: "50" }});
    assert.equal(state.resourceGap.radiusMi, 50);
    handleSettingChange({{ dataset: {{ setting: "stuck-threshold" }}, value: "999" }});
    assert.equal(state.stuckDetector.thresholdMin, 120);
    handleSettingChange({{ dataset: {{ setting: "alliance-credit-minimum" }}, value: "123" }});
    assert.equal(state.allianceCreditMinimum, 0);

    handleSettingChange({{ dataset: {{ setting: "discord-name" }}, value: `  ${{"A".repeat(100)}}  ` }});
    assert.equal(state.discordReport.webhookName.length, 80);
    handleSettingChange({{ dataset: {{ setting: "discord-period" }}, value: "invalid" }});
    assert.equal(state.discordReport.period, "today");
    handleSettingChange({{ dataset: {{ setting: "discord-report-mode" }}, value: "executive" }});
    assert.equal(state.discordReport.reportMode, "executive");
    handleSettingChange({{ dataset: {{ setting: "discord-risk" }}, value: "false" }});
    assert.equal(state.discordReport.includeRisk, false);

    handleSettingChange({{ dataset: {{ setting: "finance-vault-enabled" }}, value: "false" }});
    assert.equal(state.financialVault.enabled, false);
    handleSettingChange({{ dataset: {{ setting: "finance-vault-retention" }}, value: "365" }});
    assert.equal(state.financialVault.retentionDays, 365);
    handleSettingChange({{ dataset: {{ setting: "finance-rule-feed" }}, value: "false" }});
    await Promise.resolve();
    assert.equal(state.financialVault.ruleFeedEnabled, false);

    handleSettingChange({{ dataset: {{ setting: "payout-template" }}, value: "hyruleQuest" }});
    assert.equal(state.payoutFlash.template, "hyruleQuest");
    handleSettingChange({{ dataset: {{ setting: "payout-template" }}, value: "invalid" }});
    assert.equal(state.payoutFlash.template, "gta5");
    handleSettingChange({{ dataset: {{ setting: "payout-threshold" }}, value: "500000" }});
    assert.equal(state.payoutFlash.threshold, 500000);
    handleSettingChange({{ dataset: {{ setting: "payout-volume" }}, value: "0.8" }});
    assert.equal(state.payoutFlash.soundVolume, 0.8);

    handleSettingChange({{ dataset: {{ setting: "auto-night-start" }}, value: "20:30" }});
    assert.equal(state.autoNight.nightStart, "20:30");
    handleSettingChange({{ dataset: {{ setting: "auto-night-theme" }}, value: "nightshift" }});
    assert.equal(state.autoNight.nightTheme, "nightshift");

    const before = JSON.stringify(state);
    handleSettingChange({{ dataset: {{ setting: "payout-test-amount" }}, value: "90000" }});
    assert.equal(JSON.stringify(state), before);
}}

(async () => {{
    testStateMigration();
    testImportContracts();
    await testToggleContracts();
    await testActionContracts();
    await testSettingContracts();
    console.log(`Settings/UI contract passed: defaults, migrations, import rollback, ${{fixtures.toggleRoutes.length}} toggles, ${{fixtures.actions.length}} actions and ${{fixtures.settings.length}} settings.`);
}})().catch(error => {{
    console.error(error?.stack || error);
    process.exitCode = 1;
}});
'''


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert_static_routes(source, fixtures)
    harness = build_harness(source, fixtures)
    with tempfile.TemporaryDirectory(prefix="missionchief-settings-ui-contract-") as temporary:
        harness_path = Path(temporary) / "settings-ui-contract.cjs"
        harness_path.write_text(harness, encoding="utf-8")
        completed = subprocess.run(
            ["node", str(harness_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            env={**os.environ, "TZ": "Europe/London"},
        )
    print(completed.stdout, end="")
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
