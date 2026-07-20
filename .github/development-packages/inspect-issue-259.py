#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"


def function_block(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    quote = None
    escaped = False
    template_depth = 0
    i = brace
    while i < len(source):
        ch = source[i]
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch in ("'", '"', '`'):
            quote = ch
            i += 1
            continue
        if source.startswith("//", i):
            end = source.find("\n", i)
            i = len(source) if end < 0 else end + 1
            continue
        if source.startswith("/*", i):
            end = source.find("*/", i + 2)
            i = len(source) if end < 0 else end + 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
        i += 1
    raise RuntimeError(f"unterminated {name}")


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    names = [
        "missionRequirementsEquipmentTypes",
        "missionRequirementsStaffCapacity",
        "missionRequirementsCollectUnits",
        "missionRequirementsAggregate",
        "missionRequirementsResolve",
    ]
    parts = []
    for name in names:
        block = function_block(source, name)
        compact = " ".join(block.split())
        parts.append(f"[{name}] {compact[:2600]}")
    resource_pos = source.find("water-resource")
    parts.append("[water-resource-context] " + " ".join(source[max(0, resource_pos - 700):resource_pos + 1300].split()))
    raise RuntimeError("ISSUE259_SOURCE_INSPECTION || " + " || ".join(parts))


if __name__ == "__main__":
    main()
