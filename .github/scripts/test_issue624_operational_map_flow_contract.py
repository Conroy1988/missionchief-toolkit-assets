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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.5.1"

    for required in [
        "delete merged.missionProgressRings",
        "delete merged.allianceChatPreviews",
        "function openUnitLocator(",
        "function openSessionCleanup(",
        "function performSessionCleanup(",
        'data-action="open-unit-locator"',
        'data-action="open-session-cleanup"',
        "runtimeListen(document, 'click'",
    ]:
        assert required in source, required

    for retired in [
        "state.missionProgressRings",
        "state.allianceChatPreviews",
        "function clearMissionProgressRings(",
        "function missionProgressRingModel(",
        "function makeMissionProgressRingIcon(",
        "function updateMissionProgressRings(",
        "function clearAllianceChatMissionPreviews(",
        "function allianceChatMissionSnapshot(",
        "function allianceChatPreviewHtml(",
        "function renderAllianceChatMissionPreviews(",
        "makeToggleButton('missionProgressRings'",
        "makeToggleButton('allianceChatPreviews'",
        ".mcms-mission-progress-icon",
        ".mcms-alliance-mission-preview",
        "function mutationAffectsAllianceChat(",
        "#mission_chat_messages",
        'data-feature="progressRings"',
        'data-feature="alliancePreviews"',
    ]:
        assert retired not in source, retired

    locator = section(source, "    function vehicleMarkerForId(", "    function commandPaletteOpenSetting(")
    for required in [
        "getPersonalVehicleRecords()",
        "building_caption",
        "vehicleStatusCode(record)",
        "marker.on?.('move'",
        "followedVehicleMarker.off?.('move'",
        "Manual map movement stops following immediately",
    ]:
        assert required in locator, required
    for forbidden in ["dispatch", "vehicleSelection", "clickVehicle", "fetch(", "GM_xmlhttpRequest("]:
        assert forbidden not in locator, forbidden

    cleanup = section(source, "    function sessionCleanupSpawnLayers(", "    function dismissUpdateBriefing(")
    for required in [
        "const plan = sessionCleanupPlan()",
        "Protected:",
        "notificationEventSeen.clear()",
        "recentCompletedMissions.length = 0",
        "resourceGapAnalysisCache.clear()",
        "missionSnapshotCache.clear()",
        "Session cleanup complete",
    ]:
        assert required in cleanup, required
    assert "notificationActiveEvents.clear()" not in cleanup
    for forbidden in [
        "localStorage.clear",
        "GM_deleteValue",
        "state = defaultState",
        "state.bookmarks",
        "state.profiles",
        "setDiscordWebhookUrl",
        "clearDiscordWebhook",
        "financeVault",
        "settingsSnapshots",
    ]:
        assert forbidden not in cleanup, forbidden

    briefing = section(source, "    function updateBriefingBody(", "    function openUpdateBriefing(")
    assert "RELEASE_BRIEFING.highlights" in briefing
    assert 'data-mcms-command-action="briefing-open-feature"' not in briefing
    for feature in ["unitLocator", "sessionCleanup"]:
        assert f'data-feature="{feature}"' not in briefing

    print("Issue #624 v10.2.3 retirement contract passed: progress rings and Alliance Chat previews are absent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
