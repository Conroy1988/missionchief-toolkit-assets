#!/usr/bin/env python3
"""Static contract for deterministic verified GitHub Pages deployment."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "github-pages.yml"


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
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
    missing = [fragment for fragment in required if fragment not in text]
    assert not missing, f"Pages production deployment contract fragments missing: {missing}"
    assert "group: toolkit-pages-${{" not in text, (
        "Legacy event-specific production concurrency group still permits release/push deployment races"
    )

    resolve_index = text.index("Resolve verified production source")
    build_index = text.index("Build deployment site")
    deploy_index = text.index("Deploy GitHub Pages")
    assert resolve_index < build_index < deploy_index, (
        "Verified production source must be resolved before building and deploying Pages"
    )

    print(
        "Pages deployment contract passed: all production events share one concurrency group "
        "and build from verified current main state."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
