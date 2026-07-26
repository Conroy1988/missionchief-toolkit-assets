#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
SOURCE = SOURCE_PATH.read_text(encoding='utf-8')
EXPECTED = 'e8673da8a40db757f7a1b1165092e1a22f87581de84ebb9c2bc78ce5e4ceb101'

assert hashlib.sha256(SOURCE.encode()).hexdigest() == EXPECTED
assert re.search(r'(?m)^//\s*@version\s+8\.0\.4$', SOURCE)
for token in (
    'building_markers_params_cache_per_id',
    'pageWindow.map_filters_service',
    'service.getFilterLayerByBuildingParams',
    'function nativeAllianceBuildingLayerAllowed(',
    'function suppressLeakedAllianceBuildingLayer(',
    'function synchroniseNativeAllianceBuildingVisibility(',
    'const allowedByNativeFilter = nativeAllianceBuildingLayerAllowed(map, layer);',
    "map.on('overlayadd overlayremove', onNativeOverlayChange);",
    "map.on('moveend zoomend viewreset', onMapMove);",
    'if (!isPersonalBuilding) suppressLeakedAllianceBuildingLayer(map, layer);',
):
    assert token in SOURCE, token
assert "data-mcms-show-buildings" in SOURCE
assert 'mcms-marker-personal-building' in SOURCE
assert 'mcms-marker-alliance-building' not in SOURCE
assert SOURCE.count("runtimeRegisterTask('building-visibility'") == 1
assert "intervalResolver: () => !state.visibility.buildings ? BUILDING_VISIBILITY_RECHECK_MS : 60 * 1000" in SOURCE

def visible(*, alliance: bool, native_filter_visible: bool, direct_on_map: bool) -> bool:
    if not alliance:
        return direct_on_map
    return direct_on_map and native_filter_visible

assert visible(alliance=True, native_filter_visible=False, direct_on_map=True) is False
assert visible(alliance=True, native_filter_visible=False, direct_on_map=False) is False
assert visible(alliance=True, native_filter_visible=True, direct_on_map=True) is True
assert visible(alliance=False, native_filter_visible=False, direct_on_map=True) is True
for dist in (ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js', ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt'):
    assert dist.read_bytes() == SOURCE_PATH.read_bytes(), dist
print('Issue #536 alliance-building native-filter persistence contract passed.')
