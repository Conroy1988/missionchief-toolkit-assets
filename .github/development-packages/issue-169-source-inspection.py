#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "docs" / "diagnostics" / "issue-169-mission-requirements-source.txt"

text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()
function_pattern = re.compile(r"^    function (missionRequirements[A-Za-z0-9_]*)\s*\(")
starts: list[tuple[int, str]] = []
for index, line in enumerate(lines):
    match = function_pattern.match(line)
    if match:
        starts.append((index, match.group(1)))

keywords = (
    "candidate", "mount", "source", "catalogue", "missionid", "mission id",
    "mutationobserver", "queryselector", "lightbox", "missions/", "panel",
    "schedule", "refresh", "observer", "document", "location", "root"
)

sections: list[str] = []
sections.append("ISSUE #169 MISSION REQUIREMENTS SOURCE INSPECTION\n")
sections.append(f"Source lines: {len(lines)}\n")
sections.append("FUNCTION INDEX\n")
for start, name in starts:
    sections.append(f"{start + 1}: {name}\n")

sections.append("\nTARGETED FUNCTION BLOCKS\n")
for position, (start, name) in enumerate(starts):
    end = starts[position + 1][0] if position + 1 < len(starts) else min(len(lines), start + 600)
    body = "\n".join(lines[start:end])
    lowered = body.lower()
    if not any(keyword in lowered for keyword in keywords):
        continue
    numbered = "\n".join(f"{line_number + 1:05d}: {lines[line_number]}" for line_number in range(start, end))
    sections.append(f"\n--- {name} ({start + 1}-{end}) ---\n{numbered}\n")

sections.append("\nNON-FUNCTION REFERENCES\n")
for index, line in enumerate(lines):
    lowered = line.lower()
    if "missionrequirements" not in lowered:
        continue
    if function_pattern.match(line):
        continue
    if any(keyword in lowered for keyword in ("observer", "schedule", "refresh", "render", "panel", "candidate", "catalogue", "lightbox")):
        start = max(0, index - 2)
        end = min(len(lines), index + 3)
        numbered = "\n".join(f"{line_number + 1:05d}: {lines[line_number]}" for line_number in range(start, end))
        sections.append(f"\n--- reference near line {index + 1} ---\n{numbered}\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(sections), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(starts)} indexed functions")
