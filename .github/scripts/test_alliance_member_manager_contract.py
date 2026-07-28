#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
start = source.index("    // <mcms-alliance-member-manager>")
end = source.index("    // </mcms-alliance-member-manager>", start)
block = source[start:end]
metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
runtime = re.search(r"version:\s*'([^']+)'", source)
assert metadata and runtime and metadata.group(1) == runtime.group(1)
current_version = tuple(int(part) for part in metadata.group(1).split('.'))
assert current_version >= (8, 1, 5)
for marker in [
    "disposeAllianceMemberManager();",
    "allianceMemberManagerEnsureMountObserver",
    "isAllianceMemberManagerRoute() || allianceMemberManagerHasDomContext()",
    "allianceMemberManagerDisconnectMountObserver",
    "allianceMemberManagerMutationRelevant",
    "pageWindow.__MCMS_UI_MOUNTS__",
    "data-mcms-alliance-member-manager-mount",
    "GM_getValue",
    "GM_setValue",
    "'watching'",
    "'waiting'",
    "'mounted'",
    "'error'",
    "pill.textContent = !enabled ? 'OFF' : failed ? 'ERR' : mounted ? 'ON' : 'WAIT'",
    "Alliance Member Manager could not attach",
]: assert marker in block, marker
assert "teardownAllianceMemberManager" not in source
assert block.count("new Observer(") == 1
assert block.count("setInterval(") == 0
assert block.count("setTimeout(") == 0
assert "installAllianceMemberManager() {" not in (ROOT / ".github/scripts/test_ui_mount_integration.mjs").read_text(encoding="utf-8")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
assert "## [8.1.5] - 2026-07-27" in changelog
assert "### Hardened UI mounting and live member-page recovery" in changelog
performance = json.loads((ROOT / ".github/performance-budget.json").read_text(encoding="utf-8"))
assert performance["revision"] == "2026-07-27-issue-553-ui-mount-hardening"
assert performance["transitionApproval"]["version"] == "8.1.5"
assert performance["transitionApproval"]["approvedMutationObserverDelta"] == 1
preflight = (ROOT / ".github/scripts/run_userscript_preflight.sh").read_text(encoding="utf-8")
assert "test_ui_mount_policy.py" in preflight
workflow = (ROOT / ".github/workflows/validate-userscript.yml").read_text(encoding="utf-8")
assert "test_ui_mount_integration.mjs" in workflow
print("Alliance Member Manager contract passed: corrected lifecycle symbol, DOM-authoritative observation, cross-origin persistence, visible mount states, exception recovery and full rendered integration gate.")
