#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"


def replace_region(text: str, start_token: str, end_token: str, replacement: str, label: str) -> str:
    start = text.find(start_token)
    end = text.find(end_token, start + len(start_token))
    if start < 0 or end < 0 or end <= start:
        raise SystemExit(f"{label}: unable to resolve region start={start} end={end}")
    return text[:start] + replacement.rstrip() + "\n\n    " + text[end:]


source = SOURCE.read_text(encoding="utf-8")

source = replace_region(
    source,
    "function missionRequirementsNumber(",
    "function missionRequirementsCleanRemaining(",
    r'''function missionRequirementsNumber(value) {
        const digits = String(value ?? '').replace(/[^0-9-]/g, '');
        const number = Number.parseInt(digits, 10);
        return Number.isFinite(number) ? Math.max(0, number) : 0;
    }

    function missionRequirementsOptionalNumber(value) {
        const text = String(value ?? '').trim();
        if (!/\d/u.test(text)) return null;
        return missionRequirementsNumber(text);
    }

    function missionRequirementsCapacity(min = 0, max = min, known = null) {
        const safeMin = Math.max(0, Number(min) || 0);
        let safeMax = max === null || max === undefined ? null : Math.max(safeMin, Number(max) || 0);
        if (safeMax !== null && !Number.isFinite(safeMax)) safeMax = null;
        const exact = known === true ? true : known === false ? false : safeMax !== null && safeMin === safeMax;
        return { min: safeMin, max: safeMax, known: exact, value: safeMin };
    }

    function missionRequirementsCapacityText(capacity) {
        const value = missionRequirementsCapacity(capacity?.min ?? capacity?.value ?? 0, capacity?.max, capacity?.known);
        if (value.known || value.max === value.min) return value.min.toLocaleString('en-GB');
        if (value.max === null) return value.min > 0 ? `${value.min.toLocaleString('en-GB')}+` : '?';
        return `${value.min.toLocaleString('en-GB')}–${value.max.toLocaleString('en-GB')}`;
    }

    function missionRequirementsCoverageRow(requirement, selectedCapacity, enRouteCapacity) {
        const missing = Math.max(0, Number(requirement?.missing) || 0);
        const selected = missionRequirementsCapacity(selectedCapacity?.min ?? selectedCapacity?.value ?? 0, selectedCapacity?.max, selectedCapacity?.known);
        const enRoute = missionRequirementsCapacity(enRouteCapacity?.min ?? enRouteCapacity?.value ?? 0, enRouteCapacity?.max, enRouteCapacity?.known);
        const totalMin = selected.min + enRoute.min;
        const totalMax = selected.max === null || enRoute.max === null ? null : selected.max + enRoute.max;
        const covered = totalMin >= missing;
        const definitelyOpen = !covered && totalMax !== null && totalMax < missing;
        const uncertain = !covered && !definitelyOpen;
        const stillMin = enRoute.max === null ? 0 : Math.max(0, missing - enRoute.max);
        const stillMax = Math.max(0, missing - enRoute.min);
        const still = missionRequirementsCapacity(stillMin, stillMax, enRoute.known && stillMin === stillMax);
        const partial = !covered && (selected.min > 0 || enRoute.min > 0 || (selected.max || 0) > 0 || (enRoute.max || 0) > 0);
        return {
            ...requirement,
            selected: selected.min,
            selectedMin: selected.min,
            selectedMax: selected.max,
            selectedKnown: selected.known,
            selectedText: missionRequirementsCapacityText(selected),
            enRoute: enRoute.min,
            enRouteMin: enRoute.min,
            enRouteMax: enRoute.max,
            enRouteKnown: enRoute.known,
            enRouteText: missionRequirementsCapacityText(enRoute),
            stillNeeded: still.max === null ? still.min : still.max,
            stillNeededMin: still.min,
            stillNeededMax: still.max,
            stillNeededKnown: still.known,
            stillNeededText: missionRequirementsCapacityText(still),
            covered,
            definitelyOpen,
            uncertain,
            partial,
            coverageKnown: covered || definitelyOpen
        };
    }''',
    "capacity primitives and pure calculator",
)

