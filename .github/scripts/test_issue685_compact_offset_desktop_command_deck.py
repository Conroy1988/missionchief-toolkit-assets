#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
PREFLIGHT = (ROOT / ".github/scripts/run_userscript_preflight.sh").read_text(encoding="utf-8")


def main() -> None:
    layout = SOURCE[SOURCE.index("    function applyDesktopDockLayout("):SOURCE.index("    function stopDesktopPanelWorkspaceObservation(")]
    assert "resolveDesktopDockGrid(workspace.maxWidth" in layout
    assert "workspace.maxWidth - grid.dockWidth" in layout
    assert "const effectiveNudgeX = rightAnchored" in layout
    assert "--mcms-desktop-dock-offset-x" in layout
    assert "workspace.maxWidth - nudgeX" not in layout
    assert "margin-left:0!important" in SOURCE
    assert "var(--mcms-desktop-dock-offset-x,0px)" in SOURCE
    for forbidden in ("setInterval(", "MutationObserver(", "requestAnimationFrame(", "fetch("):
        assert forbidden not in layout
    assert "test_issue685_compact_offset_desktop_command_deck.py" in PREFLIGHT
    assert "test_issue685_compact_offset_desktop_command_deck_runtime.mjs" in PREFLIGHT
    print("Issue #685 compact offset Desktop command deck static contract passed.")


if __name__ == "__main__":
    main()
