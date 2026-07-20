# Issue #259 — LSSM Mission Requirements parity audit

## Pinned baselines

- Toolkit: `8619c79b794ad7241e0a37a0c91a6176daee7911` (v4.20.12)
- LSSM V.4: `4f731e1d6d009cbf2129530fb31d10177b21a52a` (4.7.12+20260720.0722)

## Source marker inspection

This section is generated from the canonical Toolkit source during the guarded development-package preflight.

### `missionRequirementsEquipmentTypes` — position `1398211`
```text
*="/vehicles/"]');
        const hrefMatch = String(link?.getAttribute?.('href') || link?.href || '').match(/\/vehicles\/(\d+)(?:\/|$)/u);
        if (hrefMatch) return Number(hrefMatch[1]);
        }
        return -1;
    }

    function missionRequirementsEquipmentTypes(element) {
        const values = new Set();
        const add = raw => String(raw || '').split(',').map(value => value.trim().toLowerCase()).filter(Boolean).forEach(value => values.add(value));
        const scopes = Array.from(new Set([element, element?.closest?.('tr')].filter(Boolean)));
        for (const scope of scopes) {
        add(scope?.dataset?.equipmentType);
        add(scope?.dataset?.equipmentTypes);
        add(scope?.getAttribute?.('data-equipment-type'));
        add(scope?.getAttribute?.('data-equipment-types'));
        scope?.querySelectorAll?.('[data-equipment-type], [data-equipment-types]').forEach(node => {
            add(node.getAttribute('data-equipment-type'));
            add(node.getAttribute('data-equipment-types'));
        });
        }
        return values;
    }

function missionRequirementsCapabilityLabel(value) { ret
```

### `missionRequirementsStaffCapacity` — position `1401509`
```text
mentsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }

function missionRequirementsStaffCapacity(element) {
        const row = element?.closest?.('tr') || element;
        const semanticSelectors = [
            '[data-personnel-count]',
            '[data-current-personnel]',
            '[data-min-personnel]',
            '[data-max-personnel]',
            '[data-min-crew]',
            '[data-max-crew]',
            '[data-column="crew"]',
            '[data-column="personnel"]',
            '[data-column="staff"]'
        ];
        let crewCell = null;
        for (const selector of semanticSelectors) {
            crewCell = row?.querySelector?.(selector) || null;
            if (crewCell) break;
        }
        const scopes = Array.from(new Set([element, row, crewCell].filter(Boolean)));
        const exactAttributes = ['data-personnel-count', 'data-current-personnel', 'data-personnel', 'data-staff', 'data-crew'];
        for (const scope 
```

### `missionRequirementsCollectUnits` — position `1409505`
```text
 const actualMission = missionRequirementsMissionIdentity({ root: missionRoot, mount: missionRoot }, null);
            if (actualMission > 0 && actualMission !== expectedMission) return false;
        }
        return true;
    }
function missionRequirementsCollectUnits(candidate, mode) { const root = candidate?.root; const context = missionRequirementsPatientContext(candidate); const doc = context.doc || candidate?.source?.ownerDocument || root?.ownerDocument; if (!root?.querySelectorAll && !doc?.querySelectorAll) return []; const selectors = missionRequirementsOperationalSelectors(mode); const windowScopes = missionRequirementsOperationalWindowScopes(candidate, context); const anchorSelector = mode === 'selected' ? '#vehicle_show_table_body_all, #occupied, .vehicle_checkbox' : mode === 'onsite' ? '#mission_vehicle_at_mission, [data-mcms-vehicle-state="onsite"]' : '#mission_vehicle_driving, [data-mcms-vehicle-state="responding"]'; let activeWindow = context.activeWindow || null; for (const scope of windowScopes) { if (scope?.querySelector?.(anchorSelector)) { activeWindow = scope; break; } } const operationalContext = { 
```

### `missionRequirementsAggregate` — position `1417761`
```text
typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1); const value = Number.isFinite(factor) && factor > 0 ? factor : 1; return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) }; }

function missionRequirementsAggregate(requirement, units) { const contributions = new Map(); let unresolvedClassification = false; for (const unit of units) { const contribution = missionRequirementsUnitContribution(requirement, unit); unresolvedClassification = unresolvedClassification || contribution.unknown === true; if (!contribution.eligible) continue; const capacity = contribution.capacity; const existing = contributions.get(unit.contributionKey); if (!existing) { contributions.set(unit.contributionKey, capacity); continue; } const pairMin = Math.max(existing.min, capacity.min); const pairMax = existing.max === null || capacity.max === null ? null : Math.max(existing.max, capacity.max); contributions.set(unit.contributionKey, missionRequirementsCapacity(pairMin, pairMax, existing.known && capacity.known && pairMax === pairMin)); } let min = 0; let max = 0; let exact = true; for (const capac
```

### `missionRequirementsResolve` — position `1442737`
```text
     return true;
        });
        const onSite = claim(onSiteUnits);
        const responding = claim(respondingUnits);
        const selected = claim(selectedUnits);
        return { selected, responding, onSite };
    }

    function missionRequirementsResolve(candidate, parsed, catalogue = null) { const rawSelectedUnits = missionRequirementsCollectUnits(candidate, 'selected'); const rawRespondingUnits = missionRequirementsCollectUnits(candidate, 'responding'); const rawOnSiteUnits = missionRequirementsCollectUnits(candidate, 'onsite'); const buckets = missionRequirementsExclusiveUnitBuckets(rawSelectedUnits, rawRespondingUnits, rawOnSiteUnits); const catalogueByKey = new Map(Array.from(catalogue?.requirements || []).map(item => [item.key, item])); return parsed.requirements.map(requirement => { if (requirement.patientCondition === true) { const requiredValue = Math.max(0, Number(requirement.patientConditionRequired ?? requirement.patientRequired ?? requirement.missing) || 0); const fulfilledValue = Math.max(0, Number(requirement.patientConditionFulfilled) || 0); const fulfilledKnown = requirement.patientConditionFul
```

