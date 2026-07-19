#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
s = SOURCE.read_text(encoding="utf-8")

def one(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    s = s.replace(old, new, 1)

def compact_js(value):
    return re.sub(r"\s*\n\s*", " ", value.strip())

def fn(name, next_name, new):
    global s
    start = s.index("    function " + name)
    end = s.index("    function " + next_name, start)
    s = s[:start] + compact_js(new) + "\n\n" + s[end:]

fn('missionRequirementsUnitContribution','missionRequirementsAggregate',r'''    function missionRequirementsUnitContribution(requirement, unit) {
        const definition = requirement.definition || {};
        const typeEligible = Array.from(definition.types || []).includes(unit.typeId);
        const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase()));
        const labelEligible = unit.knownDefinitionKeys?.has?.(definition.key) || missionRequirementsDefinitionMatchesValues(definition, unit.labels);
        const trainingRequired = Array.from(definition.training || []).length > 0;
        const trainingEligible = trainingRequired && missionRequirementsDefinitionMatchesValues(definition, unit.training, 'training');
        const eligible = requirement.group === 'staff' && trainingRequired ? trainingEligible : typeEligible || equipmentEligible || labelEligible;
        const classificationUnknown = requirement.group === 'staff' && trainingRequired
            ? Boolean(unit.staff && !unit.training?.size)
            : unit.typeId < 0 && !unit.knownDefinitionKeys?.size && !unit.equipment?.size;
        if (!eligible) return { eligible: false, unknown: classificationUnknown, capacity: missionRequirementsCapacity(0, classificationUnknown ? null : 0, !classificationUnknown) };
        if (requirement.group === 'staff') {
            const capacity = unit.staff
                ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known)
                : missionRequirementsCapacity(0, null, false);
            return { eligible: true, unknown: !capacity.known, capacity };
        }
        const factor = Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1);
        const value = Number.isFinite(factor) && factor > 0 ? factor : 1;
        return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) };
    }''')

fn('missionRequirementsAggregate','missionRequirementsProgressValue',r'''    function missionRequirementsAggregate(requirement, units) {
        const contributions = new Map();
        let unresolvedClassification = false;
        for (const unit of units) {
            const contribution = missionRequirementsUnitContribution(requirement, unit);
            unresolvedClassification = unresolvedClassification || contribution.unknown === true;
            if (!contribution.eligible) continue;
            const capacity = contribution.capacity;
            const existing = contributions.get(unit.contributionKey);
            if (!existing) { contributions.set(unit.contributionKey, capacity); continue; }
            const pairMin = Math.max(existing.min, capacity.min);
            const pairMax = existing.max === null || capacity.max === null ? null : Math.max(existing.max, capacity.max);
            contributions.set(unit.contributionKey, missionRequirementsCapacity(pairMin, pairMax, existing.known && capacity.known && pairMax === pairMin));
        }
        let min = 0;
        let max = 0;
        let exact = true;
        for (const capacity of contributions.values()) {
            min += capacity.min;
            if (max === null || capacity.max === null) max = null;
            else max += capacity.max;
            exact = exact && capacity.known;
        }
        if (unresolvedClassification) return missionRequirementsCapacity(min, null, false);
        return missionRequirementsCapacity(min, max, exact && max !== null && min === max);
    }''')

SOURCE.write_text(s, encoding="utf-8")
print('Applied v4.20.3 capacity uncertainty source patch')
