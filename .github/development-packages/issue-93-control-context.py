#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source_path = root / "src" / "MissionChief_Map_Command_Toolkit.user.js"
out_path = root / ".github" / "diagnostics" / "issue-93-control-context.txt"
lines = source_path.read_text(encoding="utf-8").splitlines()
ranges = [(1330, 1520), (16440, 16630), (26940, 27030), (27500, 27980), (28290, 28480)]
parts = []
for start, end in ranges:
    parts.append(f"### {start}-{end}")
    for number in range(start, min(end, len(lines)) + 1):
        parts.append(f"{number:6d}: {lines[number - 1]}")
    parts.append("")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text("\n".join(parts), encoding="utf-8")
