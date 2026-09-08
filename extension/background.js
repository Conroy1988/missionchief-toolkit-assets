import { gameOrigin, safeKey, readUrl } from './policy.js';

const requests = new Map();
const starts = new Map();
let storageQueue = Promise.resolve();
const MAX_BYTES = 4 * 1024 * 1024;

function pageSender(sender) {
  const origin = gameOrigin(sender.url);
  if (!origin || sender.frameId !== 0 || !sender.tab?.id || !sender.documentId) throw Error('Unsupported page.');
  return {origin, tabId: sender.tab.id, documentId: sender.documentId};
}
function target(sender) {
  const s = pageSender(sender);
  return {tabId: s.tabId, documentIds: [s.documentId]};
}
async function save(sender, message) {
  const {origin} = pageSender(sender);
  if (!['ls', 'gm'].includes(message.area) || !safeKey(message.key)) throw Error('Private or unknown storage key.');
  const encoded = JSON.stringify(message.value);
  if (message.value !== null && (encoded === undefined || encoded.length > 512 * 1024)) throw Error('Setting is too large.');
  if (message.area === 'ls' && message.value !== null && typeof message.value !== 'string') throw Error('Invalid local setting.');
  const key = `pilot:${origin}`;
  const stored = await chrome.storage.local.get(key);
  const data = stored[key] || {ls: {}, gm: {}};
  if (message.value === null) delete data[message.area][message.key];
  else data[message.area][message.key] = message.value;
  if (JSON.stringify(data).length > MAX_BYTES) throw Error('Pilot settings capacity reached.');
  await chrome.storage.local.set({[key]: data});
  return true;
}
async function start(sender) {
  const {origin, documentId} = pageSender(sender);
  const config = await chrome.storage.local.get(['enabled', `pilot:${origin}`]);
  if (!config.enabled) return {state: 'off'};
  if (starts.has(documentId)) return starts.get(documentId);
  const job = (async () => {
    const result = await chrome.scripting.executeScript({target: target(sender), world: 'MAIN', func: data => {
      if (window.__MCMS_EXTENSION_PILOT__) return 'already-started';
      const existing = window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__;
      if ((existing && !existing.destroyed) || window.__MCMS_FIRST_BYTE_BOOTSTRAP__) return 'userscript-active';
      window.__MCMS_EXTENSION_SEED__ = data;
      return 'ready';
    }, args: [config[`pilot:${origin}`] || {ls: {}, gm: {}}]});
    const state = result[0]?.result;
    if (state !== 'ready') return {state};
    await chrome.scripting.executeScript({target: target(sender), world: 'MAIN', files: ['toolkit.js']});
    const [receipt] = await chrome.scripting.executeScript({target: target(sender), world: 'MAIN', func: () => Boolean(window.__MCMS_EXTENSION_PILOT__)});
    return {state: receipt?.result ? 'started' : 'userscript-active'};
  })();
  starts.set(documentId, job);
  try { return await job; } finally { starts.delete(documentId); }
}
async function engine(sender) {
  await chrome.scripting.executeScript({target: target(sender), world: 'MAIN', files: ['vendor/maplibre-bundle.js']});
  await chrome.scripting.executeScript({target: target(sender), world: 'MAIN', func: workerUrl => {
    const library = window.__MCMS_EXTENSION_MAPLIBRE__;
    if (!library) throw Error('Packaged map engine unavailable.');
    if (!library.__pilotWorkerConfigured) {
      const url = URL.createObjectURL(new Blob([`importScripts(${JSON.stringify(workerUrl)});`], {type: 'text/javascript'}));
      library.setWorkerUrl(url);
      library.__pilotWorkerConfigured = true;
      window.addEventListener('pagehide', event => { if (!event.persisted) URL.revokeObjectURL(url); });
    }
  }, args: [chrome.runtime.getURL('vendor/maplibre-gl-csp-worker.js')]});
  return true;
}
async function request(sender, message) {
  const {documentId} = pageSender(sender);
  const key = `${documentId}:${message.id}`;
  if (requests.has(key) || requests.size >= 12) throw Error('Too many external requests.');
  if (message.method !== 'GET') throw Error('External posting is unavailable in the local pilot.');
  const url = readUrl(message.url);
  const controller = new AbortController();
  requests.set(key, controller);
  const timer = setTimeout(() => controller.abort(), Math.min(20000, Math.max(1, Number(message.timeout) || 15000)));
  try {
    const response = await fetch(url, {credentials: 'omit', redirect: 'error', signal: controller.signal});
    if (Number(response.headers.get('content-length')) > MAX_BYTES) throw Error('Response too large.');
    const reader = response.body.getReader();
    const chunks = [];
    let size = 0;
    while (true) {
      const {value, done} = await reader.read();
      if (done) break;
      size += value.length;
      if (size > MAX_BYTES) { await reader.cancel(); throw Error('Response too large.'); }
      chunks.push(value);
    }
    const bytes = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
    return {status: response.status, finalUrl: response.url,
      responseHeaders: [...response.headers].map(([k,v]) => `${k}: ${v}`).join('\r\n'),
      ...(message.responseType === 'arraybuffer' ? {bytes: Array.from(bytes)} : {responseText: new TextDecoder().decode(bytes)})};
  } finally { clearTimeout(timer); requests.delete(key); }
}
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  const run = async () => {
    pageSender(sender);
    if (!message || typeof message.id !== 'string' || message.id.length > 100) throw Error('Invalid request.');
    if (message.op === 'start') return start(sender);
    if (!(await chrome.storage.local.get('enabled')).enabled) throw Error('Pilot is off. Reload the game tab.');
    if (message.op === 'engine') return engine(sender);
    if (message.op === 'request') return request(sender, message);
    if (message.op === 'abort') { requests.get(`${sender.documentId}:${message.requestId}`)?.abort(); return true; }
    if (message.op === 'save') {
      const next = storageQueue.then(() => save(sender, message));
      storageQueue = next.catch(() => {});
      return next;
    }
    throw Error('Unknown pilot operation.');
  };
  run().then(value => respond({ok: true, value}), error => respond({ok: false, error: error.message}));
  return true;
});
