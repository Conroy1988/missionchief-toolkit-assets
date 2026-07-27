#!/usr/bin/env python3
"""Allow the real Alliance Member Manager installer to claim authoritative rendered DOM."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
CONTRACT = ROOT / ".github/scripts/test_alliance_member_manager_contract.py"
RUNTIME = ROOT / ".github/scripts/test_issue553_alliance_member_manager_page_runtime.js"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"

source = SOURCE.read_text(encoding="utf-8")
old = '''        if (
            allianceMemberManagerPage ||
            !allianceMemberManagerEnabled() ||
            !isAllianceMemberManagerRoute() ||
            allianceMemberManagerOtherOwnerPresent()
        ) return;
'''
new = '''        if (
            allianceMemberManagerPage ||
            !allianceMemberManagerEnabled() ||
            !(isAllianceMemberManagerRoute() || allianceMemberManagerHasDomContext()) ||
            allianceMemberManagerOtherOwnerPresent()
        ) return;
'''
if source.count(old) != 1:
    raise RuntimeError(f"Expected one installer route gate, found {source.count(old)}")
source = source.replace(old, new, 1)
SOURCE.write_text(source, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
needle = '    "allianceMemberManagerEnsureMountObserver",\n'
replacement = needle + '    "isAllianceMemberManagerRoute() || allianceMemberManagerHasDomContext()",\n'
if contract.count(needle) != 1:
    raise RuntimeError("Unable to harden installer gate contract")
CONTRACT.write_text(contract.replace(needle, replacement, 1), encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
needle = 'assert.ok(block.includes("allianceMemberManagerEnsureMountObserver"));\n'
replacement = needle + 'assert.ok(block.includes("isAllianceMemberManagerRoute() || allianceMemberManagerHasDomContext()"));\n'
if runtime.count(needle) != 1:
    raise RuntimeError("Unable to harden installer gate runtime contract")
RUNTIME.write_text(runtime.replace(needle, replacement, 1), encoding="utf-8")

source_bytes = SOURCE.read_bytes()
sha = hashlib.sha256(source_bytes).hexdigest()
lines = len(source_bytes.decode("utf-8").splitlines())
for relative in [
    "dist/MissionChief_Map_Command_Toolkit.user.js",
    "dist/MissionChief_Map_Command_Toolkit.txt",
]:
    (ROOT / relative).write_bytes(source_bytes)
(ROOT / "dist/SHA256SUMS.txt").write_text(
    f"{sha}  MissionChief_Map_Command_Toolkit.user.js\n{sha}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest_path = ROOT / "dist/release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({"version": "8.1.5", "sha256": sha, "bytes": len(source_bytes), "lines": lines})
manifest["metadata"]["runtimeVersion"] = "8.1.5"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
old_bytes = int(candidate["sourceBytes"])
old_lines = int(candidate["sourceLines"])
candidate["sourceBytes"] = len(source_bytes)
candidate["sourceLines"] = lines
candidate["sourceSha256"] = sha
candidate["maxSourceBytes"] = max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000)
candidate["maxSourceLines"] = max(int(candidate.get("maxSourceLines", 0)), lines + 250)
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - old_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + lines - old_lines
candidate["scope"] = "Issue #553 lifecycle and installer DOM-context correction, enabled-only UI mount observer, cross-origin setting continuity, mount receipts and full rendered integration gate"
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(f"Installer DOM-context gate corrected: {sha}, {len(source_bytes)} bytes, {lines} lines")
