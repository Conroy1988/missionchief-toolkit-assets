#!/usr/bin/env python3
"""Contract for the narrow alliance-building native-filter leak safeguard."""

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
current_version = metadata.group(1)
assert current_version == runtime.group(1)
assert version_tuple(current_version) >= (8, 0, 4)

for token in (
    "building_markers_params_cache_per_id",
    "pageWindow.map_filters_service",
    "service.getFilterLayerByBuildingParams",
    "function nativeAllianceBuildingLayerAllowed(",
    "function suppressLeakedAllianceBuildingLayer(",
    "function restoreEligibleAllianceBuildingLayer(",
    "function nativeAllianceBuildingFilterMayNeedEnforcement(",
    "function synchroniseNativeAllianceBuildingVisibility(",
    "function releaseNativeAllianceBuildingVisibility(",
    "map.on('overlayadd overlayremove', onNativeOverlayChange);",
    "map.on('moveend zoomend viewreset', onMapMove);",
    "if (nativeAllianceBuildingFilterMayNeedEnforcement()) synchroniseNativeAllianceBuildingVisibility();",
):
    assert token in SOURCE, token

assert "function synchroniseBuildingVisibilitySelector(" not in SOURCE
assert "function buildingVisibilityLayerAllowed(" not in SOURCE
assert "runtimeRegisterTask('building-visibility'" not in SOURCE
assert 'html[data-mcms-show-buildings="false"]' not in SOURCE
assert "state.visibility.buildings" not in SOURCE
assert "economyHiddenBuildingLayers" not in SOURCE
assert "mcms-marker-alliance-building" not in SOURCE


def visible(*, alliance: bool, native_filter_visible: bool, direct_on_map: bool) -> bool:
    if not alliance:
        return direct_on_map
    return direct_on_map and native_filter_visible


assert visible(alliance=True, native_filter_visible=False, direct_on_map=True) is False
assert visible(alliance=True, native_filter_visible=False, direct_on_map=False) is False
assert visible(alliance=True, native_filter_visible=True, direct_on_map=True) is True
assert visible(alliance=False, native_filter_visible=False, direct_on_map=True) is True

for dist in (ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js", ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"):
    assert dist.read_bytes() == SOURCE_PATH.read_bytes(), dist

print(f"Issue #536 narrow alliance-building native-filter safeguard passed for Toolkit {current_version}.")
