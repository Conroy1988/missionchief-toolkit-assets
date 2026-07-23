#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / ".github" / "diagnostics" / "issue456-context-registry.txt"
lines = SOURCE.read_text(encoding="utf-8").splitlines()
needles = [
    "operationalSuiteContexts",
    "function installOperationalSuiteShell",
    "function operationalSuite",
    "operationalRequirementsBindContext",
    "operationalRequirementsScheduleContext",
    "context.panel",
    "data-mcms-operational-suite",
]
out = []
seen = set()
for needle in needles:
    out.append(f"===== {needle} =====")
    matches = [i for i, line in enumerate(lines) if needle in line]
    if not matches:
        out.append("NOT FOUND")
        continue
    for index in matches:
        start = max(0, index - 160)
        end = min(len(lines), index + 241)
        key = (start, end)
        if key in seen:
            out.append(f"DUPLICATE RANGE {start + 1}-{end} OMITTED")
            continue
        seen.add(key)
        out.append(f"--- lines {start + 1}-{end} ---")
        out.extend(f"{i + 1:05d}: {lines[i]}" for i in range(start, end))
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"Wrote {REPORT.relative_to(ROOT)}")
