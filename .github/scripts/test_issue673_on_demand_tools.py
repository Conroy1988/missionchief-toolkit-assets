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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.9.5"

    measure = section(source, "    const MAP_MEASURE_MAX_POINTS", "    function coverageLeafletPathRenderer(")
    for required in [
        "const MAP_MEASURE_MAX_POINTS = 64",
        "function mapMeasurePointDistance(",
        "function mapMeasureArea(",
        "function startMapMeasure(",
        "function stopMapMeasure(",
        "map.on('click', mapMeasureRuntime.clickHandler)",
        "mapMeasureRuntime.map?.off?.('click', mapMeasureRuntime.clickHandler)",
        "hud.onclick = event =>",
        "hud[`on${type}`] = stopMapInteraction",
        "group.__mcmsMapMeasureLayer = true",
        "renderer.__mcmsMapMeasureLayer = true",
        "renderer: mapMeasureRuntime.renderer || undefined",
        "map.removeLayer(renderer)",
        "function mapDrawingTagLayer(",
        "layer.__mcmsMapMeasureLayer = true",
        "mapMeasureRuntime.points.length >= MAP_MEASURE_MAX_POINTS",
        "mapMeasureRuntime.points = []",
        "data-mcms-map-measuring",
    ]:
        assert required in measure, required
    for forbidden in [
        "runtimeSetInterval(",
        "setInterval(",
        "MutationObserver",
        "runtimeFetch(",
        "GM_xmlhttpRequest(",
        "fetch(",
        "runtimeRequestAnimationFrame(",
        "runtimeListen(",
    ]:
        assert forbidden not in measure, forbidden

    for required in [
        "mapMeasureHudId: 'mc-map-command-toolkit-map-measure'",
        "layer.__mcmsMapMeasureLayer",
        'data-action="open-map-measure"',
        "add('map-measure'",
        "stopMapMeasure(false)",
        "mapMeasureRuntime.active && mapMeasureRuntime.map !== map",
        "if (mapMeasureRuntime.active && !event.defaultPrevented && !isTypingTarget(event.target))",
        "toolkitAnalyticsRecordFeature('mapMeasure')",
        "syncMapMeasureToolbarButton()",
        "const squareKilometres = safeArea / 1000000",
        "return `${kilometres.toLocaleString('en-GB', { maximumFractionDigits })} km`",
        "return `${squareKilometres.toLocaleString('en-GB', { maximumFractionDigits })} km²`",
    ]:
        assert required in source, required

    print("Issue #673 static contract passed: Drawing preserves kilometre-first Measure as an explicit, bounded, local-only tool.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
