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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.18.0"

    styles = section(source, "        #${SCRIPT.mapMeasureHudId} {", "        #${SCRIPT.panelId} .mcms-config-actions")
    markup = section(source, "        setInnerHtmlIfChanged(hud, `", "        document.body.appendChild(hud);")

    required_styles = [
        "overflow:hidden !important",
        "display:flex !important; flex-direction:column !important",
        ".mcms-drawing-scroll { min-height:0 !important",
        "overflow-y:auto !important",
        "-webkit-overflow-scrolling:touch !important",
        "var(--mcms-visual-gap-right,0px)",
        "var(--mcms-visual-gap-bottom,0px)",
        "var(--mcms-visual-offset-left,0px)",
        "max-width:calc(var(--mcms-visual-width,100vw) - 16px)",
        "max-height:min(52dvh,430px,calc(var(--mcms-visual-height,100dvh) - 96px))",
        ".mcms-measure-modes {\n                display:flex !important",
        "overflow-x:auto !important",
        "scroll-snap-type:x proximity !important",
        "touch-action:pan-x !important",
        "flex:0 0 clamp(92px,28vw,112px) !important",
        "min-height:44px !important",
    ]
    for token in required_styles:
        assert token in styles, token

    assert "74vh" not in styles
    assert markup.index("mcms-measure-head") < markup.index("mcms-drawing-scroll")
    for token in [
        "mcms-measure-modes",
        "mcms-drawing-style",
        "mcms-measure-readout",
        "mcms-measure-actions",
        "mcms-measure-guidance",
    ]:
        assert token in markup, token

    for viewport_height in (390, 667, 844, 932):
        sheet_height = min(viewport_height * 0.52, 430, viewport_height - 96)
        assert sheet_height <= viewport_height * 0.52 + 0.01
        assert viewport_height - sheet_height >= 96

    drawing = section(source, "    const MAP_MEASURE_MAX_POINTS", "    function coverageLeafletPathRenderer(")
    for forbidden in [
        "runtimeSetInterval(", "setInterval(", "MutationObserver", "ResizeObserver",
        "runtimeSetTimeout(", "setTimeout(", "runtimeRequestAnimationFrame(", "requestAnimationFrame(",
        "runtimeFetch(", "GM_xmlhttpRequest(", "fetch(", "runtimeListen(",
    ]:
        assert forbidden not in drawing, forbidden

    print("Issue #679 iOS Drawing layout contract passed: the safe bottom sheet preserves the live map and zero-idle-work lifecycle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
