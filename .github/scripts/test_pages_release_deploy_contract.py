#!/usr/bin/env python3
"""Static contract for deterministic, non-blocking GitHub Pages deployment."""
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
        "status.tkbDistribution // empty",
        '[[ -n "$EXPECTED_VERSION" && "$DASHBOARD_VERSION" == "$EXPECTED_VERSION" && "$RELEASE_STATE" == "published" && "$DISTRIBUTION_STATE" == "verified" ]]',
        '.github/scripts/build_download_stats.py --self-test',
        '--output _site/data/download-stats.json',
        "source_sha=$SOURCE_SHA",
        'grep -Fq "${{ steps.production.outputs.release_version }}" _site/index.html',
        ".github/scripts/test_pages_release_deploy_contract.py",
    ]
    missing = [fragment for fragment in required if fragment not in pages]
    assert not missing, f"Pages production deployment contract fragments missing: {missing}"
    assert "  release:\n" not in pages, "Release publication must not trigger a duplicate Pages deployment"
    assert "group: toolkit-pages-${{" not in pages, "Legacy production concurrency group returned"

    resolve_index = pages.index("Resolve verified production source")
    build_index = pages.index("Build deployment site")
    deploy_index = pages.index("Deploy GitHub Pages")
    assert resolve_index < build_index < deploy_index

    release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    release_required = [
        "permissions:\n  contents: write\n  actions: write",
        "Record successful release, manifest, announcement and speed state",
        "Dispatch GitHub Pages asynchronously",
        "gh workflow run github-pages.yml --ref main",
        'echo "dispatched=true" >> "$GITHUB_OUTPUT"',
        "PAGES_DISPATCHED: ${{ steps.pages.outputs.dispatched }}",
        "GitHub Pages deployment dispatched asynchronously",
    ]
    release_missing = [fragment for fragment in release_required if fragment not in release]
    assert not release_missing, f"Pipeline v4 Pages dispatch fragments missing: {release_missing}"
    for forbidden in [
        'gh run watch "$PAGES_RUN_ID" --exit-status',
        "gh run list --workflow github-pages.yml",
        "steps.pages.outputs.pages_run_id",
        "The dispatched GitHub Pages run was not found",
        "- name: Publish GitHub Pages",
    ]:
        assert forbidden not in release, f"Blocking Pages marker returned: {forbidden}"

    state_index = release.index("Record successful release, manifest, announcement and speed state")
    dispatch_index = release.index("Dispatch GitHub Pages asynchronously")
    summary_index = release.index("Write release summary")
    assert state_index < dispatch_index < summary_index

    print("Pages deployment contract passed: verified source, one production concurrency group and asynchronous non-blocking release dispatch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
