#!/usr/bin/env python3
"""Structural security contract for the reviewed development-package workflow."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "apply-development-package.yml"
VALIDATOR = ROOT / ".github" / "workflows" / "validate-development-package-workflow.yml"
SECURITY_POLICY = ROOT / ".github" / "actions-security-policy.json"
DOC = ROOT / "docs" / "DEVELOPMENT_PACKAGE_WORKFLOW.md"
WORKFLOW_PATH = ".github/workflows/apply-development-package.yml"


def require(text: str, marker: str, label: str | None = None) -> None:
    if marker not in text:
        raise AssertionError(label or f"Missing required marker: {marker}")


def forbid(text: str, marker: str, label: str | None = None) -> None:
    if marker in text:
        raise AssertionError(label or f"Forbidden marker present: {marker}")


def main() -> int:
    source = WORKFLOW.read_text(encoding="utf-8")

    # The command surface must be an owner comment on an existing open PR.
    for marker in (
        "on:\n  issue_comment:",
        "github.event.sender.login == 'Conroy1988'",
        "github.event.issue.pull_request != null",
        "github.event.issue.state == 'open'",
        "/preflight-development-package",
        "/apply-development-package",
        "Verify existing pull request context",
        "The pull request must target main.",
        "Fork pull requests are not accepted by the package workflow.",
        "The command branch does not match the pull request head branch.",
        "The pull request must be owned by Conroy1988.",
    ):
        require(source, marker)

    # The workflow must never manufacture repository records.
    for marker in (
        "github.event.issue.pull_request == null",
        "gh pr create",
        "gh issue create",
        "Open or update pull request",
        "CREATE_ISSUE",
        "CREATE_PR",
    ):
        forbid(source, marker)

    # The GitHub Actions token is read-only except for PR conversation comments.
    permissions_start = source.index("permissions:")
    jobs_start = source.index("\njobs:", permissions_start)
    permissions = source[permissions_start:jobs_start]
    require(permissions, "contents: read")
    require(permissions, "pull-requests: read")
    require(permissions, "issues: write")
    forbid(permissions, "contents: write")
    forbid(permissions, "pull-requests: write")

    # Runs serialize per existing PR, not per throwaway issue or branch.
    require(source, "group: development-package-pr-${{ needs.command.outputs.pr_number }}")
    require(source, "cancel-in-progress: true")
    forbid(source, "group: development-package-${{ github.event.issue.number }}")

    # Apply must be owner-authenticated. The read-only token may service preflight,
    # but the explicit owner-token gate must execute before any apply checkout/push.
    require(source, "Require owner push token")
    require(source, "secrets.DEVELOPMENT_PR_TOKEN")
    require(source, "DEVELOPMENT_PR_TOKEN is required for owner-authenticated PR updates.")
    require(source, "token: ${{ needs.command.outputs.mode == 'apply' && secrets.DEVELOPMENT_PR_TOKEN || github.token }}")
    require(source, "git config user.name \"Conroy1988\"")
    require(source, "27301455+Conroy1988@users.noreply.github.com")
    forbid(source, "git config user.name \"github-actions[bot]\"")

    token_gate = source.index("      - name: Require owner push token")
    checkout = source.index("      - name: Check out exact authorized commit")
    push = source.index("          git push --force-with-lease")
    if not token_gate < checkout < push:
        raise AssertionError("Owner-token gate must precede apply checkout and branch publication")

    # Fingerprints, exact-head leases and validation remain mandatory.
    for marker in (
        "development-package-preflight-passed:${fingerprint}",
        "development-package-preflight-stopped:${fingerprint}",
        "development-package-apply:${fingerprint}",
        "This exact package has not passed preflight against the current main branch.",
        "--force-with-lease=\"refs/heads/${BRANCH}:${EXPECTED_HEAD}\"",
        "python3 .github/scripts/validate_userscript.py",
        "node --check src/MissionChief_Map_Command_Toolkit.user.js",
        "cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt",
    ):
        require(source, marker)

    preflight_start = source.index("      - name: Run neutral preflight")
    apply_start = source.index("      - name: Rebase package onto exact main")
    preflight = source[preflight_start:apply_start]
    require(preflight, "exit 0")
    forbid(preflight, "git push")

    apply = source[apply_start:]
    require(apply, "git push --force-with-lease")
    require(apply, "gh pr comment")
    forbid(apply, "gh pr create")
    forbid(apply, "gh issue create")

    validator = VALIDATOR.read_text(encoding="utf-8")
    for marker in (
        "pull_request:",
        WORKFLOW_PATH,
        ".github/actions-security-policy.json",
        "python3 .github/scripts/test_development_package_workflow.py",
    ):
        require(validator, marker)

    policy = json.loads(SECURITY_POLICY.read_text(encoding="utf-8"))
    allowed = policy.get("allowedWritePermissions", {}).get(WORKFLOW_PATH)
    if allowed != ["issues"]:
        raise AssertionError(f"Development workflow write permissions must be exactly ['issues']; found {allowed!r}")
    if "pull_request_target" not in policy.get("forbiddenTriggers", []):
        raise AssertionError("pull_request_target must remain forbidden")

    documentation = DOC.read_text(encoding="utf-8")
    for marker in (
        "existing open pull request",
        "never creates an issue, branch, or pull request",
        "owner-authenticated",
        "DEVELOPMENT_PR_TOKEN",
        "/preflight-development-package",
        "/apply-development-package",
        "Genuine publish failures remain red",
    ):
        require(documentation, marker)

    print("Development-package workflow policy passed: existing PR only, owner-authenticated apply, no issue/PR creation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
