#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
FIXTURE = ROOT / ".github" / "fixtures" / "mission-requirements-contract.json"
DIAGNOSTIC = ROOT / "docs" / "diagnostics" / "issue-167-source-extract.txt"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_function(text: str, name: str, replacement: str) -> str:
    marker = f"    function {name}("
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"function {name} missing")
    next_function = text.find("\n    function ", start + len(marker))
    if next_function < 0:
        raise AssertionError(f"next function after {name} missing")
    return text[:start] + replacement.rstrip() + "\n" + text[next_function + 1:]


def insert_before(text: str, marker: str, addition: str, label: str) -> str:
    if addition.strip() in text:
        return text
    return replace_once(text, marker, addition + marker, label)


def run(*cmd: str) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


coverage_function = r'''    function missionRequirementsCoverageRow(requirement, selectedCapacity, respondingCapacity, onSiteCapacity = null, requiredCapacity = null) {
        const missing = Math.max(0, Number(requirement?.missing) || 0);
        const selected = missionRequirementsCapacity(selectedCapacity?.min ?? selectedCapacity?.value ?? 0, selectedCapacity?.max, selectedCapacity?.known);
        const responding = missionRequirementsCapacity(respondingCapacity?.min ?? respondingCapacity?.value ?? 0, respondingCapacity?.max, respondingCapacity?.known);
        const onSite = missionRequirementsCapacity(onSiteCapacity?.min ?? onSiteCapacity?.value ?? 0, onSiteCapacity?.max, onSiteCapacity?.known);
        const derivedRequiredMin = missing + onSite.min;
        const derivedRequiredMax = onSite.max === null ? null : missing + onSite.max;
        const required = requiredCapacity
            ? missionRequirementsCapacity(requiredCapacity?.min ?? requiredCapacity?.value ?? derivedRequiredMin, requiredCapacity?.max, requiredCapacity?.known)
            : missionRequirementsCapacity(derivedRequiredMin, derivedRequiredMax, onSite.known && derivedRequiredMax !== null && derivedRequiredMin === derivedRequiredMax);
        const fulfilledMin = onSite.min + responding.min + selected.min;
        const fulfilledMax = onSite.max === null || responding.max === null || selected.max === null
            ? null
            : onSite.max + responding.max + selected.max;
        const covered = required.max !== null && fulfilledMin >= required.max;
        const definitelyOpen = !covered && fulfilledMax !== null && fulfilledMax < required.min;
        const uncertain = !covered && !definitelyOpen;
        const stillMin = fulfilledMax === null ? 0 : Math.max(0, required.min - fulfilledMax);
        const stillMax = required.max === null ? null : Math.max(0, required.max - fulfilledMin);
        const stillKnown = covered || (stillMax !== null && stillMin === stillMax && required.known && onSite.known && responding.known && selected.known);
        const still = missionRequirementsCapacity(stillMin, stillMax, stillKnown);
        const partial = !covered && fulfilledMin > 0;
        return {
            ...requirement,
            required: required.min,
            requiredMin: required.min,
            requiredMax: required.max,
            requiredKnown: required.known,
            requiredText: missionRequirementsCapacityText(required),
            onSite: onSite.min,
            onSiteMin: onSite.min,
            onSiteMax: onSite.max,
            onSiteKnown: onSite.known,
            onSiteText: missionRequirementsCapacityText(onSite),
            responding: responding.min,
            respondingMin: responding.min,
            respondingMax: responding.max,
            respondingKnown: responding.known,
            respondingText: missionRequirementsCapacityText(responding),
            enRoute: responding.min,
            enRouteMin: responding.min,
            enRouteMax: responding.max,
            enRouteKnown: responding.known,
            enRouteText: missionRequirementsCapacityText(responding),
            selected: selected.min,
            selectedMin: selected.min,
            selectedMax: selected.max,
            selectedKnown: selected.known,
            selectedText: missionRequirementsCapacityText(selected),
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
    }'''

