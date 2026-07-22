#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue368-authoritative-reconciliation.txt"

source = SOURCE.read_text(encoding="utf-8")
function_names = [
    "missionRequirementsParseSource",
    "missionRequirementsReconcileCatalogue",
    "missionRequirementsResolve",
    "missionRequirementsOverallState",
    "missionRequirementsCoverageRow",
    "missionRequirementsUpdateRecord",
    "missionRequirementsRenderRecord",
    "missionRequirementsSourceForCandidate",
]


def extract_function(name: str) -> str:
    pattern = re.compile(rf"^    (?:async\s+)?function\s+{re.escape(name)}\b", re.MULTILINE)
    match = pattern.search(source)
    if not match:
        return f"// NOT FOUND: {name}\n"
    next_match = re.compile(r"^    (?:async\s+)?function\s+", re.MULTILINE).search(source, match.end())
    end = next_match.start() if next_match else len(source)
    return source[match.start():end].rstrip() + "\n"

sections = []
for name in function_names:
    sections.append(f"\n===== {name} =====\n")
    sections.append(extract_function(name))

# Also capture the exact call sites that combine live parsing, catalogue data,
# aggregation and panel rendering, without exporting the complete userscript.
for token in (
    "missionRequirementsReconcileCatalogue(",
    "missionRequirementsOverallState(",
    "missionRequirementsResolve(",
):
    sections.append(f"\n===== CALL SITES: {token} =====\n")
    for match in re.finditer(re.escape(token), source):
        line_start = source.rfind("\n", 0, match.start()) + 1
        line_end = source.find("\n", match.end())
        if line_end < 0:
            line_end = len(source)
        sections.append(source[line_start:line_end] + "\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(sections), encoding="utf-8")
print(f"Exported Issue #368 reconciliation boundary to {OUTPUT.relative_to(ROOT)}")
