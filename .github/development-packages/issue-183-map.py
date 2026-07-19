#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue-183-source-map.txt"

text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()
patterns = [
    r"Requirements for this Mission",
    r"requirements for this mission",
    r"missionRequirements",
    r"mission_requirement",
    r"mission-requirement",
    r"missionType",
    r"mission_type",
    r"/einsaetze/",
    r"/missions/",
    r"missing_text",
    r"personnel",
    r"education",
    r"training",
    r"patient_button",
    r"fetch\(",
    r"GM_xmlhttpRequest",
]
compiled = [(pattern, re.compile(pattern, re.I)) for pattern in patterns]

sections: list[str] = []
seen: set[tuple[int, int]] = set()
for pattern, regex in compiled:
    matches = [index for index, line in enumerate(lines) if regex.search(line)]
    sections.append(f"\n===== PATTERN {pattern!r}: {len(matches)} MATCHES =====\n")
    for index in matches[:80]:
        start = max(0, index - 10)
        end = min(len(lines), index + 16)
        key = (start, end)
        if key in seen:
            continue
        seen.add(key)
        sections.append(f"\n--- lines {start + 1}-{end} ---\n")
        for line_no in range(start, end):
            sections.append(f"{line_no + 1:05d}: {lines[line_no]}\n")

for path in sorted((ROOT / ".github" / "scripts").glob("*mission*requirements*")):
    sections.append(f"\n===== FILE {path.relative_to(ROOT)} =====\n")
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for index, line in enumerate(content[:1200], start=1):
        sections.append(f"{index:05d}: {line}\n")

for path in sorted((ROOT / ".github" / "fixtures").glob("*mission*requirements*")):
    sections.append(f"\n===== FILE {path.relative_to(ROOT)} =====\n")
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for index, line in enumerate(content[:1200], start=1):
        sections.append(f"{index:05d}: {line}\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(sections), encoding="utf-8")
print(OUTPUT.relative_to(ROOT))
