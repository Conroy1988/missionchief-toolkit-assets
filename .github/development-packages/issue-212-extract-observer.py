#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source = (root / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
start = source.index("function observeMissionRequirementsDocument")
end = source.index("function installMissionRequirementsWindows", start)
out = root / ".github" / "diagnostics" / "issue-212-observer-runtime.txt"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(source[start:end], encoding="utf-8")
Path(__file__).unlink()
print(f"Extracted observer runtime: {end-start} characters")
