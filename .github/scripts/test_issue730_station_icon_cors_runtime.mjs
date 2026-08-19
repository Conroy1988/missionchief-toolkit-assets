#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { Blob } from 'node:buffer';
import { fileURLToPath } from 'node:url';
import { JSDOM } from 'jsdom';


const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const requestStart = source.indexOf('    function runtimeGmRequest(');
const requestEnd = source.indexOf('    runtimeOnCleanup(', requestStart);
const copierStart = source.indexOf('    function stationIconText(');
const copierEnd = source.indexOf('    function vehicleTargetInfo(', copierStart);
assert.ok(requestStart >= 0 && requestEnd > requestStart, 'Lifecycle-owned userscript request helper is missing');
assert.ok(copierStart >= 0 && copierEnd > copierStart, 'Station Icon Copier helpers are missing');

const shell = new JSDOM('<!doctype html><html><body></body></html>', {
    url: 'https://www.missionchief.co.uk/',
});
const runtime = { destroyed: false, requests: new Set() };
const stationIconCopierRuntime = {
    dispatches: [], typeLabels: {}, buildings: [], queue: [], selectedBuildingIds: new Set(), log: [],
};
let nativeCalls = 0;
let gmOptions = null;
let gmResponse = null;
const context = vm.createContext({
    console,
    Date,
    Set,
    Map,
    Array,
    ArrayBuffer,
    Blob,
    Number,
    String,
    Object,
    Promise,
    Error,
    TypeError,
    URL,
    Uint8Array,
    Math,
    FormData: shell.window.FormData,
    DOMParser: shell.window.DOMParser,
    document: shell.window.document,
    pageWindow: { location: shell.window.location, URL: shell.window.URL, Image: shell.window.Image },
    runtime,
    state: { stationIconCopier: { dispatchIds: [], sourceBuildingId: '', replaceMode: 'defaults', delayMs: 1500 } },
    stationIconCopierRuntime,
    dispatchRecruitmentRuntime: { running: false },
    DISPATCH_RECRUITMENT_ALL_CENTRES: 'all',
    STATION_ICON_REPLACE_DEFAULTS: 'defaults',
    STATION_ICON_REPLACE_INCONSISTENT: 'inconsistent',
    STATION_ICON_REPLACE_ALL: 'all',
    STATION_ICON_REPLACE_OPTIONS: Object.freeze(['defaults', 'inconsistent', 'all']),
    STATION_ICON_DELAY_OPTIONS: Object.freeze([1000, 1500, 2000, 3000, 5000]),
    STATION_ICON_SCAN_LIMIT: 2000,
    STATION_ICON_APPLY_LIMIT: 2000,
    STATION_ICON_REQUEST_TIMEOUT_MS: 15000,
    STATION_ICON_MAX_BYTES: 4 * 1024 * 1024,
    STATION_ICON_MAX_DIMENSION: 200,
    STATION_ICON_MIME_TYPES: Object.freeze(['image/png', 'image/jpeg']),
    STATION_ICON_PRIVILEGED_IMAGE_HOSTS: Object.freeze(['leitstellenspiel.s3.amazonaws.com']),
    GM_xmlhttpRequest(options) {
        gmOptions = options;
        const handle = { abort() { options.onabort(); } };
        queueMicrotask(() => options.onload(gmResponse));
        return handle;
    },
    runtimeFetch: async () => {
        nativeCalls += 1;
        throw new TypeError('Blocked by CORS');
    },
});
vm.runInContext(source.slice(requestStart, requestEnd), context, { filename: 'issue730-runtime-request.js' });
vm.runInContext(source.slice(copierStart, copierEnd), context, { filename: 'issue730-station-icon-copier.js' });

let inspected = null;
context.stationIconInspectBlob = async (blob, mime) => {
    inspected = { size: blob.size, type: blob.type, mime };
    return { blob, mime, width: 25, height: 25, pixelDigest: 'verified' };
};

const uploadUrl = 'https://leitstellenspiel.s3.amazonaws.com/buildings/images/000/123/456/icon.png?1234';
gmResponse = {
    status: 200,
    finalUrl: uploadUrl,
    responseHeaders: 'Content-Type: image/png\r\nContent-Length: 4\r\n',
    response: new Uint8Array([137, 80, 78, 71]).buffer,
};
const downloaded = await context.fetchStationIconImage(uploadUrl, 'source icon');
assert.equal(nativeCalls, 1, 'The normal browser fetch must be attempted first');
assert.equal(gmOptions.url, uploadUrl);
assert.equal(gmOptions.responseType, 'arraybuffer');
assert.equal(gmOptions.anonymous, true, 'Upload-host fallback must not send account credentials');
assert.equal(gmOptions.headers.Accept, 'image/png,image/jpeg');
assert.deepEqual(inspected, { size: 4, type: 'image/png', mime: 'image/png' });
assert.equal(downloaded.pixelDigest, 'verified');
assert.equal(runtime.requests.size, 0, 'Completed userscript requests must leave runtime ownership');

context.runtimeFetch = async () => {
    nativeCalls += 1;
    return {
        ok: true,
        status: 200,
        url: 'https://www.missionchief.co.uk/uploads/building.png',
        headers: { get: name => String(name).toLowerCase() === 'content-type' ? 'image/png' : '' },
        blob: async () => new Blob([new Uint8Array([1, 2, 3])], { type: 'image/png' }),
    };
};
gmOptions = null;
await context.fetchStationIconImage('/uploads/building.png', 'same-origin icon');
assert.equal(nativeCalls, 2);
assert.equal(gmOptions, null, 'A successful browser download must not invoke privileged retrieval');

context.runtimeFetch = async () => {
    nativeCalls += 1;
    throw new TypeError('Blocked by CORS');
};
await assert.rejects(
    context.fetchStationIconImage('https://images.example.test/icon.png', 'source icon'),
    error => error.message.includes('not an approved MissionChief upload host') && error.message.includes('images.example.test'),
    'An unapproved image host must fail closed without privileged access',
);
assert.equal(gmOptions, null, 'No privileged request may be sent to an unapproved host');

gmResponse = {
    status: 200,
    finalUrl: 'https://images.example.test/redirected.png',
    responseHeaders: 'Content-Type: image/png\r\n',
    response: new Uint8Array([1, 2, 3]).buffer,
};
await assert.rejects(
    context.fetchStationIconImage(uploadUrl, 'source icon'),
    error => error.message.includes('redirected outside the approved MissionChief upload host'),
    'A redirect away from the exact upload host must fail closed',
);

gmResponse = {
    status: 200,
    responseHeaders: 'Content-Type: image/png\r\n',
    response: new Uint8Array([1, 2, 3]).buffer,
};
await assert.rejects(
    context.fetchStationIconImage(uploadUrl, 'source icon'),
    error => error.message.includes('did not expose its final response URL'),
    'A privileged response without a final URL must fail closed',
);

gmResponse = {
    status: 200,
    finalUrl: uploadUrl,
    responseHeaders: 'Content-Type: image/png\r\n',
    response: { byteLength: (4 * 1024 * 1024) + 1 },
};
await assert.rejects(
    context.fetchStationIconImage(uploadUrl, 'source icon'),
    error => error.message.includes('exceeds the 4 MB safety limit'),
    'Oversized privileged responses must be rejected before Blob decoding',
);

console.log('Issue #730 Station Icon Copier runtime contract passed: browser-first retrieval, exact-host anonymous fallback, redirect rejection and pre-decode size limits are proven');
