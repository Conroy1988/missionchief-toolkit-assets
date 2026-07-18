#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue-171-record-refresh.txt"
text = SOURCE.read_text(encoding="utf-8")
needles = [
    "function missionRequirementsEnsureRecord",
    "function missionRequirementsRenderRecord",
    "function missionRequirementsScheduleRecord",
    "function missionRequirementsCanonicalPanel",
    "function missionRequirementsRemoveRecord",
]
parts = ["ISSUE #171 RECORD REFRESH INSPECTION\n"]
for needle in needles:
    index = text.find(needle)
    parts.append(f"\n===== {needle} =====\n")
    if index < 0:
        parts.append("NOT FOUND\n")
        continue
    parts.append(text[max(0,index-1200):min(len(text),index+7000)])
    parts.append("\n")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print(OUTPUT.relative_to(ROOT))
