#!/usr/bin/env python3
"""Permanent contract for Issue #554 Alliance Member Manager rollback."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
SITE_DATA = ROOT / "docs" / "site-data.json"
HELP = ROOT / "help" / "index.html"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
PERFORMANCE = ROOT / ".github" / "performance-budget.json"

source = SOURCE.read_text(encoding="utf-8")
assert re.search(r"^// @version\s+8\.1\.1$", source, re.MULTILINE)
assert "version: '8.1.1'" in source
for forbidden in (
    "<mcms-alliance-member-manager>",
    "mcms_alliance_member_manager_enabled_v1",
    "data-mcms-alliance-member-manager-toggle",
    "Alliance Member Manager",
    "Load All Member Pages",
):
    assert forbidden not in source, forbidden

assert "## [8.1.1] - 2026-07-27" in CHANGELOG.read_text(encoding="utf-8")
assert "Alliance Member Manager" not in HELP.read_text(encoding="utf-8")
site = json.loads(SITE_DATA.read_text(encoding="utf-8"))
assert not any(item.get("name") == "Alliance operations" for item in site.get("featureCategories", []))
performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
assert performance["absoluteLimits"]["network_request_calls"] == 4
assert performance["relativeLimits"]["network_request_calls"]["warnDelta"] == 0
assert performance["relativeLimits"]["network_request_calls"]["failDelta"] == 0
preflight = PREFLIGHT.read_text(encoding="utf-8")
assert ".github/scripts/test_alliance_member_manager_contract.py" not in preflight
assert ".github/scripts/test_issue554_alliance_member_manager_rollback.py" in preflight
print("Issue #554 rollback contract passed: Alliance Member Manager removed and pre-feature Toolkit behaviour restored.")