### `water-resource` — position `1355592`
```text
"Paramedics"],"group":"staff","types":[5,9,20,27,28,31,34,81,83,95,96]},{"key":"search-technicians","label":"Search Technicians","aliases":["Search Technician","Search Technicians"],"group":"staff","types":[86,87,92,93,99,101,102]},{"key":"water-resource","label":"Water","aliases":["Water","litres of water","liters of water"],"group":"other","bar":"water","types":[]},{"key":"foam-resource","label":"Foam","aliases":["Foam","litres of foam","liters of foam"],"group":"other","bar":"foam","types":[]},{"key":"pump-resource","label":"Pumping Capacity","aliases":["l/min pumping process","l/min pumping capacity","Pumping Capacity"],"group":"other","bar":"pump","types":[]},{"key":"fire-engine-2","group":"vehicles","aliases":["Fire engine","Fire engines"],"types":[0,1,16,17,26,37,38,47]},{"key":"fire-engine-or-riv-2","group":"vehicles","aliases":["Fire Engine or RIV","Fire Engines or RIVs"],"types":[0,1,16,17,26,37,38,47,76]},{"key":"aerial-appliance-truck","group":"vehicles","aliases":["Aerial Appliance Truck","Aerial Appliance Trucks"],"types":[2,17]},{"key":"aerial-appliance-truck-or-rescue-stairs","group":"vehicles","aliases":["
```

### `tractive_vehicle_id` — position `1411631`
```text
/vehicles/"]') || element); const typeId = missionRequirementsVehicleType(vehicleElement); const vehicleId = missionRequirementsVehicleId(vehicleElement); const tractiveId = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('tractive_vehicle_id') ?? vehicleElement?.getAttribute?.('data-tractive-vehicle-id') ?? row?.getAttribute?.('tractive_vehicle_id') ?? row?.getAttribute?.('data-tractive-vehicle-id') ?? row?.dataset?.tractiveVehicleId); const trailerId = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('trailer_id') ?? vehicleElement?.getAttribute?.('data-trailer-id') ?? row?.getAttribute?.('trailer_id') ?? row?.getAttribute?.('data-trailer-id') ?? row?.dataset?.trailerId); let contributionKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : `element:${index}`; const pairedId = tractiveId !== null && tractiveId >= 0 ? tractiveId : trailerId; if (vehicleId >= 0 && pairedId !== null && pairedId >= 0) contributionKey = `pair:${Math.min(vehicleId, pairedId)}:${Math.max(vehicleId, pairedId)}`; const identityKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : contributionKey; const labels = missionRequire
```

### `data-equipment-type` — position `1398699`
```text
s = Array.from(new Set([element, element?.closest?.('tr')].filter(Boolean)));
        for (const scope of scopes) {
        add(scope?.dataset?.equipmentType);
        add(scope?.dataset?.equipmentTypes);
        add(scope?.getAttribute?.('data-equipment-type'));
        add(scope?.getAttribute?.('data-equipment-types'));
        scope?.querySelectorAll?.('[data-equipment-type], [data-equipment-types]').forEach(node => {
            add(node.getAttribute('data-equipment-type'));
            add(node.getAttribute('data-equipment-types'));
        });
        }
        return values;
    }

function missionRequirementsCapabilityLabel(value) { return String(value || '') .replace(/\u00a0/gu, ' ') .replace(/&/gu, ' and ') .replace(/\([^)]*\)/gu, ' ') .replace(/[^a-z0-9]+/giu, ' ') .replace(/\s+/gu, ' ') .trim() .toLowerCase(); } function missionRequirementsMetadataValues(element, kind = 'labels') { const values = new Set(); const add = raw => String(raw || '').split(/[,;|]/u).map(missionRequirementsCapabilityLabel).filter(Boolean).forEach(value => values.add(value)); const row = element?.closest?.('tr') || element; const scopes
```

### `max_personnel_override` — position `-1`
```text
NOT FOUND
```

### `mission_water_bar_` — position `1419370`
```text
idate.root : candidate?.mount;
        const holder = root?.querySelector?.(`[id^="mission_${bar}_holder"]`);
        if (!holder) return null;
        const node = holder.querySelector?.(`[class*="mission_${bar}_bar_${metric}_"], [class*="mission_water_bar_${metric}_"]`);
        return node ? missionRequirementsNumber(node.textContent) : null;
    }

    function missionRequirementsUnknownCoverageRow(requirement) {
        const missing = Math.max(0, missionRequirementsNumber(requirement?.missing));
        return {
        ...requirement,
        missing,
        missingText: missing.toLocaleString('en-GB'),
        selectedMin: 0,
        selectedMax: null,
        selectedKnown: false,
        selectedText: '?',
        enRouteMin: 0,
        enRouteMax: null,
        enRouteKnown: false,
        enRouteText: '?',
        stillNeededMin: 0,
        stillNeededMax: missing,
        stillNeededText: '?',
        covered: false,
        definitelyOpen: false,
        uncertain: true
        };
    }


    const MISSION_REQUIREMENTS_CATALOGUE_TTL_MS = 6 * 60 * 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_STALE_MS =
```
