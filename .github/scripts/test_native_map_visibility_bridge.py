#!/usr/bin/env python3
"""Static contract for the generic MissionChief visibility bridge."""

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
assert metadata and runtime and metadata.group(1) == runtime.group(1)
assert version_tuple(metadata.group(1)) >= (10, 15, 2)

for token in (
    "const NATIVE_VISIBILITY_RETRY_DELAYS_MS = Object.freeze([0, 180, 700, 1800, 4200]);",
    "const NATIVE_VISIBILITY_FEATURES = Object.freeze(['myMissions', 'allianceMissions', 'vehicles']);",
    "const NATIVE_VEHICLE_SETTINGS_API_PATH = '/api/settings';",
    "const NATIVE_VEHICLE_SETTINGS_PATH_PREFIX = '/settings';",
    "const NATIVE_VEHICLE_SETTINGS_SEED_PATHS = Object.freeze(['/settings/index', '/settings']);",
    "myMissions: Object.freeze({",
    "filterId: 'user_missions'",
    "allianceMissions: Object.freeze({",
    "filterId: 'alliance_missions'",
    "vehicles: Object.freeze({",
    "aliases: Object.freeze(['vehicles', 'vehicle_markers', 'show_vehicle', 'show_vehicles'])",
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
    "const nativeVisibilityFeature = handleNativeVisibilityControlEvent(event);",
    "adoptNativeVisibilityFeature(nativeVisibilityFeature);",
    "if (mutations.some(mutationTouchesNativeVisibilityControls)) scheduleNativeVisibilityReconcile(0);",
    "async function fetchNativeVehicleSetting()",
    "async function fetchNativeVehicleSettingsDocument()",
    "function prepareNativeVehicleSettingsSubmission(",
    "async function submitNativeVehicleSetting(",
    "async function verifyNativeVehicleSetting(",
    "function applyNativeVehicleRuntimeSetting(",
    "function mirrorNativeVehicleSetting(",
    "async function toggleNativeVehicleVisibility()",
    "delete profileVisibility.vehicles;",
    "delete profileVisibility.buildings;",
    "Toggle MissionChief’s Show vehicles on map setting. Shortcut: 3",
    "function nativeBuildingQuickFilterDescriptor(",
):
    assert token in SOURCE, token

generic_block = SOURCE[
    SOURCE.index("const NATIVE_VISIBILITY_FILTERS") : SOURCE.index("const MAP_DISCOVERY_RETRY_MS")
]
assert "user_buildings" not in generic_block
assert "buildings: Object.freeze" not in generic_block
assert "document.getElementsByTagName('label')" not in SOURCE
assert "data-mcms-show-vehicles" not in SOURCE
assert "runtimeRegisterTask('native-visibility'" not in SOURCE
assert "runtimeRegisterTask('building-visibility'" not in SOURCE
assert "function nativeBuildingVisibilityDesired(" not in SOURCE
assert "if (feature === 'buildings') synchroniseBuildingVisibilitySelector();" not in SOURCE
assert "const nativeDesired = feature === 'vehicles' ? true : Boolean(desired);" not in SOURCE
assert SOURCE.count("const vehiclesAllowedByNativeSetting = nativeVehicleSnapshot.available ? nativeVehicleSnapshot.value : true;") == 2

bridge_slice = SOURCE[SOURCE.index("function installNativeVisibilityBridge(") : SOURCE.index("function getVehicleMarkerLayers(")]
assert "setInterval(" not in bridge_slice
assert "runtimeListen(" not in bridge_slice

print(f"Native map visibility bridge contract passed for Toolkit {metadata.group(1)}.")
