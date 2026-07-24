#!/usr/bin/env python3
"""Static policy checks for the reviewed development-package workflow."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "apply-development-package.yml"
VALIDATOR = ROOT / ".github" / "workflows" / "validate-development-package-workflow.yml"
SECURITY_POLICY = ROOT / ".github" / "actions-security-policy.json"
DOC = ROOT / "docs" / "DEVELOPMENT_PACKAGE_WORKFLOW.md"


def require(text: str, marker: str) -> None:
    if marker not in text:
        raise AssertionError(f"Missing development-package workflow marker: {marker}")


def forbid(text: str, marker: str) -> None:
    if marker in text:
        raise AssertionError(f"Forbidden development-package workflow marker: {marker}")


def main() -> int:
    source = WORKFLOW.read_text(encoding="utf-8")

    for marker in (
        "name: Apply Reviewed Development Package",
        "/preflight-development-package",
        "/apply-development-package",
        "github.event.issue.pull_request != null",
        "github.event.issue.state == 'open'",
        "Verify existing pull request context",
        "The pull request must target main.",
        "Fork pull requests are not accepted by the package workflow.",
        "The command branch does not match the pull request head branch.",
        "The pull request must be owned by Conroy1988.",
        "group: development-package-pr-${{ needs.command.outputs.pr_number }}",
        "cancel-in-progress: true",
        "This exact package has not passed preflight against the current main branch.",
        "development-package-preflight-passed:${fingerprint}",
        "development-package-preflight-stopped:${fingerprint}",
        "development-package-apply:${fingerprint}",
        "Require owner push token",
        "secrets.DEVELOPMENT_PR_TOKEN",
        "DEVELOPMENT_PR_TOKEN is required for owner-authenticated PR updates.",
        "git config user.name \"Conroy1988\"",
        "27301455+Conroy1988@users.noreply.github.com",
        "Existing pull request updated; no issue or pull request was created",
        "Record neutral skip",
        "Record exact publish failure",
        "failure() && needs.command.outputs.mode == 'apply'",
        "--force-with-lease=\"refs/heads/${BRANCH}:${EXPECTED_HEAD}\"",
        "python3 .github/scripts/validate_userscript.py",
        "node --check src/MissionChief_Map_Command_Toolkit.user.js",
        "cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt",
    ):
        require(source, marker)

    for marker in (
        "github.event.issue.pull_request == null",
        "gh pr create",
        "Open or update pull request",
        "secrets.DEVELOPMENT_PR_TOKEN || github.token",
        "git config user.name \"github-actions[bot]\"",
        "contents: write",
        "pull-requests: write",
        "group: development-package-${{ github.event.issue.number }}",
        "cancel-in-progress: false",
    ):
        forbid(source, marker)

    preflight_start = source.index("      - name: Run neutral preflight")
    apply_start = source.index("      - name: Rebase package onto exact main")
    preflight_block = source[preflight_start:apply_start]
    require(preflight_block, "exit 0")
    forbid(preflight_block, "git push")
    forbid(preflight_block, "gh pr create")

    apply_block = source[apply_start:]
    require(apply_block, "git push --force-with-lease")
    require(apply_block, "gh pr comment")
    forbid(apply_block, "gh pr create")
    forbid(apply_block, "gh issue create")

    validator = VALIDATOR.read_text(encoding="utf-8")
    require(validator, "python3 .github/scripts/test_development_package_workflow.py")
    require(validator, "pull_request:")
    require(validator, ".github/actions-security-policy.json")

    security_policy = SECURITY_POLICY.read_text(encoding="utf-8")
    require(security_policy, '".github/workflows/apply-development-package.yml": [')
    require(security_policy, '"issues"')

    documentation = DOC.read_text(encoding="utf-8")
    require(documentation, "existing open pull request")
    require(documentation, "never creates an issue, branch, or pull request")
    require(documentation, "owner-authenticated")
    require(documentation, "/preflight-development-package")
    require(documentation, "/apply-development-package")
    require(documentation, "Genuine publish failures remain red")

    print("Development-package workflow policy passed: existing PR only, owner-authenticated updates, no issue/PR creation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
