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
schedule = section("    function scheduleOperationalSuiteScan", "    function installOperationalSuiteShell")
install = section("    function installOperationalSuiteShell", "    // Issue #378 retained UK operational capability catalogue")

assert "failed without blocking the Toolkit launcher" in helper
assert coordinator.index("const ready = Boolean(runBootIntegration('core UI mount', ensureUi));") < coordinator.index("installMissionMarkerAddHook")
assert boot.index("startBootAttemptCoordinator(bootPerformanceStartedAt);") < boot.index("installOperationalSuiteShell")
assert "runBootIntegration('operational suite shell', installOperationalSuiteShell);" in boot
assert "scanOperationalSuiteShell();" in schedule
assert "failed without blocking the Toolkit menu" in schedule
assert install.count("operationalStartupComplete") == 2
assert "if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);" not in install
print("Issue #447 menu boot fail-open contract passed under the Issue #450 bootstrap architecture.")
