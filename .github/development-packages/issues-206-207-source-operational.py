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

fn('missionRequirementsStaffCapacity','missionRequirementsCollectUnits',r'''    function missionRequirementsStaffCapacity(element) {
        const row = element?.closest?.('tr') || element;
        const crewCell = row?.querySelector?.('[data-personnel-count], [data-current-personnel], [data-min-personnel], [data-max-personnel], [data-min-crew], [data-max-crew], [data-column="crew"], td:nth-of-type(4), td:nth-of-type(5)[sortvalue]');
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
    }

    function missionRequirementsOperationalSelectors(mode) {
        if (mode === 'selected') return ['#vehicle_show_table_body_all .vehicle_checkbox:checked, #occupied .vehicle_checkbox:checked, .vehicle_checkbox:checked'];
        if (mode === 'onsite') return ['#mission_vehicle_at_mission tbody tr', 'tbody#mission_vehicle_at_mission > tr', '#mission_vehicle_at_mission > tr', '[data-mcms-vehicle-state="onsite"]'];
        return ['#mission_vehicle_driving tbody tr', 'tbody#mission_vehicle_driving > tr', '#mission_vehicle_driving > tr', '[data-mcms-vehicle-state="responding"]'];
    }

    function missionRequirementsOperationalElementActive(element, candidate, context = missionRequirementsPatientContext(candidate)) {
        if (!element || element.isConnected === false || !isVisible(element)) return false;
        const row = element.matches?.('tr') ? element : element.closest?.('tr') || element;
        if (context.activeWindow && !(context.activeWindow === row || context.activeWindow.contains?.(row) || row.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog') === context.activeWindow)) return false;
        const expectedMission = missionRequirementsMissionIdentity(candidate, candidate?.source);
        const explicitMission = missionRequirementsOptionalNumber(row?.getAttribute?.('data-mission-id') ?? row?.dataset?.missionId);
        if (expectedMission > 0 && explicitMission !== null && explicitMission !== expectedMission) return false;
        const missionRoot = row.closest?.('#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]');
        if (expectedMission > 0 && missionRoot) {
            const actualMission = missionRequirementsMissionIdentity({ root: missionRoot, mount: missionRoot }, null);
            if (actualMission > 0 && actualMission !== expectedMission) return false;
        }
        return true;
    }

    function missionRequirementsCollectUnits(candidate, mode) {
        const root = candidate?.root;
        const context = missionRequirementsPatientContext(candidate);
        const doc = context.doc || candidate?.source?.ownerDocument || root?.ownerDocument;
        if (!root?.querySelectorAll && !doc?.querySelectorAll) return [];
        const selectors = missionRequirementsOperationalSelectors(mode);
        const elements = [];
        const seenElements = new Set();
        const localScopes = Array.from(new Set([root, candidate?.mount, context.activeWindow].filter(scope => scope?.querySelectorAll)));
        const search = scope => {
            for (const selector of selectors) {
                for (const element of Array.from(scope?.querySelectorAll?.(selector) || [])) {
                    if (seenElements.has(element) || !missionRequirementsOperationalElementActive(element, candidate, context)) continue;
                    seenElements.add(element);
                    elements.push(element);
                }
            }
        };
        localScopes.forEach(search);
        if (!elements.length && doc?.querySelectorAll && !localScopes.includes(doc)) search(doc);

        const units = new Map();
        elements.forEach((element, index) => {
            const row = element.matches?.('tr') ? element : element.closest?.('tr');
            const vehicleElement = mode === 'selected'
                ? element
                : (element.querySelector?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-vehicle-id], a[href*="/vehicles/"]') || element);
            const typeId = missionRequirementsVehicleType(vehicleElement);
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
            const labels = missionRequirementsMetadataValues(vehicleElement, 'labels');
            const training = missionRequirementsMetadataValues(vehicleElement, 'training');
            const knownDefinitionKeys = missionRequirementsKnownDefinitionKeys(labels);
            const unit = {
                typeId,
                vehicleId,
                tractiveId,
                equipment: missionRequirementsEquipmentTypes(vehicleElement),
                staff: missionRequirementsStaffCapacity(vehicleElement),
                labels,
                training,
                knownDefinitionKeys,
                contributionKey
            };
            const existing = units.get(identityKey);
            if (!existing) { units.set(identityKey, unit); return; }
            if (existing.typeId < 0 && unit.typeId >= 0) existing.typeId = unit.typeId;
            for (const equipment of unit.equipment) existing.equipment.add(equipment);
            for (const label of unit.labels) existing.labels.add(label);
            for (const qualification of unit.training) existing.training.add(qualification);
            for (const key of unit.knownDefinitionKeys) existing.knownDefinitionKeys.add(key);
            if ((!existing.staff || !existing.staff.known) && unit.staff?.known) existing.staff = unit.staff;
            if (existing.contributionKey.startsWith('element:') && !unit.contributionKey.startsWith('element:')) existing.contributionKey = unit.contributionKey;
        });
        return Array.from(units.values());
    }''')

SOURCE.write_text(s, encoding="utf-8")
print('Applied v4.20.3 responding and on-site acquisition source patch')
