#!/usr/bin/env python3
"""Static contract for the desktop-only resizable Toolkit Workspace."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
PREFLIGHT = (ROOT / ".github" / "scripts" / "run_userscript_preflight.sh").read_text(encoding="utf-8")


def section(start: str, end: str) -> str:
    left = SOURCE.index(start)
    return SOURCE[left:SOURCE.index(end, left)]


def main() -> int:
    required = (
        "const DESKTOP_WORKSPACE_MAX_WIDTH = 1440",
        "panelHeightPx: null",
        "mcms-workspace-window",
        "mcms-workspace-maximize",
        "mcms-workspace-resize-handle",
        "toggle-workspace-maximize",
        "container-name:mcms-toolkit-workspace",
        "@container mcms-toolkit-workspace (min-width:1100px)",
        "@container mcms-toolkit-workspace (max-width:760px)",
        "--mcms-workspace-body-size:14px",
        "--mcms-workspace-meta-size:12px",
        'html:is([data-mcms-tablet-active="true"],[data-mcms-mobile-active="true"])',
        "runtimeListen(resizeHandle, 'pointerdown', startPanelResize)",
        "runtimeListen(resizeHandle, 'pointermove', movePanelResize)",
        "runtimeListen(resizeHandle, 'pointerup', endPanelResize)",
        "runtimeListen(resizeHandle, 'pointercancel', endPanelResize)",
        "runtimeListen(resizeHandle, 'keydown', resizePanelFromKeyboard)",
        "document.body.appendChild(panel)",
    )
    missing = [fragment for fragment in required if fragment not in SOURCE]
    assert not missing, f"Desktop Toolkit Workspace fragments missing: {missing}"

    assert SOURCE.count("function createPanel(") == 1, "workspace must retain one panel factory"
    assert SOURCE.count("function startPanelResize(") == 1
    assert SOURCE.count("function movePanelResize(") == 1
    assert SOURCE.count("function endPanelResize(") == 1
    assert SOURCE.count("function resizePanelFromKeyboard(") == 1
    assert SOURCE.count("function toggleDesktopWorkspaceMaximize(") == 1

    resizing = section("    function startPanelResize(", "    function toggleDesktopWorkspaceMaximize(")
    assert "saveState()" not in resizing, "pointer movement must not write settings continuously"
    end_resize = section("    function endPanelResize(", "    function toggleDesktopWorkspaceMaximize(")
    assert "preferences.panelWidth" in end_resize
    assert "preferences.panelHeightPx" in end_resize
    assert "preferences.panelPosition" in end_resize
    assert "saveAndApplyPersonalisation" in end_resize

    maximization = section("    function toggleDesktopWorkspaceMaximize(", "    function setPanelCssPosition(")
    assert "saveState()" not in maximization, "temporary maximise state must not overwrite saved geometry"
    assert "applyDesktopPanelSizing(panel)" in maximization
    assert "panelWorkspaceRestoreGeometry" in maximization

    dock = section("    function applyDesktopDockLayout(", "    function stopDesktopPanelWorkspaceObservation(")
    assert "panelResizeState" not in dock, "map toolbar fitter must remain independent from workspace resizing"

    assert ".github/scripts/test_desktop_toolkit_workspace.py" in PREFLIGHT
    assert ".github/scripts/test_desktop_toolkit_workspace_runtime.mjs" in PREFLIGHT
    print("Desktop Toolkit Workspace static contract passed: single runtime, resize-on-release persistence, readable container layout and touch isolation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
