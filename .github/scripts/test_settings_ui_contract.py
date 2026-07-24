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
    "defaultOperationalWindowState",
    "operationalSuiteBoolean",
    "operationalSuiteArray",
    "normaliseOperationalWindowState",
    "defaultState",
    "normaliseLoadedState",
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
    "handleMapVisibilityToggle",
    "applyMapVisibilityToggleEffects",
    "handleMissionWindowToggle",
    "applyMissionWindowToggleEffects",
    "handlePayoutAudioToggle",
    "applyPayoutAudioToggleEffects",
    "handleMissionMonitoringToggle",
    "applyMissionMonitoringToggleEffects",
    "handleInterfaceShellToggle",
    "toggleFeature",
    "handleAction",
    "handleDiscordFinancialSettingChange",
    "handleDeviceLayoutSettingChange",
    "handleOperationalWindowSettingChange",
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
    handle_financial_setting = extract_function(source, masked, "handleDiscordFinancialSettingChange")
    handle_device_layout_setting = extract_function(source, masked, "handleDeviceLayoutSettingChange")
    handle_setting = extract_function(source, masked, "handleSettingChange")
    handle_map_visibility_toggle = extract_function(source, masked, "handleMapVisibilityToggle")
    apply_map_visibility_effects = extract_function(source, masked, "applyMapVisibilityToggleEffects")
    handle_mission_window_toggle = extract_function(source, masked, "handleMissionWindowToggle")
    apply_mission_window_effects = extract_function(source, masked, "applyMissionWindowToggleEffects")
    handle_payout_audio_toggle = extract_function(source, masked, "handlePayoutAudioToggle")
    apply_payout_audio_effects = extract_function(source, masked, "applyPayoutAudioToggleEffects")
    handle_mission_monitoring_toggle = extract_function(source, masked, "handleMissionMonitoringToggle")
    apply_mission_monitoring_effects = extract_function(source, masked, "applyMissionMonitoringToggleEffects")
    handle_interface_shell_toggle = extract_function(source, masked, "handleInterfaceShellToggle")
    toggle_feature = extract_function(source, masked, "toggleFeature")

    actions = values(r'data-action\s*=\s*["\']([^"\']+)["\']', create_panel)
    settings = values(r'data-setting\s*=\s*["\']([^"\']+)["\']', create_panel)
    tabs = values(r'data-tab\s*=\s*["\']([^"\']+)["\']', create_panel)
    rendered_toggles = sorted(set(
        re.findall(r'makeToggleButton\(\s*["\']([^"\']+)["\']', create_panel)
        + re.findall(r'data-toggle\s*=\s*["\']([^"\']+)["\']', create_panel)
    ))
    handled_actions = values(r'action\s*===\s*["\']([^"\']+)["\']', handle_action)
    direct_settings = values(r'setting\s*===\s*["\']([^"\']+)["\']', handle_setting)
    extracted_settings = values(r'setting\s*===\s*["\']([^"\']+)["\']', handle_financial_setting)
    device_layout_settings = values(r'setting\s*===\s*["\']([^"\']+)["\']', handle_device_layout_setting)
    handled_settings = sorted(set(direct_settings + extracted_settings + device_layout_settings))
    direct_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', toggle_feature)
    extracted_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_map_visibility_toggle)
    extracted_toggle_effect_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', apply_map_visibility_effects)
    mission_window_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_mission_window_toggle)
    mission_window_effect_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', apply_mission_window_effects)
    payout_audio_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_payout_audio_toggle)
    payout_audio_effect_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', apply_payout_audio_effects)
    mission_monitoring_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_mission_monitoring_toggle)
    mission_monitoring_effect_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', apply_mission_monitoring_effects)
    interface_shell_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_interface_shell_toggle)
    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes + payout_audio_toggle_routes + mission_monitoring_toggle_routes + interface_shell_toggle_routes))
    setting_families = values(r'setting\.startsWith\(\s*["\']([^"\']+)["\']\s*\)', handle_setting)

    assert actions == sorted(fixtures["actions"]), "Visible data-action inventory changed"
    assert settings == sorted(fixtures["settings"]), "Visible data-setting inventory changed"
    assert tabs == sorted(fixtures["tabs"]), "Panel tab inventory changed"
    assert handled_actions == sorted(fixtures["actions"] + fixtures["dynamicActions"]), "Action routing inventory changed"
    assert toggle_routes == sorted(fixtures["toggleRoutes"]), "Feature toggle routing inventory changed"
    assert extracted_toggle_routes == sorted(fixtures["extractedToggleRoutes"]), "Extracted map/visibility toggle routing changed"
    assert extracted_toggle_effect_routes == sorted(fixtures["extractedToggleEffectRoutes"]), "Extracted map/visibility effect routing changed"
    assert not set(direct_toggle_routes).intersection(extracted_toggle_routes), "Extracted toggles must not remain duplicated in toggleFeature"
    assert "handleMapVisibilityToggle(feature)" in toggle_feature, "Main toggle router must delegate to the extracted map/visibility state family"
    assert "applyMapVisibilityToggleEffects(feature)" in toggle_feature, "Main toggle router must delegate to the extracted map/visibility effect family"
    assert mission_window_toggle_routes == sorted(fixtures["extractedMissionWindowToggleRoutes"]), "Extracted mission-window toggle routing changed"
    assert mission_window_effect_routes == sorted(fixtures["extractedMissionWindowEffectRoutes"]), "Extracted mission-window effect routing changed"
    assert not set(direct_toggle_routes).intersection(mission_window_toggle_routes), "Extracted mission-window toggles must not remain duplicated in toggleFeature"
    assert "handleMissionWindowToggle(feature)" in toggle_feature, "Main toggle router must delegate to the extracted mission-window state family"
    assert "applyMissionWindowToggleEffects(feature)" in toggle_feature, "Main toggle router must delegate to the extracted mission-window effect family"
    assert payout_audio_toggle_routes == sorted(fixtures["extractedPayoutAudioToggleRoutes"]), "Extracted payout/audio toggle routing changed"
    assert payout_audio_effect_routes == sorted(fixtures["extractedPayoutAudioEffectRoutes"]), "Extracted payout/audio effect routing changed"
    assert not set(direct_toggle_routes).intersection(payout_audio_toggle_routes), "Extracted payout/audio toggles remain duplicated"
    assert "handlePayoutAudioToggle(feature)" in toggle_feature
    assert "applyPayoutAudioToggleEffects(feature)" in toggle_feature
    assert mission_monitoring_toggle_routes == sorted(fixtures["extractedMissionMonitoringToggleRoutes"]), "Extracted mission-monitoring toggle routing changed"
    assert mission_monitoring_effect_routes == sorted(fixtures["extractedMissionMonitoringEffectRoutes"]), "Extracted mission-monitoring effect routing changed"
    assert not set(direct_toggle_routes).intersection(mission_monitoring_toggle_routes), "Extracted mission-monitoring toggles remain duplicated"
    assert "handleMissionMonitoringToggle(feature)" in toggle_feature
    assert "applyMissionMonitoringToggleEffects(feature)" in toggle_feature
    assert interface_shell_toggle_routes == sorted(fixtures["extractedInterfaceShellToggleRoutes"]), "Extracted interface-shell toggle routing changed"
    assert not set(direct_toggle_routes).intersection(interface_shell_toggle_routes), "Extracted interface-shell toggles remain duplicated"
    assert "handleInterfaceShellToggle(feature)" in toggle_feature
    assert setting_families == sorted(fixtures["settingFamilies"]), "Setting-family routing changed"
    assert extracted_settings == sorted(fixtures["extractedSettingRoutes"]), "Extracted financial setting routing changed"
    assert not set(direct_settings).intersection(extracted_settings), "Extracted settings must not remain duplicated in handleSettingChange"
    assert "handleDiscordFinancialSettingChange(target, setting)" in handle_setting, "Main setting router must delegate to the extracted financial route family"
    assert device_layout_settings == sorted(fixtures["extractedDeviceLayoutSettingRoutes"]), "Extracted device-layout setting routing changed"
    assert not set(direct_settings).intersection(device_layout_settings), "Extracted device-layout settings remain duplicated in handleSettingChange"
    assert "handleDeviceLayoutSettingChange(target, setting)" in handle_setting, "Main setting router must delegate to the extracted device-layout route family"
    assert handle_device_layout_setting.index("saveState();") < handle_device_layout_setting.index("applyRootAttributes();") < handle_device_layout_setting.index("refreshTabletModeUi();"), "Device-layout persistence and reconciliation ordering changed"
    assert handle_device_layout_setting.index("fitControlToMap();") < handle_device_layout_setting.index("positionPanelOverlay(true);") < handle_device_layout_setting.index("showToast("), "Device-layout fit, positioning and notification ordering changed"

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
const LEGACY_THEME_MAP = {{ legacyNight: "nightshift" }};
const PAYOUT_TEMPLATES = {{ gta5: {{}}, hyruleQuest: {{}}, bond007: {{}} }};
const PAYOUT_MEDIA_SOUNDS = {{}};
const PAYOUT_FLASH_MIN_MS = 2000;
const PAYOUT_FLASH_MAX_MS = 10000;
const PAYOUT_FLASH_STEP_MS = 1000;
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
const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;

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
let missionAgeTimer = null;
let inlineMissionDataScanned = false;
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
function installMissionValueWindows() {{ record("installMissionValueWindows"); }}
function clearMissionValueIndicators() {{ record("clearMissionValueIndicators"); }}
function installCustomVehicleBadges() {{ record("installCustomVehicleBadges"); }}
function clearCustomVehicleBadges() {{ record("clearCustomVehicleBadges"); }}
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
function scanInlineMissionMarkerData(value) {{ record("scanInlineMissionMarkerData", value); }}
function invalidateMarkerRegistryCaches(value) {{ record("invalidateMarkerRegistryCaches", value); }}
function scheduleMarkerStateSync(...args) {{ record("scheduleMarkerStateSync", ...args); }}
function scheduleMissionAgeRefresh(value) {{ record("scheduleMissionAgeRefresh", value); }}
function clearMissionAgeLabels() {{ record("clearMissionAgeLabels"); }}
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
    missionAgeTimer = null;
    inlineMissionDataScanned = false;
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
    assert.equal(value.missionValue, true);
    assert.equal(Object.hasOwn(value, "missionRequirements"), false);
    assert.equal(value.operationalWindow.requirements.enabled, true);
    assert.equal(value.operationalWindow.migration.matrixRetired, true);
}}

