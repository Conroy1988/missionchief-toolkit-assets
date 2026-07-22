#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CANONICAL = (
    SOURCE,
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
)
TEST = ROOT / ".github" / "scripts" / "test_issue378_operational_suite_shell.py"
HEADROOM_FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
HEADROOM_TEST = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"

source = SOURCE.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


source = replace_once(
    source,
    """    const missionRequirementsRecords = new Map();
    let customVehicleBadgeScanTimer = null;
""",
    """    const missionRequirementsRecords = new Map();
    let operationalSuiteScanTimer = null;
    let operationalSuiteInstalled = false;
    let operationalSuiteRevision = 0;
    const operationalSuiteContexts = new Map();
    let customVehicleBadgeScanTimer = null;
""",
    "Issue #378 runtime records",
)

settings_shell = r'''    const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;
    const OPERATIONAL_SUITE_LSSM_BASELINE = Object.freeze({
        repository: 'LSSM-V.4',
        branch: 'dev',
        commit: '88e41646e59a7d620624f90f1d9a0a62320c2775'
    });

    function defaultOperationalWindowState(legacyMatrixEnabled = true) {
        return {
            schemaVersion: OPERATIONAL_SUITE_SETTINGS_VERSION,
            enabled: false,
            phase: 'shell',
            requirements: {
                enabled: legacyMatrixEnabled !== false,
                calcMaxStaff: false,
                hoverTip: true,
                viewMode: 'table',
                overlay: false,
                minified: false,
                pushRight: false,
                sort: 'requirement',
                sortDir: 'asc',
                drag: { active: false, top: 60, left: null, offset: { x: 0, y: 0 } }
            },
            callWindow: {
                enabled: false,
                generationDate: true,
                yellowBorderHours: 0,
                redBorder: false,
                patientSummary: true,
                collapsiblePatients: false,
                collapsiblePatientsMinPatients: 7,
                arrCounter: false,
                arrCounterAsBadge: false,
                arrClickHighlight: false,
                arrClickHighlightColor: '#008000',
                arrClickHighlightWidth: 2,
                arrCounterResetSelection: false,
                arrMatchHighlight: false,
                arrMatchHighlightAllWords: false,
                arrTime: false,
                arrSpecs: false,
                alarmTime: false,
                stickyHeader: false,
                loadMoreVehiclesInHeader: false,
                hideVehicleList: false,
                centerMap: false,
                stagingAreaSelectedCounter: true,
                vehicleTypeInList: false,
                remainingPatientTime: true,
                vehicleCounter: false,
                vehicleCounterColor: 'info',
                vehicleListPermanentSearch: false,
                playerCounter: false,
                playerCounterColor: 'danger',
                selectedVehicleCounter: false,
                selectedVehicleCounterVehicleTypes: [],
                arrSearch: false,
                arrSearchDissolveCategories: false,
                arrSearchCompactResults: false,
                arrSearchSelectOnEnter: false,
                arrSearchClearOnEnter: false,
                arrSearchAutoFocus: false,
                arrSearchDropdown: false,
                arrSearchCloseDropdownOnSelect: false,
                moreReleasePatientButtons: false,
                tailoredTabs: [],
                missionKeywords: [],
                alarmIcons: [],
                arrCategoryColors: []
            },
            missionList: {
                enabled: false,
                remainingTime: false,
                remainingTimeGreenOnly: true,
                remainingPatientTime: false,
                remainingPumpingTime: false,
                starrableMissions: false,
                starredMissions: [],
                averageCredits: true,
                collapsibleMissions: false,
                collapsibleMissionsAllButton: true,
                collapsedMissions: [],
                allMissionsCollapsed: false,
                shareMissions: false,
                shareMissionTypes: ['', 'sicherheitswache'],
                shareMissionsMinCredits: 0,
                shareMissionsButtonColor: 'success',
                sortMissions: false,
                sortMissionsType: '',
                sortMissionsDirection: '',
                sortMissionsButtonColor: 'default',
                sortMissionsInMissionWindow: true,
                sortMissionsInMissionWindowChecked: false,
                sortMissionsOrder: {},
                currentPatients: false,
                hideZeroCurrentPatients: true,
                currentPatientsInTooltips: false,
                currentPrisoners: false,
                hideZeroCurrentPrisoners: true,
                currentPrisonersInTooltips: false,
                fixedEventInfo: false,
                eventMissions: []
            },
            transport: {
                enabled: false,
                autoClickSuccessButtons: true,
                autoOpenTransportRequest: false
            },
            migration: {
                legacyMatrixEnabled: legacyMatrixEnabled !== false,
                matrixPreferenceCaptured: true,
                matrixRetired: false
            }
        };
    }

    function operationalSuiteBoolean(value, fallback = false) {
        return value === undefined || value === null ? Boolean(fallback) : Boolean(value);
    }

    function operationalSuiteArray(value, fallback = []) {
        return Array.isArray(value) ? value.slice() : fallback.slice();
    }

    function normaliseOperationalWindowState(value, legacyMatrixEnabled = true) {
        const base = defaultOperationalWindowState(legacyMatrixEnabled);
        const parsed = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
        const requirements = parsed.requirements && typeof parsed.requirements === 'object' ? parsed.requirements : {};
        const callWindow = parsed.callWindow && typeof parsed.callWindow === 'object' ? parsed.callWindow : {};
        const missionList = parsed.missionList && typeof parsed.missionList === 'object' ? parsed.missionList : {};
        const transport = parsed.transport && typeof parsed.transport === 'object' ? parsed.transport : {};
        const migration = parsed.migration && typeof parsed.migration === 'object' ? parsed.migration : {};
        const merged = {
            ...base,
            ...parsed,
            schemaVersion: OPERATIONAL_SUITE_SETTINGS_VERSION,
            phase: 'shell',
            requirements: { ...base.requirements, ...requirements },
            callWindow: { ...base.callWindow, ...callWindow },
            missionList: { ...base.missionList, ...missionList },
            transport: { ...base.transport, ...transport },
            migration: { ...base.migration, ...migration }
        };
        merged.enabled = operationalSuiteBoolean(parsed.enabled, false);
        merged.requirements.enabled = operationalSuiteBoolean(requirements.enabled, legacyMatrixEnabled !== false);
        merged.requirements.calcMaxStaff = operationalSuiteBoolean(requirements.calcMaxStaff, false);
        merged.requirements.hoverTip = operationalSuiteBoolean(requirements.hoverTip, true);
        merged.requirements.viewMode = ['table', 'text'].includes(String(requirements.viewMode)) ? String(requirements.viewMode) : 'table';
        merged.requirements.overlay = operationalSuiteBoolean(requirements.overlay, false);
        merged.requirements.minified = operationalSuiteBoolean(requirements.minified, false);
        merged.requirements.pushRight = operationalSuiteBoolean(requirements.pushRight, false);
        merged.requirements.sort = ['requirement', 'missing', 'driving', 'total', 'selected'].includes(String(requirements.sort)) ? String(requirements.sort) : 'requirement';
        merged.requirements.sortDir = String(requirements.sortDir) === 'desc' ? 'desc' : 'asc';
        merged.requirements.drag = {
            ...base.requirements.drag,
            ...(requirements.drag && typeof requirements.drag === 'object' ? requirements.drag : {}),
            offset: {
                ...base.requirements.drag.offset,
                ...(requirements.drag?.offset && typeof requirements.drag.offset === 'object' ? requirements.drag.offset : {})
            }
        };
        const callWindowBooleanKeys = [
            'enabled', 'generationDate', 'redBorder', 'patientSummary', 'collapsiblePatients',
            'arrCounter', 'arrCounterAsBadge', 'arrClickHighlight', 'arrCounterResetSelection',
            'arrMatchHighlight', 'arrMatchHighlightAllWords', 'arrTime', 'arrSpecs', 'alarmTime',
            'stickyHeader', 'loadMoreVehiclesInHeader', 'hideVehicleList', 'centerMap',
            'stagingAreaSelectedCounter', 'vehicleTypeInList', 'remainingPatientTime',
            'vehicleCounter', 'vehicleListPermanentSearch', 'playerCounter', 'selectedVehicleCounter',
            'arrSearch', 'arrSearchDissolveCategories', 'arrSearchCompactResults',
            'arrSearchSelectOnEnter', 'arrSearchClearOnEnter', 'arrSearchAutoFocus',
            'arrSearchDropdown', 'arrSearchCloseDropdownOnSelect', 'moreReleasePatientButtons'
        ];
        for (const key of callWindowBooleanKeys) merged.callWindow[key] = operationalSuiteBoolean(callWindow[key], base.callWindow[key]);
        merged.callWindow.yellowBorderHours = Math.max(0, Math.min(48, Number(callWindow.yellowBorderHours ?? base.callWindow.yellowBorderHours) || 0));
        merged.callWindow.collapsiblePatientsMinPatients = Math.max(0, Math.round(Number(callWindow.collapsiblePatientsMinPatients ?? base.callWindow.collapsiblePatientsMinPatients) || 7));
        merged.callWindow.arrClickHighlightColor = /^#[0-9a-f]{6}$/iu.test(String(callWindow.arrClickHighlightColor || '')) ? String(callWindow.arrClickHighlightColor) : '#008000';
        merged.callWindow.arrClickHighlightWidth = Math.max(1, Math.min(12, Number(callWindow.arrClickHighlightWidth ?? 2) || 2));
        merged.callWindow.vehicleCounterColor = ['success', 'warning', 'danger', 'primary', 'info', 'default'].includes(String(callWindow.vehicleCounterColor)) ? String(callWindow.vehicleCounterColor) : 'info';
        merged.callWindow.playerCounterColor = ['success', 'warning', 'danger', 'primary', 'info', 'default'].includes(String(callWindow.playerCounterColor)) ? String(callWindow.playerCounterColor) : 'danger';
        for (const key of ['selectedVehicleCounterVehicleTypes', 'tailoredTabs', 'missionKeywords', 'alarmIcons', 'arrCategoryColors']) merged.callWindow[key] = operationalSuiteArray(callWindow[key], base.callWindow[key]);
        const missionListBooleanKeys = [
            'enabled', 'remainingTime', 'remainingTimeGreenOnly', 'remainingPatientTime',
            'remainingPumpingTime', 'starrableMissions', 'averageCredits', 'collapsibleMissions',
            'collapsibleMissionsAllButton', 'allMissionsCollapsed', 'shareMissions', 'sortMissions',
            'sortMissionsInMissionWindow', 'sortMissionsInMissionWindowChecked', 'currentPatients',
            'hideZeroCurrentPatients', 'currentPatientsInTooltips', 'currentPrisoners',
            'hideZeroCurrentPrisoners', 'currentPrisonersInTooltips', 'fixedEventInfo'
        ];
        for (const key of missionListBooleanKeys) merged.missionList[key] = operationalSuiteBoolean(missionList[key], base.missionList[key]);
        for (const key of ['starredMissions', 'collapsedMissions', 'shareMissionTypes', 'eventMissions']) merged.missionList[key] = operationalSuiteArray(missionList[key], base.missionList[key]);
        merged.missionList.shareMissionsMinCredits = Math.max(0, Number(missionList.shareMissionsMinCredits ?? 0) || 0);
        merged.missionList.shareMissionsButtonColor = ['success', 'warning', 'danger', 'primary', 'info', 'default'].includes(String(missionList.shareMissionsButtonColor)) ? String(missionList.shareMissionsButtonColor) : 'success';
        merged.missionList.sortMissionsButtonColor = ['success', 'warning', 'danger', 'primary', 'info', 'default'].includes(String(missionList.sortMissionsButtonColor)) ? String(missionList.sortMissionsButtonColor) : 'default';
        merged.missionList.sortMissionsOrder = missionList.sortMissionsOrder && typeof missionList.sortMissionsOrder === 'object' && !Array.isArray(missionList.sortMissionsOrder) ? { ...missionList.sortMissionsOrder } : {};
        merged.transport.enabled = operationalSuiteBoolean(transport.enabled, false);
        merged.transport.autoClickSuccessButtons = operationalSuiteBoolean(transport.autoClickSuccessButtons, true);
        merged.transport.autoOpenTransportRequest = operationalSuiteBoolean(transport.autoOpenTransportRequest, false);
        merged.migration.legacyMatrixEnabled = operationalSuiteBoolean(migration.legacyMatrixEnabled, legacyMatrixEnabled !== false);
        merged.migration.matrixPreferenceCaptured = operationalSuiteBoolean(migration.matrixPreferenceCaptured, true);
        merged.migration.matrixRetired = operationalSuiteBoolean(migration.matrixRetired, false);
        return merged;
    }

'''

