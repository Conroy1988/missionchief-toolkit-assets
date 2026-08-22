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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.16.7"

    palette = section(source, "    function commandPaletteNormalise(", "    function closeHelpCenter(")
    for required in [
        "function buildCommandPaletteEntries(",
        "function commandPaletteEntryScore(",
        "function commandPaletteSearch(",
        "function commandPaletteUpdateSelection(",
        "function commandPaletteTrapFocus(",
        "function createCommandPalette(",
        "function openCommandPalette(",
        "function closeCommandPalette(",
        "focusMissionById(snapshot.missionId, true)",
        "getPersonalVehicleRecords()",
        "getBuildingRecordIndex()",
        "QUICK_PLACES",
        "state.bookmarks",
        "state.profiles",
        ".mcms-command-card[data-command-card]",
        'role="combobox"',
        'role="listbox"',
        'role="option"',
        "event.key === 'ArrowDown'",
        "event.key === 'ArrowUp'",
        "event.key === 'Enter'",
        "event.key === 'Escape'",
        "event.key !== 'Tab'",
        "commandPaletteReturnFocus",
    ]:
        assert required in palette, required

    for kind in ["action", "mission", "vehicle", "building", "location", "setting"]:
        assert f"kind: '{kind}'" in source, kind

    for forbidden in [
        "runtimeSetTimeout(",
        "runtimeSetInterval(",
        "runtimeRequestAnimationFrame(",
        "runtimeRegisterTask(",
        "MutationObserver",
        "GM_xmlhttpRequest",
        "fetch(",
        "startDispatchRecruitment(",
        "applyDispatchRecruitmentStation(",
        "selectVehicle",
    ]:
        assert forbidden not in palette, forbidden

    for required in [
        "commandPaletteId: 'mc-map-command-toolkit-command-palette'",
        "makeActionFloatButton('open-command-palette', 'K'",
        "palette: 'K'",
        "state.inputStudio.hotkeys[key] === binding",
        "data-action=\"open-command-palette\"",
        "commandPalette: Object.freeze({ label: 'Palette'",
        "if (command === 'commandPalette') { openCommandPalette(); return; }",
        "SCRIPT.commandPaletteId,",
        "data-mcms-command-palette-open",
        "closeCommandPalette({ restoreFocus: false })",
        "Open Dispatch Recruitment",
        "commandPaletteOpenSetting('dispatch', 'dispatch-recruitment')",
    ]:
        assert required in source, required

    responsive_css = section(
        source,
        "        #${SCRIPT.commandPaletteId} {",
        "        #${SCRIPT.commandExperienceModalId} {",
    )
    for required in [
        'html[data-mcms-ui-theme="cyberpunk"]',
        'html[data-mcms-ui-theme="godfather"]',
        'html[data-mcms-economy="true"]',
        "@media (max-width:620px)",
        "safe-area-inset-top",
        "safe-area-inset-bottom",
    ]:
        assert required in responsive_css, required

    print("Issue #618 Command Palette static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
