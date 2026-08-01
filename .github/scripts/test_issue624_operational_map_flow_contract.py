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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.2.1"

    for required in [
        "missionProgressRings: true",
        "allianceChatPreviews: true",
        "merged.missionProgressRings = merged.missionProgressRings !== false",
        "merged.allianceChatPreviews = merged.allianceChatPreviews !== false",
        "function missionProgressRingModel(",
        "function openUnitLocator(",
        "function renderAllianceChatMissionPreviews(",
        "function openSessionCleanup(",
        "function performSessionCleanup(",
        "makeToggleButton('missionProgressRings'",
        "makeToggleButton('allianceChatPreviews'",
        'data-action="open-unit-locator"',
        'data-action="open-session-cleanup"',
        "#mission_chat_messages",
        "runtimeListen(document, 'click'",
    ]:
        assert required in source, required

    progress = section(source, "    function clearMissionProgressRings(", "    function clearAllianceChatMissionPreviews(")
    for required in [
        "const completion = Math.round(100 - liveValue)",
        "possible - safeRemaining",
        "__mcmsMissionProgressLayer",
        "__mcmsMissionProgressRing",
        "interactive: false",
        "role=\"img\"",
    ]:
        assert required in progress, required
    for forbidden in ["fetch(", "GM_xmlhttpRequest(", "setInterval(", "runtimeSetInterval("]:
        assert forbidden not in progress, forbidden

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

    chat = section(source, "    function clearAllianceChatMissionPreviews(", "    function refreshMissionSnapshots(")
    for required in [
        "#mission_chat_messages",
        "url.origin !== pageWindow.location.origin",
        "allianceChatMissionSnapshot",
        "liveMissionSnapshots.get(id)",
        "link.insertAdjacentElement('afterend', preview)",
    ]:
        assert required in chat, required
    for forbidden in ["fetch(", "GM_xmlhttpRequest(", "localStorage", "textContent = link", "innerText"]:
        assert forbidden not in chat, forbidden

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

    observer = section(source, "    function mutationBelongsToToolkit(", "    const ALLIANCE_BUILDINGS_MAP_NOTICE_ID")
    assert "function mutationAffectsAllianceChat(" in observer
    assert "const chatRoot = document.querySelector('#mission_chat_messages')" in source
    assert "if (chatRoot?.isConnected) roots.add(chatRoot)" in source

    briefing = section(source, "    function updateBriefingBody(", "    function openUpdateBriefing(")
    assert briefing.count('data-mcms-command-action="briefing-open-feature"') == 4
    for feature in ["progressRings", "unitLocator", "alliancePreviews", "sessionCleanup"]:
        assert f'data-feature="{feature}"' in briefing

    print("Issue #624 v10.2 operational-map-flow static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
