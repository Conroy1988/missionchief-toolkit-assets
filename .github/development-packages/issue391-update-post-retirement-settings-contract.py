#!/usr/bin/env python3
from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
META_REL = Path(".github/development-packages/issue391-finalize-canonical-retirement.py")
META = ROOT / META_REL

text = META.read_text(encoding="utf-8")

old_constant = '''SETTINGS_FIXTURE = ROOT / ".github" / "fixtures" / "settings-ui-contract.json"
HEADROOM_TEST = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"
'''
new_constant = '''SETTINGS_FIXTURE = ROOT / ".github" / "fixtures" / "settings-ui-contract.json"
SETTINGS_TEST = ROOT / ".github" / "scripts" / "test_settings_ui_contract.py"
HEADROOM_TEST = ROOT / ".github" / "scripts" / "test_main_style_source_headroom.py"
'''
if text.count(old_constant) != 1:
    raise RuntimeError("canonical meta settings-test constant anchor drifted")
text = text.replace(old_constant, new_constant)

runtime_anchor = r'SETTINGS_FIXTURE.write_text(json.dumps(settings_fixture, indent=2) + "\\n", encoding="utf-8")'
settings_block = '''settings_test = SETTINGS_TEST.read_text(encoding="utf-8")
settings_test = replace_exact(
    settings_test,
    """FUNCTION_NAMES = [
    "defaultState",
""",
    """FUNCTION_NAMES = [
    "defaultOperationalWindowState",
    "operationalSuiteBoolean",
    "operationalSuiteArray",
    "normaliseOperationalWindowState",
    "defaultState",
""",
    "settings contract operational helper extraction",
)
settings_test = replace_exact(
    settings_test,
    """    "handleDeviceLayoutSettingChange",
    "handleSettingChange",
""",
    """    "handleDeviceLayoutSettingChange",
    "handleOperationalWindowSettingChange",
    "handleSettingChange",
""",
    "settings contract operational setting router extraction",
)
settings_test = replace_exact(
    settings_test,
    """const TRANSPORT_SWEEP_MAX_REQUESTS = 100;
""",
    """const TRANSPORT_SWEEP_MAX_REQUESTS = 100;
const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;
""",
    "settings contract operational schema constant",
)
settings_test = replace_exact(
    settings_test,
    """function installMissionRequirementsWindows() {{ record("installMissionRequirementsWindows"); }}
function clearMissionRequirementsPanels() {{ record("clearMissionRequirementsPanels"); }}
""",
    "",
    "settings contract obsolete Matrix effect stubs",
)
settings_test = replace_exact(
    settings_test,
    """    assert.equal(value.missionValue, true);
    assert.equal(value.missionRequirements, true);
""",
    """    assert.equal(value.missionValue, true);
    assert.equal(Object.hasOwn(value, "missionRequirements"), false);
    assert.equal(value.operationalWindow.requirements.enabled, true);
    assert.equal(value.operationalWindow.migration.matrixRetired, true);
""",
    "settings contract default operational state",
)
settings_test = replace_exact(
    settings_test,
    """    assert.equal(directMigrated.missionValue, false);
    assert.equal(directMigrated.missionRequirements, false);
""",
    """    assert.equal(directMigrated.missionValue, false);
    assert.equal(Object.hasOwn(directMigrated, "missionRequirements"), false);
    assert.equal(directMigrated.operationalWindow.requirements.enabled, false);
    assert.equal(directMigrated.operationalWindow.migration.matrixRetired, true);
""",
    "settings contract direct legacy Matrix migration",
)
settings_test = replace_exact(
    settings_test,
    """    assert.equal(migrated.autoLoadAllVehicles, true);
    assert.equal(migrated.missionValue, false);
    assert.equal(migrated.missionRequirements, false);
""",
    """    assert.equal(migrated.autoLoadAllVehicles, true);
    assert.equal(migrated.missionValue, false);
    assert.equal(Object.hasOwn(migrated, "missionRequirements"), false);
    assert.equal(migrated.operationalWindow.requirements.enabled, false);
    assert.equal(migrated.operationalWindow.migration.matrixRetired, true);
""",
    "settings contract persisted legacy Matrix migration",
)
settings_test = replace_exact(
    settings_test,
    """    assert.equal(modern.missionValue, true);
    assert.equal(modern.missionRequirements, true);
""",
    """    assert.equal(modern.missionValue, true);
    assert.equal(Object.hasOwn(modern, "missionRequirements"), false);
    assert.equal(modern.operationalWindow.requirements.enabled, true);
    assert.equal(modern.operationalWindow.migration.matrixRetired, true);
""",
    "settings contract modern operational state",
)
settings_test = replace_exact(
    settings_test,
    """        ["missionRequirements", "installMissionRequirementsWindows", "clearMissionRequirementsPanels"],
""",
    "",
    "settings contract obsolete Matrix effect case",
)
settings_test = replace_exact(
    settings_test,
    """        ["missionRequirements", "installMissionRequirementsWindows"],
""",
    "",
    "settings contract obsolete Matrix mission-effect ordering case",
)
SETTINGS_TEST.write_text(settings_test, encoding="utf-8")'''
if text.count(runtime_anchor) != 1:
    raise RuntimeError(f"canonical meta settings-test runtime anchor drifted: {text.count(runtime_anchor)}")
text = text.replace(runtime_anchor, runtime_anchor + "\n\n" + settings_block, 1)

old_diagnostic = '''    ROOT / ".github" / "diagnostics" / "issue391-migration-v2-failure.txt",
)'''
new_diagnostic = '''    ROOT / ".github" / "diagnostics" / "issue391-migration-v2-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-canonical-retirement-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-operational-settings-helper-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-post-retirement-settings-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-post-retirement-settings-failure-v2.txt",
    ROOT / ".github" / "diagnostics" / "issue391-post-retirement-settings-failure-v3.txt",
    ROOT / ".github" / "diagnostics" / "issue391-post-retirement-settings-failure-v4.txt",
    ROOT / ".github" / "diagnostics" / "issue391-post-retirement-settings-failure-v5.txt",
    ROOT / ".github" / "diagnostics" / "issue391-post-retirement-settings-failure-v6.txt",
)'''
if text.count(old_diagnostic) != 1:
    raise RuntimeError("canonical meta final diagnostic cleanup anchor drifted")
text = text.replace(old_diagnostic, new_diagnostic)

META.write_text(text, encoding="utf-8")
py_compile.compile(str(META), doraise=True)

with tempfile.TemporaryDirectory(prefix="issue391-post-retirement-settings-selftest-") as temporary:
    sandbox = Path(temporary) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    result = subprocess.run(
        ["python3", str(sandbox / META_REL)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        raise SystemExit("Post-retirement settings-contract correction failed full retirement sandbox")

for obsolete in (
    ROOT / ".github" / "development-packages" / "issue391-canonical-retirement-diagnostic.py",
    ROOT / ".github" / "development-packages" / "issue391-operational-settings-helper-map.py",
    ROOT / ".github" / "development-packages" / "issue391-post-retirement-settings-diagnostic-v6.py",
):
    obsolete.unlink(missing_ok=True)

print("Post-retirement settings contract updated; canonical retirement sandbox passed.")
