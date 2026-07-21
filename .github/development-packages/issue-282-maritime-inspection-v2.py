#!/usr/bin/env python3
from __future__ import annotations

import json
import re
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


def extract_definition_fragment(source: str, key: str) -> str:
    pattern = re.compile(r'\{"key":"' + re.escape(key) + r'"[^{}]*\}')
    match = pattern.search(source)
    if not match:
        raise RuntimeError(f"missing embedded definition {key}")
    return match.group(0)


def safe(output: list[str], title: str, callback) -> None:
    output.append(f"\n===== {title} =====")
    try:
        output.append(callback())
    except Exception as exc:  # inspection must report limitations, not hide them
        output.append(f"INSPECTION ERROR: {type(exc).__name__}: {exc}")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    relevant_keys = (
        "boat-or-inland", "ilb-or-alb", "ilb", "alb", "4x4",
        "rescue-watercraft", "hovercraft", "medical-trailer", "sar-support",
    )
    relevant_dataset = [entry for entry in dataset["vehicleRequirements"] if set(entry.get("types", [])) & {67, 68, 69, 73, 74}]

    output = [
        "Issue #282 focused maritime source inspection",
        f"Source lines: {source.count(chr(10)) + 1}",
        "\n===== DATASET MARITIME DEFINITIONS =====",
        json.dumps(relevant_dataset, indent=2, sort_keys=True),
    ]

    for key in relevant_keys:
        safe(output, f"embedded definition: {key}", lambda key=key: extract_definition_fragment(source, key))
    safe(output, "tractive constants", lambda: extract_statement(source, "const MISSION_REQUIREMENTS_TRACTIVE_TYPES"))

    for name in (
        "missionRequirementsVehicleId",
        "missionRequirementsVehicleType",
        "missionRequirementsDefinitionCondition",
        "missionRequirementsCollectUnits",
        "missionRequirementsUnitContribution",
        "missionRequirementsAggregate",
        "missionRequirementsCoverageRow",
        "missionRequirementsOverallState",
        "missionRequirementsPanelHtml",
    ):
        safe(output, name, lambda name=name: extract_function(source, name))

    output.append("\n===== TRACTIVE / PAIR SOURCE LINES =====")
    for line_no, line in enumerate(source.splitlines(), 1):
        folded = line.casefold()
        if any(token in folded for token in ("tractive", ".pair", "pair:", "contributionkey")) and 22100 <= line_no <= 25200:
            output.append(f"{line_no:06d}: {line}")

    REPORT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote focused report: {REPORT.relative_to(ROOT)} ({REPORT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
