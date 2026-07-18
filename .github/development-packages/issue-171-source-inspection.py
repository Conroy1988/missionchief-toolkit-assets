#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue-171-source-inspection.txt"

text = SOURCE.read_text(encoding="utf-8")
needles = [
    "function missionRequirementsCandidateRoot",
    "function missionRequirementsCandidateFromSource",
    "function missionRequirementsPlacement",
    "function missionRequirementsPlacePanel",
    "function missionRequirementsWindowCandidates",
    "function missionRequirementsMissionIdentity",
    "function missionRequirementsSourceForCandidate",
    "function missionRequirementsAnchorForCandidate",
    "function missionRequirementsLooksLikeWindow",
    "function scanMissionRequirementsWindows",
    "function installMissionRequirementsWindows",
    "function missionValueWindowCandidates",
    "function transportSweepDocumentContexts",
]

parts = ["ISSUE #171 SOURCE INSPECTION\n"]
for needle in needles:
    index = text.find(needle)
    if index < 0:
        parts.append(f"\n===== {needle}: NOT FOUND =====\n")
        continue
    line = text.count("\n", 0, index) + 1
    start = max(0, index - 1000)
    end = min(len(text), index + 9000)
    parts.append(f"\n===== {needle} @ line {line} =====\n")
    parts.append(text[start:end])
    parts.append("\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
