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
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "10.4.0"

    measure = section(source, "    const MAP_MEASURE_MAX_POINTS", "    function coverageLeafletPathRenderer(")
    for required in [
        "const MAP_MEASURE_MAX_POINTS = 64",
        "function mapMeasurePointDistance(",
        "function mapMeasureArea(",
        "function startMapMeasure(",
        "function stopMapMeasure(",
        "map.on('click', mapMeasureRuntime.clickHandler)",
        "mapMeasureRuntime.map?.off?.('click', mapMeasureRuntime.clickHandler)",
        "runtimeListen(document, 'keydown', mapMeasureRuntime.keyHandler, true)",
        "runtimeUnlisten(document, 'keydown', mapMeasureRuntime.keyHandler, true)",
        "group.__mcmsMapMeasureLayer = true",
        "renderer.__mcmsMapMeasureLayer = true",
        "renderer: mapMeasureRuntime.renderer || undefined",
        "map.removeLayer(renderer)",
        "path.__mcmsMapMeasureLayer = true",
        "marker.__mcmsMapMeasureLayer = true",
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
    ]:
        assert forbidden not in measure, forbidden

    incident = section(source, "    function incidentCardWindowRoot(", "    function refreshMissionSnapshots(")
    for required in [
        "function incidentCardModel(",
        "resourceRequirementsFromSnapshot({ ...snapshot, missingText })",
        "personalUnitCommitmentForMission(id)",
        "function renderIncidentCardCanvas(",
        "canvas.width = 1200",
        "canvas.height = 675",
        "canvas.toBlob(",
        "new ClipboardItemCtor({ 'image/png': incidentCardRuntime.blob })",
        "link.download = incidentCardRuntime.filename",
        "generated locally",
        "clearIncidentCardRuntime()",
    ]:
        assert required in incident, required
    for forbidden in [
        "runtimeSetInterval(",
        "setInterval(",
        "MutationObserver",
        "runtimeFetch(",
        "GM_xmlhttpRequest(",
        "fetch(",
    ]:
        assert forbidden not in incident, forbidden

    for required in [
        "mapMeasureHudId: 'mc-map-command-toolkit-map-measure'",
        "layer.__mcmsMapMeasureLayer",
        'data-action="open-map-measure"',
        'data-action="open-incident-card"',
        "add('map-measure'",
        "add('incident-card'",
        "if (command === 'card' && record.kind === 'mission')",
        "stopMapMeasure(false)",
        "clearIncidentCardRuntime()",
        "mapMeasureRuntime.active && mapMeasureRuntime.map !== map",
        "toolkitAnalyticsRecordFeature('mapMeasure')",
        "toolkitAnalyticsRecordFeature('incidentCard')",
    ]:
        assert required in source, required

    print("Issue #673 static contract passed: both operational tools are explicit, bounded and local-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
