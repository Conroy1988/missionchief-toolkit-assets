#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue391-matrix-retirement-map.txt"
source = SOURCE.read_text(encoding="utf-8")
start_marker = "    // Issue #133 clean-room live mission requirements matrix."
start = source.index(start_marker)
line_start = source.count("\n", 0, start) + 1

issue_markers = []
for match in re.finditer(r"^    // Issue #(\d+)[^\n]*$", source[start + len(start_marker):], re.MULTILINE):
    absolute = start + len(start_marker) + match.start()
    issue_markers.append((absolute, source.count("\n", 0, absolute) + 1, match.group(0)))
    if len(issue_markers) >= 20:
        break

candidate_end = issue_markers[0][0] if issue_markers else len(source)
block = source[start:candidate_end]
block_lines = block.splitlines()

symbol_pattern = re.compile(r"^    (?:const|let|var|function)\s+([A-Za-z_$][\w$]*)", re.MULTILINE)
symbols = sorted(set(symbol_pattern.findall(block)), key=str.lower)

parts = [
    "ISSUE391_MATRIX_RETIREMENT_MAP_V1\n",
    f"source_lines={len(source.splitlines())}\n",
    f"matrix_start_line={line_start}\n",
    f"candidate_end_line={source.count(chr(10), 0, candidate_end) + 1}\n",
    f"candidate_block_lines={len(block_lines)}\n",
    f"candidate_block_chars={len(block)}\n",
    "\n=== NEXT ISSUE MARKERS ===\n",
]
for absolute, line, text in issue_markers:
    parts.append(f"line={line} char={absolute} marker={text}\n")

parts.extend(["\n=== MATRIX TOP-LEVEL SYMBOLS ===\n", "\n".join(symbols), "\n"])
parts.append("\n=== SYMBOL REFERENCE COUNTS ===\n")
for symbol in symbols:
    inside = len(re.findall(rf"\b{re.escape(symbol)}\b", block))
    outside_text = source[:start] + source[candidate_end:]
    outside = len(re.findall(rf"\b{re.escape(symbol)}\b", outside_text))
    parts.append(f"{symbol}: inside={inside} outside={outside}\n")

parts.append("\n=== MATRIX BLOCK FIRST 900 LINES ===\n")
parts.append("\n".join(block_lines[:900]))
parts.append("\n\n=== MATRIX BLOCK LAST 500 LINES ===\n")
parts.append("\n".join(block_lines[-500:]))

terms = [
    "missionRequirements:", "state.missionRequirements", "data-toggle=\"missionRequirements\"",
    "data-mcms-requirements", "scanMissionRequirementsWindows", "scheduleMissionRequirementsScan",
    "installMissionRequirementsWindows", "clearMissionRequirementsPanels", "MISSION_REQUIREMENT_DEFINITIONS",
    "MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE", "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
]
parts.append("\n\n=== GLOBAL TERM WINDOWS ===\n")
for term in terms:
    matches = [m.start() for m in re.finditer(re.escape(term), source)]
    parts.append(f"\n--- {term!r} matches={len(matches)} ---\n")
    for number, index in enumerate(matches[:20], 1):
        line = source.count("\n", 0, index) + 1
        parts.append(f"\nmatch={number} line={line} char={index}\n")
        parts.append(source[max(0, index - 500):min(len(source), index + 1300)])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote Issue #391 Matrix retirement map for {len(block_lines)} candidate lines and {len(symbols)} symbols.")
