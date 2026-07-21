#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs/issue-230-probability-source-inspection-v2.txt"


def extract_function(source: str, name: str) -> str:
    match = re.search(rf"\bfunction\s+{re.escape(name)}\s*\(", source)
    if not match:
        return f"MISSING: {name}\n"
    start = match.start()
    opening = source.find("{", match.end())
    if opening < 0:
        return f"MISSING OPENING BRACE: {name}\n"
    depth = 0
    quote = None
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        else:
            if char in ("'", '"', "`"):
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return source[start:index + 1]
    return f"UNTERMINATED: {name}\n"


def matching_lines(source: str, tokens: tuple[str, ...]) -> str:
    output = []
    for line_no, line in enumerate(source.splitlines(), 1):
        if any(token.casefold() in line.casefold() for token in tokens):
            output.append(f"{line_no:06d}: {line}")
    return "\n".join(output) or "NO MATCHES"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    names = (
        "missionRequirementsCatalogueText",
        "missionRequirementsCatalogueRowKind",
        "missionRequirementsCatalogueRequirement",
        "missionRequirementsCataloguePersonnelRequirements",
        "missionRequirementsCatalogueParseDocument",
        "missionRequirementsCatalogueCompare",
        "missionRequirementsReconcileCatalogue",
        "missionRequirementsParseGenericText",
        "missionRequirementsCleanRemaining",
        "missionRequirementsSafeDiagnostic",
    )
    output = ["Issue #230 focused catalogue classification inspection"]
    for name in names:
        output.extend((f"\n===== {name} =====", extract_function(source, name)))
    output.extend((
        "\n===== RELATED SOURCE LINES =====",
        matching_lines(source, (
            "catalogueClassification",
            "classification:",
            "informational",
            "preconditions",
            "probability",
            "when available",
            "only required",
            "patient transport",
            "critical care",
            "unresolved.push",
        )),
    ))
    REPORT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)} ({REPORT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
