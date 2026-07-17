#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs" / "issue-133-integration-context.md"

lines = SOURCE.read_text(encoding="utf-8").splitlines()
anchors = [
    ("const SCRIPT =", 30, 90),
    ("const UI_THEMES =", 20, 180),
    ("function toggleFeature(", 30, 220),
    ("function handleAction(", 30, 220),
    ("function updateUI(", 30, 240),
    ("function scanMissionValueWindows(", 20, 150),
    ("function observeMissionValueDocument(", 20, 90),
    ("function connectMainMutationObserver(", 20, 180),
    ("function scheduleDeferredOperationalStartup(", 20, 180),
    ("function startBootAttemptCoordinator(", 20, 170),
    ("function boot(", 20, 140),
    (".mcms-mission-value-row {", 30, 120),
    ("<section class=\"mcms-tab-panel\" data-panel=\"ops\">", 10, 110)
]

report = [
    "# Issue #133 — Integration context",
    "",
    "Generated mechanically from the canonical userscript. Inspection only.",
    ""
]

for anchor, before, after in anchors:
    matches = [index for index, line in enumerate(lines) if anchor in line]
    report.extend([f"## `{anchor}`", ""])
    if not matches:
        report.extend(["Not found.", ""])
        continue
    for match_number, index in enumerate(matches[:3], start=1):
        start = max(0, index - before)
        end = min(len(lines), index + after + 1)
        report.extend([f"### Match {match_number} · canonical line {index + 1}", "", "```javascript"])
        for line_number in range(start, end):
            report.append(f"{line_number + 1:05d}: {lines[line_number]}")
        report.extend(["```", ""])

REPORT.write_text("\n".join(report), encoding="utf-8")
print(f"Wrote {REPORT.relative_to(ROOT)}")
