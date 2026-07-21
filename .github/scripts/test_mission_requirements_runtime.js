#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const fixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-requirements-contract.json'), 'utf8'));
const catalogueFixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-catalogue-pages.json'), 'utf8'));
const ukCapabilityFixture = JSON.parse(fs.readFileSync(path.join(root, 'src', 'data', 'mission-requirements-en_GB.json'), 'utf8'));
const crossSourceFixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-requirements-cross-source-en_GB.json'), 'utf8'));
const startMarker = '    // Issue #133 clean-room live mission requirements matrix.';
const endMarker = '    function criticalMissionValueForEntry(entry) {';
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker, start);
assert(start >= 0 && end > start, 'unable to extract Issue #133 runtime block');
const block = source.slice(start, end);

const escapeHtml = value => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

class FakeClassList {
    constructor() { this.values = new Set(); }
    contains(value) { return this.values.has(value); }
    toggle(value, force) {
        const enabled = force === undefined ? !this.values.has(value) : Boolean(force);
        if (enabled) this.values.add(value);
        else this.values.delete(value);
        return enabled;
    }
}

class FakeElement {
    constructor(tagName = 'div', ownerDocument = null) {
        this.tagName = String(tagName).toUpperCase();
        this.ownerDocument = ownerDocument;
        this.dataset = {};
        this.attributes = new Map();
        this.classList = new FakeClassList();
        this.children = [];
        this.parentNode = null;
        this.isConnected = true;
        this.textContent = '';
        this.innerText = '';
        this.innerHTML = '';
        this.id = '';
        this.className = '';
        this.hidden = false;
        this.value = '';
        this.listeners = new Map();
        this.matchSet = new Set();
        this.queryMap = new Map();
        this.queryAllMap = new Map();
        this.queryHandler = null;
        this.queryAllHandler = null;
        this.closestMap = new Map();
    }
    get firstChild() { return this.children[0] || null; }
    get parentElement() { return this.parentNode?.tagName ? this.parentNode : null; }
    get nextSibling() { const index = this.parentNode?.children?.indexOf(this) ?? -1; return index >= 0 ? (this.parentNode.children[index + 1] || null) : null; }
    setAttribute(name, value) {
        this.attributes.set(name, String(value));
        if (name === 'id') this.id = String(value);
    }
    removeAttribute(name) {
        this.attributes.delete(name);
        if (name === 'id') this.id = '';
    }
    getAttribute(name) {
        if (name === 'data-raw-html' && this._lssmActive) {
            return '<div data-requirement-type="personnel">Missing Personnel</div>';
        }
        if (name === 'id') return this.id || null;
        return this.attributes.has(name) ? this.attributes.get(name) : null;
    }
    matches(selector) { return this.matchSet.has(selector); }
    querySelector(selector) {
        if (this.queryHandler) {
            const value = this.queryHandler(selector);
            if (value !== undefined) return value;
        }
        return this.queryMap.get(selector) || null;
    }
    querySelectorAll(selector) {
        if (this.queryAllHandler) {
            const value = this.queryAllHandler(selector);
            if (value !== undefined) return value;
        }
        return this.queryAllMap.get(selector) || [];
    }
    closest(selector) { return this.closestMap.get(selector) || null; }
    addEventListener(type, listener) {
        const listeners = this.listeners.get(type) || [];
        listeners.push(listener);
        this.listeners.set(type, listeners);
    }
    appendChild(child) {
        child.parentNode = this;
        child.ownerDocument ||= this.ownerDocument;
        child.isConnected = true;
        this.children.push(child);
        child.ownerDocument?.nodes.add(child);
        return child;
    }
    insertBefore(child, reference) {
        if (child.parentNode) child.parentNode.children = child.parentNode.children.filter(item => item !== child);
        child.parentNode = this;
        child.ownerDocument ||= this.ownerDocument;
        child.isConnected = true;
        const index = this.children.indexOf(reference);
        if (index >= 0) this.children.splice(index, 0, child);
        else this.children.push(child);
        child.ownerDocument?.nodes.add(child);
        return child;
    }
    contains(node) {
        if (this === node) return true;
        return this.children.some(child => child.contains?.(node));
    }
    remove() {
        this.isConnected = false;
        if (this.parentNode) this.parentNode.children = this.parentNode.children.filter(child => child !== this);
        this.ownerDocument?.nodes.delete(this);
    }
}

class FakeDocument {
    constructor() {
        this.nodes = new Set();
        this.documentElement = new FakeElement('html', this);
        this.head = new FakeElement('head', this);
        this.body = new FakeElement('body', this);
        this.defaultView = null;
        this.nodes.add(this.documentElement);
        this.nodes.add(this.head);
        this.nodes.add(this.body);
    }
    createElement(tagName) { return new FakeElement(tagName, this); }
    getElementById(id) { return Array.from(this.nodes).find(node => node.isConnected && node.id === id) || null; }
    querySelectorAll(selector) {
        if (selector === 'iframe, frame') return [];
        if (selector.startsWith('#')) {
            const node = this.getElementById(selector.slice(1));
            return node ? [node] : [];
        }
        if (selector === '[data-mcms-requirements-source-hidden="1"]') {
            return Array.from(this.nodes).filter(node => node.isConnected && node.dataset.mcmsRequirementsSourceHidden === '1');
        }
        return [];
    }
}

class FakeMutationObserver {
    static created = 0;
    constructor(callback) {
        this.callback = callback;
        this.connected = false;
        FakeMutationObserver.created += 1;
    }
    observe() { this.connected = true; }
    disconnect() { this.connected = false; }
}

let candidates = [];
let documentContexts = [];
let animationQueue = [];
let nextAnimationId = 1;
const trackedObservers = new Set();
const listenedEvents = [];
const openedUrls = [];
const flushAnimationFrames = () => {
    while (animationQueue.length) {
        const queue = animationQueue;
        animationQueue = [];
        for (const item of queue) item.callback();
    }
};

const context = {
    console,
    escapeHtml,
    SCRIPT: {
        missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements',
        missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style',
        version: '4.20.20'
    },
    state: { missionRequirements: true, uiTheme: 'mapCommand' },
    pageWindow: { MutationObserver: FakeMutationObserver, navigator: { platform: 'FixtureOS', userAgentData: { platform: 'FixtureOS', mobile: false } }, innerWidth: 1280, innerHeight: 720, open: url => { openedUrls.push(url); return {}; } },
    URL,
    URLSearchParams,
    document: {},
    MutationObserver: FakeMutationObserver,
    runtime: { destroyed: false },
    missionRequirementsScanTimer: null,
    missionRequirementsFeatureInstalled: false,
    missionRequirementsObservedDocuments: new WeakSet(),
    missionRequirementsObservedFrames: new WeakSet(),
    missionRequirementsRecords: new Map(),
    personalVehicleApiCache: new Map(),
    vehicleApiReady: true,
    vehicleApiFetchPromise: null,
    refreshPersonalVehicleData: () => Promise.resolve(true),
    runtimeSetTimeout: () => 1,
    runtimeClearTimeout: () => {},
    runtimeRequestAnimationFrame: callback => {
        const id = nextAnimationId++;
        animationQueue.push({ id, callback });
        return id;
    },
    runtimeCancelAnimationFrame: id => { animationQueue = animationQueue.filter(item => item.id !== id); },
    runtimeTrackObserver: observer => { trackedObservers.add(observer); return observer; },
    runtimeUntrackObserver: observer => { observer?.disconnect?.(); trackedObservers.delete(observer); },
    runtimeListen: (target, type, listener, options) => { listenedEvents.push({ target, type, listener, options }); },
    runtimeOnCleanup: () => {},
    transportSweepDocumentContexts: () => Array.from(new Set([...(documentContexts || []), ...candidates.map(candidate => candidate.root?.ownerDocument).filter(Boolean)])).map(doc => ({ doc })),
    missionValueWindowCandidates: () => candidates,
    mutationTouchesSelector: () => false,
    setInnerHtmlIfChanged: (element, html) => { if (element.innerHTML !== html) element.innerHTML = html; },
    isVisible: element => element?._visible !== false,
};
vm.createContext(context);
vm.runInContext(
    block + `
this.__mcmsRequirements = {
    definitions: MISSION_REQUIREMENT_DEFINITIONS,
    parseText: missionRequirementsParseText,
    parseSource: missionRequirementsParseSource,
    patientCount: missionRequirementsPatientCount,
    patientDetails: missionRequirementsPatientDetails,
    patientState: missionRequirementsPatientState,
    reconcilePatientDemand: missionRequirementsReconcilePatientDemand,
    reconcileCatalogue: missionRequirementsReconcileCatalogue,
    capacity: missionRequirementsCapacity,
    capacityText: missionRequirementsCapacityText,
    coverageRow: missionRequirementsCoverageRow,
    staffCapacity: missionRequirementsStaffCapacity,
    respondingCrewCapacity: missionRequirementsRespondingCrewCapacity,
    linkedTrainingValues: missionRequirementsLinkedTrainingValues,
    defaultStaffCapacity: missionRequirementsDefaultStaffCapacity,
    equipmentTypes: missionRequirementsEquipmentTypes,
    progressValue: missionRequirementsProgressValue,
    metadataValues: missionRequirementsMetadataValues,
    arrCapabilityState: missionRequirementsArrCapabilityState,
    vehicleApiCache: personalVehicleApiCache,
    vehicleApiRecord: missionRequirementsVehicleApiRecord,
    vehicleApiStaff: missionRequirementsVehicleApiStaff,
    resolvedStaffCapacity: missionRequirementsResolvedStaffCapacity,
    operationalSelectors: missionRequirementsOperationalSelectors,
    operationalActive: missionRequirementsOperationalElementActive,
    cataloguePersonnel: missionRequirementsCataloguePersonnelRequirements,
    catalogueRequirement: missionRequirementsCatalogueRequirement,
    vehicleId: missionRequirementsVehicleId,
    vehicleType: missionRequirementsVehicleType,
    collectUnits: missionRequirementsCollectUnits,
    aggregate: missionRequirementsAggregate,
    resolve: missionRequirementsResolve,
    overallState: missionRequirementsOverallState,
    lssmActive: missionRequirementsLssmActive,
    panelHtml: missionRequirementsPanelHtml,
    documentCss: missionRequirementsDocumentCss,
    windowCandidates: missionRequirementsWindowCandidates,
    primaryRuntime: missionRequirementsPrimaryRuntime,
    canonicalPanel: missionRequirementsCanonicalPanel,
    fallbackHtml: missionRequirementsFallbackHtml,
    catalogueDescriptor: missionRequirementsCatalogueDescriptor,
    catalogueModifier: missionRequirementsCatalogueModifier,
    stripNonDemandMetadata: missionRequirementsStripNonDemandMetadata,
    catalogueRequirement: missionRequirementsCatalogueRequirement,
    parseCatalogueDocument: missionRequirementsCatalogueParseDocument,
    cataloguePanelHtml: missionRequirementsCataloguePanelHtml,
    catalogueCompare: missionRequirementsCatalogueCompare,
    catalogueCacheStore: missionRequirementsCatalogueCacheStore,
    catalogueCacheLookup: missionRequirementsCatalogueCacheLookup,
    catalogueFailureFallback: missionRequirementsCatalogueFailureFallback,
    catalogueEnsure: missionRequirementsCatalogueEnsure,
    sourceForCandidate: missionRequirementsSourceForCandidate,
    candidateRoot: missionRequirementsCandidateRoot,
    placement: missionRequirementsPlacement,
    anchorForCandidate: missionRequirementsAnchorForCandidate,
    widthMode: missionRequirementsWidthMode,
    catalogueTtl: MISSION_REQUIREMENTS_CATALOGUE_TTL_MS,
    catalogueStale: MISSION_REQUIREMENTS_CATALOGUE_STALE_MS,
    reportUrl: missionRequirementsReportUrl,
    sanitize: missionRequirementsSafeDiagnostic,
    scan: scanMissionRequirementsWindows,
    clear: clearMissionRequirementsPanels,
    observeDocument: observeMissionRequirementsDocument,
    records: missionRequirementsRecords
};`,
    context,
    { filename: 'mission-requirements-runtime.js' }
);
const api = context.__mcmsRequirements;

for (const testCase of fixture.parserCases) {
    const result = api.parseText(testCase.input, testCase.group);
    assert.deepStrictEqual(
        JSON.parse(JSON.stringify(result.requirements.map(item => ({ key: item.key, missing: item.missing })))),
        testCase.expected,
        testCase.name
    );
    assert.strictEqual(result.remaining, testCase.remaining, testCase.name);
}


for (const [group, entries] of [
    ['vehicles', ukCapabilityFixture.vehicleRequirements],
    ['staff', ukCapabilityFixture.staffRequirements]
]) {
    for (const entry of entries) {
        for (const alias of entry.aliases) {
            const parsed = api.parseText(`1 ${alias}`, group);
            const parsedRequirement = parsed.requirements.find(requirement => requirement.missing === 1);
            assert.ok(parsedRequirement, `${group}:${entry.key}: parser handles ${alias}`);
            assert.strictEqual(parsed.remaining, '', `${group}:${entry.key}: parser consumes ${alias}`);
            const definition = api.definitions.find(candidate =>
                candidate.group === group && candidate.key === parsedRequirement.key
            );
            assert.ok(definition, `${group}:${entry.key}: parsed definition exists for ${alias}`);
            assert.ok((definition.aliases || []).some(value => String(value).trim().toLowerCase() === String(alias).trim().toLowerCase()), `${group}:${entry.key}: parsed alias ${alias}`);
            for (const typeId of entry.types) {
                assert.ok((definition.types || []).includes(typeId), `${group}:${entry.key}: ${alias} supports vehicle type ${typeId}`);
            }
            for (const equipment of entry.equipment || []) {
                assert.ok((definition.equipment || []).includes(equipment), `${group}:${entry.key}: ${alias} supports equipment ${equipment}`);
            }
            for (const training of entry.training || []) {
                assert.ok((definition.training || []).includes(training), `${group}:${entry.key}: ${alias} supports training ${training}`);
            }
            for (const attribute of entry.arrAttributes || []) {
                assert.ok((definition.arrAttributes || []).includes(attribute), `${group}:${entry.key}: ${alias} supports ARR attribute ${attribute}`);
            }
        }
    }
}


// Issue #282: every accepted vehicle alias and eligible type executes through
// the production parser, aggregator and all three operational buckets.
for (const entry of ukCapabilityFixture.vehicleRequirements) {
    const firstAlias = entry.aliases[0];
    const parsed = api.parseText(`1 ${firstAlias}`, 'vehicles');
    const parsedRequirement = parsed.requirements.find(requirement => requirement.missing === 1);
    assert.ok(parsedRequirement, `runtime audit parses ${firstAlias}`);
    const definition = api.definitions.find(candidate => candidate.key === parsedRequirement.key && candidate.group === 'vehicles');
    assert.ok(definition, `runtime audit resolves ${entry.key}`);
    for (const typeId of entry.types) {
        const factor = Number(definition.factors?.[typeId] ?? definition.factors?.[String(typeId)] ?? 1);
        const expected = Number.isFinite(factor) && factor > 0 ? factor : 1;
        const unit = {
            typeId,
            vehicleId: 282000 + typeId,
            equipment: new Set(),
            labels: new Set(),
            training: new Set(),
            arrCapabilities: new Set(),
            arrCapabilityKnown: true,
            knownDefinitionKeys: new Set(),
            compatibleTractiveTypes: new Set(),
            staff: null,
            contributionKey: `vehicle:282-${entry.key}-${typeId}`
        };
        const capacity = api.aggregate({ group: 'vehicles', definition }, [unit]);
        assert.strictEqual(capacity.min, expected, `${entry.key}: type ${typeId} contributes expected minimum`);
        assert.strictEqual(capacity.max, expected, `${entry.key}: type ${typeId} contributes expected maximum`);
        const zero = api.capacity(0, 0, true);
        const required = api.capacity(expected, expected, true);
        for (const [bucket, selected, responding, onSite] of [
            ['selected', capacity, zero, zero],
            ['responding', zero, capacity, zero],
            ['on-site', zero, zero, capacity]
        ]) {
            const row = api.coverageRow(
                { key: definition.key, requirement: definition.label, missing: expected, group: 'vehicles', definition },
                selected,
                responding,
                onSite,
                required
            );
            assert.strictEqual(row.covered, true, `${entry.key}: type ${typeId} covers ${bucket}`);
            assert.strictEqual(row.stillNeededText, '0', `${entry.key}: type ${typeId} clears ${bucket}`);
        }
        const duplicate = api.aggregate({ group: 'vehicles', definition }, [unit, { ...unit }]);
        assert.strictEqual(duplicate.min, expected, `${entry.key}: duplicate contribution key is counted once`);
    }
    const ineligible = api.aggregate({ group: 'vehicles', definition }, [{
        typeId: 99999,
        vehicleId: 99999,
        equipment: new Set(),
        labels: new Set(),
        training: new Set(),
        arrCapabilities: new Set(),
        arrCapabilityKnown: true,
        knownDefinitionKeys: new Set(),
        compatibleTractiveTypes: new Set(),
        staff: null,
        contributionKey: `vehicle:ineligible-${entry.key}`
    }]);
    assert.strictEqual(ineligible.min, 0, `${entry.key}: ineligible type contributes zero`);
    assert.strictEqual(ineligible.max, 0, `${entry.key}: ineligible type is definitively excluded`);
}

for (const group of crossSourceFixture.authoritativeLabels) {
    for (const label of group.labels) {
        const parsed = api.parseText(`1 ${label}`, 'vehicles');
        const requirement = parsed.requirements.find(item => item.missing === 1);
        assert.ok(requirement, `authoritative label parses: ${label}`);
        assert.strictEqual(parsed.remaining, '', `authoritative label is consumed: ${label}`);
        for (const typeId of group.types) {
            assert.ok(requirement.definition.types.includes(typeId), `${label}: supports type ${typeId}`);
        }
    }
}

for (const testCase of fixture.coverageCases) {
    const row = api.coverageRow(
        { key: testCase.name, requirement: testCase.name, missing: testCase.missing, group: 'vehicles', definition: {} },
        testCase.selected,
        testCase.responding,
        testCase.onSite,
        testCase.required
    );
    assert.strictEqual(row.covered, testCase.covered, `${testCase.name}: covered`);
    assert.strictEqual(row.definitelyOpen, testCase.definitelyOpen, `${testCase.name}: definitelyOpen`);
    assert.strictEqual(row.uncertain, testCase.uncertain, `${testCase.name}: uncertain`);
    assert.strictEqual(row.stillNeededText, testCase.stillNeededText, `${testCase.name}: still-needed range`);
}

const equipmentRow = {
    dataset: { equipmentTypes: 'drone, hazmat' },
    getAttribute(name) { return name === 'data-equipment-types' ? 'drone, hazmat' : null; },
    querySelectorAll() { return []; }
};
const equipmentCheckbox = {
    dataset: {},
    getAttribute() { return null; },
    querySelectorAll() { return []; },
    closest(selector) { return selector === 'tr' ? equipmentRow : null; }
};
assert.deepStrictEqual(Array.from(api.equipmentTypes(equipmentCheckbox)).sort(), ['drone', 'hazmat'], 'row-owned equipment metadata');

const boundedRow = {
    getAttribute(name) {
        if (name === 'data-min-personnel') return '2';
        if (name === 'data-max-personnel') return '6';
        return null;
    },
    querySelector() { return null; }
};
const boundedCheckbox = {
    getAttribute() { return null; },
    closest(selector) { return selector === 'tr' ? boundedRow : null; }
};
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(api.staffCapacity(boundedCheckbox))),
    { min: 2, max: 6, known: false, value: 2 },
    'bounded personnel capacity'
);

