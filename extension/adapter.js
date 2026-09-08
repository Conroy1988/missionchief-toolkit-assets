// Wrapped together with the canonical source; these names are closure-local.
const pilot = {state: 'starting', storageError: '', pending: new Map(), next: 0};
const existingRuntime = window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__;
if (window.__MCMS_EXTENSION_PILOT__ || (existingRuntime && !existingRuntime.destroyed) || window.__MCMS_FIRST_BYTE_BOOTSTRAP__) return;
window.__MCMS_EXTENSION_PILOT__ = pilot;
const seed = window.__MCMS_EXTENSION_SEED__ || {ls: {}, gm: {}};
delete window.__MCMS_EXTENSION_SEED__;
const allowedKey = key => typeof key === 'string' && /^(mc_map_command_toolkit_|mcms_)/.test(key)
  && key.length < 160 && !/discord|webhook|credential|secret|token|identity|finance|financial/i.test(key);
const ls = Object.assign(Object.create(null), seed.ls);
const gm = Object.assign(Object.create(null), seed.gm);
const unsafeWindow = window;
function pilotCall(payload, timeout = 25000) {
  const id = `p${++pilot.next}`;
  let timer;
  const promise = new Promise((resolve, reject) => {
    timer = setTimeout(() => { pilot.pending.delete(id); reject(Error('Extension request timed out.')); }, timeout);
    pilot.pending.set(id, {resolve, reject, timer});
    window.postMessage({channel: 'mcms-extension-pilot-v1', direction: 'request', payload: {...payload, id}}, location.origin);
  });
  return {id, promise};
}
window.addEventListener('message', event => {
  if (event.source !== window || event.origin !== location.origin || event.data?.channel !== 'mcms-extension-pilot-v1' || event.data?.direction !== 'response') return;
  const pending = pilot.pending.get(event.data.id);
  if (!pending) return;
  clearTimeout(pending.timer);
  pilot.pending.delete(event.data.id);
  const response = event.data.response;
  if (response?.ok) pending.resolve(response.value);
  else pending.reject(Error(response?.error || 'Extension operation failed.'));
});
function pilotSave(area, key, value) {
  pilotCall({op: 'save', area, key, value}).promise.catch(error => {
    pilot.storageError = error.message;
    document.documentElement.dataset.mcmsExtensionStorageError = error.message;
    console.error('Toolkit pilot settings were not saved:', error.message);
  });
}
const localStorage = {
  getItem(key) {
    if (!allowedKey(key)) return null;
    return Object.hasOwn(ls, key) ? ls[key] : null;
  },
  setItem(key, value) {
    if (!allowedKey(key)) throw Error('Private storage is unavailable in this pilot.');
    const text = String(value);
    if (text.length > 512 * 1024) throw Error('Setting is too large.');
    ls[key] = text; pilotSave('ls', key, text);
  },
  removeItem(key) { if (allowedKey(key)) { delete ls[key]; pilotSave('ls', key, null); } }
};
// Copy ordinary settings once, without editing the userscript's website storage.
const initialKey = 'mc_map_command_toolkit_state_v150';
if (!Object.hasOwn(ls, initialKey)) {
  try {
    const value = window.localStorage.getItem(initialKey);
    if (value && value.length < 512 * 1024 && typeof JSON.parse(value) === 'object') localStorage.setItem(initialKey, value);
  } catch { /* A fresh pilot uses the canonical defaults. */ }
}
function GM_getValue(key, fallback) { return allowedKey(key) && Object.hasOwn(gm, key) ? structuredClone(gm[key]) : fallback; }
function GM_setValue(key, value) {
  if (!allowedKey(key)) throw Error('Private integrations are unavailable in this pilot.');
  if (JSON.stringify(value).length > 512 * 1024) throw Error('Setting is too large.');
  gm[key] = structuredClone(value); pilotSave('gm', key, value);
}
function GM_deleteValue(key) { if (allowedKey(key)) { delete gm[key]; pilotSave('gm', key, null); } }
function GM_xmlhttpRequest(options) {
  let settled = false;
  const call = pilotCall({op: 'request', method: options.method || 'GET', url: options.url,
    responseType: options.responseType, timeout: options.timeout});
  call.promise.then(response => {
    if (settled) return;
    settled = true;
    if (response.bytes) { response.response = new Uint8Array(response.bytes).buffer; delete response.bytes; }
    else response.response = response.responseText;
    options.onload?.(response);
  }).catch(error => { if (!settled) { settled = true; options.onerror?.({error: error.message}); } });
  return {abort() {
    if (settled) return;
    settled = true;
    pilotCall({op: 'abort', requestId: call.id}).promise.catch(() => {});
    options.onabort?.();
  }};
}
async function pilotLoadEngine() {
  await pilotCall({op: 'engine'}).promise;
  const library = window.__MCMS_EXTENSION_MAPLIBRE__;
  if (!library || typeof library.Map !== 'function') throw Error('Packaged map engine did not load.');
  return library;
}
