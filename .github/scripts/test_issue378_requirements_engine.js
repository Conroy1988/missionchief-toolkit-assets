#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '..', '..');
const sourcePath = path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js');
const fixturePath = path.join(root, '.github', 'fixtures', 'issue-378-enhanced-requirements-cases.json');
const source = fs.readFileSync(sourcePath, 'utf8');
const startMarker = '    // Issue #378 enhanced requirements pure engine.';
const endMarker = '    // Issue #378 end enhanced requirements pure engine.';
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker);
if (start < 0 || end <= start) throw new Error('Issue #378 engine markers are missing or invalid');
const block = source.slice(start, end + endMarker.length);
const context = { console };
vm.createContext(context);
vm.runInContext(`${block}\n;globalThis.__issue378Engine = { operationalRequirementCreateModel, operationalRequirementRows, operationalRequirementFingerprint };`, context);
const engine = context.__issue378Engine;
const fixture = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));

function mergeInput(testCase) {
    return {
        catalog: fixture.catalog,
        vehicleTypes: fixture.vehicleTypes,
        ...(testCase.input || {})
    };
}

function assertEqual(actual, expected, label) {
    const actualJson = JSON.stringify(actual);
    const expectedJson = JSON.stringify(expected);
    if (actualJson !== expectedJson) {
        throw new Error(`${label}\nexpected: ${expectedJson}\nactual:   ${actualJson}`);
    }
}

for (const testCase of fixture.cases) {
    const model = engine.operationalRequirementCreateModel(mergeInput(testCase));
    const rows = engine.operationalRequirementRows(model, testCase.options || {});
    const expectedRows = testCase.expect.rows || [];
    for (const expected of expectedRows) {
        const row = rows.find(candidate => candidate.key === expected.key);
        if (!row) throw new Error(`${testCase.name}: missing row ${expected.key}`);
        const projected = {};
        for (const key of Object.keys(expected)) projected[key] = row[key];
        assertEqual(projected, expected, `${testCase.name}: row ${expected.key}`);
    }
    for (const [group, expected] of Object.entries(testCase.expect.remaining || {})) {
        assertEqual(model.requirementTexts[group]?.remaining ?? null, expected, `${testCase.name}: remaining ${group}`);
    }
    const firstFingerprint = engine.operationalRequirementFingerprint(model, testCase.options || {});
    const secondFingerprint = engine.operationalRequirementFingerprint(
        engine.operationalRequirementCreateModel(mergeInput(testCase)),
        testCase.options || {}
    );
    assertEqual(firstFingerprint, secondFingerprint, `${testCase.name}: deterministic fingerprint`);
}

const staffCase = fixture.cases.find(testCase => testCase.name === 'staff minimum and maximum ranges');
const staffModel = engine.operationalRequirementCreateModel(mergeInput(staffCase));
const maxRow = engine.operationalRequirementRows(staffModel, { calcMaxStaff: true }).find(row => row.key === 'firefighters');
assertEqual({ selectedValue: maxRow.selectedValue, covered: maxRow.covered }, { selectedValue: 6, covered: true }, 'staff maximum mode');

if (source.includes('data-mcms-operational-suite') || source.includes('mcms-operational-suite-panel')) {
    throw new Error('Phase 3 engine core must not render a competing operational-suite surface');
}
if (!source.includes('// Issue #133 clean-room live mission requirements matrix.')) {
    throw new Error('Phase 3 engine core must retain the legacy Matrix rollback runtime');
}

console.log(`Issue #378 enhanced requirements engine passed ${fixture.cases.length} deterministic cases.`);
