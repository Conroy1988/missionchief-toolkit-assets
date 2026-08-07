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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.6.1"

    drawing = section(source, "    const MAP_MEASURE_MAX_POINTS", "    function coverageLeafletPathRenderer(")
    for required in [
        "const MAP_DRAWING_MAX_OBJECTS = 48",
        "const MAP_DRAWING_MAX_FREEHAND_POINTS = 160",
        "const MAP_DRAWING_FREEHAND_SAMPLE_PIXELS = 6",
        "distance: Object.freeze(", "area: Object.freeze(", "line: Object.freeze(",
        "arrow: Object.freeze(", "freehand: Object.freeze(", "circle: Object.freeze(",
        "rectangle: Object.freeze(", "polygon: Object.freeze(", "label: Object.freeze(", "marker: Object.freeze(",
        "function mapDrawingCreateObjectLayers(",
        "function mapDrawingAddObject(",
        "function mapDrawingHandleFreehandStart(",
        "function mapDrawingHandleFreehandMove(",
        "function mapDrawingHandleFreehandEnd(",
        "map.on('mousedown touchstart', mapMeasureRuntime.pointerStartHandler)",
        "map.on('mousemove touchmove', mapMeasureRuntime.pointerMoveHandler)",
        "map.on('mouseup touchend mouseout', mapMeasureRuntime.pointerEndHandler)",
        "mapMeasureRuntime.map?.off?.('mousedown touchstart', mapMeasureRuntime.pointerStartHandler)",
        "mapMeasureRuntime.map?.off?.('mousemove touchmove', mapMeasureRuntime.pointerMoveHandler)",
        "mapMeasureRuntime.map?.off?.('mouseup touchend mouseout', mapMeasureRuntime.pointerEndHandler)",
        "mapMeasureRuntime.group?.remove?.()",
        "mapMeasureRuntime.draftGroup?.remove?.()",
        "pageWindow.prompt?.('Temporary map label:'",
        "mapDrawingRestoreDragging()",
        "data-drawing-colour",
        "data-drawing-style",
        "data-drawing-weight",
        "<strong>Drawing</strong>",
    ]:
        assert required in drawing, required

    for forbidden in [
        "runtimeSetInterval(", "setInterval(", "MutationObserver", "ResizeObserver",
        "runtimeSetTimeout(", "setTimeout(", "runtimeRequestAnimationFrame(", "requestAnimationFrame(",
        "runtimeFetch(", "GM_xmlhttpRequest(", "fetch(", "runtimeListen(", "localStorage", "sessionStorage",
    ]:
        assert forbidden not in drawing, forbidden

    for required in [
        "'open-map-measure': 'Drawing'",
        "makeActionFloatButton('open-map-measure', '', 'Drawing'",
        "<span class=\"mcms-label\">Drawing</span>",
        "`${mapMeasureRuntime.active ? 'Return to' : 'Open'} Drawing`",
        "mapMeasureHudId: 'mc-map-command-toolkit-map-measure'",
        "toolkitAnalyticsRecordFeature('mapMeasure')",
        ".mcms-map-drawing-arrow-icon",
        ".mcms-map-drawing-label-icon",
    ]:
        assert required in source, required

    print("Issue #677 static contract passed: Drawing is unified, bounded, session-local and dormant until opened.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
