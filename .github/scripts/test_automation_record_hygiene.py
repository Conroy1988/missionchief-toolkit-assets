#!/usr/bin/env python3
"""Prevent workflows from recreating issue, PR and approval-gate clutter."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / ".github/workflows/asset-health-monitor.yml"
ROLLBACK = ROOT / ".github/workflows/prepare-release-rollback.yml"
PAGES = ROOT / ".github/scripts/reconcile_pages_incident.sh"
POLICY = ROOT / ".github/actions-security-policy.json"


def require(text: str, marker: str) -> None:
    if marker not in text:
        raise AssertionError(f"Missing automation hygiene marker: {marker}")


def forbid(text: str, marker: str) -> None:
    if marker in text:
        raise AssertionError(f"Forbidden automation hygiene marker: {marker}")


def main() -> int:
    asset = ASSET.read_text(encoding="utf-8")
    require(asset, "SEARCH_QUERY='\"Toolkit public assets unavailable\" in:title'")
    require(asset, 'gh issue list \\\n            --state all \\\n            --search "$SEARCH_QUERY"')
    require(asset, "TRANSITION=\"existing\"")
    forbid(asset, "gh issue list --state all --limit 100")

    pages = PAGES.read_text(encoding="utf-8")
    require(pages, "SEARCH_QUERY='\"GitHub Pages production health incident\" in:title'")
    require(pages, 'gh issue list --state all --search "$SEARCH_QUERY"')

    rollback = ROLLBACK.read_text(encoding="utf-8")
    permission_block = rollback[rollback.index("permissions:"):rollback.index("\nconcurrency:")]
    require(permission_block, "contents: read")
    forbid(permission_block, "contents: write")
    forbid(permission_block, "pull-requests: write")
    forbid(permission_block, "issues: write")
    require(rollback, "Require owner rollback token")
    require(rollback, "secrets.DEVELOPMENT_PR_TOKEN")
    require(rollback, "DEVELOPMENT_PR_TOKEN is required to create an owner-authenticated rollback PR.")
    require(rollback, 'git config user.name "Conroy1988"')
    require(rollback, "27301455+Conroy1988@users.noreply.github.com")
    require(rollback, "GH_TOKEN: ${{ secrets.DEVELOPMENT_PR_TOKEN }}")
    forbid(rollback, 'git config user.name "github-actions[bot]"')
    forbid(rollback, "41898282+github-actions[bot]@users.noreply.github.com")
    forbid(rollback, "GH_TOKEN: ${{ github.token }}\n          SOURCE_VERSION")

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if ".github/workflows/prepare-release-rollback.yml" in policy.get("allowedWritePermissions", {}):
        raise AssertionError("Rollback workflow must not receive GITHUB_TOKEN write permissions")
    if policy.get("allowedWritePermissions", {}).get(".github/workflows/asset-health-monitor.yml") != ["issues"]:
        raise AssertionError("Asset-health monitor should retain issue-only incident write permission")

    print("Automation record hygiene passed: managed incidents deduplicate and rollback PRs use owner identity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
