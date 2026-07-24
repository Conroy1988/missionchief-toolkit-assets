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
POLICY = ROOT / ".github" / "shadow-branch-policy.json"


def semver(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(value or ""))
    assert match, f"stable semantic version required: {value!r}"
    return tuple(int(part) for part in match.groups())


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    start = source.index("    // Issue #153: stable live Toolkit version-status control.")
    end = source.index("    function createCleanExit() {", start)
    block = source[start:end]

    assert source.count("// Issue #153: stable live Toolkit version-status control.") == 1
    assert "cacheMs: 30 * 60 * 1000" in block
    assert "autoIntervalMs: 30 * 60 * 1000" in block
    assert "failureCooldownMs: 10 * 60 * 1000" in block
    assert "requestTimeoutMs: 8 * 1000" in block
    assert "bootDelayMs: 15 * 1000" in block
    assert "setInterval(" not in block
    assert "scheduleVersionStatusCheck(versionStatusAutomaticDelay(), false)" in block
    assert "document.visibilityState === 'hidden'" in block
    assert "Number(versionStatusModel.failedAt)" in block
    assert "ensureVersionStatusButton();" in block
    assert "Number(delay) === VERSION_STATUS.bootDelayMs" in block
    assert "mcms-version-btn--unified" in block
    assert "button.className = 'mcms-version-btn mcms-version-btn--unified'" in block
    assert "button.dataset.variant = 'control-family'" in block
    assert "button.dataset.label = label" in block
    assert "button.textContent = ''" in block
    assert "content:attr(data-label)!important" in block
    assert "white-space:nowrap!important" in block
    assert "word-break:keep-all!important" in block
    assert "width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important" in block
    assert '[data-state="latest"]::before{content:"✓"!important' in block
    assert '[data-state="update"]::before{content:"↑"!important' in block
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

    compatibility_url = (
        "raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/"
        "status/update-manifest.json"
    )
    assert compatibility_url in block
    assert "scheduleVersionStatusCheck(VERSION_STATUS.bootDelayMs, false);" in source
    assert "scheduleVersionStatusCheck(0, false);" in source
    assert "disposeVersionStatus();" in source
    assert source.count("@connect      raw.githubusercontent.com") == 1
    assert len(source.splitlines()) <= 64000

    assert manifest["schemaVersion"] == 1
    assert manifest["channel"] == "stable"
    assert semver(manifest["version"]) == semver(dashboard["latestRelease"]["version"])
    source_version = re.search(r"// @version\s+([^\s]+)", source).group(1)
    assert semver(manifest["version"]) <= semver(source_version)
    assert manifest["releaseNotesUrl"].endswith(f"/releases/tag/v{manifest['version']}")
    assert manifest["updateUrl"].startswith("https://update.greasyfork.org/scripts/586018/")

    release_state = policy["branches"]["release-state"]
    mirror = release_state["compatibilityMirror"]
    assert release_state["primaryProductionWriter"] == ".github/workflows/release-toolkit.yml"
    assert release_state["externalConsumersEnabled"] is False
    assert mirror == {
        "branch": "main",
        "paths": [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
        ],
        "requiredForRuntimeVersionsThrough": "5.0.7",
        "externalConsumersEnabled": True,
        "retirementRequiresVersionedMigration": True,
    }

    for marker in [
        "workflow_dispatch:",
        "permissions:\n  contents: read",
        "Build expected manifest from verified release ledger",
        "Verify committed stable manifest",
        "Upload immutable update-manifest evidence",
    ]:
        assert marker in workflow, f"read-only manifest verifier marker missing: {marker}"
    for forbidden in ["contents: write", "git commit", "git push origin HEAD:main"]:
        assert forbidden not in workflow, f"manifest verifier regained mutation: {forbidden}"

    for marker in [
        "Prepare authoritative production state projection",
        "release_recovery_state.py prepare-production",
        "Publish backward-compatible main state copy",
        "Publish authoritative release-state ledger",
        "Verify authoritative and compatibility state parity",
        "Publish GitHub Pages",
    ]:
        assert marker in release, f"production state marker missing: {marker}"
    projection = release.index("Prepare authoritative production state projection")
    compatibility = release.index("Publish backward-compatible main state copy")
    authority = release.index("Publish authoritative release-state ledger")
    parity = release.index("Verify authoritative and compatibility state parity")
    pages = release.index("Publish GitHub Pages")
    assert projection < compatibility < authority < parity < pages

    result = subprocess.run(["node", str(RUNTIME)], cwd=ROOT)
    assert result.returncode == 0, "version status runtime fixtures failed"
    print(
        "Version status contract passed: v5.0.7 compatibility URL retained while "
        "release-state owns the primary production projection."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
