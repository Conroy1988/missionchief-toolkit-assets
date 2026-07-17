#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "reports" / "issue-127-transport-sweep-flow.md"
source = SOURCE.read_text(encoding="utf-8")


def segment(start_marker: str, end_marker: str, label: str) -> str:
    start = source.find(start_marker)
    if start < 0:
        return f"## {label}\n\n_NOT FOUND: {start_marker}_\n"
    end = source.find(end_marker, start + len(start_marker))
    if end < 0:
        return f"## {label}\n\n_END NOT FOUND: {end_marker}_\n"
    start_line = source.count("\n", 0, start) + 1
    return f"## {label} — line {start_line}\n\n```javascript\n{source[start:end]}\n```\n"

sections = [
    segment("async function processTransportSweepMission(item, remainingAllowance) {", "\n    async function startTransportSweep", "processTransportSweepMission"),
    segment("async function startTransportSweep", "\n    function stopTransportSweep", "startTransportSweep"),
    segment("function stopTransportSweep", "\n    function ", "stopTransportSweep"),
]

for marker, label in [
    ("function transportSweepLog(", "transportSweepLog"),
    ("function transportSweepReleaseConfirmationVisible(", "transportSweepReleaseConfirmationVisible"),
    ("function renderTransportSweepPanel(", "renderTransportSweepPanel"),
]:
    start = source.find(marker)
    if start >= 0:
        next_function = source.find("\n    function ", start + len(marker))
        next_async = source.find("\n    async function ", start + len(marker))
        candidates = [value for value in (next_function, next_async) if value > start]
        end = min(candidates) if candidates else min(len(source), start + 8000)
        line = source.count("\n", 0, start) + 1
        sections.append(f"## {label} — line {line}\n\n```javascript\n{source[start:end]}\n```\n")

css_marker = ".mcms-sweep-card"
css_start = source.find(css_marker)
if css_start >= 0:
    block_start = max(0, source.rfind("\n", 0, max(0, css_start - 2500)))
    block_end = min(len(source), css_start + 9000)
    sections.append(f"## Existing sweep CSS context — line {source.count(chr(10), 0, block_start) + 1}\n\n```css\n{source[block_start:block_end]}\n```\n")

updates = []
for number, line in enumerate(source.splitlines(), 1):
    if "transportSweepRuntime." in line and any(token in line for token in ("cleared", "skipped", "errors", "processed", "running", "stopRequested", "currentMissionId", "currentVehicleHref")):
        updates.append(f"{number:05d}: {line}")
sections.append("## Runtime state updates\n\n```text\n" + "\n".join(updates) + "\n```\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("# Issue #127 exact Transport Sweep flow\n\n" + "\n".join(sections), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