source = replace_once(
    source,
    """    let helpCenterReturnFocus = null;

    function defaultState() {
""",
    """    let helpCenterReturnFocus = null;

""" + settings_shell + """    function defaultState() {
""",
    "Issue #378 settings shell",
)

source = replace_once(
    source,
    """        missionRequirements: true,
        customVehicleBadges: true,
""",
    """        missionRequirements: true,
        operationalWindow: defaultOperationalWindowState(true),
        customVehicleBadges: true,
""",
    "Issue #378 default state",
)

source = replace_once(
    source,
    """        financialVault: { ...base.financialVault, ...(parsed.financialVault || {}) },
        autoNight: { ...base.autoNight, ...(parsed.autoNight || {}) },
""",
    """        financialVault: { ...base.financialVault, ...(parsed.financialVault || {}) },
        operationalWindow: normaliseOperationalWindowState(parsed.operationalWindow, parsed.missionRequirements !== false),
        autoNight: { ...base.autoNight, ...(parsed.autoNight || {}) },
""",
    "Issue #378 loaded-state merge",
)

source = replace_once(
    source,
    """        merged.missionRequirements = merged.missionRequirements !== false;
        merged.tabletMode = ['auto', 'on', 'off'].includes(String(merged.tabletMode)) ? String(merged.tabletMode) : 'auto';
""",
    """        merged.missionRequirements = merged.missionRequirements !== false;
        merged.operationalWindow = normaliseOperationalWindowState(merged.operationalWindow, merged.missionRequirements);
        merged.tabletMode = ['auto', 'on', 'off'].includes(String(merged.tabletMode)) ? String(merged.tabletMode) : 'auto';
""",
    "Issue #378 loaded-state normalisation",
)

