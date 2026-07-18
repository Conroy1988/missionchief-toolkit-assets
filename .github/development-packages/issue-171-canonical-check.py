#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / "src/MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
needle = "function missionRequirementsCanonicalPanel"
index = text.find(needle)
output = text[max(0,index-500):min(len(text),index+4000)] if index >= 0 else "NOT FOUND"
path = ROOT / ".github/diagnostics/issue-171-canonical-panel.txt"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(output, encoding="utf-8")
print(path.relative_to(ROOT))