const exactCheckbox = {
    getAttribute(name) { return name === 'data-current-personnel' ? '4' : null; },
    closest() { return null; }
};
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(api.staffCapacity(exactCheckbox))),
    { min: 4, max: 4, known: true, value: 4 },
    'exact personnel capacity'
);


const railwayRegressionAmbiguousCell = {
    textContent: '239',
    getAttribute(name) { return name === 'sortvalue' ? '239' : null; }
};
const railwayRegressionCrewCell = {
    textContent: '1 / 1',
    getAttribute(name) { return name === 'data-current-personnel' ? '1' : null; }
};
const railwayRegressionRow = {
    getAttribute() { return null; },
    querySelector(selector) {
        if (selector === '[data-current-personnel]') return railwayRegressionCrewCell;
        if (selector === 'td:nth-of-type(4)' || selector === 'td:nth-of-type(5)[sortvalue]') return railwayRegressionAmbiguousCell;
        return null;
    },
    querySelectorAll() { return [railwayRegressionAmbiguousCell, railwayRegressionCrewCell]; }
};
const railwayRegressionCheckbox = {
    getAttribute() { return null; },
    closest(selector) { return selector === 'tr' ? railwayRegressionRow : null; }
};
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(api.staffCapacity(railwayRegressionCheckbox))),
    { min: 1, max: 1, known: true, value: 1 },
    'Railway Police semantic crew count wins over unrelated sortvalue 239'
);
const railwayRegressionUnlabelledRow = {
    getAttribute() { return null; },
    querySelector() { return null; },
    querySelectorAll() { return [railwayRegressionAmbiguousCell]; }
};
const railwayRegressionUnlabelledCheckbox = {
    getAttribute() { return null; },
    closest(selector) { return selector === 'tr' ? railwayRegressionUnlabelledRow : null; }
};
assert.strictEqual(
    api.staffCapacity(railwayRegressionUnlabelledCheckbox),
    null,
    'unlabelled numeric table metadata must not become personnel capacity'
);
const railwayPoliceDefinition = api.definitions.find(item => item.key === 'railway-police-officer');
const railwaySelectedUnit = {
    typeId: -1,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(['railway police officer']),
    knownDefinitionKeys: new Set(['railway-police-officer']),
    staff: api.staffCapacity(railwayRegressionCheckbox),
    contributionKey: 'vehicle:239'
};
const railwaySelectedCapacity = api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [railwaySelectedUnit]);
assert.strictEqual(railwaySelectedCapacity.min, 1, 'one selected Railway Police Officer contributes one');
assert.strictEqual(railwaySelectedCapacity.max, 1, 'one selected Railway Police Officer remains exact');


// Issue #285: canonical Units Responding crew and exact Railway Policing evidence.
{
const issue285CrewCell = {
    textContent: '4',
    getAttribute(name) { return name === 'sortvalue' ? '4' : null; }
};
const issue285DrivingContainer = {};
const issue285RespondingRow = {
    textContent: '',
    innerText: '',
    ownerDocument: null,
    matches(selector) { return selector === 'tr'; },
    closest(selector) {
        if (selector === '#mission_vehicle_driving, tbody#mission_vehicle_driving') return issue285DrivingContainer;
        return null;
    },
    querySelector(selector) {
        if (selector === 'td:nth-of-type(5)[sortvalue]') return issue285CrewCell;
        return null;
    },
    querySelectorAll() { return []; },
    getAttribute() { return null; }
};
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(api.respondingCrewCapacity(issue285RespondingRow))),
    { min: 4, max: 4, known: true, value: 4 },
    'canonical responding fifth-cell sortvalue provides exact crew capacity'
);
const issue285NonRespondingRow = { ...issue285RespondingRow, closest() { return null; } };
assert.strictEqual(api.respondingCrewCapacity(issue285NonRespondingRow), null, 'positional sortvalue is rejected outside the canonical responding table');

const issue285Local = new FakeElement('a');
const issue285Linked = new FakeElement('input');
issue285Linked.setAttribute('data-education-key', 'railway_police');
const issue285LinkedRow = new FakeElement('tr');
issue285Linked.closestMap.set('tr', issue285LinkedRow);
const issue285Candidate = {
    root: {
        querySelectorAll(selector) { return selector.includes('28501') ? [issue285Linked] : []; }
    },
    mount: null,
    source: null
};
const issue285Training = api.linkedTrainingValues(issue285Candidate, 28501, issue285Local);
assert(issue285Training.has('railway police'), 'linked data-education-key railway_police is recognised');
const issue285Command = new FakeElement('span');
issue285Command.setAttribute('data-education-key', 'railway_police_command');
const issue285CommandValues = api.metadataValues(issue285Command, 'training');
assert(issue285CommandValues.has('railway police command'), 'railway_police_command is preserved exactly');
assert(!issue285CommandValues.has('railway police'), 'Mobile Operations Management does not collapse into Railway Policing');
assert(railwayPoliceDefinition.training.includes('railway_police'), 'runtime Railway Police definition contains the native education key');

const issue285RespondingUnit = {
    typeId: 108,
    vehicleId: 28501,
    equipment: new Set(),
    labels: new Set(),
    training: issue285Training,
    arrCapabilities: new Set(),
    arrCapabilityKnown: false,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set(),
    staff: api.respondingCrewCapacity(issue285RespondingRow),
    contributionKey: 'vehicle:28501'
};
const issue285RespondingCapacity = api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [issue285RespondingUnit]);
assert.strictEqual(issue285RespondingCapacity.min, 4, 'four proven Railway Police Officers count as Responding');
assert.strictEqual(issue285RespondingCapacity.max, 4, 'responding Railway Police capacity remains exact');
const issue285Coverage = api.coverageRow(
    { key: 'railway-police-officer', requirement: 'Railway Police Officer', missing: 4, group: 'staff', definition: railwayPoliceDefinition },
    api.capacity(0, 0, true),
    issue285RespondingCapacity,
    api.capacity(0, 0, true),
    api.capacity(4, 4, true)
);
assert.strictEqual(issue285Coverage.stillNeededText, '0', 'four responding Railway Police Officers clear a requirement of four');
assert.strictEqual(issue285Coverage.covered, true, 'responding specialist personnel cover the requirement');

const issue285CommandUnit = {
    ...issue285RespondingUnit,
    training: new Set(['railway police command']),
    contributionKey: 'vehicle:28502'
};
assert.strictEqual(api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [issue285CommandUnit]).min, 0, 'Mobile Operations Managers do not satisfy Railway Police Officer demand');
const issue285UnknownUnit = {
    ...issue285RespondingUnit,
    training: new Set(),
    arrCapabilityKnown: false,
    contributionKey: 'vehicle:28503'
};
const issue285Unknown = api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [issue285UnknownUnit]);
assert.strictEqual(issue285Unknown.min, 0, 'unproven responding specialist crew contributes no confirmed capacity');
assert.strictEqual(issue285Unknown.max, null, 'unproven responding specialist crew remains fail-closed rather than confident zero');
}


// Issue #242: MissionChief's live missing total already reflects selected personnel.
{
const issue242Doc = new FakeDocument();
issue242Doc.defaultView = { MutationObserver: FakeMutationObserver };
const issue242Candidate = makeMissionCandidate(issue242Doc, '4 Railway Police Officers');
const issue242Definition = api.definitions.find(item => item.key === 'railway-police-officer');
const issue242Catalogue = { requirements: [{ key: 'railway-police-officer', baseline: 8, missing: 8 }] };
let issue242Rows = api.resolve(issue242Candidate, {
    requirements: [{ key: 'railway-police-officer', requirement: 'Railway Police Officer', missing: 4, group: 'staff', definition: issue242Definition, statedRequirement: true }],
    unresolved: []
}, issue242Catalogue);
let issue242Row = issue242Rows.find(item => item.key === 'railway-police-officer');
assert.strictEqual(issue242Row.requiredText, '8', 'authoritative Railway Police requirement remains eight');
assert.strictEqual(issue242Row.onSiteMin, 0, 'committed selected personnel are not falsely reported On site');
assert.strictEqual(issue242Row.respondingMin, 0, 'committed selected personnel are not falsely reported Responding');
assert.strictEqual(issue242Row.selectedMin, 4, 'baseline eight minus live missing four is reported Selected four');
assert.strictEqual(issue242Row.stillNeededText, '4', 'four Railway Police Officers remain needed');

issue242Rows = api.resolve(issue242Candidate, {
    requirements: [{ key: 'railway-police-officer', requirement: 'Railway Police Officer', missing: 8, group: 'staff', definition: issue242Definition, statedRequirement: true }],
    unresolved: []
}, issue242Catalogue);
issue242Row = issue242Rows.find(item => item.key === 'railway-police-officer');
assert.strictEqual(issue242Row.selectedMin, 0, 'restored live missing demand removes inferred Selected after deselection');
assert.strictEqual(issue242Row.onSiteMin, 0, 'deselection does not create false On-site personnel');
}

const issue191AmbulanceDefinition = api.definitions.find(item => item.key === 'ambulance');
const issue191HemsDefinition = api.definitions.find(item => item.key === 'hems');
const issue191SelectedHemsUnit = { typeId: 9, equipment: new Set(), staff: null, contributionKey: 'vehicle:hems-9001' };
const issue191DuplicateSelectedHemsUnit = { ...issue191SelectedHemsUnit };
const issue191SelectedRoadAmbulance = { typeId: 5, equipment: new Set(), staff: null, contributionKey: 'vehicle:ambulance-5001' };
const issue191HemsAsAmbulance = api.aggregate({ group: 'vehicles', definition: issue191AmbulanceDefinition }, [issue191SelectedHemsUnit]);
assert.strictEqual(issue191HemsAsAmbulance.min, 1, 'selected HEMS contributes one Ambulance capability');
assert.strictEqual(issue191HemsAsAmbulance.max, 1, 'selected HEMS has exact Ambulance capacity');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: issue191HemsDefinition }, [issue191SelectedHemsUnit]).min, 1, 'selected HEMS retains HEMS capability');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: issue191AmbulanceDefinition }, [issue191SelectedHemsUnit, issue191DuplicateSelectedHemsUnit]).min, 1, 'same HEMS contribution key is not duplicated within the Ambulance row');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: issue191HemsDefinition }, [issue191SelectedRoadAmbulance]).min, 0, 'road Ambulance does not satisfy HEMS');


// Issue #269 vehicle crew fallback and canonical PRV/SRV aliases.
{
const policeStaff = api.defaultStaffCapacity(8, null);
assert.strictEqual(policeStaff.min, 1, 'Police Car contributes at least one officer');
assert.strictEqual(policeStaff.max, 2, 'Police Car preserves its two-officer maximum');
const overrideElement = { getAttribute(name) { return name === 'data-max-personnel-override' ? '1' : null; }, closest() { return null; } };
const overriddenStaff = api.defaultStaffCapacity(8, overrideElement);
assert.strictEqual(overriddenStaff.min, 1, 'override preserves minimum crew');
assert.strictEqual(overriddenStaff.max, 1, 'native override narrows maximum crew');
const policeDefinition = api.definitions.find(definition => definition.key === 'police-officers');
const selectedPoliceCar = { typeId: 8, equipment: new Set(), labels: new Set(), training: new Set(), knownDefinitionKeys: new Set(), staff: policeStaff, contributionKey: 'vehicle:26901' };
const selectedPoliceCapacity = api.aggregate({ group: 'staff', definition: policeDefinition }, [selectedPoliceCar]);
assert.strictEqual(selectedPoliceCapacity.min, 1, 'selected Police Car credits one confirmed Police Officer');
assert.strictEqual(selectedPoliceCapacity.max, 2, 'selected Police Car retains bounded officer capacity');
const coveredPoliceRow = api.coverageRow({ key: 'police-officers', requirement: 'Police Officers', missing: 1, group: 'staff', definition: policeDefinition }, selectedPoliceCapacity, api.capacity(0, 0, true), api.capacity(0, 0, true), api.capacity(1, 1, true));
assert.strictEqual(coveredPoliceRow.stillNeededText, '0', 'selected Police Car clears a one-officer shortage');
for (const [text, key, label] of [['2 PRVs', 'primary-response', 'Primary Response Vehicle'], ['2 SRVs', 'secondary-response', 'Secondary Response Vehicle']]) {
    const parsed = api.parseText(text, 'vehicles');
    const requirement = parsed.requirements.find(item => item.missing === 2);
    assert(requirement, `${text} parses as a requirement`);
    assert.strictEqual(requirement.key, key, `${text} uses the canonical key`);
    assert.strictEqual(requirement.definition.label, label, `${text} uses the full canonical label`);
    assert.strictEqual(parsed.remaining, '', `${text} is consumed without unresolved residue`);
}
}



// Issue #273: exact assigned personnel clears trained and generic police requirements.
{
const issue273Doc = new FakeDocument();
issue273Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/273' } };
const issue273Candidate = makeMissionCandidate(issue273Doc, '18 Level 2 Public Order Officers');
const level2Definition = api.definitions.find(definition => definition.key === 'public-order-level-2');
const cacheVehicle = (id, type, personnel) => api.vehicleApiCache.set(String(id), { id, vehicle_type: type, assigned_personnel_count: personnel });
const firstCarrier = makeVehicleElement(issue273Doc, 27301, 51, { typeOnRow: true });
const secondCarrier = makeVehicleElement(issue273Doc, 27302, 51, { typeOnRow: true });
for (const carrier of [firstCarrier, secondCarrier]) {
    carrier.vehicle.checked = true;
    carrier.vehicle.matchSet.add('.vehicle_checkbox');
    carrier.vehicle.classList.values.add('vehicle_checkbox');
    carrier.row.textContent = carrier.row.innerText = 'Police Support Unit Carrier [Level 2 Public Order Officer]';
}
cacheVehicle(27301, 51, 9);
cacheVehicle(27302, 51, 9);
issue273Candidate.root.selectedUnits = [firstCarrier.vehicle, secondCarrier.vehicle];
let issue273Units = api.collectUnits(issue273Candidate, 'selected');
let issue273Capacity = api.aggregate({ group: 'staff', definition: level2Definition }, issue273Units);
assert.strictEqual(issue273Capacity.min, 18, 'two exact nine-person public-order carriers contribute eighteen');
assert.strictEqual(issue273Capacity.max, 18, 'exact assigned personnel removes the 2–18 fallback range');
let issue273Rows = api.resolve(issue273Candidate, {
    requirements: [{ key: 'public-order-level-2', requirement: 'Level 2 Public Order Officer', missing: 18, group: 'staff', definition: level2Definition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'public-order-level-2', baseline: 18, missing: 18 }] });
let issue273Row = issue273Rows.find(row => row.key === 'public-order-level-2');
assert.strictEqual(issue273Row.selectedText, '18', 'Matrix displays exact selected public-order personnel');
assert.strictEqual(issue273Row.stillNeededText, '0', '9 + 9 clears the eighteen-person requirement');
assert.strictEqual(issue273Row.covered, true, 'fulfilled public-order row is marked covered');
issue273Candidate.root.selectedUnits = [firstCarrier.vehicle];
issue273Rows = api.resolve(issue273Candidate, {
    requirements: [{ key: 'public-order-level-2', requirement: 'Level 2 Public Order Officer', missing: 18, group: 'staff', definition: level2Definition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'public-order-level-2', baseline: 18, missing: 18 }] });
issue273Row = issue273Rows.find(row => row.key === 'public-order-level-2');
assert.strictEqual(issue273Row.selectedText, '9', 'deselecting one public-order carrier removes nine personnel');
assert.strictEqual(issue273Row.stillNeededText, '9', 'nine-person shortage returns after deselection');

const policeDefinition = api.definitions.find(definition => definition.key === 'police-officers');
const sceneUnits = [];
for (let index = 0; index < 11; index += 1) {
    const id = 273100 + index;
    const unit = makeVehicleElement(issue273Doc, id, 8, { typeOnRow: true });
    unit.row.setAttribute('data-vehicle-id', String(id));
    unit.row.id = `mission_vehicle_${id}`;
    cacheVehicle(id, 8, 1);
    sceneUnits.push(unit.row);
}
issue273Candidate.root.selectedUnits = [];
issue273Candidate.root.onSiteRows = sceneUnits;
let policeRows = api.resolve(issue273Candidate, {
    requirements: [{ key: 'police-officers', requirement: 'Police Officers', missing: 2, group: 'staff', definition: policeDefinition, statedRequirement: true }],
    unresolved: []
});
let policeRow = policeRows.find(row => row.key === 'police-officers');
assert.strictEqual(policeRow.onSiteText, '11', 'eleven on-scene police personnel are exact rather than 7+');
assert.strictEqual(policeRow.requiredText, '13', 'live missing two plus exact on-scene eleven reconstructs required thirteen');
assert.strictEqual(policeRow.stillNeededText, '2', 'generic Police Officers shortage remains accurate');
const selectedTrafficCar = makeVehicleElement(issue273Doc, 273200, 24, { typeOnRow: true });
selectedTrafficCar.vehicle.checked = true;
selectedTrafficCar.vehicle.matchSet.add('.vehicle_checkbox');
selectedTrafficCar.vehicle.classList.values.add('vehicle_checkbox');
cacheVehicle(273200, 24, 2);
issue273Candidate.root.selectedUnits = [selectedTrafficCar.vehicle];
policeRows = api.resolve(issue273Candidate, {
    requirements: [{ key: 'police-officers', requirement: 'Police Officers', missing: 2, group: 'staff', definition: policeDefinition, statedRequirement: true }],
    unresolved: []
});
policeRow = policeRows.find(row => row.key === 'police-officers');
assert.strictEqual(policeRow.selectedText, '2', 'any eligible selected police vehicle contributes exact assigned officers');
assert.strictEqual(policeRow.stillNeededText, '0', 'selected police officers clear the remaining generic shortage');
assert.strictEqual(policeRow.covered, true, 'generic Police Officers row clears when exact total is met');

const nativeExact = makeVehicleElement(issue273Doc, 273300, 51, { staff: 4 });
cacheVehicle(273300, 51, 9);
assert.strictEqual(api.resolvedStaffCapacity(273300, 51, nativeExact.vehicle).min, 4, 'native exact crew metadata remains higher priority than cached API data');
assert.deepStrictEqual(JSON.parse(JSON.stringify(api.vehicleApiStaff({ assigned_personnel_count: 0 }))), { min: 0, max: 0, known: true, value: 0 }, 'zero assigned personnel remains exact');
}

