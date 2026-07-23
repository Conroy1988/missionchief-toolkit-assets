#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / ".github" / "diagnostics" / "issue456-operational-requirements-block.txt"
text = SOURCE.read_text(encoding="utf-8")
needles = [
    "Operational Requirements",
    "All displayed requirements covered",
    "No active missing requirements reported",
    "data-mcms-operational-suite",
    "mcms-operational-suite-panel",
    "operationalRequirementCreateModel",
    "operationalRequirementRows",
    "operationalSuiteContexts",
    "installOperationalSuiteShell",
]
lines = text.splitlines()
out = []
for needle in needles:
    out.append(f"===== {needle} =====")
    matches = [i for i, line in enumerate(lines) if needle in line]
    if not matches:
        out.append("NOT FOUND")
        continue
    for index in matches:
        start = max(0, index - 80)
        end = min(len(lines), index + 181)
        out.append(f"--- lines {start + 1}-{end} ---")
        out.extend(f"{i + 1:05d}: {lines[i]}" for i in range(start, end))

for start_marker, end_marker in (
    ("    // Issue #378 enhanced requirements pure engine.", "    // Issue #378 end enhanced requirements pure engine."),
    ("    // Issue #378 complete operational feature suite.", "    // Issue #378 end complete operational feature suite."),
):
    start = text.find(start_marker)
    end = text.find(end_marker, start)
    out.append(f"===== BLOCK {start_marker.strip()} =====")
    if start < 0 or end < 0:
        out.append("BLOCK NOT FOUND")
    else:
        block = text[start:end + len(end_marker)]
        block_lines = block.splitlines()
        out.extend(f"{i + 1:05d}: {line}" for i, line in enumerate(block_lines))

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"Wrote {REPORT.relative_to(ROOT)} with {len(out)} diagnostic lines.")
