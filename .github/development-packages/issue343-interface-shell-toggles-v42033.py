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
OLD_VERSION = "4.20.32"
NEW_VERSION = "4.20.33"


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
source = replace_once(
    source,
    """    function toggleFeature(feature) {
        handleMapVisibilityToggle(feature);
        handleMissionWindowToggle(feature);
        handlePayoutAudioToggle(feature);
        handleMissionMonitoringToggle(feature);
""",
    """    function handleInterfaceShellToggle(feature) {
        if (feature === 'clean') state.cleanMode = !state.cleanMode; else if (feature === 'shortcuts') state.shortcuts = !state.shortcuts; else if (feature === 'compactDock') state.compactDock = !state.compactDock; else return false; return true; }
    function toggleFeature(feature) {
        handleMapVisibilityToggle(feature);
        handleMissionWindowToggle(feature);
        handlePayoutAudioToggle(feature);
        handleMissionMonitoringToggle(feature);
        handleInterfaceShellToggle(feature);
""",
    "interface-shell helper insertion",
)
source = replace_once(
    source,
    """        if (feature === 'clean') state.cleanMode = !state.cleanMode;
        if (feature === 'shortcuts') state.shortcuts = !state.shortcuts;
""",
    "",
    "direct clean and shortcuts routes",
)
source = replace_once(
    source,
    "        if (feature === 'compactDock') state.compactDock = !state.compactDock;\n",
    "",
    "direct compactDock route",
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
fixture["extractedInterfaceShellToggleRoutes"] = [
    "clean",
    "compactDock",
    "shortcuts",
]
fixture["extractedInterfaceShellToggleStatePaths"] = {
    "clean": "cleanMode",
    "compactDock": "compactDock",
    "shortcuts": "shortcuts",
}
FIXTURE.write_text(
    json.dumps(fixture, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    """    "handleMissionMonitoringToggle",
    "applyMissionMonitoringToggleEffects",
    "toggleFeature",""",
    """    "handleMissionMonitoringToggle",
    "applyMissionMonitoringToggleEffects",
    "handleInterfaceShellToggle",
    "toggleFeature",""",
    "contract function inventory",
)
contract = replace_once(
    contract,
    """    handle_mission_monitoring_toggle = extract_function(source, masked, "handleMissionMonitoringToggle")
    apply_mission_monitoring_effects = extract_function(source, masked, "applyMissionMonitoringToggleEffects")
    toggle_feature = extract_function(source, masked, "toggleFeature")""",
    """    handle_mission_monitoring_toggle = extract_function(source, masked, "handleMissionMonitoringToggle")
    apply_mission_monitoring_effects = extract_function(source, masked, "applyMissionMonitoringToggleEffects")
    handle_interface_shell_toggle = extract_function(source, masked, "handleInterfaceShellToggle")
    toggle_feature = extract_function(source, masked, "toggleFeature")""",
    "contract static function extraction",
)
contract = replace_once(
    contract,
    r"""    mission_monitoring_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_mission_monitoring_toggle)
    mission_monitoring_effect_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', apply_mission_monitoring_effects)
    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes + payout_audio_toggle_routes + mission_monitoring_toggle_routes))""",
    r"""    mission_monitoring_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_mission_monitoring_toggle)
    mission_monitoring_effect_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', apply_mission_monitoring_effects)
    interface_shell_toggle_routes = values(r'feature\s*===\s*["\']([^"\']+)["\']', handle_interface_shell_toggle)
    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes + payout_audio_toggle_routes + mission_monitoring_toggle_routes + interface_shell_toggle_routes))""",
    "contract interface-shell route inventory",
)
contract = replace_once(
    contract,
    """    assert "handleMissionMonitoringToggle(feature)" in toggle_feature
    assert "applyMissionMonitoringToggleEffects(feature)" in toggle_feature""",
    """    assert "handleMissionMonitoringToggle(feature)" in toggle_feature
    assert "applyMissionMonitoringToggleEffects(feature)" in toggle_feature
    assert interface_shell_toggle_routes == sorted(fixtures["extractedInterfaceShellToggleRoutes"]), "Extracted interface-shell toggle routing changed"
    assert not set(direct_toggle_routes).intersection(interface_shell_toggle_routes), "Extracted interface-shell toggles remain duplicated"
    assert "handleInterfaceShellToggle(feature)" in toggle_feature""",
    "contract interface-shell static invariants",
)

interface_shell_test = r"""

function testExtractedInterfaceShellToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedInterfaceShellToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        assert.equal(handleInterfaceShellToggle(feature), true, `${{feature}} was not handled directly`);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle ${{path}}`);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null);
        assert.equal(wasCalled("updateUI"), false);
    }}

    resetEnvironment();
    const unknownBefore = JSON.stringify(state);
    assert.equal(handleInterfaceShellToggle("unknown-interface-shell-toggle"), false);
    assert.equal(JSON.stringify(state), unknownBefore);
    assert.equal(calls.length, 0);
}}
"""
contract = replace_once(
    contract,
    "\nasync function testToggleContracts() {{\n",
    interface_shell_test + "\nasync function testToggleContracts() {{\n",
    "direct interface-shell contracts",
)

interface_shell_delegated_test = r"""

    for (const [feature, path] of Object.entries(fixtures.extractedInterfaceShellToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        toggleFeature(feature);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle through the main router`);
        assert.equal(localStorage.getItem(SCRIPT.storageState) !== null, true, `${{feature}} did not persist state`);
        const updateIndex = calls.findIndex(call => call.name === "updateUI");
        const reconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
        assert.ok(updateIndex >= 0 && updateIndex < reconcileIndex, `${{feature}} reconciliation must remain after UI update`);
        if (feature === "clean") {{
            const closeIndex = calls.findIndex(call => call.name === "closePanel");
            assert.ok(closeIndex >= 0 && closeIndex < updateIndex, "Clean Mode must close the panel before UI synchronization");
        }}
    }}
"""
contract = replace_once(
    contract,
    '\n    resetEnvironment();\n    toggleFeature("criticalView");',
    interface_shell_delegated_test + '\n    resetEnvironment();\n    toggleFeature("criticalView");',
    "delegated interface-shell contracts",
)
contract = replace_once(
    contract,
    """    testExtractedMissionMonitoringToggleContracts();
    await testToggleContracts();""",
    """    testExtractedMissionMonitoringToggleContracts();
    testExtractedInterfaceShellToggleContracts();
    await testToggleContracts();""",
    "interface-shell contract invocation",
)
contract = replace_once(
    contract,
    "extracted mission-monitoring toggle parity, extracted financial route parity,",
    "extracted mission-monitoring toggle parity, extracted interface-shell toggle parity, extracted financial route parity,",
    "contract result summary",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = f"""## [{NEW_VERSION}] - 2026-07-22

### Internal reliability
- Extracted Clean Mode, Shortcuts and Compact Dock state routing from `toggleFeature()` into a dedicated interface-shell helper.
- Preserved the shared Clean Mode panel-close lifecycle, persistence, root attributes, UI synchronization and feature-reconciliation order.
- Added direct and delegated contracts for all three routes and unknown-route safety.

### Benefit
- Future interface-shell changes are easier to isolate, test and roll back without tracing unrelated operational feature branches.

### Compatibility
- No visual design, layout, theme, notification, timing, public asset or user-facing feature behaviour changed.

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
    "while interface-shell toggle routing remains fixture-backed and managed runtime budgets remain unchanged."
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