runtime_shell = r'''    // Issue #378 LSSM operational-suite lifecycle shell.
    // This phase owns settings, context identity, scheduling and teardown only. It must not
    // render a second requirements surface while the legacy Matrix remains the stable runtime.
    function operationalSuiteEnabled() {
        return state.operationalWindow?.enabled === true;
    }

    function operationalSuiteDocumentContexts() {
        const contexts = [];
        const seen = new Set();
        for (const candidate of transportSweepDocumentContexts()) {
            const doc = candidate?.doc;
            if (!doc?.querySelector || seen.has(doc)) continue;
            seen.add(doc);
            contexts.push(doc);
        }
        return contexts;
    }

    function operationalSuiteDisposeContext(context) {
        if (!context) return;
        try { context.observer?.disconnect?.(); } catch (err) {}
        context.observer = null;
        context.root = null;
        if (context.doc) operationalSuiteContexts.delete(context.doc);
        context.doc = null;
    }

    function clearOperationalSuiteContexts() {
        for (const context of Array.from(operationalSuiteContexts.values())) operationalSuiteDisposeContext(context);
        operationalSuiteContexts.clear();
    }

    function operationalSuiteEnsureContext(doc) {
        if (!doc?.querySelector) return null;
        const existing = operationalSuiteContexts.get(doc);
        if (existing) {
            existing.root = doc.documentElement || doc.body || existing.root;
            existing.seenAt = Date.now();
            return existing;
        }
        const context = {
            doc,
            root: doc.documentElement || doc.body || null,
            observer: null,
            generation: 0,
            seenAt: Date.now(),
            baseline: OPERATIONAL_SUITE_LSSM_BASELINE.commit
        };
        operationalSuiteContexts.set(doc, context);
        return context;
    }

    function scanOperationalSuiteShell() {
        if (runtime.destroyed) return;
        if (!operationalSuiteEnabled()) {
            clearOperationalSuiteContexts();
            return;
        }
        const activeDocuments = new Set();
        for (const doc of operationalSuiteDocumentContexts()) {
            const context = operationalSuiteEnsureContext(doc);
            if (!context) continue;
            activeDocuments.add(doc);
            context.generation = ++operationalSuiteRevision;
        }
        for (const [doc, context] of Array.from(operationalSuiteContexts.entries())) {
            if (!activeDocuments.has(doc) || context.root?.isConnected === false) operationalSuiteDisposeContext(context);
        }
    }

    function scheduleOperationalSuiteScan(delay = 0) {
        if (runtime.destroyed) return;
        runtimeClearTimeout(operationalSuiteScanTimer);
        operationalSuiteScanTimer = runtimeSetTimeout(() => {
            operationalSuiteScanTimer = null;
            scanOperationalSuiteShell();
        }, Math.max(0, Number(delay) || 0));
    }

    function installOperationalSuiteShell() {
        if (operationalSuiteInstalled) {
            if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
            return;
        }
        operationalSuiteInstalled = true;
        runtime.operationalSuite = Object.freeze({
            baseline: OPERATIONAL_SUITE_LSSM_BASELINE,
            settingsVersion: OPERATIONAL_SUITE_SETTINGS_VERSION,
            phase: 'shell',
            schedule: scheduleOperationalSuiteScan,
            contextCount: () => operationalSuiteContexts.size
        });
        runtimeOnCleanup(() => {
            runtimeClearTimeout(operationalSuiteScanTimer);
            operationalSuiteScanTimer = null;
            clearOperationalSuiteContexts();
            if (runtime.operationalSuite?.phase === 'shell') delete runtime.operationalSuite;
        });
        if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
    }

'''

