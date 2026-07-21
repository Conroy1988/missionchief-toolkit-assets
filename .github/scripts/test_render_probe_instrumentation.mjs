#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import * as acorn from 'acorn';
import { instrumentSource } from '../../tools/build-render-probe-userscript.mjs';

const fixture = `function updateUI(value) { if (value < 0) throw new Error('bad'); if (!value) return 4; return value + 1; }\nfunction renderOperationalPanels() { return 'ok'; }`;
const events = [];
globalThis.__MCMS_PROFILER__ = {
    beginRender(name) { events.push(['begin', name]); return name; },
    endRender(token) { events.push(['end', token]); },
};
const transformed = instrumentSource(fixture);
assert.deepEqual(transformed.targets, ['renderOperationalPanels', 'updateUI']);
assert.match(transformed.generated, /beginRender\?\.\("updateUI"\)/);
assert.match(transformed.generated, /endRender\?\.\(__mcmsRenderProbeToken_updateUI\)/);
acorn.parse(transformed.generated, { ecmaVersion: 'latest' });
const api = Function(`${transformed.generated}; return { updateUI, renderOperationalPanels };`)();
assert.equal(api.updateUI(0), 4);
assert.equal(api.updateUI(2), 3);
assert.throws(() => api.updateUI(-1), /bad/);
assert.equal(api.renderOperationalPanels(), 'ok');
assert.deepEqual(events, [
    ['begin', 'updateUI'], ['end', 'updateUI'],
    ['begin', 'updateUI'], ['end', 'updateUI'],
    ['begin', 'updateUI'], ['end', 'updateUI'],
    ['begin', 'renderOperationalPanels'], ['end', 'renderOperationalPanels'],
]);
delete globalThis.__MCMS_PROFILER__;

const root = path.resolve(import.meta.dirname, '..', '..');
const sourcePath = path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js');
const sourceBefore = fs.readFileSync(sourcePath, 'utf8');
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'mcms-render-probe-'));
const output = path.join(temp, 'MissionChief_Map_Command_Toolkit.render-probe.user.js');
const manifest = path.join(temp, 'render-probe-manifest.json');
execFileSync(process.execPath, [
    path.join(root, 'tools', 'build-render-probe-userscript.mjs'),
    '--source', sourcePath,
    '--output', output,
    '--manifest', manifest,
], { cwd: root, stdio: 'inherit' });
const sourceAfter = fs.readFileSync(sourcePath, 'utf8');
assert.equal(sourceAfter, sourceBefore, 'canonical source remains byte-identical');
const generated = fs.readFileSync(output, 'utf8');
const metadata = JSON.parse(fs.readFileSync(manifest, 'utf8'));
assert.match(generated, /@name\s+MissionChief Map Command Toolkit \[Render Probe\]/);
assert.equal((generated.match(/beginRender\?\./g) || []).length, 2);
assert.equal((generated.match(/endRender\?\./g) || []).length, 2);
assert.deepEqual(metadata.instrumentedFunctions, ['renderOperationalPanels', 'updateUI']);
assert.equal(metadata.productionSourceModified, false);
acorn.parse(generated, { ecmaVersion: 'latest', sourceType: 'script' });
execFileSync(process.execPath, ['--check', output], { stdio: 'inherit' });
console.log('Render probe instrumentation contracts passed.');
