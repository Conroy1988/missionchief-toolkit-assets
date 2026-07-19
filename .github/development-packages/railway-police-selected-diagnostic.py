#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUT = ROOT / "status" / "railway-police-selected-diagnostic.txt"
source = SOURCE.read_text(encoding="utf-8")


def extract_function(name: str) -> str:
    marker = f"function {name}"
    start = source.find(marker)
    if start < 0:
        return f"{marker}: NOT FOUND\n"
    brace = source.find("{", start)
    if brace < 0:
        return f"{marker}: OPENING BRACE NOT FOUND\n"
    depth = 0
    quote = None
    escaped = False
    template_depth = 0
    for index in range(brace, len(source)):
        char = source[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"', '`'):
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1] + "\n"
    return f"{marker}: CLOSING BRACE NOT FOUND\n"


def context(needle: str, radius: int = 900) -> str:
    position = source.find(needle)
    if position < 0:
        return f"{needle}: NOT FOUND\n"
    return source[max(0, position - radius):min(len(source), position + len(needle) + radius)] + "\n"

sections = [
    ("railway definition", context("railway-police-officer", 1400)),
    ("staff capacity", extract_function("missionRequirementsStaffCapacity")),
    ("metadata values", extract_function("missionRequirementsMetadataValues")),
    ("aggregate", extract_function("missionRequirementsAggregate")),
    ("collect units", extract_function("missionRequirementsCollectUnits")),
    ("vehicle id", extract_function("missionRequirementsVehicleId")),
]

metadata_needles = [
    "data-current-personnel",
    "data-personnel",
    "data-max-personnel",
    "data-min-personnel",
    "data-vehicle-id",
]
metadata_context = []
for needle in metadata_needles:
    cursor = 0
    hits = 0
    while True:
        position = source.find(needle, cursor)
        if position < 0:
            break
        hits += 1
        metadata_context.append(f"--- {needle} hit {hits} ---\n" + source[max(0, position - 260):position + len(needle) + 360])
        cursor = position + len(needle)
    if hits == 0:
        metadata_context.append(f"--- {needle}: no hits ---")
sections.append(("numeric metadata contexts", "\n\n".join(metadata_context) + "\n"))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    "Railway Police selected-capacity diagnostic\n"
    "==========================================\n\n"
    + "\n\n".join(f"## {title}\n{body}" for title, body in sections),
    encoding="utf-8",
)
print(OUT.relative_to(ROOT))