source = replace_once(
    source,
    """    // Issue #133 clean-room live mission requirements matrix.
""",
    runtime_shell + """    // Issue #133 clean-room live mission requirements matrix.
""",
    "Issue #378 lifecycle shell",
)

source = replace_once(
    source,
    """        if (state.missionRequirements) scheduleMissionRequirementsScan(0);
        if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(40);
""",
    """        if (state.missionRequirements) scheduleMissionRequirementsScan(0);
        if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
        if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(40);
""",
    "Issue #378 updateUI scheduling",
)

source = replace_once(
    source,
    """        installMissionRequirementsWindows();
        installCustomVehicleBadges();
""",
    """        installMissionRequirementsWindows();
        installOperationalSuiteShell();
        installCustomVehicleBadges();
""",
    "Issue #378 boot installation",
)

source = replace_once(
    source,
    """                if (missionChanged) {
                    scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
                    scheduleMissionRequirementsScan(35);
                }
""",
    """                if (missionChanged) {
                    scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
                    scheduleMissionRequirementsScan(35);
                    if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(35);
                }
""",
    "Issue #378 mission mutation scheduling",
)

source = replace_once(
    source,
    """            if (state.economyMode) scheduleEconomyLayerSync(0);
            scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: true });
            scheduleMajorIncidentFeedRender(80);
""",
    """            if (state.economyMode) scheduleEconomyLayerSync(0);
            scheduleEnabledMapRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: true });
            if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);
            scheduleMajorIncidentFeedRender(80);
""",
    "Issue #378 visibility scheduling",
)

