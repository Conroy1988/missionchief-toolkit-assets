#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import { createRequire } from "node:module";

const { chromium } = createRequire(import.meta.url)("playwright-core");

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const hostCheck = "            return /(^|\\.)((?:missionchief\\.(?:co\\.uk|com))|leitstellenspiel\\.de|meldkamerspel\\.com)$/iu.test(String(location.hostname || ''));";
const testableSource = source.replace(
  hostCheck,
  "            return String(location.hostname || '') === '127.0.0.1' || /(^|\\.)((?:missionchief\\.(?:co\\.uk|com))|leitstellenspiel\\.de|meldkamerspel\\.com)$/iu.test(String(location.hostname || ''));",
);
assert.notEqual(testableSource, source, "Chromium fixture could not extend the first-byte host guard");

const fixture = `<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{width:100%;height:100%;margin:0}#map_outer,#map{width:100%;height:calc(100vh - 46px)}
</style></head><body><nav id="navbar-main" style="height:46px"></nav><aside id="mission_list"></aside>
<script>
setTimeout(() => {
  const outer = document.createElement('div'); outer.id = 'map_outer';
  const element = document.createElement('div'); element.id = 'map'; element.className = 'leaflet-container';
  element.innerHTML = '<div class="leaflet-map-pane"></div>'; outer.appendChild(element); document.body.appendChild(outer);
  let nextId = 30;
  const bounds = { contains:()=>true, getNorth:()=>56.2, getSouth:()=>55.7, getEast:()=>-2.8, getWest:()=>-3.6 };
  const map = {
    _leaflet_id: 1, _layers: {}, getContainer:()=>element, getBounds:()=>bounds,
    getCenter:()=>({lat:55.9533,lng:-3.1883}), getZoom:()=>12, eachLayer(){}, on(){return this},
    off(){return this}, hasLayer(){return false}, invalidateSize(){return this},
    latLngToContainerPoint:()=>({x:100,y:100}), containerPointToLatLng:()=>({lat:55.9533,lng:-3.1883})
  };
  const layer = extra => ({ _leaflet_id:nextId++, options:{}, addTo(){return this}, remove(){return this},
    bindTooltip(){return this}, setIcon(){return this}, setLatLng(){return this}, setStyle(){return this},
    getLatLng:()=>({lat:55.9533,lng:-3.1883}), ...extra });
  window.map = map; window.mapkit = map;
  window.L = {
    map:()=>map, stamp(value){if(!value._leaflet_id)value._leaflet_id=nextId++;return value._leaflet_id},
    layerGroup:()=>layer({clearLayers(){return this},addLayer(){return this},eachLayer(){}}),
    featureGroup:()=>layer({clearLayers(){return this},addLayer(){return this},eachLayer(){}}),
    marker:latlng=>layer({getLatLng:()=>latlng}), circle:latlng=>layer({getLatLng:()=>latlng}),
    circleMarker:latlng=>layer({getLatLng:()=>latlng}), polyline:()=>layer({getBounds:()=>bounds}),
    divIcon:options=>({options}), latLng:(lat,lng)=>({lat:Number(lat),lng:Number(lng)}),
    latLngBounds:()=>bounds, point:(x,y)=>({x,y})
  };
}, 120);
</script></body></html>`;

function browserExecutable() {
  const candidates = [
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    chromium.executablePath(),
  ];
  return candidates.find(candidate => candidate && fs.existsSync(candidate)) || null;
}

function initScript(applicationSource) {
  const storedState = JSON.stringify({
    setupWizard: { completed: true, schema: 1 },
    updateBriefing: { enabled: false, seenVersion: "10.16.8", seenFeatures: [] },
    cleanMode: false,
  });
  return `
    window.__MCMS_CHROMIUM_ROOT_WAS_NULL__ = document.documentElement === null;
    Object.defineProperty(window, 'unsafeWindow', { configurable:true, value:window });
    window.GM_getValue = (_key, fallback) => fallback;
    window.GM_setValue = () => undefined;
    window.GM_deleteValue = () => undefined;
    window.GM_xmlhttpRequest = () => ({ abort() {} });
    localStorage.setItem('mc_map_command_toolkit_state_v150', ${JSON.stringify(storedState)});
    ${applicationSource}
  `;
}

async function healthyScenario(browser, url) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  await context.addInitScript({ content: initScript(testableSource) });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded" });
  assert.equal(await page.evaluate(() => window.__MCMS_CHROMIUM_ROOT_WAS_NULL__), true, "Chromium init did not execute before the HTML root");
  const control = page.locator("#mc-map-command-toolkit-control");
  await control.waitFor({ state: "visible", timeout: 15000 });
  const box = await control.boundingBox();
  assert.ok(box && box.width > 40 && box.height > 30, "Chromium launcher has no visible geometry");
  assert.equal(await control.evaluate(element => element.parentElement?.id), "map", "Chromium launcher missed the canonical map");
  assert.equal(await page.evaluate(() => window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__?.version), "10.16.8");
  assert.equal(await page.locator("html").getAttribute("data-mcms-first-byte-phase"), "ui-mounted");
  await control.locator(".mcms-menu-btn").click();
  await page.locator("#mc-map-command-toolkit-panel.mcms-open").waitFor({ state: "visible", timeout: 10000 });
  await context.close();
}

async function fatalScenario(browser, url) {
  const fatalSource = testableSource.replace(
    "    MCMS_FIRST_BYTE.mark('application-entered');",
    "    MCMS_FIRST_BYTE.mark('application-entered');\n    throw new Error('intentional Chromium application failure');",
  );
  assert.notEqual(fatalSource, testableSource, "Chromium fatal source transform failed");
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  await context.addInitScript({ content: initScript(fatalSource) });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded" });
  assert.equal(await page.evaluate(() => window.__MCMS_CHROMIUM_ROOT_WAS_NULL__), true);
  const recovery = page.locator("#mcms-first-byte-recovery");
  await recovery.waitFor({ state: "visible", timeout: 10000 });
  assert.equal(await page.locator("html").getAttribute("data-mcms-first-byte-phase"), "application-failed");
  await recovery.click();
  const details = page.locator("#mcms-first-byte-recovery-details");
  await details.waitFor({ state: "visible", timeout: 5000 });
  assert.equal(
    await details.locator("a").getAttribute("href"),
    "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/MissionChief_Map_Command_Toolkit.user.js",
  );
  await context.close();
}

const executablePath = browserExecutable();
if (!executablePath) {
  if (process.env.CI) throw new Error("A Chromium executable is required for the CI first-byte runtime contract");
  console.log("SKIP Chromium first-byte runtime: no local Chromium executable is installed.");
  process.exit(0);
}

const server = http.createServer((request, response) => {
  if (request.url?.startsWith("/api/")) {
    response.writeHead(404, { "content-type": "application/json" }); response.end("{}"); return;
  }
  response.writeHead(200, { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" });
  response.end(fixture);
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const address = server.address();
assert.ok(address && typeof address === "object");
const url = `http://127.0.0.1:${address.port}/`;
const browser = await chromium.launch({ executablePath, headless: true, args: ["--no-sandbox"] });
try {
  await healthyScenario(browser, url);
  await fatalScenario(browser, url);
  console.log("Chromium first-byte runtime passed: true pre-root execution mounts the UI, and fatal application startup retains visible recovery and repair controls.");
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
