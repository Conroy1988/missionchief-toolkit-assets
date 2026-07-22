#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "settings-ui-contract.json"
CONTRACT = ROOT / ".github" / "scripts" / "test_settings_ui_contract.py"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
OLD_VERSION = "4.20.31"
NEW_VERSION = "4.20.32"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
original_lines = len(source.splitlines())
source = replace_once(
    source,
    f"// @version      {OLD_VERSION}",
    f"// @version      {NEW_VERSION}",
    "userscript metadata version",
)
source = replace_once(
    source,
    f"version: '{OLD_VERSION}'",
    f"version: '{NEW_VERSION}'",
    "runtime version",
)

old_state_block = """        if (feature === 'stuckDetector') state.stuckDetector.enabled = !state.stuckDetector.enabled;
        if (feature === 'missionSpawn') state.missionSpawn.enabled = !state.missionSpawn.enabled;
        if (feature === 'missionSpawn') {
            missionSpawnArmed = false;
            runtimeClearTimeout(missionSpawnPrimeTimer);
            knownMissionIds.clear();
            if (state.missionSpawn.enabled) primeMissionSpawnDetector();
        }
"""
new_helper_and_call = """    function handleMissionMonitoringToggle(feature) {
        if (feature === 'stuckDetector') state.stuckDetector.enabled = !state.stuckDetector.enabled;
        else if (feature === 'missionSpawn') { state.missionSpawn.enabled = !state.missionSpawn.enabled; missionSpawnArmed = false; runtimeClearTimeout(missionSpawnPrimeTimer); knownMissionIds.clear(); if (state.missionSpawn.enabled) primeMissionSpawnDetector(); }
        else return false;
        return true; }
    function applyMissionMonitoringToggleEffects(feature) {
        if (feature === 'stuckDetector') showToast(state.stuckDetector.enabled ? `Stuck detector on · ${state.stuckDetector.thresholdMin} min` : 'Stuck detector off');
        else if (feature === 'missionSpawn') showToast(state.missionSpawn.enabled ? 'New mission animation on' : 'New mission animation off'); }
    function toggleFeature(feature) {
        handleMapVisibilityToggle(feature);
        handleMissionWindowToggle(feature);
        handlePayoutAudioToggle(feature);
        handleMissionMonitoringToggle(feature);
"""
source = replace_once(
    source,
    """    function toggleFeature(feature) {
        handleMapVisibilityToggle(feature);
        handleMissionWindowToggle(feature);
        handlePayoutAudioToggle(feature);
""",
    new_helper_and_call,
    "mission-monitoring helper insertion",
)
source = replace_once(source, old_state_block, "", "direct monitoring state routes")
source = replace_once(
    source,
    """        applyMissionWindowToggleEffects(feature);
        applyPayoutAudioToggleEffects(feature);
""",
    """        applyMissionWindowToggleEffects(feature);
        applyPayoutAudioToggleEffects(feature);
        applyMissionMonitoringToggleEffects(feature);
""",
    "post-reconciliation monitoring delegation",
)
source = replace_once(
    source,
    """        if (feature === 'stuckDetector') showToast(state.stuckDetector.enabled ? `Stuck detector on · ${state.stuckDetector.thresholdMin} min` : 'Stuck detector off');
        if (feature === 'missionSpawn') showToast(state.missionSpawn.enabled ? 'New mission animation on' : 'New mission animation off');
""",
    "",
    "direct monitoring effect routes",
)

if len(source.splitlines()) != original_lines:
    raise RuntimeError(
        f"source-headroom line count changed: {original_lines} -> {len(source.splitlines())}"
    )

