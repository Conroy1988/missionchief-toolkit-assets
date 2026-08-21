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
assert version_tuple(metadata.group(1)) >= (10, 13, 3)

for token in (
    "const NATIVE_VISIBILITY_RETRY_DELAYS_MS = Object.freeze([0, 180, 700, 1800, 4200]);",
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
    "function adoptNativeVisibilityFeature(",
    "if (toolkitFreshInstallAtLoad) {",
    "nativeVisibilityPendingFeatures.has(feature)",
    "serviceState.map.fire?.(wanted ? 'overlayadd' : 'overlayremove'",
    "function installNativeVisibilityBridge(",
    "runBootIntegration('native map visibility bridge', installNativeVisibilityBridge);",
    "for (const delay of NATIVE_VISIBILITY_RETRY_DELAYS_MS) scheduleNativeVisibilityReconcile(delay);",
    "void runtimeDelay(delayMs).then(completed => {",
    "const nativeVisibilityFeature = handleNativeVisibilityControlEvent(event);",
    "adoptNativeVisibilityFeature(nativeVisibilityFeature);",
    "if (mutations.some(mutationTouchesNativeVisibilityControls)) scheduleNativeVisibilityReconcile(0);",
    "return feature === 'vehicles' || !nativeVisibilityBoundFeatures.has(feature);",
    "if (feature === 'vehicles') synchroniseVehicleMarkerClasses();",
    "const nativeDesired = feature === 'vehicles' ? true : Boolean(desired);",
    "if (feature === 'vehicles' && snapshot.value === true) continue;",
    "const { missionMarkerIcons, personalMissionIcons, allianceMissionIcons } = getMissionIconsByOwnership();",
    "const missionId = missionIdFromMarker(marker);",
    "const ownerId = missionOwnerId(marker, missionId);",
    "if (missionMarkerIcons.has(icon)) continue;",
    "vehicleMarkerIcons.delete(icon);",
    "return { missionMarkerIcons, personalMissionIcons, allianceMissionIcons };",
    "if (nativeVisibilityFallbackNeeded('buildings') && !state.visibility.buildings) synchronisePersonalBuildingVisibility();",
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

assert SOURCE.count("runtimeRegisterTask('building-visibility'") == 1
assert "runtimeRegisterTask('native-visibility'" not in SOURCE
assert "setInterval(" not in SOURCE[SOURCE.index("function installNativeVisibilityBridge("):SOURCE.index("function getVehicleMarkerLayers(")]
assert "runtimeListen(" not in SOURCE[SOURCE.index("function installNativeVisibilityBridge("):SOURCE.index("function getVehicleMarkerLayers(")]
assert "runtimeSetTimeout(" not in SOURCE[SOURCE.index("function scheduleNativeVisibilityReconcile("):SOURCE.index("function getVehicleMarkerLayers(")]

print(f"Native map visibility bridge contract passed for Toolkit {metadata.group(1)}.")
