#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-matrix-hook-map.txt"
source = SOURCE.read_text(encoding="utf-8")
start = source.index("    // Issue #133 clean-room live mission requirements matrix.")
end = source.index("    function criticalMissionValueForEntry", start)

terms = [
    "missionRequirements: true",
    "missionRequirements:",
    "merged.missionRequirements",
    "state.missionRequirements",
    "missionRequirementsPanelId",
    "missionRequirementsDocumentStyleId",
    "missionRequirementsRecords",
    "scheduleMissionRequirementsScan(",
    "installMissionRequirementsWindows(",
    "clearMissionRequirementsPanels(",
    "data-toggle=\"missionRequirements\"",
    "makeToggleButton('missionRequirements'",
]
parts = [
    "ISSUE391_MATRIX_HOOK_MAP_V1\n",
    f"removal_start_line={source.count(chr(10), 0, start) + 1}\n",
    f"removal_end_line={source.count(chr(10), 0, end) + 1}\n",
    f"removal_lines={len(source[start:end].splitlines())}\n",
]
for term in terms:
    parts.append(f"\n=== {term!r} ===\n")
    for number, match in enumerate(re.finditer(re.escape(term), source), 1):
        index = match.start()
        zone = "inside-removal" if start <= index < end else "outside-removal"
        line = source.count("\n", 0, index) + 1
        parts.append(f"\nmatch={number} line={line} zone={zone}\n")
        if zone == "outside-removal":
            parts.append(source[max(0, index - 900):min(len(source), index + 1900)])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print("Wrote Issue #391 Matrix hook map.")
