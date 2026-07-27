#!/usr/bin/env python3
"""Apply the reviewed v8.1.0 bootstrap-tail compatibility fix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
CONTRACT = ROOT / ".github" / "scripts" / "test_alliance_member_manager_contract.py"

OLD = """    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            queueAllianceMemberManagerMenuControl();
            reconcileAllianceMemberManager();
        }, { once: true });
    } else {
        queueAllianceMemberManagerMenuControl();
        reconcileAllianceMemberManager();
    }
"""

NEW = """    if (document.readyState !== 'loading') {
        queueAllianceMemberManagerMenuControl();
        reconcileAllianceMemberManager();
    } else {
        document.addEventListener('DOMContentLoaded', () => {
            queueAllianceMemberManagerMenuControl();
            reconcileAllianceMemberManager();
        }, { once: true });
    }
"""


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    if hashlib.sha256(source.encode()).hexdigest() != "549ad43f6c5c0b1aaaf2d7794bca0ccb0e689b69357ea6ca52e3deb400bfbf85":
        raise SystemExit("Unexpected pre-fix v8.1.0 source authority")
    if source.count(OLD) != 1:
        raise SystemExit(f"Expected one Alliance Member Manager bootstrap block, found {source.count(OLD)}")
    source = source.replace(OLD, NEW, 1)
    SOURCE.write_text(source, encoding="utf-8")

    source_bytes = len(source.encode())
    source_lines = len(source.splitlines())
    source_sha = hashlib.sha256(source.encode()).hexdigest()
    if source_bytes != 1641511 or source_lines != 25006:
        raise SystemExit(
            f"Bootstrap reordering changed physical footprint: bytes={source_bytes}, lines={source_lines}"
        )

    fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
    candidate = fixture["v8Candidate"]
    if candidate.get("issue") != 551 or candidate.get("version") != "8.1.0":
        raise SystemExit("v8.1.0 source-headroom authority is missing")
    if candidate.get("sourceSha256") != "549ad43f6c5c0b1aaaf2d7794bca0ccb0e689b69357ea6ca52e3deb400bfbf85":
        raise SystemExit("v8.1.0 source-headroom pre-fix hash changed")
    candidate["sourceSha256"] = source_sha
    candidate["scope"] = (
        "Issue #551 native Alliance Member Manager with opt-in English role/activity controls, "
        "explicit sequential member-page loading, deterministic teardown and boot-tail-safe startup"
    )
    HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    marker = "        \"document.addEventListener('DOMContentLoaded'\",\n"
    readiness = "        \"document.readyState !== 'loading'\",\n"
    if readiness not in contract:
        if contract.count(marker) != 1:
            raise SystemExit("Alliance Member Manager contract bootstrap marker changed")
        contract = contract.replace(marker, readiness + marker, 1)
        CONTRACT.write_text(contract, encoding="utf-8")

    print(
        "Applied v8.1.0 bootstrap-tail compatibility fix: equivalent document-ready startup, "
        "unchanged physical footprint and reviewed source-headroom hash."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
