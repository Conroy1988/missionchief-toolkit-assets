#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
policy = json.loads((ROOT / ".github/ui-mount-policy.json").read_text(encoding="utf-8"))
assert policy["schemaVersion"] == 1
source = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/validate-userscript.yml").read_text(encoding="utf-8")
legacy = (ROOT / ".github/scripts/test_issue553_alliance_member_manager_page_runtime.js").read_text(encoding="utf-8")
for name, surface in policy["surfaces"].items():
    fixture = ROOT / surface["fixture"]
    integration = ROOT / surface["integrationTest"]
    assert fixture.is_file(), fixture
    assert integration.is_file(), integration
    test = integration.read_text(encoding="utf-8")
    assert surface["sourceMarker"] in source
    assert "managerBlock" in test and "vm.runInContext" in test
    for scenario in surface["requiredScenarios"]:
        assert scenario in test, scenario
    forbidden_installer_mock = "installAllianceMemberManager()" + " {"
    forbidden_teardown_mock = "teardownAllianceMemberManager()" + " {}"
    assert forbidden_installer_mock not in test
    assert forbidden_teardown_mock not in test
assert "jsdom@26.1.0" in workflow
assert "node .github/scripts/test_ui_mount_integration.mjs" in workflow
assert "\nfunction installAllianceMemberManager() {" not in legacy
assert "\nfunction teardownAllianceMemberManager() {}" not in legacy
assert "pageWindow.__MCMS_UI_MOUNTS__" in source
assert "data-mcms-alliance-member-manager-mount" in source
print("UI mount policy passed: real installer execution, rendered fixture, delayed neutral-route mount, rerender recovery, mount receipt and no mocked lifecycle substitutions.")
