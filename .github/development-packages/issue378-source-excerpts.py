#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue378-source-excerpts.txt"

source = SOURCE.read_text(encoding="utf-8")
lines = source.splitlines()

ranges = [
    (430, 525, "SCRIPT constants"),
    (1280, 1555, "runtime records, default state and state loading"),
    (1780, 1830, "owned-node cleanup"),
    (22970, 23135, "Matrix scan and lifecycle"),
    (28780, 29040, "mission-window toggle handlers"),
    (29680, 30100, "settings panel creation and mission-window controls"),
    (30450, 30675, "updateUI state projection"),
    (31370, 31535, "boot installation sequence"),
    (31535, 31653, "shutdown and final startup"),
]

report = [
    "ISSUE378_TARGETED_SOURCE_EXCERPTS",
    f"source_lines={len(lines)}",
    f"source_sha256={hashlib.sha256(source.encode()).hexdigest()}",
]

for start, end, label in ranges:
    if start < 1 or end > len(lines) or end < start:
        raise RuntimeError(f"invalid excerpt range {start}-{end}: {label}")
    report.append("")
    report.append(f"===== {label} [{start}-{end}] =====")
    for number in range(start, end + 1):
        report.append(f"{number:05d}: {lines[number - 1]}")

for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    if path.read_text(encoding="utf-8") != source:
        raise RuntimeError(f"canonical parity was broken before excerpt capture: {path}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(report) + "\n", encoding="utf-8")
print(f"Persisted {len(ranges)} Issue #378 source excerpts to {OUTPUT.relative_to(ROOT)}")
