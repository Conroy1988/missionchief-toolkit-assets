#!/usr/bin/env python3
"""Security contract for connector-triggered guarded Toolkit releases."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/owner-release-command.yml"
POLICY = ROOT / ".github/connector-release-command-policy.json"


def main() -> int:
    source = WORKFLOW.read_text(encoding="utf-8")
    for marker in [
        "issue_comment:",
        "push:",
        "automation/releases",
        ".github/automation-commands/release-toolkit.json",
        "github.actor == 'Conroy1988'",
        "A connector release command commit must change only",
        '.command == "release-toolkit"',
        '.confirmation == "RELEASE"',
        "Release command must be a direct child of the expected main commit.",
        "Release command main head is stale.",
        "Main moved after release authorization.",
        "GitHub Release v${VERSION} already exists.",
        "python3 .github/scripts/validate_userscript.py",
        'node --check "$SOURCE"',
        "release-readiness-check.yml",
        "release-toolkit.yml",
        "confirmation: RELEASE",
        "MIGRATION_REPO_TOKEN",
        "DISCORD_RELEASE_WEBHOOK",
    ]:
        assert marker in source, marker

    for forbidden in [
        "pull_request_target",
        "secrets: inherit",
        "eval ",
        "bash -c",
        "HEAD:main",
        "HEAD:refs/heads/main",
    ]:
        assert forbidden not in source, forbidden

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    command = policy["commandTransport"]
    assert command["branch"] == "automation/releases"
    assert command["changedFiles"] == 1
    assert command["directChildOfExpectedMain"] is True
    assert command["exactCurrentMain"] is True
    assert command["nonceRequired"] is True
    assert command["confirmation"] == "RELEASE"
    assert "mandatory release readiness" in policy["requiredValidation"]
    assert "guarded production release" in policy["requiredValidation"]
    print("Connector-triggered guarded release contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
