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
    assert metadata and runtime and metadata.group(1) == runtime.group(1)
    assert tuple(int(part) for part in metadata.group(1).split(".")[:3]) >= (9, 1, 0)

    for name in [
        "calculateOperationalPressureModel",
        "buildOperationalPressureSnapshot",
        "createOperationalPressureBoard",
        "renderOperationalPressureBoard",
        "refreshOperationalPressureBoard",
        "toggleOperationalPressureBoard",
        "buildOperationalSitrepPayload",
        "postOperationalSitrep",
    ]:
        assert source.count(f"function {name}(") == 1, name

    controls = section(source, "    function createControl(mapEl)", "    function createPanel()")
    assert "makeActionFloatButton('open-pressure-board', 'B', 'Pressure Board'" in controls
    assert "'pressureBoard'" in controls
    assert "data-control-group=\"dashboard\"" in controls

    board = section(source, "    function createOperationalPressureBoard()", "    function renderOperationalPressureBoard(")
    for action in ["focus", "open", "pin"]:
        assert f"data-pressure-action=\"{action}\"" in source
    assert "data-pressure-command=\"sitrep\"" in board
    assert "Read-only intelligence" in board
    assert "dispatch vehicles" in board

    shortcuts = section(source, "    function handleKeyboard(event)", "    function buildThemeOptions(")
    assert "key === 'b'" in shortcuts
    assert "toggleOperationalPressureBoard()" in shortcuts

    update_ui = section(source, "    function updateUI()", "    function ensureUi()")
    assert "Operational Pressure Board: ${open ? 'active' : 'off'}. Shortcut: B." in update_ui
    assert "open ? 'ACTIVE' : 'OFF'" in update_ui
    assert "pressureBoardToggle" in update_ui

    sitrep = section(source, "    function buildOperationalSitrepPayload(", "    async function postOperationalSitrep(")
    assert "allowed_mentions: { parse: [] }" in sitrep
    assert "Read-only briefing; no units were selected or dispatched." in sitrep
    assert "discordWebhook" not in sitrep
    assert "webhookUrl" not in sitrep

    posting = section(source, "    async function postOperationalSitrep(", "    function clearDiscordPreviewChartUrl(")
    assert "readDiscordWebhookInput({ save: true })" in posting
    assert "sendDiscordWithRetry" in posting
    assert "if (!snapshot) throw new Error(" in posting
    assert "SITREP was not posted" in posting
    assert "setInterval" not in posting
    assert "MutationObserver" not in posting

    model = section(source, "    function calculateOperationalPressureModel(", "    function invalidateOperationalPressureSnapshot(")
    assert "allocatedVehicleIds" in model
    assert "fleetConflicts" in model
    assert "reserveRisks" in model
    assert "topActions: actions.slice(0, 3)" in model
    assert "dispatch" not in model.lower()

    refresh = section(source, "    async function refreshOperationalPressureBoard(", "    function closeOperationalPressureBoard(")
    assert "refreshMissionSnapshots()" in refresh
    assert "refreshPersonalVehicleData" in refresh
    assert "fetch(" not in refresh

    for theme in ["mapCommand", "cyberpunk", "fallout4", "umbrella", "factorio", "bond007", "hyrule", "godfather"]:
        assert f'html[data-mcms-ui-theme="{theme}"] #${{SCRIPT.pressureBoardId}}' in source
    assert 'html[data-mcms-tablet-active="true"] #${SCRIPT.pressureBoardId}' in source
    assert 'html[data-mcms-mobile-active="true"] #${SCRIPT.pressureBoardId}' in source
    assert "env(safe-area-inset-bottom)" in source

    print("Issue #601 Operational Pressure Board static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
