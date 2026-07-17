#!/usr/bin/env python3
from pathlib import Path

source_path = Path("src/MissionChief_Map_Command_Toolkit.user.js")
report_path = Path(".github/audits/issue-70-financial-renderer-context.md")
text = source_path.read_text(encoding="utf-8")
lines = text.splitlines()
needles = [
    "Checkpoint variance",
    "Operating Snapshot",
    "checkpointVariance",
    "checkpoint variance",
]

matches: list[tuple[int, str]] = []
seen: set[int] = set()
for index, line in enumerate(lines, start=1):
    lowered = line.lower()
    if any(needle.lower() in lowered for needle in needles):
        if index not in seen:
            seen.add(index)
            matches.append((index, line.strip()))

if not matches:
    raise RuntimeError("Unable to locate the Financial Command Operating Snapshot renderer")

sections = [
    "# Issue #70 Financial Command renderer inspection",
    "",
    f"Canonical source: `{source_path}`",
    f"Source lines: **{len(lines)}**",
    f"Matched locations: **{len(matches)}**",
    "",
]

for number, summary in matches:
    start = max(1, number - 90)
    end = min(len(lines), number + 120)
    sections.extend([
        f"## Match at line {number}",
        "",
        f"Matched source: `{summary}`",
        "",
        "```javascript",
    ])
    for line_number in range(start, end + 1):
        sections.append(f"{line_number:05d}: {lines[line_number - 1]}")
    sections.extend(["```", ""])

report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text("\n".join(sections), encoding="utf-8")
print(f"Wrote {report_path} with {len(matches)} matched renderer locations")
