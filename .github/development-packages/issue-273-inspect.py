#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src/data/mission-requirements-en_GB.json"


def function_block(text: str, name: str) -> str:
    marker = f"function {name}("
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"missing {name}")
    brace = text.find("{", start)
    depth = 0
    quote = None
    escape = False
    for index in range(brace, len(text)):
        char = text[index]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise RuntimeError(f"unterminated {name}")


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    print("=== PUBLIC ORDER DEFINITION ===")
    key = '"key":"public-order-level-2"'
    pos = source.find(key)
    print(source[max(0, pos - 80):pos + 520])
    print("=== STAFF RANGES ===")
    staff_marker = "const MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE"
    pos = source.find(staff_marker)
    print(source[pos:pos + 1200])
    for name in [
        "missionRequirementsCollectUnits",
        "missionRequirementsUnitContribution",
        "missionRequirementsAggregate",
        "missionRequirementsCoverageRow",
        "missionRequirementsResolve",
    ]:
        print(f"=== {name} ===")
        print(function_block(source, name))
    print("=== DATASET STAFF REQUIREMENTS ===")
    data = DATA.read_text(encoding="utf-8")
    pos = data.find('"key":"public-order-level-2"')
    print(data[pos:pos + 500])


if __name__ == "__main__":
    main()
