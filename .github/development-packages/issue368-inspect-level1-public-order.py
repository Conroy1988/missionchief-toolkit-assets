#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
DATA = ROOT / "src" / "data" / "mission-requirements-en_GB.json"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue368-level1-public-order.txt"

source = SOURCE.read_text(encoding="utf-8")
test = TEST.read_text(encoding="utf-8")
data = DATA.read_text(encoding="utf-8")

function_names = [
    "missionRequirementsLinkedTrainingValues",
    "missionRequirementsQualifiedStaffCounts",
    "missionRequirementsDefaultStaffCapacity",
    "missionRequirementsResolvedStaffCapacity",
    "missionRequirementsStaffCapacity",
    "missionRequirementsRespondingCrewCapacity",
    "missionRequirementsOperationalCrewCapacity",
    "missionRequirementsCollectUnits",
    "missionRequirementsAggregate",
]


def extract_function(name: str) -> str:
    pattern = re.compile(rf"^    (?:async\s+)?function\s+{re.escape(name)}\b", re.MULTILINE)
    match = pattern.search(source)
    if not match:
        return f"// NOT FOUND: {name}\n"
    next_match = re.compile(r"^    (?:async\s+)?function\s+", re.MULTILINE).search(source, match.end())
    end = next_match.start() if next_match else len(source)
    return source[match.start():end].rstrip() + "\n"


def contexts(text: str, patterns: list[str], radius: int = 700) -> str:
    out: list[str] = []
    seen: set[tuple[int, int]] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, match.start() - radius)
            end = min(len(text), match.end() + radius)
            key = (start, end)
            if key in seen:
                continue
            seen.add(key)
            out.append(text[start:end])
    return "\n\n---\n\n".join(out) or "// NO MATCHES\n"

sections: list[str] = []
sections.append("===== SOURCE CONTEXT: LEVEL 1 PUBLIC ORDER =====\n")
sections.append(contexts(source, [r"Level 1 Public Order", r"public[-_ ]order[-_ ]level[-_ ]1", r"level[-_ ]1[-_ ]public[-_ ]order"], 1100))

for name in function_names:
    sections.append(f"\n\n===== FUNCTION: {name} =====\n")
    sections.append(extract_function(name))

sections.append("\n\n===== TEST CONTEXT: PUBLIC ORDER =====\n")
sections.append(contexts(test, [r"Level 1 Public Order", r"Level 2 Public Order", r"public[-_ ]order"], 900))

sections.append("\n\n===== DATA CONTEXT: PUBLIC ORDER =====\n")
sections.append(contexts(data, [r"Level 1 Public Order", r"Level 2 Public Order", r"public[-_ ]order"], 700))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(sections), encoding="utf-8")
print(f"Exported Issue #368 Level 1 public-order boundary to {OUTPUT.relative_to(ROOT)}")