collect_function = r'''    function missionRequirementsCollectUnits(candidate, mode) {
        const root = candidate?.root;
        const doc = candidate?.source?.ownerDocument || root?.ownerDocument;
        if (!root?.querySelectorAll && !doc?.querySelectorAll) return [];
        const selector = mode === 'selected'
            ? '#vehicle_show_table_body_all .vehicle_checkbox:checked, #occupied .vehicle_checkbox:checked, .vehicle_checkbox:checked'
            : mode === 'onsite'
                ? '#mission_vehicle_at_mission tbody tr'
                : '#mission_vehicle_driving tbody tr';
        const elements = [];
        const seenElements = new Set();
        const missionScopes = Array.from(new Set([root, candidate?.mount].filter(scope => scope?.querySelectorAll)));
        const scopes = missionScopes.length ? missionScopes : [doc].filter(scope => scope?.querySelectorAll);
        for (const scope of scopes) {
            for (const element of Array.from(scope.querySelectorAll?.(selector) || [])) {
                if (seenElements.has(element)) continue;
                seenElements.add(element);
                elements.push(element);
            }
        }

        const units = new Map();
        elements.forEach((element, index) => {
            const row = element.matches?.('tr') ? element : element.closest?.('tr');
            const vehicleElement = mode === 'selected'
                ? element
                : (element.querySelector?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id]') || element);
            const typeId = missionRequirementsVehicleType(vehicleElement);
            if (typeId < 0) return;
            const vehicleId = missionRequirementsVehicleId(vehicleElement);
            const tractiveId = missionRequirementsOptionalNumber(
                vehicleElement?.getAttribute?.('tractive_vehicle_id')
                ?? vehicleElement?.getAttribute?.('data-tractive-vehicle-id')
                ?? row?.getAttribute?.('tractive_vehicle_id')
                ?? row?.getAttribute?.('data-tractive-vehicle-id')
                ?? row?.dataset?.tractiveVehicleId
            );
            const trailerId = missionRequirementsOptionalNumber(
                vehicleElement?.getAttribute?.('trailer_id')
                ?? vehicleElement?.getAttribute?.('data-trailer-id')
                ?? row?.getAttribute?.('trailer_id')
                ?? row?.getAttribute?.('data-trailer-id')
                ?? row?.dataset?.trailerId
            );
            let contributionKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : `element:${index}`;
            const pairedId = tractiveId !== null && tractiveId >= 0 ? tractiveId : trailerId;
            if (vehicleId >= 0 && pairedId !== null && pairedId >= 0) contributionKey = `pair:${Math.min(vehicleId, pairedId)}:${Math.max(vehicleId, pairedId)}`;
            const identityKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : contributionKey;
            const unit = {
                typeId,
                vehicleId,
                tractiveId,
                equipment: missionRequirementsEquipmentTypes(vehicleElement),
                staff: missionRequirementsStaffCapacity(vehicleElement),
                contributionKey
            };
            const existing = units.get(identityKey);
            if (!existing) {
                units.set(identityKey, unit);
                return;
            }
            if (existing.typeId < 0 && unit.typeId >= 0) existing.typeId = unit.typeId;
            for (const equipment of unit.equipment) existing.equipment.add(equipment);
            if ((!existing.staff || !existing.staff.known) && unit.staff?.known) existing.staff = unit.staff;
            if (existing.contributionKey.startsWith('element:') && !unit.contributionKey.startsWith('element:')) existing.contributionKey = unit.contributionKey;
        });
        return Array.from(units.values());
    }'''

bucket_helper = r'''
    function missionRequirementsExclusiveUnitBuckets(selectedUnits, respondingUnits, onSiteUnits) {
        const claimed = new Set();
        const keysFor = unit => {
            const keys = [];
            if (unit?.vehicleId >= 0) keys.push(`vehicle:${unit.vehicleId}`);
            if (unit?.contributionKey && !String(unit.contributionKey).startsWith('element:')) keys.push(String(unit.contributionKey));
            return keys;
        };
        const claim = units => Array.from(units || []).filter(unit => {
            const keys = keysFor(unit);
            if (keys.some(key => claimed.has(key))) return false;
            keys.forEach(key => claimed.add(key));
            return true;
        });
        const onSite = claim(onSiteUnits);
        const responding = claim(respondingUnits);
        const selected = claim(selectedUnits);
        return { selected, responding, onSite };
    }

'''

resolve_function = r'''    function missionRequirementsResolve(candidate, parsed, catalogue = null) {
        const rawSelectedUnits = missionRequirementsCollectUnits(candidate, 'selected');
        const rawRespondingUnits = missionRequirementsCollectUnits(candidate, 'responding');
        const rawOnSiteUnits = missionRequirementsCollectUnits(candidate, 'onsite');
        const buckets = missionRequirementsExclusiveUnitBuckets(rawSelectedUnits, rawRespondingUnits, rawOnSiteUnits);
        const catalogueByKey = new Map(Array.from(catalogue?.requirements || []).map(item => [item.key, item]));
        return parsed.requirements.map(requirement => {
            if (requirement.definition?.countable === false) return missionRequirementsUnknownCoverageRow(requirement);
            const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate);
            if (condition !== true) {
                const unknown = missionRequirementsCapacity(0, null, false);
                const unresolvedRow = missionRequirementsCoverageRow(requirement, unknown, unknown, unknown, unknown);
                return { ...unresolvedRow, conditionKnown: condition !== null, conditionMatched: false, uncertain: true, definitelyOpen: false, coverageKnown: false };
            }
            let selected;
            let responding;
            let onSite;
            if (requirement.definition?.bar) {
                const selectedValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'selected');
                const respondingValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'driving');
                const onSiteMetrics = ['at_mission', 'on_site', 'onsite', 'arrived', 'actual'];
                const onSiteValue = onSiteMetrics.map(metric => missionRequirementsProgressValue(candidate, requirement.definition.bar, metric)).find(value => value !== null);
                selected = selectedValue === null ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(selectedValue, selectedValue, true);
                responding = respondingValue === null ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(respondingValue, respondingValue, true);
                onSite = onSiteValue === undefined ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(onSiteValue, onSiteValue, true);
            } else {
                selected = missionRequirementsAggregate(requirement, buckets.selected);
                responding = missionRequirementsAggregate(requirement, buckets.responding);
                onSite = missionRequirementsAggregate(requirement, buckets.onSite);
            }

            const catalogueRequirement = catalogueByKey.get(requirement.key);
            const baseline = missionRequirementsOptionalNumber(catalogueRequirement?.baseline ?? catalogueRequirement?.missing);
            if (baseline !== null) {
                const inferredOnSite = Math.max(0, baseline - Math.max(0, Number(requirement.missing) || 0));
                if (inferredOnSite > onSite.min) {
                    const inferredMax = onSite.max === null ? null : Math.max(onSite.max, inferredOnSite);
                    onSite = missionRequirementsCapacity(inferredOnSite, inferredMax, onSite.known && inferredMax === inferredOnSite);
                }
            }
            const liveRequiredMin = Math.max(0, Number(requirement.missing) || 0) + onSite.min;
            const liveRequiredMax = onSite.max === null ? null : Math.max(0, Number(requirement.missing) || 0) + onSite.max;
            const required = baseline !== null
                ? missionRequirementsCapacity(Math.max(baseline, liveRequiredMin), Math.max(baseline, liveRequiredMin), true)
                : missionRequirementsCapacity(liveRequiredMin, liveRequiredMax, onSite.known && liveRequiredMax !== null && liveRequiredMin === liveRequiredMax);
            return {
                ...missionRequirementsCoverageRow(requirement, selected, responding, onSite, required),
                conditionKnown: true,
                conditionMatched: true,
                requirementAuthority: baseline !== null ? 'catalogue+live' : 'live-reconstructed'
            };
        });
    }'''

