#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue353-scheduler-context.txt"

text = SOURCE.read_text(encoding="utf-8")
needle = "missionRequirementsScheduleDocumentRecords"
positions = []
start = 0
while True:
    index = text.find(needle, start)
    if index < 0:
        break
    positions.append(index)
    start = index + len(needle)

if not positions:
    raise RuntimeError("scheduler symbol not found")

chunks = []
for number, index in enumerate(positions, 1):
    left = max(0, index - 2600)
    right = min(len(text), index + 3200)
    chunks.append(f"===== occurrence {number} at offset {index} =====\n{text[left:right]}\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(chunks), encoding="utf-8")
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)
print(f"Exported {len(positions)} scheduler occurrences")
