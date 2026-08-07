#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    function runtimeFetch(');
const end = source.indexOf('    runtimeOnCleanup(() => {', start);
assert.ok(start >= 0 && end > start, 'Issue #698 bounded runtime fetch helper is missing');

const runtime = { destroyed: false, fetchControllers: new Set() };
let capturedOptions = null;
const pageWindow = {
    AbortController,
    fetch(_input, options) {
        capturedOptions = options;
        return new Promise((_resolve, reject) => {
            options.signal.addEventListener('abort', () => {
                const error = new Error('aborted');
                error.name = 'AbortError';
                reject(error);
            }, { once: true });
        });
    }
};
const context = vm.createContext({
    AbortController,
    Error,
    Number,
    Promise,
    runtime,
    pageWindow,
    runtimeDelay: delay => new Promise(resolve => setTimeout(() => resolve(true), delay))
});
vm.runInContext(source.slice(start, end), context, { filename: 'issue698-bounded-runtime-fetch.js' });

await assert.rejects(
    context.runtimeFetch('/missions/101', { timeoutMs: 20, headers: { Accept: 'text/html' } }),
    error => error?.name === 'AbortError'
);
assert.equal(capturedOptions.timeoutMs, undefined, 'The internal timeout option must not leak into browser fetch');
assert.ok(capturedOptions.signal instanceof AbortSignal, 'The tracked Toolkit controller must own the browser fetch signal');
assert.equal(runtime.fetchControllers.size, 0, 'Timed-out fetch controllers must be released');
console.log('Issue #698 iOS transport request timeout runtime contract passed');
