#!/usr/bin/env python3
"""Static contract for deterministic verified GitHub Pages deployment."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES_WORKFLOW = ROOT / ".github" / "workflows" / "github-pages.yml"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release-toolkit.yml"


def main() -> int:
    pages = PAGES_WORKFLOW.read_text(encoding="utf-8")
    required = [
        "format('toolkit-pages-pr-{0}', github.event.pull_request.number)",
        "'toolkit-pages-production'",
        "cancel-in-progress: true",
        "Resolve verified production source",
        "git fetch --no-tags --depth=1 origin main",
        "git reset --hard origin/main",
        "latestRelease.version // empty",
        "status.githubRelease // empty",
        "status.greasyForkSync // empty",
        '[[ -n "$EXPECTED_VERSION" && "$DASHBOARD_VERSION" == "$EXPECTED_VERSION" && "$RELEASE_STATE" == "published" && "$GREASY_FORK_STATE" == "verified" ]]',
        "source_sha=$SOURCE_SHA",
        'grep -Fq "${{ steps.production.outputs.release_version }}" _site/index.html',
        ".github/scripts/test_pages_release_deploy_contract.py",
    ]
    missing = [fragment for fragment in required if fragment not in pages]
    assert not missing, f"Pages production deployment contract fragments missing: {missing}"
    assert "  release:\n" not in pages
    assert "group: toolkit-pages-${{" not in pages

    resolve_index = pages.index("Resolve verified production source")
    build_index = pages.index("Build deployment site")
    deploy_index = pages.index("Deploy GitHub Pages")
    assert resolve_index < build_index < deploy_index

    release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    release_required = [
        "permissions:\n  contents: write\n  actions: write",
        "Prepare authoritative production state projection",
        "Publish backward-compatible main state copy",
        "Publish authoritative release-state ledger",
        "Verify authoritative and compatibility state parity",
        "Publish GitHub Pages",
        "gh workflow run github-pages.yml --ref main",
        "gh run list --workflow github-pages.yml --event workflow_dispatch --branch main",
        "The dispatched GitHub Pages run was not found",
        'gh run watch "$PAGES_RUN_ID" --exit-status',
        "steps.pages.outputs.pages_run_id",
    ]
    release_missing = [fragment for fragment in release_required if fragment not in release]
    assert not release_missing, (
        "Production release-to-Pages dispatch contract fragments missing: "
        f"{release_missing}"
    )
    for retired in [
        "Publish update channels in parallel",
        "gh workflow run publish-update-manifest.yml",
        "steps.channels.outputs.pages_run_id",
    ]:
        assert retired not in release, f"Retired publication marker returned: {retired}"

    projection_index = release.index("Prepare authoritative production state projection")
    compatibility_index = release.index("Publish backward-compatible main state copy")
    authority_index = release.index("Publish authoritative release-state ledger")
    parity_index = release.index("Verify authoritative and compatibility state parity")
    pages_dispatch_index = release.index("Publish GitHub Pages")
    summary_index = release.index("Write release summary")
    assert (
        projection_index
        < compatibility_index
        < authority_index
        < parity_index
        < pages_dispatch_index
        < summary_index
    ), "Pages must run only after both state publications and their byte-parity gate"

    print(
        "Pages deployment contract passed: production state is projected once, published to "
        "release-state and the compatibility branch, verified byte-identical, then deployed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
