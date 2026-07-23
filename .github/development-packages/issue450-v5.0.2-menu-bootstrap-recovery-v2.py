#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github" / "development-packages" / "issue450-v5.0.2-menu-bootstrap-recovery.py"
LEGACY_CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"

LEGACY_CONTRACT.write_text(r'''#!/usr/bin/env python3
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
assert coordinator.index("runBootIntegration('core UI mount', ensureUi);") < coordinator.index("installMissionMarkerAddHook")
assert "Boolean(document.getElementById(SCRIPT.controlId))" in coordinator
assert boot.index("startBootAttemptCoordinator(bootPerformanceStartedAt);") < boot.index("installOperationalSuiteShell")
assert "runBootIntegration('operational suite shell', installOperationalSuiteShell);" in boot
assert "scanOperationalSuiteShell();" in schedule
assert "failed without blocking the Toolkit menu" in schedule
assert install.count("operationalStartupComplete") == 2
assert "if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);" not in install
print("Issue #447 menu boot fail-open contract passed under the Issue #450 bootstrap architecture.")
''', encoding="utf-8")

try:
    runpy.run_path(str(ORIGINAL), run_name="__main__")
finally:
    ORIGINAL.unlink(missing_ok=True)