source = replace_region(
    source,
    "function missionRequirementsStaffCapacity(",
    "function missionRequirementsCollectUnits(",
    r'''function missionRequirementsStaffCapacity(element) {
        const row = element?.closest?.('tr') || element;
        const crewCell = row?.querySelector?.('[data-personnel-count], [data-current-personnel], [data-min-personnel], [data-max-personnel], [data-min-crew], [data-max-crew], td:nth-of-type(5)[sortvalue]');
        const scopes = Array.from(new Set([element, row, crewCell].filter(Boolean)));
        const exactAttributes = ['data-personnel-count', 'data-current-personnel', 'data-personnel', 'data-staff', 'data-crew'];
        for (const scope of scopes) {
            for (const attribute of exactAttributes) {
                const value = missionRequirementsOptionalNumber(scope.getAttribute?.(attribute));
                if (value !== null) return missionRequirementsCapacity(value, value, true);
            }
        }
        let min = null;
        let max = null;
        for (const scope of scopes) {
            if (min === null) min = missionRequirementsOptionalNumber(scope.getAttribute?.('data-min-personnel') ?? scope.getAttribute?.('data-min-crew'));
            if (max === null) max = missionRequirementsOptionalNumber(scope.getAttribute?.('data-max-personnel') ?? scope.getAttribute?.('data-max-crew'));
        }
        if (min !== null || max !== null) return missionRequirementsCapacity(min ?? 0, max, min !== null && max !== null && min === max);
        const text = String(crewCell?.textContent || '').trim();
        const currentMaximum = text.match(/(\d[\d,.]*)\s*\/\s*(\d[\d,.]*)/u);
        if (currentMaximum) {
            const current = missionRequirementsNumber(currentMaximum[1]);
            return missionRequirementsCapacity(current, current, true);
        }
        const bounded = text.match(/(\d[\d,.]*)\s*(?:-|–|to)\s*(\d[\d,.]*)/iu);
        if (bounded) return missionRequirementsCapacity(missionRequirementsNumber(bounded[1]), missionRequirementsNumber(bounded[2]), false);
        const visible = missionRequirementsOptionalNumber(text);
        if (visible !== null) return missionRequirementsCapacity(visible, visible, true);
        const sortValue = missionRequirementsOptionalNumber(crewCell?.getAttribute?.('sortvalue'));
        if (sortValue !== null) return missionRequirementsCapacity(sortValue, sortValue, true);
        return null;
    }''',
    "bounded personnel capacity extraction",
)

source = replace_region(
    source,
    "function missionRequirementsUnitContribution(",
    "function missionRequirementsAggregate(",
    r'''function missionRequirementsMissionTypeId(candidate) {
        const scopes = [candidate?.root, candidate?.mount].filter(Boolean);
        const attributes = ['mission_type_id', 'data-mission-type-id', 'data-mission_type_id'];
        for (const scope of scopes) {
            for (const attribute of attributes) {
                const value = Number.parseInt(scope.getAttribute?.(attribute), 10);
                if (Number.isFinite(value) && value >= 0) return value;
            }
            const node = scope.querySelector?.('[mission_type_id], [data-mission-type-id], [data-mission_type_id], input[name="mission_type_id"]');
            if (node) {
                for (const raw of [node.getAttribute?.('mission_type_id'), node.getAttribute?.('data-mission-type-id'), node.getAttribute?.('data-mission_type_id'), node.value]) {
                    const value = Number.parseInt(raw, 10);
                    if (Number.isFinite(value) && value >= 0) return value;
                }
            }
        }
        const runtimeValue = Number.parseInt(pageWindow.missionTypeId ?? pageWindow.mission_type_id, 10);
        return Number.isFinite(runtimeValue) && runtimeValue >= 0 ? runtimeValue : null;
    }

    function missionRequirementsDefinitionCondition(definition, candidate) {
        const included = Array.from(definition?.missionTypes || []).map(Number).filter(Number.isFinite);
        const excluded = Array.from(definition?.excludedMissionTypes || []).map(Number).filter(Number.isFinite);
        if (!included.length && !excluded.length) return true;
        const missionTypeId = missionRequirementsMissionTypeId(candidate);
        if (missionTypeId === null) return null;
        if (included.length && !included.includes(missionTypeId)) return false;
        if (excluded.includes(missionTypeId)) return false;
        return true;
    }

    function missionRequirementsUnitContribution(requirement, unit) {
        const definition = requirement.definition || {};
        const typeEligible = Array.from(definition.types || []).includes(unit.typeId);
        const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase()));
        if (!typeEligible && !equipmentEligible) return { eligible: false, capacity: missionRequirementsCapacity(0, 0, true) };
        if (requirement.group === 'staff') {
            const capacity = unit.staff
                ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known)
                : missionRequirementsCapacity(0, null, false);
            return { eligible: true, capacity };
        }
        const factor = Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1);
        const value = Number.isFinite(factor) && factor > 0 ? factor : 1;
        return { eligible: true, capacity: missionRequirementsCapacity(value, value, true) };
    }''',
    "conditional mapping and unit contribution",
)

source = replace_region(
    source,
    "function missionRequirementsAggregate(",
    "function missionRequirementsProgressValue(",
    r'''function missionRequirementsAggregate(requirement, units) {
        const contributions = new Map();
        for (const unit of units) {
            const contribution = missionRequirementsUnitContribution(requirement, unit);
            if (!contribution.eligible) continue;
            const capacity = contribution.capacity;
            const existing = contributions.get(unit.contributionKey);
            if (!existing) {
                contributions.set(unit.contributionKey, capacity);
                continue;
            }
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
        return missionRequirementsCapacity(min, max, exact && max !== null && min === max);
    }''',
    "paired and ranged capacity aggregation",
)

