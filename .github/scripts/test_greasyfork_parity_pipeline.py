#!/usr/bin/env python3
"""Structural and executable contracts for the retired Greasy Fork importer."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "import-canonical-userscript.yml"
AUDITOR = ROOT / ".github" / "scripts" / "audit_greasyfork_canonical_parity.py"
BASELINE = ROOT / "status" / "source-baseline.json"


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise AssertionError(f"{label} contains forbidden marker: {marker}")


def main() -> int:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    auditor = AUDITOR.read_text(encoding="utf-8")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))

    require(workflow, [
        "name: Verify Greasy Fork Canonical Parity",
        "schedule:",
        'cron: "17 5 * * *"',
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Validate parity-auditor self-tests",
        "audit_greasyfork_canonical_parity.py --self-test",
        "Download live Greasy Fork distribution",
        "Audit GitHub canonical authority",
        "Upload immutable parity evidence",
        "missionchief-greasyfork-canonical-parity-${{ github.sha }}",
        "retention-days: 30",
        "Automatic importing is retired; owner review is required.",
    ], "Greasy Fork parity workflow")
    forbid(workflow, [
        "contents: write",
        "git commit",
        "git push",
        "git pull --rebase",
        "github-actions[bot]",
        "DEVELOPMENT_PR_TOKEN",
        "gh pr create",
        "status/source-baseline.json >",
        "cp \"$TEMP\" \"$TARGET\"",
    ], "Greasy Fork parity workflow")

    require(auditor, [
        '"authority": "GitHub canonical source"',
        '"automaticImportEnabled": False',
        '"publicMainChanged": False',
        '"canonicalSourceChanged": False',
        '"sourceBaselineChanged": False',
        '"pullRequestCreated": False',
        '"liveAheadRequiresOwnerReview": True',
        '"equalVersionHashMismatchRequiresOwnerReview": True',
        '"canonical-ahead"',
        '"live-ahead"',
        '"equal-version-content-mismatch"',
    ], "Greasy Fork parity auditor")
    forbid(auditor, [
        "git commit",
        "git push",
        "gh pr create",
        "DEVELOPMENT_PR_TOKEN",
    ], "Greasy Fork parity auditor")

    if baseline.get("schemaVersion") != 2:
        raise AssertionError("Historical source baseline must use schemaVersion 2")
    if baseline.get("recordType") != "historical-bootstrap-baseline":
        raise AssertionError("Source baseline must be explicitly historical")
    if baseline.get("automaticImportEnabled") is not False:
        raise AssertionError("Historical source baseline must disable automatic importing")
    if baseline.get("canonicalStatus") != "historical-bootstrap-record-github-authoritative":
        raise AssertionError("Source baseline must identify GitHub as current authority")
    if baseline.get("currentAuthority") != "src/MissionChief_Map_Command_Toolkit.user.js":
        raise AssertionError("Source baseline current authority path changed")

    result = subprocess.run(["python3", str(AUDITOR), "--self-test"], cwd=ROOT)
    if result.returncode != 0:
        raise AssertionError("Greasy Fork parity auditor self-tests failed")

    print("Greasy Fork parity pipeline passed: GitHub authority, read-only audit, no automatic import.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
