#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-operational-suite-tail-map.txt"

lines = SOURCE.read_text(encoding="utf-8").splitlines()
lower = 22820
upper = 23250
output = ["ISSUE391_OPERATIONAL_SUITE_TAIL_MAP_V1", f"range={lower}-{upper}"]
for number in range(lower, min(upper, len(lines)) + 1):
    output.append(f"{number:05d}: {lines[number - 1]}")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
print(f"Mapped operational suite tail {lower}-{upper}.")
