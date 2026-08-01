#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
PREFLIGHT = (ROOT / ".github" / "scripts" / "run_userscript_preflight.sh").read_text(encoding="utf-8")
RUNTIME = ".github/scripts/test_issue643_desktop_command_grid_runtime.mjs"


def section(start: str, end: str) -> str:
    left = SOURCE.index(start)
    return SOURCE[left:SOURCE.index(end, left)]


def main() -> int:
    assert "// @version      10.2.7" in SOURCE
    assert "version: '10.2.7'" in SOURCE
    for helper in ("resolveDesktopDockPresentation", "applyDesktopDockLayout"):
        assert SOURCE.count(f"function {helper}(") == 1, f"{helper} declaration count changed"

    presentation = section("    function resolveDesktopDockPresentation(", "    function clearDesktopDockSizing(")
    for fragment in ("Math.min(920", "filterColumns", "pinColumns", "contentWidth"):
        assert fragment in presentation, f"responsive Desktop presentation missing: {fragment}"

    layout = section("    function applyDesktopDockLayout(", "    function stopDesktopPanelWorkspaceObservation(")
    for fragment in (
        "resolveDesktopDockPresentation(workspace.maxWidth)",
        "--mcms-desktop-dock-width",
        "--mcms-desktop-dock-content-width",
        "--mcms-desktop-filter-columns",
        "--mcms-desktop-pin-columns",
        "mcmsDesktopDockColumns",
    ):
        assert fragment in layout, f"Desktop grid layout missing: {fragment}"
    assert "ResizeObserver" not in layout and "setInterval" not in layout and "addEventListener" not in layout

    for fragment in (
        'grid-template-areas:"menu filters" ". pins"',
        "repeat(var(--mcms-desktop-filter-columns,4),minmax(0,1fr))",
        "repeat(var(--mcms-desktop-pin-columns,8),minmax(0,1fr))",
        "width:var(--mcms-desktop-dock-width",
        'data-mcms-command-bar-open="false"',
        ".mcms-float-label-desktop{display:block",
        ".mcms-float-icon{display:none",
        "height:36px!important",
        "overflow-x:hidden!important",
    ):
        assert fragment in SOURCE, f"Desktop command-grid CSS missing: {fragment}"

    for tablet_contract in (
        'html[data-mcms-tablet-active="true"][data-mcms-ui-theme] body #${SCRIPT.controlId} .mcms-floating-filter',
        'html[data-mcms-mobile-active="true"][data-mcms-ui-theme] body #${SCRIPT.controlId} .mcms-floating-filter',
    ):
        assert tablet_contract in SOURCE, f"retained touch layout missing: {tablet_contract}"

    assert ".github/scripts/test_issue643_desktop_command_grid.py" in PREFLIGHT
    assert RUNTIME in PREFLIGHT
    print("Issue #643 responsive Desktop command-grid static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
