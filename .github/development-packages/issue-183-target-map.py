#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue-183-target-map.txt"

text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()
needles = [
    "MISSION_REQUIREMENT_DEFINITIONS",
    "missionRequirementsMissionIdentity",
    "missionRequirementsCandidateRoot",
    "missionRequirementsCatalogueDescriptor",
    "missionRequirementsCatalogueParse",
    "missionRequirementsCatalogueRequest",
    "missionRequirementsCatalogueCompare",
    "missionRequirementsCatalogueBaselineRender",
    "missionRequirementsParseSource",
    "missionRequirementsResolveRequirements",
    "missionRequirementsRender",
    "missionRequirementsRenderRecord",
    "missionRequirementsUpdateRecord",
    "missionRequirementsCreateRecord",
    "missionRequirementsScheduleRecord",
    "missionRequirementsObserveRecord",
    "missionRequirementsObserveDocument",
    "missionRequirementsScanDocument",
    "missionRequirementsCandidate",
    "MISSION_REQUIREMENTS_CATALOGUE",
    "#missing_text",
    "/einsaetze/",
    "data-requirement-type",
]

out: list[str] = []
seen: set[tuple[int, int]] = set()
for needle in needles:
    matches = [index for index, line in enumerate(lines) if needle in line]
    out.append(f"\n===== {needle}: {len(matches)} matches =====\n")
    for index in matches[:20]:
        start = max(0, index - 35)
        end = min(len(lines), index + 145)
        key = (start, end)
        if key in seen:
            continue
        seen.add(key)
        out.append(f"\n--- source lines {start + 1}-{end} ---\n")
        for line_no in range(start, end):
            out.append(f"{line_no + 1:05d}: {lines[line_no]}\n")

for relative in [
    ".github/scripts/test_mission_requirements_runtime.js",
    ".github/scripts/test_mission_requirements_contract.py",
    "docs/issue-181-patient-derived-ambulance-demand-contract.md",
]:
    path = ROOT / relative
    if not path.exists():
        continue
    out.append(f"\n===== FILE {relative} =====\n")
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        out.append(f"{line_no:05d}: {line}\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(out), encoding="utf-8")
print(OUTPUT.relative_to(ROOT))
