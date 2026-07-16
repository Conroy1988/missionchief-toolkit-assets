#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
TEST = ROOT / ".github" / "scripts" / "test_settings_ui_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


text = TEST.read_text(encoding="utf-8")
text = replace_once(
    text,
    'function stopAutoLoadAllVehicles() {{ record("stopAutoLoadAllVehicles"); }}\n',
    'function stopAutoLoadAllVehicles() {{ record("stopAutoLoadAllVehicles"); }}\n'
    'function installMissionValueWindows() {{ record("installMissionValueWindows"); }}\n'
    'function clearMissionValueIndicators() {{ record("clearMissionValueIndicators"); }}\n',
    "Mission Value harness stubs",
)
text = replace_once(
    text,
    '    assert.equal(value.payoutFlash.template, "gta5");\n',
    '    assert.equal(value.payoutFlash.template, "gta5");\n'
    '    assert.equal(value.missionValue, true);\n',
    "default-on assertion",
)
text = replace_once(
    text,
    '    assert.equal(directMigrated.payoutFlash.template, "gta5");\n',
    '    assert.equal(directMigrated.payoutFlash.template, "gta5");\n'
    '    assert.equal(directMigrated.missionValue, false);\n',
    "direct migration explicit-off assertion",
)
text = replace_once(
    text,
    '    assert.equal(migrated.autoLoadAllVehicles, true);\n',
    '    assert.equal(migrated.autoLoadAllVehicles, true);\n'
    '    assert.equal(migrated.missionValue, false);\n',
    "loaded migration explicit-off assertion",
)
text = replace_once(
    text,
    '    assert.equal(modern.discordReport.reportMode, "executive");\n',
    '    assert.equal(modern.discordReport.reportMode, "executive");\n'
    '    assert.equal(modern.missionValue, true);\n',
    "missing-field default-on assertion",
)
TEST.write_text(text, encoding="utf-8")
subprocess.run(["python3", str(TEST)], cwd=ROOT, check=True)

for path in [
    ROOT / ".github" / "development-packages" / "issue-93-settings-contract-fix.py",
    ROOT / ".github" / "diagnostics" / "issue-93-settings-diagnostic.txt",
]:
    path.unlink(missing_ok=True)

print("Mission Value settings defaults, migration, persistence and toggle contract passed.")
