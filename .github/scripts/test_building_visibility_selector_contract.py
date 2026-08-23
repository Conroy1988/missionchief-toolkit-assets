#!/usr/bin/env python3
"""Static contract for the complete popularity-ranked UK Building filter popup."""

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
    "const NATIVE_BUILDING_QUICK_FILTER_ORDER = Object.freeze([",
    "const NATIVE_BUILDING_QUICK_FILTERS = Object.freeze({",
    "defineNativeBuildingQuickFilter('Ambulance Stations'",
    "defineNativeBuildingQuickFilter('Police Stations'",
    "defineNativeBuildingQuickFilter('Fire Stations'",
    "defineNativeBuildingQuickFilter('Hospitals'",
    "defineNativeBuildingQuickFilter('Small Ambulance Stations'",
    "defineNativeBuildingQuickFilter('Search and Rescue HQs'",
    "defineNativeBuildingQuickFilter('Coastguard Rescue Stations'",
    "defineNativeBuildingQuickFilter('Home Response Locations'",
    "defineNativeBuildingQuickFilter('GP Surgeries'",
    "defineNativeBuildingQuickFilter('Recovery Centres'",
    "defineNativeBuildingQuickFilter('Building Complexes'",
    "function nativeBuildingQuickFilterTranslatedLabels(",
    "function nativeBuildingQuickFilterControlLabels(",
    "function nativeBuildingQuickFilterTokenMatches(",
    "function nativeBuildingQuickFilterControlMatches(",
    "control.closest?.('.building-filter')",
    "function nativeBuildingQuickFilterControls(",
    "function findNativeBuildingQuickFilterControl(",
    "function nativeBuildingQuickFilterSnapshot(",
    "function nativeBuildingQuickFilterMarkup(",
    "function ensureNativeBuildingQuickFilterPopover(",
    "function positionNativeBuildingQuickFilterPopover(",
    "function activateNativeBuildingQuickFilter(",
    "dispatchNativeVisibilityControl(snapshot.control, desired)",
    "toolkitAnalyticsRecordFeature('buildingVisibility', 'native_building_filter')",
    "Direct MissionChief controls · UK popularity order",
    "Most popular",
    "All other buildings · popularity order",
    "Every UK building type is covered.",
    "function handleNativeBuildingQuickFilterKeyboard(",
    "if (insideBuildingPopover) {",
    "const closeButton = closestEventTarget(event, '[data-native-building-close]');",
    "activateNativeBuildingQuickFilter(filterButton.dataset.nativeBuildingFilter)",
    "if (nativeVisibilityWriteInProgress) return;",
    "keyboardBindingFromEvent(event) === 'Shift+4'",
    "Open all UK building filters in popularity order, powered directly by MissionChief. Shortcut: 4",
    "aria-controls', SCRIPT.buildingQuickFilterId",
    "#${SCRIPT.buildingQuickFilterId}[hidden]",
    "max-height:calc(100dvh - 16px)",
    "mcms-native-building-section-title",
    "mcms-native-building-featured",
    "mcms-native-building-tone-rescue",
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
order_block = SOURCE[
    SOURCE.index("const NATIVE_BUILDING_QUICK_FILTER_ORDER") : SOURCE.index("const NATIVE_BUILDING_QUICK_FILTERS")
]
order = re.findall(r"^\s{8}'([a-z_]+)'", order_block, re.MULTILINE)
descriptors = re.findall(r"^\s{8}([a-z_]+): defineNativeBuildingQuickFilter", descriptor_block, re.MULTILINE)
assert len(order) == 30, f"Expected 30 native filter rows, found {len(order)}"
assert order[:3] == ["ambulance", "police", "fire"], "The user-approved leading trio or order changed"
assert descriptors == order, "Descriptor declaration order must exactly match the popularity order"

type_groups = re.findall(
    r"^\s{8}[a-z_]+: defineNativeBuildingQuickFilter\(.*?, \[([0-9, ]+)\], '[a-z]+'\),?$",
    descriptor_block,
    re.MULTILINE,
)
covered_type_ids = sorted(int(value) for group in type_groups for value in group.split(", "))
assert covered_type_ids == [0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
assert SOURCE.count('data-native-building-filter="${escapeHtml(key)}"') == 1
assert SOURCE.count('data-popularity-rank="${rank}"') == 1
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
assert "Need another building type? Use MissionChief’s own Filters menu." not in SOURCE
assert "Open Ambulance, Fire and Police station filters" not in SOURCE

print(f"Native Building quick-filter static contract passed for Toolkit {metadata.group(1)}.")