function testStateMigration() {{
    resetEnvironment();
    assertDefaultShape(loadState());

    const directInput = JSON.parse(JSON.stringify(fixtures.legacyMigration));
    const directInputBefore = JSON.stringify(directInput);
    const directBase = defaultState();
    const directBaseBefore = JSON.stringify(directBase);
    const directMigrated = normaliseLoadedState(directInput, directBase);
    assert.equal(JSON.stringify(directInput), directInputBefore, "normalization must not mutate parsed settings");
    assert.equal(JSON.stringify(directBase), directBaseBefore, "normalization must not mutate default settings");
    assert.equal(directMigrated.activeTab, "resources");
    assert.equal(directMigrated.visibility.buildings, true);
    assert.equal(directMigrated.payoutFlash.template, "gta5");
    assert.equal(directMigrated.missionValue, false);
    assert.equal(Object.hasOwn(directMigrated, "missionRequirements"), false);
    assert.equal(directMigrated.operationalWindow.requirements.enabled, false);
    assert.equal(directMigrated.operationalWindow.migration.matrixRetired, true);

    localStorage.setItem(SCRIPT.storageState, "{{not-json");
    localStorage.setItem(SCRIPT.oldStorageKeys[0], JSON.stringify(fixtures.modernState));
    assertDefaultShape(loadState());

    resetEnvironment();
    localStorage.setItem(SCRIPT.oldStorageKeys[0], JSON.stringify(fixtures.legacyMigration));
    const migrated = loadState();
    assert.deepEqual(migrated, directMigrated, "loadState must preserve direct normalization output");
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
    assert.equal(migrated.missionValue, false);
    assert.equal(Object.hasOwn(migrated, "missionRequirements"), false);
    assert.equal(migrated.operationalWindow.requirements.enabled, false);
    assert.equal(migrated.operationalWindow.migration.matrixRetired, true);
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
    assert.equal(modern.missionValue, true);
    assert.equal(Object.hasOwn(modern, "missionRequirements"), false);
    assert.equal(modern.operationalWindow.requirements.enabled, true);
    assert.equal(modern.operationalWindow.migration.matrixRetired, true);

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

function testExtractedMapVisibilityToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        assert.equal(handleMapVisibilityToggle(feature), true, `${{feature}} was not handled directly`);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle ${{path}} directly`);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null, `${{feature}} helper must not persist before the router finalizes`);
        assert.equal(wasCalled("updateUI"), false, `${{feature}} helper must not render before the router finalizes`);
    }}

    resetEnvironment();
    const beforeUnknown = JSON.stringify(state);
    assert.equal(handleMapVisibilityToggle("unknown-map-toggle"), false);
    assert.equal(JSON.stringify(state), beforeUnknown, "unknown map toggle mutated state");

    resetEnvironment();
    state.economyMode = true;
    applyMapVisibilityToggleEffects("vehicles");
    assert.equal(wasCalled("synchroniseVehicleMarkerClasses"), true);
    assert.equal(wasCalled("synchronisePersonalBuildingVisibility"), false);
    assert.deepEqual(callFor("scheduleEconomyLayerSync").args, [0]);

    resetEnvironment();
    state.economyMode = true;
    applyMapVisibilityToggleEffects("buildings");
    assert.equal(wasCalled("synchroniseVehicleMarkerClasses"), false);
    assert.equal(wasCalled("synchronisePersonalBuildingVisibility"), true);
    assert.deepEqual(callFor("scheduleEconomyLayerSync").args, [0]);

    resetEnvironment();
    missionAgeTimer = 91;
    state.missionAge = false;
    applyMapVisibilityToggleEffects("missionAge");
    assert.deepEqual(callFor("runtimeClearTimeout").args, [91]);
    assert.equal(missionAgeTimer, null);
    assert.equal(wasCalled("clearMissionAgeLabels"), true);
    assert.equal(wasCalled("scanInlineMissionMarkerData"), false);

    resetEnvironment();
    missionAgeTimer = 92;
    state.missionAge = true;
    inlineMissionDataScanned = true;
    applyMapVisibilityToggleEffects("missionAge");
    assert.deepEqual(callFor("runtimeClearTimeout").args, [92]);
    assert.equal(missionAgeTimer, null);
    assert.equal(inlineMissionDataScanned, false);
    assert.deepEqual(callFor("scanInlineMissionMarkerData").args, [true]);
    assert.deepEqual(callFor("invalidateMarkerRegistryCaches").args, ["mission"]);
    assert.deepEqual(callFor("scheduleMarkerStateSync").args, [0, true]);
    assert.deepEqual(callFor("scheduleMissionAgeRefresh").args, [0]);
    assert.deepEqual(callFor("runtimeSetTimeout").args, [1000]);
    assert.equal(wasCalled("clearMissionAgeLabels"), false);

    resetEnvironment();
    state.economyMode = true;
    applyMapVisibilityToggleEffects("coverage");
    assert.equal(calls.length, 0, "map overlays without direct layer sync must remain side-effect free in the extracted effect phase");
}}


function testExtractedMissionWindowToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedMissionWindowToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        assert.equal(handleMissionWindowToggle(feature), true, `${{feature}} was not handled directly`);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle ${{path}} directly`);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null, `${{feature}} helper must not persist before router finalization`);
        assert.equal(wasCalled("updateUI"), false, `${{feature}} helper must not render before router finalization`);
    }}

    resetEnvironment();
    const beforeUnknown = JSON.stringify(state);
    assert.equal(handleMissionWindowToggle("unknown-mission-window-toggle"), false);
    assert.equal(JSON.stringify(state), beforeUnknown, "unknown mission-window toggle mutated state");

    const effects = [
        ["missionValue", "installMissionValueWindows", "clearMissionValueIndicators"],
        ["customVehicleBadges", "installCustomVehicleBadges", "clearCustomVehicleBadges"],
    ];
    for (const [feature, installCall, clearCall] of effects) {{
        resetEnvironment();
        applyMissionWindowToggleEffects(feature);
        assert.equal(wasCalled(installCall), true, `${{feature}} enabled effect did not install`);
        assert.equal(wasCalled(clearCall), false, `${{feature}} enabled effect cleared unexpectedly`);
        resetEnvironment();
        state[feature] = false;
        applyMissionWindowToggleEffects(feature);
        assert.equal(wasCalled(clearCall), true, `${{feature}} disabled effect did not clear`);
        assert.equal(wasCalled(installCall), false, `${{feature}} disabled effect installed unexpectedly`);
    }}

    resetEnvironment();
    applyMissionWindowToggleEffects("missionInspector");
    assert.equal(callFor("showToast").args[0], "Mission Inspector on");
    resetEnvironment();
    applyMissionWindowToggleEffects("coverage");
    assert.equal(calls.length, 0, "unrelated toggle entered mission-window effect phase");
}}


function testExtractedPayoutAudioToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedPayoutAudioToggleStatePaths)) {{
        resetEnvironment(); const before = pathValue(state, path);
        assert.equal(handlePayoutAudioToggle(feature), true); assert.notEqual(pathValue(state, path), before);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null); assert.equal(wasCalled("updateUI"), false);
    }}
    resetEnvironment(); const before = JSON.stringify(state);
    assert.equal(handlePayoutAudioToggle("unknown-payout-audio"), false); assert.equal(JSON.stringify(state), before);
    resetEnvironment(); state.missionLockAudio = false; handlePayoutAudioToggle("missionLockAudio"); assert.deepEqual(callFor("unlockPayoutAudio").args, [true]);
    resetEnvironment(); state.payoutFlash.soundEnabled = true; handlePayoutAudioToggle("payoutSound"); assert.equal(wasCalled("disposePayoutMediaAudio"), true);
    for (const [feature, message] of [["missionLockAudio","Mission tracking audio on"],["payoutSound","Theme audio off"],["payoutFlash","Emergency payout flash on"]]) {{
        resetEnvironment(); applyPayoutAudioToggleEffects(feature); assert.equal(callFor("showToast").args[0], message);
    }}
    resetEnvironment(); applyPayoutAudioToggleEffects("coverage"); assert.equal(calls.length, 0);
}}


function testExtractedMissionMonitoringToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedMissionMonitoringToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        assert.equal(handleMissionMonitoringToggle(feature), true, `${{feature}} was not handled directly`);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle ${{path}}`);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null);
        assert.equal(wasCalled("updateUI"), false);
    }}

    resetEnvironment();
    const unknownBefore = JSON.stringify(state);
    assert.equal(handleMissionMonitoringToggle("unknown-monitoring-toggle"), false);
    assert.equal(JSON.stringify(state), unknownBefore);
    assert.equal(calls.length, 0);

    resetEnvironment();
    state.missionSpawn.enabled = false;
    missionSpawnPrimeTimer = 73;
    missionSpawnArmed = true;
    knownMissionIds.add("existing");
    handleMissionMonitoringToggle("missionSpawn");
    assert.equal(state.missionSpawn.enabled, true);
    assert.equal(missionSpawnArmed, false);
    assert.equal(knownMissionIds.size, 0);
    assert.deepEqual(callFor("runtimeClearTimeout").args, [73]);
    assert.equal(wasCalled("primeMissionSpawnDetector"), true);

    resetEnvironment();
    state.missionSpawn.enabled = true;
    missionSpawnPrimeTimer = 74;
    missionSpawnArmed = true;
    knownMissionIds.add("existing");
    handleMissionMonitoringToggle("missionSpawn");
    assert.equal(state.missionSpawn.enabled, false);
    assert.equal(missionSpawnArmed, false);
    assert.equal(knownMissionIds.size, 0);
    assert.deepEqual(callFor("runtimeClearTimeout").args, [74]);
    assert.equal(wasCalled("primeMissionSpawnDetector"), false);

    resetEnvironment();
    applyMissionMonitoringToggleEffects("missionSpawn");
    assert.equal(callFor("showToast").args[0], "New mission animation on");

    resetEnvironment();
    applyMissionMonitoringToggleEffects("stuckDetector");
    assert.equal(callFor("showToast").args[0], "Stuck detector on · 20 min");

    resetEnvironment();
    applyMissionMonitoringToggleEffects("coverage");
    assert.equal(calls.length, 0);
}}


function testExtractedInterfaceShellToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedInterfaceShellToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        assert.equal(handleInterfaceShellToggle(feature), true, `${{feature}} was not handled directly`);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle ${{path}}`);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null);
        assert.equal(wasCalled("updateUI"), false);
    }}

    resetEnvironment();
    const unknownBefore = JSON.stringify(state);
    assert.equal(handleInterfaceShellToggle("unknown-interface-shell-toggle"), false);
    assert.equal(JSON.stringify(state), unknownBefore);
    assert.equal(calls.length, 0);
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
    state.economyMode = true;
    toggleFeature("vehicles");
    const vehicleUpdateIndex = calls.findIndex(call => call.name === "updateUI");
    const vehicleSyncIndex = calls.findIndex(call => call.name === "synchroniseVehicleMarkerClasses");
    const vehicleEconomyIndex = calls.findIndex(call => call.name === "scheduleEconomyLayerSync");
    const vehicleReconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
    assert.ok(vehicleUpdateIndex >= 0 && vehicleUpdateIndex < vehicleSyncIndex, "vehicle synchronization must remain after UI synchronization");
    assert.ok(vehicleSyncIndex < vehicleEconomyIndex, "economy synchronization must remain after vehicle class synchronization");
    assert.ok(vehicleEconomyIndex < vehicleReconcileIndex, "feature reconciliation must remain after map visibility effects");

    resetEnvironment();
    state.economyMode = true;
    toggleFeature("buildings");
    const buildingUpdateIndex = calls.findIndex(call => call.name === "updateUI");
    const buildingSyncIndex = calls.findIndex(call => call.name === "synchronisePersonalBuildingVisibility");
    const buildingEconomyIndex = calls.findIndex(call => call.name === "scheduleEconomyLayerSync");
    const buildingReconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
    assert.ok(buildingUpdateIndex >= 0 && buildingUpdateIndex < buildingSyncIndex, "building synchronization must remain after UI synchronization");
    assert.ok(buildingSyncIndex < buildingEconomyIndex, "economy synchronization must remain after building visibility synchronization");
    assert.ok(buildingEconomyIndex < buildingReconcileIndex, "feature reconciliation must remain after map visibility effects");


    const missionEffects = [
        ["missionValue", "installMissionValueWindows"],
        ["customVehicleBadges", "installCustomVehicleBadges"],
        ["missionInspector", "showToast"],
    ];
    for (const [feature, effectName] of missionEffects) {{
        resetEnvironment();
        state[feature] = false;
        toggleFeature(feature);
        const updateIndex = calls.findIndex(call => call.name === "updateUI");
        const reconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
        const effectIndex = calls.findIndex(call => call.name === effectName);
        assert.ok(updateIndex >= 0 && updateIndex < reconcileIndex, `${{feature}} reconciliation must remain after UI update`);
        assert.ok(reconcileIndex < effectIndex, `${{feature}} effect must remain after feature reconciliation`);
    }}



    for (const [feature, prepare, immediate] of [
        ["missionLockAudio", () => {{ state.missionLockAudio = false; }}, "unlockPayoutAudio"],
        ["payoutSound", () => {{ state.payoutFlash.soundEnabled = false; }}, "unlockPayoutAudio"],
        ["payoutFlash", () => {{ state.payoutFlash.enabled = false; }}, null],
    ]) {{
        resetEnvironment(); prepare(); toggleFeature(feature);
        const update = calls.findIndex(call => call.name === "updateUI");
        const reconcile = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
        const toast = calls.findIndex(call => call.name === "showToast");
        assert.ok(update >= 0 && update < reconcile && reconcile < toast);
        if (immediate) assert.ok(calls.findIndex(call => call.name === immediate) < update);
    }}


    resetEnvironment();
    state.missionSpawn.enabled = false;
    missionSpawnPrimeTimer = 75;
    missionSpawnArmed = true;
    knownMissionIds.add("existing");
    toggleFeature("missionSpawn");
    const spawnClearIndex = calls.findIndex(call => call.name === "runtimeClearTimeout");
    const spawnPrimeIndex = calls.findIndex(call => call.name === "primeMissionSpawnDetector");
    const spawnUpdateIndex = calls.findIndex(call => call.name === "updateUI");
    const spawnReconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
    const spawnToastIndex = calls.findIndex(call => call.name === "showToast");
    assert.ok(spawnClearIndex >= 0 && spawnClearIndex < spawnUpdateIndex);
    assert.ok(spawnPrimeIndex >= 0 && spawnPrimeIndex < spawnUpdateIndex);
    assert.ok(spawnUpdateIndex < spawnReconcileIndex && spawnReconcileIndex < spawnToastIndex);
    assert.equal(knownMissionIds.size, 0);

    resetEnvironment();
    toggleFeature("stuckDetector");
    const stuckUpdateIndex = calls.findIndex(call => call.name === "updateUI");
    const stuckReconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
    const stuckToastIndex = calls.findIndex(call => call.name === "showToast");
    assert.ok(stuckUpdateIndex >= 0 && stuckUpdateIndex < stuckReconcileIndex);
    assert.ok(stuckReconcileIndex < stuckToastIndex);


    for (const [feature, path] of Object.entries(fixtures.extractedInterfaceShellToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        toggleFeature(feature);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle through the main router`);
        assert.equal(localStorage.getItem(SCRIPT.storageState) !== null, true, `${{feature}} did not persist state`);
        const updateIndex = calls.findIndex(call => call.name === "updateUI");
        const reconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
        assert.ok(updateIndex >= 0 && updateIndex < reconcileIndex, `${{feature}} reconciliation must remain after UI update`);
        if (feature === "clean") {{
            const closeIndex = calls.findIndex(call => call.name === "closePanel");
            assert.ok(closeIndex >= 0 && closeIndex < updateIndex, "Clean Mode must close the panel before UI synchronization");
        }}
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

async function testDiscordFinancialSettingRoutesDirectly() {{
    resetEnvironment();
    const beforeUnknown = JSON.stringify(state);
    assert.equal(handleDiscordFinancialSettingChange({{ value: "ignored" }}, "unknown-setting"), false);
    assert.equal(JSON.stringify(state), beforeUnknown, "unknown settings must not mutate state");

    const apply = (setting, value) => assert.equal(handleDiscordFinancialSettingChange({{ value }}, setting), true, `${{setting}} must be handled`);
    apply("discord-webhook", "https://discord.com/api/webhooks/1/token");
    assert.equal(gmStorage.get("webhook"), "https://discord.com/api/webhooks/1/token");
    apply("discord-name", `  ${{"A".repeat(100)}}  `);
    assert.equal(state.discordReport.webhookName.length, 80);
    apply("discord-top-categories", "8");
    assert.equal(state.discordReport.topCategories, 8);
    apply("discord-period", "last30");
    assert.equal(state.discordReport.period, "last30");
    apply("discord-custom-start", "2026-07-01");
    apply("discord-custom-end", "2026-07-21");
    assert.equal(state.discordReport.customStart, "2026-07-01");
    assert.equal(state.discordReport.customEnd, "2026-07-21");
    apply("discord-comparison", "false");
    apply("discord-chart", "false");
    apply("discord-report-mode", "executive");
    apply("discord-risk", "false");
    apply("discord-forecast", "false");
    assert.equal(state.discordReport.includeComparison, false);
    assert.equal(state.discordReport.includeChart, false);
    assert.equal(state.discordReport.reportMode, "executive");
    assert.equal(state.discordReport.includeRisk, false);
    assert.equal(state.discordReport.includeForecast, false);

    apply("finance-vault-enabled", "false");
    apply("finance-vault-retention", "365");
    clearCalls();
    apply("finance-rule-feed", "false");
    await Promise.resolve();
    await Promise.resolve();
    assert.equal(state.financialVault.enabled, false);
    assert.equal(state.financialVault.retentionDays, 365);
    assert.equal(state.financialVault.ruleFeedEnabled, false);
    assert.equal(wasCalled("refreshFinancialIntelligenceFeeds"), true);
    assert.equal(wasCalled("updateUI"), true);
    assert.equal(wasCalled("renderFinanceVaultStatus"), true);
}}


function testDeviceLayoutSettingRoutesDirectly() {{
    resetEnvironment();
    const unknownBefore = JSON.stringify(state);
    assert.equal(handleDeviceLayoutSettingChange({{ value: "ignored" }}, "unknown-layout-setting"), false);
    assert.equal(JSON.stringify(state), unknownBefore);
    assert.equal(calls.length, 0);

    resetEnvironment();
    state.tabletMode = "on";
    assert.equal(handleDeviceLayoutSettingChange({{ value: "on" }}, "mobile-mode"), true);
    assert.equal(state.mobileMode, "on");
    assert.equal(state.tabletMode, "off");
    assert.equal(activeDeviceLayout, "mobile");
    assert.equal(JSON.parse(localStorage.getItem(SCRIPT.storageState)).mobileMode, "on");
    assert.deepEqual(calls.map(call => call.name), ["applyRootAttributes", "refreshTabletModeUi", "fitControlToMap", "positionPanelOverlay", "showToast"]);
    assert.equal(callFor("showToast").args[0], "iOS Mobile Mode active");

    resetEnvironment();
    state.mobileMode = "on";
    assert.equal(handleDeviceLayoutSettingChange({{ value: "on" }}, "tablet-mode"), true);
    assert.equal(state.tabletMode, "on");
    assert.equal(state.mobileMode, "off");
    assert.equal(activeDeviceLayout, "tablet");
    assert.equal(callFor("showToast").args[0], "Tablet Mode active");

    resetEnvironment();
    state.mobileMode = "on";
    applyRootAttributes();
    clearCalls();
    assert.equal(handleDeviceLayoutSettingChange({{ value: "invalid" }}, "mobile-mode"), true);
    assert.equal(state.mobileMode, "auto");
    assert.equal(activeDeviceLayout, "desktop");
    assert.deepEqual(calls.map(call => call.name), ["applyRootAttributes", "refreshTabletModeUi", "clearTabletPanelSizing", "clearTabletDockSizing", "fitControlToMap", "positionPanelOverlay", "showToast"]);
    assert.equal(callFor("showToast").args[0], "Desktop layout active");
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
    testExtractedMapVisibilityToggleContracts();
    testExtractedMissionWindowToggleContracts();
    testExtractedPayoutAudioToggleContracts();
    testExtractedMissionMonitoringToggleContracts();
    testExtractedInterfaceShellToggleContracts();
    await testToggleContracts();
    await testActionContracts();
    await testDiscordFinancialSettingRoutesDirectly();
    testDeviceLayoutSettingRoutesDirectly();
    await testSettingContracts();
    console.log(`Settings/UI contract passed: direct normalization, defaults, migrations, import rollback, extracted map/visibility toggle parity, extracted mission-window toggle parity, extracted payout/audio toggle parity, extracted mission-monitoring toggle parity, extracted interface-shell toggle parity, extracted financial route parity, extracted device-layout setting parity, ${{fixtures.toggleRoutes.length}} toggles, ${{fixtures.actions.length}} actions and ${{fixtures.settings.length}} settings.`);
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
