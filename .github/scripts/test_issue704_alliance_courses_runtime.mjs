#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    const ALLIANCE_COURSE_DAY_META');
const end = source.indexOf('    function vehicleTargetInfo(', start);
assert.ok(start >= 0 && end > start, 'Issue #704 Alliance Courses helpers are missing');

const pageWindow = { location: { origin: 'https://www.missionchief.co.uk', href: 'https://www.missionchief.co.uk/' } };
const document = { baseURI: pageWindow.location.href };
const context = vm.createContext({
    console,
    Date,
    Set,
    Map,
    Array,
    Number,
    String,
    Object,
    Promise,
    Error,
    URL,
    URLSearchParams,
    document,
    pageWindow,
    ALLIANCE_COURSE_DAY_OPTIONS: Object.freeze(['today', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']),
    ALLIANCE_COURSE_SHARE_DURATION_OPTIONS: Object.freeze([3600, 43200, 86400, 172800]),
    ALLIANCE_COURSE_DELAY_OPTIONS: Object.freeze([1000, 1500, 2000, 3000, 5000]),
    ALLIANCE_COURSE_SCAN_LIMIT: 150,
    ALLIANCE_COURSE_START_LIMIT: 100,
    ALLIANCE_COURSE_REQUEST_TIMEOUT_MS: 12000,
    state: { allianceCourses: { day: 'today', shareDuration: 86400, delayMs: 1500 } },
    allianceCourseRuntime: { running: false, stopRequested: false, scanPromise: null, queue: [], summary: null, scannedAt: 0, scannedDay: '', processed: 0, created: 0, skipped: 0, errors: 0, log: [] },
    runtime: { destroyed: false },
    renderAllianceCoursesPanel: () => {},
    isAllianceBuildingsPath: () => false,
    showToast: () => {},
    toolkitAnalyticsRecordFeature: () => {},
    escapeHtml: value => String(value),
    setInnerHtmlIfChanged: () => {},
    runtimeDelay: async () => true,
    runtimeFetch: async () => { throw new Error('network use is outside this helper contract'); },
    DOMParser: class {},
});
vm.runInContext(source.slice(start, end), context, { filename: 'issue704-alliance-courses.js' });

assert.equal(context.allianceCourseResolvedDay('today', new Date('2026-08-15T12:00:00Z')), 'sat');
assert.equal(context.allianceCourseResolvedDay('wed', new Date('2026-08-15T12:00:00Z')), 'wed');
assert.equal(context.allianceCourseNameMatchesDay('AF - ARF - 6 - Saturday - 1', 'sat'), true);
assert.equal(context.allianceCourseNameMatchesDay('AE - Drone Operator - 6 - TUE - 1', 'tue'), true);
assert.equal(context.allianceCourseNameMatchesDay('AD - Ambulance Officer - 6 - Saturday - 1', 'sun'), false);

assert.equal(context.allianceCourseDefinitionForName('AD - Critical Care - 6 - Sat - 1', 'ambulance').nativeLabel, 'Critical care');
assert.equal(context.allianceCourseDefinitionForName('AE - # Level 1 Public Order - 6 - SAT - 1', 'police').nativeLabel, 'Level 1 Public Order Training');
assert.equal(context.allianceCourseDefinitionForName('AF - ARF - 6 - Saturday - 1', 'fire').nativeLabel, 'Aircraft Rescue and Firefighting');
assert.equal(context.allianceCourseDefinitionForName('AF - Drone Operator - 6 - Sat - 1', 'fire').nativeLabel, 'Drone Operator Training');
assert.equal(context.allianceCourseDefinitionForName('AI - Coastal Search Advis - 6 - Sat - 1', 'rescue').nativeLabel, 'Coastguard Search Advisor Training');
assert.equal(context.allianceCourseDefinitionForName('AI - SAR Search Management - 6 - Sat - 1', 'rescue').nativeLabel, 'Search Management Training');
assert.equal(context.allianceCourseDefinitionForName('AF - Unknown Specialist - Sat - 1', 'fire'), null);

const classList = values => ({ contains: value => values.includes(value) });
const buildingRow = ({ name, icon, href = '', button = true }) => {
    const nameNode = { textContent: name };
    const nameLink = { textContent: name, classList: classList([]), getAttribute: key => key === 'href' ? `/buildings/name-${name}` : '' };
    const action = { textContent: 'Start a new training course', classList: classList(['btn', 'btn-success']), getAttribute: key => key === 'href' ? href : '' };
    const image = { getAttribute: key => key === 'src' ? `/images/${icon}.png` : '' };
    return {
        querySelector(selector) { return selector === '.search_attribute' ? nameNode : null; },
        querySelectorAll(selector) {
            if (selector === 'img[src]') return [image];
            if (selector === 'a[href*="/buildings/"]') return button ? [nameLink, action] : [nameLink];
            if (selector === 'a.btn-success[href*="/buildings/"]') return button ? [action] : [];
            return [];
        },
    };
};
const rows = [
    buildingRow({ name: 'AF - ARF - 6 - Saturday - 1', icon: 'building_fireschool', href: '/buildings/101' }),
    buildingRow({ name: 'AD - Critical Care - 6 - Sat - 1', icon: 'building_rettungsschule', button: false }),
    buildingRow({ name: 'AE - Unknown Specialist - Sat - 1', icon: 'policechief_building_polizeischule', href: '/buildings/103' }),
    buildingRow({ name: 'AI - Drone Operator - 6 - SAT - 1', icon: 'building_water_rescue_school', href: '/buildings/104' }),
    buildingRow({ name: 'AF - ARF - 6 - Monday - 1', icon: 'building_fireschool', href: '/buildings/105' }),
];
const scanDocument = { querySelectorAll: selector => selector === 'tr.alliance_buildings_table_searchable' ? rows : [] };
const scan = context.buildAllianceCourseQueue(scanDocument, 'sat');
assert.deepEqual(Array.from(scan.queue, item => item.buildingId), ['101', '104']);
assert.deepEqual({ matching: scan.summary.matching, ready: scan.summary.ready, busy: scan.summary.busy, unmapped: scan.summary.unmapped }, { matching: 4, ready: 2, busy: 1, unmapped: 1 });
assert.deepEqual(Array.from(scan.summary.busyNames), ['AD - Critical Care - 6 - Sat - 1'], 'Busy buildings must remain visible in the preview');
assert.deepEqual(Array.from(scan.summary.unmappedNames), ['AE - Unknown Specialist - Sat - 1'], 'Unmapped buildings must remain visible in the preview');
assert.equal(scan.queue[0].nativeLabel, 'Aircraft Rescue and Firefighting');
assert.equal(scan.queue[1].academyKey, 'rescue', 'Academy identity must disambiguate crossover Drone Operator training');

const option = (value, textContent, disabled = false) => ({ value, textContent, disabled });
const selectors = {
    '#building_rooms_use[name="building_rooms_use"]': { options: [option('1', '1'), option('2', '2'), option('4', '4'), option('3', '3')] },
    '#education_select[name="education_select"]': { options: [option('', 'Select an education'), option('arff:future-id', 'Aircraft Rescue and Firefighting (3 days)')] },
    '#alliance_duration[name="alliance[duration]"]': { options: [option('3600', '1 hour'), option('86400', '1 day'), option('172800', '2 days')] },
    '#alliance_cost[name="alliance[cost]"]': { options: [option('0', '0 Credits')] },
    'input[name="authenticity_token"]': { value: 'csrf-token' },
};
const hiddenInputs = [
    { name: 'utf8', value: '✓', disabled: false },
    { name: 'authenticity_token', value: 'csrf-token', disabled: false },
];
const form = {
    getAttribute: key => key === 'action' ? '/buildings/101/education' : '',
    querySelector: selector => selectors[selector] || null,
    querySelectorAll: selector => selector === 'input[type="hidden"][name]' ? hiddenInputs : [],
};
const formDocument = {
    querySelectorAll(selector) {
        if (selector === 'form[action]') return [form];
        if (selector === '#building_schooling_table [sortvalue]') return [{ getAttribute: () => 'Aircraft Rescue and Firefighting' }];
        return [];
    },
};
const prepared = context.prepareAllianceCourseSubmission(formDocument, scan.queue[0], 86400);
const body = new URLSearchParams(prepared.body);
assert.equal(prepared.roomCount, 4, 'The maximum native classroom option must be selected');
assert.equal(prepared.baseline, 1);
assert.equal(body.get('education_select'), 'arff:future-id', 'Opaque native option values must be discovered, never hard-coded');
assert.equal(body.get('building_rooms_use'), '4');
assert.equal(body.get('alliance[duration]'), '86400');
assert.equal(body.get('alliance[cost]'), '0');
assert.equal(body.get('commit'), 'Educate');
assert.equal(prepared.action, 'https://www.missionchief.co.uk/buildings/101/education');

selectors['#education_select[name="education_select"]'] = { options: [option('', 'Select an education'), option('other:1', 'Mobile command (5 days)')] };
assert.throws(
    () => context.prepareAllianceCourseSubmission(formDocument, scan.queue[0], 86400),
    error => error?.allianceCourseSafeSkip === true && error.message.includes('found 0'),
    'A missing exact native label must safely skip rather than guess'
);

console.log('Issue #704 Alliance Courses runtime contract passed: day scan, academy disambiguation, max rooms and native form payload verified');
