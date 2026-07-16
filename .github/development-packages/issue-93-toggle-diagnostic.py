#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = (root / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
marker = "function toggleFeature("
start = source.find(marker)
if start < 0:
    raise SystemExit("toggleFeature not found")
line_start = source.rfind("\n", 0, start) + 1
end = source.find("\n    function ", start + len(marker))
if end < 0:
    end = min(len(source), start + 12000)
out = root / ".github" / "diagnostics" / "issue-93-toggle-function.txt"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(source[line_start:end], encoding="utf-8")
