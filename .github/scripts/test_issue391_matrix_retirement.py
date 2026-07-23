#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
source = SOURCE.read_text(encoding="utf-8")

required = [
    "// Issue #378 retained UK operational capability catalogue.",
    "// Issue #391: legacy Mission Requirements Matrix retired; operationalWindow is authoritative.",
    "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([",
    "const MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE =",
    "const MISSION_REQUIREMENTS_TRACTIVE_TYPES =",
    "function operationalRequirementCreateModel(input = {})",
    "function operationalRequirementsRenderContext(context)",
    "function operationalFeatureRenderContext(context)",
    "matrixRetired: true",
    "parsed?.missionRequirements",
    "function criticalMissionValueForEntry",
    "// Issue #153: stable live Toolkit version-status control.",
]
for marker in required:
    if marker not in source:
        raise SystemExit(f"Issue #391 required marker missing: {marker}")

for forbidden in [
    "// Issue #133 clean-room live mission requirements matrix.",
    "MISSION_REQUIREMENT_PARSE_DEFINITIONS",
    "function missionRequirementsParseText(",
    "function missionRequirementsResolve(",
    "function missionRequirementsEnsureRecord(",
    "function installMissionRequirementsWindows(",
    "function scanMissionRequirementsWindows(",
    "scheduleMissionRequirementsScan(",
    "clearMissionRequirementsPanels(",
    "missionRequirementsPanelId",
    "missionRequirementsDocumentStyleId",
    "data-mcms-requirements-panel",
    "state.missionRequirements",
    "merged.missionRequirements",
    "makeToggleButton('missionRequirements'",
]:
    if forbidden in source:
        raise SystemExit(f"Issue #391 legacy Matrix token survived: {forbidden}")

for name in (
    "MISSION_REQUIREMENT_DEFINITIONS",
    "MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE",
    "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
):
    if source.count(f"const {name} =") != 1:
        raise SystemExit(f"Issue #391 shared catalogue count changed: {name}")
if source.count("parsed?.missionRequirements") != 1:
    raise SystemExit("Issue #391 historical preference migration must occur exactly once")

for obsolete in (
    ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py",
    ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js",
    ROOT / ".github" / "fixtures" / "mission-requirements-contract.json",
    ROOT / ".github" / "diagnostics" / "issue391-matrix-retirement-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-matrix-full-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-matrix-hook-map.txt",
):
    if obsolete.exists():
        raise SystemExit(f"Issue #391 obsolete Matrix artifact remains: {obsolete.relative_to(ROOT)}")

fixture = json.loads((ROOT / ".github" / "fixtures" / "main-style-source-headroom.json").read_text(encoding="utf-8"))
if fixture.get("retiredNonStyleSourceLines") != 1398:
    raise SystemExit("Issue #391 retirement source ledger changed")
if fixture.get("expectedSourceLines") != len(source.splitlines()):
    raise SystemExit("Issue #391 retired source line count is inconsistent")

uk = json.loads((ROOT / "src" / "data" / "mission-requirements-en_GB.json").read_text(encoding="utf-8"))
if uk.get("locale") != "en_GB" or len(uk.get("vehicleRequirements", [])) < 68:
    raise SystemExit("Issue #391 retained UK capability dataset is incomplete")

print("Issue #391 legacy Mission Requirements Matrix retirement contract passed.")