// Issue #271: ARR specialist capabilities reconcile Search Advisor and SAR Commander personnel.
{
const issue271Doc = new FakeDocument();
issue271Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/271' } };
const issue271Candidate = makeMissionCandidate(issue271Doc, '1 Search Advisor, 2 SAR Commanders');
const searchAdvisorDefinition = api.definitions.find(definition => definition.key === 'search-advisor-personnel');
const sarCommanderDefinition = api.definitions.find(definition => definition.key === 'sar-commander-personnel');
assert(searchAdvisorDefinition?.countable, 'Search Advisor is countable');
assert(sarCommanderDefinition?.countable, 'SAR Commander is countable');

const advisor = makeVehicleElement(issue271Doc, 27101, 86, { staff: 1 });
advisor.vehicle.checked = true;
advisor.vehicle.matchSet.add('.vehicle_checkbox');
advisor.vehicle.classList.values.add('vehicle_checkbox');
advisor.vehicle.setAttribute('search_and_rescue', '1');
issue271Candidate.root.selectedUnits = [advisor.vehicle];
let issue271Units = api.collectUnits(issue271Candidate, 'selected');
let issue271Capacity = api.aggregate({ group: 'staff', definition: searchAdvisorDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 1, 'ARR-selected Search Advisor contributes confirmed personnel');
assert.strictEqual(issue271Capacity.max, 1, 'semantic selected crew keeps Search Advisor exact');
let issue271Rows = api.resolve(issue271Candidate, {
    requirements: [{ key: 'search-advisor-personnel', requirement: 'Search Advisor', missing: 1, group: 'staff', definition: searchAdvisorDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'search-advisor-personnel', baseline: 1, missing: 1 }] });
let issue271Row = issue271Rows.find(row => row.key === 'search-advisor-personnel');
assert.strictEqual(issue271Row.selectedMin, 1, 'selected ARR Search Advisor appears in Matrix Selected');
assert.strictEqual(issue271Row.stillNeededText, '0', 'selected ARR Search Advisor clears shortage');

const explicitState = api.arrCapabilityState(advisor.vehicle, issue271Candidate, 27101);
assert.strictEqual(explicitState.authoritative, true, 'vehicle checkbox is an authoritative ARR capability source');
assert.strictEqual(explicitState.values.size, 1, 'positive ARR attribute is captured');

const nonAdvisor = makeVehicleElement(issue271Doc, 27102, 86, { staff: 1 });
nonAdvisor.vehicle.checked = true;
nonAdvisor.vehicle.matchSet.add('.vehicle_checkbox');
nonAdvisor.vehicle.classList.values.add('vehicle_checkbox');
nonAdvisor.vehicle.setAttribute('search_and_rescue', '0');
issue271Candidate.root.selectedUnits = [nonAdvisor.vehicle];
issue271Units = api.collectUnits(issue271Candidate, 'selected');
issue271Capacity = api.aggregate({ group: 'staff', definition: searchAdvisorDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 0, 'zero ARR Search Advisor attribute contributes nothing');
assert.strictEqual(issue271Capacity.max, 0, 'authoritative zero ARR attribute remains known rather than unknown');

const commander = makeVehicleElement(issue271Doc, 27103, 85);
commander.vehicle.checked = true;
commander.vehicle.matchSet.add('.vehicle_checkbox');
commander.vehicle.classList.values.add('vehicle_checkbox');
issue271Candidate.root.selectedUnits = [commander.vehicle];
issue271Units = api.collectUnits(issue271Candidate, 'selected');
issue271Capacity = api.aggregate({ group: 'staff', definition: sarCommanderDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 1, 'Control Van guarantees at least one SAR Commander');
assert.strictEqual(issue271Capacity.max, 3, 'Control Van preserves reviewed SAR Commander staff range');

const respondingAdvisor = makeVehicleElement(issue271Doc, 27104, 86, { typeOnRow: true });
respondingAdvisor.row.setAttribute('search_and_rescue', '1');
issue271Candidate.root.selectedUnits = [];
issue271Candidate.root.enRouteRows = [respondingAdvisor.row];
issue271Units = api.collectUnits(issue271Candidate, 'responding');
issue271Capacity = api.aggregate({ group: 'staff', definition: searchAdvisorDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 1, 'responding row ARR capability contributes Search Advisor');
assert.strictEqual(issue271Capacity.max, 3, 'responding Search Advisor preserves vehicle staff range');

const onsiteCommander = makeVehicleElement(issue271Doc, 27105, 100, { typeOnRow: true });
issue271Candidate.root.enRouteRows = [];
issue271Candidate.root.onSiteRows = [onsiteCommander.row];
issue271Units = api.collectUnits(issue271Candidate, 'onsite');
issue271Capacity = api.aggregate({ group: 'staff', definition: sarCommanderDefinition }, issue271Units);
assert.strictEqual(issue271Capacity.min, 1, 'Mountain Rescue Control Van contributes on-site SAR Commander');
assert.strictEqual(issue271Capacity.max, 3, 'on-site SAR Commander retains reviewed staff range');

issue271Candidate.root.selectedUnits = [];
issue271Candidate.root.onSiteRows = [];
issue271Rows = api.resolve(issue271Candidate, {
    requirements: [{ key: 'search-advisor-personnel', requirement: 'Search Advisor', missing: 1, group: 'staff', definition: searchAdvisorDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: 'search-advisor-personnel', baseline: 1, missing: 1 }] });
issue271Row = issue271Rows.find(row => row.key === 'search-advisor-personnel');
assert.strictEqual(issue271Row.selectedMin, 0, 'deselection removes Search Advisor selected capacity');
assert.strictEqual(issue271Row.stillNeededText, '1', 'Search Advisor shortage returns after deselection');
}

const factorRequirement = { group: 'vehicles', definition: { types: [5], equipment: [], factors: { 5: 2 } } };
const factorUnit = { typeId: 5, equipment: new Set(), staff: null, contributionKey: 'vehicle:1' };
assert.strictEqual(api.aggregate(factorRequirement, [factorUnit]).min, 2, 'capacity factor greater than one');

const pairedRequirement = { group: 'vehicles', definition: { types: [67, 74], equipment: [], factors: {} } };
const pairedUnits = [
    { typeId: 67, equipment: new Set(), staff: null, contributionKey: 'pair:10:11' },
    { typeId: 74, equipment: new Set(), staff: null, contributionKey: 'pair:10:11' },
];
const paired = api.aggregate(pairedRequirement, pairedUnits);
assert.strictEqual(paired.min, 1, 'towing vehicle and trailer must not double-count');
assert.strictEqual(paired.max, 1, 'paired maximum must remain one');

const genericTableSource = {
    matches() { return false; },
    querySelector(selector) { return selector.includes('table.table-striped') ? {} : null; }
};
assert.strictEqual(api.lssmActive({ root: { querySelector() { return null; } } }, genericTableSource), false, 'generic MissionChief table is not LSSM');
const nativeMissingSource = {
    matches(selector) { return selector === '.alert-missing-vehicles'; },
    classList: { contains(value) { return value === 'alert-missing-vehicles'; } },
    getAttribute() { return null; },
    closest() { return null; },
    querySelector() { return null; }
};
assert.strictEqual(
    api.lssmActive({ root: null }, nativeMissingSource),
    false,
    'MissionChief native missing alert must not be classified as LSSM'
);
const lssmSource = {
    matches(selector) { return selector === '.alert-missing-vehicles'; },
    classList: { contains(value) { return value === 'alert-missing-vehicles'; } },
    getAttribute(name) { return name === 'data-raw-html' ? '<div data-requirement-type="personnel">Missing Personnel</div>' : null; },
    closest() { return null; },
    querySelector() { return null; }
};
assert.strictEqual(api.lssmActive({ root: null }, lssmSource), true, 'active LSSM panel is detected by explicit ownership metadata');

const fulfilledAmbulanceRow = api.coverageRow(
    { key: 'ambulance', requirement: 'Ambulance', missing: 1, group: 'vehicles', definition: {} },
    { min: 1, max: 1, known: true },
    { min: 0, max: 0, known: true }
);
const openPoliceRow = api.coverageRow(
    { key: 'police-car', requirement: 'Police Car', missing: 2, group: 'vehicles', definition: {} },
    { min: 0, max: 0, known: true },
    { min: 0, max: 0, known: true }
);
const coveredPanel = api.panelHtml([fulfilledAmbulanceRow], []);
assert.strictEqual(coveredPanel.stateName, 'success', 'covered panel state');
assert(coveredPanel.html.includes('All currently known requirements are covered.'), 'all-covered panel retains explicit success state');
assert(!coveredPanel.html.includes('<table'), 'all-covered panel hides the empty requirement table');
assert(!coveredPanel.html.includes('Ambulance'), 'fulfilled row is hidden from the rendered list');

const mixedPanel = api.panelHtml([fulfilledAmbulanceRow, openPoliceRow], []);
for (const header of fixture.layout.requiredHeaders) assert(mixedPanel.html.includes(header), `missing table header: ${header}`);
assert(mixedPanel.html.includes('Police Car'), 'outstanding requirement remains visible');
assert(!mixedPanel.html.includes('Ambulance'), 'fulfilled requirement is hidden beside an outstanding row');
assert(!mixedPanel.html.includes('All currently known requirements are covered.'), 'mixed panel does not show all-covered success');

const renewedAmbulanceRow = api.coverageRow(
    { key: 'ambulance', requirement: 'Ambulance', missing: 2, group: 'vehicles', definition: {} },
    { min: 1, max: 1, known: true },
    { min: 0, max: 0, known: true }
);
const renewedPanel = api.panelHtml([renewedAmbulanceRow], []);
assert(renewedPanel.html.includes('Ambulance'), 'hidden row returns when an upgrade or re-entry creates a positive shortage');
assert(renewedPanel.html.includes('data-row-state="partial"'), 'renewed shortage keeps its live partial state');

const unresolvedPanel = api.panelHtml(
    [fulfilledAmbulanceRow],
    [{ group: 'vehicles', text: 'Unknown specialist response requirement' }]
);
assert(unresolvedPanel.html.includes('Unknown specialist response requirement'), 'unresolved authority remains visible');
assert(!unresolvedPanel.html.includes('All currently known requirements are covered.'), 'unresolved authority overrides all-covered success');
assert.strictEqual(unresolvedPanel.stateName, 'warning', 'unresolved authority remains warning state');

const css = api.documentCss().replace(/\s+/g, '').toLowerCase();
const normalPanelRule = css.split('.mcms-req-head', 1)[0];
for (const forbidden of fixture.layout.forbiddenNormalPanelPositioning) {
    assert(!normalPanelRule.includes(forbidden), `normal-flow panel contains ${forbidden}`);
}
assert(normalPanelRule.includes('position:relative!important'), 'normal-flow panel must be relative');
assert(normalPanelRule.includes('[data-mcms-requirements-source-hidden="1"]{display:none!important}'), 'native source hiding must be CSS-owned');
assert(css.includes('@media(max-width:767px)'), 'mobile breakpoint missing');
assert(css.includes(`width:min(100%,${fixture.layout.standardDesktopWidth})!important`), 'standard width missing');
assert(css.includes(`data-width-mode="wide"]{width:min(100%,${fixture.layout.wideDesktopWidth})!important`), 'wide width missing');
assert(css.includes('data-width-mode="fluid"]{width:100%!important'), 'fluid width missing');

function makeVehicleElement(doc, vehicleId, typeId, options = {}) {
    const row = new FakeElement('tr', doc);
    const vehicle = new FakeElement('input', doc);
    vehicle.value = String(vehicleId);
    if (options.typeOnRow) row.setAttribute('vehicle_type_id', String(typeId));
    else vehicle.setAttribute('vehicle_type_id', String(typeId));
    if (options.tractiveId !== undefined) vehicle.setAttribute('tractive_vehicle_id', String(options.tractiveId));
    if (options.staff !== undefined) vehicle.setAttribute('data-current-personnel', String(options.staff));
    if (options.equipment) row.setAttribute('data-equipment-types', options.equipment.join(','));
    vehicle.closestMap.set('tr', row);
    row.queryHandler = selector => selector.includes('vehicle_type_id') ? (options.typeOnRow ? null : vehicle) : null;
    row.queryAllHandler = () => [];
    return { row, vehicle };
}

function makeMissionCandidate(doc, requirementText = '1 Ambulance') {
    const missionRoot = new FakeElement('div', doc);
    const sourceNode = new FakeElement('div', doc);
    sourceNode.id = 'missing_text';
    sourceNode.innerText = requirementText;
    sourceNode.textContent = requirementText;
    sourceNode.queryAllHandler = selector => selector === '[data-requirement-type]' ? [] : [];
    sourceNode.queryHandler = selector => sourceNode._lssmActive && selector.includes('.alert-missing-vehicles') ? new FakeElement('div', doc) : null;
    sourceNode.matches = selector => sourceNode._lssmActive && selector === '.alert-missing-vehicles';
    missionRoot.appendChild(sourceNode);
    missionRoot.selectedUnits = [];
    missionRoot.enRouteRows = [];
    missionRoot.onSiteRows = [];
    missionRoot.patientForm = null;
    missionRoot.patientText = null;
    missionRoot.queryHandler = selector => {
        if (selector === '#missing_text') return sourceNode.isConnected ? sourceNode : null;
        if (selector === '#patient_button_form') return missionRoot.patientForm?.isConnected === false ? null : missionRoot.patientForm;
        if (selector === '#patient_button_text') return missionRoot.patientText?.isConnected === false ? null : missionRoot.patientText;
        if (selector === '[data-mcms-requirements-anchor="1"]') return missionRoot.children.find(child => child.getAttribute?.('data-mcms-requirements-anchor') === '1') || null;
        if (selector.includes('.alert-missing-vehicles')) return sourceNode._lssmActive ? sourceNode : null;
        return null;
    };
    missionRoot.queryAllHandler = selector => {
        if (selector.includes('.vehicle_checkbox')) return missionRoot.selectedUnits;
        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;
        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;
        if (selector === 'iframe, frame') return [];
        return [];
    };
    return { root: missionRoot, mount: missionRoot, source: sourceNode };
}

function makeMissionCandidateWithoutSource(doc) {
    const missionRoot = new FakeElement('form', doc);
    missionRoot.setAttribute('action', '/missions/9901');
    missionRoot.matchSet.add('form[action*="/missions/"]');
    missionRoot.selectedUnits = [];
    missionRoot.enRouteRows = [];
    missionRoot.onSiteRows = [];
    missionRoot.patientForm = null;
    missionRoot.patientText = null;
    missionRoot.queryHandler = selector => {
        if (selector === '#missing_text') return missionRoot.children.find(child => child.id === 'missing_text' && child.isConnected) || null;
        if (selector === '#patient_button_form') return missionRoot.patientForm?.isConnected === false ? null : missionRoot.patientForm;
        if (selector === '#patient_button_text') return missionRoot.patientText?.isConnected === false ? null : missionRoot.patientText;
        if (selector === '[data-mcms-requirements-anchor="1"]') return missionRoot.children.find(child => child.getAttribute?.('data-mcms-requirements-anchor') === '1' && child.isConnected) || null;
        return null;
    };
    missionRoot.queryAllHandler = selector => {
        if (selector.includes('.vehicle_checkbox')) return missionRoot.selectedUnits;
        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;
        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;
        return [];
    };
    return { root: missionRoot, mount: missionRoot };
}


// Issue #282: maritime authoritative labels, trailer identity and screenshot regression.
{
const maritimeDoc = new FakeDocument();
maritimeDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/282' } };
const inlandDefinition = api.definitions.find(definition => definition.key === 'boat-or-inland');
const seagoingDefinition = api.definitions.find(definition => definition.key === 'ilb-or-alb');
assert.strictEqual(inlandDefinition.label, 'Inland Rescue Boat (Trailer)', 'authoritative inland label is canonical');
assert.strictEqual(seagoingDefinition.label, 'Seagoing Vessel', 'authoritative seagoing label is canonical');

const zero = api.capacity(0, 0, true);
const one = api.capacity(1, 1, true);
const three = api.capacity(3, 3, true);
const inlandRequirement = { key: 'boat-or-inland', requirement: 'Inland Rescue Boat (Trailer)', missing: 3, group: 'vehicles', definition: inlandDefinition };
const screenshotRow = api.coverageRow(inlandRequirement, one, zero, zero, three);
assert.strictEqual(screenshotRow.covered, false, 'Required 3 with Selected 1 is not covered');
assert.strictEqual(screenshotRow.definitelyOpen, true, 'known maritime shortage is definitely open');
assert.strictEqual(screenshotRow.stillNeededText, '2', 'screenshot shortage remains two');
const screenshotPanel = api.panelHtml([screenshotRow], []);
assert(screenshotPanel.html.includes('1 outstanding · 0/1 covered'), 'screenshot summary reports zero covered');
assert(!screenshotPanel.html.includes('1/1 covered'), 'screenshot summary never reports the open row as covered');

const towOnlyUnit = {
    typeId: 66,
    vehicleId: 28201,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(),
    arrCapabilities: new Set(),
    arrCapabilityKnown: true,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set([67]),
    staff: null,
    contributionKey: 'pair:28201:28202'
};
const trailerUnit = {
    ...towOnlyUnit,
    typeId: 67,
    vehicleId: 28202,
    compatibleTractiveTypes: new Set(),
    contributionKey: 'pair:28201:28202'
};
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [towOnlyUnit]).min, 0, 'tow-only selection contributes no inland boat capacity');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [towOnlyUnit]).max, 0, 'tow-only exclusion is exact');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [towOnlyUnit, trailerUnit]).min, 1, 'trailer and tow pair contributes exactly one');
const randomTowOnly = { ...towOnlyUnit, compatibleTractiveTypes: new Set([67, 74]), contributionKey: 'vehicle:28203' };
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [randomTowOnly]).min, 0, 'random tractive compatibility cannot replace the maritime asset');

const maritimeCandidate = makeMissionCandidate(maritimeDoc, '3 Inland Rescue Boats (Trailer)');
const selected67 = makeVehicleElement(maritimeDoc, 28211, 67);
selected67.row.textContent = selected67.row.innerText = 'Custom Harbour Asset';
const responding74 = makeVehicleElement(maritimeDoc, 28212, 74, { typeOnRow: true });
responding74.row.setAttribute('data-vehicle-id', '28212');
const onSite67 = makeVehicleElement(maritimeDoc, 28213, 67, { typeOnRow: true });
onSite67.row.setAttribute('data-vehicle-id', '28213');
maritimeCandidate.root.selectedUnits = [selected67.vehicle];
maritimeCandidate.root.enRouteRows = [responding74.row];
maritimeCandidate.root.onSiteRows = [onSite67.row];
// MissionChief live missing excludes the one asset already on site.
const inlandOperationalRequirement = { ...inlandRequirement, missing: 2 };
const inlandParsed = { requirements: [inlandOperationalRequirement], unresolved: [] };
const inlandCatalogue = { requirements: [{ key: 'boat-or-inland', baseline: 3, missing: 3 }] };
let maritimeRow = api.resolve(maritimeCandidate, inlandParsed, inlandCatalogue)[0];
assert.strictEqual(maritimeRow.selectedMin, 1, 'custom-caption type 67 selected capacity resolves');
assert.strictEqual(maritimeRow.respondingMin, 1, 'type 74 responding capacity resolves');
assert.strictEqual(maritimeRow.onSiteMin, 1, 'type 67 on-site capacity resolves');
assert.strictEqual(maritimeRow.stillNeededText, '0', 'mixed type 67/74 buckets satisfy quantity three');
assert.strictEqual(maritimeRow.covered, true, 'mixed maritime assets cover requirement');

const seagoingCandidate = makeMissionCandidate(maritimeDoc, '1 Seagoing Vessel');
const ilb = makeVehicleElement(maritimeDoc, 28221, 68);
const alb = makeVehicleElement(maritimeDoc, 28222, 69, { typeOnRow: true });
alb.row.setAttribute('data-vehicle-id', '28222');
const seagoingRequirement = { key: 'ilb-or-alb', requirement: 'Seagoing Vessel', missing: 1, group: 'vehicles', definition: seagoingDefinition };
const seagoingParsed = { requirements: [seagoingRequirement], unresolved: [] };
const seagoingCatalogue = { requirements: [{ key: 'ilb-or-alb', baseline: 1, missing: 1 }] };
seagoingCandidate.root.selectedUnits = [ilb.vehicle];
maritimeRow = api.resolve(seagoingCandidate, seagoingParsed, seagoingCatalogue)[0];
assert.strictEqual(maritimeRow.selectedMin, 1, 'selected ILB satisfies Seagoing Vessel');
assert.strictEqual(maritimeRow.stillNeededText, '0', 'selected ILB clears Seagoing Vessel');
seagoingCandidate.root.selectedUnits = [];
seagoingCandidate.root.enRouteRows = [alb.row];
maritimeRow = api.resolve(seagoingCandidate, seagoingParsed, seagoingCatalogue)[0];
assert.strictEqual(maritimeRow.respondingMin, 1, 'responding ALB satisfies Seagoing Vessel');
seagoingCandidate.root.enRouteRows = [];
seagoingCandidate.root.onSiteRows = [alb.row];
maritimeRow = api.resolve(seagoingCandidate, seagoingParsed, seagoingCatalogue)[0];
assert.strictEqual(maritimeRow.onSiteMin, 1, 'on-site ALB satisfies Seagoing Vessel');

