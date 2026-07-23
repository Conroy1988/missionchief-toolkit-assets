#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
ROOT_USER = ROOT / "MissionChief_Map_Command_Toolkit.user.js"
ROOT_TXT = ROOT / "MissionChief_Map_Command_Toolkit.txt"
CHANGELOG = ROOT / "CHANGELOG.md"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
CONTRACT = ROOT / ".github" / "scripts" / "test_issue450_core_launcher_bootstrap.py"
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
    "// @version      5.0.1",
    "// @version      5.0.2",
    "metadata version",
)
source = replace_exact(
    source,
    "version: '5.0.1',",
    "version: '5.0.2',",
    "runtime version",
)

old_map_discovery = '''    function getLargestLeafletMap() {
        const now = Date.now();
        if (cachedMapElement?.isConnected && now - cachedMapElementCheckedAt <= MAP_ELEMENT_CACHE_MS) return cachedMapElement;
        if (cachedMapElement?.isConnected && isVisible(cachedMapElement)) {
        cachedMapElementCheckedAt = now;
        return cachedMapElement;
        }
        const candidates = Array.from(document.querySelectorAll('.leaflet-container')).filter(isVisible);
        let largest = null;
        let largestArea = 0;
        for (const candidate of candidates) {
        const rect = candidate.getBoundingClientRect();
        const area = rect.width * rect.height;
        if (area > largestArea) {
            largest = candidate;
            largestArea = area;
        }
        }
        cachedMapElement = largest;
        cachedMapElementCheckedAt = now;
        return largest;
    }
'''
new_map_discovery = '''    function getLargestLeafletMap() {
        const now = Date.now();
        if (cachedMapElement?.isConnected && now - cachedMapElementCheckedAt <= MAP_ELEMENT_CACHE_MS) return cachedMapElement;
        if (cachedMapElement?.isConnected && isVisible(cachedMapElement)) {
        cachedMapElementCheckedAt = now;
        return cachedMapElement;
        }
        const candidates = Array.from(document.querySelectorAll('.leaflet-container, #map, [data-leaflet-map]')).filter(isVisible);
        let largest = null;
        let largestArea = 0;
        for (const candidate of candidates) {
        const rect = candidate.getBoundingClientRect();
        const area = rect.width * rect.height;
        if (area > largestArea) {
            largest = candidate;
            largestArea = area;
        }
        }
        cachedMapElement = largest;
        cachedMapElementCheckedAt = now;
        return largest;
    }
'''
source = replace_exact(source, old_map_discovery, new_map_discovery, "resilient map discovery")

old_empty_selector = '''                target.closest?.(`#${SCRIPT.majorIncidentFeedId}`) ||
                target.closest?.(`#${SCRIPT.missionInspectorId}`) ||
                target.closest?.(``)
'''
new_empty_selector = '''                target.closest?.(`#${SCRIPT.majorIncidentFeedId}`) ||
                target.closest?.(`#${SCRIPT.missionInspectorId}`)
'''
source = replace_exact(source, old_empty_selector, new_empty_selector, "empty closest selector removal")

source = replace_exact(
    source,
    "        return initiallyInContext && !enabled;\n",
    "        return isAllianceBuildingsPath() && !enabled;\n",
    "exact Alliance Buildings boot boundary",
)

