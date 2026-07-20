# Issue #259 — LSSM Mission Requirements parity audit

## Pinned baselines

- Toolkit: `8619c79b794ad7241e0a37a0c91a6176daee7911` (v4.20.12)
- LSSM V.4: `4f731e1d6d009cbf2129530fb31d10177b21a52a` (4.7.12+20260720.0722)

## Confirmed source capabilities

- Nested `data-equipment-type` and `data-equipment-types` markers are already read from the unit and closest row.
- Water, foam and pumping definitions already carry MissionChief progress-bar keys.
- A MissionChief progress-bar reader already exists; integration and fixture coverage remain under audit.
- Explicit tractive/trailer IDs already share one contribution key.
- No LSSM `max_personnel_override` dependency exists.

## Equipment metadata

```javascript
s?.('a[href*="/vehicles/"]') ? scope : scope?.querySelector?.('a[href*="/vehicles/"]');
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

function missionRequirementsCapabilityLabel(value) { return String(value || '') .replace(/\u00a0/gu, ' ') .replace(/&/gu, ' and ') .replace(/\([^)]*\)/gu, ' ') .replace(/[^a-z0-9]+/giu, ' ') .replace(/\s+/gu, ' ') .trim() .toLowerCase(); } function missionRequirementsMetadataValues(element, kind = 'labels') { const values = new Set(); const add = raw => String(raw || '').split(/[,;|]/u).map(missionRequirementsCapabilityLabel).filter(Boolean).forEach(value => values.add(value)); const row = element?.closest?.('tr') || element; const scopes = Array.from(new Set([element, row].filter(Boolean))); const attributes = kind === 'training' ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name'] : ['data-mcms-custom-vehicle-category', 'data-custom-vehicle-category', 'data-vehicle-category', 'data-vehicle-type-name', 'data-vehicle-type']; for (const scope of scopes) { for (const attribute of attributes) add(scope?.getAttribute?.(attribute)); scope?.querySelectorAll?.(attributes.map(attribute => `[${attribute}]`).join(', ')).forEach(node => attributes.forEach(attribute => add(node.getAttribute?.(attribute)))); } if (kind === 'labels') { const typeCell = row?.querySelector?.('[data-column="vehicle-type"], [data-vehicle-type-name], td:nth-of-type(2)'); add(missionRequirementsElementText(typeCell)); const vehicleId = missionRequirementsVehicleId(element); const custom = vehicleId >= 0 && typeof customVehicleClassificationForId === 'function' ? customVehicleClassificationForId(vehicleId) : null; add(custom?.category); } return values; } function missionRequirementsDefinitionTokens(definition, property = 'aliases') { const raw = property === 'training' ? Array.from(d
```

## Personnel capacity

```javascript
kens.has(value)) return true; return false; } function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }

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
        const parseCrewText = cell => {
            const text = String(cell?.textContent || '').trim();
            const currentMaximum = text.match(/(\d[\d,.]*)\s*\/\s*(\d[\d,.]*)/u);
            if (currentMaximum) {
                const current = missionRequirementsNumber(currentMaximum[1]);
                return missionRequirementsCapacity(current, current, true);
            }
            const bounded = text.match(/(\d[\d,.]*)\s*(?:-|–|to)\s*(\d[\d,.]*)/iu);
            if (bounded) return missionRequirementsCapacity(missionRequirementsNumber(bounded[1]), missionRequirementsNumber(bounded[2]), false);
            return null;
        };
        const semanticTextCapacity = parseCrewText(crewCell);
        if (semanticTextCapacity) return semanticTextCapacity;
        for (const cell of Array.from(row?.querySelectorAll?.('td, th') || [])) {
            const capacity = parseCrewText(cell);
            if (capacity) return capacity;
        }
        if (crewCell) {
            const visible = missionRequirementsOptionalNumber(String(crewCell.textContent || '').trim());
            if (visible !== null) return missionRequirementsCapacity(visible, visible, true);
            const sortValue = missionRequirementsOptionalNumber(crewCell.getAttribute?.('sortvalue'));
            if (sortValue !== null) return missionRequirementsCapacity(sortValue, sortValue, true);
        }
        return null;
    } function missionRequirementsOperationalSelectors(mode) { if (mode === 'selected') return ['#vehicle_show_table_body_all .vehicle_checkbox:checked, #occupied .vehicle_checkbox:checked, .vehicle_checkbox:checked']; if (mode === 'onsite') return ['#mission_vehicle_at_mission tbody tr', 'tbody#mission_vehicle_at_mission > tr', '#mission_vehicle_at_mission > tr', '[data-mcms-vehicle-state="onsite"]']; return ['#mission_vehicle_driving tbody tr', 'tbody#mission_vehicle_driving > tr', '#mission_vehicle_driving > tr', '[data-mcms-vehicle-state="responding"]']; }
function missionRequirementsOperationalWindowScopes(candidate, context = missionRequirementsPatientContext(candidate)) { const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog'; const scopes = []; const addChain = origin => { let current = origin?.closest?.(windowSelector) || null; while (current && !scopes.includes(current)) { scopes.push(current); const parent = current.parentElement || current.parentNode; current = parent?.closest?.(windowSelector) || null; } }; [candidate?.root, candidate?.mount, candidate?.source, missionRequirementsCandidateRoot(candidate), context?.activeWindow].forEach(addChain); if (context?.activeWindow && !scopes.includes(context.activeWindow)) scopes.unshift(context.activeWindow); return scopes; }
function missionRequirementsOperationalCanonicalStateContainer(element, mode) {
        if (mode === 'selected') return null;
        const row = element?.matches?.('tr') ? element : element?.closest?.('tr') || element;
        if (!row) return null;
        const selectors = mode === 'onsite'
            ? ['#mission_vehicle_at_mission', 'tbody#mission_vehicle_at_mission']
            : ['#mission_vehicle_driving', 'tbody#mission_vehicle_driving'];
        for (const selector of selectors) {
            if (row.matches?.(selector)) return row;
            const container = row.closest?.(selector);
            if (container) return container;
        }
        return null;
    }

    function missionRequirementsOperationalElementActive(element, candidate, context = missionRequirementsPatientContext(candidate), mode = '') {
        if (!element || element.isConnected === false) return false;
        if (mode === 'selected' && typeof element.checked === 'boolean' && !element.checked) return false;
        const row = element.matches?.('tr') ? element : element.closest?.('tr') || element;
        const expectedMission = missionRequirementsMissionIdentity(candidate, candidate?.source);
        const canonicalContainer = missionRequirementsOperationalCanonicalStateContainer(row, mode);
        const candidateRoot = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount;
        const canonicalId = mode === 'onsite' ? 'mission_vehicle_at_mission' : 'mission_vehicle_driving';
        const documentCanonical = mode === 'selected' ? null : context?.doc?.getElementById?.(canonicalId);
        const pathname = String(context?.doc?.defaultView?.location?.pathname || '');
        const pathMission = missionRequirementsOptionalNumber(pathname.match(/\/missions\/(\d+)/u)?.[1]);
        const canonicalOwned = Boolean(canonicalContainer && (
            context?.activeWindow?.contains?.(row)
            || candidateRoot?.contains?.(row)
            || candidate?.root?.contains?.(row)
            || candidate?.mount?.contains?.(row)
            || (
                expectedMission > 0
                && pathMission === expectedMission
                && documentCanonical
                && (documentCanonical === canonicalContainer || documentCanonical.contains?.(row))
            )
        ));
        if (mode !== 'selected' && !canonicalOwned && !isVisible(element)) return false;
        if (context.
```

