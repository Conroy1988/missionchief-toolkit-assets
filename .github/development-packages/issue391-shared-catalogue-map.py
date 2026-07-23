#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-shared-catalogue-map.txt"

source = SOURCE.read_text(encoding="utf-8")
lines = source.splitlines()
names = (
    "MISSION_REQUIREMENT_DEFINITIONS",
    "MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE",
    "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
)

report = ["ISSUE391_SHARED_CATALOGUE_MAP_V1", f"source_lines={len(lines)}", ""]
for name in names:
    report.append(f"=== {name} ===")
    pattern = re.compile(rf"^\s*const\s+{re.escape(name)}\s*=", re.MULTILINE)
    matches = list(pattern.finditer(source))
    report.append(f"declaration_matches={len(matches)}")
    literal = f"    const {name} ="
    report.append(f"literal_token_matches={source.count(literal)}")
    for index, match in enumerate(matches, 1):
        line_number = source.count("\n", 0, match.start()) + 1
        report.append(f"match={index} line={line_number}")
        start = max(0, line_number - 4)
        end = min(len(lines), line_number + 4)
        for cursor in range(start, end):
            report.append(f"{cursor + 1:05d}: {lines[cursor]}")
    report.append("")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(report) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
