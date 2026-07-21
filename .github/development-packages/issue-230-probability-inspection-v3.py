#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs/issue-230-catalogue-parser-body.txt"


def function_body(source: str, name: str) -> str:
    match = re.search(rf"\bfunction\s+{re.escape(name)}\s*\(", source)
    if not match:
        raise RuntimeError(f"missing function {name}")
    opening_paren = source.find("(", match.start())
    paren_depth = 0
    brace_depth = 0
    bracket_depth = 0
    quote = None
    escaped = False
    body_open = None
    for index in range(opening_paren, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"', "`"):
            quote = char
            continue
        if char == "(": paren_depth += 1
        elif char == ")":
            paren_depth -= 1
            if paren_depth == 0:
                cursor = index + 1
                while cursor < len(source) and source[cursor].isspace(): cursor += 1
                if cursor >= len(source) or source[cursor] != "{":
                    raise RuntimeError(f"missing body opening for {name}")
                body_open = cursor
                break
        elif char == "{": brace_depth += 1
        elif char == "}": brace_depth -= 1
        elif char == "[": bracket_depth += 1
        elif char == "]": bracket_depth -= 1
    if body_open is None:
        raise RuntimeError(f"unable to locate body for {name}")
    depth = 0
    quote = None
    escaped = False
    for index in range(body_open, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"', "`"):
            quote = char
        elif char == "{": depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():index + 1]
    raise RuntimeError(f"unterminated function {name}")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    names = (
        "missionRequirementsCatalogueParseDocument",
        "missionRequirementsCatalogueRowClassification",
        "missionRequirementsCatalogueRequirement",
        "missionRequirementsReconcileCatalogue",
    )
    output = []
    for name in names:
        output.extend((f"===== {name} =====", function_body(source, name) if f"function {name}" in source else f"MISSING: {name}"))
    REPORT.write_text("\n\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)} ({REPORT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
