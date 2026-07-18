#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
FIXTURE = ROOT / ".github" / "fixtures" / "settings-ui-contract.json"
SETTINGS_TEST = ROOT / ".github" / "scripts" / "test_settings_ui_contract.py"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
DIAGNOSTIC = ROOT / "docs" / "issue-133-preflight-diagnostics.json"
DIAGNOSTIC_PACKAGE = ROOT / ".github" / "development-packages" / "issue-133-preflight-diagnose.py"
OLD_PACKAGE = ROOT / ".github" / "development-packages" / "issue-133-final-preflight-fix.py"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
DOC_AUDIT = ROOT / ".github" / "scripts" / "check_documentation_drift.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
if "missionRequirements" not in fixture["toggleRoutes"]:
    fixture["toggleRoutes"].append("missionRequirements")
    fixture["toggleRoutes"].sort()
fixture["toggleStatePaths"]["missionRequirements"] = "missionRequirements"
fixture["toggleStatePaths"] = dict(sorted(fixture["toggleStatePaths"].items()))
fixture["legacyMigration"]["missionRequirements"] = False
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

settings_test = SETTINGS_TEST.read_text(encoding="utf-8")
settings_test = replace_once(
    settings_test,
    'function installMissionValueWindows() {{ record("installMissionValueWindows"); }}\nfunction clearMissionValueIndicators() {{ record("clearMissionValueIndicators"); }}\n',
    'function installMissionValueWindows() {{ record("installMissionValueWindows"); }}\nfunction clearMissionValueIndicators() {{ record("clearMissionValueIndicators"); }}\nfunction installMissionRequirementsWindows() {{ record("installMissionRequirementsWindows"); }}\nfunction clearMissionRequirementsPanels() {{ record("clearMissionRequirementsPanels"); }}\n',
    "settings harness Mission Requirements lifecycle stubs",
)
settings_test = replace_once(settings_test, '    assert.equal(value.missionValue, true);\n', '    assert.equal(value.missionValue, true);\n    assert.equal(value.missionRequirements, true);\n', "default Mission Requirements state assertion")
settings_test = replace_once(settings_test, '    assert.equal(directMigrated.missionValue, false);\n', '    assert.equal(directMigrated.missionValue, false);\n    assert.equal(directMigrated.missionRequirements, false);\n', "direct migration Mission Requirements assertion")
settings_test = replace_once(settings_test, '    assert.equal(migrated.missionValue, false);\n', '    assert.equal(migrated.missionValue, false);\n    assert.equal(migrated.missionRequirements, false);\n', "loaded migration Mission Requirements assertion")
settings_test = replace_once(settings_test, '    assert.equal(modern.missionValue, true);\n', '    assert.equal(modern.missionValue, true);\n    assert.equal(modern.missionRequirements, true);\n', "modern state Mission Requirements assertion")
SETTINGS_TEST.write_text(settings_test, encoding="utf-8")

preflight = PREFLIGHT.read_text(encoding="utf-8")
preflight = replace_once(
    preflight,
    '  .github/scripts/test_mission_value_contract.py\n  .github/scripts/test_transport_sweep_lssm_contract.py\n',
    '  .github/scripts/test_mission_value_contract.py\n  .github/scripts/test_mission_requirements_contract.py\n  .github/scripts/test_transport_sweep_lssm_contract.py\n',
    "full preflight Mission Requirements contract",
)
PREFLIGHT.write_text(preflight, encoding="utf-8")

for path in (DIAGNOSTIC, DIAGNOSTIC_PACKAGE, OLD_PACKAGE):
    if path.exists():
        path.unlink()

subprocess.run(["bash", str(PREFLIGHT), "--contracts"], cwd=ROOT, check=True)
validation = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
if validation.returncode != 0:
    raise SystemExit(validation.returncode)
doc_audit = subprocess.run([sys.executable, str(DOC_AUDIT), "--allow-release-candidate"], cwd=ROOT)
if doc_audit.returncode != 0:
    raise SystemExit(doc_audit.returncode)
print("Updated Settings/Ops routing inventory and deterministic Mission Requirements preflight")
