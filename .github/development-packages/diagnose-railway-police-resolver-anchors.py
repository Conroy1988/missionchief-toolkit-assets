#!/usr/bin/env python3
from pathlib import Path
source = (Path(__file__).resolve().parents[2] / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
for value in [
    "function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }",
    "function missionRequirementsResolve(candidate, parsed, catalogue = null)",
    "if (baseline !== null && hasStatedRequirement) { const inferredOnSite = Math.max(0, baseline - Math.max(0, Number(requirement.missing) || 0)); if (inferredOnSite > onSite.min) { const inferredMax = onSite.max === null ? null : Math.max(onSite.max, inferredOnSite); onSite = missionRequirementsCapacity(inferredOnSite, inferredMax, onSite.known && inferredMax === inferredOnSite); } }",
]:
    assert source.count(value) == 1
print("Railway Police resolver anchors passed")
