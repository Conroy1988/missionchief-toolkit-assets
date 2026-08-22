#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.16.6"

    state = section(source, "    function defaultState()", "    function normaliseLoadedState(")
    for required in [
        "fullscreenMap: false",
        "interfaceDensity: { desktop: 'standard', tablet: 'standard' }",
        "quickWheel: { enabled: true",
        "updateBriefing: { enabled: true, seenVersion: '', seenFeatures: [] }",
    ]:
        assert required in state, required

    transfer = section(
        source,
        "    function settingsTransferBytesToBase64(",
        "    function toolkitDoctorSafeText(",
    )
    assert "iterations: 310000" in source
    for required in [
        "AES-GCM",
        "PBKDF2-SHA-256",
        "SHA-256",
        "getRandomValues",
        "additionalData",
        "tagLength: 128",
        "at least 12 characters",
        "wrong or the encrypted file has been altered",
        "Discord webhook",
        "Included · redacted",
        "Legacy unencrypted file",
    ]:
        assert required in transfer, required
    assert "location.href" not in transfer
    assert "document.cookie" not in transfer

    export_entry = section(
        source,
        "    function exportToolkitConfig()",
        "    function looksLikeToolkitState(",
    )
    assert "openEncryptedSettingsExport()" in export_entry
    assert "JSON.stringify(buildToolkitSettingsBackup" not in export_entry

    backup = section(
        source,
        "    function buildToolkitSettingsBackup(",
        "    function downloadToolkitSettingsBlob(",
    )
    assert "includeSecrets = true" in backup
    assert "includeSecrets ? getDiscordWebhookUrl() : ''" in backup
    assert "integrations: includeSecrets ?" in backup
    assert "secretsExcluded: !includeSecrets" in backup

    imported = section(
        source,
        "    function applyImportedToolkitSettings(",
        "    function importToolkitConfigFile(",
    )
    for required in [
        "previousStateRaw",
        "previousSettingsVaultRaw",
        "previousWebhook",
        "previousCredentialRaw",
        "previousVaultRaw",
        "Financial Archive identity storage is unavailable.",
        "Financial Archive storage is unavailable.",
        "applyLoadedConfiguration()",
    ]:
        assert required in imported, required

    fullscreen = section(
        source,
        "    function findFullscreenMapTarget(",
        "    function quickWheelOptions(",
    )
    for required in [
        "mcms-map-fullscreen-target",
        "fullscreenExitId",
        "invalidateSize",
        "Escape to restore",
    ]:
        assert required in fullscreen, required

    wheel_binding = section(
        source,
        "        const onTabletQuickWheel = event =>",
        "    function setMapView(",
    )
    assert "activeDeviceLayout !== 'tablet'" in wheel_binding
    assert "map.on('contextmenu', onTabletQuickWheel)" in wheel_binding
    assert "runtime.mapBindings.push" in wheel_binding
    assert "setTimeout" not in wheel_binding
    assert "MutationObserver" not in wheel_binding

    doctor = section(
        source,
        "    function toolkitDoctorSafeText(",
        "    function updateBriefingBody(",
    )
    for required in [
        "Runtime ownership",
        "Saved settings",
        "Map controls",
        "UK intelligence",
        "Responsive layout",
        "Overlay safety",
        "Secrets, player identity, balances, coordinates and operational data were excluded.",
    ]:
        assert required in doctor, required
    for forbidden in ["getDiscordWebhookUrl()", "discordWebhookEndpoint(", "document.cookie"]:
        assert forbidden not in doctor, forbidden

    briefing = section(
        source,
        "    function updateBriefingBody(",
        "    function settingsBackupFilename(",
    )
    assert "transportSweepRuntime.running" in briefing
    assert "state.updateBriefing.seenVersion === SCRIPT.version" in briefing
    assert "openUpdateBriefing({ manual = false }" in briefing
    assert "Don’t Show Again" in briefing

    for required in [
        'data-setting="density-desktop"',
        'data-setting="density-tablet"',
        'data-action="toolkit-doctor"',
        "makeActionToggleButton('toggle-map-fullscreen'",
        'data-action="open-tablet-quick-wheel"',
        'data-action="open-update-briefing"',
        'data-action="export-safe-config"',
        'accept="application/json,text/json,.json,.mcms"',
        'data-mcms-density',
        'data-mcms-map-fullscreen',
    ]:
        assert required in source, required

    command_experience = section(
        source,
        "    function closeCommandExperienceModal(",
        "    function settingsBackupFilename(",
    )
    assert "runtimeSetInterval(" not in command_experience
    assert "MutationObserver" not in command_experience

    performance = json.loads(
        (ROOT / ".github" / "performance-budget.json").read_text(encoding="utf-8")
    )
    approvals = [performance["transitionApproval"], *performance["approvalHistory"]]
    issue_612 = next(item for item in approvals if item["issue"] == 612 and item["version"] == "9.3.0")
    assert issue_612["approvedNetworkRequestDelta"] == 0
    assert performance["absoluteLimits"]["network_request_calls"] == 6
    print("Issue #612 command experience static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
