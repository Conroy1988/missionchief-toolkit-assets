#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
PREFLIGHT = (ROOT / ".github/scripts/run_userscript_preflight.sh").read_text(encoding="utf-8")


def main() -> None:
    resolver = SOURCE[SOURCE.index("    function resolveDesktopDockGrid("):SOURCE.index("    function clearDesktopDockSizing(")]
    layout = SOURCE[SOURCE.index("    function applyDesktopDockLayout("):SOURCE.index("    function stopDesktopPanelWorkspaceObservation(")]
    assert "const balanced = groupColumns === 3 && safeHeight >= 280;" in resolver
    assert "if (balanced) groupColumns = 2;" in resolver
    assert "pinWidth = balanced && pins.height ? contentWidth : pins.width;" in resolver
    assert "grid.balanced ? 'balanced' : 'compact'" in layout
    assert '[data-mcms-desktop-dock-flow="balanced"] .mcms-floating-filter{align-items:stretch!important}' in SOURCE
    assert '[data-mcms-desktop-dock-flow="balanced"] .mcms-screen-pin-btn{height:36px!important;min-height:36px!important}' in SOURCE
    for forbidden in ("setInterval(", "MutationObserver(", "requestAnimationFrame(", "fetch("):
        assert forbidden not in resolver
    assert "test_issue683_balanced_desktop_command_deck.py" in PREFLIGHT
    assert "test_issue683_balanced_desktop_command_deck_runtime.mjs" in PREFLIGHT
    print("Issue #683 balanced Desktop command deck static contract passed.")


if __name__ == "__main__":
    main()
