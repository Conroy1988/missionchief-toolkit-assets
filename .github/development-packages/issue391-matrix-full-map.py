#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-matrix-full-map.txt"
source = SOURCE.read_text(encoding="utf-8")
start_marker = "    // Issue #133 clean-room live mission requirements matrix."
end_marker = "    // Issue #153: stable live Toolkit version-status control."
start = source.index(start_marker)
end = source.index(end_marker, start)
block = source[start:end]
start_line = source.count("\n", 0, start) + 1
end_line = source.count("\n", 0, end) + 1

symbol_re = re.compile(r"^    (?:(const|let|var)|function)\s+([A-Za-z_$][\w$]*)", re.MULTILINE)
symbols = []
for match in symbol_re.finditer(block):
    kind = match.group(1) or "function"
    name = match.group(2)
    absolute = start + match.start()
    line = source.count("\n", 0, absolute) + 1
    symbols.append((line, kind, name))

outside = source[:start] + source[end:]
parts = [
    "ISSUE391_MATRIX_FULL_MAP_V1\n",
    f"source_lines={len(source.splitlines())}\n",
    f"matrix_start_line={start_line}\n",
    f"matrix_end_line={end_line}\n",
    f"matrix_total_lines={len(block.splitlines())}\n",
    f"matrix_total_chars={len(block)}\n",
    f"top_level_symbols={len(symbols)}\n",
    "\n=== INTERNAL ISSUE MARKERS ===\n",
]
for match in re.finditer(r"^    // Issue #[^\n]*$", block, re.MULTILINE):
    line = source.count("\n", 0, start + match.start()) + 1
    parts.append(f"line={line} {match.group(0)}\n")

parts.append("\n=== TOP-LEVEL SYMBOL OWNERSHIP ===\n")
for line, kind, name in symbols:
    inside_count = len(re.findall(rf"\b{re.escape(name)}\b", block))
    outside_count = len(re.findall(rf"\b{re.escape(name)}\b", outside))
    parts.append(f"line={line} kind={kind} name={name} inside={inside_count} outside={outside_count}\n")

preserve = [
    "MISSION_REQUIREMENT_DEFINITIONS",
    "MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE",
    "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
]
parts.append("\n=== PRESERVE-CANDIDATE WINDOWS ===\n")
for name in preserve:
    for match in re.finditer(rf"^    (?:const|let|var)\s+{re.escape(name)}\b", block, re.MULTILINE):
        absolute = start + match.start()
        line = source.count("\n", 0, absolute) + 1
        next_symbol = symbol_re.search(source, absolute + 10, end)
        snippet_end = next_symbol.start() if next_symbol else min(end, absolute + 25000)
        parts.append(f"\n--- {name} line={line} chars={snippet_end - absolute} ---\n")
        parts.append(source[absolute:snippet_end])

terms = [
    "missionRequirements:", "state.missionRequirements", "data-toggle=\"missionRequirements\"",
    "data-setting=\"missionRequirements\"", "scanMissionRequirementsWindows",
    "scheduleMissionRequirementsScan", "installMissionRequirementsWindows",
    "clearMissionRequirementsPanels", "missionRequirementsRecords",
    "MISSION_REQUIREMENT_DEFINITIONS", "MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE",
    "MISSION_REQUIREMENTS_TRACTIVE_TYPES", "test_mission_requirements",
]
parts.append("\n=== GLOBAL REFERENCE WINDOWS ===\n")
for term in terms:
    matches = [m.start() for m in re.finditer(re.escape(term), source)]
    parts.append(f"\n--- {term!r} matches={len(matches)} ---\n")
    for number, index in enumerate(matches[:30], 1):
        line = source.count("\n", 0, index) + 1
        zone = "inside" if start <= index < end else "outside"
        parts.append(f"match={number} line={line} zone={zone}\n")
        if zone == "outside":
            parts.append(source[max(0, index - 650):min(len(source), index + 1600)])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote full Issue #391 Matrix map for {len(block.splitlines())} lines and {len(symbols)} top-level symbols.")
