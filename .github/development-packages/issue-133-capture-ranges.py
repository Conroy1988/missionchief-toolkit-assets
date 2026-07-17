#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs" / "issue-133-source-ranges.md"

lines = SOURCE.read_text(encoding="utf-8").splitlines()

ranges = [
    (560, 820, "Runtime ownership, observers and cleanup"),
    (1180, 1540, "Global state and feature lifecycle variables"),
    (3800, 4380, "Mission-window and Mission Value CSS vicinity"),
    (16350, 17580, "Transport Sweep mission-window discovery and lifecycle patterns"),
    (21000, 21920, "Mission Value mission-window discovery, rendering and observation"),
    (27800, 29240, "Control events, createPanel markup, Ops controls and updateUI"),
    (29180, 29520, "Main mutation observer and mission-data mutation routing"),
    (29740, 29840, "Boot installation sequence")
]

report = [
    "# Issue #133 — Selected canonical source ranges",
    "",
    "Generated mechanically to support a small, anchored source transformation.",
    ""
]

for start, end, title in ranges:
    start = max(1, start)
    end = min(len(lines), end)
    report.extend([
        f"## {title}",
        "",
        f"Canonical lines {start}–{end}",
        "",
        "```javascript"
    ])
    for number in range(start, end + 1):
        report.append(f"{number:05d}: {lines[number - 1]}")
    report.extend(["```", ""])

REPORT.write_text("\n".join(report), encoding="utf-8")
print(f"Wrote {REPORT.relative_to(ROOT)}")