## Unit collection and tractive pairing

```javascript
ent]');
        if (expectedMission > 0 && missionRoot) {
            const actualMission = missionRequirementsMissionIdentity({ root: missionRoot, mount: missionRoot }, null);
            if (actualMission > 0 && actualMission !== expectedMission) return false;
        }
        return true;
    }
function missionRequirementsCollectUnits(candidate, mode) { const root = candidate?.root; const context = missionRequirementsPatientContext(candidate); const doc = context.doc || candidate?.source?.ownerDocument || root?.ownerDocument; if (!root?.querySelectorAll && !doc?.querySelectorAll) return []; const selectors = missionRequirementsOperationalSelectors(mode); const windowScopes = missionRequirementsOperationalWindowScopes(candidate, context); const anchorSelector = mode === 'selected' ? '#vehicle_show_table_body_all, #occupied, .vehicle_checkbox' : mode === 'onsite' ? '#mission_vehicle_at_mission, [data-mcms-vehicle-state="onsite"]' : '#mission_vehicle_driving, [data-mcms-vehicle-state="responding"]'; let activeWindow = context.activeWindow || null; for (const scope of windowScopes) { if (scope?.querySelector?.(anchorSelector)) { activeWindow = scope; break; } } const operationalContext = { ...context, activeWindow }; const elements = []; const seenElements = new Set(); const localScopes = Array.from(new Set([root, candidate?.mount, activeWindow, ...windowScopes].filter(scope => scope?.querySelectorAll))); const search = scope => { for (const selector of selectors) { for (const element of Array.from(scope?.querySelectorAll?.(selector) || [])) { if (seenElements.has(element) || !missionRequirementsOperationalElementActive(element, candidate, operationalContext, mode)) continue; seenElements.add(element); elements.push(element); } } }; localScopes.forEach(search); if (!elements.length && doc?.querySelectorAll && !localScopes.includes(doc)) search(doc); const units = new Map(); elements.forEach((element, index) => { const row = element.matches?.('tr') ? element : element.closest?.('tr'); const vehicleElement = mode === 'selected' ? element : (element.querySelector?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-vehicle-id], a[href*="/vehicles/"]') || element); const typeId = missionRequirementsVehicleType(vehicleElement); const vehicleId = missionRequirementsVehicleId(vehicleElement); const tractiveId = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('tractive_vehicle_id') ?? vehicleElement?.getAttribute?.('data-tractive-vehicle-id') ?? row?.getAttribute?.('tractive_vehicle_id') ?? row?.getAttribute?.('data-tractive-vehicle-id') ?? row?.dataset?.tractiveVehicleId); const trailerId = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('trailer_id') ?? vehicleElement?.getAttribute?.('data-trailer-id') ?? row?.getAttribute?.('trailer_id') ?? row?.getAttribute?.('data-trailer-id') ?? row?.dataset?.trailerId); let contributionKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : `element:${index}`; const pairedId = tractiveId !== null && tractiveId >= 0 ? tractiveId : trailerId; if (vehicleId >= 0 && pairedId !== null && pairedId >= 0) contributionKey = `pair:${Math.min(vehicleId, pairedId)}:${Math.max(vehicleId, pairedId)}`; const identityKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : contributionKey; const labels = missionRequirementsMetadataValues(vehicleElement, 'labels'); const training = missionRequirementsMetadataValues(vehicleElement, 'training'); const knownDefinitionKeys = missionRequirementsKnownDefinitionKeys(labels); const rowText = missionRequirementsCapabilityLabel(`${row?.textContent || ''} ${row?.innerText || ''}`); if (rowText) { for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { const aliases = Array.from(definition?.training || []).map(missionRequirementsCapabilityLabel).filter(Boolean); if (!aliases.some(alias => rowText.includes(alias))) continue; aliases.forEach(alias => training.add(alias)); knownDefinitionKeys.add(definition.key); } } const unit = { typeId, vehicleId, tractiveId, equipment: missionRequirementsEquipmentTypes(vehicleElement), staff: missionRequirementsStaffCapacity(vehicleElement), labels, training, knownDefinitionKeys, contributionKey }; const existing = units.get(identityKey); if (!existing) { units.set(identityKey, unit); return; } if (existing.typeId < 0 && unit.typeId >= 0) existing.typeId = unit.typeId; for (const equipment of unit.equipment) existing.equipment.add(equipment); for (const label of unit.labels) existing.labels.add(label); for (const qualification of unit.training) existing.training.add(qualification); for (const key of unit.knownDefinitionKeys) existing.knownDefinitionKeys.add(key); if ((!existing.staff || !existing.staff.known) && unit.staff?.known) existing.staff = unit.staff; if (existing.contributionKey.startsWith('element:') && !unit.contributionKey.startsWith('element:')) existing.contributionKey = unit.contributionKey; }); return Array.from(units.values()); }

    function missionRequirementsMissionTypeId(candidate) {
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

function missionRequirementsUnitContribution(requirement, unit) { const definition = requirement.definition || {}; const typeEligible = Array.from(definition.types || []).includes(unit.typeId); const equipmentEligible = Array.from(definition.equipment || []).some(equipment => unit.equipment.has(String(equipment).toLowerCase())); const labelEligible = unit.knownDefinitionKeys?.has?.(definition.key) || missionRequirementsDefinitionMatchesValues(definition, unit.labels); const trainingRequired = Array.from(definition.training || []).length > 0; const trainingEligible = trainingRequired && missionRequirementsDefinitionMatchesValues(definition, unit.training, 'training'); const eligible = requirement.group === 'staff' && trainingRequired ? trainingEligible : typeEligible || equipmentEligible || labelEligible; const classificationUnknown = requirement.group === 'staff' && trainingRequired ? Boolean(unit.staff && !unit.training?.size) : unit.typeId < 0 && !unit.knownDefinitionKeys?.size && !unit.equipment?.size; if (!eligible) return { eligible: false, unknown: classificationUnknown, capacity: missionRequirementsCapacity(0, classificationUnknown ? null : 0, !classificationUnknown) }; if (requirement.group === 'staff') { const capacity = unit.staff ? missionRequirementsCapacity(unit.staff.min ?? unit.staff.value ?? 0, unit.staff.max, unit.staff.known) : missionRequirementsCapacity(0, null, false); return { eligible: true, unknown: !capacity.known, capacity }; } const factor = Number(definition.factors?.[unit.typeId] ?? definition.factors?.[String(unit.typeId)] ?? 1); const value = Number.isFinite(factor) && factor > 0 ? factor : 1; return { eligible: true, unknown: false, capacity: missionRequirementsCapacity(value, value, true) }; }

function missionRequirementsAggregate(requirement, units) { const contributions = new Map(); let unresolvedClassification = false; for (const unit of units) { const contribution = missionRequirementsUnitContribution(requirement, unit); unresolvedClassification = unresolvedClassification || contribution.unknown === true; if (!contribution.eligible) continue; const capacity = contribution.capacity; const existing = contributions.get(unit.contributionKey); if (!existing) { contributions.set(unit.contributionKey, capacity); continue; } const pairMin = Math.max(existing.min, capacity.min); const pairMax = existing.max === null || capacity.max === null ? null : Math.max(existing.max, capacity.max); contributions.set(unit.contributionKey, missionRequirementsCapacity(pairMin, pairMax, existing.known && capacity.known && pairMax === pairMin)); } let min = 0; let max = 0; let exact = true; for (const capacity of contributions.values()) { min += capacity.min; if (max === null || capacity.max === null) max = null; else max += capacity.max; exact = exact && capacity.known; } if (unresolvedClassification) return missionRequirementsCapacity(min, null, false); return missionRequirementsCapacity(min, max, exact && max !== null && min === max); }

    function missionRequirementsProgressValue(candidate, bar, metric) {
        const root = candidate?.root?.isConnected ? candidate.root : candidate?.mount;
        const holder = root?.querySelector?.(`[id^="mission_${bar}_holder"]`);
        if (!holder) return null;
        const node = holder.querySelector?.(`[class*="mission_${bar}_bar_${metric}_"], [class*="mission_water_bar_${metric}_"]`);
        return node ? missionRequirementsNumber(node.textContent) : null;
    }

    functio
```

