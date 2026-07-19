#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source_path = root / "src" / "MissionChief_Map_Command_Toolkit.user.js"
source = source_path.read_text(encoding="utf-8")
start_marker = "function missionRequirementsOperationalSelectors"
end_marker = "function missionRequirementsMissionTypeId"
start = source.index(start_marker)
end = source.index(end_marker, start)
block = source[start:end]
out = root / ".github" / "diagnostics" / "issue-212-selected-runtime.txt"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(block, encoding="utf-8")
Path(__file__).unlink()
print(f"Extracted {len(block)} characters for Issue #212")