SOURCE.write_text(source, encoding="utf-8")
for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    path.write_text(source, encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
fixture["extractedMissionMonitoringToggleRoutes"] = [
    "missionSpawn",
    "stuckDetector",
]
fixture["extractedMissionMonitoringEffectRoutes"] = [
    "missionSpawn",
    "stuckDetector",
]
fixture["extractedMissionMonitoringToggleStatePaths"] = {
    "missionSpawn": "missionSpawn.enabled",
    "stuckDetector": "stuckDetector.enabled",
}
FIXTURE.write_text(
    json.dumps(fixture, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    """    "applyPayoutAudioToggleEffects",
    "toggleFeature",""",
    """    "applyPayoutAudioToggleEffects",
    "handleMissionMonitoringToggle",
    "applyMissionMonitoringToggleEffects",
    "toggleFeature",""",
    "contract function inventory",
)
contract = replace_once(
    contract,
    """    apply_payout_audio_effects = extract_function(source, masked, "applyPayoutAudioToggleEffects")
    toggle_feature = extract_function(source, masked, "toggleFeature")""",
    """    apply_payout_audio_effects = extract_function(source, masked, "applyPayoutAudioToggleEffects")
    handle_mission_monitoring_toggle = extract_function(source, masked, "handleMissionMonitoringToggle")
    apply_mission_monitoring_effects = extract_function(source, masked, "applyMissionMonitoringToggleEffects")
    toggle_feature = extract_function(source, masked, "toggleFeature")""",
    "contract static function extraction",
)
contract = replace_once(
    contract,
    "    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes + payout_audio_toggle_routes))",
    """    mission_monitoring_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_mission_monitoring_toggle)
    mission_monitoring_effect_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', apply_mission_monitoring_effects)
    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes + payout_audio_toggle_routes + mission_monitoring_toggle_routes))""",
    "contract monitoring route inventory",
)
contract = replace_once(
    contract,
    """    assert "applyPayoutAudioToggleEffects(feature)" in toggle_feature""",
    """    assert "applyPayoutAudioToggleEffects(feature)" in toggle_feature
    assert mission_monitoring_toggle_routes == sorted(fixtures["extractedMissionMonitoringToggleRoutes"]), "Extracted mission-monitoring toggle routing changed"
    assert mission_monitoring_effect_routes == sorted(fixtures["extractedMissionMonitoringEffectRoutes"]), "Extracted mission-monitoring effect routing changed"
    assert not set(direct_toggle_routes).intersection(mission_monitoring_toggle_routes), "Extracted mission-monitoring toggles remain duplicated"
    assert "handleMissionMonitoringToggle(feature)" in toggle_feature
    assert "applyMissionMonitoringToggleEffects(feature)" in toggle_feature""",
    "contract monitoring static invariants",
)

monitoring_test = r"""

function testExtractedMissionMonitoringToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedMissionMonitoringToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        assert.equal(handleMissionMonitoringToggle(feature), true, `${{feature}} was not handled directly`);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle ${{path}}`);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null);
        assert.equal(wasCalled("updateUI"), false);
    }}

    resetEnvironment();
    const unknownBefore = JSON.stringify(state);
    assert.equal(handleMissionMonitoringToggle("unknown-monitoring-toggle"), false);
    assert.equal(JSON.stringify(state), unknownBefore);
    assert.equal(calls.length, 0);

    resetEnvironment();
    state.missionSpawn.enabled = false;
    missionSpawnPrimeTimer = 73;
    missionSpawnArmed = true;
    knownMissionIds.add("existing");
    handleMissionMonitoringToggle("missionSpawn");
    assert.equal(state.missionSpawn.enabled, true);
    assert.equal(missionSpawnArmed, false);
    assert.equal(knownMissionIds.size, 0);
    assert.deepEqual(callFor("runtimeClearTimeout").args, [73]);
    assert.equal(wasCalled("primeMissionSpawnDetector"), true);

    resetEnvironment();
    state.missionSpawn.enabled = true;
    missionSpawnPrimeTimer = 74;
    missionSpawnArmed = true;
    knownMissionIds.add("existing");
    handleMissionMonitoringToggle("missionSpawn");
    assert.equal(state.missionSpawn.enabled, false);
    assert.equal(missionSpawnArmed, false);
    assert.equal(knownMissionIds.size, 0);
    assert.deepEqual(callFor("runtimeClearTimeout").args, [74]);
    assert.equal(wasCalled("primeMissionSpawnDetector"), false);

    resetEnvironment();
    applyMissionMonitoringToggleEffects("missionSpawn");
    assert.equal(callFor("showToast").args[0], "New mission animation on");

    resetEnvironment();
    applyMissionMonitoringToggleEffects("stuckDetector");
    assert.equal(callFor("showToast").args[0], "Stuck detector on · 15 min");

    resetEnvironment();
    applyMissionMonitoringToggleEffects("coverage");
    assert.equal(calls.length, 0);
}}
"""
contract = replace_once(
    contract,
    "\nasync function testToggleContracts() {{\n",
    monitoring_test + "\nasync function testToggleContracts() {{\n",
    "direct monitoring contracts",
)

delegated_test = r"""

    resetEnvironment();
    state.missionSpawn.enabled = false;
    missionSpawnPrimeTimer = 75;
    missionSpawnArmed = true;
    knownMissionIds.add("existing");
    toggleFeature("missionSpawn");
    const spawnClearIndex = calls.findIndex(call => call.name === "runtimeClearTimeout");
    const spawnPrimeIndex = calls.findIndex(call => call.name === "primeMissionSpawnDetector");
    const spawnUpdateIndex = calls.findIndex(call => call.name === "updateUI");
    const spawnReconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
    const spawnToastIndex = calls.findIndex(call => call.name === "showToast");
    assert.ok(spawnClearIndex >= 0 && spawnClearIndex < spawnUpdateIndex);
    assert.ok(spawnPrimeIndex >= 0 && spawnPrimeIndex < spawnUpdateIndex);
    assert.ok(spawnUpdateIndex < spawnReconcileIndex && spawnReconcileIndex < spawnToastIndex);
    assert.equal(knownMissionIds.size, 0);

    resetEnvironment();
    toggleFeature("stuckDetector");
    const stuckUpdateIndex = calls.findIndex(call => call.name === "updateUI");
    const stuckReconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
    const stuckToastIndex = calls.findIndex(call => call.name === "showToast");
    assert.ok(stuckUpdateIndex >= 0 && stuckUpdateIndex < stuckReconcileIndex);
    assert.ok(stuckReconcileIndex < stuckToastIndex);
"""
contract = replace_once(
    contract,
    '\n    resetEnvironment();\n    toggleFeature("criticalView");',
    delegated_test + '\n    resetEnvironment();\n    toggleFeature("criticalView");',
    "delegated monitoring contracts",
)
contract = replace_once(
    contract,
    """    testExtractedPayoutAudioToggleContracts();
    await testToggleContracts();""",
    """    testExtractedPayoutAudioToggleContracts();
    testExtractedMissionMonitoringToggleContracts();
    await testToggleContracts();""",
    "monitoring contract invocation",
)
contract = replace_once(
    contract,
    "extracted payout/audio toggle parity, extracted financial route parity,",
    "extracted payout/audio toggle parity, extracted mission-monitoring toggle parity, extracted financial route parity,",
    "contract result summary",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = f"""## [{NEW_VERSION}] - 2026-07-22

### Internal reliability
- Extracted Mission Spawn and Stuck Detector state and notification routing from `toggleFeature()` into dedicated mission-monitoring helpers.
- Preserved Mission Spawn arming reset, timer cancellation, known-mission reset and enabled-only detector priming before the shared persistence/UI phase.
- Added direct and delegated contracts proving both monitoring notifications remain after feature reconciliation.

### Compatibility
- No monitoring threshold, timer duration, mission classification, visual design, device layout, theme or public asset changed.

"""
changelog_path.write_text(
    replace_once(
        changelog,
        "## [Unreleased]\n\n",
        "## [Unreleased]\n\n" + entry,
        "changelog insertion",
    ),
    encoding="utf-8",
)

help_path = ROOT / "help" / "index.html"
help_text = help_path.read_text(encoding="utf-8")
if OLD_VERSION not in help_text:
    raise RuntimeError("help page does not contain the current version")
help_path.write_text(help_text.replace(OLD_VERSION, NEW_VERSION), encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
source_lines = len(source.splitlines())
headroom["candidateVersion"] = NEW_VERSION
headroom["candidateSourceLines"] = source_lines
headroom["recoveredSourceLines"] = headroom["originalSourceLines"] - source_lines
headroom["candidateSourceSha256"] = hashlib.sha256(source.encode()).hexdigest()
headroom["invariant"] = (
    f'The reviewed compact stylesheet retains {headroom["recoveredSourceLines"]} recovered source lines '
    "while mission-monitoring toggle routing remains fixture-backed and managed runtime budgets remain unchanged."
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

subprocess.check_call(
    [sys.executable, str(CONTRACT)],
    cwd=ROOT,
    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

print(
    f"Prepared Toolkit {NEW_VERSION}; source lines={source_lines}; "
    f"recovered={headroom['recoveredSourceLines']}"
)
