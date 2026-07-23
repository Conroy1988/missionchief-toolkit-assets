#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
ROOT_USER = ROOT / "MissionChief_Map_Command_Toolkit.user.js"
ROOT_TXT = ROOT / "MissionChief_Map_Command_Toolkit.txt"
CHANGELOG = ROOT / "CHANGELOG.md"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def replace_exact(text: str, old: str, new: str, label: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{label}: expected {count}, found {actual}")
    return text.replace(old, new, count)

source = SOURCE.read_text(encoding="utf-8")
old_source_lines = len(source.splitlines())

source = replace_exact(
    source,
    "// @version      5.0.0",
    "// @version      5.0.1",
    "metadata version",
)
source = replace_exact(
    source,
    "version: '5.0.0',",
    "version: '5.0.1',",
    "runtime version",
)

old_schedule = '''    function scheduleOperationalSuiteScan(delay = 0) {
        if (runtime.destroyed) return;
        runtimeClearTimeout(operationalSuiteScanTimer);
        operationalSuiteScanTimer = runtimeSetTimeout(() => {
            operationalSuiteScanTimer = null;
            scanOperationalSuiteShell();
        }, Math.max(0, Number(delay) || 0));
    }
'''
new_schedule = '''    function scheduleOperationalSuiteScan(delay = 0) {
        if (runtime.destroyed) return;
        runtimeClearTimeout(operationalSuiteScanTimer);
        operationalSuiteScanTimer = runtimeSetTimeout(() => {
            operationalSuiteScanTimer = null;
            try {
                scanOperationalSuiteShell();
            } catch (error) {
                console.error(`[${SCRIPT.name}] Operational suite scan failed without blocking the Toolkit menu.`, error);
            }
        }, Math.max(0, Number(delay) || 0));
    }
'''
source = replace_exact(source, old_schedule, new_schedule, "operational scan fail-open")

old_install = '''    function installOperationalSuiteShell() {
        if (operationalSuiteInstalled) {
            if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
            return;
        }
        operationalSuiteInstalled = true;
        runtime.operationalSuite = Object.freeze({
            baseline: OPERATIONAL_SUITE_LSSM_BASELINE,
            settingsVersion: OPERATIONAL_SUITE_SETTINGS_VERSION,
            phase: 'operational-suite',
            schedule: scheduleOperationalSuiteScan,
            contextCount: () => operationalSuiteContexts.size
        });
        runtimeOnCleanup(() => {
            runtimeClearTimeout(operationalSuiteScanTimer);
            operationalSuiteScanTimer = null;
            clearOperationalSuiteContexts();
            if (runtime.operationalSuite?.phase === 'operational-suite') delete runtime.operationalSuite;
        });
        if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
    }
'''
new_install = '''    function installOperationalSuiteShell() {
        if (operationalSuiteInstalled) {
            if (operationalSuiteEnabled() && operationalStartupComplete) scheduleOperationalSuiteScan(0);
            return;
        }
        operationalSuiteInstalled = true;
        runtime.operationalSuite = Object.freeze({
            baseline: OPERATIONAL_SUITE_LSSM_BASELINE,
            settingsVersion: OPERATIONAL_SUITE_SETTINGS_VERSION,
            phase: 'operational-suite',
            schedule: scheduleOperationalSuiteScan,
            contextCount: () => operationalSuiteContexts.size
        });
        runtimeOnCleanup(() => {
            runtimeClearTimeout(operationalSuiteScanTimer);
            operationalSuiteScanTimer = null;
            clearOperationalSuiteContexts();
            if (runtime.operationalSuite?.phase === 'operational-suite') delete runtime.operationalSuite;
        });
        if (operationalSuiteEnabled() && operationalStartupComplete) scheduleOperationalSuiteScan(0);
    }
'''
source = replace_exact(source, old_install, new_install, "operational shell deferred scan")

old_ready = '''                scheduleMarkerStateSync(0, false);
                scheduleDeferredOperationalStartup();
                scheduleVersionStatusCheck(VERSION_STATUS.bootDelayMs, false);
'''
new_ready = '''                scheduleMarkerStateSync(0, false);
                scheduleDeferredOperationalStartup();
                if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
                scheduleVersionStatusCheck(VERSION_STATUS.bootDelayMs, false);
'''
source = replace_exact(source, old_ready, new_ready, "post-menu operational scan")

old_boot = '''        installCreditsUpdateHook();
        observeCreditValue();
        installOperationalSuiteShell();
        installCustomVehicleBadges();
        startBootAttemptCoordinator(bootPerformanceStartedAt);
'''
new_boot = '''        installCreditsUpdateHook();
        observeCreditValue();
        startBootAttemptCoordinator(bootPerformanceStartedAt);
        try {
            installOperationalSuiteShell();
        } catch (error) {
            console.error(`[${SCRIPT.name}] Operational suite shell failed; core Toolkit menu startup continues.`, error);
        }
        installCustomVehicleBadges();
'''
source = replace_exact(source, old_boot, new_boot, "core UI before operational shell")

for path in (SOURCE, ROOT_USER, ROOT_TXT):
    path.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
anchor = "## [Unreleased]\n"
notes = '''
## [5.0.1] - 2026-07-23

### Emergency menu recovery
- Restored the Toolkit launcher and settings menu for users upgrading from v4.20.37 to v5.0.0.
- Made core UI startup fail-open so an operational-suite initialisation or scan error cannot prevent the map command bar from mounting.
- Deferred the first operational DOM scan until after `ensureUi()` has created the launcher.
- Isolated operational scan failures with explicit diagnostics while preserving the rest of the Toolkit runtime.

### Compatibility
- No settings reset is required. Existing v5.0.0 operational-window preferences are retained.
- Enhanced Requirements, Extended Call Window, Extended Call List and Enhanced Transport Requests remain available after the core launcher mounts.

'''
if "## [5.0.1] - 2026-07-23" not in changelog:
    changelog = replace_exact(changelog, anchor, anchor + notes, "changelog unreleased anchor")
CHANGELOG.write_text(changelog, encoding="utf-8")

CONTRACT.write_text('''#!/usr/bin/env python3
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
''', encoding="utf-8")

validator = VALIDATOR.read_text(encoding="utf-8")
validator = replace_exact(
    validator,
    'ISSUE378_OPERATIONAL_FEATURE_RUNTIME = ROOT / ".github" / "scripts" / "test_issue378_operational_feature_runtime.js"\n',
    'ISSUE378_OPERATIONAL_FEATURE_RUNTIME = ROOT / ".github" / "scripts" / "test_issue378_operational_feature_runtime.js"\nISSUE447_MENU_BOOT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"\n',
    "validator contract constant",
)
validator = replace_exact(
    validator,
    '''        if issue378_feature_runtime.returncode != 0:
            fail("Issue #378 operational feature runtime fixtures failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
''',
    '''        if issue378_feature_runtime.returncode != 0:
            fail("Issue #378 operational feature runtime fixtures failed")

        issue447_menu_boot = subprocess.run(
            [sys.executable, str(ISSUE447_MENU_BOOT_CONTRACT)],
            cwd=ROOT,
        )
        if issue447_menu_boot.returncode != 0:
            fail("Issue #447 menu boot fail-open contract failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
''',
    "validator contract execution",
)
VALIDATOR.write_text(validator, encoding="utf-8")

fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
new_source_lines = len(source.splitlines())
delta = new_source_lines - old_source_lines
fixture["candidateVersion"] = "5.0.1"
entries = fixture.setdefault("approvedNonStyleChanges", [])
entries.append({"issue": 447, "phase": "menu-boot-fail-open-hotfix", "lines": delta})
fixture["approvedNonStyleSourceLines"] = int(fixture.get("approvedNonStyleSourceLines", 0)) + delta
fixture["expectedSourceLines"] = int(fixture.get("expectedSourceLines", old_source_lines)) + delta
HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

subprocess.run(["python3", str(CONTRACT)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, env=ENV, check=True)

for path in (ROOT / ".github" / "diagnostics").glob("v5-*.txt"):
    path.unlink(missing_ok=True)

print(f"Prepared v5.0.1 menu boot hotfix; source line delta {delta:+d}.")
