#!/usr/bin/env python3
"""Permanent contract for the Toolkit-native Alliance Member Manager."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
SITE_DATA = ROOT / "docs" / "site-data.json"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
PERFORMANCE = ROOT / ".github" / "performance-budget.json"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    start_marker = "    // <mcms-alliance-member-manager>"
    end_marker = "    // </mcms-alliance-member-manager>"
    assert source.count(start_marker) == 1
    assert source.count(end_marker) == 1
    start = source.index(start_marker)
    end = source.index(end_marker, start) + len(end_marker)
    block = source[start:end]

    assert re.search(r"^// @version\s+8\.1\.3$", source, re.MULTILINE)
    assert "version: '8.1.3'" in source
    for marker in [
        "mcms_alliance_member_manager_enabled_v1",
        "Alliance Member Manager",
        "Role",
        "Activity",
        "Sort by",
        "Load All Member Pages",
        "All Member Pages Loaded",
        "All roles",
        "No role",
        "All members",
        "Online",
        "Offline",
        "Original order",
        "Member name",
        "Alliance role",
        "Showing ${visible} of ${context.members.size} members",
        r"alliance\/members|verband\/mitglieder",
        "img.online_icon",
        "user_(?<state>blue|gray|green|red|yellow)",
        "new AbortController()",
        "context.abortController?.abort()",
        "credentials: 'same-origin'",
        "for (let page = 1; page <= context.totalPages; page += 1)",
        "const response = await fetch(",
        "document.importNode(row, true)",
        "context.importedRows.forEach(row => row.remove())",
        "context.originalRows.forEach(row =>",
        "typeof document.addEventListener === 'function'",
        "document.readyState !== 'loading'",
        "document.addEventListener('DOMContentLoaded', reconcileAllianceMemberManager",
        "{ once: true }",
        "allianceMemberManagerOtherOwnerPresent()",
        "#allianceMemberList-controls",
    ]:
        assert marker in block, marker

    for forbidden in [
        "setInterval(",
        "new MutationObserver(",
        "requestAnimationFrame(",
        "allianceMemberManagerMapBlockerButton",
        "ensureAllianceMemberManagerMenuControl",
        "queueAllianceMemberManagerMenuControl",
        "allianceMemberManagerMenuObserver",
        "GM_xmlhttpRequest",
        "last seen",
        "lastSeen",
        "getElementById(",
    ]:
        assert forbidden not in block, forbidden

    for marker in [
        "function makeAllianceMemberManagerToggleButton()",
        'data-action="toggle-alliance-member-manager"',
        'data-mcms-alliance-member-manager-toggle="true"',
        '<div class="mcms-section-label" data-mcms-alliance-operations="label">Alliance Operations</div>',
        '<div class="mcms-grid-2" data-mcms-alliance-operations="controls">',
        "${makeAllianceMemberManagerToggleButton()}",
        "if (action === 'toggle-alliance-member-manager')",
        "setAllianceMemberManagerEnabled(!allianceMemberManagerEnabled())",
        "updateAllianceMemberManagerMenuControl();",
    ]:
        assert marker in source, marker

    assert block.index("for (let page = 1;") < block.index("await fetch(")
    assert block.count("await fetch(") == 1
    assert block.count("new AbortController()") == 1
    assert block.count("new MutationObserver(") == 0
    assert block.count("data-mcms-alliance-member-manager-toggle") == 1
    assert source.count("${makeAllianceMemberManagerToggleButton()}") == 1
    assert source.count('data-action="toggle-alliance-member-manager"') == 1

    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert "## [8.1.3] - 2026-07-27" in changelog
    assert "### Canonical Alliance Member Manager Tools rendering" in changelog
    assert "## [8.1.2] - 2026-07-27" in changelog
    assert "## [8.1.1] - 2026-07-27" in changelog
    assert "## [8.1.0] - 2026-07-27" in changelog

    site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
    alliance = [item for item in site_data["featureCategories"] if item.get("name") == "Alliance operations"]
    assert len(alliance) == 1
    features = alliance[0]["features"]
    assert len(features) == 1
    assert features[0]["name"] == "Alliance Member Manager"
    assert "Load all pages only on request" in features[0]["details"]

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert ".github/scripts/test_alliance_member_manager_contract.py" in preflight
    assert "test_issue553_alliance_member_manager_menu_runtime.js" in preflight
    assert "test_issue554_alliance_member_manager_rollback.py" not in preflight

    performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
    assert performance["revision"] == "2026-07-27-issue-553-canonical-menu-render"
    assert performance["transitionApproval"]["issue"] == 553
    assert performance["transitionApproval"]["version"] == "8.1.3"
    assert performance["transitionApproval"]["approvedNetworkRequestDelta"] == 1
    assert performance["absoluteLimits"]["network_request_calls"] == 5

    print(
        "Alliance Member Manager contract passed: canonical Tools markup, panel-owned action routing, "
        "persisted state reconciliation, responsive member controls and zero added observers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
