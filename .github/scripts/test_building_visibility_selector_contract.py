#!/usr/bin/env python3
"""Static contract for the type-aware Building Visibility Selector."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")


def require(*tokens: str) -> None:
    for token in tokens:
        assert token in SOURCE, f"Building Visibility Selector contract missing {token!r}"


metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", SOURCE)
runtime = re.search(r"version:\s*'([^']+)'", SOURCE)
assert metadata and runtime and metadata.group(1) == runtime.group(1)

require(
    "const BUILDING_VISIBILITY_SCOPES = Object.freeze(['own', 'alliance', 'both']);",
    "const BUILDING_VISIBILITY_MODES = Object.freeze(['all', 'selected']);",
    "buildingVisibility: { scope: 'both', mode: 'all', selectedTypeIds: [] }",
    "buildingVisibility: { ...base.buildingVisibility, ...(parsed.buildingVisibility || {}) }",
    "merged.buildingVisibility.selectedTypeIds = Array.from(new Set",
    "function buildingVisibilityTypeId(",
    "function buildingVisibilityOwnerScope(",
    "function buildingVisibilityLayerAllowed(",
    "function buildingVisibilityTypeEntries(",
    "function synchroniseBuildingVisibilitySelector(",
    "function releaseBuildingVisibilitySelector(",
    "function nativeBuildingVisibilityDesired(",
    "service.getFilterLayerByBuildingParams",
    "buildingVisibilityManagedTargets.set(target",
    "runtimeRegisterTask('building-visibility'",
    "intervalResolver: () => buildingVisibilityFilterIsCustom() ? BUILDING_VISIBILITY_RECHECK_MS : 60 * 1000",
    "data-building-visibility-selector",
    "data-building-visibility-search",
    "data-setting=\"building-visibility-type\"",
    "data-action=\"building-type-only\"",
    "data-action=\"building-types-all\"",
    "data-action=\"building-types-none\"",
    "data-action=\"building-types-restore\"",
    "data-action=\"building-scope\"",
    "Choose building types &amp; ownership",
    "Shift+4 opens the type selector",
    "keyboardBindingFromEvent(event) === 'Shift+4'",
    "buildingVisibility: state.buildingVisibility",
    "settings.buildingVisibility && typeof settings.buildingVisibility === 'object'",
    "data-mcms-building-scope",
    "data-mcms-building-mode",
    "html[data-mcms-mobile-active=\"true\"] #${SCRIPT.panelId} .mcms-building-only-btn",
)

assert SOURCE.count("runtimeRegisterTask('building-visibility'") == 1
assert SOURCE.count("data-action=\"toggle-building-selector\"") >= 2
assert "setInterval(" not in SOURCE[SOURCE.index("function synchroniseBuildingVisibilitySelector("):SOURCE.index("function getVehicleMarkerIcons(")]
assert "(state.buildingVisibility?.scope || 'both') !== 'alliance'" in SOURCE
assert "state.visibility.buildings = false;\n        commitBuildingVisibilitySelection('All buildings hidden · selection saved');" in SOURCE

print(f"Building Visibility Selector static contract passed for Toolkit {metadata.group(1)}.")
