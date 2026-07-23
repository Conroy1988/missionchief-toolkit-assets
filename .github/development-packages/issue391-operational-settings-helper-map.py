#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-operational-settings-helper-map.txt"

source = SOURCE.read_text(encoding="utf-8")
lines = source.splitlines()
names = ("defaultOperationalWindowState", "normaliseOperationalWindowState")
report = ["ISSUE391_OPERATIONAL_SETTINGS_HELPER_MAP_V1", f"source_lines={len(lines)}", ""]

for name in names:
    pattern = re.compile(rf"\bfunction\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(source))
    report.append(f"=== {name} matches={len(matches)} ===")
    for match in matches:
        line = source.count("\n", 0, match.start()) + 1
        report.append(f"line={line}")
        start = max(0, line - 30)
        end = min(len(lines), line + 90)
        for index in range(start, end):
            report.append(f"{index + 1:05d}: {lines[index]}")
    report.append("")

for token in ("operationalWindow", "legacyRequirementsEnabled", "matrixRetired"):
    report.append(f"token={token} occurrences={source.count(token)}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(report) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
