#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "docs" / "issue-133-hardening-inspection.md"

source = SOURCE.read_text(encoding="utf-8")


def extract_balanced(start_token: str, open_char: str, close_char: str) -> str:
    start = source.find(start_token)
    if start < 0:
        raise SystemExit(f"Missing token: {start_token}")
    open_index = source.find(open_char, start + len(start_token))
    if open_index < 0:
        raise SystemExit(f"Missing opening {open_char!r} for {start_token}")
    depth = 0
    quote = None
    escaped = False
    template_depth = 0
    i = open_index
    while i < len(source):
        ch = source[i]
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif quote == "`" and ch == "$" and i + 1 < len(source) and source[i + 1] == "{":
                template_depth += 1
                i += 1
            elif quote == "`" and ch == "}" and template_depth:
                template_depth -= 1
            elif ch == quote and template_depth == 0:
                quote = None
        else:
            if ch in "'\"`":
                quote = ch
            elif ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1
                if depth == 0:
                    end = i + 1
                    while end < len(source) and source[end] in "; \t":
                        end += 1
                    return source[start:end]
        i += 1
    raise SystemExit(f"Unbalanced block: {start_token}")


def line_number(offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def section(title: str, token: str, kind: str = "function") -> str:
    if kind == "const":
        block = extract_balanced(token, "[", "]")
    else:
        block = extract_balanced(token, "{", "}")
    start = source.find(token)
    return f"## {title}\n\nCanonical line {line_number(start)}.\n\n```javascript\n{block}\n```\n"

parts = [
    "# Issue #133 — hardening inspection\n\nGenerated mechanically from the applied v4.15.0 candidate. Inspection only.\n",
    section("Requirement registry", "const MISSION_REQUIREMENT_DEFINITIONS =", "const"),
]

for title, token in [
    ("Normalisation", "function missionRequirementsNormaliseLabel("),
    ("Numeric parsing", "function missionRequirementsNumber("),
    ("Definition lookup", "function missionRequirementsFindDefinition("),
    ("Text parser", "function missionRequirementsParseText("),
    ("DOM requirement parser", "function missionRequirementsParseSource("),
    ("Vehicle type extraction", "function missionRequirementsVehicleTypeId("),
    ("Equipment extraction", "function missionRequirementsEquipment("),
    ("Staff extraction", "function missionRequirementsStaff("),
    ("Unit collection", "function missionRequirementsCollectUnits("),
    ("Unit contribution", "function missionRequirementsUnitContribution("),
    ("Contribution aggregation", "function missionRequirementsAggregate("),
    ("Coverage resolver", "function missionRequirementsResolve("),
    ("Overall state", "function missionRequirementsOverallState("),
    ("LSSM coexistence", "function missionRequirementsLssmActive("),
    ("Panel rendering", "function missionRequirementsPanelHtml("),
    ("Record ownership", "function missionRequirementsEnsureRecord("),
    ("Record teardown", "function missionRequirementsRemoveRecord("),
    ("Window scan", "function scanMissionRequirementsWindows("),
    ("Document observer", "function observeMissionRequirementsDocument("),
    ("Feature installation", "function installMissionRequirementsWindows("),
]:
    parts.append(section(title, token))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(parts), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
