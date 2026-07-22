#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = (root / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
start_marker = "    function toggleFeature(feature) {"
end_marker = "\n    function runAutoNight("
start = source.index(start_marker)
end = source.index(end_marker, start)
diagnostic = root / ".github" / "diagnostics" / "issue343-toggle-feature.txt"
diagnostic.parent.mkdir(parents=True, exist_ok=True)
diagnostic.write_text(source[start:end] + "\n", encoding="utf-8")
print("Exported current toggleFeature() body for Issue #343")
