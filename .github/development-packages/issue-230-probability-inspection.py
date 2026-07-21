#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
REPORT = ROOT / "docs/issue-230-probability-source-inspection.txt"


def extract_function(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.find(marker)
    if start < 0:
        return f"MISSING: {name}\n"
    opening = source.find("{", start)
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


def context(source: str, token: str, radius: int = 1800) -> str:
    positions = []
    start = 0
    folded = source.casefold()
    needle = token.casefold()
    while True:
        index = folded.find(needle, start)
        if index < 0:
            break
        positions.append(index)
        start = index + max(1, len(needle))
    if not positions:
        return f"NO MATCHES: {token}\n"
    chunks = []
    for number, index in enumerate(positions, 1):
        chunks.append(f"\n--- match {number} ---\n")
        chunks.append(source[max(0, index - radius):min(len(source), index + len(token) + radius)])
    return "".join(chunks)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    test = TEST.read_text(encoding="utf-8")
    functions = (
        "missionRequirementsNormalizeText",
        "missionRequirementsParseText",
        "missionRequirementsParseSource",
        "missionRequirementsCatalogueDescriptor",
        "missionRequirementsCatalogueRequirement",
        "missionRequirementsCataloguePersonnelRequirements",
        "missionRequirementsCatalogueParseDocument",
        "missionRequirementsReconcileCatalogue",
        "missionRequirementsResolve",
        "missionRequirementsPanelHtml",
        "missionRequirementsOverallState",
    )
    output = ["Issue #230 probability and availability metadata inspection"]
    for name in functions:
        output.extend((f"\n===== {name} =====", extract_function(source, name)))
    for token in (
        "catalogueProbability",
        "Probability of",
        "only required, when available",
        "only required when available",
        "probability",
        "conditional",
        "unresolved",
        "Mission Info",
    ):
        output.extend((f"\n===== TOKEN: {token} =====", context(source, token)))
    output.extend(("\n===== CURRENT TEST CONTEXT =====", context(test, "catalogueProbability", 2600)))
    REPORT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)} ({REPORT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
