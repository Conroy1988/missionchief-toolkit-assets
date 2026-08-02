#!/usr/bin/env python3
from __future__ import annotations

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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.3.7"

    for required in [
        "personalisationStyleId: 'mc-map-command-personalisation-style'",
        "settingsSnapshotsState: 'mc_map_command_toolkit_settings_snapshots_v1'",
        "const LAYOUT_DEVICE_KEYS = Object.freeze(['desktop', 'tablet', 'mobile'])",
        "const QUICK_WHEEL_SLOT_MIN = 4",
        "const QUICK_WHEEL_SLOT_MAX = 8",
        "const SETTINGS_SNAPSHOT_LIMIT = 5",
        "const SETTINGS_SNAPSHOT_INTERVAL_MS = 6 * 60 * 60 * 1000",
        "layoutBuilder: defaultLayoutBuilderState(getLegacyPosition())",
        "themeStudio: defaultThemeStudioState()",
        "setupWizard: { completed: false, schema: 1 }",
        "notifications: defaultNotificationState()",
        "const notificationActiveEvents = new Set()",
        "merged.setupWizard.completed = parsed?.setupWizard",
        ": true;",
        "if (!parsed.layoutBuilder && merged.panelPosition)",
        "if (!maybeShowSetupWizard()) maybeShowUpdateBriefing()",
        "(state.notifications.enabled && Object.values(state.notifications.events).some(Boolean))",
        "nextNotificationEvents.forEach(key => notificationActiveEvents.add(key))",
        "add('personalisation', 'Open Personalisation Studio'",
        'data-action="open-personalisation-studio"',
        'data-action="open-layout-studio"',
        'data-action="open-wheel-studio"',
        'data-action="open-backup-centre"',
        'data-action="open-setup-wizard"',
        'data-action="open-notification-studio"',
    ]:
        assert required in source, required

    studio = section(source, "    function quickWheelSlotValue(", "    function settingsTransferBytesToBase64(")
    for required in [
        "function executeQuickWheelSlot(",
        "function movePersonalisationItem(",
        "function openPersonalisationStudio(",
        "function encodeThemeStudioCode(",
        "function importThemeStudioCode(",
        "function restoreSettingsSnapshot(",
        "function openSetupWizard(",
        "function maybeShowSetupWizard(",
        "function emitToolkitNotification(",
        "function requestToolkitNotificationPermission(",
        "aria-label=\"Personalisation Studio sections\"",
        "draggable=\"true\"",
        "data-layout-move-group",
        "data-layout-move-control",
        "data-personal-backup-file",
        "Request Browser Permission",
        "No unit is selected or dispatched.",
    ]:
        assert required in studio, required

    for forbidden in [
        "GM_xmlhttpRequest(",
        "GM.xmlHttpRequest(",
        "fetch(",
        "new XMLHttpRequest(",
        "runtimeSetInterval(",
        "runtimeRequestAnimationFrame(",
        "new MutationObserver(",
        ".addEventListener(",
    ]:
        assert forbidden not in studio, forbidden

    persistence = section(source, "    function loadSettingsSnapshots(", "    function parseSettingsPersistenceCandidate(")
    for required in [
        "slice(0, SETTINGS_SNAPSHOT_LIMIT)",
        "delete stateCopy.__mcmsPersistence",
        "saveSettingsSnapshots(snapshots)",
    ]:
        assert required in persistence, required
    for forbidden in ["discordWebhook", "financialArchive", "discordReportVault", "financialVaultState"]:
        assert forbidden not in persistence, forbidden

    theme = section(source, "    function defaultThemeStudioState(", "    function defaultQuickWheelSlots(")
    assert r"/^#[0-9a-f]{6}$/u" in theme
    assert "slice(0, 40)" in theme

    notifications = section(source, "    function unlockNotificationAudio(", "    function settingsTransferBytesToBase64(")
    assert "NotificationCtor.requestPermission()" in notifications
    assert "state.notifications.browserEnabled &&" in notifications
    assert "notificationEventSeen.has(key)" in notifications

    print("Issue #620 Personalisation Studio static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
