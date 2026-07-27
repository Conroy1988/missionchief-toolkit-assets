#!/usr/bin/env python3
"""Repair the v8.1.0 member-manager document-start hook for minimal boot harnesses."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_alliance_member_manager_contract.py"

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

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                queueAllianceMemberManagerMenuControl();
                reconcileAllianceMemberManager();
            }, { once: true });
        } else {
            queueAllianceMemberManagerMenuControl();
            reconcileAllianceMemberManager();
        }
    }
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, OLD, NEW, "member-manager startup block")
    SOURCE.write_text(source, encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    marker = '        "document.addEventListener(\'DOMContentLoaded\'",\n'
    guard = '        "typeof document.addEventListener === \'function\'",\n'
    if guard not in contract:
        contract = replace_once(contract, marker, guard + marker, "member-manager guard contract")
        CONTRACT.write_text(contract, encoding="utf-8")

    print("Repaired v8.1.0 member-manager startup hook with a minimal-document capability guard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
