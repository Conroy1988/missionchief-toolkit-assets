#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
OUT = ROOT / "docs/issue-285-railway-responding-diagnostic.txt"


def section(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    if begin < 0:
        return f"MISSING START: {start}\n"
    finish = text.find(end, begin + len(start))
    if finish < 0:
        return f"MISSING END AFTER {start}: {end}\n"
    return text[begin:finish]


def around(text: str, token: str, radius: int = 1600) -> str:
    index = text.find(token)
    if index < 0:
        return f"MISSING TOKEN: {token}\n"
    return text[max(0, index - radius):min(len(text), index + len(token) + radius)]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    runtime = RUNTIME.read_text(encoding="utf-8")
    function_names = sorted(set(re.findall(r"function\s+(missionRequirements[A-Za-z0-9_]+)\s*\(", source)))
    unit_functions = [name for name in function_names if any(token in name.casefold() for token in ("unit", "staff", "metadata", "training", "operational"))]
    parts = [
        "# Issue 285 diagnostic\n",
        "## Matching runtime functions\n" + "\n".join(unit_functions) + "\n",
        "## Railway definition\n" + around(source, 'railway-police-officer', 2200),
        "## Metadata and definition matching\n" + section(source, "function missionRequirementsMetadataValues", "function missionRequirementsStaffCapacity"),
        "## Staff capacity and selectors\n" + section(source, "function missionRequirementsStaffCapacity", "function missionRequirementsOperationalWindowScopes"),
        "## Operational scopes through collector\n" + section(source, "function missionRequirementsOperationalWindowScopes", "function missionRequirementsAggregate"),
        "## Aggregation\n" + section(source, "function missionRequirementsAggregate", "function missionRequirementsCoverageRow"),
        "## Current Railway runtime fixtures\n" + around(runtime, "const railwayPoliceDefinition", 5200),
    ]
    OUT.write_text("\n\n".join(parts), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