css_function = r'''    function missionRequirementsDocumentCss() {
        return `
#${SCRIPT.missionRequirementsPanelId}{--mcms-req-accent:#6fd7ff;--mcms-req-surface:#101820;--mcms-req-surface-2:#17242f;--mcms-req-border:rgba(111,215,255,.38);--mcms-req-text:#eef9ff;--mcms-req-muted:#a9bdc8;display:block!important;position:relative!important;clear:both!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important;margin:0 0 7px!important;border:1px solid var(--mcms-req-border)!important;border-left:4px solid var(--mcms-req-state,#ef5350)!important;border-radius:9px!important;background:linear-gradient(145deg,var(--mcms-req-surface),var(--mcms-req-surface-2))!important;color:var(--mcms-req-text)!important;box-shadow:0 5px 14px rgba(0,0,0,.19)!important;overflow:hidden!important;font-family:Arial,Helvetica,sans-serif!important;z-index:auto!important}
[data-mcms-requirements-source-hidden="1"]{display:none!important}
#${SCRIPT.missionRequirementsPanelId}[data-state="danger"]{--mcms-req-state:#ef5350}
#${SCRIPT.missionRequirementsPanelId}[data-state="warning"]{--mcms-req-state:#ffb74d}
#${SCRIPT.missionRequirementsPanelId}[data-state="success"]{--mcms-req-state:#4dd68a}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="cyberpunk"]{--mcms-req-accent:#00f0ff;--mcms-req-surface:#080b12;--mcms-req-surface-2:#111725;--mcms-req-border:rgba(0,240,255,.50);border-radius:2px!important}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="fallout4"]{--mcms-req-accent:#c8ff8b;--mcms-req-surface:#071008;--mcms-req-surface-2:#172817;--mcms-req-border:rgba(164,234,101,.48);--mcms-req-text:#d8ffad;--mcms-req-muted:#91b978}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="umbrella"]{--mcms-req-accent:#f4f6f8;--mcms-req-surface:#101114;--mcms-req-surface-2:#1c1d21;--mcms-req-border:rgba(214,39,50,.55)}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="factorio"]{--mcms-req-accent:#f0a44a;--mcms-req-surface:#171717;--mcms-req-surface-2:#2a2824;--mcms-req-border:rgba(240,164,74,.48);border-radius:4px!important}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="bond007"]{--mcms-req-accent:#d9bd77;--mcms-req-surface:#090a0c;--mcms-req-surface-2:#17191e;--mcms-req-border:rgba(217,189,119,.45)}
#${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="hyrule"]{--mcms-req-accent:#6ee6d6;--mcms-req-surface:#10231d;--mcms-req-surface-2:#17352b;--mcms-req-border:rgba(217,183,90,.48)}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-head{display:flex!important;align-items:center!important;gap:7px!important;min-width:0!important;padding:6px 9px!important;border-bottom:1px solid rgba(255,255,255,.10)!important;background:rgba(0,0,0,.16)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-title{display:flex!important;align-items:center!important;gap:7px!important;min-width:0!important;flex:1 1 auto!important;font-size:13px!important;line-height:1.15!important;font-weight:900!important;letter-spacing:.12px!important;color:var(--mcms-req-text)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-title i{display:block!important;width:8px!important;height:8px!important;flex:0 0 8px!important;border-radius:50%!important;background:var(--mcms-req-state)!important;box-shadow:0 0 9px color-mix(in srgb,var(--mcms-req-state) 65%,transparent)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-summary{flex:0 1 auto!important;min-width:0!important;max-width:50%!important;padding:3px 7px!important;border:1px solid color-mix(in srgb,var(--mcms-req-state) 52%,transparent)!important;border-radius:999px!important;color:var(--mcms-req-text)!important;background:color-mix(in srgb,var(--mcms-req-state) 15%,transparent)!important;font-size:10px!important;line-height:1.15!important;font-weight:850!important;white-space:normal!important;text-align:center!important;overflow-wrap:anywhere!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-collapse{display:inline-flex!important;align-items:center!important;justify-content:center!important;flex:0 0 26px!important;width:26px!important;height:24px!important;padding:0!important;border:1px solid rgba(255,255,255,.18)!important;border-radius:6px!important;background:rgba(255,255,255,.07)!important;color:var(--mcms-req-text)!important;font:900 13px/1 Arial,sans-serif!important;cursor:pointer!important}
#${SCRIPT.missionRequirementsPanelId}.mcms-collapsed .mcms-req-body{display:none!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-body{max-height:min(36vh,360px)!important;overflow:auto!important;overscroll-behavior:contain!important}
#${SCRIPT.missionRequirementsPanelId} table{width:100%!important;max-width:100%!important;border-collapse:separate!important;border-spacing:0!important;table-layout:fixed!important;margin:0!important;background:transparent!important;color:inherit!important}
#${SCRIPT.missionRequirementsPanelId} col.mcms-req-name-col{width:40%!important}
#${SCRIPT.missionRequirementsPanelId} col.mcms-req-number-col{width:12%!important}
#${SCRIPT.missionRequirementsPanelId} thead th{position:sticky!important;top:0!important;z-index:2!important;padding:5px 4px!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.12)!important;background:color-mix(in srgb,var(--mcms-req-surface-2) 94%,black)!important;color:var(--mcms-req-muted)!important;font-size:9.5px!important;line-height:1.1!important;font-weight:900!important;letter-spacing:.12px!important;text-transform:uppercase!important;white-space:normal!important;text-align:center!important;overflow-wrap:anywhere!important}
#${SCRIPT.missionRequirementsPanelId} thead th:first-child{text-align:left!important;padding-left:7px!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr{--mcms-row-state:#ef5350}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="covered"]{--mcms-row-state:#4dd68a}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="partial"]{--mcms-row-state:#ffb74d}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="unresolved"]{--mcms-row-state:#aab2bd}
#${SCRIPT.missionRequirementsPanelId} tbody td{box-sizing:border-box!important;padding:5px 4px!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.07)!important;background:transparent!important;color:var(--mcms-req-text)!important;font-size:12px!important;line-height:1.15!important;vertical-align:middle!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr:last-child td{border-bottom:0!important}
#${SCRIPT.missionRequirementsPanelId} tbody td:first-child{padding-left:7px!important;border-left:3px solid var(--mcms-row-state)!important;font-weight:850!important;text-align:left!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important}
#${SCRIPT.missionRequirementsPanelId} tbody td:not(:first-child){font-variant-numeric:tabular-nums!important;text-align:center!important;white-space:nowrap!important;font-weight:800!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="covered"] td{background:rgba(77,214,138,.075)!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="covered"] td:first-child{color:#9bf2bf!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="partial"] td{background:rgba(255,183,77,.055)!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="partial"] td:first-child{color:#ffd18a!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="open"] td{background:rgba(239,83,80,.045)!important}
#${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="unresolved"] td{background:rgba(170,178,189,.055)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-still{font-size:13px!important;font-weight:950!important;color:var(--mcms-row-state)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown{display:grid!important;gap:4px!important;padding:7px 9px 8px!important;border-top:1px solid rgba(255,183,77,.22)!important;background:rgba(255,183,77,.06)!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown b{color:#ffd18a!important;font-size:10px!important;text-transform:uppercase!important;letter-spacing:.2px!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown span{color:var(--mcms-req-text)!important;font-size:11px!important;line-height:1.3!important;overflow-wrap:anywhere!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-fallback{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:10px!important;padding:9px!important;color:var(--mcms-req-text)!important;font-size:11px!important;line-height:1.35!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-fallback-message{min-width:0!important;overflow-wrap:anywhere!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-report{display:inline-flex!important;align-items:center!important;justify-content:center!important;flex:0 0 auto!important;padding:5px 8px!important;border:1px solid rgba(255,183,77,.58)!important;border-radius:6px!important;background:rgba(255,183,77,.14)!important;color:#ffe0aa!important;font:800 10px/1.2 Arial,sans-serif!important;cursor:pointer!important}
#${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown .mcms-req-report{justify-self:start!important;margin-top:2px!important}
@media(min-width:768px) and (max-width:1180px){#${SCRIPT.missionRequirementsPanelId} .mcms-req-head{padding:6px 8px!important}#${SCRIPT.missionRequirementsPanelId} thead th{font-size:9px!important}#${SCRIPT.missionRequirementsPanelId} tbody td{font-size:11.5px!important;padding:5px 3px!important}}
@media(max-width:767px){#${SCRIPT.missionRequirementsPanelId}{margin-bottom:6px!important;border-radius:7px!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-head{padding:6px 7px!important;gap:6px!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-title{font-size:12px!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-summary{max-width:47%!important;font-size:9px!important;padding:3px 5px!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-body{max-height:min(42vh,390px)!important;padding:5px!important}#${SCRIPT.missionRequirementsPanelId} table,#${SCRIPT.missionRequirementsPanelId} tbody{display:block!important;width:100%!important}#${SCRIPT.missionRequirementsPanelId} colgroup,#${SCRIPT.missionRequirementsPanelId} thead{display:none!important}#${SCRIPT.missionRequirementsPanelId} tbody tr{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:0!important;margin:0 0 5px!important;border:1px solid rgba(255,255,255,.11)!important;border-left:3px solid var(--mcms-row-state)!important;border-radius:6px!important;background:rgba(255,255,255,.035)!important;overflow:hidden!important}#${SCRIPT.missionRequirementsPanelId} tbody tr:last-child{margin-bottom:0!important}#${SCRIPT.missionRequirementsPanelId} tbody td{display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;min-width:0!important;min-height:38px!important;padding:4px 2px!important;border:0!important;border-right:1px solid rgba(255,255,255,.07)!important;font-size:11.5px!important;white-space:normal!important}#${SCRIPT.missionRequirementsPanelId} tbody td:last-child{border-right:0!important}#${SCRIPT.missionRequirementsPanelId} tbody td:first-child{grid-column:1/-1!important;display:block!important;min-height:0!important;padding:6px!important;border-left:0!important;border-right:0!important;border-bottom:1px solid rgba(255,255,255,.09)!important;font-size:12px!important;text-align:left!important}#${SCRIPT.missionRequirementsPanelId} tbody td:not(:first-child)::before{content:attr(data-label)!important;display:block!important;margin-bottom:2px!important;color:var(--mcms-req-muted)!important;font-size:7.5px!important;line-height:1!important;font-weight:900!important;letter-spacing:.08px!important;text-transform:uppercase!important;text-align:center!important;white-space:normal!important;overflow-wrap:anywhere!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-fallback{align-items:stretch!important;flex-direction:column!important}#${SCRIPT.missionRequirementsPanelId} .mcms-req-report{align-self:flex-start!important}}
        `;
    }'''

