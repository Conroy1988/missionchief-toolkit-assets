#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"

source = SOURCE.read_text(encoding="utf-8")

def function_starts(name: str) -> list[int]:
    marker = f"function {name}"
    starts = []
    offset = 0
    while True:
        index = source.find(marker, offset)
        if index < 0:
            return starts
        starts.append(index)
        offset = index + len(marker)

def remove_shadowed_function(name: str, next_name: str) -> None:
    global source
    starts = function_starts(name)
    if len(starts) != 2:
        raise AssertionError(f"{name}: expected one compact replacement plus one legacy declaration, found {len(starts)}")
    legacy_start = starts[1]
    line_start = source.rfind("\n", 0, legacy_start) + 1
    legacy_end = source.index(f"function {next_name}", legacy_start)
    next_line_start = source.rfind("\n", 0, legacy_end) + 1
    source = source[:line_start] + source[next_line_start:]

remove_shadowed_function("missionRequirementsCollectUnits", "missionRequirementsMissionTypeId")
remove_shadowed_function("missionRequirementsAggregate", "missionRequirementsProgressValue")

if len(function_starts("missionRequirementsCollectUnits")) != 1:
    raise AssertionError("responding-unit collector must have one active declaration")
if len(function_starts("missionRequirementsAggregate")) != 1:
    raise AssertionError("capacity aggregate must have one active declaration")

SOURCE.write_text(source, encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")
print("Removed indentation-independent legacy declarations shadowing the v4.20.3 Matrix runtime")
