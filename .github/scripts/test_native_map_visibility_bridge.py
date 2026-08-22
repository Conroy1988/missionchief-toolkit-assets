#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")


def version_tuple(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value)
    assert match, value
    return tuple(map(int, match.groups()))


metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", SOURCE)
runtime = re.search(r"version:\s*'([^']+)'", SOURCE)
assert metadata and runtime
assert metadata.group(1) == runtime.group(1)
assert version_tuple(metadata.group(1)) >= (10, 15, 2)

for token in (
    "const NATIVE_VISIBILITY_RETRY_DELAYS_MS = Object.freeze([0, 180, 700, 1800, 4200]);",
    "const NATIVE_VEHICLE_SETTINGS_API_PATH = '/api/settings';",
    "const NATIVE_VEHICLE_SETTINGS_PATH_PREFIX = '/settings';",
    "const NATIVE_VEHICLE_SETTINGS_SEED_PATHS = Object.freeze(['/settings/index', '/settings']);",
    "const NATIVE_VEHICLE_SETTINGS_DISCOVERY_LIMIT = 12;",
    "myMissions: Object.freeze({",
    "filterId: 'user_missions'",
    "allianceMissions: Object.freeze({",
    "filterId: 'alliance_missions'",
    "vehicles: Object.freeze({",
    "aliases: Object.freeze(['vehicles', 'vehicle_markers', 'show_vehicle', 'show_vehicles'])",
    "buildings: Object.freeze({",
    "filterId: 'user_buildings'",
    "nativeVisibility: { migratedFeatures: [] }",
    "function findNativeVisibilityControl(",
    "function nativeVisibilityServiceState(",
    "pageWindow.xy_map_filters_service",
    "pageWindow.map_filters_service",
    "function writeNativeVisibilityState(",
    "if (feature === 'vehicles') return { handled: false, verified: false, source: 'native-settings-form' };",
    "function adoptNativeVisibilityFeature(",
    "nativeVisibilityPendingFeatures.has(feature)",
    "serviceState.map.fire?.(wanted ? 'overlayadd' : 'overlayremove'",
    "function installNativeVisibilityBridge(",
    "runBootIntegration('native map visibility bridge', installNativeVisibilityBridge);",
    "for (const delay of NATIVE_VISIBILITY_RETRY_DELAYS_MS) scheduleNativeVisibilityReconcile(delay);",
    "void runtimeDelay(delayMs).then(completed => {",
    "const nativeVisibilityFeature = handleNativeVisibilityControlEvent(event);",
    "adoptNativeVisibilityFeature(nativeVisibilityFeature);",
    "if (mutations.some(mutationTouchesNativeVisibilityControls)) scheduleNativeVisibilityReconcile(0);",
    "if (feature === 'vehicles') return false;",
    "const result = writeNativeVisibilityState(feature, Boolean(desired));",
    "if (toolkitFreshInstallAtLoad || feature === 'vehicles') {",
    "async function fetchNativeVehicleSetting()",
    "typeof payload.show_vehicle !== 'boolean'",
    "function nativeVehicleSettingsPathAllowed(",
    "function nativeVehicleSettingsControls(",
    "function nativeVehicleSettingsCandidateUrls(",
    "async function fetchNativeVehicleSettingsDocument(",
    "nativeVehicleSettingsCandidateUrls(settingsDocument, finalUrl.href)",
    "MissionChief did not expose its global Show vehicles on map form.",
    "input[type=\"checkbox\"][name]",
    "settingName === 'show_vehicle' || /(?:\\[|\\.)show_vehicle\\]?$/u.test(settingName)",
    "function prepareNativeVehicleSettingsSubmission(",
    "Boolean(checkbox.checked) !== expectedCurrent",
    "source.hash",
    "const body = new FormData(form);",
    "body.get('authenticity_token')",
    "'X-CSRF-Token': formToken || metaToken",
    "'X-Requested-With': 'XMLHttpRequest'",
    "async function submitNativeVehicleSetting(",
    "async function verifyNativeVehicleSetting(",
    "function applyNativeVehicleRuntimeSetting(",
    "pageWindow.loadVehiclesOnTheMove?.call(pageWindow);",
    "pageWindow.vehicleArrive?.call(pageWindow, marker);",
    "pageWindow.deregisterVehicleAnim?.call(pageWindow, index);",
    "const missionMarkers = new Set(getMissionMarkerLayers().filter(Boolean));",
    "const isMissionMarker = marker => missionMarkers.has(marker)",
    "function mirrorNativeVehicleSetting(",
    "async function toggleNativeVehicleVisibility()",
    "const snapshot = await fetchNativeVehicleSetting();",
    "const desired = !snapshot.value;",
    "const verified = await submitNativeVehicleSetting(desired, snapshot.value);",
    "showToast('MissionChief vehicle setting unavailable · no change made');",
    "showToast(verified.value ? 'MissionChief vehicles on' : 'MissionChief vehicles off');",
    "if (feature === 'vehicles') {\n            void toggleNativeVehicleVisibility();",
    "delete profileVisibility.vehicles;",
    "if (feature !== 'vehicles') applyNativeVisibilityPreference(feature, feature === 'buildings' ? nativeBuildingVisibilityDesired() : state.visibility[feature]);",
    "Toggle MissionChief’s Show vehicles on map setting. Shortcut: 3",
    "const { missionMarkerIcons, personalMissionIcons, allianceMissionIcons } = getMissionIconsByOwnership();",
    "const missionId = missionIdFromMarker(marker);",
    "const ownerId = missionOwnerId(marker, missionId);",
    "if (missionMarkerIcons.has(icon)) continue;",
    "vehicleMarkerIcons.delete(icon);",
    "return { missionMarkerIcons, personalMissionIcons, allianceMissionIcons };",
    "function nativeBuildingVisibilityDesired()",
    "if (feature === 'buildings') synchroniseBuildingVisibilitySelector();",
):
    assert token in SOURCE, token

