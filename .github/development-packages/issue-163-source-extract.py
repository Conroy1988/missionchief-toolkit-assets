#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
FIXTURE = ROOT / ".github" / "fixtures" / "mission-requirements-contract.json"
OUT = ROOT / "docs" / "diagnostics" / "issue-163-source-extract.txt"


def section(text: str, start: str, end: str | None = None, max_chars: int = 18000) -> str:
    begin = text.find(start)
    if begin < 0:
        return f"[MISSING MARKER] {start}\n"
    if end:
        finish = text.find(end, begin + len(start))
        if finish < 0:
            finish = min(len(text), begin + max_chars)
    else:
        finish = min(len(text), begin + max_chars)
    return text[begin:finish]


def function_block(text: str, name: str) -> str:
    marker = f"    function {name}("
    begin = text.find(marker)
    if begin < 0:
        return f"[MISSING FUNCTION] {name}\n"
    next_function = text.find("\n    function ", begin + len(marker))
    finish = next_function if next_function >= 0 else min(len(text), begin + 30000)
    return text[begin:finish]


source = SRC.read_text(encoding="utf-8")
runtime = RUNTIME.read_text(encoding="utf-8")
contract = CONTRACT.read_text(encoding="utf-8")
fixture = FIXTURE.read_text(encoding="utf-8")

parts = [
    "Issue #163 Mission Requirements source extraction\n",
    "\n=== RUNTIME CONSTANTS / DEFINITIONS ===\n",
    section(source, "    // Issue #133 clean-room live mission requirements matrix.", "    function missionRequirementsParseText", 45000),
]

for name in [
    "missionRequirementsParseText",
    "missionRequirementsParseSource",
    "missionRequirementsMissionTypeId",
    "missionRequirementsMissionIdentity",
    "missionRequirementsMissionTitle",
    "missionRequirementsWindowCandidates",
    "missionRequirementsResolve",
    "missionRequirementsPanelHtml",
    "missionRequirementsFallbackHtml",
    "missionRequirementsReportUrl",
    "missionRequirementsEnsureRecord",
    "missionRequirementsRenderRecord",
    "scanMissionRequirementsWindows",
    "observeMissionRequirementsDocument",
    "installMissionRequirementsWindows",
]:
    parts.append(f"\n=== FUNCTION {name} ===\n")
    parts.append(function_block(source, name))

parts.extend([
    "\n=== RUNTIME TEST API EXPOSURE ===\n",
    section(runtime, "this.__mcmsRequirements = {", "for (const testCase of fixture.parserCases)", 12000),
    "\n=== RUNTIME TEST FALLBACK / REPORT CASES ===\n",
    section(runtime, "const missingDoc = new FakeDocument();", "const canonicalDoc = new FakeDocument();", 18000),
    "\n=== CONTRACT TEST ===\n",
    contract,
    "\n=== FIXTURE JSON ===\n",
    fixture,
])

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
