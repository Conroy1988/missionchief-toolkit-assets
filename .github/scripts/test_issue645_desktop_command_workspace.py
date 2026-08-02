#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
PREFLIGHT = (ROOT / ".github" / "scripts" / "run_userscript_preflight.sh").read_text(encoding="utf-8")
RUNTIME = ".github/scripts/test_issue645_desktop_command_workspace_runtime.mjs"


def section(start: str, end: str) -> str:
    left = SOURCE.index(start)
    return SOURCE[left:SOURCE.index(end, left)]


def main() -> int:
    assert SOURCE.count("function resolveDesktopDockGrid(") == 1
    layout = section("    function applyDesktopDockLayout(", "    function stopDesktopPanelWorkspaceObservation(")
    for fragment in (
        "resolveDesktopDockGrid",
        "--mcms-desktop-dock-width",
        "--mcms-desktop-group-columns",
        "--mcms-desktop-button-columns",
        "--mcms-desktop-pin-columns",
        "mcmsDesktopDockSize",
        "mcmsDesktopDockScroll",
        "preferredGroupWidth",
        "availableContentWidth",
    ):
        assert fragment in layout, f"adaptive Desktop layout is missing {fragment}"
    assert "ResizeObserver" not in layout and "setInterval" not in layout

    for fragment in (
        'grid-template-areas:"menu filters" ". pins"',
        "repeat(var(--mcms-desktop-group-columns,4),minmax(0,1fr))",
        "repeat(var(--mcms-desktop-button-columns,2),minmax(0,1fr))",
        "height:36px!important",
        "font-size:9px!important",
        "repeat(var(--mcms-desktop-pin-columns,6),minmax(0,1fr))",
        '[data-mcms-desktop-dock-size="tight"]',
        '[data-mcms-desktop-dock-scroll="true"]',
    ):
        assert fragment in SOURCE, f"adaptive Desktop CSS is missing {fragment}"

    assert "width:min(240px,var(--mcms-desktop-dock-max-width,240px))" not in SOURCE
    assert ".github/scripts/test_issue645_desktop_command_workspace.py" in PREFLIGHT
    assert RUNTIME in PREFLIGHT
    print("Issue #645 adaptive Desktop command workspace static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
