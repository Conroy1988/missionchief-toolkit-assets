#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue-183-function-map.txt"
text = SOURCE.read_text(encoding="utf-8")


def extract_function(name: str) -> str:
    patterns = [
        re.compile(rf"\bfunction\s+{re.escape(name)}\s*\("),
        re.compile(rf"\b(?:const|let|var)\s+{re.escape(name)}\s*=\s*(?:async\s*)?\("),
    ]
    match = next((m.search(text) for m in patterns if m.search(text)), None)
    if not match:
        return f"[NOT FOUND] {name}\n"
    start = match.start()
    brace = text.find("{", match.end())
    if brace < 0:
        return f"[NO BODY] {name}\n"
    depth = 0
    quote = None
    escaped = False
    template_depth = 0
    i = brace
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif quote == "`" and ch == "$" and nxt == "{":
                template_depth += 1
                depth += 1
                i += 1
            elif ch == quote and not (quote == "`" and template_depth > 0):
                quote = None
            elif quote == "`" and ch == "}" and template_depth > 0:
                template_depth -= 1
                depth -= 1
            i += 1
            continue
        if ch in "'\"`":
            quote = ch
        elif ch == "/" and nxt == "/":
            end = text.find("\n", i + 2)
            i = len(text) if end < 0 else end
            continue
        elif ch == "/" and nxt == "*":
            end = text.find("*/", i + 2)
            i = len(text) if end < 0 else end + 2
            continue
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1] + "\n"
        i += 1
    return f"[UNTERMINATED] {name}\n"

names = [
    "missionRequirementsCatalogueDescriptor",
    "missionRequirementsCatalogueParse",
    "missionRequirementsCatalogueRequest",
    "missionRequirementsCatalogueCompare",
    "missionRequirementsCatalogueBaselineRender",
    "missionRequirementsCatalogueDiagnosticLines",
    "missionRequirementsEnsureCatalogue",
    "missionRequirementsParseSource",
    "missionRequirementsResolveRequirements",
    "missionRequirementsResolveRequirement",
    "missionRequirementsRender",
    "missionRequirementsRenderRecord",
    "missionRequirementsUpdateRecord",
    "missionRequirementsCreateRecord",
    "missionRequirementsScheduleRecord",
    "missionRequirementsObserveRecord",
    "missionRequirementsSourceForCandidate",
    "missionRequirementsCandidateFromSource",
    "missionRequirementsWindowCandidates",
]

out = []
for name in names:
    out.append(f"\n===== {name} =====\n")
    out.append(extract_function(name))

for token in [
    "MISSION_REQUIREMENTS_CATALOGUE_TTL_MS",
    "MISSION_REQUIREMENTS_CATALOGUE_STALE_MS",
    "MISSION_REQUIREMENTS_CATALOGUE_RETRY_MS",
    "missionRequirementsCatalogueCache",
    "catalogueState",
    "catalogueDescriptor",
    "catalogueBaseline",
]:
    out.append(f"\n===== CONTEXT {token} =====\n")
    for match in list(re.finditer(re.escape(token), text))[:20]:
        start = max(0, text.rfind("\n", 0, match.start() - 600))
        end = text.find("\n", match.end() + 900)
        if end < 0:
            end = len(text)
        out.append(text[start:end] + "\n---\n")

runtime = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
if runtime.exists():
    rt = runtime.read_text(encoding="utf-8")
    out.append("\n===== RUNTIME FIXTURE RELEVANT BLOCKS =====\n")
    for token in ["catalogue", "patientAmbulanceDefinition", "missionRequirementsResolveRequirements", "missionRequirementsCatalogueParse"]:
        out.append(f"\n--- {token} ---\n")
        for match in list(re.finditer(re.escape(token), rt, re.I))[:30]:
            start = max(0, rt.rfind("\n", 0, match.start() - 500))
            end = rt.find("\n", match.end() + 850)
            if end < 0:
                end = len(rt)
            out.append(rt[start:end] + "\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(out), encoding="utf-8")
print(OUTPUT.relative_to(ROOT))
