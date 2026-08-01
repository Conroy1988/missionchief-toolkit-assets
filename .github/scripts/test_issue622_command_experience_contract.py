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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.2.6"

    for required in [
        "const FEATURE_BEACON_KEYS = Object.freeze(['context', 'reskin', 'dock', 'input', 'safeMode', 'unitLocator', 'sessionCleanup'])",
        "const DEFAULT_HOTKEY_BINDINGS = Object.freeze({",
        "missionChiefReskin: false",
        "autoHideDock: defaultAutoHideDockState()",
        "inputStudio: defaultInputStudioState()",
        "safeMode: normaliseSafeModeState(null)",
        "data-mcms-missionchief-reskin",
        "data-mcms-dock-auto-hide",
        "data-mcms-auto-hide-axis",
        "data-mcms-safe-mode",
        "data-feature-beacon",
        'data-action="open-input-studio"',
        'data-action="open-shell-studio"',
        'data-action="toggle-safe-mode"',
        'data-personal-pane="input"',
        'data-personal-pane="shell"',
        "function openFeatureRoute(",
        "function handleContextCommandRequest(",
        "function setToolkitSafeMode(",
        "function handleDockGesturePointerUp(",
        "runtimeListen(document, 'contextmenu', handleContextCommandRequest, true)",
        "closeContextCommandMenu()",
    ]:
        assert required in source, required

    context = section(source, "    function contextCommandRecordFromElement(", "    function loadMissionProgressState(")
    for required in [
        "Focus on map",
        "Open mission",
        "Find in Command Palette",
        "pageWindow.lightboxOpen(record.route)",
        "markFeatureBeaconViewed('context')",
    ]:
        assert required in context, required
    for forbidden in ["dispatch", "vehicleSelection", "clickVehicle", "fetch(", "GM_xmlhttpRequest("]:
        assert forbidden not in context, forbidden

    safe_mode = section(source, "    function safeModeSuspendedModules(", "    function keyboardBindingFromEvent(")
    for required in [
        "captureSettingsSnapshot(state",
        "state.safeMode = { enabled: true",
        "state.activeTab = 'settings'",
        "state.safeMode = { enabled: false",
        "reconcileFeatureRefreshes({ includeSnapshots: !next",
        "settings preserved",
        "modules restored",
    ]:
        assert required in safe_mode, required
    for forbidden in ["discordWebhook =", "financialVault =", "defaultState()", "localStorage.clear", "GM_deleteValue"]:
        assert forbidden not in safe_mode, forbidden

    for feature in ["context", "reskin", "dock", "input", "safeMode"]:
        assert feature in source

    gesture = section(source, "    function handleDockGesturePointerDown(", "    function quickWheelSlotValue(")
    assert "Math.max(Math.abs(dx), Math.abs(dy)) < 56" in gesture
    assert "event.pointerType === 'mouse'" in gesture
    assert "state.safeMode.enabled" in gesture

    print("Issue #622 retained command-experience static contract passed on v10.2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
