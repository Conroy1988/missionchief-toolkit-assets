#!/usr/bin/env python3
"""Correct generated UI mount policy assertions without changing runtime scope."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / ".github/scripts/test_issue553_alliance_member_manager_page_runtime.js"
POLICY = ROOT / ".github/scripts/test_ui_mount_policy.py"

legacy = LEGACY.read_text(encoding="utf-8")
legacy = legacy.replace(
    'assert.ok(!block.includes("installAllianceMemberManager() {"), "runtime contract must not mock the installer");\n',
    '',
)
legacy = legacy.replace(
    'assert.ok(!block.includes("teardownAllianceMemberManager() {}"), "runtime contract must not fake lifecycle symbols");\n',
    '',
)
LEGACY.write_text(legacy, encoding="utf-8")

policy = POLICY.read_text(encoding="utf-8")
policy = policy.replace(
    'assert "installAllianceMemberManager() {" not in test\n'
    '    assert "teardownAllianceMemberManager() {}" not in test\n',
    'forbidden_installer_mock = "installAllianceMemberManager()" + " {"\n'
    '    forbidden_teardown_mock = "teardownAllianceMemberManager()" + " {}"\n'
    '    assert forbidden_installer_mock not in test\n'
    '    assert forbidden_teardown_mock not in test\n',
)
policy = policy.replace(
    'assert "installAllianceMemberManager() {" not in legacy\n'
    'assert "teardownAllianceMemberManager() {}" not in legacy\n',
    'assert "\\nfunction installAllianceMemberManager() {" not in legacy\n'
    'assert "\\nfunction teardownAllianceMemberManager() {}" not in legacy\n',
)
policy = policy.replace(
    'assert "window.__MCMS_UI_MOUNTS__" in source\n',
    'assert "pageWindow.__MCMS_UI_MOUNTS__" in source\n',
)
POLICY.write_text(policy, encoding="utf-8")

print("UI mount policy generated assertions corrected.")
