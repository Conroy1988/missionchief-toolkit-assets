#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"

source = SOURCE.read_text(encoding="utf-8")
lines = source.splitlines()

print("ISSUE378_SOURCE_DIAGNOSTIC")
print(f"source_lines={len(lines)}")
print(f"source_sha256={hashlib.sha256(source.encode()).hexdigest()}")

version_match = re.search(r"^// @version\s+([^\s]+)$", source, re.MULTILINE)
script_version_match = re.search(r"\bversion:\s*'([^']+)'", source)
print(f"metadata_version={version_match.group(1) if version_match else 'missing'}")
print(f"script_version={script_version_match.group(1) if script_version_match else 'missing'}")

needles = [
    "// Issue #133 clean-room live mission requirements matrix.",
    "missionRequirements: true",
    "missionRequirements:",
    "Mission Requirements Matrix",
    "function boot(",
    "async function boot(",
    "function createPanel(",
    "function loadState(",
    "function saveState(",
    "runtimeOnCleanup(",
    "clearMissionRequirementsPanels(",
    "installMissionRequirementsFeature(",
    "scanMissionRequirementsWindows(",
    "missionRequirementsFeatureInstalled",
    "state.missionRequirements",
]

for needle in needles:
    matches = [index for index, line in enumerate(lines, start=1) if needle in line]
    print(f"needle={needle!r} count={len(matches)} lines={','.join(map(str, matches[:30]))}")
    for line_number in matches[:8]:
        start = max(1, line_number - 3)
        end = min(len(lines), line_number + 3)
        print(f"--- context {needle!r} line={line_number} range={start}-{end}")
        for current in range(start, end + 1):
            print(f"{current:05d}: {lines[current - 1]}")

# Identify likely settings/control definitions without printing the full source.
patterns = {
    "state-default-lines": re.compile(r"^\s*[A-Za-z_$][\w$]*:\s*(?:true|false|null|\d+|'[^']*'|\"[^\"]*\"),?\s*$"),
    "mission-requirements-labelled-lines": re.compile(r"missionRequirements|Mission Requirements Matrix", re.IGNORECASE),
    "boot-definitions": re.compile(r"^\s*(?:async\s+)?function\s+boot\s*\("),
    "panel-definitions": re.compile(r"^\s*function\s+createPanel\s*\("),
    "cleanup-definitions": re.compile(r"^\s*function\s+(?:destroy|teardown|cleanup)[A-Za-z0-9_$]*\s*\(", re.IGNORECASE),
}

for name, pattern in patterns.items():
    matches = [(index, line) for index, line in enumerate(lines, start=1) if pattern.search(line)]
    print(f"pattern={name} count={len(matches)}")
    for line_number, line in matches[:80]:
        if name == "state-default-lines" and not (350 <= line_number <= 4000):
            continue
        print(f"{line_number:05d}: {line}")

# The diagnostic package must be neutral and must not alter canonical artefacts.
for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    if path.read_text(encoding="utf-8") != source:
        raise RuntimeError(f"canonical parity was already broken before diagnostic: {path}")

print("ISSUE378_SOURCE_DIAGNOSTIC_COMPLETE")
