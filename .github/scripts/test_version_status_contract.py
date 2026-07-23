#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_version_status_runtime.js"
WORKFLOW = ROOT / ".github" / "workflows" / "publish-update-manifest.yml"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release-toolkit.yml"
MANIFEST = ROOT / "status" / "update-manifest.json"
DASHBOARD = ROOT / "status" / "release-dashboard.json"


def semver(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(value or ""))
    assert match, f"stable semantic version required: {value!r}"
    return tuple(int(part) for part in match.groups())


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    release_workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
    start = source.index("    // Issue #153: stable live Toolkit version-status control.")
    end = source.index("    function createCleanExit() {", start)
    block = source[start:end]

    assert source.count("// Issue #153: stable live Toolkit version-status control.") == 1
    assert "cacheMs: 30 * 60 * 1000" in block
    assert "autoIntervalMs: 30 * 60 * 1000" in block
    assert "failureCooldownMs: 10 * 60 * 1000" in block
    assert "requestTimeoutMs: 8 * 1000" in block
    assert "bootDelayMs: 15 * 1000" in block
    assert "setInterval(" not in block, "version checker must use a non-overlapping recursive timeout"
    assert "scheduleVersionStatusCheck(versionStatusAutomaticDelay(), false)" in block
    assert "document.visibilityState === 'hidden'" in block
    assert "Number(versionStatusModel.failedAt)" in block
    assert "ensureVersionStatusButton();" in block
    assert "Number(delay) === VERSION_STATUS.bootDelayMs" in block
    assert "mcms-version-btn--unified" in block
    assert "button.className = 'mcms-version-btn mcms-version-btn--unified'" in block
    assert "button.className = 'mcms-economy-btn mcms-version-btn mcms-version-btn--unified'" not in block
    assert "button.dataset.variant = 'control-family'" in block
    assert "button.dataset.label = label" in block
    assert "button.textContent = ''" in block
    assert "content:attr(data-label)!important" in block
    assert "white-space:nowrap!important" in block
    assert "word-break:keep-all!important" in block
    assert "width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important" in block
    assert '[data-state="latest"]::before{content:"✓"!important' in block
    assert '[data-state="update"]::before{content:"↑"!important' in block
    assert "grid-template-rows:20px auto" not in block
    assert "mcms-version-btn--tile" not in block
    for marker in [
        "function versionStatusCompare(left, right)",
        "function versionStatusValidateManifest(payload)",
        "function versionStatusCacheIsFresh(cache, now = Date.now())",
        "function ensureVersionStatusButton()",
        "function versionStatusRequestManifest()",
        "function versionStatusAutomaticDelay(now = Date.now())",
        "function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false)",
        "function disposeVersionStatus()",
        "data-mcms-tablet-active",
        "data-mcms-mobile-active",
        "runtime.requests?.add?.(versionStatusRequest)",
    ]:
        assert marker in block, f"version-status runtime marker missing: {marker}"
    assert "raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/status/update-manifest.json" in block
    assert "scheduleVersionStatusCheck(VERSION_STATUS.bootDelayMs, false);" in source
    assert "scheduleVersionStatusCheck(0, false);" in source
    assert "disposeVersionStatus();" in source
    assert "ensureVersionStatusButton();" in source
    assert source.count("@connect      raw.githubusercontent.com") == 1
    assert len(source.splitlines()) <= 64000, "source exceeds release performance line ceiling"

    assert manifest["schemaVersion"] == 1
    assert manifest["channel"] == "stable"
    assert semver(manifest["version"]) == semver(dashboard["latestRelease"]["version"])
    source_version = re.search(r"// @version\s+([^\s]+)", source).group(1)
    assert semver(manifest["version"]) <= semver(source_version)
    assert manifest["releaseNotesUrl"].endswith(f"/releases/tag/v{manifest['version']}")
    assert manifest["updateUrl"].startswith("https://update.greasyfork.org/scripts/586018/")

    for marker in [
        "workflow_dispatch:",
        "Build manifest from verified release ledger",
        "status/update-manifest.json",
        "'githubRelease': 'published'",
        "'greasyForkSync': 'verified'",
        "'backup': 'private-repository-verified'",
        "'discordRelease': 'posted'",
        "git push origin HEAD:main",
    ]:
        assert marker in workflow, f"verified manifest workflow marker missing: {marker}"
    assert "workflow_run:" not in workflow, "manifest publication must not duplicate the explicit release dispatch"
    dispatch_index = workflow.index("workflow_dispatch:")
    build_index = workflow.index("Build manifest from verified release ledger")
    push_index = workflow.index("git push origin HEAD:main")
    assert dispatch_index < build_index < push_index, "manifest dispatch must precede verified publication"

    for marker in [
        "- name: Publish update channels in parallel",
        "gh workflow run publish-update-manifest.yml --ref main",
        "gh workflow run github-pages.yml --ref main",
        'gh run list --workflow "$workflow" --event workflow_dispatch --branch main',
        'gh run watch "$MANIFEST_RUN_ID" --exit-status',
        'gh run watch "$PAGES_RUN_ID" --exit-status',
        "MANIFEST_RUN_ID: ${{ steps.channels.outputs.manifest_run_id }}",
    ]:
        assert marker in release_workflow, f"release workflow parallel publication marker missing: {marker}"
    dashboard_index = release_workflow.index("- name: Record successful release in dashboard")
    publish_index = release_workflow.index("- name: Publish update channels in parallel")
    assert dashboard_index < publish_index, "parallel update channels must start after dashboard reconciliation"

    result = subprocess.run(["node", str(RUNTIME)], cwd=ROOT)
    assert result.returncode == 0, "version status runtime fixtures failed"
    print("Version status contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