const unknownMaritime = api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [{
    typeId: -1,
    vehicleId: -1,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(),
    arrCapabilities: new Set(),
    arrCapabilityKnown: false,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set(),
    staff: null,
    contributionKey: 'element:unknown-maritime'
}]);
assert.strictEqual(unknownMaritime.min, 0, 'malformed maritime evidence contributes no confirmed capacity');
assert.strictEqual(unknownMaritime.max, null, 'malformed maritime evidence remains fail-closed');
}


// Issue #282: Police Sergeant capability survives Selected -> Responding -> On site.
{
const sergeantDoc = new FakeDocument();
sergeantDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/282-sergeant' } };
const sergeantCandidate = makeMissionCandidate(sergeantDoc, '2 Police Sergeants');
const sergeantDefinition = api.definitions.find(definition => (definition.training || []).includes('police_sergeant'));
assert(sergeantDefinition, 'Police Sergeant definition exists');
assert((sergeantDefinition.arrAttributes || []).includes('police_sergeant'), 'Police Sergeant exposes its ARR attribute');
const cacheSergeant = id => api.vehicleApiCache.set(String(id), { id, vehicle_type: 8, assigned_personnel_count: 1 });

const respondingAssignment = makeVehicleElement(sergeantDoc, 282401, 8);
respondingAssignment.vehicle.classList.values.add('vehicle_checkbox');
respondingAssignment.vehicle.matchSet.add('.vehicle_checkbox');
respondingAssignment.vehicle.checked = false;
respondingAssignment.vehicle.setAttribute('police_sergeant', '1');
const respondingSergeant = makeVehicleElement(sergeantDoc, 282401, 8, { typeOnRow: true });
respondingSergeant.row.setAttribute('data-vehicle-id', '282401');
cacheSergeant(282401);

const onSiteSergeants = [];
for (let index = 0; index < 3; index += 1) {
    const id = 282410 + index;
    const unit = makeVehicleElement(sergeantDoc, id, 8, { typeOnRow: true });
    unit.row.setAttribute('data-vehicle-id', String(id));
    unit.row.setAttribute('police_sergeant', '1');
    cacheSergeant(id);
    onSiteSergeants.push(unit.row);
}

sergeantCandidate.root.selectedUnits = [respondingAssignment.vehicle];
sergeantCandidate.root.enRouteRows = [respondingSergeant.row];
sergeantCandidate.root.onSiteRows = onSiteSergeants;
const sergeantParsed = {
    requirements: [{ key: sergeantDefinition.key, requirement: 'Police Sergeant', missing: 2, group: 'staff', definition: sergeantDefinition, statedRequirement: true }],
    unresolved: []
};
const sergeantCatalogue = { requirements: [{ key: sergeantDefinition.key, baseline: 5, missing: 5 }] };
let sergeantRow = api.resolve(sergeantCandidate, sergeantParsed, sergeantCatalogue)[0];
assert.strictEqual(sergeantRow.requiredText, '5', 'Police Sergeant total required remains five');
assert.strictEqual(sergeantRow.onSiteText, '3', 'three on-site Police Sergeants are counted');
assert.strictEqual(sergeantRow.respondingText, '1', 'travelling Police Sergeant is counted through matching vehicle identity');
assert.strictEqual(sergeantRow.selectedText, '0', 'unchecked travelling assignment is not left in Selected');
assert.strictEqual(sergeantRow.stillNeededText, '1', '5 required minus 3 on site and 1 responding leaves one');
assert.strictEqual(sergeantRow.covered, false, 'one remaining Police Sergeant keeps row outstanding');

const respondingState = api.arrCapabilityState(respondingSergeant.row, sergeantCandidate, 282401);
assert.strictEqual(respondingState.authoritative, true, 'matching dispatch checkbox is authoritative capability evidence');
assert(respondingState.values.has('police sergeant'), 'matching dispatch checkbox supplies Police Sergeant capability');

respondingAssignment.vehicle.checked = true;
sergeantCandidate.root.enRouteRows = [];
sergeantCandidate.root.onSiteRows = [];
sergeantRow = api.resolve(sergeantCandidate, {
    requirements: [{ key: sergeantDefinition.key, requirement: 'Police Sergeant', missing: 1, group: 'staff', definition: sergeantDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: sergeantDefinition.key, baseline: 1, missing: 1 }] })[0];
assert.strictEqual(sergeantRow.selectedText, '1', 'Police Sergeant first appears in Selected');
assert.strictEqual(sergeantRow.respondingText, '0', 'selected Police Sergeant is not responding');

respondingAssignment.vehicle.checked = false;
sergeantCandidate.root.enRouteRows = [respondingSergeant.row];
sergeantRow = api.resolve(sergeantCandidate, {
    requirements: [{ key: sergeantDefinition.key, requirement: 'Police Sergeant', missing: 1, group: 'staff', definition: sergeantDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: sergeantDefinition.key, baseline: 1, missing: 1 }] })[0];
assert.strictEqual(sergeantRow.selectedText, '0', 'dispatch removes Police Sergeant from Selected');
assert.strictEqual(sergeantRow.respondingText, '1', 'dispatch moves Police Sergeant into Responding');

sergeantCandidate.root.enRouteRows = [];
respondingSergeant.row.setAttribute('police_sergeant', '1');
sergeantCandidate.root.onSiteRows = [respondingSergeant.row];
sergeantRow = api.resolve(sergeantCandidate, {
    requirements: [{ key: sergeantDefinition.key, requirement: 'Police Sergeant', missing: 0, group: 'staff', definition: sergeantDefinition, statedRequirement: true }],
    unresolved: []
}, { requirements: [{ key: sergeantDefinition.key, baseline: 1, missing: 1 }] })[0];
assert.strictEqual(sergeantRow.respondingText, '0', 'arrival removes Police Sergeant from Responding');
assert.strictEqual(sergeantRow.onSiteText, '1', 'arrival moves Police Sergeant into On site');

const genericPoliceOnly = api.aggregate({ group: 'staff', definition: sergeantDefinition }, [{
    typeId: 8,
    vehicleId: 282499,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(),
    arrCapabilities: new Set(),
    arrCapabilityKnown: true,
    knownDefinitionKeys: new Set(),
    staff: api.capacity(1, 1, true),
    contributionKey: 'vehicle:282499'
}]);
assert.strictEqual(genericPoliceOnly.min, 0, 'generic Police Officer is not credited as Police Sergeant');
assert.strictEqual(genericPoliceOnly.max, 0, 'generic Police Officer exclusion is exact');
}


const issue169Doc = new FakeDocument();
issue169Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/' }, navigator: context.pageWindow.navigator, innerWidth: 1600, innerHeight: 900 };
const issue169Root = new FakeElement('form', issue169Doc);
issue169Root.setAttribute('action', '/missions/255577319');
issue169Root.matchSet.add('form[action*="/missions/"]');
const issue169Title = new FakeElement('h1', issue169Doc);
issue169Title.id = 'mission_caption';
const issue169Address = new FakeElement('div', issue169Doc);
issue169Address.id = 'mission_address';
const issue169Source = new FakeElement('div', issue169Doc);
issue169Source.id = 'missing_text';
issue169Source.textContent = issue169Source.innerText = '3 Police cars, 2 4x4 Vehicles';
issue169Source.queryAllHandler = () => [];
const issue169Generic = new FakeElement('div', issue169Doc);
issue169Generic.id = 'incident_note';
for (const node of [issue169Title, issue169Address, issue169Source, issue169Generic]) issue169Root.appendChild(node);
issue169Root.queryHandler = selector => {
    if (selector === '#missing_text') return issue169Source;
    if (selector.includes('#mission_address')) return issue169Address;
    if (selector.includes('#mission_caption')) return issue169Title;
    if (selector === '[data-mcms-requirements-anchor="1"]') return issue169Root.children.find(child => child.getAttribute?.('data-mcms-requirements-anchor') === '1') || null;
    return null;
};
issue169Root.queryAllHandler = selector => selector.includes('.vehicle_checkbox') || selector.includes('#mission_vehicle_') ? [] : [];
const issue169Candidate = { root: issue169Root, mount: issue169Root, source: issue169Generic, missionId: 255577319 };
assert.strictEqual(api.sourceForCandidate(issue169Candidate), issue169Source, 'native source outranks generic lightbox source');
candidates = [issue169Candidate];
api.scan();
flushAnimationFrames();
const issue169Record = Array.from(api.records.values())[0];
const issue169PanelIndex = issue169Root.children.indexOf(issue169Record.panel);
assert.strictEqual(issue169Root.children[issue169PanelIndex + 1], issue169Source, 'panel mounts immediately before native missing_text');
assert(issue169Root.children.indexOf(issue169Address) < issue169PanelIndex, 'panel remains below the mission address');
api.clear();