## Progress-bar reader

```javascript
ts) { const contributions = new Map(); let unresolvedClassification = false; for (const unit of units) { const contribution = missionRequirementsUnitContribution(requirement, unit); unresolvedClassification = unresolvedClassification || contribution.unknown === true; if (!contribution.eligible) continue; const capacity = contribution.capacity; const existing = contributions.get(unit.contributionKey); if (!existing) { contributions.set(unit.contributionKey, capacity); continue; } const pairMin = Math.max(existing.min, capacity.min); const pairMax = existing.max === null || capacity.max === null ? null : Math.max(existing.max, capacity.max); contributions.set(unit.contributionKey, missionRequirementsCapacity(pairMin, pairMax, existing.known && capacity.known && pairMax === pairMin)); } let min = 0; let max = 0; let exact = true; for (const capacity of contributions.values()) { min += capacity.min; if (max === null || capacity.max === null) max = null; else max += capacity.max; exact = exact && capacity.known; } if (unresolvedClassification) return missionRequirementsCapacity(min, null, false); return missionRequirementsCapacity(min, max, exact && max !== null && min === max); }

    function missionRequirementsProgressValue(candidate, bar, metric) {
        const root = candidate?.root?.isConnected ? candidate.root : candidate?.mount;
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
    const MISSION_REQUIREMENTS_CATALOGUE_STALE_MS = 7 * 24 * 60 * 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_RETRY_MS = 60 * 1000;
    const MISSION_REQUIREMENTS_CATALOGUE_CACHE_LIMIT = 96;
    const missionRequirementsCatalogueCache = new Map();

    function missionRequirementsCatalogueText(node) {
        return String(node?.textContent || node?.innerText || '').replace(/\s+/gu, ' ').trim();
    }

function missionRequirementsCatalogueDescriptor(candidate) { const context = missionRequirementsPatientContext(candidate); const scopes = Array.from(new Set([candidate?.root, candidate?.mount, context.activeWindow, context.doc].filter(scope => scope?.querySelectorAll))); const links = []; const seen = new Set(); for (const scope of scopes) { for (const link of Array.from(scope.querySelectorAll?.('a[href*="/einsaetze/"]') || [])) { if (seen.has(link)) continue; seen.add(link); links.push(link); } } links.sort((left, right) => Number(/Requirements\s+for\s+this\s+Mission/iu.test(missionRequirementsElementText(right))) - Number(/Requirements\s+for\s+this\s+Mission/iu.test(missionRequirementsElementText(left)))); const doc = candidate?.root?.ownerDocument || candidate?.mount?.ownerDocument || context.doc; const location = doc?.defaultView?.location || pageWindow.location || {}; const origin = location.origin || `${location.protocol || 'https:'}//${location.host || 'www.missionchief.co.uk'}`; let matched = null; for (const link of links) { const href = String(link.getAttribute?.('href') || link.href || ''); let parsed; try { parsed = new URL(href, origin); } catch (err) { continue; } const match = parsed.pathname.match(/^\/einsaetze\/(\d+)\/?$/iu); if (!match) continue; const parameters = new URLSearchParams(); for (const name of ['overlay_index', 'additive_overlays']) { for (const value of parsed.searchParams.getAll(name)) if (value !== '') parameters.append(name, value); } const query = parameters.toString(); matched = { id: Number(match[1]), overlayIndex: missionRequirementsOptionalNumber(parsed.searchParams.get('overlay_index')), additiveOverlays: parsed.searchParams.getAll('additive_overlays'), path: `${parsed.pathname}${query ? `?${query}` : ''}` }; break; } if (!matched) { const id = missionRequirementsMissionTypeId(candidate); if (id === null || id === undefined || !Number.isFinite(Number(id)) || Number(id) < 0) return null; matched = { id: Number(id), overlayIndex: null, additiveOverlays: [], path: `/einsaetze/${Number(id)}` }; } return { ...matched, origin, url: `${origin}${matched.path}`, key: `${origin}${matched.path}` }; }

    function missionRequirementsCatalogueRequirement(label, value) {
        const rawLabel = missionRequirementsCatalogueText({ textContent: label });
        const rawValue = missionRequirementsCatalogueText({ textContent: value });
        const quantityMatch = rawValue.match(/^\s*(\d+(?:[\s,.]\d{3})*)/u);
        const quantity = quantityMatch ? missionRequirementsNumber(quantityMatch[1]) : null;
        if (quantity === null) return null;
        const cleanedLabel = rawLabel
            .replace(/^(?:required|requirement\s+of|needed)\s+/iu, '')
            .replace(/\s*\([^)]*%[^)]*\)\s*$/u, '')
            .trim();
        if (!cleanedLabel) return null;
        const probabilityMatch = `${rawLabel} ${rawValue}`.match(/(\d+(?:\.\d+)?)\s*%/u);
        const probability = probabilityMatch ? Math.max(0, Math.min(100, Number(probabilityMatch[1]))) : 100;
        const sourceText = `${quantity} ${cleanedLabel}`;
        for (const group of ['vehicles', 'staff', 'other']) {
            const parsed = missionRequirementsParseText(sourceText, group);
            if (!parsed.requirements.length) continue;
            const requirement = parsed.requirements[0];
            return {
      
```

## Resolver integration

```javascript
& !String(unit.contributionKey).startsWith('element:')) keys.push(String(unit.contributionKey));
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

    function missionRequirementsResolve(candidate, parsed, catalogue = null) { const rawSelectedUnits = missionRequirementsCollectUnits(candidate, 'selected'); const rawRespondingUnits = missionRequirementsCollectUnits(candidate, 'responding'); const rawOnSiteUnits = missionRequirementsCollectUnits(candidate, 'onsite'); const buckets = missionRequirementsExclusiveUnitBuckets(rawSelectedUnits, rawRespondingUnits, rawOnSiteUnits); const catalogueByKey = new Map(Array.from(catalogue?.requirements || []).map(item => [item.key, item])); return parsed.requirements.map(requirement => { if (requirement.patientCondition === true) { const requiredValue = Math.max(0, Number(requirement.patientConditionRequired ?? requirement.patientRequired ?? requirement.missing) || 0); const fulfilledValue = Math.max(0, Number(requirement.patientConditionFulfilled) || 0); const fulfilledKnown = requirement.patientConditionFulfilledKnown === true; const zero = missionRequirementsCapacity(0, 0, true); const fulfilled = fulfilledKnown ? missionRequirementsCapacity(fulfilledValue, fulfilledValue, true) : missionRequirementsCapacity(fulfilledValue, null, false); const row = missionRequirementsCoverageRow(requirement, zero, zero, fulfilled, missionRequirementsCapacity(requiredValue, requiredValue, true)); if (!fulfilledKnown && !row.covered) { row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } return { ...row, conditionKnown: true, conditionMatched: true, requirementAuthority: 'patient-details' }; } if (requirement.definition?.countable === false) return missionRequirementsUnknownCoverageRow(requirement); const condition = missionRequirementsDefinitionCondition(requirement.definition, candidate); if (condition !== true) { const unknown = missionRequirementsCapacity(0, null, false); const unresolvedRow = missionRequirementsCoverageRow(requirement, unknown, unknown, unknown, unknown); return { ...unresolvedRow, conditionKnown: condition !== null, conditionMatched: false, uncertain: true, definitelyOpen: false, coverageKnown: false }; } let selected; let responding; let onSite; if (requirement.definition?.bar) { const selectedValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'selected'); const respondingValue = missionRequirementsProgressValue(candidate, requirement.definition.bar, 'driving'); const onSiteMetrics = ['at_mission', 'on_site', 'onsite', 'arrived', 'actual']; const onSiteValue = onSiteMetrics.map(metric => missionRequirementsProgressValue(candidate, requirement.definition.bar, metric)).find(value => value !== null); selected = selectedValue === null ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(selectedValue, selectedValue, true); responding = respondingValue === null ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(respondingValue, respondingValue, true); onSite = onSiteValue === undefined ? missionRequirementsCapacity(0, null, false) : missionRequirementsCapacity(onSiteValue, onSiteValue, true); } else { selected = missionRequirementsAggregate(requirement, buckets.selected); responding = missionRequirementsAggregate(requirement, buckets.responding); onSite = missionRequirementsAggregate(requirement, buckets.onSite); } const catalogueRequirement = catalogueByKey.get(requirement.key); const baseline = missionRequirementsOptionalNumber(catalogueRequirement?.baseline ?? catalogueRequirement?.missing); const catalogueOnly = requirement.catalogueDerived === true && requirement.statedRequirement === false; const catalogueProbability = missionRequirementsOptionalNumber(requirement.catalogueProbability ?? catalogueRequirement?.probability) ?? 100; const patientKnown = requirement.patientDerived === true && requirement.patientCountKnown === true; const patientUnknown = requirement.patientDerived === true && requirement.patientCountKnown === false; const patientRequired = patientKnown ? Math.max(0, Number(requirement.patientRequired) || 0) : null; const hasStatedRequirement = requirement.statedRequirement !== false; if (baseline !== null && hasStatedRequirement) { const committed = Math.max(0, baseline - Math.max(0, Number(requirement.missing) || 0)); const operationalMin = onSite.min + responding.min; const operationalMax = onSite.max === null || responding.max === null ? null : onSite.max + responding.max; const inferredSelectedMin = operationalMax === null ? 0 : Math.max(0, committed - operationalMax); const inferredSelectedMax = Math.max(0, committed - operationalMin); if (inferredSelectedMax > selected.min) { const selectedMin = Math.max(selected.min, inferredSelectedMin); const selectedMax = selected.max === null ? inferredSelectedMax : Math.max(selected.max, inferredSelectedMax); selected = missionRequirementsCapacity(selectedMin, selectedMax, selectedMax !== null && selectedMin === selectedMax && onSite.known && responding.known); } } const statedRequiredMin = hasStatedRequirement ? Math.max(0, Number(requirement.missing) || 0) + onSite.min : 0; const statedRequiredMax = hasStatedRequirement ? (onSite.max === null ? null : Math.max(0, Number(requirement.missing) || 0) + onSite.max) : 0; const fixedMinimum = Math.max(patientRequired ?? 0, baseline ?? 0, statedRequiredMin); let required; if (patientUnknown) { required = missionRequirementsCapacity(Math.max(baseline ?? 0, statedRequiredMin), null, false); } else if (catalogueOnly && catalogueProbability < 100) { required = missionRequirementsCapacity(0, baseline ?? 0, false); } else if (patientKnown) { const possibleMaximum = statedRequiredMax === null ? null : Math.max(patientRequired, baseline ?? 0, statedRequiredMax); const exact = possibleMaximum !== null && possibleMaximum === fixedMinimum && (hasStatedRequirement ? onSite.known : true); required = missionRequirementsCapacity(fixedMinimum, possibleMaximum, exact); } else { const liveRequiredMin = statedRequiredMin; const liveRequiredMax = statedRequiredMax; required = baseline !== null ? missionRequirementsCapacity(Math.max(baseline, liveRequiredMin), Math.max(baseline, liveRequiredMin), true) : missionRequirementsCapacity(liveRequiredMin, liveRequiredMax, onSite.known && liveRequiredMax !== null && liveRequiredMin === liveRequiredMax); } const row = missionRequirementsCoverageRow(requirement, selected, responding, onSite, required); if (patientUnknown) { row.covered = false; row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } else if (catalogueOnly && catalogueProbability < 100 && !row.covered) { row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } const authorities = []; if (requirement.patientDerived) authorities.push('patients'); if (baseline !== null) authorities.push('mission-info'); if (hasStatedRequirement) authorities.push('live'); return { ...row, conditionKnown: true, conditionMatched: true, requirementAuthority: authorities.length ? authorities.join('+') : 'live-reconstructed' }; }); }

    function missionRequirementsOverallState(rows, unresolved) {
        if (rows.some(row => row.definitelyOpen)) return 'danger';
        if (rows.some(row => row.uncertain) || unresolved.length) return 'warning';
        return rows.length ? 'success' : 'warning';
    }

    function missionRequirementsLssmActive(candidate, source) {
        // MissionChief and LSSM both use the generic alert-missing-vehicles class.
        // Only explicit LSSM ownership metadata may suppress the Toolkit panel.
        const ownedSelector = [
        '.alert-missing-vehicles[data-raw-html]',
        '[data-lssm-enhanced-missing-vehicles]',
            '[data-lssm-module="extendedCallWindow.enhancedMissingVehicles"]'
        ].join(', ');
        const isLssmOwned = element => {
        if (!element) return false;
        const sharedAlert = Boolean(
            element.matches?.('.alert-missing-vehicles')
            || element.classList?.contains?.('alert-missing-vehicles')
        );
            const rawHtml = element.getAttribute?.('data-raw-html');
            if (sharedAlert && rawHtml !== null && rawHtml !== undefined) return true;
            return Boolean(
                element.matches?.('[data-lssm-enhanced-missing-vehicles]')
                || element.matches?.('[data-lssm-module="extendedCallWindow.enhancedMissingVehicles"]')
            );
        };

        if (isLssmOwned(source)) return true;
        const closestOwned = source?.closest?.(ownedSelector);
        if (isLssmOwned(closestOwned)) return true;
        return isLssmOwned(candidate?.root?.querySelector?.(ownedSelector));
    }

    function missionRequirementsExplicitSource(source) {
        if (!source || source.isConnected === false) return false;
        if (source.getAttribute?.('data-mcms-requirements-anchor') === '1' || source.id === 'missing_text') return true;
        if (source.matches?.('[data-requirement-type], .alert-missing-vehicles, [data-lssm-enhanced-missing-vehicles], [data-lssm-module="extendedCallWindow.enhancedMissingVehicles"]')) return true;
        return Boolean(source.querySelector?.('[data-requirement-type], .alert-missing-vehicles[data-raw-html], [data-lssm-enhanced-missing-vehicles]'));
    }

    function missionRequirementsDirectChild(root, node) {
        let current = node;
        while (current?.parentNode && current.parentNode !== root) current = current.parentNode;
        return current?.parentNode === root ? current : node;
    }

    function missionRequirementsPlacementHostUnsafe(node, boundary = null) {
        const unsafeTags = new Set(['TABLE', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TD', 'TH', 'COLGROUP']);
        let current = node;
        while (current && current !== boundary) {
            if (unsafeTags.has(String(current.tagName || '').toUpperCase())) return true;
            current = current.parentNode;
        }
        return false;
    }

    function missionRequirementsPlacementBlock(root, node) {
        if (!root || !node) return null;
        let target = node;
        let current = node;
        while (current && current !== root) {
            if (String(current.tagName || '').toUpperCase() === 'TABLE') target = current;
            current = current.parentNode;
        }
        const block = missionRequirementsDirectChild(root, target);
        const parent = block?.parentNode || root;
        if (!parent || missionRequirementsPlacementHostUnsafe(parent, root?.parentNode || null)) {
            return { root, parent: root, before: root.firstChild || null };
        }
        return { root, parent, before: block };
    }

    function missionRequirementsPlacement(candidate, source = null) {
        const root = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount;
        if (!root) return null;
        const native = root.matches?.('#missing_text') ? root : root.querySelector?.('#missing_text');
        const explicit = native || (missionRequirementsExplicitSource(source) && source?.getAttribute?.('data-mcms-requirements-anchor') !== '1' ? source : null);
        if (explicit?.parentNode) return missionRequirementsPlacementHostUnsafe(explicit.parentNode, root?.parentNode || null)
            ? missionRequirementsPlacementBlock(root, explicit)
            : { root, parent: explicit.parentNode, before: explicit };
        const address = root.querySelector?.('#mission_address, [data-mission-address], .mission-address, .mission_address');
        const title = root.querySelector?.('#mission_caption, #mission_name, [data-mission-title], .mission-title, .mission_caption, h1');
        const header = address || title;
        if (header) {
            const block = missionRequirementsDirectChild(root, header);
            const parent = block?.parentNode || root;
            const siblings = Array.from(parent.children || []);
            const index = siblings.indexOf(block);
            return { root, parent, before: index >= 0 ? (siblings[index + 1] || null) : (block?.nextSibling || null) };
        }
        // Operational regions may load before the mission header during AJAX dispatch.
        // They remain data sources only and are never valid panel hosts.
        return null;
    }

    function missionRequirementsPlacePanel(candidate, source, panel) {
        const placement = missionRequirementsPlacement(candidate, source);
        if (!placement?.parent || !panel) return false;
        const siblings = Array.from(placement.parent.children || []);
        const panelIndex = siblings.indexOf(panel);
        const beforeIndex = placement.before ? siblings.indexOf(placement.before) : siblings.length;
        if (panel.parentNode !== placement.parent || panelIndex < 0 || panelIndex !== beforeIndex - 1) {
            placement.parent.insertBefore?.(panel, placement.before || null);
        }
        return true;
    }

    function missionRequirementsSourceForCandidate(candidate) {
        const root = missionRequirementsCandidateRoot(candidate) || candidate?.root;
        const supplied = candidate?.source;
        const native = root?.matches?.('#missing_text') ? root : root?.querySelector?.('#missing_text');
        if (native && native.isConnected !== false) return native;
        if (supplied?.getAttribute?.('data-mcms-requirements-anchor') === '1' && supplied.isConnected !== false) {
            const placement = missionRequirementsPlacement({ ...candidate, root, mount: root }, supplied);
            if (placement?.parent) return supplied;
            supplied.remove?.();
        }
        return missionRequirementsExplicitSource(supplied) ? supplied : null;
    }

    function missionRequirementsCandidateFromSource(source) {
        if (!source?.ownerDocument || source.isConnected === false) return null;
        const rootSelector = [
            '#mission_form',
            'form[action*="/missions/"]',
            '#mission_content',
            '#lightbox_box',
            '#lightbox',
            '.lightbox_content',
            '.modal',
            '[role="dialog"]',
            '.ui-dialog'
        ].join(', ');
        const root = source.closest?.(rootSelector) || source.parentNode || source.ownerDocument.body;
        if (!root) return null;
        return { root, mount: root, source, directMissionRequirements: true };
    }

    function missionRequirementsAnchorForCandidate(candidate) {
        const root = missionRequirementsCandidateRoot(candidate) || candidate?.root || candidate?.mount;
        if (!root?.ownerDocument?.createElement) return null;
        let anchor = Array.from(root.children || []).find(node => node?.getAttribute?.('data-mcms-requirements-anchor') === '1')
            || root.querySelector?.('[data-mcms-requirements-anchor="1"]');
        const placement = missionRequirementsPlacement({ ...candidate, root, mount: root });
        if (!placement?.parent) {
            anchor?.remove?.();
            return null;
        }
        if (!anchor || anchor.isConnected === false) {
            anchor = root.ownerDocument.createElement('span');
            anchor.hidden = true;
            anchor.setAttribute('aria-hidden', 'true');
            anchor.setAttribute('data-mcms-requirements-anchor', '1');
        }
        placement.parent.insertBefore?.(anchor, placement.before || null);
        return anchor;
    }

    function missionRequirementsCandidateRoot(candidate) {
        const missionSelector = '#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]';
        const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
        const nodes = [candidate?.source, candidate?.root, candidate?.mount].filter(Boolean);
        const missionWithin = node => {
            if (!node) return null;
            if (node.matches?.(missionSelector)) return node;
            const closest = node.closest?.(missionSelector);
            if (closest) return 
```

## Observer integration

```javascript
{
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
        const activitySelector = '#missing_text, [data-mcms-requirements-anchor], #patient_button_form, #patient_button_text, #patient_button_text strong, [id^="patient_"], [data-patient-id], [data-patient], [class*="patient"], [data-patient-count], [data-patient-total], [data-patients], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all, #occupied, .vehicle_checkbox, [vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-equipment-types], [data-equipment-type], [data-current-personnel], [data-min-personnel], [data-max-personnel], [id^="mission_water_holder"], [id^="mission_foam_holder"], [id^="mission_pump_holder"], #lightbox_box, #lightbox, .lightbox_content, .modal, [role="dialog"], .ui-dialog, iframe, frame';
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
        if (!missionRequirementsPrimaryRuntime()) return;
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
        runtimeSetTimeout(() => scheduleMissionRequirementsScan(0), 1600);
    }

    function criticalMissionValueForEntry(entry) {
        return criticalMissionValueDetails(entry).value;
    }

    function criticalValueEligible(entry) {
        return selectedCriticalValueMode() === 'total' || Boolean(entry?.eligibleForCredits);
    }

    function criticalValueGroup(entries, predicate = () => true) {
        let total = 0;
        let known = 0;
        let unknown = 0;
        let eligible = 0;
        const seenMissionIds = new Set();
        const sources = new Map();
        for (const entry of entries) {
            if (!predicate(entry) || !criticalValueEligible(entry)) continue;
            const missionId = normaliseMissionId(entry?.missionId);
            if (missionId !== null && seenMissionIds.has(missionId)) continue;
            if (missionId !== null) seenMissionIds.add(missionId);
            if (entry?.eligibleForCredits) eligible += 1;
            const details = criticalMissionValueDetails(entry);
            const value = details.value;
            if (value === null || !Number.isFinite(Number(value))) {
                unknown += 1;
                continue;
            }
            total += Math.max(0, Number(value) || 0);
            known += 1;
            sources.set(details.source, (sources.get(details.source) || 0) + 1);
        }
        return { total: Math.round(total), known, unknown, eligible, count: seenMissionIds.size, sources };
    }

    function criticalValueDisplay(group) {
        if (!group?.known) return 'UNKNOWN';
        return `≈${formatOperationalCompactCredits(group.total)} CR`;
    }

    function criticalValueCoverage(group) {
        return `${group.known.toLocaleString('en-GB')} / ${(group.known + group.unknown).toLocaleString('en-GB')} valued`;
    }

    function criticalValueTitle(label, group) {
        const knownText = `${group.known.toLocaleString('en-GB')} valued mission${group.known === 1 ? '' : 's'}`;
        const unknownText = group.unknown ? ` · ${group.unknown.toLocaleString('en-GB')} value${group.unknown === 1 ? '' : 's'} unavailable` : '';
        return `${label}: approximately ${group.total.toLocaleString('en-GB')} credits from MissionChief average-credit data · ${knownText}${unknownText}`;
    }

    function criticalValuesHtml(allEntries, visibleEntries) {
        const scopedEntries = visibleEntries;
        const noScene = criticalValueGroup(scopedEntries, entry => Boolean(entry?.units?.known) && Math.max(0, Number(entry?.units?.onScene) || 0) === 0);
        const assistance = criticalValueGroup(scopedEntries, entry => criticalEntryPrimaryStatus(entry) === 'assistance');
        const visible = criticalValueGroup(scopedEntries);
        const mode = selectedCriticalValueMode();
        const showingText = `${mode === 'eligible' ? 'Eligible' : 'Total'} MissionChief average credits for ${visibleEntries.length.toLocaleString('en-GB')} currently visible mission${visibleEntries.length === 1 ? '' : 's'}`;
        const valueCard = (className, label, group) => `<div class="mcms-critical-value-card ${className}" title="${escapeHtml(criticalValueTitle(label, group))}"><span>${escapeHtml(label)}</span><strong>${escapeHtml(criticalValueDisplay(group))}</strong><small>${escapeHtml(criticalValueCoverage(group))}</small></div>`;
        return `
            <div class="mcms-critical-values-label" title="${escapeHtml(showingText)}"><strong>MISSION</strong><span>VALUE</span></div>
            <div class="mcms-critical-value-mode" role="group" aria-label="Mission value mode">
                <button type="button" data-critical-value-mode="total" class="${mode === 'total' ? 'mcms-filter-active' : ''}" aria-pressed="${mode === 'total'}">TOTAL</button>
                <button type="button" data-critical-value-mode="eligible" class="${mode === 'eligible' ? 'mcms-filter-active' : ''}" aria-pressed="${mode === 'eligible'}">ELIGIBLE</button>
            </div>
            <div class="mcms-critical-values-grid">
                ${valueCard('mcms-value-no-scene', 'No Scene', noScene)}
                ${valueCard('mcms-value-assistance', 'Assistance', assistance)}
                ${valueCard('mcms-value-all', 'Visible Value', visible)}
            </div>
            <span class="mcms-critical-showing">SHOWING ${visibleEntries.length.toLocaleString('en-GB')} OF ${allEntries.length.toLocaleString('en-GB')} MISSIONS</span>`;
    }

    function criticalSummaryHtml(allEntries) {
        const baseForStatus = criticalFilterEntries(allEntries, ['status']);
        const baseForOnWay = criticalFilterEntries(allEntries, ['onway']);
        const baseForMyUnits = criticalFilterEntries(allEntries, ['myunits']);
        const statusCounts = { all: baseForStatus.length, attention: 0, 'no-scene': 0, assistance: 0, clearing: 0, 'on-scene': 0, syncing: 0 };
        for (const entry of baseForStatus) {
            const key = criticalEntryPrimaryStatus(entry);
            if (Object.prototype.hasOwnProperty.call(statusCounts, key)) statusCounts[key] += 1;
            if (key === 'no-scene' || key === 'assistance') statusCounts.attention += 1;
        }
        let onWayMissions = 0;
        let onWayVehicles = 0;
        for (const entry of baseForOnWay) {
            const count = Math.max(0, Number(entry?.units?.onWay ?? entry?.units?.travelling) || 0);
            if (count > 0) onWayMissions += 1;
            onWayVehicles += count;
        }
        const selectedStatus = selectedCriticalPrimaryStatus();
        const statusCard = (key, className, label, value, title = '') => {
            const active = selecte
```
