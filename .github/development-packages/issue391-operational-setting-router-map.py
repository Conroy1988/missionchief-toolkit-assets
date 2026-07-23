#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-operational-setting-router-map.txt"

source = SOURCE.read_text(encoding="utf-8")
token = "handleOperationalWindowSettingChange"
positions = []
start = 0
while True:
    position = source.find(token, start)
    if position < 0:
        break
    positions.append(position)
    start = position + len(token)

lines = source.splitlines()
line_numbers = []
for position in positions:
    line_number = source.count("\n", 0, position) + 1
    line_numbers.append(line_number)

output = ["ISSUE391_OPERATIONAL_SETTING_ROUTER_MAP_V1", f"occurrences={len(positions)}", f"lines={line_numbers}"]
for line_number in line_numbers:
    lower = max(1, line_number - 12)
    upper = min(len(lines), line_number + 36)
    output.append(f"\n=== context line {line_number} ===")
    for number in range(lower, upper + 1):
        output.append(f"{number:05d}: {lines[number - 1]}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
print(f"Mapped {len(positions)} operational-setting router occurrence(s).")
