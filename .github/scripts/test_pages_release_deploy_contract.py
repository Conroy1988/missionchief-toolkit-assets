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
        "  release:\n    types:\n      - published",
        "format('toolkit-pages-pr-{0}', github.event.pull_request.number)",
        "'toolkit-pages-production'",
        "cancel-in-progress: true",
        "Resolve verified production source",
        "github.event.release.tag_name",
        "EXPECTED_TAG#v",
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
    assert "group: toolkit-pages-${{" not in pages, (
        "Legacy event-specific production concurrency group still permits release/push deployment races"
    )

    resolve_index = pages.index("Resolve verified production source")
    build_index = pages.index("Build deployment site")
    deploy_index = pages.index("Deploy GitHub Pages")
    assert resolve_index < build_index < deploy_index, (
        "Verified production source must be resolved before building and deploying Pages"
    )

    release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    release_required = [
        "permissions:\n  contents: write\n  actions: write",
        "Record successful release in dashboard",
        "Deploy verified documentation site",
        "gh workflow run github-pages.yml --ref main",
        "gh run list --workflow github-pages.yml --event workflow_dispatch --branch main",
        "The dispatched GitHub Pages deployment run was not found",
        'gh run watch "$RUN_ID" --exit-status',
        "steps.pages_deploy.outputs.run_id",
    ]
    release_missing = [fragment for fragment in release_required if fragment not in release]
    assert not release_missing, (
        "Production release-to-Pages dispatch contract fragments missing: "
        f"{release_missing}"
    )

    dashboard_index = release.index("Record successful release in dashboard")
    pages_dispatch_index = release.index("Deploy verified documentation site")
    summary_index = release.index("Write release summary")
    assert dashboard_index < pages_dispatch_index < summary_index, (
        "The release must record verified state, await the Pages deployment, then write its final summary"
    )

    print(
        "Pages deployment contract passed: production events share one concurrency group, "
        "build from verified current main state, and every Toolkit release explicitly awaits Pages."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
