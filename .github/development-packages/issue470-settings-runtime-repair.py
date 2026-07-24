#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TEST = ROOT / '.github/scripts/test_settings_ui_contract.py'
DIAGNOSTIC = ROOT / '.github/diagnostics/issue470-contract-after-settings-runtime.txt'

text = TEST.read_text(encoding='utf-8')

variable_anchor = '''let missionSpawnArmed = false;
let missionSpawnPrimeTimer = null;
let payoutMediaAudio = null;'''
variable_value = '''let missionSpawnArmed = false;
let missionSpawnPrimeTimer = null;
let missionAgeTimer = null;
let inlineMissionDataScanned = false;
let payoutMediaAudio = null;'''
if text.count(variable_anchor) != 1:
    raise SystemExit(f'Settings harness Mission Age variable anchor count changed: {text.count(variable_anchor)}')
text = text.replace(variable_anchor, variable_value, 1)

function_anchor = '''function synchroniseVehicleMarkerClasses() {{ record("synchroniseVehicleMarkerClasses"); }}
function synchronisePersonalBuildingVisibility() {{ record("synchronisePersonalBuildingVisibility"); }}
function scheduleEconomyLayerSync(value) {{ record("scheduleEconomyLayerSync", value); }}
function showToast(value) {{ record("showToast", value); }}'''
function_value = '''function synchroniseVehicleMarkerClasses() {{ record("synchroniseVehicleMarkerClasses"); }}
function synchronisePersonalBuildingVisibility() {{ record("synchronisePersonalBuildingVisibility"); }}
function scheduleEconomyLayerSync(value) {{ record("scheduleEconomyLayerSync", value); }}
function scanInlineMissionMarkerData(value) {{ record("scanInlineMissionMarkerData", value); }}
function invalidateMarkerRegistryCaches(value) {{ record("invalidateMarkerRegistryCaches", value); }}
function scheduleMarkerStateSync(...args) {{ record("scheduleMarkerStateSync", ...args); }}
function scheduleMissionAgeRefresh(value) {{ record("scheduleMissionAgeRefresh", value); }}
function clearMissionAgeLabels() {{ record("clearMissionAgeLabels"); }}
function showToast(value) {{ record("showToast", value); }}'''
if text.count(function_anchor) != 1:
    raise SystemExit(f'Settings harness Mission Age function anchor count changed: {text.count(function_anchor)}')
text = text.replace(function_anchor, function_value, 1)

reset_anchor = '''    missionSpawnArmed = false;
    missionSpawnPrimeTimer = null;
    knownMissionIds.clear();'''
reset_value = '''    missionSpawnArmed = false;
    missionSpawnPrimeTimer = null;
    missionAgeTimer = null;
    inlineMissionDataScanned = false;
    knownMissionIds.clear();'''
if text.count(reset_anchor) != 1:
    raise SystemExit(f'Settings harness Mission Age reset anchor count changed: {text.count(reset_anchor)}')
text = text.replace(reset_anchor, reset_value, 1)

effect_anchor = '''    resetEnvironment();
    state.economyMode = true;
    applyMapVisibilityToggleEffects("coverage");
    assert.equal(calls.length, 0, "map overlays without direct layer sync must remain side-effect free in the extracted effect phase");
}}'''
effect_value = '''    resetEnvironment();
    missionAgeTimer = 91;
    state.missionAge = false;
    applyMapVisibilityToggleEffects("missionAge");
    assert.deepEqual(callFor("runtimeClearTimeout").args, [91]);
    assert.equal(missionAgeTimer, null);
    assert.equal(wasCalled("clearMissionAgeLabels"), true);
    assert.equal(wasCalled("scanInlineMissionMarkerData"), false);

    resetEnvironment();
    missionAgeTimer = 92;
    state.missionAge = true;
    inlineMissionDataScanned = true;
    applyMapVisibilityToggleEffects("missionAge");
    assert.deepEqual(callFor("runtimeClearTimeout").args, [92]);
    assert.equal(missionAgeTimer, null);
    assert.equal(inlineMissionDataScanned, false);
    assert.deepEqual(callFor("scanInlineMissionMarkerData").args, [true]);
    assert.deepEqual(callFor("invalidateMarkerRegistryCaches").args, ["mission"]);
    assert.deepEqual(callFor("scheduleMarkerStateSync").args, [0, true]);
    assert.deepEqual(callFor("scheduleMissionAgeRefresh").args, [0]);
    assert.deepEqual(callFor("runtimeSetTimeout").args, [1000]);
    assert.equal(wasCalled("clearMissionAgeLabels"), false);

    resetEnvironment();
    state.economyMode = true;
    applyMapVisibilityToggleEffects("coverage");
    assert.equal(calls.length, 0, "map overlays without direct layer sync must remain side-effect free in the extracted effect phase");
}}'''
if text.count(effect_anchor) != 1:
    raise SystemExit(f'Settings harness Mission Age effect-test anchor count changed: {text.count(effect_anchor)}')
text = text.replace(effect_anchor, effect_value, 1)

TEST.write_text(text, encoding='utf-8')

result = subprocess.run(
    ['bash', '.github/scripts/run_userscript_preflight.sh', '--contracts'],
    cwd=ROOT,
    text=True,
    capture_output=True,
    timeout=600,
)

(ROOT / '.github/diagnostics/issue470-contract-after-settings.txt').unlink(missing_ok=True)
if result.returncode != 0:
    DIAGNOSTIC.parent.mkdir(parents=True, exist_ok=True)
    DIAGNOSTIC.write_text(
        'Issue #470 contract preflight after Settings UI runtime repair\n'
        f'exit={result.returncode}\n\n'
        '=== STDOUT ===\n'
        + result.stdout[-60000:]
        + '\n=== STDERR ===\n'
        + result.stderr[-60000:]
        + '\n',
        encoding='utf-8',
    )
    SELF.unlink(missing_ok=True)
    print('Settings UI Mission Age runtime harness repaired; a later contract failure was captured.')
else:
    DIAGNOSTIC.unlink(missing_ok=True)
    SELF.unlink(missing_ok=True)
    print(result.stdout.strip())
    print('Issue #470 aggregate contract preflight passed after Settings UI runtime repair.')
