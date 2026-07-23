#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / ".github" / "diagnostics" / "issue454-state-region.txt"
lines = SOURCE.read_text(encoding="utf-8").splitlines()
start = 1260
end = 1405
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    "\n".join(f"{index + 1:05d}: {line}" for index, line in enumerate(lines[start - 1:end], start=start - 1)) + "\n",
    encoding="utf-8",
)
print(f"Extracted source lines {start}-{end} for Issue #454.")
