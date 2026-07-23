#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue378-renderer-integration-map.txt"

source = SOURCE.read_text(encoding="utf-8")


def bounded_excerpt(start_token: str, end_token: str, limit: int = 120000) -> str:
    start = source.find(start_token)
    end = source.find(end_token, start + len(start_token)) if start >= 0 else -1
    if start < 0 or end < 0 or end <= start:
        return f"MISSING EXCERPT: {start_token!r} -> {end_token!r}\n"
    return source[start:min(end, start + limit)]


def line_window(index: int, before: int = 700, after: int = 1500) -> str:
    return source[max(0, index - before):min(len(source), index + after)]

parts: list[str] = [
    "ISSUE378_RENDERER_INTEGRATION_MAP_V1\n",
    f"source_lines={len(source.splitlines())}\n",
    "\n=== OPERATIONAL SUITE SHELL ===\n",
    bounded_excerpt(
        "    // Issue #378 LSSM operational-suite lifecycle shell.",
        "    // Issue #133 clean-room live mission requirements matrix.",
        80000,
    ),
    "\n=== MATRIX SYMBOL INDEX ===\n",
]

symbol_pattern = re.compile(
    r"^\s*(?:const|let|var|function)\s+([A-Za-z_$][\w$]*(?:missionRequirement|MissionRequirement|MISSION_REQUIREMENT)[\w$]*)",
    re.MULTILINE,
)
symbols = sorted(set(symbol_pattern.findall(source)), key=str.lower)
parts.append("\n".join(symbols) + "\n")

search_terms = [
    "const MISSION_REQUIREMENT",
    "function missionRequirement",
    "function findMissionRequirement",
    "function parseMissionRequirement",
    "function missionRequirements",
    "function scheduleMissionRequirementsScan",
    "function installMissionRequirementsWindows",
    "missionRequirementsRecords",
    "vehicle_checkbox:checked",
    "mission_vehicle_driving",
    "data-equipment-types",
    "tractive_vehicle_id",
    "#missing_text",
    "data-requirement-type",
]

for term in search_terms:
    parts.append(f"\n=== TERM: {term} ===\n")
    indexes = [match.start() for match in re.finditer(re.escape(term), source)]
    parts.append(f"matches={len(indexes)}\n")
    for number, index in enumerate(indexes[:12], 1):
        parts.append(f"\n--- match {number} at char {index} ---\n")
        parts.append(line_window(index))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote bounded Issue #378 renderer integration map with {len(symbols)} indexed symbols.")
