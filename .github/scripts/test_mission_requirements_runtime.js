#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const fixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-requirements-contract.json'), 'utf8'));
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

const context = {
    console,
    escapeHtml,
    SCRIPT: {
        missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements',
        missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style'
    },
    state: { missionRequirements: true, uiTheme: 'mapCommand' },
    pageWindow: {},
    document: {},
    MutationObserver: class MutationObserver {},
    runtime: { destroyed: false },
    runtimeSetTimeout: () => 1,
    runtimeClearTimeout: () => {},
    runtimeRequestAnimationFrame: callback => { callback(); return 1; },
    runtimeCancelAnimationFrame: () => {},
    runtimeTrackObserver: observer => observer,
    runtimeUntrackObserver: () => {},
    runtimeListen: () => {},
    runtimeOnCleanup: () => {},
    transportSweepDocumentContexts: () => [],
    missionValueWindowCandidates: () => [],
    mutationTouchesSelector: () => false,
    setInnerHtmlIfChanged: () => {},
    isVisible: () => true,
};
vm.createContext(context);
vm.runInContext(
    block + `
this.__mcmsRequirements = {
    definitions: MISSION_REQUIREMENT_DEFINITIONS,
    parseText: missionRequirementsParseText,
    capacity: missionRequirementsCapacity,
    capacityText: missionRequirementsCapacityText,
    coverageRow: missionRequirementsCoverageRow,
    staffCapacity: missionRequirementsStaffCapacity,
    equipmentTypes: missionRequirementsEquipmentTypes,
    vehicleId: missionRequirementsVehicleId,
    aggregate: missionRequirementsAggregate,
    overallState: missionRequirementsOverallState,
    lssmActive: missionRequirementsLssmActive,
    panelHtml: missionRequirementsPanelHtml,
    documentCss: missionRequirementsDocumentCss
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

for (const testCase of fixture.coverageCases) {
    const row = api.coverageRow(
        { key: testCase.name, requirement: testCase.name, missing: testCase.missing, group: 'vehicles', definition: {} },
        testCase.selected,
        testCase.enRoute
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
const lssmSource = {
    matches(selector) { return selector === '.alert-missing-vehicles'; },
    querySelector() { return null; }
};
assert.strictEqual(api.lssmActive({ root: null }, lssmSource), true, 'active LSSM panel is detected');

const html = api.panelHtml([
    api.coverageRow(
        { key: 'ambulance', requirement: 'Ambulance', missing: 1, group: 'vehicles', definition: {} },
        { min: 1, max: 1, known: true },
        { min: 0, max: 0, known: true }
    )
], []);
for (const header of fixture.layout.requiredHeaders) assert(html.html.includes(header), `missing table header: ${header}`);
assert.strictEqual(html.stateName, 'success', 'covered panel state');

const css = api.documentCss().replace(/\s+/g, '').toLowerCase();
const normalPanelRule = css.split('.mcms-req-head', 1)[0];
for (const forbidden of fixture.layout.forbiddenNormalPanelPositioning) {
    assert(!normalPanelRule.includes(forbidden), `normal-flow panel contains ${forbidden}`);
}
assert(normalPanelRule.includes('position:relative!important'), 'normal-flow panel must be relative');
assert(normalPanelRule.includes('[data-mcms-requirements-source-hidden="1"]{display:none!important}'), 'native source hiding must be CSS-owned');
assert(css.includes('@media(max-width:767px)'), 'mobile breakpoint missing');

console.log('Mission requirements runtime fixtures passed');
