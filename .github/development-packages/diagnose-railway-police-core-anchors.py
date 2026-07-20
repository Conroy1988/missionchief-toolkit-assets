#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
checks = {
    "metadata version": "// @version      4.20.9",
    "runtime version": "version: '4.20.9',",
    "guide version": "guideVersion: '4.20.9',",
    "railway definition": '"training":["Railway Police Officer","Railway Police"]',
    "training attributes": "const attributes = kind === 'training' ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name'] :",
    "known definition keys": "function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }",
    "resolve marker": "function missionRequirementsResolve(candidate, parsed, catalogue = null)",
    "old inference": "if (baseline !== null && hasStatedRequirement) { const inferredOnSite = Math.max(0, baseline - Math.max(0, Number(requirement.missing) || 0)); if (inferredOnSite > onSite.min) { const inferredMax = onSite.max === null ? null : Math.max(onSite.max, inferredOnSite); onSite = missionRequirementsCapacity(inferredOnSite, inferredMax, onSite.known && inferredMax === inferredOnSite); } }",
}
failed = {name: source.count(value) for name, value in checks.items() if source.count(value) != 1}
if failed:
    raise AssertionError(f"core anchor mismatch: {failed}")
print("Railway Police core source anchors passed")