baseline_source_lines = len(SOURCE.read_text(encoding="utf-8").splitlines())
candidate_source_lines = len(source.splitlines())
approved_non_style_lines = candidate_source_lines - baseline_source_lines
if approved_non_style_lines != 317:
    raise RuntimeError(
        f"Issue #378 shell line delta changed unexpectedly: {approved_non_style_lines} != 317"
    )

for path in CANONICAL:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")

TEST.parent.mkdir(parents=True, exist_ok=True)
TEST.write_text(r'''#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
source = SOURCE.read_text(encoding="utf-8")

required = {
    "baseline": "const OPERATIONAL_SUITE_LSSM_BASELINE = Object.freeze({",
    "baseline commit": "commit: '88e41646e59a7d620624f90f1d9a0a62320c2775'",
    "settings namespace": "operationalWindow: defaultOperationalWindowState(true)",
    "normaliser": "function normaliseOperationalWindowState(value, legacyMatrixEnabled = true)",
    "runtime shell": "function installOperationalSuiteShell()",
    "context map": "const operationalSuiteContexts = new Map();",
    "coalesced scheduler": "function scheduleOperationalSuiteScan(delay = 0)",
    "cleanup": "clearOperationalSuiteContexts();",
    "boot installation": "installOperationalSuiteShell();",
    "safe auto-open default": "autoOpenTransportRequest: false",
    "upstream continuation default": "autoClickSuccessButtons: true",
    "suite disabled default": "enabled: false,\n            phase: 'shell'",
    "legacy Matrix retained": "// Issue #133 clean-room live mission requirements matrix.",
}
for label, needle in required.items():
    if needle not in source:
        raise SystemExit(f"Issue #378 shell missing {label}: {needle}")

if source.index("installOperationalSuiteShell();") > source.index("startBootAttemptCoordinator(bootPerformanceStartedAt);"):
    raise SystemExit("Issue #378 shell must install before the boot-attempt coordinator")

if "data-mcms-operational-suite" in source or "mcms-operational-suite-panel" in source:
    raise SystemExit("Phase 2 shell must not render a competing operational-suite surface")

for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    if path.read_text(encoding="utf-8") != source:
        raise SystemExit(f"canonical parity failed: {path}")

fixture = __import__('json').loads((ROOT / '.github' / 'fixtures' / 'main-style-source-headroom.json').read_text(encoding='utf-8'))
expected_lines = fixture['candidateSourceLines'] + fixture.get('approvedNonStyleSourceLines', 0)
if fixture.get('expectedSourceLines') != expected_lines or expected_lines != len(source.splitlines()):
    raise SystemExit('Issue #378 source-headroom additive accounting is inconsistent')
if fixture.get('approvedNonStyleChanges') != [{'issue': 378, 'phase': 'operational-suite-shell', 'lines': 317}]:
    raise SystemExit('Issue #378 source-headroom change ledger is missing or altered')

print("Issue #378 operational-suite lifecycle/settings shell contract passed.")
''', encoding="utf-8")

