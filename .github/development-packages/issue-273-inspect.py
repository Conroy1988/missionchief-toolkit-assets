#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src/data/mission-requirements-en_GB.json"
OUTPUT = ROOT / "docs/issue-273-runtime-snippets.txt"


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
    sections = []
    key = '"key":"public-order-level-2"'
    pos = source.find(key)
    sections += ["=== PUBLIC ORDER DEFINITION ===", source[max(0, pos - 120):pos + 700]]
    police_key = '"key":"police-officers"'
    pos = source.find(police_key)
    sections += ["=== POLICE OFFICERS DEFINITION ===", source[max(0, pos - 120):pos + 700]]
    staff_marker = "const MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE"
    pos = source.find(staff_marker)
    sections += ["=== STAFF RANGES ===", source[pos:pos + 2400]]
    for name in [
        "missionRequirementsStaffCapacity",
        "missionRequirementsDefaultStaffCapacity",
        "missionRequirementsCollectUnits",
        "missionRequirementsUnitContribution",
        "missionRequirementsAggregate",
        "missionRequirementsCoverageRow",
        "missionRequirementsResolve",
    ]:
        sections += [f"=== {name} ===", function_block(source, name)]
    data = DATA.read_text(encoding="utf-8")
    pos = data.find('"key":"public-order-level-2"')
    sections += ["=== DATASET STAFF REQUIREMENTS ===", data[pos:pos + 1000]]
    OUTPUT.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
