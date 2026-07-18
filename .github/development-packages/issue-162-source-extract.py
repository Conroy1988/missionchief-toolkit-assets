#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUT = ROOT / "docs" / "diagnostics" / "issue-162-report-source.txt"

text = SRC.read_text(encoding="utf-8")
start = text.find("    function missionRequirementsReportUrl(")
if start < 0:
    raise AssertionError("missionRequirementsReportUrl not found")
end = text.find("\n    function ", start + 20)
if end < 0:
    raise AssertionError("next function boundary not found")
block = text[start:end].rstrip()

templates = ROOT / ".github" / "ISSUE_TEMPLATE"
parts = ["Issue #162 source extraction", "", block, "", "Existing issue templates:"]
if templates.exists():
    for path in sorted(templates.iterdir()):
        if path.is_file():
            parts.extend([f"\n--- {path.name} ---", path.read_text(encoding="utf-8", errors="replace")])
else:
    parts.append("(directory absent)")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
print(f"Extracted report URL function to {OUT.relative_to(ROOT)}")
