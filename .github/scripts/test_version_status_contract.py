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
BUILDER = ROOT / ".github" / "scripts" / "build_stable_update_manifest.py"
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
    builder = BUILDER.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
    marker = "    // Issue #153 introduced the control; Issues #639 and #41 make verified TKB release discovery live and release-state authoritative."
    start = source.index(marker)
    end = source.index("    function createCleanExit() {", start)
    block = source[start:end]

    assert source.count(marker.strip()) == 1
    assert "productUrl: 'https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/'" in block
    assert "cacheMs: 60 * 1000" in block
    assert "autoIntervalMs: 60 * 1000" in block
    assert "failureCooldownMs: 60 * 1000" in block
    assert "requestTimeoutMs: 8 * 1000" in block
    assert "bootDelayMs: 1500" in block
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
    assert "button.classList.toggle('mcms-version-update-alert', stateName === 'update')" in block
    assert "button.textContent = ''" in block
    assert "content:attr(data-label)!important" in block
    assert "white-space:nowrap!important" in block
    assert "word-break:keep-all!important" in block
    assert "width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important" in block
    assert '[data-state="latest"]::before{content:"✓"!important' in block
    assert '[data-state="update"]::before{content:"↑"!important' in block
    assert "@keyframes mcmsVersionUpdateNeon" in block
    assert "prefers-reduced-motion:reduce" in block
    assert "animation:none !important" in block
    assert "box-shadow:0 0 7px rgba(57,255,207,1)" in block
    assert "grid-template-rows:20px auto" not in block
    assert "mcms-version-btn--tile" not in block
    for marker in [
        "function versionStatusCompare(left, right)",
        "function versionStatusValidateManifest(payload)",
        "function versionStatusCacheIsFresh(cache, now = Date.now())",
        "function ensureVersionStatusButton()",
        "function ensureVersionStatusAlertStyle()",
        "function versionStatusRequestManifest()",
        "function versionStatusAutomaticDelay(now = Date.now())",
        "function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false)",
        "function disposeVersionStatus()",
        "data-mcms-tablet-active",
        "data-mcms-mobile-active",
        "runtime.requests?.add?.(requestHandle)",
        "versionStatusRequestToken += 1",
        "toolkitCommandShellContextActive()",
    ]:
        assert marker in block, f"version-status runtime marker missing: {marker}"
    primary_manifest = "raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/release-state/status/update-manifest.json"
    assert primary_manifest in block
    assert "raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/status/update-manifest.json" not in block
    assert "manifestUrl: 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/release-state/status/update-manifest.json'" in block
    assert "manifestUrls" not in block
    assert "endpointIndex" not in block
    assert "pageWindow.open(VERSION_STATUS.productUrl" in block
    assert "pageWindow.open(destination" not in block
    assert "versionStatusPresentation(SCRIPT.version, manifest).destination" not in block
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
    assert manifest["updateUrl"] == "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/"

    for marker in [
        "name: Verify Toolkit Update Manifest",
        "workflow_dispatch:",
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "Validate stable manifest builder self-tests",
        "Verify committed manifest against release ledger",
        "--check",
        "missionchief-update-manifest-verification-${{ github.sha }}",
    ]:
        assert marker in workflow, f"verified manifest workflow marker missing: {marker}"
    for forbidden in ["contents: write", "git push", "git commit", "git pull --rebase"]:
        assert forbidden not in workflow, f"read-only manifest verifier contains mutation marker: {forbidden}"

    for marker in [
        "def build_manifest(dashboard: dict, settings: dict)",
        "Stable update manifest self-tests passed.",
        '"publicMainChanged": False',
    ]:
        assert marker in builder, f"stable manifest builder marker missing: {marker}"

    for marker in [
        "- name: Record successful release, manifest, announcement and speed state",
        "python3 .github/scripts/build_stable_update_manifest.py",
        "status/update-manifest.json",
        "- name: Dispatch GitHub Pages asynchronously",
        "gh workflow run github-pages.yml --ref main",
        "PAGES_DISPATCHED: ${{ steps.pages.outputs.dispatched }}",
    ]:
        assert marker in release_workflow, f"release workflow atomic manifest marker missing: {marker}"
    for forbidden in [
        "gh workflow run publish-update-manifest.yml",
        "MANIFEST_RUN_ID",
        "manifest_run_id",
        'gh run watch "$PAGES_RUN_ID" --exit-status',
    ]:
        assert forbidden not in release_workflow, f"retired manifest dispatch marker returned: {forbidden}"

    dashboard_index = release_workflow.index("- name: Record successful release, manifest, announcement and speed state")
    build_index = release_workflow.index("python3 .github/scripts/build_stable_update_manifest.py", dashboard_index)
    state_commit_index = release_workflow.index("release_state_branch.py commit", build_index)
    pages_index = release_workflow.index("- name: Dispatch GitHub Pages asynchronously", state_commit_index)
    assert "git push origin HEAD:main" not in release_workflow
    assert dashboard_index < build_index < state_commit_index < pages_index

    result = subprocess.run(["node", str(RUNTIME)], cwd=ROOT)
    assert result.returncode == 0, "version status runtime fixtures failed"
    print("Version status contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
