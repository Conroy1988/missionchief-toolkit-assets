#!/usr/bin/env python3
"""Static contract for the native three-station Building quick-filter popup."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")


def require(*tokens: str) -> None:
    for token in tokens:
        assert token in SOURCE, f"Native Building quick-filter contract missing {token!r}"


metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", SOURCE)
runtime = re.search(r"version:\s*'([^']+)'", SOURCE)
assert metadata and runtime and metadata.group(1) == runtime.group(1)

require(
    "buildingQuickFilterId: 'mc-map-command-toolkit-building-quick-filter'",
    "const NATIVE_VISIBILITY_FEATURES = Object.freeze(['myMissions', 'allianceMissions', 'vehicles']);",
    "const NATIVE_BUILDING_QUICK_FILTERS = Object.freeze({",
    "label: 'Ambulance Stations'",
    "labels: Object.freeze(['Ambulance Station', 'Ambulance Stations'])",
    "label: 'Fire Stations'",
    "labels: Object.freeze(['Fire Station', 'Fire Stations'])",
    "label: 'Police Stations'",
    "labels: Object.freeze(['Police Station', 'Police Stations'])",
    "function nativeBuildingQuickFilterControlMatches(",
    "control.closest?.('.building-filter')",
    "function findNativeBuildingQuickFilterControl(",
    "function nativeBuildingQuickFilterSnapshot(",
    "function nativeBuildingQuickFilterMarkup(",
    "function ensureNativeBuildingQuickFilterPopover(",
    "function positionNativeBuildingQuickFilterPopover(",
    "function activateNativeBuildingQuickFilter(",
    "dispatchNativeVisibilityControl(snapshot.control, desired)",
    "toolkitAnalyticsRecordFeature('buildingVisibility', 'native_building_filter')",
    "Direct MissionChief controls · no Toolkit layer scan",
    "Need another building type? Use MissionChief’s own Filters menu.",
    "function handleNativeBuildingQuickFilterKeyboard(",
    "if (insideBuildingPopover) {",
    "const closeButton = closestEventTarget(event, '[data-native-building-close]');",
    "activateNativeBuildingQuickFilter(filterButton.dataset.nativeBuildingFilter)",
    "if (nativeVisibilityWriteInProgress) return;",
    "keyboardBindingFromEvent(event) === 'Shift+4'",
    "Open Ambulance, Fire and Police station filters powered directly by MissionChief. Shortcut: 4",
    "aria-controls', SCRIPT.buildingQuickFilterId",
    "#${SCRIPT.buildingQuickFilterId}[hidden]",
    "max-height:calc(100dvh - 16px)",
    "overflow-wrap:anywhere",
    "@media (max-width:360px)",
    "SCRIPT.buildingQuickFilterId,",
    "data-mcms-native-building-filter-open",
    "delete profileVisibility.buildings;",
    "root?.removeAttribute('data-mcms-show-buildings');",
    "if (feature === 'buildings') return false;",
    "Building layers stay entirely under MissionChief's native filter service.",
    "buildingVisibility: { scope: 'both', mode: 'all', selectedTypeIds: [] }",
)

descriptor_block = SOURCE[
    SOURCE.index("const NATIVE_BUILDING_QUICK_FILTERS") : SOURCE.index("const NATIVE_VISIBILITY_FILTERS")
]
assert len(re.findall(r"^\s{8}(ambulance|fire|police): Object\.freeze", descriptor_block, re.MULTILINE)) == 3
assert SOURCE.count('data-native-building-filter="${escapeHtml(key)}"') == 1
assert SOURCE.count("runtimeRegisterTask('building-visibility'") == 0
popup_runtime_block = SOURCE[
    SOURCE.index("function ensureNativeBuildingQuickFilterPopover(") : SOURCE.index("function writeNativeVisibilityState(")
]
assert "runtimeListen(" not in popup_runtime_block, "Popup must reuse the command shell's delegated listeners"
assert "runtimeSetTimeout(" not in popup_runtime_block, "Popup must add no managed timer call sites"

for retired in (
    "function synchroniseBuildingVisibilitySelector(",
    "function releaseBuildingVisibilitySelector(",
    "function buildingVisibilityLayerAllowed(",
    "function renderBuildingVisibilitySelector(",
    "data-building-visibility-selector",
    "data-building-visibility-search",
    "data-setting=\"building-visibility-type\"",
    "data-action=\"building-type-only\"",
    "data-action=\"building-types-all\"",
    "data-action=\"building-types-none\"",
    "data-action=\"building-types-restore\"",
    "mcms-building-launcher",
    "mcms-building-selector",
    "filterId: 'user_buildings'",
    'html[data-mcms-show-buildings="false"]',
    "buildingVisibility: state.buildingVisibility",
):
    assert retired not in SOURCE, f"Retired building-visibility path remains: {retired!r}"

assert "state.visibility.buildings" not in SOURCE
assert "settings.buildingVisibility && typeof settings.buildingVisibility" not in SOURCE

print(f"Native Building quick-filter static contract passed for Toolkit {metadata.group(1)}.")
