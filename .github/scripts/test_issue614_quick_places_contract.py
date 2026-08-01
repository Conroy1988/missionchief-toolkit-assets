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
    assert metadata and runtime
    assert metadata.group(1) == runtime.group(1) == "10.2.0"

    quick_places = section(source, "    const QUICK_PLACES = [", "    const SMART_BOOKMARK_LABEL_MAX")
    expected = [
        "{ id: 'edi', label: 'EDI', name: 'Edinburgh', lat: 55.9533, lng: -3.1883, zoom: 11 }",
        "{ id: 'fife', label: 'FIFE', name: 'Fife', lat: 56.2082, lng: -3.1495, zoom: 10 }",
        "{ id: 'wake', label: 'WKFD', name: 'Wakefield', lat: 53.6833, lng: -1.4977, zoom: 11 }",
        "{ id: 'lond', label: 'LDN', name: 'London', lat: 51.5074, lng: -0.1278, zoom: 10 }",
        "{ id: 'newc', label: 'NCL', name: 'Newcastle', lat: 54.9783, lng: -1.6178, zoom: 11 }",
    ]
    positions = [quick_places.index(entry) for entry in expected]
    assert positions == sorted(positions)
    assert quick_places.count("{ id:") == 5

    catalogue = section(source, "    const QUICK_PLACES = [", "    const LEGACY_QUICK_PLACE_REPLACEMENTS")
    for legacy_name in ("Glasgow", "Dundee", "Stirling"):
        assert legacy_name not in catalogue

    for required in [
        "glas: 'wake'",
        "dund: 'lond'",
        "stir: 'newc'",
        "function normaliseQuickPins(loadedQuickPins, defaultQuickPins)",
        "loaded[legacyId] === true",
        "Object.prototype.hasOwnProperty.call(loaded, replacementId)",
        "QUICK_PLACES.map(place => [place.id, Boolean(merged[place.id])])",
        "quickPins: normaliseQuickPins(parsed.quickPins, base.quickPins)",
    ]:
        assert required in source, required

    print("Issue #614 Quick Jump catalogue and migration contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
