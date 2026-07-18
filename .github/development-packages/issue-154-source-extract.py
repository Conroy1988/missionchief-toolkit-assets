#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source_path = root / "src" / "MissionChief_Map_Command_Toolkit.user.js"
out_path = root / "docs" / "diagnostics" / "issue-154-mission-requirements-source.txt"
source = source_path.read_text(encoding="utf-8")
start_marker = "    // Issue #133 clean-room live mission requirements matrix."
end_marker = "    function criticalMissionValueForEntry(entry) {"
start = source.find(start_marker)
end = source.find(end_marker, start)
if start < 0 or end <= start:
    raise SystemExit("Unable to locate Mission Requirements runtime block")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(source[start:end], encoding="utf-8")
print(f"Extracted {end-start} characters to {out_path.relative_to(root)}")
