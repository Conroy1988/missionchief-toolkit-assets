#!/usr/bin/env python3
"""Verify LSSM ownership, delayed controls, multi-ambulance returns and DOM-delta window cleanup."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github/fixtures/transport-sweep-lssm-contract.json"


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    own_ids = set(data["current_player_vehicle_ids"])
    for row in data["rows"]:
        html = row["html"]
        action = re.search(r'href="/vehicles/(\d+)/patient/-1"', html)
        owner = re.search(r'href="/profile/(\d+)"', html)
        fms5 = "building_list_fms_5" in html
        assert action and action.group(1) == row["vehicle_id"], row["name"]
        assert owner and owner.group(1) == row["owner_profile_id"], row["name"]
        eligible = bool(fms5 and action.group(1) not in own_ids and owner.group(1))
        assert eligible is row["eligible"], row["name"]

    eligible_rows = [row for row in data["rows"] if row["eligible"]]
    assert len(eligible_rows) >= 3, "multi-ambulance fixture must contain at least three eligible alliance rows"
    assert len({row["vehicle_id"] for row in eligible_rows}) == len(eligible_rows), "eligible alliance vehicle IDs must be unique"

    source = SOURCE.read_text(encoding="utf-8")
    required = [
        "function transportSweepReleaseVehicleIdFromHref(href)",
        "/patient\/-1",
        "function transportSweepOwnerProfileId(row)",
        "function collectTransportSweepLssmCandidates(excludedVehicleIds = null)",
        "function waitForTransportSweepLssmCandidates(excludedVehicleIds = null, timeoutMs = 18000)",
        "waitForTransportSweepLssmCandidates(attemptedVehicleIds, 18000)",
        "function activateTransportSweepLssmRelease(candidate)",
        "LSSM mission release controls",
        "rejectedAmbiguousOwner",
        "ownIds.has(String(vehicleId))",
        "attemptedVehicleIds.add(String(lssmCandidate.vehicleId))",
        "await collectTransportSweepVehicleCandidatesForMission(missionId)",
        "existing vehicle-window route remains available as a fallback",
        "Returning to ${item.caption} for remaining alliance ambulances",
        "missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');",
        "if (transportSweepReleaseConfirmationVisible()) return true;",
        "async function closeTransportSweepWindows(reason = 'navigation')",
        "const closed = await closeTransportSweepWindows(mode === 'mission' ? 'opening a mission' : 'opening a vehicle')",
        "const opened = await openTransportSweepPath(candidate.href, 'vehicle')",
        "await closeTransportSweepWindows('finishing the mission')",
        "activeWindowRoot: null",
        "ownedWindowLayers: new Set()",
        "activeWindowCreatedLayer: false",
        "function transportSweepNativeWindowLayers()",
        "function transportSweepClaimWindow(root, beforeLayers = null)",
        "const beforeLayers = new Set(transportSweepNativeWindowLayers())",
        "transportSweepClaimWindow(root, beforeLayers)",
        "layer.dataset.mcmsTransportSweepOwned = '1'",
        "layer.remove()",
        "const target = transportSweepRuntime.activeWindowRoot",
        "const changed = !beforeRootText.has(root) || afterText !== beforeRootText.get(root)",
        "await closeTransportSweepWindows('finishing the sweep')",
    ]
    processor = re.search(r"async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep", source)
    assert processor, "transport sweep mission processor is missing"
    processor_text = processor.group(1)
    release_index = processor_text.index("transportSweepRuntime.cleared += 1")
    return_index = processor_text.index("Returning to ${item.caption} for remaining alliance ambulances", release_index)
    reopen_index = processor_text.index("missionOpen = await openTransportSweepPath(`/missions/${missionId}`, 'mission');", return_index)
    assert release_index < return_index < reopen_index, "successful releases must explicitly return to the same mission before the next scan"
    assert "waitForTransportSweepLssmCandidates(attemptedVehicleIds, 18000)" in processor_text, "every direct-control scan must allow the full LSSM delay"

    missing = [item for item in required if item not in source]
    assert not missing, f"Missing LSSM transport sweep contract markers: {missing}"
    assert "lssmSeen ? 8000 : 18000" not in source, "A repeated mission load must not use an eight-second LSSM timeout"
    vehicle_processor = re.search(r"async function openTransportSweepVehicle\(candidate\) \{([\s\S]*?)\n    \}", source)
    assert vehicle_processor, "transport sweep vehicle opener is missing"
    assert "anchor.click()" not in vehicle_processor.group(1), "fallback vehicles must not stack over the mission via an in-window click"
    assert "pageWindow.lightboxOpen(candidate.href)" not in vehicle_processor.group(1), "fallback vehicles must use the managed single-window opener"
    opener = re.search(r"async function openTransportSweepPath\(path, mode\) \{([\s\S]*?)\n    \}", source)
    assert opener, "transport sweep path opener is missing"
    close_index = opener.group(1).index("await closeTransportSweepWindows")
    open_index = opener.group(1).index("pageWindow.lightboxOpen(path)")
    assert close_index < open_index, "the current MissionChief window must close before another opens"
    closer = re.search(r"async function closeTransportSweepWindows\(reason = 'navigation'\) \{([\s\S]*?)\n    \}", source)
    assert closer, "transport sweep closer is missing"
    assert "transportSweepTopLevelWindowRoots()" not in closer.group(1), "cleanup must not scan or close unrelated visible dialogs"
    assert "const target = transportSweepRuntime.activeWindowRoot" in closer.group(1), "cleanup must target only the sweep-owned window"
    assert "transportSweepRuntime.ownedWindowLayers" in closer.group(1), "cleanup must retain the exact DOM-delta layer set"
    control_index = closer.group(1).index("transportSweepWindowCloseControl(target)")
    global_index = closer.group(1).index("pageWindow.lightboxClose")
    assert control_index < global_index, "the owned window close control must be preferred over the global lightbox closer"
    assert "transportSweepRuntime.activeWindowCreatedLayer" in closer.group(1), "forced teardown must be limited to newly created sweep layers"
    assert "layer.remove()" in closer.group(1), "newly created owned layers must be removed if MissionChief leaves them connected"
    hud = data["hud"]
    assert f"transportSweepHudId: '{hud['id']}'" in source, "HUD ID must be owned by SCRIPT"
    required_hud_markers = [
        "function transportSweepHudElements()",
        "function ensureTransportSweepHud()",
        "function removeTransportSweepHud()",
        "function scheduleTransportSweepHudDismiss(delay = 6500)",
        "function renderTransportSweepHud()",
        "runtimeOnCleanup(removeTransportSweepHud);",
        "document.body || document.documentElement",
        "pointer-events:none !important",
        "env(safe-area-inset-bottom)",
        "Patients cleared",
    ]
    missing_hud = [marker for marker in required_hud_markers if marker not in source]
    assert not missing_hud, f"Missing Transport Sweep HUD contract markers: {missing_hud}"
    assert source.count("runtimeOnCleanup(removeTransportSweepHud);") == 1, "HUD cleanup must be registered exactly once"
    assert source.count("transportSweepRuntime.cleared += 1") == 2, "Only the two confirmed direct/fallback release paths may increment cleared"

    renderer = re.search(r"function renderTransportSweepPanel\(\) \{([\s\S]*?)\n    \}", source)
    assert renderer, "Transport Sweep panel renderer is missing"
    renderer_text = renderer.group(1)
    assert renderer_text.index("renderTransportSweepHud();") < renderer_text.index("const host = document.querySelector"), "HUD must render even when the main Toolkit panel is unavailable"

    hud_renderer = re.search(r"function renderTransportSweepHud\(\) \{([\s\S]*?)\n    \}", source)
    assert hud_renderer, "Transport Sweep HUD renderer is missing"
    hud_text = hud_renderer.group(1)
    for stat in hud["required_stats"]:
        assert stat in hud_text, f"HUD is missing required stat: {stat}"
    assert "sweep.running || sweep.stopRequested || sweep.hudFinal" in hud_text, "HUD visibility must follow the complete sweep lifecycle"
    assert "sweep.cleared" in hud_text and "sweep.skipped" in hud_text and "sweep.errors" in hud_text, "HUD totals must come from the canonical runtime counters"

    ensure_hud = re.search(r"function ensureTransportSweepHud\(\) \{([\s\S]*?)\n    \}", source)
    remove_hud = re.search(r"function removeTransportSweepHud\(\) \{([\s\S]*?)\n    \}", source)
    assert ensure_hud and remove_hud, "HUD ownership helpers are missing"
    assert "matches.shift()" in ensure_hud.group(1) and "duplicate.remove()" in ensure_hud.group(1), "HUD creation must deduplicate existing instances"
    assert "for (const hud of transportSweepHudElements())" in remove_hud.group(1), "HUD teardown must remove every remaining instance"

    start_flow = re.search(r"async function startTransportSweep\(\) \{([\s\S]*?)\n    \}\n\n    function stopTransportSweep", source)
    assert start_flow, "Transport Sweep start flow is missing"
    start_text = start_flow.group(1)
    assert "transportSweepRuntime.startedAt = Date.now()" in start_text
    assert "transportSweepRuntime.missionTotal = queue.length" in start_text
    assert "transportSweepRuntime.hudFinal = false" in start_text
    assert "transportSweepRuntime.missionIndex = missionOffset + 1" in start_text
    assert "transportSweepRuntime.hudFinal = true" in start_text
    assert f"scheduleTransportSweepHudDismiss({hud['final_summary_delay_ms']})" in start_text

    direct_click = processor_text.index("const cleared = await activateTransportSweepLssmRelease")
    direct_increment = processor_text.index("transportSweepRuntime.cleared += 1", direct_click)
    direct_log = processor_text.index("transportSweepLog(`Released", direct_increment)
    assert direct_click < direct_increment < direct_log, "Direct LSSM HUD count must update only after confirmed release and then render through the canonical log"

    fallback_click = processor_text.index("button.click()")
    fallback_confirmation = processor_text.index("const cleared = await transportSweepWaitFor", fallback_click)
    fallback_increment = processor_text.index("transportSweepRuntime.cleared += 1", fallback_confirmation)
    fallback_log = processor_text.index("transportSweepLog(`Cleared", fallback_increment)
    assert fallback_click < fallback_confirmation < fallback_increment < fallback_log, "Fallback HUD count must update only after confirmed discharge and then render through the canonical log"

    assert hud["id"] not in closer.group(1), "MissionChief lightbox cleanup must not target the persistent HUD"
    assert "removeTransportSweepHud" not in closer.group(1), "Window replacement must not remove the persistent HUD"
    print("LSSM transport sweep contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