const issue171Doc = new FakeDocument();
issue171Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/' }, navigator: context.pageWindow.navigator, innerWidth: 1600, innerHeight: 900 };
const issue171Root = new FakeElement('form', issue171Doc);
const issue171MissionSelector = '#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]';
issue171Root.matchSet.add(issue171MissionSelector);
issue171Root.setAttribute('action', '/missions/255577320');
const issue171Title = new FakeElement('h1', issue171Doc);
issue171Title.id = 'mission_caption';
const issue171Address = new FakeElement('div', issue171Doc);
issue171Address.id = 'mission_address';
const issue171Source = new FakeElement('div', issue171Doc);
issue171Source.id = 'missing_text';
issue171Source.textContent = issue171Source.innerText = 'Missing Vehicles: 3 Police cars';
issue171Source.queryAllHandler = () => [];
const issue171VehicleArea = new FakeElement('div', issue171Doc);
issue171VehicleArea.id = 'available_units';
const issue171Table = new FakeElement('table', issue171Doc);
const issue171Body = new FakeElement('tbody', issue171Doc);
issue171Body.id = 'vehicle_show_table_body_all';
issue171Root.appendChild(issue171Title);
issue171Root.appendChild(issue171Address);
issue171Root.appendChild(issue171Source);
issue171Root.appendChild(issue171VehicleArea);
issue171VehicleArea.appendChild(issue171Table);
issue171Table.appendChild(issue171Body);
issue171Body.closestMap.set(issue171MissionSelector, issue171Root);
issue171Root.queryHandler = selector => {
    if (selector === '#missing_text') return issue171Source;
    if (selector.includes('#mission_address')) return issue171Address;
    if (selector.includes('#mission_caption')) return issue171Title;
    if (selector.includes('#vehicle_show_table_body_all')) return issue171Body;
    if (selector === issue171MissionSelector) return issue171Root;
    if (selector === '[data-mcms-requirements-anchor="1"]') return issue171Root.children.find(child => child.getAttribute?.('data-mcms-requirements-anchor') === '1') || null;
    return null;
};
issue171Root.queryAllHandler = selector => selector.includes('.vehicle_checkbox') || selector.includes('#mission_vehicle_') ? [] : [];
const issue171NestedCandidate = { root: issue171Body, mount: issue171Body, missionId: 255577320 };
assert.strictEqual(api.candidateRoot(issue171NestedCandidate), issue171Root, 'nested AJAX vehicle candidate promotes to mission root');
const issue171Placement = api.placement(issue171NestedCandidate, null);
assert.strictEqual(issue171Placement.parent, issue171Root, 'nested AJAX placement uses mission root');
assert.strictEqual(issue171Placement.before, issue171Source, 'nested AJAX placement remains before native requirements');
candidates = [issue171NestedCandidate];
api.scan();
flushAnimationFrames();
const issue171Record = Array.from(api.records.values())[0];
assert.strictEqual(issue171Record.panel.parentNode, issue171Root, 'normal dispatch panel mounts beneath mission header');
issue171Table.insertBefore(issue171Record.panel, issue171Body);
assert.strictEqual(issue171Record.panel.parentNode, issue171Table, 'fixture reproduces invalid table mounting');
api.scan();
flushAnimationFrames();
const issue171RehomedRecord = Array.from(api.records.values())[0];
assert.strictEqual(issue171RehomedRecord.panel.parentNode, issue171Root, 'subsequent scan re-homes a mis-mounted panel');
assert.strictEqual(issue171Record.panel.isConnected, false, 'stale table-mounted panel is removed');
assert(!['TABLE', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TD', 'TH'].includes(issue171RehomedRecord.panel.parentNode.tagName), 'panel host is never table structure');
api.clear();
candidates = [];

const issue171FallbackDoc = new FakeDocument();
issue171FallbackDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/255577321' } };
const issue171FallbackRoot = new FakeElement('div', issue171FallbackDoc);
const issue171WindowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
issue171FallbackRoot.matchSet.add(issue171WindowSelector);
const issue171FallbackArea = new FakeElement('div', issue171FallbackDoc);
const issue171FallbackTable = new FakeElement('table', issue171FallbackDoc);
const issue171FallbackBody = new FakeElement('tbody', issue171FallbackDoc);
issue171FallbackBody.id = 'vehicle_show_table_body_all';
issue171FallbackRoot.appendChild(issue171FallbackArea);
issue171FallbackArea.appendChild(issue171FallbackTable);
issue171FallbackTable.appendChild(issue171FallbackBody);
let issue171HeaderReady = false;
const issue171LateTitle = new FakeElement('h1', issue171FallbackDoc);
issue171LateTitle.id = 'mission_caption';
const issue171LateAddress = new FakeElement('div', issue171FallbackDoc);
issue171LateAddress.id = 'mission_address';
const issue171LateSource = new FakeElement('div', issue171FallbackDoc);
issue171LateSource.id = 'missing_text';
issue171LateSource.textContent = issue171LateSource.innerText = 'Missing Vehicles: 1 Police car';
issue171LateSource.queryAllHandler = () => [];
issue171FallbackRoot.queryHandler = selector => {
    if (selector.includes('#vehicle_show_table_body_all')) return issue171FallbackBody;
    if (!issue171HeaderReady) return null;
    if (selector === '#missing_text') return issue171LateSource;
    if (selector.includes('#mission_address')) return issue171LateAddress;
    if (selector.includes('#mission_caption')) return issue171LateTitle;
    if (selector === '[data-mcms-requirements-anchor="1"]') return issue171FallbackRoot.children.find(child => child.getAttribute?.('data-mcms-requirements-anchor') === '1') || null;
    return null;
};
issue171FallbackRoot.queryAllHandler = () => [];
const issue171FallbackCandidate = { root: issue171FallbackRoot, mount: issue171FallbackRoot, missionId: 255577321 };
assert.strictEqual(api.placement(issue171FallbackCandidate, null), null, 'vehicle-only AJAX state has no valid panel placement');
assert.strictEqual(api.anchorForCandidate(issue171FallbackCandidate), null, 'vehicle-only AJAX state creates no placeholder');
candidates = [issue171FallbackCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'vehicle-only AJAX state creates no record');
issue171HeaderReady = true;
issue171FallbackRoot.insertBefore(issue171LateTitle, issue171FallbackArea);
issue171FallbackRoot.insertBefore(issue171LateAddress, issue171FallbackArea);
issue171FallbackRoot.insertBefore(issue171LateSource, issue171FallbackArea);
api.scan();
flushAnimationFrames();
const issue171LateRecord = Array.from(api.records.values())[0];
assert(issue171LateRecord, 'header-ready AJAX state creates a record');
assert.strictEqual(issue171LateRecord.panel.parentNode, issue171FallbackRoot, 'header-ready panel mounts in mission root');
const issue171LatePanelIndex = issue171FallbackRoot.children.indexOf(issue171LateRecord.panel);
assert(issue171FallbackRoot.children.indexOf(issue171LateAddress) < issue171LatePanelIndex, 'late panel mounts below address');
assert(issue171LatePanelIndex < issue171FallbackRoot.children.indexOf(issue171LateSource), 'late panel mounts before missing_text');
api.clear();
candidates = [];

const delayedDoc = new FakeDocument();
delayedDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/7002' } };
const delayedRoot = new FakeElement('form', delayedDoc);
delayedRoot.setAttribute('action', '/missions/7002');
delayedRoot.matchSet.add('form[action*="/missions/"]');
const delayedTitle = new FakeElement('h1', delayedDoc);
delayedTitle.id = 'mission_caption';
const delayedAddress = new FakeElement('div', delayedDoc);
delayedAddress.id = 'mission_address';
delayedRoot.appendChild(delayedTitle);
delayedRoot.appendChild(delayedAddress);
delayedRoot.queryHandler = selector => selector.includes('#mission_address') ? delayedAddress : selector.includes('#mission_caption') ? delayedTitle : null;
const delayedAnchor = api.anchorForCandidate({ root: delayedRoot, mount: delayedRoot, missionId: 7002 });
assert.strictEqual(delayedRoot.children[delayedRoot.children.indexOf(delayedAddress) + 1], delayedAnchor, 'delayed source anchor follows the address');

const visibilityDoc = new FakeDocument();
visibilityDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/' } };
const staleCandidate = makeMissionCandidate(visibilityDoc, '1 Ambulance');
const visibleCandidate = makeMissionCandidate(visibilityDoc, '2 Fire engines');
staleCandidate.missionId = 8101;
visibleCandidate.missionId = 8102;
staleCandidate.root._visible = false;
visibleCandidate.root._visible = true;
api.records.set(staleCandidate.source, { source: staleCandidate.source });
candidates = [staleCandidate, visibleCandidate];
assert.strictEqual(api.windowCandidates()[0].root, visibleCandidate.root, 'visible AJAX mission outranks hidden existing record');
api.records.clear();
candidates = [];

assert.strictEqual(api.widthMode([{ requirement: 'Police Car' }], []), 'standard', 'ordinary content uses standard width');
assert.strictEqual(api.widthMode([{ requirement: 'Operational Support or Search and Rescue Vehicle' }], []), 'wide', 'long content expands width');
assert.strictEqual(api.widthMode([{ requirement: 'X'.repeat(70) }], []), 'fluid', 'exceptional content may use available width');

const transitionDoc = new FakeDocument();
transitionDoc.defaultView = { location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk' } };
const transitionRoot = new FakeElement('div', transitionDoc);
transitionRoot.queryAllMap.set('a[href*="/einsaetze/"]', [{ getAttribute(name) { return name === 'href' ? '/einsaetze/202' : null; } }]);
const transitionSource = new FakeElement('div', transitionDoc);
transitionRoot.appendChild(transitionSource);
const transitionRecord = {
    candidate: { root: transitionRoot, mount: transitionRoot },
    source: transitionSource,
    catalogueDescriptor: { key: 'https://www.missionchief.co.uk/einsaetze/101' },
    catalogue: { title: 'Previous mission baseline' },
    catalogueState: 'ready'
};
api.catalogueEnsure(transitionRecord);
assert.strictEqual(transitionRecord.catalogueDescriptor.path, '/einsaetze/202', 'new mission descriptor is resolved');
assert.strictEqual(transitionRecord.catalogue, null, 'previous mission catalogue is cleared');

const unitDoc = new FakeDocument();
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


// Issue #226: collapsed or relocated canonical operational tables remain authoritative.
{
const issue226WindowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
const issue226Doc = new FakeDocument();
issue226Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const issue226Candidate = makeMissionCandidate(issue226Doc, '1 Police car');
issue226Candidate.missionId = 6226;
const issue226Window = new FakeElement('div', issue226Doc);
issue226Candidate.root.closestMap.set(issue226WindowSelector, issue226Window);
issue226Candidate.source.closestMap.set(issue226WindowSelector, issue226Window);
issue226Window.appendChild(issue226Candidate.root);
const issue226PoliceDefinition = api.definitions.find(definition => definition.key === 'police-car');
const issue226Parsed = { requirements: [{ key: 'police-car', requirement: 'Police Car', missing: 1, group: 'vehicles', definition: issue226PoliceDefinition, statedRequirement: false, catalogueDerived: true, catalogueProbability: 100 }], unresolved: [] };
const issue226Catalogue = { requirements: [{ key: 'police-car', baseline: 1, missing: 1 }] };

const issue226RespondingBody = new FakeElement('tbody', issue226Doc);
issue226RespondingBody.id = 'mission_vehicle_driving';
issue226Window.appendChild(issue226RespondingBody);
const issue226Responding = makeVehicleElement(issue226Doc, 622601, 8, { typeOnRow: true });
issue226Responding.row.setAttribute('data-vehicle-id', '622601');
issue226Responding.row._visible = false;
issue226Responding.row.closestMap.set('#mission_vehicle_driving', issue226RespondingBody);
issue226Responding.row.closestMap.set('tbody#mission_vehicle_driving', issue226RespondingBody);
issue226Responding.row.closestMap.set(issue226WindowSelector, issue226Window);
issue226RespondingBody.appendChild(issue226Responding.row);
issue226Window.queryAllHandler = selector => selector === 'tbody#mission_vehicle_driving > tr' || selector === '#mission_vehicle_driving > tr' ? [issue226Responding.row] : [];
let issue226Row = api.resolve(issue226Candidate, issue226Parsed, issue226Catalogue)[0];
assert.strictEqual(issue226Row.respondingMin, 1, 'collapsed canonical Units Responding row contributes capacity');
assert.strictEqual(issue226Row.stillNeededText, '0', 'responding capacity fulfils the requirement');
assert.strictEqual(issue226Row.covered, true, 'collapsed responding capacity produces a covered row');
let issue226Panel = api.panelHtml([issue226Row], []);
assert(!issue226Panel.html.includes('Police Car'), 'responding-covered requirement is hidden from the Matrix list');
assert(issue226Panel.html.includes('All currently known requirements are covered.'), 'responding-covered mission retains explicit success state');

const issue226OnSiteBody = new FakeElement('tbody', issue226Doc);
issue226OnSiteBody.id = 'mission_vehicle_at_mission';
issue226Window.appendChild(issue226OnSiteBody);
const issue226OnSite = makeVehicleElement(issue226Doc, 622601, 8, { typeOnRow: true });
issue226OnSite.row.setAttribute('data-vehicle-id', '622601');
issue226OnSite.row._visible = false;
issue226OnSite.row.closestMap.set('#mission_vehicle_at_mission', issue226OnSiteBody);
issue226OnSite.row.closestMap.set('tbody#mission_vehicle_at_mission', issue226OnSiteBody);
issue226OnSite.row.closestMap.set(issue226WindowSelector, issue226Window);
issue226OnSiteBody.appendChild(issue226OnSite.row);
issue226Window.queryAllHandler = selector => selector === 'tbody#mission_vehicle_at_mission > tr' || selector === '#mission_vehicle_at_mission > tr' ? [issue226OnSite.row] : [];
issue226Row = api.resolve(issue226Candidate, issue226Parsed, issue226Catalogue)[0];
assert.strictEqual(issue226Row.onSiteMin, 1, 'collapsed canonical Vehicles on Scene row contributes capacity');
assert.strictEqual(issue226Row.respondingMin, 0, 'on-site state supersedes responding after arrival');
assert.strictEqual(issue226Row.stillNeededText, '0', 'on-site capacity fulfils the requirement');
issue226Panel = api.panelHtml([issue226Row], []);
assert(!issue226Panel.html.includes('Police Car'), 'on-site-covered requirement is hidden from the Matrix list');

issue226Window.queryAllHandler = () => [];
issue226Row = api.resolve(issue226Candidate, issue226Parsed, issue226Catalogue)[0];
assert.strictEqual(issue226Row.stillNeededText, '1', 'shortage returns when committed capacity is removed');
assert(api.panelHtml([issue226Row], []).html.includes('Police Car'), 'hidden row returns after cancellation or departure');

const issue226StaleWindow = new FakeElement('div', issue226Doc);
const issue226StaleBody = new FakeElement('tbody', issue226Doc);
issue226StaleBody.id = 'mission_vehicle_driving_stale';
issue226StaleWindow.appendChild(issue226StaleBody);
const issue226Stale = makeVehicleElement(issue226Doc, 622699, 8, { typeOnRow: true });
issue226Stale.row.setAttribute('data-vehicle-id', '622699');
issue226Stale.row.setAttribute('data-mission-id', '9999');
issue226Stale.row._visible = false;
issue226Stale.row.closestMap.set('#mission_vehicle_driving', issue226StaleBody);
issue226Stale.row.closestMap.set(issue226WindowSelector, issue226StaleWindow);
issue226StaleBody.appendChild(issue226Stale.row);
assert.strictEqual(
    api.operationalActive(issue226Stale.row, issue226Candidate, { doc: issue226Doc, activeWindow: issue226Window }, 'responding'),
    false,
    'hidden stale operational table from another mission remains excluded'
);
}

const personnelDoc = new FakeDocument();
personnelDoc.defaultView = { MutationObserver: FakeMutationObserver };
const personnelCandidate = makeMissionCandidate(
    personnelDoc,
    'Missing Personnel: 8x Level 1 Public Order Officer, 22x Level 2 Public Order Officer'
);
const personnelParsed = api.parseSource(personnelCandidate.source);
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(personnelParsed.requirements.map(item => ({ key: item.key, missing: item.missing, group: item.group })))),
    [
        { key: 'public-order-level-1', missing: 8, group: 'staff' },
        { key: 'public-order-level-2', missing: 22, group: 'staff' }
    ],
    'unstructured Missing Personnel banner is inferred as staff and parsed in source order'
);
const publicOrderRows = api.resolve(personnelCandidate, personnelParsed);
const level1PublicOrderRow = publicOrderRows.find(row => row.key === 'public-order-level-1');
const level2PublicOrderRow = publicOrderRows.find(row => row.key === 'public-order-level-2');
assert(level1PublicOrderRow.uncertain && level1PublicOrderRow.selectedText === '?' && level1PublicOrderRow.enRouteText === '?', 'unverified Level 1 Public Order capacity remains safely uncertain');
assert.strictEqual(level2PublicOrderRow.uncertain, false, 'verified Level 2 Public Order capacity has an exact empty state');
assert.strictEqual(level2PublicOrderRow.selectedText, '0', 'verified Level 2 Public Order selected capacity starts at zero');
assert.strictEqual(level2PublicOrderRow.respondingText, '0', 'verified Level 2 Public Order responding capacity starts at zero');

const genericCandidate = makeMissionCandidate(personnelDoc, 'Missing Personnel: 3x Specialist Evidence Officer');
const genericParsed = api.parseSource(genericCandidate.source);
assert.strictEqual(genericParsed.requirements.length, 1, 'unknown quantified requirement becomes a visible table row');
assert.strictEqual(genericParsed.requirements[0].requirement, 'Specialist Evidence Officer', 'unknown requirement label is preserved');
assert.strictEqual(genericParsed.requirements[0].missing, 3, 'unknown requirement quantity is preserved');
assert.strictEqual(api.resolve(genericCandidate, genericParsed)[0].uncertain, true, 'unknown requirement cannot become falsely covered');


{
function attachPatientSummary(candidate, totalText, detailText = '') {
    const doc = candidate.root.ownerDocument;
    const form = new FakeElement('div', doc);
    form.id = 'patient_button_form';
    const text = new FakeElement('span', doc);
    text.id = 'patient_button_text';
    const strong = new FakeElement('strong', doc);
    strong.textContent = strong.innerText = String(totalText || '');
    text.textContent = text.innerText = `${totalText || ''}${detailText ? ` - ${detailText}` : ''}`;
    text.queryMap.set('strong', strong);
    form.queryMap.set('#patient_button_text strong, strong', strong);
    form.queryMap.set('#patient_button_text', text);
    candidate.root.patientForm = form;
    candidate.root.patientText = text;
    candidate.root.appendChild(form);
    form.appendChild(text);
    text.appendChild(strong);
    return { form, text, strong };
}

const patientDoc = new FakeDocument();
patientDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/18101' } };
const patientCandidate = makeMissionCandidate(patientDoc, '');
patientCandidate.missionId = 18101;
const patientNodes = attachPatientSummary(patientCandidate, '1 Patient', '1 Untreated patients');
let patientState = api.patientCount(patientCandidate);
assert.deepStrictEqual(JSON.parse(JSON.stringify({ present: patientState.present, known: patientState.known, count: patientState.count, source: patientState.source })), {
    present: true, known: true, count: 1, source: 'patient-total-strong'
}, 'singular patient total is read from the strong summary rather than untreated text');

patientNodes.strong.textContent = patientNodes.strong.innerText = '3 Patients';
patientNodes.text.textContent = patientNodes.text.innerText = '3 Patients - 1 Untreated patients';
patientState = api.patientCount(patientCandidate);
assert.strictEqual(patientState.count, 3, 'plural patient total is parsed');
let reconciledPatients = api.reconcilePatientDemand({ requirements: [], unresolved: [] }, patientState);
assert.strictEqual(reconciledPatients.requirements.length, 1, 'patient-only mission creates one requirement row');
assert.strictEqual(reconciledPatients.requirements[0].key, 'ambulance', 'patient demand creates the Ambulance row');
assert.strictEqual(reconciledPatients.requirements[0].patientRequired, 3, 'one ambulance is required per patient');
assert.strictEqual(reconciledPatients.requirements[0].requirementSource, 'Patients', 'patient source is retained for the UI');

let patientResolved = api.resolve(patientCandidate, reconciledPatients)[0];
assert.strictEqual(patientResolved.requiredText, '3', 'patient-only demand sets exact required capacity');
assert.strictEqual(patientResolved.stillNeededText, '3', 'three patients with no ambulances need three');
assert.strictEqual(patientResolved.definitelyOpen, true, 'uncovered patient demand keeps the matrix red');

const patientOnSite = makeVehicleElement(patientDoc, 18111, 5);
const patientResponding = makeVehicleElement(patientDoc, 18112, 5);
const patientSelected = makeVehicleElement(patientDoc, 18113, 5);
patientCandidate.root.onSiteRows = [patientOnSite.row];
patientCandidate.root.enRouteRows = [patientResponding.row];
patientCandidate.root.selectedUnits = [patientSelected.vehicle];
patientResolved = api.resolve(patientCandidate, reconciledPatients)[0];
assert.strictEqual(patientResolved.onSiteText, '1', 'on-site ambulance capacity is counted');
assert.strictEqual(patientResolved.respondingText, '1', 'responding ambulance capacity is counted');
assert.strictEqual(patientResolved.selectedText, '1', 'selected ambulance capacity is counted separately');
assert.strictEqual(patientResolved.stillNeededText, '0', 'committed and selected ambulances cover patient demand');
assert.strictEqual(patientResolved.covered, true, 'covered patient demand allows a green row');

const patientAmbulanceDefinition = api.definitions.find(definition => definition.key === 'ambulance');
const statedLower = {
    requirements: [{ key: 'ambulance', requirement: 'Ambulance', missing: 1, group: 'vehicles', definition: patientAmbulanceDefinition }],
    unresolved: []
};
const mergedDemand = api.reconcilePatientDemand(statedLower, patientState);
assert.strictEqual(mergedDemand.requirements.filter(item => item.key === 'ambulance').length, 1, 'stated and patient demand never duplicate the Ambulance row');
assert.strictEqual(mergedDemand.requirements[0].missing, 1, 'stated missing quantity is retained for live reconstruction');
assert.strictEqual(mergedDemand.requirements[0].patientRequired, 3, 'patient total remains the minimum authoritative requirement');
patientCandidate.root.onSiteRows = [];
patientCandidate.root.enRouteRows = [];
patientCandidate.root.selectedUnits = [];
patientResolved = api.resolve(patientCandidate, mergedDemand)[0];
assert.strictEqual(patientResolved.requiredText, '3', 'lower stated requirement does not reduce patient-derived demand');

patientNodes.strong.textContent = patientNodes.strong.innerText = '0 Patients';
patientNodes.text.textContent = patientNodes.text.innerText = '0 Patients - 0 Untreated patients';
const zeroState = api.patientCount(patientCandidate);
assert.strictEqual(api.reconcilePatientDemand({ requirements: [], unresolved: [] }, zeroState).requirements.length, 0, 'zero patients create no synthetic ambulance row');

patientNodes.strong.textContent = patientNodes.strong.innerText = '';
patientNodes.text.textContent = patientNodes.text.innerText = 'Patient details loading';
const unknownState = api.patientCount(patientCandidate);
assert.strictEqual(unknownState.known, false, 'present but unparseable patient summary is unknown');
const unknownDemand = api.reconcilePatientDemand({ requirements: [], unresolved: [] }, unknownState);
assert.strictEqual(unknownDemand.requirements.length, 1, 'unknown patient total still creates a guarded Ambulance row');
assert.strictEqual(unknownDemand.unresolved.length, 1, 'unknown patient total is visible as unresolved');
const unknownResolved = api.resolve(patientCandidate, unknownDemand)[0];
assert.strictEqual(unknownResolved.uncertain, true, 'unknown patient total cannot become covered');
assert.strictEqual(unknownResolved.requiredText, '?', 'unknown patient total displays unknown required capacity');

const transitionRecord = { candidate: patientCandidate, source: patientCandidate.source, missionIdentity: 18101 };
patientNodes.strong.textContent = patientNodes.strong.innerText = '2 Patients';
patientNodes.text.textContent = patientNodes.text.innerText = '2 Patients - 2 Untreated patients';
let transition = api.patientState(transitionRecord, 1000);
assert.strictEqual(transition.count, 2, 'known patient snapshot is stored');
patientCandidate.root.patientForm = null;
patientCandidate.root.patientText = null;
patientNodes.form.isConnected = false;
patientNodes.text.isConnected = false;
transition = api.patientState(transitionRecord, 1100);
assert.strictEqual(transition.count, 2, 'brief same-mission DOM replacement preserves patient demand');
assert.strictEqual(transition.transitional, true, 'bounded replacement state is marked transitional');
const otherMissionCandidate = makeMissionCandidate(patientDoc, '');
otherMissionCandidate.missionId = 18102;
const otherMissionState = api.patientState({ candidate: otherMissionCandidate, source: otherMissionCandidate.source, missionIdentity: 18102 }, 1100);
assert.strictEqual(otherMissionState.count, 0, 'patient snapshot never leaks into a different mission');
transition = api.patientState(transitionRecord, 2501);
assert.strictEqual(transition.count, 0, 'patient snapshot expires after the bounded transition');

const patientRenderDoc = new FakeDocument();
patientRenderDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/18103' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const patientRenderCandidate = makeMissionCandidate(patientRenderDoc, '');
patientRenderCandidate.missionId = 18103;
attachPatientSummary(patientRenderCandidate, '1 Patient', '1 Untreated patients');
candidates = [patientRenderCandidate];
api.scan();
flushAnimationFrames();
const patientRecord = api.records.get(patientRenderCandidate.source);
assert(patientRecord, 'patient-only mission creates a normal Matrix record');
assert(patientRecord.panel.innerHTML.includes('Ambulance'), 'patient-only mission renders an Ambulance row');
assert(!patientRecord.panel.innerHTML.includes('>Patients<'), 'patient-derived row has no visible source badge');
assert(patientRecord.panel.innerHTML.includes('data-requirement-source="patients"'), 'patient-derived row keeps machine-readable provenance');
assert.strictEqual(patientRenderCandidate.root.children.filter(child => child.id === 'mc-map-command-toolkit-mission-requirements').length, 1, 'patient demand uses the existing single Matrix panel');
api.clear();
candidates = [];
}


// Issue #186: live patient nodes outside #mission_form and direct patient flags.
{
const externalDoc = new FakeDocument();
externalDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/18601' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const externalCandidate = makeMissionCandidate(externalDoc, '');
externalCandidate.missionId = 18601;
const externalPanel = new FakeElement('div', externalDoc);
externalPanel.textContent = externalPanel.innerText = '1 Patient Critical Care required: Yes HEMS required: Yes Requires Transport: Yes Ambulance with the patient: Yes Critical Care with the patient: No';
const externalForm = new FakeElement('div', externalDoc);
externalForm.id = 'patient_button_form';
const externalText = new FakeElement('span', externalDoc);
externalText.id = 'patient_button_text';
externalText.textContent = externalText.innerText = '1 Patient - 1 Untreated patients';
const externalStrong = new FakeElement('strong', externalDoc);
externalStrong.textContent = externalStrong.innerText = '1 Patient';
externalText.queryMap.set('strong', externalStrong);
externalForm.queryMap.set('#patient_button_text strong, strong', externalStrong);
externalForm.queryMap.set('#patient_button_text', externalText);
externalDoc.body.appendChild(externalPanel);
externalPanel.appendChild(externalForm);
externalForm.appendChild(externalText);
externalText.appendChild(externalStrong);

const externalCount = api.patientCount(externalCandidate);
assert.strictEqual(externalCount.count, 1, 'document-context fallback reads a patient summary outside #mission_form');
const externalDetails = api.patientDetails(externalCandidate);
assert.strictEqual(externalDetails.criticalCareRequired.yes, 1, 'affirmative Critical Care requirement is parsed');
assert.strictEqual(externalDetails.hemsRequired.yes, 1, 'affirmative HEMS requirement is parsed');
assert.strictEqual(externalDetails.transportRequired.yes, 1, 'affirmative transport requirement is parsed');
assert.strictEqual(externalDetails.ambulanceWithPatient.yes, 1, 'ambulance-with-patient fulfilment is parsed');
assert.strictEqual(externalDetails.criticalCareWithPatient.no, 1, 'negative Critical Care fulfilment is parsed without becoming a requirement');

const externalReconciled = api.reconcilePatientDemand(
    { requirements: [], unresolved: [] },
    { ...externalCount, details: externalDetails }
);
assert.strictEqual(externalReconciled.requirements.filter(item => item.key === 'ambulance').length, 1, 'outside-form patient count creates one Ambulance row');
assert.strictEqual(externalReconciled.requirements.find(item => item.key === 'ambulance').patientRequired, 1, 'outside-form patient count requires one Ambulance');
assert.strictEqual(externalReconciled.requirements.filter(item => item.key === 'hems').length, 1, 'affirmative HEMS creates one HEMS row');
assert.strictEqual(externalReconciled.requirements.filter(item => item.key === 'critical-care-patient').length, 1, 'affirmative Critical Care creates one condition row');
assert.strictEqual(externalReconciled.requirements.filter(item => item.key === 'patient-transport').length, 1, 'affirmative transport creates one condition row');

const externalRows = api.resolve(externalCandidate, externalReconciled);
const transportRow = externalRows.find(item => item.key === 'patient-transport');
const criticalCareRow = externalRows.find(item => item.key === 'critical-care-patient');
assert.strictEqual(transportRow.covered, true, 'Ambulance with the patient fulfils Patient Transport');
assert.strictEqual(transportRow.stillNeededText, '0', 'fulfilled Patient Transport needs zero');
assert.strictEqual(criticalCareRow.definitelyOpen, true, 'explicit Critical Care with patient No leaves Critical Care outstanding');
assert.strictEqual(criticalCareRow.stillNeededText, '1', 'unfulfilled Critical Care still needs one');
assert.strictEqual(api.overallState(externalRows, []), 'danger', 'patient conditions prevent a false green Matrix');

externalPanel.textContent = externalPanel.innerText = '1 Patient Critical Care required: No HEMS required: No Requires Transport: No Ambulance with the patient: No Critical Care with the patient: No';
const negativeDetails = api.patientDetails(externalCandidate);
const negativeReconciled = api.reconcilePatientDemand(
    { requirements: [], unresolved: [] },
    { ...externalCount, details: negativeDetails }
);
assert.strictEqual(negativeReconciled.requirements.filter(item => item.key === 'hems').length, 0, 'No HEMS flag creates no HEMS requirement');
assert.strictEqual(negativeReconciled.requirements.filter(item => item.key === 'critical-care-patient').length, 0, 'No Critical Care flag creates no Critical Care requirement');
assert.strictEqual(negativeReconciled.requirements.filter(item => item.key === 'patient-transport').length, 0, 'No transport flag creates no Patient Transport condition');
assert.strictEqual(negativeReconciled.requirements.find(item => item.key === 'ambulance').patientRequired, 1, 'patient total remains authoritative when all direct flags are No');
}
const directDoc = new FakeDocument();
directDoc.defaultView = { MutationObserver: FakeMutationObserver };
const directCandidate = makeMissionCandidate(directDoc, '2 Police cars');
candidates = [];
documentContexts = [directDoc];
const directCandidates = api.windowCandidates();
assert.strictEqual(directCandidates.length, 1, 'Mission Requirements discovers MissionChief #missing_text without Mission Value');
assert.strictEqual(directCandidates[0].source, directCandidate.source, 'direct discovery retains the native MissionChief source');
documentContexts = [];

const policeDoc = new FakeDocument();
policeDoc.defaultView = { MutationObserver: FakeMutationObserver };
const policeCandidate = makeMissionCandidate(policeDoc, '2 Police cars');
const firstPolice = makeVehicleElement(policeDoc, 301, 8, { typeOnRow: true });
const duplicateFirstPolice = makeVehicleElement(policeDoc, 301, 8, { typeOnRow: true });
const secondPolice = makeVehicleElement(policeDoc, 302, 8, { typeOnRow: true });
assert.strictEqual(api.vehicleType(firstPolice.vehicle), 8, 'vehicle type is read from the closest MissionChief row');
const policeDefinition = api.definitions.find(definition => definition.key === 'police-car');
const policeParsed = {
    requirements: [{ key: 'police-car', requirement: 'Police Car', missing: 2, group: 'vehicles', definition: policeDefinition }],
    unresolved: []
};
policeCandidate.root.selectedUnits = [firstPolice.vehicle, duplicateFirstPolice.vehicle];
let policeResolved = api.resolve(policeCandidate, policeParsed)[0];
assert.strictEqual(policeResolved.selectedMin, 1, 'duplicate normal/occupied representation of one vehicle counts once');
assert.strictEqual(policeResolved.covered, false, 'one selected police car does not cover two required');
policeCandidate.root.selectedUnits = [firstPolice.vehicle, duplicateFirstPolice.vehicle, secondPolice.vehicle];
policeResolved = api.resolve(policeCandidate, policeParsed)[0];
assert.strictEqual(policeResolved.selectedMin, 2, 'selecting a second unique police car updates Selected to two');
assert.strictEqual(policeResolved.covered, true, 'two selected police cars cover two required');
policeCandidate.root.selectedUnits = [secondPolice.vehicle];
policeResolved = api.resolve(policeCandidate, policeParsed)[0];
assert.strictEqual(policeResolved.selectedMin, 1, 'deselecting one police car updates Selected back to one');


// Issue #212: checked Available Units can be siblings of the narrow mission content root.
{
const issue212Doc = new FakeDocument();
issue212Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk', pathname: '/missions/21201' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const issue212Candidate = makeMissionCandidate(issue212Doc, '');
issue212Candidate.missionId = 21201;
const issue212WindowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
const issue212OuterWindow = new FakeElement('div', issue212Doc);
issue212OuterWindow.id = 'lightbox_box';
const issue212InnerWindow = new FakeElement('div', issue212Doc);
issue212InnerWindow.className = 'lightbox_content';
issue212OuterWindow.closestMap.set(issue212WindowSelector, issue212OuterWindow);
issue212InnerWindow.closestMap.set(issue212WindowSelector, issue212InnerWindow);
issue212Candidate.root.closestMap.set(issue212WindowSelector, issue212InnerWindow);
issue212Candidate.source.closestMap.set(issue212WindowSelector, issue212InnerWindow);
issue212Doc.body.appendChild(issue212OuterWindow);
issue212OuterWindow.appendChild(issue212InnerWindow);
issue212InnerWindow.appendChild(issue212Candidate.root);
const issue212Available = new FakeElement('tbody', issue212Doc);
issue212Available.id = 'vehicle_show_table_body_all';
issue212OuterWindow.appendChild(issue212Available);
const issue212Police = makeVehicleElement(issue212Doc, 212011, 8, { typeOnRow: true });
const issue212DsuDefinition = api.definitions.find(definition => definition.key === 'dsu');
const issue212Dsu = makeVehicleElement(issue212Doc, 212012, issue212DsuDefinition.types[0], { typeOnRow: true });
const issue212Railway = makeVehicleElement(issue212Doc, 212013, 116, { typeOnRow: true, staff: 2 });
for (const item of [issue212Police, issue212Dsu, issue212Railway]) {
    item.vehicle.checked = true;
    item.vehicle._visible = false;
    item.row.appendChild(item.vehicle);
    issue212Available.appendChild(item.row);
}
issue212Railway.row.setAttribute('data-current-personnel', '2');
issue212Railway.row.textContent = issue212Railway.row.innerText = 'Craigleith Railway-PC-5 [Railway Police Officer]';
let issue212Selected = [issue212Police.vehicle, issue212Dsu.vehicle, issue212Railway.vehicle];
issue212OuterWindow.queryHandler = selector => selector.includes('#vehicle_show_table_body_all') || selector.includes('.vehicle_checkbox') ? issue212Available : null;
issue212OuterWindow.queryAllHandler = selector => selector.includes('.vehicle_checkbox:checked') ? issue212Selected : [];
const issue212Requirements = [
    ['police-car', 'Police Car', 4],
    ['dsu', 'Dog Support Unit (DSU)', 1],
    ['railway-police-officer', 'Railway Police Officer', 8]
].map(([key, requirement, missing]) => ({ key, requirement, missing, group: key === 'railway-police-officer' ? 'staff' : 'vehicles', definition: api.definitions.find(item => item.key === key) }));
const issue212Parsed = { requirements: issue212Requirements, unresolved: [] };
const issue212Catalogue = { requirements: issue212Requirements.map(item => ({ key: item.key, baseline: item.missing, missing: item.missing })) };
let issue212Rows = api.resolve(issue212Candidate, issue212Parsed, issue212Catalogue);
assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 3, 'all selected police-family vehicles contribute to the broad Police Car requirement');
assert.strictEqual(issue212Rows.find(item => item.key === 'dsu').selectedMin, 1, 'outer Available Units DSU is selected');
assert.strictEqual(issue212Rows.find(item => item.key === 'railway-police-officer').selectedMin, 2, 'Railway Police badge and current crew contribute selected trained personnel');
issue212Police.vehicle.checked = false;
issue212Selected = [issue212Dsu.vehicle, issue212Railway.vehicle];
issue212Rows = api.resolve(issue212Candidate, issue212Parsed, issue212Catalogue);
assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 2, 'deselecting the IRV immediately removes one broad Police Car contribution');
assert.strictEqual(issue212Rows.find(item => item.key === 'dsu').selectedMin, 1, 'other selected units remain stable after deselection');
}



