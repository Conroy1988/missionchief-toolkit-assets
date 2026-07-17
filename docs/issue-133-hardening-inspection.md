# Issue #133 — hardening inspection

Generated mechanically from the applied v4.15.0 candidate. Inspection only.

Canonical source lines 21857–22491.

```javascript
    // Issue #133 clean-room live mission requirements matrix.
    // MissionChief's active mission DOM is authoritative. Unknown labels remain unresolved.
    const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze([
        { key: 'fire-engine-or-riv', label: 'Fire Engine or RIV', aliases: ['Fire Engine or RIV', 'Fire Engines or RIVs'], types: [0, 1, 16, 17, 26, 37, 38, 47, 76] },
        { key: 'aerial-or-stairs', label: 'Aerial Appliance or Rescue Stairs', aliases: ['Aerial Appliance Truck or Rescue Stairs', 'Aerial Appliance Trucks or Rescue Stairs'], types: [2, 17, 78] },
        { key: 'fire-rescue-aerial', label: 'Fire, rescue or aerial appliance', aliases: ['Fire engine, Rescue Support Vehicle or Aerial Appliance Truck', 'Fire engines, Rescue Support Vehicles or Aerial Appliance Trucks'], types: [0, 1, 2, 4, 16, 17, 26, 37, 38, 43, 47] },
        { key: 'fire-or-rescue', label: 'Fire Engine or Rescue Support Vehicle', aliases: ['Fire engine or Rescue Support Vehicle', 'Fire engines or Rescue Support Vehicles'], types: [0, 1, 4, 16, 17, 26, 37, 38, 43, 47] },
        { key: 'police-or-arv', label: 'Police Car or ARV', aliases: ['Police Car or Armed Response Vehicle (ARV)', 'Police Cars or Armed Response Vehicles (ARVs)'], types: [8, 12, 13, 19, 24, 25, 51, 52, 56, 82, 116] },
        { key: 'rsu-or-rescue-pump', label: 'Rescue Support Unit or Rescue Pump', aliases: ['Rescue Support Unit or Rescue Pump', 'Rescue Support Units or Rescue Pumps'], types: [4, 16, 38, 43] },
        { key: 'iccu-or-control', label: 'ICCU or Ambulance Control Unit', aliases: ['ICCU or Ambulance Control Unit', 'ICCU or Ambulance Control Units'], types: [15, 31, 44, 77] },
        { key: 'hazmat-or-cbrn', label: 'HazMat Unit or CBRN Vehicle', aliases: ['HazMat Unit or CBRN Vehicle', 'HazMat Units or CBRN Vehicles'], types: [7, 32, 39, 48, 49] },
        { key: 'boat-or-inland', label: 'Boat Trailer or Inland Rescue Boat', aliases: ['Boat Trailer or Inland Rescue Boat', 'Boat Trailers or Inland Rescue Boats'], types: [67, 74], pair: true },
        { key: 'ilb-or-alb', label: 'ILB or ALB', aliases: ['ILB or ALB', 'ILBs or ALBs'], types: [68, 69] },
        { key: 'sar-support', label: 'Operational Support or SAR Vehicle', aliases: ['Operational Support Van, Trailer or Personal SAR Vehicle', 'Operational Support Vans, Trailers or Personal SAR Vehicles'], types: [86, 87, 92], pair: true },
        { key: 'fire-engine', label: 'Fire Engine', aliases: ['Fire engine', 'Fire engines'], types: [0, 1, 16, 17, 26, 37, 38, 47] },
        { key: 'aerial', label: 'Aerial Appliance Truck', aliases: ['Aerial Appliance Truck', 'Aerial Appliance Trucks'], types: [2, 17] },
        { key: 'fire-officer', label: 'Fire Officer', aliases: ['Fire Officer', 'Fire Officers'], types: [3, 15, 44, 77] },
        { key: 'basu', label: 'BASU', aliases: ['BASU', 'BASUs'], types: [14, 39, 46, 49] },
        { key: 'water-carrier', label: 'Water Carrier', aliases: ['Water Carrier', 'Water Carriers'], types: [6, 26, 36, 41, 50] },
        { key: 'drone', label: 'Drone', aliases: ['Drone', 'Drones'], types: [89, 90, 91], equipment: ['drone'] },
        { key: 'control-van', label: 'Control Van', aliases: ['Control Van', 'Control Vans'], types: [85] },
        { key: 'ambulance', label: 'Ambulance', aliases: ['Ambulance', 'Ambulances'], types: [5] },
        { key: 'police-car', label: 'Police Car', aliases: ['Police car', 'Police cars'], types: [8, 12, 13, 19, 24, 25, 51, 52, 56, 82, 116] },
        { key: 'hems', label: 'HEMS', aliases: ['HEMS'], types: [9] },
        { key: 'police-helicopter', label: 'Police Helicopter', aliases: ['Police helicopter', 'Police helicopters', 'Policehelicopter', 'Policehelicopters'], types: [11] },
        { key: 'armed-response', label: 'Armed Response', aliases: ['Armed Response', 'Armed Response Vehicle', 'Armed Response Vehicles'], types: [13, 25, 52, 56, 82] },
        { key: 'dsu', label: 'Dog Support Unit (DSU)', aliases: ['Dog Support Unit (DSU)', 'Dog Support Units (DSUs)'], types: [12, 53] },
        { key: 'otl', label: 'Operational Team Leader', aliases: ['Operational Team Leader', 'Operational Team Leaders'], types: [20, 31, 34] },
        { key: 'traffic-car', label: 'Traffic Car', aliases: ['Traffic Car', 'Traffic Cars'], types: [24, 25] },
        { key: 'atv-carrier', label: 'ATV Carrier', aliases: ['ATV Carrier', 'ATV Carriers'], types: [30] },
        { key: 'primary-response', label: 'Primary Response Vehicle', aliases: ['Primary Response Vehicle', 'Primary Response Vehicles'], types: [27] },
        { key: 'secondary-response', label: 'Secondary Response Vehicle', aliases: ['Secondary Response Vehicle', 'Secondary Response Vehicles'], types: [28] },
        { key: 'welfare', label: 'Welfare Vehicle', aliases: ['Welfare Vehicle', 'Welfare Vehicles'], types: [29, 39, 45, 49, 115] },
        { key: 'ambulance-officer', label: 'Ambulance Officer', aliases: ['Ambulance Officer', 'Ambulance Officers'], types: [34] },
        { key: 'foam-unit', label: 'Foam Unit', aliases: ['Foam Unit', 'Foam Units'], types: [35, 36, 37, 38, 42, 75] },
        { key: 'mass-casualty', label: 'Mass Casualty Equipment', aliases: ['Mass Casualty Equipment'], types: [33] },
        { key: 'mounted', label: 'Mounted Unit', aliases: ['Mounted Unit', 'Mounted Units'], types: [55] },
        { key: '4x4', label: '4x4 Vehicle', aliases: ['4x4 Vehicle', '4x4 Vehicles', '4x4 Unit', '4x4 Units'], types: [66, 73, 93] },
        { key: 'coastguard-rope', label: 'Coastguard Rope Rescue Unit', aliases: ['Coastguard Rope Rescue Unit', 'Coastguard Rope Rescue Units'], types: [59] },
        { key: 'flood-rescue', label: 'Flood Rescue Unit', aliases: ['Flood Rescue Unit', 'Flood Rescue Units'], types: [61] },
        { key: 'crv', label: 'CRV', aliases: ['CRV', 'CRVs'], types: [57, 58, 59] },
        { key: 'coastguard-commander', label: 'Coastguard Commander', aliases: ['Coastguard Commander', 'Coastguard Commanders'], types: [60] },
        { key: 'ilb', label: 'ILB', aliases: ['ILB', 'ILBs'], types: [68, 69] },
        { key: 'coastguard-helicopter', label: 'Coastguard Rescue Helicopter', aliases: ['Coastguard Rescue Helicopter', 'Coastguard Rescue Helicopters'], types: [64, 65] },
        { key: 'alb', label: 'ALB', aliases: ['ALB', 'ALBs'], types: [69] },
        { key: 'mud-decon', label: 'Mud Decontamination Unit', aliases: ['Mud Decontamination Unit', 'Mud Decontamination Units'], types: [62] },
        { key: 'support-unit', label: 'Support Unit', aliases: ['Support Unit', 'Support Units'], types: [63] },
        { key: 'rescue-watercraft', label: 'Rescue Watercraft Trailer', aliases: ['Rescue Watercraft (Trailer)', 'Rescue Watercraft (Trailers)'], types: [70], pair: true },
        { key: 'coastguard-mud', label: 'Coastguard Mud Rescue Unit', aliases: ['Coastguard Mud Rescue Unit', 'Coastguard Mud Rescue Units'], types: [58] },
        { key: 'hovercraft', label: 'Hovercraft Trailer', aliases: ['Hovercraft (trailer)', 'Hovercrafts (trailer)'], types: [71], pair: true },
        { key: 'major-foam', label: 'Major Foam Tender', aliases: ['Major Foam Tender', 'Major Foam Tenders'], types: [75] },
        { key: 'rescue-stair', label: 'Rescue Stair', aliases: ['Rescue Stair', 'Rescue Stairs'], types: [78, 2, 17] },
        { key: 'airfield-command', label: 'Airfield Firefighting Command Vehicle', aliases: ['Airfield Firefighting Command Vehicle', 'Airfield Firefighting Command Vehicles'], types: [77] },
        { key: 'airfield-operations', label: 'Airfield Operations Vehicle', aliases: ['Airfield Operations Vehicle', 'Airfield Operations Vehicles'], types: [79, 80] },
        { key: 'riv', label: 'RIV', aliases: ['RIV', 'RIVs'], types: [76] },
        { key: 'medical-trailer', label: 'Medical Equipment Trailer', aliases: ['Medical equipment trailer', 'Medical equipment trailers'], types: [81], pair: true },
        { key: 'airfield-supervisor', label: 'Airfield Operations Supervisor', aliases: ['Airfield Operations Supervisor', 'Airfield Operations Supervisors'], types: [80] },
        { key: 'armed-cell', label: 'Armed Cell Van', aliases: ['Armed Cell Van', 'Armed Cell Vans'], types: [82] },
        { key: 'cycle-responder', label: 'Medical Cycle Responder', aliases: ['Medical cycle responder', 'Medical cycle responders'], types: [83] },
        { key: 'midwife', label: 'Community Midwife', aliases: ['Community Midwife', 'Community Midwives', 'Community Midwifes'], types: [95] },
        { key: 'specialist-paramedic', label: 'Specialist Paramedic RRV', aliases: ['Specialist Paramedic RRV', 'Specialist Paramedic RRVs'], types: [96] },
        { key: 'rescue-dog', label: 'Rescue Dog', aliases: ['Rescue Dog', 'Rescue Dogs'], types: [101, 102] },
        { key: 'mountain-4x4', label: 'Mountain Rescue 4x4', aliases: ['Mountain Rescue 4x4', 'Mountain Rescue 4x4s'], types: [99] },
        { key: 'road-rail', label: 'Road Rail Unit', aliases: ['Road Rail Unit', 'Road Rail Units'], types: [107] },
        { key: 'eiu', label: 'EIU', aliases: ['EIU', 'EIUs'], types: [108] },
        { key: 'eod-commander', label: 'EOD Commander', aliases: ['EOD Commander', 'EOD Commanders'], types: [109] },
        { key: 'eod-response', label: 'EOD Response Vehicle', aliases: ['EOD Response Vehicle', 'EOD Response Vehicles'], types: [110] },
        { key: 'eod-medium', label: 'EOD Medium Equipment Van', aliases: ['EOD Medium Equipment Van', 'EOD Medium Equipment Vans'], types: [111] },
        { key: 'eod-heavy', label: 'EOD Heavy Equipment Vehicle', aliases: ['EOD Heavy Equipment Vehicle', 'EOD Heavy Equipment Vehicles'], types: [112] },
        { key: 'marine-eod-response', label: 'Marine EOD Response Vehicle', aliases: ['Marine EOD Response Vehicle', 'Marine EOD Response Vehicles'], types: [113] },
        { key: 'marine-eod-equipment', label: 'Marine EOD Equipment Van', aliases: ['Marine EOD Equipment Van', 'Marine EOD Equipment Vans'], types: [114] },
        { key: 'firefighters', label: 'Firefighters', aliases: ['more firefighter', 'more firefighters', 'Firefighter', 'Firefighters'], group: 'staff', types: [0, 1, 2, 3, 4, 6, 7, 14, 15, 16, 17, 18, 23, 26, 35, 36, 37, 38, 39, 40] },
        { key: 'armed-personnel', label: 'Armed Response Personnel', aliases: ['Armed Response Personnel (In Armed Vehicles)', 'Armed Response Personnel'], group: 'staff', types: [13, 25, 52, 56, 82] },
        { key: 'police-officers', label: 'Police Officers', aliases: ['Police Officer', 'Police Officers'], group: 'staff', types: [8, 12, 13, 19, 24, 25, 51, 52, 53, 55, 56, 82, 116] },
        { key: 'paramedics', label: 'Paramedics', aliases: ['Paramedic', 'Paramedics'], group: 'staff', types: [5, 9, 20, 27, 28, 31, 34, 81, 83, 95, 96] },
        { key: 'search-technicians', label: 'Search Technicians', aliases: ['Search Technician', 'Search Technicians'], group: 'staff', types: [86, 87, 92, 93, 99, 101, 102] },
        { key: 'water-resource', label: 'Water', aliases: ['Water', 'litres of water', 'liters of water'], group: 'other', bar: 'water' },
        { key: 'foam-resource', label: 'Foam', aliases: ['Foam', 'litres of foam', 'liters of foam'], group: 'other', bar: 'foam' },
        { key: 'pump-resource', label: 'Pumping Capacity', aliases: ['l/min pumping process', 'l/min pumping capacity', 'Pumping Capacity'], group: 'other', bar: 'pump' }
    ].map(definition => Object.freeze({ group: 'vehicles', aliases: [], types: [], equipment: [], factors: {}, ...definition })));

    function missionRequirementsEscapeRegex(value) {
        return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function missionRequirementsNumber(value) {
        const digits = String(value ?? '').replace(/[^0-9-]/g, '');
        const number = Number.parseInt(digits, 10);
        return Number.isFinite(number) ? Math.max(0, number) : 0;
    }

    function missionRequirementsCleanRemaining(value) {
        return String(value || '')
            .replace(/\b(?:we\s+need|needed|required)\b\s*:*/giu, ' ')
            .replace(/\s*[,;]\s*(?=[,;]|$)/gu, ' ')
            .replace(/^(?:\s|[,;.])+|(?:\s|[,;.])+$/gu, '')
            .replace(/\s+/gu, ' ')
            .trim();
    }

    function missionRequirementsFindDefinitionMatch(text, definition) {
        const numberPattern = '(\\d{1,3}(?:[\\s,.]\\d{3})*|\\d+)';
        const aliases = Array.from(definition.aliases || []).sort((left, right) => right.length - left.length);
        for (const alias of aliases) {
            const labelPattern = missionRequirementsEscapeRegex(alias).replace(/\\\s+/gu, '\\s+');
            const before = new RegExp(`(^|[,;]\\s*)${numberPattern}\\s*x?\\s+(${labelPattern})(?=\\s*(?:[,;]|$))`, 'iu');
            const beforeMatch = before.exec(text);
            if (beforeMatch) return { match: beforeMatch[0], missing: missionRequirementsNumber(beforeMatch[2]), label: beforeMatch[3] };
            const after = new RegExp(`(^|[,;]\\s*)(${labelPattern})\\s*:\\s*${numberPattern}(?=\\s*(?:[,;]|$))`, 'iu');
            const afterMatch = after.exec(text);
            if (afterMatch) return { match: afterMatch[0], missing: missionRequirementsNumber(afterMatch[3]), label: afterMatch[2] };
        }
        return null;
    }

    function missionRequirementsParseText(rawText, group = 'vehicles') {
        let remaining = String(rawText || '').replace(/\s+/gu, ' ').trim();
        const requirements = [];
        const definitions = MISSION_REQUIREMENT_DEFINITIONS
            .filter(definition => definition.group === group)
            .sort((left, right) => Math.max(...right.aliases.map(alias => alias.length), 0) - Math.max(...left.aliases.map(alias => alias.length), 0));
        for (const definition of definitions) {
            const found = missionRequirementsFindDefinitionMatch(remaining, definition);
            if (!found || found.missing <= 0) continue;
            requirements.push({
                key: definition.key,
                requirement: definition.label || found.label,
                missing: found.missing,
                group,
                definition
            });
            remaining = remaining.replace(found.match, ' ');
        }
        return { requirements, remaining: missionRequirementsCleanRemaining(remaining) };
    }

    function missionRequirementsParseSource(source) {
        if (!source) return { requirements: [], unresolved: [] };
        const requirements = [];
        const unresolved = [];
        const groupElements = Array.from(source.querySelectorAll?.('[data-requirement-type]') || []);
        const parseGroupElement = element => {
            const rawType = String(element.getAttribute('data-requirement-type') || 'vehicles').toLowerCase();
            const group = rawType === 'personnel' || rawType === 'staff' ? 'staff' : rawType === 'other' ? 'other' : 'vehicles';
            const heading = String(element.querySelector?.('b')?.textContent || '').trim();
            const raw = String(element.textContent || '').replace(heading, ' ').replace(/\s+/gu, ' ').trim();
            const parsed = missionRequirementsParseText(raw, group);
            requirements.push(...parsed.requirements);
            if (parsed.remaining) unresolved.push({ group, text: parsed.remaining });
        };
        if (groupElements.length) groupElements.forEach(parseGroupElement);
        else {
            const raw = String(source.textContent || '').replace(/\s+/gu, ' ').trim();
            const parsed = missionRequirementsParseText(raw, 'vehicles');
            requirements.push(...parsed.requirements);
            if (parsed.remaining) unresolved.push({ group: 'vehicles', text: parsed.remaining });
        }
        return { requirements, unresolved };
    }

    function missionRequirementsVehicleType(element) {
        if (!element) return -1;
        const direct = element.getAttribute?.('vehicle_type_id') ?? element.dataset?.vehicleTypeId ?? element.dataset?.vehicle_type_id;
        const directNumber = Number.parseInt(direct, 10);
        if (Number.isFinite(directNumber) && directNumber >= 0) return directNumber;
        const descendant = element.querySelector?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id]');
        if (!descendant || descendant === element) return -1;
        return missionRequirementsVehicleType(descendant);
    }

    function missionRequirementsVehicleId(element) {
        const raw = element?.value ?? element?.getAttribute?.('value') ?? element?.dataset?.vehicleId ?? element?.dataset?.vehicle_id;
        const value = Number.parseInt(raw, 10);
        return Number.isFinite(value) && value >= 0 ? value : -1;
    }

    function missionRequirementsEquipmentTypes(element) {
        const values = new Set();
        const add = raw => String(raw || '').split(',').map(value => value.trim().toLowerCase()).filter(Boolean).forEach(value => values.add(value));
        add(element?.dataset?.equipmentTypes);
        add(element?.getAttribute?.('data-equipment-types'));
        element?.querySelectorAll?.('[data-equipment-type], [data-equipment-types]').forEach(node => {
            add(node.getAttribute('data-equipment-type'));
            add(node.getAttribute('data-equipment-types'));
        });
        return values;
    }

    function missionRequirementsStaffCapacity(element) {
        const row = element?.closest?.('tr') || element;
        const nodes = [element, row, row?.querySelector?.('[data-personnel-count], [data-current-personnel], [data-max-personnel]'), row?.querySelector?.('td:nth-of-type(5)[sortvalue]')].filter(Boolean);
        const attributes = ['data-personnel-count', 'data-current-personnel', 'data-max-personnel', 'data-personnel', 'data-staff', 'data-crew', 'sortvalue'];
        for (const node of nodes) {
            for (const attribute of attributes) {
                const raw = node.getAttribute?.(attribute);
                if (raw === null || raw === undefined || raw === '') continue;
                const value = missionRequirementsNumber(raw);
                if (value > 0) return value;
            }
        }
        return null;
    }

    function missionRequirementsCollectUnits(candidate, mode) {
        const root = candidate?.root?.isConnected ? candidate.root : candidate?.mount;
        if (!root?.querySelectorAll) return [];
        const selector = mode === 'selected'
            ? '#vehicle_show_table_body_all .vehicle_checkbox:checked, #occupied .vehicle_checkbox:checked, .vehicle_checkbox[vehicle_type_id]:checked'
            : '#mission_vehicle_driving tbody tr';
        const elements = Array.from(new Set(Array.from(root.querySelectorAll(selector))));
        const units = elements.map(element => {
            const vehicleElement = mode === 'selected' ? element : (element.querySelector?.('[vehicle_type_id]') || element);
            const vehicleId = missionRequirementsVehicleId(vehicleElement);
            const tractiveId = Number.parseInt(vehicleElement.getAttribute?.('tractive_vehicle_id') ?? vehicleElement.dataset?.tractiveVehicleId ?? '-1', 10);
            return {
                element,
                vehicleElement,
                typeId: missionRequirementsVehicleType(vehicleElement),
                vehicleId,
                tractiveId: Number.isFinite(tractiveId) ? tractiveId : -1,
                equipment: missionRequirementsEquipmentTypes(element),
                staff: missionRequirementsStaffCapacity(element),
                contributionKey: vehicleId >= 0 ? `vehicle:${vehicleId}` : `element:${elements.indexOf(element)}`
            };
        });
        const pairKeys = new Map();
        units.forEach(unit => {
            if (unit.vehicleId < 0 || unit.tractiveId < 0) return;
            const pair = [unit.vehicleId, unit.tractiveId].sort((a, b) => a - b);
            const key = `pair:${pair[0]}:${pair[1]}`;
            pairKeys.set(unit.vehicleId, key);
            pairKeys.set(unit.tractiveId, key);
        });
        units.forEach(unit => {
            if (unit.vehicleId >= 0 && pairKeys.has(unit.vehicleId)) unit.contributionKey = pairKeys.get(unit.vehicleId);
        });
        return units;
    }

    function missionRequirementsUnitContribution(requirement, unit) {
        const definition = requirement.definition || {};
        const typeEligible = Array.from(definition.types || []).includes(unit.typeId);
        const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase()));
        if (!typeEligible && !equipmentEligible) return { eligible: false, value: 0, known: true };
        if (requirement.group === 'staff') {
            return unit.staff === null
                ? { eligible: true, value: 0, known: false }
                : { eligible: true, value: Math.max(0, unit.staff), known: true };
        }
        const factor = Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1);
        return { eligible: true, value: Number.isFinite(factor) && factor > 0 ? factor : 1, known: true };
    }

    function missionRequirementsAggregate(requirement, units) {
        const contributions = new Map();
        let known = true;
        for (const unit of units) {
            const contribution = missionRequirementsUnitContribution(requirement, unit);
            if (!contribution.eligible) continue;
            known = known && contribution.known;
            contributions.set(unit.contributionKey, Math.max(contributions.get(unit.contributionKey) || 0, contribution.value));
        }
        return { value: Array.from(contributions.values()).reduce((total, value) => total + value, 0), known };
    }

    function missionRequirementsProgressValue(candidate, bar, metric) {
        const root = candidate?.root?.isConnected ? candidate.root : candidate?.mount;
        const holder = root?.querySelector?.(`[id^="mission_${bar}_holder"]`);
        if (!holder) return null;
        const node = holder.querySelector?.(`[class*="mission_${bar}_bar_${metric}_"], [class*="mission_water_bar_${metric}_"]`);
        return node ? missionRequirementsNumber(node.textContent) : null;
    }

    function missionRequirementsResolve(candidate, parsed) {
        const selectedUnits = missionRequirementsCollectUnits(candidate, 'selected');
        const enRouteUnits = missionRequirementsCollectUnits(candidate, 'enroute');
        return parsed.requirements.map(requirement => {
            let selected;
            let enRoute;
            if (requirement.definition?.bar) {
                selected = { value: missionRequirementsProgressValue(candidate, requirement.definition.bar, 'selected') ?? 0, known: true };
                enRoute = { value: missionRequirementsProgressValue(candidate, requirement.definition.bar, 'driving') ?? 0, known: true };
            } else {
                selected = missionRequirementsAggregate(requirement, selectedUnits);
                enRoute = missionRequirementsAggregate(requirement, enRouteUnits);
            }
            const stillNeeded = Math.max(0, requirement.missing - enRoute.value);
            const covered = selected.known && selected.value >= stillNeeded;
            const partial = !covered && (selected.value > 0 || enRoute.value > 0);
            return { ...requirement, selected: selected.value, selectedKnown: selected.known, enRoute: enRoute.value, stillNeeded, covered, partial };
        });
    }

    function missionRequirementsOverallState(rows, unresolved) {
        if (rows.some(row => !row.covered && row.selectedKnown)) return 'danger';
        if (rows.some(row => !row.selectedKnown) || unresolved.length) return 'warning';
        return rows.length ? 'success' : 'warning';
    }

    function missionRequirementsLssmActive(candidate, source) {
        if (!source) return false;
        try {
            if (source.matches?.('.alert-missing-vehicles, [class*="alert-missing-vehicles"]')) return true;
            if (source.querySelector?.('.alert-missing-vehicles, table.table-striped.table-condensed')) return true;
            return Boolean(candidate?.root?.querySelector?.('.alert-missing-vehicles[data-raw-html], .alert-missing-vehicles table'));
        } catch (err) {
            return false;
        }
    }

    function missionRequirementsSourceForCandidate(candidate) {
        for (const scope of [candidate?.root, candidate?.mount]) {
            try {
                if (scope?.matches?.('#missing_text')) return scope;
                const source = scope?.querySelector?.('#missing_text');
                if (source) return source;
            } catch (err) {}
        }
        return null;
    }

    function missionRequirementsDocumentCss() {
        return `
            #${SCRIPT.missionRequirementsPanelId}{--mcms-req-accent:#6fd7ff;--mcms-req-surface:#101820;--mcms-req-surface-2:#17242f;--mcms-req-border:rgba(111,215,255,.38);--mcms-req-text:#eef9ff;--mcms-req-muted:#a9bdc8;display:block!important;position:relative!important;clear:both!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important;margin:0 0 10px!important;border:1px solid var(--mcms-req-border)!important;border-left:4px solid var(--mcms-req-state,#ef5350)!important;border-radius:10px!important;background:linear-gradient(145deg,var(--mcms-req-surface),var(--mcms-req-surface-2))!important;color:var(--mcms-req-text)!important;box-shadow:0 7px 18px rgba(0,0,0,.22)!important;overflow:hidden!important;font-family:Arial,Helvetica,sans-serif!important;z-index:auto!important}
            #${SCRIPT.missionRequirementsPanelId}[data-state="danger"]{--mcms-req-state:#ef5350}
            #${SCRIPT.missionRequirementsPanelId}[data-state="warning"]{--mcms-req-state:#ffb74d}
            #${SCRIPT.missionRequirementsPanelId}[data-state="success"]{--mcms-req-state:#4dd68a}
            #${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="cyberpunk"]{--mcms-req-accent:#00f0ff;--mcms-req-surface:#080b12;--mcms-req-surface-2:#111725;--mcms-req-border:rgba(0,240,255,.50);border-radius:2px!important}
            #${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="fallout4"]{--mcms-req-accent:#c8ff8b;--mcms-req-surface:#071008;--mcms-req-surface-2:#172817;--mcms-req-border:rgba(164,234,101,.48);--mcms-req-text:#d8ffad;--mcms-req-muted:#91b978}
            #${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="umbrella"]{--mcms-req-accent:#f4f6f8;--mcms-req-surface:#101114;--mcms-req-surface-2:#1c1d21;--mcms-req-border:rgba(214,39,50,.55)}
            #${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="factorio"]{--mcms-req-accent:#f0a44a;--mcms-req-surface:#171717;--mcms-req-surface-2:#2a2824;--mcms-req-border:rgba(240,164,74,.48);border-radius:4px!important}
            #${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="bond007"]{--mcms-req-accent:#d9bd77;--mcms-req-surface:#090a0c;--mcms-req-surface-2:#17191e;--mcms-req-border:rgba(217,189,119,.45)}
            #${SCRIPT.missionRequirementsPanelId}[data-mcms-theme="hyrule"]{--mcms-req-accent:#6ee6d6;--mcms-req-surface:#10231d;--mcms-req-surface-2:#17352b;--mcms-req-border:rgba(217,183,90,.48)}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-head{display:flex!important;align-items:center!important;gap:10px!important;min-width:0!important;padding:9px 12px!important;border-bottom:1px solid rgba(255,255,255,.10)!important;background:rgba(0,0,0,.16)!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-title{display:flex!important;align-items:center!important;gap:8px!important;min-width:0!important;flex:1 1 auto!important;font-size:15px!important;line-height:1.2!important;font-weight:900!important;letter-spacing:.15px!important;color:var(--mcms-req-text)!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-title i{display:block!important;width:8px!important;height:8px!important;flex:0 0 8px!important;border-radius:50%!important;background:var(--mcms-req-state)!important;box-shadow:0 0 10px color-mix(in srgb,var(--mcms-req-state) 65%,transparent)!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-summary{flex:0 1 auto!important;min-width:0!important;max-width:48%!important;padding:4px 8px!important;border:1px solid color-mix(in srgb,var(--mcms-req-state) 52%,transparent)!important;border-radius:999px!important;color:var(--mcms-req-text)!important;background:color-mix(in srgb,var(--mcms-req-state) 15%,transparent)!important;font-size:11px!important;line-height:1.2!important;font-weight:800!important;white-space:normal!important;text-align:center!important;overflow-wrap:anywhere!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-collapse{display:inline-flex!important;align-items:center!important;justify-content:center!important;flex:0 0 30px!important;width:30px!important;height:28px!important;padding:0!important;border:1px solid rgba(255,255,255,.18)!important;border-radius:7px!important;background:rgba(255,255,255,.07)!important;color:var(--mcms-req-text)!important;font:900 14px/1 Arial,sans-serif!important;cursor:pointer!important}
            #${SCRIPT.missionRequirementsPanelId}.mcms-collapsed .mcms-req-body{display:none!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-body{max-height:min(42vh,430px)!important;overflow:auto!important;overscroll-behavior:contain!important}
            #${SCRIPT.missionRequirementsPanelId} table{width:100%!important;max-width:100%!important;border-collapse:separate!important;border-spacing:0!important;table-layout:fixed!important;margin:0!important;background:transparent!important;color:inherit!important}
            #${SCRIPT.missionRequirementsPanelId} col.mcms-req-name-col{width:52%!important}
            #${SCRIPT.missionRequirementsPanelId} col.mcms-req-number-col{width:12%!important}
            #${SCRIPT.missionRequirementsPanelId} thead th{position:sticky!important;top:0!important;z-index:2!important;padding:7px 8px!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.12)!important;background:color-mix(in srgb,var(--mcms-req-surface-2) 94%,black)!important;color:var(--mcms-req-muted)!important;font-size:10.5px!important;line-height:1.2!important;font-weight:900!important;letter-spacing:.2px!important;text-transform:uppercase!important;white-space:normal!important;text-align:center!important;overflow-wrap:anywhere!important}
            #${SCRIPT.missionRequirementsPanelId} thead th:first-child{text-align:left!important}
            #${SCRIPT.missionRequirementsPanelId} tbody td{box-sizing:border-box!important;padding:8px!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.075)!important;background:transparent!important;color:var(--mcms-req-text)!important;font-size:13px!important;line-height:1.25!important;vertical-align:middle!important}
            #${SCRIPT.missionRequirementsPanelId} tbody tr:last-child td{border-bottom:0!important}
            #${SCRIPT.missionRequirementsPanelId} tbody td:first-child{font-weight:800!important;text-align:left!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important}
            #${SCRIPT.missionRequirementsPanelId} tbody td:not(:first-child){font-variant-numeric:tabular-nums!important;text-align:center!important;white-space:nowrap!important;font-weight:750!important}
            #${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="covered"] td{background:rgba(77,214,138,.07)!important}
            #${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="covered"] td:first-child{color:#9bf2bf!important}
            #${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="partial"] td:first-child{color:#ffd18a!important}
            #${SCRIPT.missionRequirementsPanelId} tbody tr[data-row-state="unresolved"] td{background:rgba(255,183,77,.06)!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-still{font-size:14px!important;font-weight:950!important;color:var(--mcms-req-state)!important}
            #${SCRIPT.missionRequirementsPanelId} tr[data-row-state="covered"] .mcms-req-still{color:#7ce4a8!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown{display:grid!important;gap:5px!important;padding:8px 12px 10px!important;border-top:1px solid rgba(255,183,77,.22)!important;background:rgba(255,183,77,.06)!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown b{color:#ffd18a!important;font-size:11px!important;text-transform:uppercase!important;letter-spacing:.25px!important}
            #${SCRIPT.missionRequirementsPanelId} .mcms-req-unknown span{color:var(--mcms-req-text)!important;font-size:12px!important;line-height:1.35!important;overflow-wrap:anywhere!important}
            @media(max-width:767px){
                #${SCRIPT.missionRequirementsPanelId}{margin-bottom:8px!important;border-radius:8px!important}
                #${SCRIPT.missionRequirementsPanelId} .mcms-req-head{padding:8px!important;gap:7px!important}
                #${SCRIPT.missionRequirementsPanelId} .mcms-req-title{font-size:13px!important}
                #${SCRIPT.missionRequirementsPanelId} .mcms-req-summary{max-width:44%!important;font-size:9.5px!important;padding:3px 6px!important}
                #${SCRIPT.missionRequirementsPanelId} .mcms-req-body{max-height:min(48vh,470px)!important;padding:7px!important}
                #${SCRIPT.missionRequirementsPanelId} table,#${SCRIPT.missionRequirementsPanelId} tbody{display:block!important;width:100%!important}
                #${SCRIPT.missionRequirementsPanelId} colgroup,#${SCRIPT.missionRequirementsPanelId} thead{display:none!important}
                #${SCRIPT.missionRequirementsPanelId} tbody tr{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:0!important;margin:0 0 7px!important;border:1px solid rgba(255,255,255,.11)!important;border-left:3px solid var(--mcms-req-state)!important;border-radius:7px!important;background:rgba(255,255,255,.035)!important;overflow:hidden!important}
                #${SCRIPT.missionRequirementsPanelId} tbody tr:last-child{margin-bottom:0!important}
                #${SCRIPT.missionRequirementsPanelId} tbody td{display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;min-width:0!important;min-height:44px!important;padding:6px 4px!important;border:0!important;border-right:1px solid rgba(255,255,255,.07)!important;font-size:12px!important;white-space:normal!important}
                #${SCRIPT.missionRequirementsPanelId} tbody td:last-child{border-right:0!important}
                #${SCRIPT.missionRequirementsPanelId} tbody td:first-child{grid-column:1/-1!important;display:block!important;min-height:0!important;padding:8px!important;border-right:0!important;border-bottom:1px solid rgba(255,255,255,.09)!important;font-size:13px!important;text-align:left!important}
                #${SCRIPT.missionRequirementsPanelId} tbody td:not(:first-child)::before{content:attr(data-label)!important;display:block!important;margin-bottom:2px!important;color:var(--mcms-req-muted)!important;font-size:8.5px!important;line-height:1.05!important;font-weight:850!important;letter-spacing:.15px!important;text-transform:uppercase!important;text-align:center!important;white-space:normal!important}
            }
        `;
    }

    function ensureMissionRequirementsDocumentStyle(doc) {
        if (!doc?.createElement) return;
        const requirementsDocumentStyleId = SCRIPT.missionRequirementsDocumentStyleId;
        let style = doc.getElementById?.(requirementsDocumentStyleId);
        if (!style) {
            style = doc.createElement('style');
            style.id = requirementsDocumentStyleId;
            (doc.head || doc.documentElement)?.appendChild(style);
        }
        const css = missionRequirementsDocumentCss();
        if (style.textContent !== css) style.textContent = css;
    }

    function missionRequirementsHideSource(source) {
        if (!source || source.dataset.mcmsRequirementsSourceHidden === '1') return;
        source.dataset.mcmsRequirementsSourceHidden = '1';
        source.dataset.mcmsRequirementsOriginalDisplay = source.style.display || '';
        source.style.setProperty('display', 'none', 'important');
    }

    function missionRequirementsRestoreSource(source) {
        if (!source || source.dataset.mcmsRequirementsSourceHidden !== '1') return;
        const original = source.dataset.mcmsRequirementsOriginalDisplay || '';
        source.style.removeProperty('display');
        if (original) source.style.display = original;
        delete source.dataset.mcmsRequirementsSourceHidden;
        delete source.dataset.mcmsRequirementsOriginalDisplay;
    }

    function missionRequirementsPanelHtml(rows, unresolved) {
        const outstanding = rows.filter(row => !row.covered).length;
        const stateName = missionRequirementsOverallState(rows, unresolved);
        const summary = stateName === 'success'
            ? 'All requirements covered'
            : stateName === 'warning' && !outstanding
                ? 'Check unresolved requirement'
                : `${outstanding} requirement${outstanding === 1 ? '' : 's'} outstanding`;
        const rowHtml = rows.map(row => {
            const selectedText = row.selectedKnown ? row.selected.toLocaleString('en-GB') : '?';
            const rowState = !row.selectedKnown ? 'unresolved' : row.covered ? 'covered' : row.partial ? 'partial' : 'open';
            const prefix = row.covered ? '✓ ' : '';
            return `<tr data-row-state="${rowState}"><td>${escapeHtml(prefix + row.requirement)}</td><td data-label="Missing">${row.missing.toLocaleString('en-GB')}</td><td data-label="En route">${row.enRoute.toLocaleString('en-GB')}</td><td class="mcms-req-still" data-label="Still needed">${row.stillNeeded.toLocaleString('en-GB')}</td><td data-label="Selected">${escapeHtml(selectedText)}</td></tr>`;
        }).join('');
        const unknownHtml = unresolved.length
            ? `<div class="mcms-req-unknown"><b>Unresolved MissionChief requirement</b>${unresolved.map(item => `<span>${escapeHtml(item.text)}</span>`).join('')}</div>`
            : '';
        return {
            stateName,
            html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${escapeHtml(summary)}</span><button type="button" class="mcms-req-collapse" data-mcms-requirements-collapse aria-label="Collapse mission requirements" aria-expanded="true">⌃</button></div><div class="mcms-req-body"><table aria-label="Live mission requirements"><colgroup><col class="mcms-req-name-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"></colgroup><thead><tr><th scope="col">Requirement</th><th scope="col">Missing</th><th scope="col">En route</th><th scope="col">Still needed</th><th scope="col">Selected</th></tr></thead><tbody>${rowHtml}</tbody></table>${unknownHtml}</div>`
        };
    }

    function missionRequirementsRenderRecord(record) {
        if (!record?.source?.isConnected || !record?.candidate?.mount?.isConnected) {
            scheduleMissionRequirementsScan(0);
            return;
        }
        if (missionRequirementsLssmActive(record.candidate, record.source)) {
            missionRequirementsRemoveRecord(record.source);
            return;
        }
        const parsed = missionRequirementsParseSource(record.source);
        if (!parsed.requirements.length && !parsed.unresolved.length) {
            missionRequirementsRemoveRecord(record.source);
            return;
        }
        const rows = missionRequirementsResolve(record.candidate, parsed);
        const presentation = missionRequirementsPanelHtml(rows, parsed.unresolved);
        record.panel.dataset.state = presentation.stateName;
        record.panel.dataset.mcmsTheme = state.uiTheme;
        setInnerHtmlIfChanged(record.panel, presentation.html);
        const collapse = record.panel.querySelector('[data-mcms-requirements-collapse]');
        if (collapse) {
            const expanded = !record.panel.classList.contains('mcms-collapsed');
            collapse.setAttribute('aria-expanded', String(expanded));
            collapse.setAttribute('aria-label', expanded ? 'Collapse mission requirements' : 'Expand mission requirements');
            collapse.textContent = expanded ? '⌃' : '⌄';
        }
    }

    function missionRequirementsScheduleRecord(record) {
        if (!record || record.frame || runtime.destroyed) return;
        record.frame = runtimeRequestAnimationFrame(() => {
            record.frame = null;
            missionRequirementsRenderRecord(record);
        });
    }

    function missionRequirementsMutationRelevant(record, mutation) {
        const panel = record?.panel;
        const target = mutation?.target;
        if (panel && (target === panel || target?.closest?.(`#${SCRIPT.missionRequirementsPanelId}`))) return false;
        const selector = '#missing_text, #mission_vehicle_driving, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-equipment-types], [data-equipment-type], [id^="mission_water_holder"], [id^="mission_foam_holder"], [id^="mission_pump_holder"]';
        return mutationTouchesSelector(mutation, selector);
    }

    function missionRequirementsEnsureRecord(candidate, source) {
        let record = missionRequirementsRecords.get(source);
        if (record?.panel?.isConnected) {
            record.candidate = candidate;
            missionRequirementsScheduleRecord(record);
            return record;
        }
        if (record) missionRequirementsRemoveRecord(source);
        const doc = source.ownerDocument || document;
        ensureMissionRequirementsDocumentStyle(doc);
        const panel = doc.createElement('section');
        panel.id = SCRIPT.missionRequirementsPanelId;
        panel.setAttribute('aria-label', 'Live mission requirements');
        panel.dataset.mcmsTheme = state.uiTheme;
        source.parentNode?.insertBefore(panel, source);
        missionRequirementsHideSource(source);
        record = { candidate, source, panel, observer: null, frame: null };
        panel.addEventListener('click', event => {
            const button = event.target?.closest?.('[data-mcms-requirements-collapse]');
            if (!button) return;
            const collapsed = panel.classList.toggle('mcms-collapsed');
            button.setAttribute('aria-expanded', String(!collapsed));
            button.setAttribute('aria-label', collapsed ? 'Expand mission requirements' : 'Collapse mission requirements');
            button.textContent = collapsed ? '⌄' : '⌃';
        });
        const observeRoot = candidate.root?.isConnected ? candidate.root : candidate.mount;
        const view = doc.defaultView || pageWindow;
        const MutationObserverCtor = view?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
        if (observeRoot && typeof MutationObserverCtor === 'function') {
            record.observer = runtimeTrackObserver(new MutationObserverCtor(mutations => {
                if (mutations.some(mutation => missionRequirementsMutationRelevant(record, mutation))) missionRequirementsScheduleRecord(record);
            }));
            record.observer.observe(observeRoot, {
                childList: true,
                subtree: true,
                characterData: true,
                attributes: true,
                attributeFilter: ['checked', 'class', 'style', 'vehicle_type_id', 'data-equipment-types', 'data-equipment-type', 'tractive_vehicle_id', 'sortvalue']
            });
        }
        missionRequirementsRecords.set(source, record);
        missionRequirementsScheduleRecord(record);
        return record;
    }

    function missionRequirementsRemoveRecord(source) {
        const record = missionRequirementsRecords.get(source);
        if (!record) {
            missionRequirementsRestoreSource(source);
            return;
        }
        if (record.frame) runtimeCancelAnimationFrame(record.frame);
        runtimeUntrackObserver(record.observer);
        try { record.panel?.remove(); } catch (err) {}
        missionRequirementsRestoreSource(record.source);
        missionRequirementsRecords.delete(source);
    }

    function clearMissionRequirementsPanels() {
        for (const source of Array.from(missionRequirementsRecords.keys())) missionRequirementsRemoveRecord(source);
        for (const context of transportSweepDocumentContexts()) {
            try {
                context.doc.querySelectorAll?.(`#${SCRIPT.missionRequirementsPanelId}`).forEach(panel => panel.remove());
                context.doc.querySelectorAll?.('[data-mcms-requirements-source-hidden="1"]').forEach(missionRequirementsRestoreSource);
            } catch (err) {}
        }
    }

    function scheduleMissionRequirementsScan(delay = 60) {
        runtimeClearTimeout(missionRequirementsScanTimer);
        missionRequirementsScanTimer = runtimeSetTimeout(() => {
            missionRequirementsScanTimer = null;
            scanMissionRequirementsWindows();
        }, Math.max(0, Number(delay) || 0));
    }

    function scanMissionRequirementsWindows() {
        if (!state.missionRequirements) {
            clearMissionRequirementsPanels();
            return;
        }
        const activeSources = new Set();
        for (const candidate of missionValueWindowCandidates()) {
            const source = missionRequirementsSourceForCandidate(candidate);
            if (!source || !source.isConnected) continue;
            if (missionRequirementsLssmActive(candidate, source)) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            const raw = String(source.textContent || '').trim();
            if (!raw) {
                missionRequirementsRemoveRecord(source);
                continue;
            }
            activeSources.add(source);
            missionRequirementsEnsureRecord(candidate, source);
        }
        for (const source of Array.from(missionRequirementsRecords.keys())) {
            if (!activeSources.has(source) || !source.isConnected) missionRequirementsRemoveRecord(source);
        }
    }

    function missionRequirementsScheduleDocumentRecords(doc) {
        for (const record of missionRequirementsRecords.values()) {
            if (record.source?.ownerDocument === doc) missionRequirementsScheduleRecord(record);
        }
    }

    function observeMissionRequirementsFrame(frame) {
        if (!frame || missionRequirementsObservedFrames.has(frame)) return;
        missionRequirementsObservedFrames.add(frame);
        const onLoad = () => scheduleMissionRequirementsScan(20);
        frame.addEventListener('load', onLoad);
        runtimeOnCleanup(() => frame.removeEventListener('load', onLoad));
    }

    function observeMissionRequirementsDocument(doc) {
        if (!doc) return;
        ensureMissionRequirementsDocumentStyle(doc);
        if (missionRequirementsObservedDocuments.has(doc)) return;
        missionRequirementsObservedDocuments.add(doc);
        try { doc.querySelectorAll('iframe, frame').forEach(observeMissionRequirementsFrame); } catch (err) {}
        runtimeListen(doc, 'change', event => {
            if (!event.target?.matches?.('.vehicle_checkbox, input[type="checkbox"][vehicle_type_id]')) return;
            missionRequirementsScheduleDocumentRecords(doc);
        }, true);
        const root = doc.documentElement || doc.body;
        if (!root) return;
        const activitySelector = '#missing_text, #mission_vehicle_driving, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-equipment-types], [id^="mission_water_holder"], [id^="mission_foam_holder"], [id^="mission_pump_holder"], #lightbox_box, #lightbox, .lightbox_content, .modal, [role="dialog"], .ui-dialog, iframe, frame';
        const view = doc.defaultView || pageWindow;
        const MutationObserverCtor = view?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
        const observer = runtimeTrackObserver(new MutationObserverCtor(mutations => {
            const relevant = mutations.some(mutation => {
                if (mutation.target?.closest?.(`#${SCRIPT.missionRequirementsPanelId}`)) return false;
                if (mutationTouchesSelector(mutation, activitySelector)) return true;
                return false;
            });
            if (!relevant) return;
            try { doc.querySelectorAll('iframe, frame').forEach(observeMissionRequirementsFrame); } catch (err) {}
            scheduleMissionRequirementsScan(35);
            missionRequirementsScheduleDocumentRecords(doc);
        }));
        observer.observe(root, { childList: true, subtree: true, characterData: true });
    }

    function installMissionRequirementsWindows() {
        if (!missionRequirementsFeatureInstalled) {
            missionRequirementsFeatureInstalled = true;
            runtimeOnCleanup(() => {
                runtimeClearTimeout(missionRequirementsScanTimer);
                missionRequirementsScanTimer = null;
                clearMissionRequirementsPanels();
                for (const context of transportSweepDocumentContexts()) {
                    try { context.doc.getElementById?.(SCRIPT.missionRequirementsDocumentStyleId)?.remove(); } catch (err) {}
                }
            });
        }
        for (const context of transportSweepDocumentContexts()) observeMissionRequirementsDocument(context.doc);
        scheduleMissionRequirementsScan(0);
        runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 180);
        runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 800);
    }
```
