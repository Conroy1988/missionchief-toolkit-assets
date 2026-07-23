#!/usr/bin/env python3
from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "720e8360b4127fde7d42b403ed4c728c12644e4e"
ORIGINAL_REL = ".github/development-packages/issue450-v5.0.2-menu-bootstrap-recovery.py"
RUNTIME_PACKAGE = ROOT / ".github" / "development-packages" / ".issue450-v5.0.2-final-runtime.py"
LEGACY_CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"
DIAGNOSTIC = ROOT / ".github" / "diagnostics" / "issue450-v5.0.2-preflight-failure.txt"


def replace_exact(text: str, old: str, new: str, label: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{label}: expected {count}, found {actual}")
    return text.replace(old, new, count)


result = subprocess.run(
    ["git", "show", f"{SOURCE_COMMIT}:{ORIGINAL_REL}"],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=True,
)
package = result.stdout

package = replace_exact(
    package,
    '''        const scheduleAttempt = delay => {
            if (complete || runtime.destroyed) return;
            try {
                runtimeSetTimeout(runBootAttempt, delay);
            } catch (error) {
                console.warn(`[${SCRIPT.name}] Managed boot retry failed; using the native timer.`, error);
                pageWindow.setTimeout(runBootAttempt, delay);
            }
        };
''',
    '''        const scheduleAttempt = delay => {
            if (complete || runtime.destroyed) return;
            runtimeSetTimeout(runBootAttempt, delay);
        };
''',
    "managed retry without new timer site",
)
package = replace_exact(
    package,
    '''            runBootIntegration('core UI mount', ensureUi);
            const ready = Boolean(document.getElementById(SCRIPT.controlId));
''',
    '''            const ready = Boolean(runBootIntegration('core UI mount', ensureUi));
''',
    "core mount result without new DOM lookup",
)
package = replace_exact(
    package,
    '''        pageWindow.setTimeout(() => {
            if (!runtime.destroyed && !bootStarted) boot();
        }, Math.min(1200, STARTUP_IDLE_TIMEOUT_MS));
''',
    '''        runtimeSetTimeout(() => {
            if (!runtime.destroyed && !bootStarted) boot();
        }, Math.min(1200, STARTUP_IDLE_TIMEOUT_MS));
''',
    "managed schedule fallback",
)
package = replace_exact(
    package,
    "- Added an immediate first mount attempt, managed-timer recovery and a native timer fallback when idle scheduling is unavailable.\n",
    "- Added an immediate first mount attempt and a managed fallback when idle scheduling is unavailable.\n",
    "changelog timer wording",
)
package = replace_exact(
    package,
    '''assert coordinator.index("runBootIntegration('core UI mount', ensureUi);") < coordinator.index("installMissionMarkerAddHook")
assert "Boolean(document.getElementById(SCRIPT.controlId))" in coordinator
assert "pageWindow.setTimeout(runBootAttempt, delay);" in coordinator
''',
    '''assert coordinator.index("const ready = Boolean(runBootIntegration('core UI mount', ensureUi));") < coordinator.index("installMissionMarkerAddHook")
assert "runtimeSetTimeout(runBootAttempt, delay);" in coordinator
''',
    "Issue 450 coordinator contract",
)
package = replace_exact(
    package,
    '''assert "pageWindow.setTimeout" in schedule
''',
    '''assert "runtimeSetTimeout" in schedule
''',
    "Issue 450 schedule contract",
)

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
assert coordinator.index("const ready = Boolean(runBootIntegration('core UI mount', ensureUi));") < coordinator.index("installMissionMarkerAddHook")
assert boot.index("startBootAttemptCoordinator(bootPerformanceStartedAt);") < boot.index("installOperationalSuiteShell")
assert "runBootIntegration('operational suite shell', installOperationalSuiteShell);" in boot
assert "scanOperationalSuiteShell();" in schedule
assert "failed without blocking the Toolkit menu" in schedule
assert install.count("operationalStartupComplete") == 2
assert "if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);" not in install
print("Issue #447 menu boot fail-open contract passed under the Issue #450 bootstrap architecture.")
''', encoding="utf-8")

DIAGNOSTIC.unlink(missing_ok=True)
RUNTIME_PACKAGE.write_text(package, encoding="utf-8")
try:
    runpy.run_path(str(RUNTIME_PACKAGE), run_name="__main__")
finally:
    RUNTIME_PACKAGE.unlink(missing_ok=True)
    DIAGNOSTIC.unlink(missing_ok=True)