function makeCatalogueDocument(page) {
    const sectionNames = {
        reward: 'Reward and Precondition',
        requirements: 'Vehicle and Personnel Requirements',
        other: 'Other information'
    };
    const tables = Object.entries(page.sections).map(([key, entries]) => {
        const rows = [[sectionNames[key], 'Value'], ...entries].map(values => ({
            querySelectorAll(selector) {
                if (selector !== 'th, td') return [];
                return values.map(text => ({ textContent: String(text), innerText: String(text) }));
            }
        }));
        return {
            textContent: [sectionNames[key], 'Value', ...entries.flat()].join(' '),
            innerText: [sectionNames[key], 'Value', ...entries.flat()].join(' '),
            querySelectorAll(selector) { return selector === 'tr' ? rows : []; }
        };
    });
    const links = (page.variations || []).map(item => ({
        textContent: item.title,
        innerText: item.title,
        getAttribute(name) { return name === 'href' ? item.href : null; }
    }));
    return {
        querySelector(selector) {
            return selector.includes('h1') ? { textContent: page.title, innerText: page.title } : null;
        },
        querySelectorAll(selector) {
            if (selector === 'table') return tables;
            if (selector === 'a[href*="/einsaetze/"]') return links;
            return [];
        }
    };
}


// Issue #230: probability, availability and informational metadata never become demand.
{
const issue230Page = {
    title: 'Issue 230 conditional metadata fixture',
    sections: {
        reward: [],
        requirements: [
            ['Required Traffic Cars', '3'],
            ['Probability of Traffic Cars being required', '75'],
            ['Traffic Cars only required, when available', 'Yes'],
            ['Required Police Cars', '5'],
            ['Required Water Carrier', '1'],
            ['Probability that Water Carrier is required', '50%'],
            ['Required Aerial Appliance Truck', '1'],
            ['Probability of Aerial Appliance Truck being required', '5'],
            ['Unknown availability switch', 'Yes']
        ],
        other: [
            ['Probability of transport', '40'],
            ['Critical Care Probability', '25'],
            ['Unknown informational flag', 'Yes']
        ]
    },
    variations: []
};
const issue230Catalogue = api.parseCatalogueDocument(makeCatalogueDocument(issue230Page), { id: 23000 });
const issue230ByKey = new Map(issue230Catalogue.requirements.map(item => [item.key, item]));
assert.strictEqual(issue230ByKey.get('traffic-car')?.baseline, 3, 'Traffic Car quantity remains three');
assert.strictEqual(issue230ByKey.get('traffic-car')?.probability, 75, 'Traffic Car chance is attached separately');
assert.strictEqual(issue230ByKey.get('traffic-car')?.availabilityOnly, true, 'Traffic Car availability qualifier is attached separately');
assert.strictEqual(issue230ByKey.get('water-carrier')?.probability, 50, 'Water Carrier chance is attached separately');
assert.strictEqual(issue230ByKey.get('aerial')?.probability, 5, 'Aerial Appliance chance is attached separately');
assert.strictEqual(issue230ByKey.get('police-car')?.probability, 100, 'unconditional Police Cars remain unconditional');
assert.strictEqual(issue230Catalogue.requirements.some(item => item.baseline === 75), false, '75 percent is never a vehicle count');
assert.strictEqual(issue230Catalogue.unresolved.length, 0, 'availability and unknown informational booleans do not enter unresolved output');
assert(issue230Catalogue.metadata.some(item => item.classification === 'probability' && item.key === 'traffic-car'), 'probability metadata remains typed for diagnostics');
assert(issue230Catalogue.metadata.some(item => item.classification === 'availability' && item.key === 'traffic-car'), 'availability metadata remains typed for diagnostics');

const issue230CatalogueOnly = api.reconcileCatalogue({ requirements: [], unresolved: [] }, issue230Catalogue, 'ready', true);
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(issue230CatalogueOnly.requirements.map(item => item.key))),
    ['police-car'],
    'catalogue-only conditional vehicles are dormant while unconditional demand remains'
);
assert.strictEqual(issue230CatalogueOnly.unresolved.length, 0, 'dormant conditional metadata keeps the Matrix neutral');

const issue230LiveTraffic = api.parseText('2 Traffic Cars', 'vehicles');
const issue230LiveReconciled = api.reconcileCatalogue({ requirements: issue230LiveTraffic.requirements, unresolved: [] }, issue230Catalogue, 'ready', true);
const issue230Traffic = issue230LiveReconciled.requirements.find(item => item.key === 'traffic-car');
assert(issue230Traffic, 'live state activates conditional Traffic Car demand');
assert.strictEqual(issue230Traffic.catalogueProbability, 75, 'activated live row retains chance metadata');
assert.strictEqual(issue230Traffic.catalogueAvailabilityOnly, true, 'activated live row retains availability metadata');
assert.strictEqual(issue230LiveReconciled.requirements.some(item => item.key === 'water-carrier'), false, 'unconfirmed Water Carrier remains dormant');
assert.strictEqual(issue230LiveReconciled.requirements.some(item => item.key === 'aerial'), false, 'unconfirmed Aerial Appliance remains dormant');

const issue230MetadataText = 'Probability of Traffic Cars being required: 75; Traffic Cars only required, when available — Yes; 2 Police Cars';
const issue230MetadataParsed = api.parseText(issue230MetadataText, 'vehicles');
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(issue230MetadataParsed.requirements.map(item => ({ key: item.key, missing: item.missing })))),
    [{ key: 'police-car', missing: 2 }],
    'direct parser removes metadata before capability matching'
);
assert.strictEqual(issue230MetadataParsed.remaining, '', 'removed metadata never leaks into unresolved text');
assert.strictEqual(api.parseText('75 Probability of Traffic Cars being required', 'vehicles').requirements.length, 0, 'leading percentage is not parsed as quantity');
assert.strictEqual(api.parseText('Traffic Cars only required when available: Yes', 'vehicles').remaining, '', 'availability qualifier is consumed as metadata');
assert.strictEqual(api.catalogueRequirement('Probability of Traffic Cars being required', '75'), null, 'catalogue requirement parser rejects probability rows directly');

const issue230SourceDoc = new FakeDocument();
const issue230SourceCandidate = makeMissionCandidate(issue230SourceDoc, issue230MetadataText);
const issue230SourceParsed = api.parseSource(issue230SourceCandidate.source);
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(issue230SourceParsed.requirements.map(item => ({ key: item.key, missing: item.missing })))),
    [{ key: 'police-car', missing: 2 }],
    'normal mission source excludes probability and availability fragments'
);
assert.strictEqual(issue230SourceParsed.unresolved.length, 0, 'normal mission source has no metadata unresolved warning');

const issue230UnconditionalPage = {
    title: 'Issue 230 isolation fixture',
    sections: { reward: [], requirements: [['Required Traffic Cars', '2']], other: [] },
    variations: []
};
const issue230Unconditional = api.parseCatalogueDocument(makeCatalogueDocument(issue230UnconditionalPage), { id: 23001 });
assert.strictEqual(issue230Unconditional.requirements[0].probability, 100, 'conditional modifier state never leaks between missions');
assert.strictEqual(issue230Unconditional.requirements[0].availabilityOnly, false, 'availability state never leaks between missions');
const issue230UnconditionalReconciled = api.reconcileCatalogue({ requirements: [], unresolved: [] }, issue230Unconditional, 'ready', true);
assert.strictEqual(issue230UnconditionalReconciled.requirements[0].key, 'traffic-car', 'unconditional authoritative Traffic Cars remain active');

const issue230PanelRow = {
    key: 'police-car', requirement: 'Police Car', covered: false, definitelyOpen: true, uncertain: false, partial: false,
    requiredText: '5', onSiteText: '0', respondingText: '0', selectedText: '0', stillNeededText: '5'
};
const issue230Panel = api.panelHtml([issue230PanelRow], []);
assert(issue230Panel.html.includes('1 outstanding · 0/1 covered'), 'header totals count only operational rows');
assert(!issue230Panel.html.includes('Probability of') && !issue230Panel.html.includes('only required'), 'metadata is absent from responsive Matrix rendering');
}

// Issue #260: clean labels and typed Mission Info personnel classification.
{
const issue260Page = { title: 'Recorded Issue 260 fixture', sections: { reward: [['Average credits','7500'],['Required Police Stations','8'],['Required Personnel Available','40x Level 2 Public Order Officer 5x Police Sergeant']], requirements: [['Required Police Cars','5']], other: [['Required Personnel','18x Level 2 Public Order Officer 1x Police Sergeant']] }, variations: [] };
const issue260Catalogue = api.parseCatalogueDocument(makeCatalogueDocument(issue260Page), { id: 26000 });
const issue260ByLabel = Object.fromEntries(issue260Catalogue.requirements.map(item => [item.requirement, item.baseline]));
assert.strictEqual(issue260ByLabel['Level 2 Public Order Officer'], 18, 'operational Required Personnel becomes a canonical Level 2 Public Order Officer row');
assert.strictEqual(issue260ByLabel['Police Sergeant'], 1, 'operational Required Personnel becomes a canonical Police Sergeant row');
assert.strictEqual(issue260Catalogue.requirements.some(item => item.baseline === 40), false, 'Required Personnel Available count is excluded completely');
assert.strictEqual(issue260Catalogue.requirements.some(item => item.baseline === 5 && item.group === 'staff'), false, 'spawn-prerequisite Police Sergeant count is not merged with operational demand');
assert.strictEqual(issue260Catalogue.unresolved.some(item => /Personnel Available|40x|5x Police Sergeant/i.test(`${item.label || ''} ${item.value || ''}`)), false, 'spawn prerequisites never enter unresolved output');
assert.strictEqual(issue260Catalogue.preconditions['Required Personnel Available'], '40x Level 2 Public Order Officer 5x Police Sergeant', 'spawn prerequisite remains typed catalogue metadata');
const issue260Reconciled = api.reconcileCatalogue({ requirements: [], unresolved: [] }, issue260Catalogue, 'ready', true);
assert.strictEqual(issue260Reconciled.unresolved.length, 0, 'supported operational personnel reconcile without raw Mission info text');
const issue260Level2 = issue260Catalogue.requirements.find(item => item.key === 'public-order-level-2');
const issue260Sergeant = issue260Catalogue.requirements.find(item => item.key === 'police-sergeant-personnel');
assert.strictEqual(issue260Level2?.definition?.countable, true, 'Level 2 Public Order personnel is live-countable');
assert.strictEqual(issue260Sergeant?.definition?.countable, true, 'Police Sergeant personnel is live-countable');
for (const bucketName of ['Selected','Responding','On site']) {
    const level2Capacity = api.aggregate(issue260Level2, [{ typeId: -1, equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), training: new Set(['level 2 public order']), staff: { min: 1, max: 1, known: true }, contributionKey: `issue260-level2-${bucketName}` }]);
    const sergeantCapacity = api.aggregate(issue260Sergeant, [{ typeId: -1, equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), training: new Set(['police sergeant']), staff: { min: 1, max: 1, known: true }, contributionKey: `issue260-sergeant-${bucketName}` }]);
    assert.strictEqual(level2Capacity.min, 1, `Level 2 Public Order counts in ${bucketName}`);
    assert.strictEqual(sergeantCapacity.min, 1, `Police Sergeant counts in ${bucketName}`);
}
const unsupportedPage = { title: 'Recorded unsupported operational personnel fixture', sections: { reward: [], requirements: [], other: [['Required Personnel','2x Unsupported Tactical Specialist']] }, variations: [] };
const unsupportedCatalogue = api.parseCatalogueDocument(makeCatalogueDocument(unsupportedPage), { id: 26001 });
const unsupportedReconciled = api.reconcileCatalogue({ requirements: [], unresolved: [] }, unsupportedCatalogue, 'ready', true);
assert(unsupportedReconciled.unresolved.some(item => /Unsupported Tactical Specialist/.test(item.text)), 'unsupported operational personnel remain visible');
assert(unsupportedReconciled.unresolved.every(item => !/^Mission info:/i.test(item.text)), 'unsupported operational personnel omit the raw Mission info prefix');
const patientRows = [{ key:'ambulance', requirement:'Ambulance', requirementSource:'Patients', covered:false, definitelyOpen:true, uncertain:false, partial:false, requiredText:'1', onSiteText:'0', respondingText:'0', selectedText:'0', stillNeededText:'1' },{ key:'patient-transport', requirement:'Patient Transport', requirementSource:'Patient details', covered:false, definitelyOpen:true, uncertain:false, partial:false, requiredText:'1', onSiteText:'0', respondingText:'0', selectedText:'0', stillNeededText:'1' }];
const cleanPatientPanel = api.panelHtml(patientRows, []).html;
assert(!cleanPatientPanel.includes('>Patients<') && !cleanPatientPanel.includes('>Patient details<'), 'patient provenance badges are structurally absent');
assert(cleanPatientPanel.includes('data-requirement-source="patients"') && cleanPatientPanel.includes('data-requirement-source="patient-details"'), 'patient provenance remains machine-readable');
assert(cleanPatientPanel.includes('class="mcms-matrix-requirement-name">Ambulance</span>'), 'Ambulance label contains no provenance child');
assert(cleanPatientPanel.includes('class="mcms-matrix-requirement-name">Patient Transport</span>'), 'Patient Transport label contains no provenance child');
}

