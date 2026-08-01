#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
PREFLIGHT = (ROOT / ".github" / "scripts" / "run_userscript_preflight.sh").read_text(encoding="utf-8")
RUNTIME = ".github/scripts/test_issue641_desktop_dock_fit_runtime.mjs"


def section(start: str, end: str) -> str:
    left = SOURCE.index(start)
    return SOURCE[left:SOURCE.index(end, left)]


def main() -> int:
    for helper in ("resolveDesktopDockWorkspace", "resolveDesktopDockPresentation", "clearDesktopDockSizing", "applyDesktopDockLayout"):
        assert SOURCE.count(f"function {helper}(") == 1, f"{helper} declaration count changed"

    layout = section("    function applyDesktopDockLayout(", "    function stopDesktopPanelWorkspaceObservation(")
    assert "activeDeviceLayout !== 'desktop'" in layout
    assert "resolveDesktopDockWorkspace" in layout
    assert "--mcms-desktop-filter-max-height" in layout
    assert "--mcms-desktop-pin-max-height" in layout
    assert "mcmsDesktopDockFit" in layout
    assert "ResizeObserver" not in layout and "setInterval" not in layout

    fit = section("    function fitControlToMap()", "    function setPanelCssPosition(")
    assert "applyDesktopDockLayout(mapEl)" in fit
    assert fit.count("clearDesktopDockSizing()") >= 3

    observer = section("    function observeDesktopPanelWorkspace(", "    function applyDesktopPanelSizing(")
    assert "applyDesktopDockLayout(mapEl)" in observer

    feed = section("    function removeMajorIncidentFeed()", "    function majorIncidentFeedItemHtml(")
    assert feed.count("fitControlToMap();") >= 4

    for fragment in (
        'html[data-mcms-device-layout="desktop"]',
        "var(--mcms-desktop-dock-max-height",
        "var(--mcms-desktop-filter-max-height",
        "overflow-y:auto!important",
        "overscroll-behavior:contain!important",
    ):
        assert fragment in SOURCE, f"desktop containment CSS missing: {fragment}"

    assert ".github/scripts/test_issue641_desktop_dock_fit.py" in PREFLIGHT
    assert RUNTIME in PREFLIGHT
    print("Issue #641 Desktop dock containment static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
