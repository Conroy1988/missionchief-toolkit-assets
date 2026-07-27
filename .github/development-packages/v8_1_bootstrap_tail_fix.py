#!/usr/bin/env python3
"""Apply the reviewed v8.1.0 boot-tail and minimal-document compatibility fix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
CONTRACT = ROOT / ".github" / "scripts" / "test_alliance_member_manager_contract.py"

PRE_FIX_SHA = "549ad43f6c5c0b1aaaf2d7794bca0ccb0e689b69357ea6ca52e3deb400bfbf85"
BASELINE_BYTES = 1614530
BASELINE_LINES = 24377

OLD = """    document.addEventListener('click', event => {
        const target = event.target instanceof Element ? event.target : null;
        const toggle = target?.closest(`[${ALLIANCE_MEMBER_MANAGER.menuAttribute}]`);
        if (toggle) {
            event.preventDefault();
            event.stopPropagation();
            setAllianceMemberManagerEnabled(!allianceMemberManagerEnabled());
            queueAllianceMemberManagerMenuControl();
            return;
        }
        if (target?.closest(`#${SCRIPT.controlId}, #${SCRIPT.panelId}`)) {
            queueAllianceMemberManagerMenuControl();
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            queueAllianceMemberManagerMenuControl();
            reconcileAllianceMemberManager();
        }, { once: true });
    } else {
        queueAllianceMemberManagerMenuControl();
        reconcileAllianceMemberManager();
    }
"""

NEW = """    if (typeof document.addEventListener === 'function') {
        document.addEventListener('click', event => {
            const target = event.target instanceof Element ? event.target : null;
            const toggle = target?.closest(`[${ALLIANCE_MEMBER_MANAGER.menuAttribute}]`);
            if (toggle) {
                event.preventDefault();
                event.stopPropagation();
                setAllianceMemberManagerEnabled(!allianceMemberManagerEnabled());
                queueAllianceMemberManagerMenuControl();
                return;
            }
            if (target?.closest(`#${SCRIPT.controlId}, #${SCRIPT.panelId}`)) {
                queueAllianceMemberManagerMenuControl();
            }
        });

        if (document.readyState !== 'loading') {
            queueAllianceMemberManagerMenuControl();
            reconcileAllianceMemberManager();
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                queueAllianceMemberManagerMenuControl();
                reconcileAllianceMemberManager();
            }, { once: true });
        }
    }
"""


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    if hashlib.sha256(source.encode()).hexdigest() != PRE_FIX_SHA:
        raise SystemExit("Unexpected pre-fix v8.1.0 source authority")
    if source.count(OLD) != 1:
        raise SystemExit(f"Expected one Alliance Member Manager startup block, found {source.count(OLD)}")
    source = source.replace(OLD, NEW, 1)
    SOURCE.write_text(source, encoding="utf-8")

    source_bytes = len(source.encode())
    source_lines = len(source.splitlines())
    source_sha = hashlib.sha256(source.encode()).hexdigest()

    fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
    candidate = fixture["v8Candidate"]
    if candidate.get("issue") != 551 or candidate.get("version") != "8.1.0":
        raise SystemExit("v8.1.0 source-headroom authority is missing")
    if candidate.get("sourceSha256") != PRE_FIX_SHA:
        raise SystemExit("v8.1.0 source-headroom pre-fix hash changed")
    if source_bytes > int(candidate.get("maxSourceBytes", 0)):
        raise SystemExit(f"Corrected source exceeds byte ceiling: {source_bytes}")
    if source_lines > int(candidate.get("maxSourceLines", 0)):
        raise SystemExit(f"Corrected source exceeds line ceiling: {source_lines}")

    candidate["sourceBytes"] = source_bytes
    candidate["sourceLines"] = source_lines
    candidate["sourceSha256"] = source_sha
    candidate["approvedGrowth"] = {
        "sourceBytes": source_bytes - BASELINE_BYTES,
        "sourceLines": source_lines - BASELINE_LINES,
        "templateBytes": 0,
        "templateLines": 0,
    }
    candidate["scope"] = (
        "Issue #551 native Alliance Member Manager with opt-in English role/activity controls, "
        "explicit sequential member-page loading, deterministic teardown, boot-tail-safe startup "
        "and minimal-document listener capability guarding"
    )
    HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    marker = "        \"document.addEventListener('DOMContentLoaded'\",\n"
    required = [
        "        \"typeof document.addEventListener === 'function'\",\n",
        "        \"document.readyState !== 'loading'\",\n",
    ]
    if contract.count(marker) != 1:
        raise SystemExit("Alliance Member Manager contract bootstrap marker changed")
    insertion = "".join(item for item in required if item not in contract)
    if insertion:
        contract = contract.replace(marker, insertion + marker, 1)

    invalid_route_literal = '        "alliance\\/members|verband\\/mitglieder",\n'
    raw_route_literal = '        r"alliance\\/members|verband\\/mitglieder",\n'
    if invalid_route_literal in contract:
        contract = contract.replace(invalid_route_literal, raw_route_literal, 1)
    CONTRACT.write_text(contract, encoding="utf-8")

    print(
        "Applied v8.1.0 boot compatibility fix: tail-safe readiness, minimal-document guard, "
        f"source={source_bytes} bytes/{source_lines} lines/{source_sha}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