const parsedCatalogues = new Map();
for (const page of catalogueFixture.pages) {
    const descriptor = { id: page.id, overlayIndex: page.overlayIndex ?? null, path: `/einsaetze/${page.id}`, url: page.sourceUrl };
    const catalogue = api.parseCatalogueDocument(makeCatalogueDocument(page), descriptor);
    parsedCatalogues.set(page.name, catalogue);
    assert.strictEqual(catalogue.title, page.title, `${page.name}: title`);
    const quantities = Object.fromEntries(catalogue.requirements.map(item => [item.key, item.baseline]));
    for (const [key, value] of Object.entries(page.expected)) assert.strictEqual(quantities[key], value, `${page.name}: ${key}`);
    for (const [key, probability] of Object.entries(page.conditional || {})) {
        assert.strictEqual(catalogue.requirements.find(item => item.key === key)?.probability, probability, `${page.name}: conditional probability`);
    }
    assert.strictEqual(catalogue.variations.length, (page.variations || []).length, `${page.name}: variations`);
}

const simpleCatalogue = parsedCatalogues.get('simple fire mission');
assert.strictEqual(simpleCatalogue.averageCredits, 110, 'catalogue average credits');
assert(api.cataloguePanelHtml(simpleCatalogue).html.includes('Official MissionChief catalogue baseline only'), 'catalogue panel clearly marks baseline data');
assert(!api.cataloguePanelHtml(simpleCatalogue).html.includes('Still needed'), 'catalogue baseline must not claim current still-needed quantities');
const comparison = api.catalogueCompare({ requirements: [{ key: 'fire-engine', requirement: 'Fire Engine', missing: 2 }], unresolved: [] }, simpleCatalogue);
assert.strictEqual(comparison.state, 'mismatch', 'live quantity above baseline is reported as a mismatch');

const descriptorDoc = new FakeDocument();
descriptorDoc.defaultView = { location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk' } };
const descriptorRoot = new FakeElement('div', descriptorDoc);
const descriptorLink = { textContent: 'Requirements for this Mission', innerText: 'Requirements for this Mission', getAttribute(name) { return name === 'href' ? '/einsaetze/34?additive_overlays=7&overlay_index=2' : null; } };
descriptorRoot.queryAllMap.set('a[href*="/einsaetze/"]', [descriptorLink]);
const descriptor = api.catalogueDescriptor({ root: descriptorRoot, mount: descriptorRoot });
assert.deepStrictEqual(JSON.parse(JSON.stringify({ id: descriptor.id, overlayIndex: descriptor.overlayIndex, additiveOverlays: descriptor.additiveOverlays, path: descriptor.path })), { id: 34, overlayIndex: 2, additiveOverlays: ['7'], path: '/einsaetze/34?overlay_index=2&additive_overlays=7' }, 'catalogue descriptor preserves mission variation and additive overlays');

api.catalogueCacheStore('fixture-cache', simpleCatalogue, 1000);
assert.strictEqual(api.catalogueCacheLookup('fixture-cache', 1001).stale, false, 'fresh catalogue cache');
assert.strictEqual(api.catalogueCacheLookup('fixture-cache', 1000 + api.catalogueTtl + 1).stale, true, 'expired catalogue remains bounded stale fallback');
assert.strictEqual(api.catalogueFailureFallback('fixture-cache', 1000 + api.catalogueTtl + 1).value.title, 'Bin fire', 'network failure reuses stale catalogue');
assert.strictEqual(api.catalogueCacheLookup('fixture-cache', 1000 + api.catalogueStale + 1), null, 'catalogue cache expires after stale boundary');

const missingDoc = new FakeDocument();
missingDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9901' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const missingCandidate = makeMissionCandidateWithoutSource(missingDoc);
candidates = [missingCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'source-less mission waits for a valid header or native source');

const unsafeSource = new FakeElement('div', missingDoc);
unsafeSource.id = 'missing_text';
unsafeSource.textContent = 'token=secret https://discord.com/api/webhooks/1/abc 55.9533,-3.1883';
unsafeSource.innerText = unsafeSource.textContent;
missingCandidate.root.appendChild(unsafeSource);
api.scan();
flushAnimationFrames();
let missingRecord = Array.from(api.records.values())[0];
assert(missingRecord, 'native source creates a record after source-less wait');
const reportUrl = api.reportUrl(missingRecord, 'token=secret');
assert(reportUrl.startsWith('https://github.com/Conroy1988/missionchief-toolkit-assets/issues/new?'), 'report uses the GitHub issue composer');
const reportParams = new URL(reportUrl).searchParams;
assert.strictEqual(reportParams.get('template'), 'mission-info-missing.yml', 'report selects the repository-owned Mission Info Missing form');
assert.strictEqual(reportParams.get('labels'), null, 'report does not request permission-dependent labels');
assert.strictEqual(reportParams.get('body'), null, 'report diagnostic uses the issue-form field rather than the blank issue body');
assert(reportUrl.length <= 7600, 'report URL remains bounded');
const reportBody = reportParams.get('diagnostic');
assert(!reportBody.includes('secret'), 'report sanitises token values');
assert(!reportBody.includes('discord.com/api/webhooks'), 'report sanitises webhook URLs');
assert(!reportBody.includes('55.9533'), 'report sanitises coordinates');

api.scan();
flushAnimationFrames();
const recovered = Array.from(api.records.values())[0];
assert.strictEqual(recovered.source, unsafeSource, 'a later native source replaces the fallback anchor');
unsafeSource.textContent = '2 Police cars';
unsafeSource.innerText = unsafeSource.textContent;
recovered.startedAt = Date.now() - 2000;
api.scan();
flushAnimationFrames();
assert(Array.from(api.records.values())[0].panel.innerHTML.includes('Police Car'), 'fallback upgrades automatically to the normal matrix');
assert.strictEqual(missingDoc.querySelectorAll('#mc-map-command-toolkit-mission-requirements').length, 1, 'fallback recovery retains one panel');
api.clear();

const emptyDoc = new FakeDocument();
emptyDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9902' } };
const emptyCandidate = makeMissionCandidate(emptyDoc, '');
candidates = [emptyCandidate];
api.scan();
flushAnimationFrames();
let emptyRecord = api.records.get(emptyCandidate.source);
emptyRecord.startedAt = Date.now() - 2000;
api.scan();
flushAnimationFrames();
assert(emptyRecord.panel.innerHTML.includes('No outstanding requirements reported by MissionChief'), 'empty native source is explicit rather than silently removed');
api.clear();

const unparseableDoc = new FakeDocument();
unparseableDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9903' } };
const unparseableCandidate = makeMissionCandidate(unparseableDoc, 'Requirement information is currently unavailable');
candidates = [unparseableCandidate];
api.scan();
flushAnimationFrames();
const unparseableRecord = api.records.get(unparseableCandidate.source);
assert(unparseableRecord.panel.innerHTML.includes('Unable to pull mission requirements'), 'unparseable native text shows the failure state');
assert(unparseableRecord.panel.innerHTML.includes('Report Mission'), 'unparseable native text can be reported');
api.clear();

const canonicalDoc = new FakeDocument();
canonicalDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/7001' } };
const canonicalCandidate = makeMissionCandidate(canonicalDoc, '1 Ambulance');
canonicalCandidate.missionId = 7001;
const stalePanelA = canonicalDoc.createElement('section');
stalePanelA.id = 'mc-map-command-toolkit-mission-requirements';
canonicalCandidate.root.insertBefore(stalePanelA, canonicalCandidate.source);
const stalePanelB = canonicalDoc.createElement('section');
stalePanelB.id = 'mc-map-command-toolkit-mission-requirements';
canonicalCandidate.root.insertBefore(stalePanelB, canonicalCandidate.source);
candidates = [canonicalCandidate];
api.scan();
flushAnimationFrames();
const canonicalPanels = canonicalCandidate.root.children.filter(child => child.id === 'mc-map-command-toolkit-mission-requirements');
assert.strictEqual(canonicalPanels.length, 1, 'pre-existing Toolkit duplicates collapse to one canonical host panel');
assert.strictEqual(api.records.get(canonicalCandidate.source).panel, stalePanelA, 'the first connected host panel is adopted rather than recreated');
api.clear();

const mirrorDocA = new FakeDocument();
const mirrorDocB = new FakeDocument();
mirrorDocA.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/8001' } };
mirrorDocB.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/8001' } };
const mirrorCandidateA = makeMissionCandidate(mirrorDocA, '1 Police Sergeant');
const mirrorCandidateB = makeMissionCandidate(mirrorDocB, '1 Police Sergeant');
mirrorCandidateA.missionId = 8001;
mirrorCandidateB.missionId = 8001;
candidates = [mirrorCandidateA, mirrorCandidateB];
documentContexts = [mirrorDocA, mirrorDocB];
assert.strictEqual(api.windowCandidates().length, 1, 'parent and frame mirrors of one MissionChief mission deduplicate by mission identity');
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'mirrored MissionChief documents create one requirements record');
assert.strictEqual(
    mirrorCandidateA.root.children.filter(child => child.id === 'mc-map-command-toolkit-mission-requirements').length
    + mirrorCandidateB.root.children.filter(child => child.id === 'mc-map-command-toolkit-mission-requirements').length,
    1,
    'mirrored MissionChief documents render one visible requirements panel'
);
api.clear();
documentContexts = [];

const childDoc = new FakeDocument();
childDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9001' } };
const childCandidate = makeMissionCandidate(childDoc, '1 Ambulance');
candidates = [childCandidate];
context.pageWindow.top = {};
assert.strictEqual(api.primaryRuntime(), false, 'child-frame Toolkit runtime is not the Mission Requirements owner');
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'child-frame runtime does not mount a competing requirements panel');
delete context.pageWindow.top;

const lifecycleDoc = new FakeDocument();
lifecycleDoc.defaultView = { MutationObserver: FakeMutationObserver };
const lifecycleCandidate = makeMissionCandidate(lifecycleDoc);
const duplicateCandidate = { root: lifecycleCandidate.root, mount: lifecycleCandidate.mount, source: lifecycleCandidate.source };
candidates = [lifecycleCandidate, duplicateCandidate];
const observerBaseline = FakeMutationObserver.created;
api.observeDocument(lifecycleDoc);
api.observeDocument(lifecycleDoc);
assert.strictEqual(FakeMutationObserver.created, observerBaseline + 1, 'document observer must be installed once');
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'repeated candidates in one document create one record');
assert.strictEqual(lifecycleDoc.querySelectorAll('#mc-map-command-toolkit-mission-requirements').length, 1, 'one requirements panel per document');
assert.strictEqual(lifecycleCandidate.source.dataset.mcmsRequirementsSourceHidden, '1', 'native source is hidden only while Toolkit owns the panel');
const recordObserverCount = FakeMutationObserver.created;
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'repeated scans do not duplicate records');
assert.strictEqual(FakeMutationObserver.created, recordObserverCount, 'repeated scans do not duplicate record observers');

const replacementCandidate = makeMissionCandidate(lifecycleDoc, '2 Fire engines');
lifecycleCandidate.source.isConnected = false;
lifecycleCandidate.root.isConnected = false;
candidates = [replacementCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'mission-window replacement tears down the previous record');
assert.strictEqual(lifecycleDoc.querySelectorAll('#mc-map-command-toolkit-mission-requirements').length, 1, 'mission navigation retains one panel');
assert.strictEqual(replacementCandidate.source.dataset.mcmsRequirementsSourceHidden, '1', 'replacement mission source becomes owned');

replacementCandidate.source._lssmActive = true;
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'LSSM activation after Toolkit load removes the Toolkit panel');
assert.strictEqual(replacementCandidate.source.dataset.mcmsRequirementsSourceHidden, undefined, 'LSSM takeover restores MissionChief source ownership');
replacementCandidate.source._lssmActive = false;
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'Toolkit resumes when the LSSM equivalent is disabled');

const lssmFirstCandidate = makeMissionCandidate(new FakeDocument());
lssmFirstCandidate.root.ownerDocument.defaultView = { MutationObserver: FakeMutationObserver };
lssmFirstCandidate.source._lssmActive = true;
candidates = [lssmFirstCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'LSSM-first load order suppresses the Toolkit panel');

context.state.missionRequirements = false;
candidates = [replacementCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'disabling the feature removes every panel and observer record');
context.state.missionRequirements = true;
assert(listenedEvents.filter(event => event.type === 'change').length === 1, 'delegated checkbox change listener is installed once');
assert(trackedObservers.size >= 1, 'document lifecycle observer remains runtime-owned');


// Issue #183 authoritative Requirements for this Mission reconciliation.
{
const authoritativeMajor = parsedCatalogues.get('personnel-heavy major incident');
const authoritativeOnly = api.reconcileCatalogue({ requirements: [], unresolved: [] }, authoritativeMajor, 'ready', true);
assert.strictEqual(authoritativeOnly.requirements.filter(item => item.key === 'fire-engine').length, 1, 'catalogue-only vehicle requirement is added once');
assert.strictEqual(authoritativeOnly.requirements.filter(item => item.key === 'otl').length, 1, 'catalogue-only personnel requirement is added once');
assert.strictEqual(authoritativeOnly.requirements.filter(item => item.key === 'ambulance-officer').length, 1, 'catalogue-only specialist personnel requirement is retained');
assert(authoritativeOnly.requirements.every(item => item.requirementSource === 'Mission info'), 'catalogue-only rows identify the mission-info source');

const authoritativeDoc = new FakeDocument();
authoritativeDoc.defaultView = { MutationObserver: FakeMutationObserver };
const authoritativeCandidate = makeMissionCandidate(authoritativeDoc, '');
const authoritativeRows = api.resolve(authoritativeCandidate, authoritativeOnly, authoritativeMajor);
assert.strictEqual(authoritativeRows.find(item => item.key === 'fire-engine').requiredText, '10', 'authoritative vehicle baseline becomes Required');
assert.strictEqual(authoritativeRows.find(item => item.key === 'otl').requiredText, '1', 'authoritative personnel baseline becomes Required');
const cleanAuthoritativePanel = api.panelHtml(authoritativeRows, []).html;
assert(!cleanAuthoritativePanel.includes('>Mission info<'), 'normal Matrix does not render mission-info provenance as label text');
assert(cleanAuthoritativePanel.includes('data-requirement-source="mission-info"'), 'mission-info provenance remains machine-readable outside the label');
assert(cleanAuthoritativePanel.includes('class="mcms-matrix-requirement-name">Fire Engine</span>'), 'canonical requirement label remains structurally clean');

const fireDefinition = api.definitions.find(item => item.key === 'fire-engine');
const overlapping = api.reconcileCatalogue({ requirements: [{ key: 'fire-engine', requirement: 'Fire Engine', missing: 2, group: 'vehicles', definition: fireDefinition }], unresolved: [] }, authoritativeMajor, 'ready', true);
assert.strictEqual(overlapping.requirements.filter(item => item.key === 'fire-engine').length, 1, 'live and authoritative rows are not duplicated');
const overlappingRow = api.resolve(authoritativeCandidate, overlapping, authoritativeMajor).find(item => item.key === 'fire-engine');
assert.strictEqual(overlappingRow.requiredText, '10', 'larger authoritative baseline wins over a lower live reconstruction');

const conditionalCatalogue = parsedCatalogues.get('alternative and conditional requirements');
const conditionalParsed = api.reconcileCatalogue({ requirements: [], unresolved: [] }, conditionalCatalogue, 'ready', true);
assert.strictEqual(conditionalCatalogue.requirements.some(item => item.key === 'police-car' && item.probability < 100), true, 'probabilistic Police Car requirement remains typed in Mission Info');
assert.strictEqual(conditionalParsed.requirements.some(item => item.key === 'police-car'), false, 'catalogue-only probabilistic Police Car demand remains dormant');
assert.strictEqual(api.resolve(authoritativeCandidate, conditionalParsed, conditionalCatalogue).some(item => item.key === 'police-car'), false, 'dormant conditional demand creates no Matrix row');

const loadingAuthority = api.reconcileCatalogue({ requirements: [{ key: 'fire-engine', requirement: 'Fire Engine', missing: 1, group: 'vehicles', definition: fireDefinition }], unresolved: [] }, null, 'loading', true);
assert(loadingAuthority.unresolved.some(item => item.authoritativePending), 'Matrix fails closed while Requirements for this Mission is loading');
const failedAuthority = api.reconcileCatalogue({ requirements: [], unresolved: [] }, null, 'error', true);
assert(failedAuthority.unresolved.some(item => /could not be loaded/.test(item.text)), 'failed authoritative source remains visible for manual verification');

const patientCoexistence = api.reconcilePatientDemand(authoritativeOnly, { present: true, known: true, count: 12, source: 'fixture' });
assert.strictEqual(patientCoexistence.requirements.filter(item => item.key === 'ambulance').length, 1, 'patient Ambulance authority coexists without duplication');
assert.strictEqual(patientCoexistence.requirements.find(item => item.key === 'ambulance').patientRequired, 12, 'patient-derived Ambulance demand remains authoritative');

const staleAuthority = api.reconcileCatalogue({ requirements: [], unresolved: [] }, { ...authoritativeMajor, stale: true }, 'stale', true);
assert(staleAuthority.unresolved.some(item => /cached Requirements for this Mission/.test(item.text)), 'stale authoritative data is explicitly identified');
}


