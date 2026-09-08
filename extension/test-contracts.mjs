import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {webcrypto, createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const root = path.resolve(import.meta.dirname, '..');
const require = createRequire(path.join(root, '.dev/test-deps/package.json'));
const {JSDOM} = require('jsdom');
const ext = path.join(root, '.dev/chromium-extension');
const source = fs.readFileSync(path.join(ext, 'toolkit.js'), 'utf8');
const policy = fs.readFileSync(path.join(ext, 'policy.js'), 'utf8').replaceAll('export function', 'function');
const background = fs.readFileSync(path.join(ext, 'background.js'), 'utf8').replace(/^import .*?;\n/, '');
const html = fs.readFileSync(path.join(root, 'devlab/frame.html'), 'utf8').replace(/<script src="\/devlab\/frame\.js"><\/script>/, '');
const fixture = fs.readFileSync(path.join(root, 'devlab/frame.js'), 'utf8');
const data = {};
let listener, currentWindow;
const results = [];
const errors = [];
const network = [];
const sender = {url: 'https://missionchief.co.uk/', frameId: 0, tab: {id: 1}, documentId: 'document-1'};
const chrome = {
  storage: {local: {
    async get(keys) { return Object.fromEntries((Array.isArray(keys) ? keys : [keys]).filter(k => Object.hasOwn(data,k)).map(k => [k, structuredClone(data[k])])); },
    async set(values) { Object.assign(data, structuredClone(values)); }
  }},
  scripting: {async executeScript(options) {
    assert.equal(options.world, 'MAIN');
    assert.equal(options.target.documentIds[0], sender.documentId);
    if (options.files) for (const file of options.files) currentWindow.eval(fs.readFileSync(path.join(ext,file),'utf8'));
    else return [{result: currentWindow.eval(`(${options.func.toString()})(...${JSON.stringify(options.args || [])})`)}];
    return [{result: undefined}];
  }},
  runtime: {
    getURL: p => `chrome-extension://pilot/${p}`,
    onMessage: {addListener(fn) { listener = fn; }},
    sendMessage(message) { return new Promise(resolve => listener(message, sender, resolve)); }
  }
};
const worker = vm.createContext({chrome, URL, Map, Promise, JSON, Object, Number, String, Error, Array, Uint8Array, TextDecoder, AbortController, setTimeout, clearTimeout,
  fetch: async (url, options) => { network.push({url, options}); return new Response('{"ok":true}', {status: 200, headers: {'content-type':'application/json'}}); }});
vm.runInContext(policy + '\n' + background, worker);
function call(message, otherSender = sender) { return new Promise(resolve => listener({id: 'test-'+Math.random(), ...message}, otherSender, resolve)); }
async function waitFor(predicate, label, ms=15000) { const end=Date.now()+ms; while(Date.now()<end) {if(await predicate()) return; await new Promise(r=>setTimeout(r,20));} throw Error(label); }
async function boot({duplicate=false, device='desktop'}={}) {
  sender.documentId = `document-${Date.now()}`;
  const dom = new JSDOM(html, {url:`https://missionchief.co.uk/?device=${device}&tab=administration`,pretendToBeVisual:true,runScripts:'dangerously'});
  const w = dom.window;
  w.addEventListener('error', event => errors.push(String(event.error?.message || event.message)));
  currentWindow = w;
  Object.assign(w, {__MCMS_DEV_LAB_TEST__:true, Response, Request, Headers, TextEncoder, TextDecoder, structuredClone, chrome});
  Object.defineProperty(w,'crypto',{configurable:true,value:webcrypto});
  w.postMessage = value => w.setTimeout(()=>w.dispatchEvent(new w.MessageEvent('message',{data:value,source:w,origin:w.location.origin})),0);
  w.eval(fixture);
  w.__MCMS_DEV_LAB_API__.installEnvironment();
  if(duplicate) w.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__={version:'10.18.1',destroyed:false};
  w.eval(fs.readFileSync(path.join(ext,'bridge.js'),'utf8'));
  await waitFor(()=>w.document.documentElement.dataset.mcmsExtensionState,'startup state missing');
  return dom;
}
async function closeDom(dom) {
  const runtime = dom.window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__;
  runtime?.destroy?.('test complete');
  dom.window.__MCMS_FIRST_BYTE_BOOTSTRAP__?.dispose?.();
  if (runtime?.destroy) {
    assert.equal(runtime.destroyed, true);
    assert.equal(runtime.observers.size, 0);
    assert.equal(runtime.timeouts.size, 0);
  }
  await new Promise(resolve => setTimeout(resolve, 0));
  dom.window.close();
}

let dom = await boot();
assert.equal(dom.window.document.documentElement.dataset.mcmsExtensionState,'off');
assert.equal(dom.window.__MCMS_EXTENSION_PILOT__,undefined);
await closeDom(dom);
results.push('Disabled pilot does not inject source.');
data.enabled=true;
dom=await boot({duplicate:true});
assert.equal(dom.window.document.documentElement.dataset.mcmsExtensionState,'userscript-active');
assert.equal(dom.window.__MCMS_EXTENSION_PILOT__,undefined);
await closeDom(dom);
results.push('An existing runtime prevents all extension runtime injection.');

dom=await boot();
let w=dom.window;
await waitFor(()=>w.document.querySelector('#mc-map-command-toolkit-control'),'toolbar missing');
await w.__MCMS_DEV_LAB_API__.openTarget();
if (process.env.MCMS_EXPORT_STORE_PREVIEW === '1') {
  for (const script of w.document.querySelectorAll('script')) script.remove();
  fs.writeFileSync(path.join(root, '.dev/store-toolkit-preview.html'), dom.serialize());
}
assert.deepEqual(Array.from(w.document.querySelectorAll('.mcms-command-content > .mcms-tab-panel'),n=>n.dataset.panel),['map','incidents','fleet','administration','finance','status','settings']);
assert.equal(w.__MCMS_EXTENSION_MAPLIBRE__,undefined);
const personnel=w.document.querySelector('[data-setting="dispatch-recruitment-personnel"]');
personnel.value='275';
personnel.dispatchEvent(new w.Event('change',{bubbles:true}));
await waitFor(()=>data['pilot:https://missionchief.co.uk']?.ls.mc_map_command_toolkit_state_v150 && JSON.parse(data['pilot:https://missionchief.co.uk'].ls.mc_map_command_toolkit_state_v150).dispatchRecruitment.personnelDesired==='275','setting not saved');
assert.equal(JSON.parse(w.localStorage.getItem('mc_map_command_toolkit_state_v150')).dispatchRecruitment.personnelDesired,'400');
assert.equal(w.document.getElementById('mcms-version-status-control').textContent,'PILOT');
await waitFor(()=>w.__MCMS_EXTENSION_PILOT__.pending.size===0,'pending writes');
const runtime=w.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__;
w.eval(source);
assert.equal(w.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__,runtime);
assert.equal(w.document.querySelectorAll('#mc-map-command-toolkit-control').length,1);
results.push('Shared source mounts seven sections, pilot badge and toolbar; repeated injection is a no-op.');
results.push('Native workflow settings save separately; userscript state remains unchanged.');
await closeDom(dom);

dom=await boot();w=dom.window;
await waitFor(()=>w.document.querySelector('#mc-map-command-toolkit-control'),'reload toolbar missing');
await w.__MCMS_DEV_LAB_API__.openTarget();
assert.equal(w.document.querySelector('[data-setting="dispatch-recruitment-personnel"]').value,'275');
results.push('A fresh document restores extension settings rather than the userscript defaults.');

const fast=w.document.querySelector('.mcms-fast-map-btn');
const originalMap=w.document.getElementById('map');
fast.click();
await waitFor(()=>w.__MCMS_FAST_MAP_DIAGNOSTICS__().active,'Fast Map fixture did not activate');
assert.equal(originalMap.isConnected,false);
fast.click();
await waitFor(()=>!w.__MCMS_FAST_MAP_DIAGNOSTICS__().active,'Fast Map fixture did not stop');
assert.equal(w.document.getElementById('map'),originalMap);
results.push('Fast Map fixture activates and restores the exact native map node.');

const before=network.length;
for(const message of [
  {op:'request',method:'POST',url:'https://discord.com/api/webhooks/123/private'},
  {op:'request',method:'GET',url:'https://evil.test/data'},
  {op:'request',method:'GET',url:'https://user:pass@tkb-gaming.scot/games/missionchief/guides/api/v2/units.json'},
  {op:'save',area:'gm',key:'mc_map_command_toolkit_discord_webhook_v300',value:'private'},
  {op:'save',area:'gm',key:'__proto__',value:{}},
  {op:'save',area:'gm',key:'mcms_large',value:'x'.repeat(513*1024)},
]) assert.equal((await call(message)).ok,false);
assert.equal((await call({op:'request',method:'GET',url:'https://tkb-gaming.scot/games/missionchief/guides/api/v2/units.json'},{...sender,url:'https://evil.test/'})).ok,false);
assert.equal((await call({op:'start'},{...sender,frameId:1})).ok,false);
assert.equal(network.length,before);
const read=await call({op:'request',method:'GET',url:'https://tkb-gaming.scot/games/missionchief/guides/api/v2/units.json'});
assert.equal(read.ok,true);
assert.equal(read.value.responseText,'{"ok":true}');
assert.equal(network.at(-1).options.credentials,'omit');
assert.equal(network.at(-1).options.redirect,'error');
results.push('Worker rejects private keys, oversized writes, foreign/iframe senders, external POST and unapproved URLs before networking.');
results.push('Approved public GET returns data with credentials omitted and redirects refused.');
await waitFor(()=>w.__MCMS_EXTENSION_PILOT__.pending.size===0,'pending requests');
await closeDom(dom);
data.enabled=false;
dom=await boot();
assert.equal(dom.window.document.documentElement.dataset.mcmsExtensionState,'off');
await closeDom(dom);
results.push('Disable + new document leaves no pilot runtime.');
assert.deepEqual(errors, []);
const testedFiles = Object.fromEntries(['toolkit.js','background.js','policy.js','bridge.js'].map(name=>[name,createHash('sha256').update(fs.readFileSync(path.join(ext,name))).digest('hex')]));
const report={passed:true,kind:'Node/DOM extension-contract tests; browser APIs simulated',testedFiles,results,errors,browserGate:'Blocked: Chromium cannot create its process singleton socket in this environment. Live extension and packaged WebGL worker tests remain unverified.'};
fs.writeFileSync(path.join(root,'.dev/extension-contract-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
