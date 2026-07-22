#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github" / "development-packages" / "ios-safari-usability.py"
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"

if not ORIGINAL.exists():
    raise SystemExit("Reviewed iOS/Safari package is missing")

runpy.run_path(str(ORIGINAL), run_name="__main__")
source = SOURCE.read_text(encoding="utf-8")
for distribution in (
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    distribution.write_text(source, encoding="utf-8")

ORIGINAL.unlink(missing_ok=True)
print("Synchronized iOS/Safari candidate source and distribution before canonical validation")
