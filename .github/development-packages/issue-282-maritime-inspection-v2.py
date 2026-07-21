#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src/data/mission-requirements-en_GB.json"
REPORT = ROOT / "docs/issue-282-maritime-source-inspection.txt"


def extract_function(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.find(marker)
    if start < 0:
        raise RuntimeError(f"missing function {name}")
    opening = source.find("{", start)
    if opening < 0:
        raise RuntimeError(f"missing opening brace for {name}")
    depth = 0
    quote = None
    escaped = False
    index = opening
    while index < len(source):
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
        index += 1
    raise RuntimeError(f"unterminated function {name}")


def extract_statement(source: str, marker: str, terminator: str = ";") -> str:
    start = source.find(marker)
    if start < 0:
        raise RuntimeError(f"missing statement {marker}")
    end = source.find(terminator, start)
    if end < 0:
        raise RuntimeError(f"unterminated statement {marker}")
    return source[start:end + len(terminator)]


def embedded_definitions(source: str) -> list[dict]:
    marker = "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze("
    start = source.find(marker)
    if start < 0:
        raise RuntimeError("missing embedded definitions")
    payload_start = start + len(marker)
    payload_end = source.find(");", payload_start)
    if payload_end < 0:
        raise RuntimeError("unterminated embedded definitions")
    return json.loads(source[payload_start:payload_end])


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    definitions = embedded_definitions(source)

    relevant_keys = {
        "boat-or-inland", "ilb-or-alb", "ilb", "alb", "4x4",
        "rescue-watercraft", "hovercraft", "medical-trailer", "sar-support",
    }
    relevant_definitions = [entry for entry in definitions if entry.get("key") in relevant_keys]
    relevant_dataset = [entry for entry in dataset["vehicleRequirements"] if set(entry.get("types", [])) & {67, 68, 69, 73, 74}]

    output = [
        "Issue #282 focused maritime source inspection",
        f"Source lines: {source.count(chr(10)) + 1}",
        "\n===== EMBEDDED MARITIME DEFINITIONS =====",
        json.dumps(relevant_definitions, indent=2, sort_keys=True),
        "\n===== DATASET MARITIME DEFINITIONS =====",
        json.dumps(relevant_dataset, indent=2, sort_keys=True),
        "\n===== TRACTIVE CONSTANTS =====",
        extract_statement(source, "const MISSION_REQUIREMENTS_TRACTIVE_TYPES"),
    ]

    for name in (
        "missionRequirementsVehicleId",
        "missionRequirementsVehicleType",
        "missionRequirementsDefinitionCondition",
        "missionRequirementsCollectUnits",
        "missionRequirementsAggregate",
        "missionRequirementsCoverageRow",
        "missionRequirementsOverallState",
        "missionRequirementsPanelHtml",
    ):
        output.extend((f"\n===== {name} =====", extract_function(source, name)))

    output.append("\n===== TRACTIVE / PAIR SOURCE LINES =====")
    for line_no, line in enumerate(source.splitlines(), 1):
        folded = line.casefold()
        if any(token in folded for token in ("tractive", ".pair", "pair:", "contributionkey")):
            if 22100 <= line_no <= 25200:
                output.append(f"{line_no:06d}: {line}")

    REPORT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote focused report: {REPORT.relative_to(ROOT)} ({REPORT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
