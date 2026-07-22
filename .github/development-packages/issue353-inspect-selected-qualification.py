#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue353-selected-qualification.txt"

source = SOURCE.read_text(encoding="utf-8")
lines = source.splitlines()

function_names = [
    "missionRequirementsLinkedTrainingValues",
    "missionRequirementsArrCapabilityState",
    "missionRequirementsQualifiedStaffCounts",
    "missionRequirementsVehicleApiRecord",
    "missionRequirementsVehicleApiStaff",
    "missionRequirementsResolvedStaffCapacity",
    "missionRequirementsOperationalSelectors",
    "missionRequirementsOperationalElementActive",
    "missionRequirementsVehicleId",
    "missionRequirementsVehicleType",
    "missionRequirementsCollectUnits",
    "missionRequirementsAggregate",
]


def extract_function(name: str) -> str:
    pattern = re.compile(rf"^\s*(?:async\s+)?function\s+{re.escape(name)}\s*\(", re.MULTILINE)
    match = pattern.search(source)
    if not match:
        return f"[missing function: {name}]\n"
    start = match.start()
    next_match = re.search(r"^\s*(?:async\s+)?function\s+missionRequirements[A-Za-z0-9_]+\s*\(", source[match.end():], re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(source)
    return source[start:end].rstrip() + "\n"

sections: list[str] = [
    "# Issue 353 selected Police Sergeant / recovery diagnostic",
    "",
    "Runtime source is exported verbatim for diagnosis only.",
    "",
]
for name in function_names:
    sections.extend([f"## {name}", "", "```javascript", extract_function(name), "```", ""])

needle_patterns = [
    r"police_sergeant",
    r"qualificationCounts",
    r"arrCapabilities",
    r"vehicle_checkbox",
    r"selectedUnits",
    r"data-current-personnel",
    r"data-vehicle-id",
]
sections.extend(["## Context windows", ""])
seen: set[tuple[int, int]] = set()
for needle in needle_patterns:
    sections.append(f"### {needle}")
    sections.append("")
    for index, line in enumerate(lines):
        if not re.search(needle, line, re.IGNORECASE):
            continue
        start = max(0, index - 5)
        end = min(len(lines), index + 6)
        key = (start, end)
        if key in seen:
            continue
        seen.add(key)
        sections.append(f"Lines {start + 1}-{end}")
        sections.append("```javascript")
        sections.extend(f"{line_number + 1}: {lines[line_number]}" for line_number in range(start, end))
        sections.append("```")
        sections.append("")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(sections), encoding="utf-8")
print(f"Exported Issue 353 diagnostic to {OUTPUT.relative_to(ROOT)}")