// Issues #206 and #207: responding-unit acquisition and authoritative Fight on Train baseline.
{
const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
const issue206Doc = new FakeDocument();
issue206Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk', pathname: '/missions/6206' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const issue206Candidate = makeMissionCandidate(issue206Doc, '2 Police cars');
issue206Candidate.missionId = 6206;
const issue206Window = new FakeElement('div', issue206Doc);
issue206Candidate.root.closestMap.set(windowSelector, issue206Window);
issue206Candidate.source.closestMap.set(windowSelector, issue206Window);
issue206Window.appendChild(issue206Candidate.root);
const issue206Police = makeVehicleElement(issue206Doc, 620601, 8, { typeOnRow: true });
issue206Police.row.matchSet.add('tr');
issue206Police.row.setAttribute('data-vehicle-id', '620601');
issue206Window.appendChild(issue206Police.row);
let issue206RespondingRows = [issue206Police.row];
issue206Window.queryAllHandler = selector => selector === 'tbody#mission_vehicle_driving > tr' ? issue206RespondingRows : [];
const issue206PoliceDefinition = api.definitions.find(definition => definition.key === 'police-car');
const issue206Parsed = { requirements: [{ key: 'police-car', requirement: 'Police Car', missing: 2, group: 'vehicles', definition: issue206PoliceDefinition }], unresolved: [] };
const issue206Catalogue = { requirements: [{ key: 'police-car', baseline: 2, missing: 2 }] };
let issue206Row = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(issue206Row.respondingMin, 1, 'tbody-ID responding table contributes one eligible Police Car');
assert.strictEqual(issue206Row.stillNeededText, '1', 'one responding Police Car reduces two required to one still needed');
issue206RespondingRows = [issue206Police.row, issue206Police.row];
issue206Row = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(issue206Row.respondingMin, 1, 'duplicate responding representation of one vehicle counts once');
issue206RespondingRows = [];
issue206Candidate.root.selectedUnits = [issue206Police.vehicle];
let transitionRow = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(transitionRow.selectedMin + transitionRow.respondingMin + transitionRow.onSiteMin, 1, 'Selected state fulfils one unit');
issue206Candidate.root.selectedUnits = [];
issue206RespondingRows = [issue206Police.row];
transitionRow = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(transitionRow.selectedMin + transitionRow.respondingMin + transitionRow.onSiteMin, 1, 'Selected to Responding preserves fulfilled capacity');
issue206RespondingRows = [];
issue206Candidate.root.onSiteRows = [issue206Police.row];
transitionRow = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(transitionRow.selectedMin + transitionRow.respondingMin + transitionRow.onSiteMin, 1, 'Responding to On site preserves fulfilled capacity');
issue206Candidate.root.onSiteRows = [];
const unknownRow = new FakeElement('tr', issue206Doc);
unknownRow.matchSet.add('tr');
const unknownVehicle = new FakeElement('a', issue206Doc);
unknownVehicle.setAttribute('data-vehicle-id', '620699');
unknownVehicle.closestMap.set('tr', unknownRow);
unknownRow.queryHandler = selector => selector.includes('data-vehicle-id') || selector.includes('/vehicles/') ? unknownVehicle : null;
issue206Window.appendChild(unknownRow);
issue206RespondingRows = [unknownRow];
issue206Row = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(issue206Row.uncertain, true, 'unclassified responding unit produces an amber bounded state instead of false red or green');
const railwayUnit = makeVehicleElement(issue206Doc, 620607, 116, { typeOnRow: true, staff: 4 });
railwayUnit.row.matchSet.add('tr');
railwayUnit.row.setAttribute('data-vehicle-id', '620607');
railwayUnit.row.setAttribute('data-current-personnel', '4');
railwayUnit.row.setAttribute('data-personnel-training', 'Railway Police Officer');
issue206Window.appendChild(railwayUnit.row);
issue206RespondingRows = [railwayUnit.row];
const railwayDefinition = api.definitions.find(definition => definition.key === 'railway-police-officer');
const railwayParsed = { requirements: [{ key: 'railway-police-officer', requirement: 'Railway Police Officer', missing: 8, group: 'staff', definition: railwayDefinition }], unresolved: [] };
const railwayCatalogue = { requirements: [{ key: 'railway-police-officer', baseline: 8, missing: 8 }] };
const railwayRow = api.resolve(issue206Candidate, railwayParsed, railwayCatalogue)[0];
assert.strictEqual(railwayRow.respondingMin, 4, 'responding trained Railway Police personnel contribute their current crew');
assert.strictEqual(railwayRow.stillNeededText, '4', 'four qualified responding personnel leave four still needed');

const fightCatalogue = parsedCatalogues.get('fight on train');
assert(fightCatalogue, 'Fight on Train authoritative fixture is parsed');
const fightQuantities = Object.fromEntries(fightCatalogue.requirements.map(item => [item.key, item.baseline]));
assert.strictEqual(fightQuantities['police-car'], 4, 'Fight on Train requires four Police Cars');
assert.strictEqual(fightQuantities.dsu, 1, 'Fight on Train requires one DSU');
assert.strictEqual(fightQuantities['railway-police-officer'], undefined, 'Fight on Train spawn-availability personnel do not become operational catalogue demand');
const fightCandidate = makeMissionCandidate(new FakeDocument(), '');
fightCandidate.root.ownerDocument.defaultView = { MutationObserver: FakeMutationObserver };
const fightParsed = api.reconcileCatalogue({ requirements: [], unresolved: [] }, fightCatalogue, 'ready', true);
const fightRows = api.resolve(fightCandidate, fightParsed, fightCatalogue);
assert.strictEqual(fightRows.find(item => item.key === 'police-car').requiredText, '4', 'authoritative Police Car baseline reaches Matrix');
assert.strictEqual(fightRows.find(item => item.key === 'dsu').requiredText, '1', 'authoritative DSU baseline reaches Matrix');
assert.strictEqual(fightRows.some(item => item.key === 'railway-police-officer'), false, 'spawn-availability trained personnel never reach Matrix rows');
assert(!api.panelHtml(fightRows, fightParsed.unresolved).html.includes('No outstanding requirements'), 'authoritative Fight on Train data cannot render a false empty state');

const pendingDoc = new FakeDocument();
pendingDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk', pathname: '/missions/6207' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const pendingCandidate = makeMissionCandidate(pendingDoc, '');
pendingCandidate.missionId = 6207;
const pendingLink = { textContent: 'Requirements for this Mission', innerText: 'Requirements for this Mission', getAttribute(name) { return name === 'href' ? '/einsaetze/465' : null; } };
const pendingOriginalQueryAll = pendingCandidate.root.queryAllHandler;
pendingCandidate.root.queryAllHandler = selector => selector === 'a[href*="/einsaetze/"]' ? [pendingLink] : pendingOriginalQueryAll(selector);
candidates = [pendingCandidate];
api.scan();
flushAnimationFrames();
const pendingRecord = api.records.get(pendingCandidate.source);
assert(pendingRecord.panel.innerHTML.includes('Requirements for this Mission could not be loaded'), 'unavailable authority renders unresolved amber content');
assert(!pendingRecord.panel.innerHTML.includes('No outstanding requirements reported by MissionChief'), 'empty live text cannot overwrite pending or failed authoritative source');
api.clear();
}



// Issue #259: pinned LSSM parity for resources, equipment, tractive units and training evidence.
{
const resourceDoc = new FakeDocument();
resourceDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/25901' } };
const resourceCandidate = makeMissionCandidate(resourceDoc, '2,000 litres of water');
resourceCandidate.missionId = 25901;
const holder = new FakeElement('div', resourceDoc);
const metricNodes = { selected: new FakeElement('span', resourceDoc), driving: new FakeElement('span', resourceDoc), missing: new FakeElement('span', resourceDoc) };
metricNodes.selected.textContent = metricNodes.selected.innerText = '250';
metricNodes.driving.textContent = metricNodes.driving.innerText = '500';
metricNodes.missing.textContent = metricNodes.missing.innerText = '2,000';
holder.queryHandler = selector => Object.entries(metricNodes).find(([metric, node]) => node && selector.includes(`_${metric}_`))?.[1] || null;
const originalResourceQuery = resourceCandidate.root.queryHandler;
resourceCandidate.root.queryHandler = selector => /mission_(?:water|foam|pump)_holder/.test(selector) ? holder : originalResourceQuery(selector);
const resourceParsed = api.parseText('2,000 litres of water', 'other');
let resourceRow = api.resolve(resourceCandidate, resourceParsed)[0];
assert.strictEqual(resourceRow.requiredText, '2,500', 'resource required total reconstructs missing plus driving');
assert.strictEqual(resourceRow.respondingText, '500', 'resource driving progress is Responding');
assert.strictEqual(resourceRow.selectedText, '250', 'resource selected progress is Selected');
assert.strictEqual(resourceRow.onSiteText, '0', 'resource bar remains exact without a separate on-site metric');
assert.strictEqual(resourceRow.stillNeededText, '1,750', 'resource missing value is not double-subtracted');
assert.strictEqual(api.progressValue(resourceCandidate, 'foam', 'selected'), 250, 'generic foam progress selector accepts MissionChief water-bar class contract');
assert.strictEqual(api.progressValue(resourceCandidate, 'pump', 'driving'), 500, 'generic pump progress selector accepts MissionChief water-bar class contract');
metricNodes.missing = null;
resourceRow = api.resolve(resourceCandidate, resourceParsed)[0];
assert.strictEqual(resourceRow.stillNeededText, '?', 'malformed resource holder fails closed');
assert.strictEqual(resourceRow.covered, false, 'malformed resource holder cannot become covered');

const equipmentDoc = new FakeDocument();
equipmentDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/25902' } };
const equipmentCandidate = makeMissionCandidate(equipmentDoc, '1 Drone');
equipmentCandidate.missionId = 25902;
const droneDefinition = api.definitions.find(item => item.key === 'drone');
const droneParsed = { requirements: [{ key: 'drone', requirement: 'Drone', missing: 1, group: 'vehicles', definition: droneDefinition }], unresolved: [] };
const nestedUnit = makeVehicleElement(equipmentDoc, 2590201, -1);
const nestedMarker = new FakeElement('span', equipmentDoc);
nestedMarker.setAttribute('data-equipment-type', 'drone');
const originalNestedQueryAll = nestedUnit.row.queryAllHandler;
nestedUnit.row.queryAllHandler = selector => selector.includes('[data-equipment-type]') ? [nestedMarker] : originalNestedQueryAll(selector);
equipmentCandidate.root.selectedUnits = [nestedUnit.vehicle];
let nestedRow = api.resolve(equipmentCandidate, droneParsed)[0];
assert.strictEqual(nestedRow.selectedMin, 1, 'nested equipment marker counts in Selected');
equipmentCandidate.root.selectedUnits = [];
nestedUnit.row.matchSet.add('tr');
nestedUnit.row.setAttribute('data-vehicle-id', '2590201');
equipmentCandidate.root.enRouteRows = [nestedUnit.row];
nestedRow = api.resolve(equipmentCandidate, droneParsed)[0];
assert.strictEqual(nestedRow.respondingMin, 1, 'nested equipment marker counts in Responding');
equipmentCandidate.root.enRouteRows = [];
equipmentCandidate.root.onSiteRows = [nestedUnit.row];
nestedRow = api.resolve(equipmentCandidate, droneParsed)[0];
assert.strictEqual(nestedRow.onSiteMin, 1, 'nested equipment marker counts On site');
const dualNestedUnit = makeVehicleElement(equipmentDoc, 2590291, 91);
const dualMarker = new FakeElement('span', equipmentDoc);
dualMarker.setAttribute('data-equipment-type', 'drone');
dualNestedUnit.row.queryAllHandler = selector => selector.includes('[data-equipment-type]') ? [dualMarker] : [];
equipmentCandidate.root.onSiteRows = [];
equipmentCandidate.root.selectedUnits = [dualNestedUnit.vehicle];
nestedRow = api.resolve(equipmentCandidate, droneParsed)[0];
assert.strictEqual(nestedRow.selectedMin, 1, 'type and nested equipment evidence from one unit count once');

const guaranteedTractive = api.aggregate(
    { group: 'vehicles', definition: { types: [0, 1, 4], equipment: [], factors: {} } },
    [{ typeId: 84, compatibleTractiveTypes: new Set([0, 1, 4]), equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), staff: null, contributionKey: 'vehicle:random-tractive' }]
);
assert.strictEqual(guaranteedTractive.min, 1, 'random trailer contributes when every compatible tractive type satisfies the requirement');
const partialTractive = api.aggregate(
    { group: 'vehicles', definition: { types: [0], equipment: [], factors: {} } },
    [{ typeId: 84, compatibleTractiveTypes: new Set([0, 1, 4]), equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), staff: null, contributionKey: 'vehicle:random-tractive-partial' }]
);
assert.strictEqual(partialTractive.min, 0, 'random trailer never guesses a capability not shared by every compatible tractive type');

const unqualifiedRow = new FakeElement('tr', equipmentDoc);
unqualifiedRow.textContent = unqualifiedRow.innerText = 'Railway Police Officer';
unqualifiedRow.setAttribute('data-current-personnel', '4');
const unqualifiedElement = new FakeElement('input', equipmentDoc);
unqualifiedElement.closestMap.set('tr', unqualifiedRow);
const unqualifiedTraining = api.metadataValues(unqualifiedElement, 'training');
assert.strictEqual(unqualifiedTraining.size, 0, 'whole-row caption text is not semantic training evidence');
const explicitTraining = new FakeElement('input', equipmentDoc);
explicitTraining.setAttribute('data-personnel-training', 'Railway Police Officer');
assert(api.metadataValues(explicitTraining, 'training').has('railway police officer'), 'explicit native personnel training remains recognised');
}

// Issue #257: official combined Mission Info labels use capability unions.
{
const combinedCapabilities = fixture.combinedVehicleCapabilities;
for (const capability of combinedCapabilities) {
    const definition = api.definitions.find(item => item.key === capability.key);
    assert(definition, `${capability.key}: runtime definition exists`);
    assert.deepStrictEqual(
        Array.from(definition.types || []).sort((a, b) => a - b),
        Array.from(capability.types || []).sort((a, b) => a - b),
        `${capability.key}: accepted vehicle types`
    );
    assert.deepStrictEqual(
        Array.from(definition.equipment || []).sort(),
        Array.from(capability.equipment || []).sort(),
        `${capability.key}: accepted equipment`
    );
    for (const alias of capability.aliases) {
        const parsed = api.parseText(`1 ${alias}`, 'vehicles');
        assert.strictEqual(parsed.remaining, '', `${capability.key}: parser consumes ${alias}`);
        assert.strictEqual(parsed.requirements.length, 1, `${capability.key}: parser creates one row for ${alias}`);
        assert.strictEqual(parsed.requirements[0].key, capability.key, `${capability.key}: parser selects the capability union for ${alias}`);
        const catalogueRequirement = api.catalogueRequirement(alias, '1');
        assert(catalogueRequirement, `${capability.key}: catalogue requirement exists for ${alias}`);
        assert.strictEqual(catalogueRequirement.key, capability.key, `${capability.key}: catalogue requirement uses capability union for ${alias}`);
        assert.strictEqual(catalogueRequirement.catalogueKnown, true, `${capability.key}: catalogue requirement is countable for ${alias}`);
        assert.notStrictEqual(catalogueRequirement.definition.countable, false, `${capability.key}: catalogue requirement is not forced unknown for ${alias}`);
    }
    for (const typeId of capability.types || []) {
        const capacity = api.aggregate(
            { group: 'vehicles', definition },
            [{ typeId, equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), staff: null, contributionKey: `vehicle:${capability.key}:${typeId}` }]
        );
        assert.strictEqual(capacity.min, 1, `${capability.key}: vehicle type ${typeId} contributes one`);
        assert.strictEqual(capacity.max, 1, `${capability.key}: vehicle type ${typeId} remains exact`);
    }
    for (const equipment of capability.equipment || []) {
        const capacity = api.aggregate(
            { group: 'vehicles', definition },
            [{ typeId: -1, equipment: new Set([equipment]), labels: new Set(), knownDefinitionKeys: new Set(), staff: null, contributionKey: `equipment:${capability.key}:${equipment}` }]
        );
        assert.strictEqual(capacity.min, 1, `${capability.key}: equipment ${equipment} contributes one`);
        assert.strictEqual(capacity.max, 1, `${capability.key}: equipment ${equipment} remains exact`);
    }
}

const doc = new FakeDocument();
doc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/25701' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const candidate = makeMissionCandidate(doc, '');
candidate.missionId = 25701;
const definition = api.definitions.find(item => item.key === 'police-helicopter-or-drone');
const requirement = { ...api.catalogueRequirement('Police Helicopters or Drones', '1'), statedRequirement: true };
const parsed = { requirements: [requirement], unresolved: [] };
const catalogue = { requirements: [{ key: requirement.key, baseline: 1, missing: 1 }] };
const resolveRow = () => api.resolve(candidate, parsed, catalogue).find(item => item.key === requirement.key);

for (const typeId of [11, 89, 90, 91]) {
    const selected = makeVehicleElement(doc, 2570100 + typeId, typeId);
    candidate.root.selectedUnits = [selected.vehicle];
    const row = resolveRow();
    assert.strictEqual(row.selectedMin, 1, `selected vehicle type ${typeId} fulfils the combined row`);
    assert.strictEqual(row.selectedMax, 1, `selected vehicle type ${typeId} remains exact`);
    assert.strictEqual(row.stillNeededText, '0', `selected vehicle type ${typeId} clears the shortage`);
}

const equipmentOnly = makeVehicleElement(doc, 2570198, -1, { equipment: ['drone'] });
candidate.root.selectedUnits = [equipmentOnly.vehicle];
let row = resolveRow();
assert.strictEqual(row.selectedMin, 1, 'selected drone equipment fulfils the combined row without a known vehicle type');
assert.strictEqual(row.stillNeededText, '0', 'selected drone equipment clears the shortage');

const dualEvidence = makeVehicleElement(doc, 2570191, 91, { equipment: ['drone'] });
candidate.root.selectedUnits = [dualEvidence.vehicle];
row = resolveRow();
assert.strictEqual(row.selectedMin, 1, 'one police drone with both type and equipment evidence counts once');
assert.strictEqual(row.selectedMax, 1, 'dual police-drone evidence does not widen or double-count capacity');

candidate.root.selectedUnits = [];
row = resolveRow();
assert.strictEqual(row.selectedMin, 0, 'deselecting the combined-capability unit removes Selected capacity');
assert.strictEqual(row.stillNeededText, '1', 'deselecting restores the shortage');

const responding = makeVehicleElement(doc, 2570211, 11, { typeOnRow: true });
responding.row.matchSet.add('tr');
responding.row.setAttribute('data-vehicle-id', '2570211');
candidate.root.enRouteRows = [responding.row];
row = resolveRow();
assert.strictEqual(row.respondingMin, 1, 'responding Police Helicopter fulfils the combined row');
assert.strictEqual(row.stillNeededText, '0', 'responding Police Helicopter clears the shortage');

candidate.root.enRouteRows = [];
const onSite = makeVehicleElement(doc, 2570291, 91, { typeOnRow: true, equipment: ['drone'] });
onSite.row.matchSet.add('tr');
onSite.row.setAttribute('data-vehicle-id', '2570291');
candidate.root.onSiteRows = [onSite.row];
row = resolveRow();
assert.strictEqual(row.onSiteMin, 1, 'on-site Police Drone fulfils the combined row');
assert.strictEqual(row.onSiteMax, 1, 'on-site Police Drone remains exact');
assert.strictEqual(row.stillNeededText, '1', 'live MissionChief shortage remains authoritative after recognising the on-site Police Drone');

candidate.root.onSiteRows = [];
row = resolveRow();
assert.strictEqual(row.onSiteMin, 0, 'removing the on-site Police Drone removes recognised on-site capacity');
assert.strictEqual(row.stillNeededText, '1', 'live MissionChief shortage remains unchanged when the on-site unit is removed');
assert.strictEqual(definition.equipment.includes('drone'), true, 'combined Police Helicopter or Drone definition retains drone equipment capability');
}

console.log('Mission requirements runtime fixtures passed');