panel_function = r'''    function missionRequirementsPanelHtml(rows, unresolved) {
        const definiteOutstanding = rows.filter(row => row.definitelyOpen).length;
        const uncertain = rows.filter(row => row.uncertain).length + unresolved.length;
        const fulfilled = rows.filter(row => row.covered).length;
        const stateName = missionRequirementsOverallState(rows, unresolved);
        const summary = stateName === 'success'
            ? `All ${rows.length} covered`
            : stateName === 'warning'
                ? `${uncertain} need confirmation · ${fulfilled}/${rows.length} covered`
                : `${definiteOutstanding} outstanding · ${fulfilled}/${rows.length} covered`;
        const rowHtml = rows.map(row => {
            const rowState = row.covered ? 'covered' : row.uncertain ? 'unresolved' : row.partial ? 'partial' : 'open';
            const prefix = row.covered ? '✓ ' : '';
            const requiredText = row.requiredText || (Number.isFinite(Number(row.missing)) ? Number(row.missing).toLocaleString('en-GB') : '?');
            const onSiteText = row.onSiteText || '?';
            const respondingText = row.respondingText || row.enRouteText || '?';
            const selectedText = row.selectedText || '?';
            const stillText = row.stillNeededText || '?';
            const status = row.covered ? 'fulfilled' : row.uncertain ? 'requires confirmation' : row.partial ? 'partially fulfilled' : 'outstanding';
            return `<tr data-row-state="${rowState}" title="${escapeHtml(`${row.requirement}: ${status}`)}"><td>${escapeHtml(prefix + row.requirement)}</td><td data-label="Required">${escapeHtml(requiredText)}</td><td data-label="On site">${escapeHtml(onSiteText)}</td><td data-label="Respond.">${escapeHtml(respondingText)}</td><td data-label="Selected">${escapeHtml(selectedText)}</td><td class="mcms-req-still" data-label="Need">${escapeHtml(stillText)}</td></tr>`;
        }).join('');
        const unknownHtml = unresolved.length
            ? `<div class="mcms-req-unknown"><b>Unresolved MissionChief requirement</b>${unresolved.map(item => `<span>${escapeHtml(item.text)}</span>`).join('')}<button type="button" class="mcms-req-report" data-mcms-report-mission>Report Mission</button></div>`
            : '';
        return {
            stateName,
            html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${escapeHtml(summary)}</span><button type="button" class="mcms-req-collapse" data-mcms-requirements-collapse aria-label="Collapse mission requirements" aria-expanded="true">⌃</button></div><div class="mcms-req-body"><table aria-label="Live mission requirements"><colgroup><col class="mcms-req-name-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"></colgroup><thead><tr><th scope="col">Requirement</th><th scope="col">Required</th><th scope="col">On site</th><th scope="col">Responding</th><th scope="col">Selected</th><th scope="col">Still needed</th></tr></thead><tbody>${rowHtml}</tbody></table>${unknownHtml}</div>`
        };
    }'''

