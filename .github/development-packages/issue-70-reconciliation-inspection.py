#!/usr/bin/env python3
from pathlib import Path

source_path = Path("src/MissionChief_Map_Command_Toolkit.user.js")
report_path = Path(".github/audits/issue-70-financial-reconciliation-context.md")
lines = source_path.read_text(encoding="utf-8").splitlines()
needles = ["reconciliationLabel", "reconciliationDifference", "calculateVaultReconciliation("]
matches = []
for index, line in enumerate(lines, start=1):
    if any(needle in line for needle in needles):
        matches.append((index, line.strip()))
if not matches:
    raise RuntimeError("No reconciliation fields found")

out = ["# Issue #70 reconciliation field inspection", "", f"Matches: **{len(matches)}**", ""]
for number, summary in matches:
    start = max(1, number - 45)
    end = min(len(lines), number + 65)
    out.extend([f"## Line {number}", "", f"`{summary}`", "", "```javascript"])
    for line_number in range(start, end + 1):
        out.append(f"{line_number:05d}: {lines[line_number - 1]}")
    out.extend(["```", ""])
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text("\n".join(out), encoding="utf-8")
print(f"Wrote {report_path}")
