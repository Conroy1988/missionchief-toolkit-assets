#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
PREFLIGHT = (ROOT / ".github" / "scripts" / "run_userscript_preflight.sh").read_text(encoding="utf-8")


def section(start: str, end: str) -> str:
    left = SOURCE.index(start)
    return SOURCE[left:SOURCE.index(end, left)]


def main() -> int:
    styles = section(
        "        /* Issue #681: mid-sized Desktop windows use a wider, shorter command surface.",
        "        html[data-mcms-ui-theme] body #${SCRIPT.controlId} {",
    )
    for token in (
        "@media (min-width:1200px) and (max-width:2239px)",
        "grid-template-columns:142px minmax(0,1fr)",
        "grid-template-rows:repeat(6,minmax(48px,auto))",
        "@media (min-width:1360px) and (min-height:900px) and (max-width:2239px)",
        '.mcms-tab-panel[data-panel="settings"].mcms-active',
        "column-width:230px",
        "column-count:3",
        "column-fill:balance",
        "break-inside:avoid-column",
    ):
        assert token in styles, f"responsive Desktop menu CSS is missing {token}"

    assert 'data-mcms-device-layout="desktop"' in styles
    assert 'data-mcms-tablet-active="true"' in styles
    assert 'data-mcms-mobile-active="true"' in styles

    personalisation = section("    function applyPersonalisationStyle()", "    function mapControlLayoutKey(")
    for token in (
        "Number(desktopPreferences.panelWidth) === 720",
        "width:min(68vw,clamp(720px,calc(1844px - 50vw),1040px),calc(100vw - 24px))",
        '${responsiveDesktopPanelWidth}',
        "const css = `",
        "if (style.textContent !== css) style.textContent = css;",
    ):
        assert token in personalisation, f"adaptive Desktop width is missing {token}"

    sizing = section("    function applyDesktopPanelSizing(", "    function getIosBrowserSignals(")
    for token in (
        "resolveResponsiveDesktopPanelHeightCap",
        "desktopPreferences.panelHeight / 100",
        "responsiveHeightCap",
        "resolveResponsiveDesktopPanelWidth(viewport, desktopPreferences, availableWidth)",
        "panel.style.setProperty('width', `${savedWorkspaceWidth}px`, 'important');",
        "panel.dataset.mcmsWorkspaceSize = `${savedWorkspaceWidth}:${desiredMaxHeight}:windowed`;",
        "function resolveResponsiveDesktopPanelWidth(",
        "viewportWidth * 0.68",
        "1844 - (viewportWidth * 0.5)",
        "Number.POSITIVE_INFINITY",
    ):
        assert token in sizing, f"responsive Desktop height sizing is missing {token}"
    for forbidden in ("setInterval(", "MutationObserver", "ResizeObserver", "requestAnimationFrame(", "fetch("):
        assert forbidden not in sizing, f"responsive menu introduced background work through {forbidden}"
    assert "panel.style.removeProperty('width');" not in sizing, "ordinary content changes can no longer release the fitted Desktop width"

    positioning = section("    function setPanelCssPosition(", "    function clampPanelPosition(")
    assert "clearTabletPanelSizing(panel);\n            applyDesktopPanelSizing(panel);" in positioning, "Desktop tab changes must restore sizing after clearing touch-layout geometry"

    assert ".github/scripts/test_issue681_responsive_desktop_menu.py" in PREFLIGHT
    assert ".github/scripts/test_issue681_responsive_desktop_menu_runtime.mjs" in PREFLIGHT
    print("Issue #681 responsive Desktop menu static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
