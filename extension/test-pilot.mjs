import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';

const root = path.resolve(import.meta.dirname, '..');
const runtimeRequire = createRequire(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES || '/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules', '_pilot.cjs'));
const {chromium} = runtimeRequire('playwright');
const policySource = fs.readFileSync(path.join(root, 'extension/policy.js'), 'utf8');
const {gameOrigin, safeKey, readUrl} = await import('data:text/javascript,' + encodeURIComponent(policySource));
assert.equal(gameOrigin('https://www.missionchief.co.uk/'), 'https://www.missionchief.co.uk');
for (const value of ['http://missionchief.co.uk/', 'https://missionchief.co.uk.evil.test/', 'https://evil.test/', 'https://missionchief.co.uk:444/']) assert.equal(gameOrigin(value), null);
assert(safeKey('mc_map_command_toolkit_state_v150'));
for (const key of ['mc_map_command_toolkit_discord_webhook_v300', 'mcms_secret', '__proto__', 'sessionid']) assert(!safeKey(key));
for (const url of ['https://discord.com/api/webhooks/123/secret', 'https://evil.test/data.json', 'https://raw.githubusercontent.com/other/private/main/file', 'https://tkb-gaming.scot/admin', 'https://user:pass@tkb-gaming.scot/games/missionchief/guides/api/v2/units.json']) assert.throws(() => readUrl(url));
assert(readUrl('https://tkb-gaming.scot/games/missionchief/guides/api/v2/units.json'));

