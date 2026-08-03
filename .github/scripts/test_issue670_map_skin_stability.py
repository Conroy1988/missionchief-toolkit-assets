#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def filter_map(source: str, pattern: str) -> dict[str, str]:
    return {
        skin: value.strip()
        for skin, value in re.findall(pattern, source)
    }


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    normal = filter_map(
        source,
        r'html\[data-mc-map-skin="([^"]+)"\] \.leaflet-tile-pane img\.leaflet-tile \{ filter: ([^;]+) !important; \}',
    )
    moving = filter_map(
        source,
        r'html\[data-mcms-map-moving="true"\]\[data-mc-map-skin="([^"]+)"\] \.leaflet-tile-pane \{ filter:([^;]+) !important; \}',
    )
    road = filter_map(
        source,
        r'html\[data-mcms-road-priority="true"\]\[data-mc-map-skin="([^"]+)"\] \.leaflet-tile-pane img\.leaflet-tile \{ filter: ([^;]+) !important; \}',
    )
    moving_road = filter_map(
        source,
        r'html\[data-mcms-map-moving="true"\]\[data-mcms-road-priority="true"\]\[data-mc-map-skin="([^"]+)"\] \.leaflet-tile-pane \{ filter:([^;]+) !important; \}',
    )

    expected_skins = {
        "default", "control", "incident", "roads", "urban", "rural", "nightshift",
        "fireCommand", "policeTactical", "medicalControl", "coastalCommand",
    }
    assert normal.keys() == expected_skins, normal.keys()
    assert road.keys() == expected_skins, road.keys()
    assert moving == normal, (moving, normal)
    assert moving_road == road, (moving_road, road)
    assert source.count('html[data-mcms-map-moving="true"] .leaflet-tile-pane img.leaflet-tile { filter:none !important; }') == 1
    assert 'html[data-mcms-map-moving="true"] .leaflet-pane [class*="mcms-"]' in source
    assert "animation-play-state:paused !important" in source
    assert "backdrop-filter:none !important" in source
    assert "const MAP_INTERACTION_SETTLE_MS = 90" in source

    print("Issue #670 contract passed: every moving skin keeps normal and Road Priority colour parity through one tile-pane composite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