old_coordinator = '''    function startBootAttemptCoordinator(bootPerformanceStartedAt) {
        let attempts = 0;
        const runBootAttempt = () => {
            attempts += 1;
            installMissionMarkerAddHook();
            installRadioMessageHook();
            installCreditsUpdateHook();
            observeCreditValue();
            const ready = ensureUi();
            const mapReady = Boolean(getLargestLeafletMap());
            if (ready && (mapReady || attempts >= 12)) {
                recordStartupMetric('coreUiReadyMs', bootPerformanceStartedAt, { bootAttempts: attempts });
                scheduleMarkerStateSync(0, false);
                scheduleDeferredOperationalStartup();
                if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
                scheduleVersionStatusCheck(VERSION_STATUS.bootDelayMs, false);
                runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);
                return;
            }
            if (attempts >= 90 || runtime.destroyed) return;
            const delay = attempts < 12 ? 350 : attempts < 30 ? 700 : 1400;
            runtimeSetTimeout(runBootAttempt, delay);
        };
        runtimeSetTimeout(runBootAttempt, 250);
    }
'''
new_coordinator = '''    function runBootIntegration(label, callback) {
        try {
            return callback();
        } catch (error) {
            console.warn(`[${SCRIPT.name}] ${label} failed without blocking the Toolkit launcher.`, error);
            return null;
        }
    }

    function startBootAttemptCoordinator(bootPerformanceStartedAt) {
        let attempts = 0;
        let complete = false;
        const scheduleAttempt = delay => {
            if (complete || runtime.destroyed) return;
            try {
                runtimeSetTimeout(runBootAttempt, delay);
            } catch (error) {
                console.warn(`[${SCRIPT.name}] Managed boot retry failed; using the native timer.`, error);
                pageWindow.setTimeout(runBootAttempt, delay);
            }
        };
        const runBootAttempt = () => {
            if (complete || runtime.destroyed) return;
            attempts += 1;
            runBootIntegration('core UI mount', ensureUi);
            const ready = Boolean(document.getElementById(SCRIPT.controlId));
            const mapReady = Boolean(runBootIntegration('map discovery', getLargestLeafletMap));
            runBootIntegration('mission marker hook', installMissionMarkerAddHook);
            runBootIntegration('radio message hook', installRadioMessageHook);
            runBootIntegration('credits update hook', installCreditsUpdateHook);
            runBootIntegration('credits observer', observeCreditValue);
            if (ready && (mapReady || attempts >= 12)) {
                complete = true;
                runBootIntegration('startup metric', () => recordStartupMetric('coreUiReadyMs', bootPerformanceStartedAt, { bootAttempts: attempts }));
                runBootIntegration('marker state sync', () => scheduleMarkerStateSync(0, false));
                runBootIntegration('deferred operational startup', scheduleDeferredOperationalStartup);
                runBootIntegration('operational suite scan', () => {
                    if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
                });
                runBootIntegration('version status check', () => scheduleVersionStatusCheck(VERSION_STATUS.bootDelayMs, false));
                runBootIntegration('main observer connection', () => {
                    runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);
                });
                return;
            }
            if (attempts >= 90) return;
            const delay = attempts < 12 ? 350 : attempts < 30 ? 700 : 1400;
            scheduleAttempt(delay);
        };
        runBootAttempt();
    }
'''
source = replace_exact(source, old_coordinator, new_coordinator, "independent launcher coordinator")

old_boot = '''    function boot() {
        if (runtime.destroyed || bootStarted) return;
        bootStarted = true;
        bootStartedAt = Date.now();
        const bootPerformanceStartedAt = startupClock();
        applyRootAttributes();
        if (installAllianceBuildingsPageOptimisation()) return;
        createCleanExit();
        if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
        installMissionMarkerAddHook();
        installRadioMessageHook();
        lastObservedCredits = readCurrentCreditTotal();
        installCreditsUpdateHook();
        observeCreditValue();
        startBootAttemptCoordinator(bootPerformanceStartedAt);
        try {
            installOperationalSuiteShell();
        } catch (error) {
            console.error(`[${SCRIPT.name}] Operational suite shell failed; core Toolkit menu startup continues.`, error);
        }
        installCustomVehicleBadges();
        const observer = runtimeTrackObserver(new MutationObserver(mutations => {
'''
new_boot = '''    function boot() {
        if (runtime.destroyed || bootStarted) return;
        bootStarted = true;
        bootStartedAt = Date.now();
        const bootPerformanceStartedAt = startupClock();
        const allianceBuildingsOnly = isAllianceBuildingsPath() && state.allianceBuildingsMap === false;
        if (!allianceBuildingsOnly) startBootAttemptCoordinator(bootPerformanceStartedAt);
        runBootIntegration('root attributes', applyRootAttributes);
        runBootIntegration('Alliance Buildings optimisation', installAllianceBuildingsPageOptimisation);
        if (allianceBuildingsOnly) return;
        runBootIntegration('clean-mode exit', createCleanExit);
        if (state.autoLoadAllVehicles) runBootIntegration('auto-load all vehicles', installAutoLoadAllVehicles);
        runBootIntegration('mission marker hook', installMissionMarkerAddHook);
        runBootIntegration('radio message hook', installRadioMessageHook);
        lastObservedCredits = runBootIntegration('initial credit total', readCurrentCreditTotal);
        runBootIntegration('credits update hook', installCreditsUpdateHook);
        runBootIntegration('credits observer', observeCreditValue);
        runBootIntegration('operational suite shell', installOperationalSuiteShell);
        runBootIntegration('custom vehicle badges', installCustomVehicleBadges);
        const observer = runtimeTrackObserver(new MutationObserver(mutations => {
'''
source = replace_exact(source, old_boot, new_boot, "launcher-first boot")

