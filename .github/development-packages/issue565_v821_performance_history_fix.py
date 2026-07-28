#!/usr/bin/env python3
"""Preserve historical performance approvals while advancing v8.2.1."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PERFORMANCE = ROOT / ".github/performance-budget.json"
CONTRACT = ROOT / ".github/scripts/test_alliance_member_manager_contract.py"

performance = json.loads(PERFORMANCE.read_text(encoding="utf-8"))
history = performance.setdefault("approvalHistory", [])
required = [
    {
        "issue": 553,
        "version": "8.1.5",
        "approvedNetworkRequestDelta": 1,
        "scope": "Hardened Alliance Member Manager UI mount observation, structured receipts, visible mount states and full rendered integration gate.",
        "approvedMutationObserverDelta": 1,
    },
    dict(performance["transitionApproval"]),
]
for approval in required:
    if not any(
        item.get("issue") == approval.get("issue")
        and item.get("version") == approval.get("version")
        for item in history
    ):
        history.append(approval)
history.sort(key=lambda item: (str(item.get("version", "")), int(item.get("issue", 0))))
PERFORMANCE.write_text(json.dumps(performance, indent=2) + "\n", encoding="utf-8")

text = CONTRACT.read_text(encoding="utf-8")
old = '''performance = json.loads((ROOT / ".github/performance-budget.json").read_text(encoding="utf-8"))
assert performance["revision"] == "2026-07-27-issue-553-ui-mount-hardening"
assert performance["transitionApproval"]["version"] == "8.1.5"
assert performance["transitionApproval"]["approvedMutationObserverDelta"] == 1
'''
new = '''performance = json.loads((ROOT / ".github/performance-budget.json").read_text(encoding="utf-8"))
ui_mount_approval = next(
    (
        approval
        for approval in performance.get("approvalHistory", [])
        if approval.get("issue") == 553 and approval.get("version") == "8.1.5"
    ),
    None,
)
assert ui_mount_approval
assert ui_mount_approval["approvedMutationObserverDelta"] == 1
assert performance["absoluteLimits"]["mutation_observer_constructions"] >= 13
'''
if text.count(old) != 1:
    raise RuntimeError("Alliance Member Manager performance approval assertions changed")
CONTRACT.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Performance approval history now retains v8.1.5 UI mounting and v8.2.1 release-request transitions.")
