#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
text = SOURCE.read_text(encoding="utf-8")
boot_start = text.index("    function boot()")
boot_end = text.index("    function scheduleBoot()", boot_start)
boot = text[boot_start:boot_end]
coordinator_start = text.index("    function startBootAttemptCoordinator")
coordinator_end = text.index("    function registerBootMaintenanceTasks", coordinator_start)
coordinator = text[coordinator_start:coordinator_end]
schedule_start = text.index("    function scheduleOperationalSuiteScan")
schedule_end = text.index("    function installOperationalSuiteShell", schedule_start)
schedule = text[schedule_start:schedule_end]
install_start = text.index("    function installOperationalSuiteShell")
install_end = text.index("    // Issue #378 retained UK operational capability catalogue", install_start)
install = text[install_start:install_end]
assert boot.index("startBootAttemptCoordinator(bootPerformanceStartedAt);") < boot.index("installOperationalSuiteShell();")
assert "try {\n            installOperationalSuiteShell();" in boot
assert "core Toolkit menu startup continues" in boot
assert "if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);" in coordinator
assert coordinator.index("const ready = ensureUi();") < coordinator.index("if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);")
assert "try {\n                scanOperationalSuiteShell();" in schedule
assert "failed without blocking the Toolkit menu" in schedule
assert install.count("operationalStartupComplete") == 2
assert "if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);" not in install
print("Issue #447 menu boot fail-open contract passed.")