source = replace_region(
    source,
    "function missionRequirementsResolve(",
    "function missionRequirementsOverallState(",
    r'''function missionRequirementsResolve(candidate, parsed) {
        const selectedUnits = missionRequirementsCollectUnits(candidate, 'selected');
        const enRouteUnits = missionRequirementsCollectUnits(candidate, 'enroute');
        return parsed.requirements.map(requirement => {
            const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate);
            if (condition !== true) {
                const unresolvedRow = missionRequirementsCoverageRow(
                    requirement,
                    missionRequirementsCapacity(0, null, false),
                    missionRequirementsCapacity(0, null, false)
                );
                return { ...unresolvedRow, conditionKnown: condition !== null, conditionMatched: false, uncertain: true, definitelyOpen: false, coverageKnown: false };
            }
            let selected;
            let enRoute;
            if (requirement.definition?.bar) {
                const selectedValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'selected');
                const enRouteValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'driving');
                selected = selectedValue === null ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(selectedValue, selectedValue, true);
                enRoute = enRouteValue === null ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(enRouteValue, enRouteValue, true);
            } else {
                selected = missionRequirementsAggregate(requirement, selectedUnits);
                enRoute = missionRequirementsAggregate(requirement, enRouteUnits);
            }
            return { ...missionRequirementsCoverageRow(requirement, selected, enRoute), conditionKnown: true, conditionMatched: true };
        });
    }''',
    "range-aware requirement resolution",
)

source = replace_region(
    source,
    "function missionRequirementsOverallState(",
    "function missionRequirementsLssmActive(",
    r'''function missionRequirementsOverallState(rows, unresolved) {
        if (rows.some(row => row.definitelyOpen)) return 'danger';
        if (rows.some(row => row.uncertain) || unresolved.length) return 'warning';
        return rows.length ? 'success' : 'warning';
    }''',
    "fail-safe overall state",
)

source = replace_region(
    source,
    "function missionRequirementsPanelHtml(",
    "function missionRequirementsRenderRecord(",
    r'''function missionRequirementsPanelHtml(rows, unresolved) {
        const definiteOutstanding = rows.filter(row => row.definitelyOpen).length;
        const uncertain = rows.filter(row => row.uncertain).length + unresolved.length;
        const stateName = missionRequirementsOverallState(rows, unresolved);
        const summary = stateName === 'success'
            ? 'All requirements covered'
            : stateName === 'warning'
                ? `${uncertain} requirement${uncertain === 1 ? '' : 's'} need confirmation`
                : `${definiteOutstanding} requirement${definiteOutstanding === 1 ? '' : 's'} outstanding`;
        const rowHtml = rows.map(row => {
            const rowState = row.covered ? 'covered' : row.uncertain ? 'unresolved' : row.partial ? 'partial' : 'open';
            const prefix = row.covered ? '✓ ' : '';
            return `<tr data-row-state="${rowState}"><td>${escapeHtml(prefix + row.requirement)}</td><td data-label="Missing on mission">${row.missing.toLocaleString('en-GB')}</td><td data-label="En-route">${escapeHtml(row.enRouteText)}</td><td class="mcms-req-still" data-label="Still needed">${escapeHtml(row.stillNeededText)}</td><td data-label="Selected">${escapeHtml(row.selectedText)}</td></tr>`;
        }).join('');
        const unknownHtml = unresolved.length
            ? `<div class="mcms-req-unknown"><b>Unresolved MissionChief requirement</b>${unresolved.map(item => `<span>${escapeHtml(item.text)}</span>`).join('')}</div>`
            : '';
        return {
            stateName,
            html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${escapeHtml(summary)}</span><button type="button" class="mcms-req-collapse" data-mcms-requirements-collapse aria-label="Collapse mission requirements" aria-expanded="true">⌃</button></div><div class="mcms-req-body"><table aria-label="Live mission requirements"><colgroup><col class="mcms-req-name-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"></colgroup><thead><tr><th scope="col">Requirement</th><th scope="col">Missing on mission</th><th scope="col">En-route</th><th scope="col">Still needed</th><th scope="col">Selected</th></tr></thead><tbody>${rowHtml}</tbody></table>${unknownHtml}</div>`
        };
    }''',
    "range-aware panel rendering",
)

SOURCE.write_text(source, encoding="utf-8")
validation = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT)
if validation.returncode != 0:
    raise SystemExit(validation.returncode)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, check=True)
print("Applied Issue #133 range-aware personnel and capacity hardening")