headroom_fixture = json.loads(HEADROOM_FIXTURE.read_text(encoding="utf-8"))
if headroom_fixture.get("schemaVersion") != 4:
    raise RuntimeError("main-style source-headroom fixture schema changed before Issue #378 shell apply")
if headroom_fixture.get("candidateSourceLines") != baseline_source_lines:
    raise RuntimeError(
        "main-style source-headroom baseline no longer matches the pre-shell userscript"
    )
headroom_fixture["schemaVersion"] = 5
headroom_fixture["approvedNonStyleSourceLines"] = approved_non_style_lines
headroom_fixture["approvedNonStyleChanges"] = [
    {"issue": 378, "phase": "operational-suite-shell", "lines": approved_non_style_lines}
]
headroom_fixture["expectedSourceLines"] = candidate_source_lines
HEADROOM_FIXTURE.write_text(json.dumps(headroom_fixture, indent=2) + "\n", encoding="utf-8")

headroom_test = HEADROOM_TEST.read_text(encoding="utf-8")
old_headroom_check = '''    split_lines = re.split(r"\r?\n", text)
    source_lines = len(split_lines) - 1 if text.endswith("\n") else len(split_lines)
    if source_lines != fixture["candidateSourceLines"]:
        fail(f"candidate source line count changed: {source_lines} != {fixture['candidateSourceLines']}")
'''
new_headroom_check = '''    split_lines = re.split(r"\r?\n", text)
    source_lines = len(split_lines) - 1 if text.endswith("\n") else len(split_lines)
    approved_changes = fixture.get("approvedNonStyleChanges", [])
    if not isinstance(approved_changes, list):
        fail("approved non-style source changes must be a list")
    approved_total = 0
    for change in approved_changes:
        if not isinstance(change, dict):
            fail("approved non-style source change entries must be objects")
        issue = change.get("issue")
        phase = str(change.get("phase") or "").strip()
        lines = change.get("lines")
        if not isinstance(issue, int) or issue <= 0 or not phase or not isinstance(lines, int) or lines < 0:
            fail("approved non-style source change entry is malformed")
        approved_total += lines
    if approved_total != fixture.get("approvedNonStyleSourceLines", 0):
        fail("approved non-style source-line ledger total is inconsistent")
    expected_source_lines = fixture["candidateSourceLines"] + approved_total
    if fixture.get("expectedSourceLines", expected_source_lines) != expected_source_lines:
        fail("expected source line count is inconsistent with the approved non-style ledger")
    if source_lines != expected_source_lines:
        fail(f"candidate source line count changed: {source_lines} != {expected_source_lines}")
'''
if headroom_test.count(old_headroom_check) != 1:
    raise RuntimeError("main-style source-headroom line-count anchor changed")
HEADROOM_TEST.write_text(headroom_test.replace(old_headroom_check, new_headroom_check, 1), encoding="utf-8")

subprocess.run([sys.executable, str(TEST)], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(HEADROOM_TEST)], cwd=ROOT, check=True)
print("Issue #378 operational-suite shell applied and validated.")
