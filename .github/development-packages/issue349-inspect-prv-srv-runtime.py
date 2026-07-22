#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue349-mission-requirements-runtime.js"

source = SOURCE.read_text(encoding="utf-8")
start_marker = "    // Issue #133 clean-room live mission requirements matrix."
end_marker = "    function criticalMissionValueForEntry(entry) {"
start = source.find(start_marker)
end = source.find(end_marker, start)
if start < 0 or end <= start:
    raise RuntimeError("Unable to locate the current Mission Requirements runtime block")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(source[start:end], encoding="utf-8")
print(f"Exported {end - start} characters to {OUTPUT.relative_to(ROOT)}")
