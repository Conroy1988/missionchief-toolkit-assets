#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    // Issue #378 complete operational feature suite.');
const end = source.indexOf('    // Issue #378 end complete operational feature suite.', start);
if (start < 0 || end < 0) throw new Error('Issue #378 feature block missing');
const block = source.slice(start, end);
const sandbox = { console, globalThis: null };
sandbox.globalThis = sandbox;
vm.runInNewContext(`${block}\nglobalThis.order = operationalMissionListComputeOrder; globalThis.choose = operationalTransportChooseAction;`, sandbox);
const records = [
  { id: '1', name: 'Bravo', credits: 10, index: 0 },
  { id: '2', name: 'Alpha', credits: 30, index: 1 },
  { id: '3', name: 'Zulu', credits: 20, index: 2 },
];
const ids = rows => Array.from(rows, row => row.id).join(',');
if (ids(sandbox.order(records, 'credits', 'desc', [])) !== '2,3,1') throw new Error('credits-desc sorting failed');
if (ids(sandbox.order(records, 'name', 'asc', ['3'])) !== '3,2,1') throw new Error('starred-first name sorting failed');
const missionSettings = { enabled: true, autoOpenTransportRequest: true, autoClickSuccessButtons: true };
const vehicleSettings = { enabled: true, autoOpenTransportRequest: false, autoClickSuccessButtons: true };
const open = { mode: 'open', token: 'm|open', visible: true, disabled: false };
const success = { mode: 'success', token: 'v|success', visible: true, disabled: false };
if (sandbox.choose('/missions/123', [open], missionSettings, []) !== open) throw new Error('single mission transport-open candidate failed');
if (sandbox.choose('/missions/123', [open, { ...open, token: 'm|open2' }], missionSettings, []) !== null) throw new Error('ambiguous mission action was not rejected');
if (sandbox.choose('/missions/123', [open], missionSettings, ['m|open']) !== null) throw new Error('used mission token was not rejected');
if (sandbox.choose('/vehicles/42/patient/7', [success], vehicleSettings, []) !== success) throw new Error('vehicle success action failed');
if (sandbox.choose('/vehicles/42/patient/7', [success], { ...vehicleSettings, enabled: false }, []) !== null) throw new Error('disabled transport suite still selected an action');
console.log('Issue #378 operational feature runtime fixtures passed.');
