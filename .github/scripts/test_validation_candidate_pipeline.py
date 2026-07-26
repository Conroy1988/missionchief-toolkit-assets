#!/usr/bin/env python3
"""Static and executable contracts for artifact-only canonical validation."""
from __future__ import annotations

import base64
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / ".github/workflows/validate-userscript.yml"
AUTOMATIC = ROOT / ".github/workflows/auto-release-after-validation.yml"
OWNER = ROOT / ".github/workflows/owner-release-command.yml"
RELEASE = ROOT / ".github/workflows/release-toolkit.yml"
SYNC = ROOT / ".github/scripts/sync_greasyfork_root_mirror.sh"
VERIFIER = ROOT / ".github/scripts/verify_validation_candidate.py"
DASHBOARD = ROOT / "status/release-dashboard.json"
DASHBOARD_GENERATOR = ROOT / ".github/scripts/generate_release_dashboard.py"
RETIRED_RECONCILER = ROOT / ".github/scripts/reconcile_validation_dashboard.py"


def require(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{label} is missing required marker: {marker}")


def forbid(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise AssertionError(f"{label} contains forbidden marker: {marker}")


def emit_reconciled_readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    replacements = (
        ('## **Current verified release: `v8.0.2` · Development candidate: `v8.0.3`**', '## **Current verified release: `v8.0.3`**'),
        ('#current-release-signal--v802', '#current-release-signal--v803'),
        ('| **Production release** | 🟢 | GitHub Release `v8.0.2` published |', '| **Production release** | 🟢 | GitHub Release `v8.0.3` published |'),
        ('| **Version** | `8.0.2` |', '| **Version** | `8.0.3` |'),
        ('| **Release focus** | Godfather layout and payout-audio hotfix |', '| **Release focus** | Godfather seven-second duration and dock-clearance hotfix |'),
        ('| **Validated SHA-256** | `5a33ed92ca3c3207d421654c8cd9370f95a6127a4ec759b4924412f19b36c474` |', '| **Validated SHA-256** | `773d6686fdcfe0af5901f54bdd58c58cf0ef8503bddaae354f32ed25879ac19b` |'),
        ('| **GitHub Release** | [`v8.0.2`](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v8.0.2) |', '| **GitHub Release** | [`v8.0.3`](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v8.0.3) |'),
        ('| **Private backup** | `071c56229fc9a680f9ccbf5cddb5f57b83935958` |', '| **Private backup** | `be6f8a187c4215053a5619acedce31b7f308577a` |'),
    )
    for old, new in replacements:
        if text.count(old) != 1:
            raise AssertionError(f"Unexpected README token count: {old!r}")
        text = text.replace(old, new, 1)
    signal = """# v8.0.3 release signal

> **GODFATHER DURATION AND PAYOUT-POSITION HOTFIX // VERIFIED PRODUCTION**

Version **8.0.3** defaults the Godfather Offer flash to seven seconds when the normal four-second default is still active, preserves non-default user choices, and raises/compacts the payout on short-height layouts so the complete banner clears the command dock.

---
"""
    text, count = re.subn(r"# v8\.0\.3 hotfix signal\n.*?\n---\n", signal, text, count=1, flags=re.S)
    if count != 1:
        raise AssertionError("Unexpected v8.0.3 signal section")
    release = """# Current release signal — v8.0.3

> **CHANNEL UPDATE // GODFATHER SEVEN-SECOND OFFER AND DOCK CLEARANCE**

Version 8.0.3 completed the Godfather payout repair with a seven-second theme default, one-second duration increments and stronger short-height clearance above the command dock.

- Existing non-default payout durations remain unchanged.
- The verified stereo payout audio remains byte-identical and digest-protected.
- The v7 native MissionChief boundary and every retained operational system remain in force.

---
"""
    text, count = re.subn(r"# Current release signal — v8\.0\.2\n.*?\n---\n", release, text, count=1, flags=re.S)
    if count != 1:
        raise AssertionError("Unexpected current release section")
    print("PIPELINE_V4_README_B64=" + base64.b64encode(text.encode("utf-8")).decode("ascii"))


def main() -> int:
    validation = VALIDATION.read_text(encoding="utf-8")
    automatic = AUTOMATIC.read_text(encoding="utf-8")
    owner = OWNER.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    sync = SYNC.read_text(encoding="utf-8")
    generator = DASHBOARD_GENERATOR.read_text(encoding="utf-8")
    reconciler = RETIRED_RECONCILER.read_text(encoding="utf-8")
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))

    require(validation, [
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Write immutable validation candidate evidence",
        "missionchief-toolkit-validation-candidate-${{ github.sha }}",
        "publicMainChanged: false",
        "releaseDashboardChanged: false",
        "verify_validation_candidate.py --self-test",
    ], "Canonical validation workflow")
    forbid(validation, [
        "contents: write",
        "reconcile_validation_dashboard.py",
        "status/release-dashboard.json",
        "git commit",
        "git push",
        "git pull --rebase",
        "github-actions[bot]",
    ], "Canonical validation workflow")

    require(automatic, [
        "github.event.workflow_run.event == 'push'",
        "github.event.workflow_run.head_sha",
        "github.event.workflow_run.id",
        "missionchief-toolkit-validation-candidate-${VALIDATED_SHA}",
        "actions/runs/${VALIDATION_RUN_ID}/artifacts",
        "verify_validation_candidate.py",
        "CURRENT_MAIN=\"$(git rev-parse origin/main)\"",
        "gh release view \"v${VERSION}\"",
        "Dashboard candidate state used: no",
    ], "Automatic release workflow")
    forbid(automatic, [
        ".distributionCandidate",
        ".status.validation",
        "status/release-dashboard.json",
    ], "Automatic release workflow")

    require(owner, [
        "Freshly validate requested main candidate",
        "python3 .github/scripts/validate_userscript.py",
        "persist-credentials: false",
        "gh release view \"v${VERSION}\"",
        "dist/release-manifest.json",
    ], "Owner release workflow")
    forbid(owner, [
        ".distributionCandidate",
        "status/release-dashboard.json",
        "Verify requested version is a validated candidate",
    ], "Owner release workflow")

    require(sync, [
        "git add dist \"$ROOT_USER\" \"$ROOT_TXT\"",
        "Publish Toolkit ${VERSION} stable distribution source",
        "Stable distribution publication commit",
    ], "Stable distribution publication helper")
    require(release, [
        "run: bash .github/scripts/sync_greasyfork_root_mirror.sh",
        "Record successful release, manifest, announcement and speed state",
        "python3 .github/scripts/build_stable_update_manifest.py",
    ], "Production release workflow")

    if "distributionCandidate" in dashboard or "releaseDryRun" in dashboard:
        raise AssertionError("Persistent release dashboard still contains transient validation state")
    require(generator, [
        'sanitized.pop("distributionCandidate", None)',
        'sanitized.pop("releaseDryRun", None)',
        '"storage": "workflow-artifact"',
    ], "Dashboard stable-ledger sanitizer")
    forbid(generator, ["data.get(\"distributionCandidate\"", "candidate.get("], "Dashboard generator")
    require(reconciler, [
        "Retired compatibility stub",
        "is retired; use the exact canonical-validation artifact instead",
    ], "Retired validation-dashboard reconciler")
    forbid(reconciler, [
        "json.loads",
        "write_text",
        "def reconcile",
        "status[",
        "distributionCandidate",
    ], "Retired validation-dashboard reconciler")

    result = subprocess.run(["python3", str(VERIFIER), "--self-test"], cwd=ROOT)
    if result.returncode != 0:
        raise AssertionError("Validation candidate verifier self-tests failed")

    emit_reconciled_readme()
    print("Validation candidate pipeline passed: artifact authority, exact-run consumption and stable-only dist publication.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
