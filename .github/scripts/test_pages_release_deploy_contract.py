#!/usr/bin/env python3
"""Static contract for verified release-driven GitHub Pages deployment."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "github-pages.yml"


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = [
        "  release:\n    types:\n      - published",
        "Wait for verified release dashboard",
        "github.event.release.tag_name",
        "EXPECTED_TAG#v",
        "git fetch --no-tags --depth=1 origin main",
        "git reset --hard origin/main",
        "latestRelease.version // empty",
        "status.githubRelease // empty",
        '[[ "$DASHBOARD_VERSION" == "$EXPECTED_VERSION" && "$RELEASE_STATE" == "published" ]]',
        ".github/scripts/test_pages_release_deploy_contract.py",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    assert not missing, f"Pages release deployment contract fragments missing: {missing}"

    wait_index = text.index("Wait for verified release dashboard")
    build_index = text.index("Build deployment site")
    assert wait_index < build_index, "Verified release wait must run before the deployment build"

    print("Pages release deployment contract passed: published release waits for verified dashboard state before build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