const extensionPath = path.join(root, '.dev/chromium-extension');
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'mcms-extension-test-'));
const context = await chromium.launchPersistentContext(profile, {
  executablePath: process.env.CHROMIUM_PATH || '/root/.cache/ms-playwright/chromium-1181/chrome-linux/chrome',
  headless: true, viewport: {width: 1440, height: 900},
  ignoreDefaultArgs: ['--disable-extensions'],
  args: [`--disable-extensions-except=${extensionPath}`, `--load-extension=${extensionPath}`, '--no-sandbox', '--enable-unsafe-swiftshader'],
});
let worker = context.serviceWorkers()[0] || await context.waitForEvent('serviceworker');
const errors = [];
const results = [];
const frameRuntime = fs.readFileSync(path.join(root, 'devlab/frame.js'), 'utf8');
let duplicate = false;
let frameHtml = fs.readFileSync(path.join(root, 'devlab/frame.html'), 'utf8').replace(/<script src="\/devlab\/frame\.js"><\/script>/, '');
await context.route('https://missionchief.co.uk/**', async route => {
  if (route.request().isNavigationRequest()) {
    const script = `window.__MCMS_DEV_LAB_TEST__=true;\n${frameRuntime}\nwindow.__MCMS_DEV_LAB_API__.installEnvironment();\n${duplicate ? 'window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__={version:"10.18.1",destroyed:false};' : ''}`;
    await route.fulfill({contentType: 'text/html', body: frameHtml.replace('</body>', `<script>${script.replaceAll('</script>', '<\\/script>')}</script></body>`)});
  } else await route.fulfill({status: 404, body: ''});
});
// No real game endpoints are contacted or mutated by these tests.
await context.route(/https:\/\/(?!missionchief\.co\.uk)/, route => route.fulfill({status: 404, body: ''}));
const page = await context.newPage();
page.on('pageerror', error => errors.push(error.message));
try {
  await page.goto('https://missionchief.co.uk/');
  await page.waitForFunction(() => document.documentElement.dataset.mcmsExtensionState === 'off');
  assert.equal(await page.locator('#mc-map-command-toolkit-control').count(), 0);
  results.push('Disabled-by-default installation creates no Toolkit runtime.');

  await worker.evaluate(() => chrome.storage.local.set({enabled: true}));
  duplicate = true;
  await page.reload();
  await page.waitForFunction(() => document.documentElement.dataset.mcmsExtensionState === 'userscript-active');
  assert.equal(await page.evaluate(() => Boolean(window.__MCMS_EXTENSION_PILOT__)), false);
  results.push('Existing userscript runtime blocks extension startup before any pilot hooks.');

  duplicate = false;
  await page.reload();
  await page.waitForFunction(() => window.__MCMS_EXTENSION_PILOT__?.state === 'running', null, {timeout: 20000});
  await page.waitForSelector('#mc-map-command-toolkit-control');
  await page.evaluate(() => window.__MCMS_DEV_LAB_API__.openTarget());
  const sections = await page.locator('.mcms-command-content > .mcms-tab-panel').evaluateAll(nodes => nodes.map(n => n.dataset.panel));
  assert.deepEqual(sections, ['map', 'incidents', 'fleet', 'administration', 'finance', 'status', 'settings']);
  assert.equal(await page.evaluate(() => Boolean(window.__MCMS_EXTENSION_MAPLIBRE__)), false);
  results.push('Actual MV3 MAIN-world injection mounts all seven sections; MapLibre stays unloaded.');

  const field = page.locator('[data-setting="dispatch-recruitment-personnel"]');
  await field.fill('275');
  await field.dispatchEvent('change');
  await page.waitForFunction(() => window.__MCMS_EXTENSION_PILOT__.pending.size === 0);
  const saved = await worker.evaluate(async () => (await chrome.storage.local.get('pilot:https://missionchief.co.uk'))['pilot:https://missionchief.co.uk']);
  assert.equal(JSON.parse(saved.ls.mc_map_command_toolkit_state_v150).dispatchRecruitment.personnelDesired, '275');
  assert.equal(await page.evaluate(() => JSON.parse(window.localStorage.getItem('mc_map_command_toolkit_state_v150')).dispatchRecruitment.personnelDesired), '400');
  await page.reload();
  await page.waitForFunction(() => window.__MCMS_EXTENSION_PILOT__?.state === 'running');
  await page.evaluate(() => window.__MCMS_DEV_LAB_API__.openTarget());
  assert.equal(await field.inputValue(), '275');
  results.push('Settings persist through extension storage and reload without changing userscript settings.');

  // Request local engine through the actual isolated bridge + service worker.
  const engineResult = await page.evaluate(() => new Promise(resolve => {
    const id = 'engine-probe';
    const listener = event => { if (event.data?.direction === 'response' && event.data.id === id) { window.removeEventListener('message', listener); resolve(event.data.response); } };
    window.addEventListener('message', listener);
    window.postMessage({channel: 'mcms-extension-pilot-v1', direction: 'request', payload: {id, op: 'engine'}}, location.origin);
  }));
  assert.equal(engineResult.ok, true);
  assert.equal(await page.evaluate(() => window.__MCMS_EXTENSION_MAPLIBRE__.version), '5.24.0');
  const mapTest = await page.evaluate(async () => {
    const element = document.createElement('div'); element.style.cssText = 'width:300px;height:200px;position:fixed;top:0'; document.body.append(element);
    const lib = window.__MCMS_EXTENSION_MAPLIBRE__;
    const map = new lib.Map({container: element, style: {version: 8, sources: {points: {type: 'geojson', data: {type: 'FeatureCollection', features: [{type: 'Feature', geometry: {type: 'Point', coordinates: [0,0]}, properties: {}}]}}}, layers: [{id: 'points', type: 'circle', source: 'points'}]}, center: [0,0], zoom: 1, attributionControl: false});
    const result = await new Promise(resolve => { const timer = setTimeout(() => resolve('timeout'), 10000); map.on('error', event => { clearTimeout(timer); resolve(event.error.message); }); map.on('idle', () => { clearTimeout(timer); resolve('rendered'); }); });
    map.remove(); element.remove(); return result;
  });
  assert.equal(mapTest, 'rendered');
  results.push('Packaged MapLibre and packaged worker render GeoJSON in Chromium without downloaded JavaScript.');

  const denied = await page.evaluate(() => new Promise(resolve => {
    const id = 'deny-probe';
    const listener = event => { if (event.data?.direction === 'response' && event.data.id === id) { window.removeEventListener('message', listener); resolve(event.data.response); } };
    window.addEventListener('message', listener);
    window.postMessage({channel: 'mcms-extension-pilot-v1', direction: 'request', payload: {id, op: 'request', method: 'POST', url: 'https://discord.com/api/webhooks/123/test'}}, location.origin);
  }));
  assert.equal(denied.ok, false);
  results.push('Forged page request cannot use the bridge for external posting.');

  await page.screenshot({path: path.join(root, '.dev/extension-pilot-desktop.png')});
  const popup = await context.newPage();
  await popup.goto(`chrome-extension://${new URL(worker.url()).host}/popup.html`);
  await popup.screenshot({path: path.join(root, '.dev/extension-pilot-popup.png')});
  await popup.close();

  await worker.evaluate(() => chrome.storage.local.set({enabled: false}));
  await page.reload();
  await page.waitForFunction(() => document.documentElement.dataset.mcmsExtensionState === 'off');
  assert.equal(await page.locator('#mc-map-command-toolkit-control').count(), 0);
  results.push('Turning the pilot off and reloading returns to a page with no extension Toolkit runtime.');
  assert.deepEqual(errors, []);
  fs.writeFileSync(path.join(root, '.dev/extension-test-results.json'), JSON.stringify({passed: true, browser: context.browser()?.version() || 'Chromium', results, errors}, null, 2));
  console.log(JSON.stringify({passed: true, results, errors}, null, 2));
} finally {
  await context.close();
  fs.rmSync(profile, {recursive: true, force: true});
}
