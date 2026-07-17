#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs" / "issue-133-source-inspection.md"

text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()

anchors = [
    "#missing_text",
    "missing_text",
    "#mission-form",
    "mission-form",
    "#mission_vehicle_driving",
    "mission_vehicle_driving",
    "#vehicle_show_table_body_all",
    "vehicle_show_table_body_all",
    "#vehicle_amount",
    "vehicle_amount",
    "#occupied",
    "tractive_vehicle_id",
    "data-equipment-types",
    "navbar-alarm-spacer",
    "Mission Value",
    "missionValue",
    "runtimeOnCleanup",
    "runtimeTrackObserver",
    "createPanel",
    "function boot(",
    "data-section=\"ops\"",
    "section: 'ops'",
    "Ops"
]


def matching_lines(anchor: str) -> list[int]:
    return [index for index, line in enumerate(lines, start=1) if anchor in line]


def context(start: int, radius: int = 12) -> str:
    first = max(1, start - radius)
    last = min(len(lines), start + radius)
    rendered = []
    for number in range(first, last + 1):
        rendered.append(f"{number:05d}: {lines[number - 1]}")
    return "\n".join(rendered)

report = [
    "# Issue #133 — Canonical userscript source inspection",
    "",
    "Generated mechanically from the canonical userscript before production changes.",
    "",
    f"- Source lines: **{len(lines):,}**",
    f"- Source bytes: **{len(text.encode('utf-8')):,}**",
    "",
    "## Anchor inventory",
    ""
]

for anchor in anchors:
    matches = matching_lines(anchor)
    report.append(f"### `{anchor}`")
    report.append("")
    if not matches:
        report.append("No matches.")
        report.append("")
        continue
    report.append("Matches: " + ", ".join(str(match) for match in matches[:20]))
    if len(matches) > 20:
        report.append(f"Additional matches omitted: {len(matches) - 20}")
    report.append("")
    for match in matches[:5]:
        report.append(f"#### Context around line {match}")
        report.append("")
        report.append("```javascript")
        report.append(context(match))
        report.append("```")
        report.append("")

report.extend([
    "## Function declarations containing mission/window terminology",
    ""
])
for index, line in enumerate(lines, start=1):
    stripped = line.strip()
    if not stripped.startswith("function ") and not stripped.startswith("async function "):
        continue
    lowered = stripped.lower()
    if any(token in lowered for token in ("mission", "lightbox", "vehicle", "panel", "observer", "runtime")):
        report.append(f"- line {index}: `{stripped}`")

report.extend([
    "",
    "## Guardrails",
    "",
    "This report is inspection-only. It does not alter the userscript, distribution, version, settings or runtime behaviour.",
    ""
])

REPORT.write_text("\n".join(report), encoding="utf-8")
print(f"Wrote {REPORT.relative_to(ROOT)}")
