#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
text = SOURCE.read_text(encoding="utf-8")


def section(start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


helper = section("    function runBootIntegration", "    function startBootAttemptCoordinator")
coordinator = section("    function startBootAttemptCoordinator", "    function registerBootMaintenanceTasks")
boot = section("    function boot()", "    function scheduleBoot()")
schedule = section("    function scheduleBoot()", "\n\n    if (document.readyState")
map_discovery = section("    function getLargestLeafletMap()", "    function getViewportMetrics()")
alliance = section("    function installAllianceBuildingsPageOptimisation()", "    function connectMainMutationObserver()")

assert "try {" in helper
assert "failed without blocking the Toolkit launcher" in helper
assert coordinator.index("const ready = Boolean(runBootIntegration('core UI mount', ensureUi));") < coordinator.index("installMissionMarkerAddHook")
assert "runtimeSetTimeout(runBootAttempt, delay);" in coordinator
assert "runBootAttempt();" in coordinator
assert boot.index("startBootAttemptCoordinator(bootPerformanceStartedAt);") < boot.index("applyRootAttributes")
for integration in (
    "applyRootAttributes",
    "installMissionMarkerAddHook",
    "installRadioMessageHook",
    "installCreditsUpdateHook",
    "observeCreditValue",
    "installOperationalSuiteShell",
    "installCustomVehicleBadges",
):
    assert "runBootIntegration(" in boot and integration in boot
assert "runtimeRunWhenIdle(boot, STARTUP_IDLE_TIMEOUT_MS)" in schedule
assert "runtimeSetTimeout" in schedule
assert ".leaflet-container, #map, [data-leaflet-map]" in map_discovery
assert "target.closest?.(``)" not in text
assert "return isAllianceBuildingsPath() && !enabled;" in alliance
assert "return initiallyInContext && !enabled;" not in alliance
print("Issue #450 core launcher bootstrap contract passed.")