source = SRC.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.16.0", "// @version      4.16.1", "metadata version")
source = replace_once(source, "version: '4.16.0'", "version: '4.16.1'", "runtime version")
source = replace_function(source, "missionRequirementsCoverageRow", coverage_function)
source = replace_function(source, "missionRequirementsCollectUnits", collect_function)
source = insert_before(source, "    function missionRequirementsResolve(candidate, parsed) {", bucket_helper, "exclusive bucket helper")
source = replace_function(source, "missionRequirementsResolve", resolve_function)
source = replace_function(source, "missionRequirementsDocumentCss", css_function)
source = replace_function(source, "missionRequirementsPanelHtml", panel_function)
source = replace_once(
    source,
    "missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, parsed), parsed.unresolved)",
    "missionRequirementsPanelHtml(missionRequirementsResolve(record.candidate, parsed, record.catalogue), parsed.unresolved)",
    "catalogue-backed live resolver call",
)
source = replace_once(
    source,
    "const selected = missionRequirementsCollectUnits(candidate, 'selected');\n        const enRoute = missionRequirementsCollectUnits(candidate, 'enroute');",
    "const selected = missionRequirementsCollectUnits(candidate, 'selected');\n        const responding = missionRequirementsCollectUnits(candidate, 'responding');\n        const onSite = missionRequirementsCollectUnits(candidate, 'onsite');",
    "diagnostic live buckets",
)
source = replace_once(
    source,
    "`- en-route rows: ${count('#mission_vehicle_driving tbody tr')}`,\n            `- selected vehicle types: ${missionRequirementsTypeSummary(selected)}`,\n            `- en-route vehicle types: ${missionRequirementsTypeSummary(enRoute)}`",
    "`- responding rows: ${count('#mission_vehicle_driving tbody tr')}`,\n            `- on-site rows: ${count('#mission_vehicle_at_mission tbody tr')}`,\n            `- selected vehicle types: ${missionRequirementsTypeSummary(selected)}`,\n            `- responding vehicle types: ${missionRequirementsTypeSummary(responding)}`,\n            `- on-site vehicle types: ${missionRequirementsTypeSummary(onSite)}`",
    "diagnostic selector summaries",
)
source = replace_once(
    source,
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #vehicle_show_table_body_all",
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "on-site mutation observation",
)
SRC.write_text(source, encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
fixture["coverageCases"] = [
    {
        "name": "no live capacity remains fully open",
        "missing": 3,
        "required": {"min": 3, "max": 3, "known": True},
        "onSite": {"min": 0, "max": 0, "known": True},
        "responding": {"min": 0, "max": 0, "known": True},
        "selected": {"min": 0, "max": 0, "known": True},
        "covered": False, "definitelyOpen": True, "uncertain": False, "stillNeededText": "3"
    },
    {
        "name": "selected capacity immediately reduces shortage",
        "missing": 3,
        "required": {"min": 3, "max": 3, "known": True},
        "onSite": {"min": 0, "max": 0, "known": True},
        "responding": {"min": 0, "max": 0, "known": True},
        "selected": {"min": 1, "max": 1, "known": True},
        "covered": False, "definitelyOpen": True, "uncertain": False, "stillNeededText": "2"
    },
    {
        "name": "on-site responding and selected capacity combine",
        "missing": 3,
        "required": {"min": 4, "max": 4, "known": True},
        "onSite": {"min": 1, "max": 1, "known": True},
        "responding": {"min": 1, "max": 1, "known": True},
        "selected": {"min": 1, "max": 1, "known": True},
        "covered": False, "definitelyOpen": True, "uncertain": False, "stillNeededText": "1"
    },
    {
        "name": "all live buckets fulfil the requirement",
        "missing": 2,
        "required": {"min": 4, "max": 4, "known": True},
        "onSite": {"min": 2, "max": 2, "known": True},
        "responding": {"min": 1, "max": 1, "known": True},
        "selected": {"min": 1, "max": 1, "known": True},
        "covered": True, "definitelyOpen": False, "uncertain": False, "stillNeededText": "0"
    },
    {
        "name": "known minimum covers despite unknown maximum",
        "missing": 2,
        "required": {"min": 4, "max": 4, "known": True},
        "onSite": {"min": 2, "max": 2, "known": True},
        "responding": {"min": 0, "max": None, "known": False},
        "selected": {"min": 2, "max": 2, "known": True},
        "covered": True, "definitelyOpen": False, "uncertain": False, "stillNeededText": "0"
    },
    {
        "name": "bounded personnel remains visibly uncertain",
        "missing": 4,
        "required": {"min": 4, "max": 4, "known": True},
        "onSite": {"min": 0, "max": 0, "known": True},
        "responding": {"min": 0, "max": 0, "known": True},
        "selected": {"min": 2, "max": 6, "known": False},
        "covered": False, "definitelyOpen": False, "uncertain": True, "stillNeededText": "0–2"
    }
]
fixture["layout"]["requiredHeaders"] = ["Requirement", "Required", "On site", "Responding", "Selected", "Still needed"]
FIXTURE.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.16.0'", "version: '4.16.1'", "runtime fixture version")
runtime = replace_once(
    runtime,
    """    const row = api.coverageRow(
        { key: testCase.name, requirement: testCase.name, missing: testCase.missing, group: 'vehicles', definition: {} },
        testCase.selected,
        testCase.enRoute
    );""",
    """    const row = api.coverageRow(
        { key: testCase.name, requirement: testCase.name, missing: testCase.missing, group: 'vehicles', definition: {} },
        testCase.selected,
        testCase.responding,
        testCase.onSite,
        testCase.required
    );""",
    "runtime coverage fixture arguments",
)
runtime = replace_once(runtime, "    missionRoot.enRouteRows = [];", "    missionRoot.enRouteRows = [];\n    missionRoot.onSiteRows = [];", "mission candidate on-site store")
runtime = replace_once(runtime, "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;", "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;\n        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;", "mission candidate on-site selector")
runtime = replace_once(runtime, "    missionRoot.enRouteRows = [];", "    missionRoot.enRouteRows = [];\n    missionRoot.onSiteRows = [];", "source-less candidate on-site store")
runtime = replace_once(runtime, "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;", "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;\n        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;", "source-less candidate on-site selector")
unit_start = runtime.index("const unitDoc = new FakeDocument();")
unit_end = runtime.index("const personnelDoc = new FakeDocument();", unit_start)
if unit_start < 0 or unit_end < 0:
    raise AssertionError("runtime unit transition block missing")
unit_tests = r'''const unitDoc = new FakeDocument();
unitDoc.defaultView = { MutationObserver: FakeMutationObserver };
const unitCandidate = makeMissionCandidate(unitDoc, '2 Ambulances');
const firstAmbulance = makeVehicleElement(unitDoc, 101, 5);
const secondAmbulance = makeVehicleElement(unitDoc, 102, 5);
const ambulanceDefinition = api.definitions.find(definition => definition.key === 'ambulance');
const ambulanceParsed = {
    requirements: [{ key: 'ambulance', requirement: 'Ambulance', missing: 2, group: 'vehicles', definition: ambulanceDefinition }],
    unresolved: []
};
const ambulanceCatalogue = { requirements: [{ key: 'ambulance', baseline: 2, missing: 2 }] };
unitCandidate.root.selectedUnits = [firstAmbulance.vehicle];
let resolved = api.resolve(unitCandidate, ambulanceParsed, ambulanceCatalogue)[0];
assert.strictEqual(resolved.requiredText, '2', 'catalogue baseline supplies total required capacity');
assert.strictEqual(resolved.selectedMin, 1, 'selected vehicle is counted');
assert.strictEqual(resolved.stillNeededText, '1', 'selected capacity immediately reduces still needed');

unitCandidate.root.selectedUnits = [firstAmbulance.vehicle, secondAmbulance.vehicle];
resolved = api.resolve(unitCandidate, ambulanceParsed, ambulanceCatalogue)[0];
assert.strictEqual(resolved.stillNeededText, '0', 'second selected vehicle fulfils the requirement');
assert.strictEqual(resolved.covered, true, 'selected vehicles can produce a green fulfilled row');

unitCandidate.root.selectedUnits = [firstAmbulance.vehicle];
unitCandidate.root.enRouteRows = [secondAmbulance.row];
resolved = api.resolve(unitCandidate, ambulanceParsed, ambulanceCatalogue)[0];
assert.strictEqual(resolved.respondingMin, 1, 'dispatch moves capacity into responding');
assert.strictEqual(resolved.stillNeededText, '0', 'selected to responding transition preserves fulfilment');

unitCandidate.root.selectedUnits = [firstAmbulance.vehicle, secondAmbulance.vehicle];
resolved = api.resolve(unitCandidate, ambulanceParsed, ambulanceCatalogue)[0];
assert.strictEqual(resolved.selectedMin, 1, 'same vehicle visible as selected and responding is not double-counted');
assert.strictEqual(resolved.respondingMin, 1, 'responding bucket takes precedence during DOM transition');

unitCandidate.root.selectedUnits = [firstAmbulance.vehicle];
unitCandidate.root.enRouteRows = [];
unitCandidate.root.onSiteRows = [secondAmbulance.row];
ambulanceParsed.requirements[0].missing = 1;
resolved = api.resolve(unitCandidate, ambulanceParsed, ambulanceCatalogue)[0];
assert.strictEqual(resolved.onSiteMin, 1, 'arrival moves capacity into on-site');
assert.strictEqual(resolved.respondingMin, 0, 'arrived unit leaves responding');
assert.strictEqual(resolved.stillNeededText, '0', 'responding to on-site transition preserves fulfilment');

unitCandidate.root.onSiteRows = [];
ambulanceParsed.requirements[0].missing = 2;
resolved = api.resolve(unitCandidate, ambulanceParsed, ambulanceCatalogue)[0];
assert.strictEqual(resolved.onSiteMin, 0, 'unit removal is reconciled');
assert.strictEqual(resolved.stillNeededText, '1', 'shortage returns when capacity leaves the mission');

'''
runtime = runtime[:unit_start] + unit_tests + runtime[unit_end:]
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(contract, "function missionRequirementsCoverageRow(requirement, selectedCapacity, enRouteCapacity)", "function missionRequirementsCoverageRow(requirement, selectedCapacity, respondingCapacity, onSiteCapacity = null, requiredCapacity = null)", "contract coverage signature")
contract = replace_once(contract, "function missionRequirementsResolve(candidate, parsed)", "function missionRequirementsResolve(candidate, parsed, catalogue = null)", "contract resolver signature")
contract = replace_once(contract, '        "#mission_vehicle_driving",', '        "#mission_vehicle_driving",\n        "#mission_vehicle_at_mission",', "contract on-site selector")
contract = replace_once(contract, '    assert "grid-template-columns:repeat(4,minmax(0,1fr))" in compact_css', '    assert "grid-template-columns:repeat(5,minmax(0,1fr))" in compact_css', "contract mobile grid")
CONTRACT.write_text(contract, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = '''## [4.16.1] - 2026-07-18

### Fixed
- Reworked Mission Requirements into a complete live capacity matrix with **Required**, **On site**, **Responding**, **Selected** and **Still needed** values.
- Selected vehicles now reduce **Still needed** immediately; responding and arrived units move between mutually exclusive buckets without double-counting.
- Added `#mission_vehicle_at_mission` observation so arrivals, departures and cancellations update the matrix dynamically.

### Interface
- Added compact red, amber, green and unresolved row states with tighter headers, rows and responsive five-metric mobile cards.
- Preserved normal-flow mounting, collapse behaviour, Desktop/Tablet/iOS distinctions and equal treatment for all seven interface systems.

### Validation
- Added deterministic selection, dispatch, arrival, removal, cross-bucket de-duplication, uncertainty and compact-layout fixtures.

'''
if "## [4.16.1]" not in changelog:
    changelog = replace_once(changelog, "## [4.16.0]", entry + "## [4.16.0]", "4.16.1 changelog")
changelog_path.write_text(changelog, encoding="utf-8")

doc_path = ROOT / "docs" / "issue-167-live-requirements-capacity-contract.md"
doc_path.write_text('''# Issue #167 — Live Mission Requirements capacity contract

## Authority and calculation

- The official MissionChief catalogue supplies the total baseline where available.
- Native `#missing_text` remains the live outstanding signal and is reconciled with counted on-site capacity.
- `#mission_vehicle_at_mission`, `#mission_vehicle_driving` and checked dispatch rows are separate, mutually exclusive buckets.
- The displayed result is `max(0, Required - On site - Responding - Selected)`.
- Without a catalogue baseline, Required is reconstructed as native missing plus observed on-site capacity so on-site units are not subtracted twice.

## Lifecycle

Selection changes, dispatch transitions, arrivals, departures, cancellations, missing-text replacement and mission-window navigation schedule one bounded recalculation. On-site capacity takes precedence over responding, which takes precedence over selected during temporary DOM overlap.

## Visual states

- Green: definitely fulfilled.
- Amber: partially fulfilled or capacity is bounded/uncertain.
- Red: definitely outstanding.
- Neutral unresolved: mapping or authority is insufficient; never falsely green.

The panel remains in normal document flow and uses compact Desktop/Tablet tables and a compact five-metric iOS card row.
''', encoding="utf-8")

issue163_doc = ROOT / "docs" / "issue-163-mission-catalogue-resolver-contract.md"
if issue163_doc.exists():
    text = issue163_doc.read_text(encoding="utf-8")
    text = text.replace("Native selected checkboxes and the native en-route table remain authoritative for selected and travelling units.", "Native selected checkboxes, the responding table and the on-site table remain authoritative for selected, travelling and arrived units.")
    issue163_doc.write_text(text, encoding="utf-8")

if DIAGNOSTIC.exists():
    DIAGNOSTIC.unlink()
try:
    DIAGNOSTIC.parent.rmdir()
except OSError:
    pass

help_manifest_path = ROOT / "help" / "manifest.json"
help_manifest = json.loads(help_manifest_path.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "4.16.1"
help_manifest["toolkitVersion"] = "4.16.1"
help_manifest["updated"] = "2026-07-18"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.16.1 adds live on-site, responding and selected capacity reconciliation to Mission Requirements."
help_manifest_path.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

help_index = ROOT / "help" / "index.html"
help_text = help_index.read_text(encoding="utf-8")
help_index.write_text(help_text.replace("4.16.0", "4.16.1"), encoding="utf-8")

canonical = SRC.read_bytes()
dist_user = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
dist_txt = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
dist_user.write_bytes(canonical)
dist_txt.write_bytes(canonical)
digest = hashlib.sha256(canonical).hexdigest()
(ROOT / "dist" / "SHA256SUMS.txt").write_text(f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n", encoding="utf-8")
manifest_path = ROOT / "dist" / "release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "4.16.1"
manifest["sha256"] = digest
manifest["bytes"] = len(canonical)
manifest["lines"] = canonical.count(b"\n")
manifest.setdefault("metadata", {})["runtimeVersion"] = "4.16.1"
manifest["distributionStatus"] = "dry-run-not-yet-greasyfork-source"
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

run("node", "--check", str(SRC.relative_to(ROOT)))
run("node", str(RUNTIME.relative_to(ROOT)))
run("python3", str(CONTRACT.relative_to(ROOT)))
print(f"Issue #167 candidate ready: sha256={digest}")