buildings_block = re.search(
    r"buildings:\s*Object\.freeze\(\{(?P<body>.*?)\n\s*\}\)\n\s*\}\);",
    SOURCE,
    re.DOTALL,
)
assert buildings_block
assert "user_buildings" in buildings_block.group("body")
assert "alliance_buildings" not in buildings_block.group("body")
assert "document.getElementsByTagName('label')" not in SOURCE
assert "data-mcms-show-vehicles" not in SOURCE
assert "const nativeDesired = feature === 'vehicles' ? true : Boolean(desired);" not in SOURCE
assert "NATIVE_VEHICLE_SETTINGS_BUILDING_PATH_PREFIX" not in SOURCE
assert "Number(payload.leitstelle_building_id)" not in SOURCE
assert "snapshot.dispatchCenterId" not in SOURCE
assert "if (feature === 'vehicles' && snapshot.value === true) continue;" not in SOURCE
assert "feature === 'vehicles' || !nativeVisibilityBoundFeatures.has(feature)" not in SOURCE
assert "const visible = state.visibility.vehicles &&" not in SOURCE
assert SOURCE.count("const vehiclesAllowedByNativeSetting = nativeVehicleSnapshot.available ? nativeVehicleSnapshot.value : true;") == 2

assert SOURCE.count("runtimeRegisterTask('building-visibility'") == 1
assert "runtimeRegisterTask('native-visibility'" not in SOURCE
assert "setInterval(" not in SOURCE[SOURCE.index("function installNativeVisibilityBridge("):SOURCE.index("function getVehicleMarkerLayers(")]
assert "runtimeListen(" not in SOURCE[SOURCE.index("function installNativeVisibilityBridge("):SOURCE.index("function getVehicleMarkerLayers(")]
assert "runtimeSetTimeout(" not in SOURCE[SOURCE.index("function scheduleNativeVisibilityReconcile("):SOURCE.index("function getVehicleMarkerLayers(")]

print(f"Native map visibility bridge contract passed for Toolkit {metadata.group(1)}.")
