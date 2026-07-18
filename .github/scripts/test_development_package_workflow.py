#!/usr/bin/env python3
"""Static policy checks for the reviewed development-package workflow."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "apply-development-package.yml"
VALIDATOR = ROOT / ".github" / "workflows" / "validate-development-package-workflow.yml"
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
        "jobs:\n  command:",
        "\n  execute:",
        "group: development-package-${{ needs.command.outputs.branch }}",
        "cancel-in-progress: true",
        "This exact package has not passed preflight against the current main branch.",
        "development-package-preflight-passed:${fingerprint}",
        "development-package-preflight-stopped:${fingerprint}",
        "development-package-apply:${fingerprint}",
        "Run neutral preflight",
        "exit 0",
        "Record neutral skip",
        "Record exact publish failure",
        "failure() && needs.command.outputs.mode == 'apply'",
        "--force-with-lease=\"refs/heads/${BRANCH}:${EXPECTED_HEAD}\"",
        "python3 .github/scripts/validate_userscript.py",
        "node --check src/MissionChief_Map_Command_Toolkit.user.js",
        "cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt",
    ):
        require(source, marker)

    forbid(source, "group: development-package-${{ github.event.issue.number }}")
    forbid(source, "cancel-in-progress: false")

    preflight_start = source.index("      - name: Run neutral preflight")
    apply_start = source.index("      - name: Rebase package onto exact main")
    preflight_block = source[preflight_start:apply_start]
    require(preflight_block, "exit 0")
    forbid(preflight_block, "git push")
    forbid(preflight_block, "gh pr create")

    apply_block = source[apply_start:]
    require(apply_block, "git push --force-with-lease")
    require(apply_block, "gh pr create")

    validator = VALIDATOR.read_text(encoding="utf-8")
    require(validator, "python3 .github/scripts/test_development_package_workflow.py")
    require(validator, "pull_request:")

    documentation = DOC.read_text(encoding="utf-8")
    require(documentation, "/preflight-development-package")
    require(documentation, "/apply-development-package")
    require(documentation, "Genuine publish failures remain red")

    print("Development-package workflow policy passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