old_schedule_boot = '''    function scheduleBoot() {
        if (runtime.destroyed || bootStarted) return;
        runtimeRunWhenIdle(boot, STARTUP_IDLE_TIMEOUT_MS);
    }
'''
new_schedule_boot = '''    function scheduleBoot() {
        if (runtime.destroyed || bootStarted) return;
        runBootIntegration('idle boot scheduling', () => runtimeRunWhenIdle(boot, STARTUP_IDLE_TIMEOUT_MS));
        pageWindow.setTimeout(() => {
            if (!runtime.destroyed && !bootStarted) boot();
        }, Math.min(1200, STARTUP_IDLE_TIMEOUT_MS));
    }
'''
source = replace_exact(source, old_schedule_boot, new_schedule_boot, "native boot fallback")

for path in (SOURCE, ROOT_USER, ROOT_TXT):
    path.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
anchor = "## [Unreleased]\n"
notes = '''
## [5.0.2] - 2026-07-23

### Emergency launcher recovery
- Rebuilt startup so the core Toolkit launcher mounts before optional MissionChief hooks and operational integrations.
- Isolated every pre-launch DOM/API integration so one changing MissionChief surface cannot terminate the launcher retry loop.
- Added an immediate first mount attempt, managed-timer recovery and a native timer fallback when idle scheduling is unavailable.
- Expanded map discovery to support the live `#map` container when the Leaflet class is delayed or changed.

### Reliability corrections
- Removed an empty `closest()` selector left by Matrix retirement that could throw during DOM mutation handling.
- Restricted Alliance Buildings boot suppression to the exact Alliance Buildings route, preventing normal map pages being misclassified.
- Existing Toolkit and operational-window settings remain intact; no reset is required.

'''
if "## [5.0.2] - 2026-07-23" not in changelog:
    changelog = replace_exact(changelog, anchor, anchor + notes, "changelog unreleased anchor")
CHANGELOG.write_text(changelog, encoding="utf-8")

CONTRACT.write_text(r'''#!/usr/bin/env python3
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
assert coordinator.index("runBootIntegration('core UI mount', ensureUi);") < coordinator.index("installMissionMarkerAddHook")
assert "Boolean(document.getElementById(SCRIPT.controlId))" in coordinator
assert "pageWindow.setTimeout(runBootAttempt, delay);" in coordinator
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
assert "pageWindow.setTimeout" in schedule
assert ".leaflet-container, #map, [data-leaflet-map]" in map_discovery
assert "target.closest?.(``)" not in text
assert "return isAllianceBuildingsPath() && !enabled;" in alliance
assert "return initiallyInContext && !enabled;" not in alliance
print("Issue #450 core launcher bootstrap contract passed.")
''', encoding="utf-8")

validator = VALIDATOR.read_text(encoding="utf-8")
validator = replace_exact(
    validator,
    'ISSUE447_MENU_BOOT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"\n',
    'ISSUE447_MENU_BOOT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"\nISSUE450_CORE_BOOTSTRAP_CONTRACT = ROOT / ".github" / "scripts" / "test_issue450_core_launcher_bootstrap.py"\n',
    "validator contract constant",
)
validator = replace_exact(
    validator,
    '''        if issue447_menu_boot.returncode != 0:
            fail("Issue #447 menu boot fail-open contract failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
''',
    '''        if issue447_menu_boot.returncode != 0:
            fail("Issue #447 menu boot fail-open contract failed")

        issue450_core_bootstrap = subprocess.run(
            [sys.executable, str(ISSUE450_CORE_BOOTSTRAP_CONTRACT)],
            cwd=ROOT,
        )
        if issue450_core_bootstrap.returncode != 0:
            fail("Issue #450 core launcher bootstrap contract failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
''',
    "validator contract execution",
)
VALIDATOR.write_text(validator, encoding="utf-8")

fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
new_source_lines = len(source.splitlines())
delta = new_source_lines - old_source_lines
fixture["candidateVersion"] = "5.0.2"
entries = fixture.setdefault("approvedNonStyleChanges", [])
entries.append({"issue": 450, "phase": "core-launcher-bootstrap-recovery", "lines": delta})
fixture["approvedNonStyleSourceLines"] = int(fixture.get("approvedNonStyleSourceLines", 0)) + delta
fixture["expectedSourceLines"] = int(fixture.get("expectedSourceLines", old_source_lines)) + delta
HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

subprocess.run(["python3", str(CONTRACT)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, env=ENV, check=True)

print(f"Prepared v5.0.2 launcher recovery; source line delta {delta:+d}.")
