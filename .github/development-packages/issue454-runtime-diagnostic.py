#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OLD_REF = "3a5ab6940041edf54e87706bea0924463c3c64b8"
OLD_PATH = "src/MissionChief_Map_Command_Toolkit.user.js"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

old_source = subprocess.run(
    ["git", "show", f"{OLD_REF}:{OLD_PATH}"],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=True,
).stdout
current_source = CURRENT.read_text(encoding="utf-8")

with tempfile.TemporaryDirectory(prefix="issue454-runtime-") as tmp_raw:
    tmp = Path(tmp_raw)
    (tmp / "old.user.js").write_text(old_source, encoding="utf-8")
    (tmp / "current.user.js").write_text(current_source, encoding="utf-8")
    (tmp / "package.json").write_text(json.dumps({"private": True, "dependencies": {"jsdom": "26.1.0"}}), encoding="utf-8")
    harness = r'''const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, VirtualConsole } = require('jsdom');

const file = process.argv[2];
const label = process.argv[3];
const source = fs.readFileSync(file, 'utf8');
const logs = [];
const errors = [];
const virtualConsole = new VirtualConsole();
for (const level of ['log', 'info', 'warn', 'error']) {
  virtualConsole.on(level, (...args) => logs.push({ level, text: args.map(value => {
    try { return typeof value === 'string' ? value : JSON.stringify(value); }
    catch { return String(value); }
  }).join(' ') }));
}
const dom = new JSDOM(`<!doctype html><html><head></head><body>
  <div id="map_outer"><div id="map" class="leaflet-container"></div></div>
  <div id="mission_list"><div id="mission_1" class="missionSideBarEntry"></div></div>
  <div id="radio_messages_important"></div><div id="radio_messages"></div>
  <div id="chat_panel_body"></div><div id="buildings"></div>
  <span id="credits_top">42,000,000</span>
</body></html>`, {
  url: 'https://www.missionchief.co.uk/',
  runScripts: 'outside-only',
  pretendToBeVisual: true,
  virtualConsole,
});
const w = dom.window;
Object.defineProperty(w.document, 'readyState', { configurable: true, get: () => 'complete' });
Object.defineProperty(w.navigator, 'userAgent', { configurable: true, value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36' });
Object.defineProperty(w.navigator, 'maxTouchPoints', { configurable: true, value: 0 });
Object.defineProperty(w, 'innerWidth', { configurable: true, value: 1776 });
Object.defineProperty(w, 'innerHeight', { configurable: true, value: 864 });
Object.defineProperty(w.screen, 'width', { configurable: true, value: 1776 });
Object.defineProperty(w.screen, 'height', { configurable: true, value: 864 });
w.unsafeWindow = w;
w.GM_getValue = (_key, fallback) => fallback;
w.GM_setValue = () => undefined;
w.GM_deleteValue = () => undefined;
w.GM_xmlhttpRequest = details => { if (details?.onerror) w.setTimeout(() => details.onerror(new Error('diagnostic network disabled')), 0); return { abort() {} }; };
w.alert = () => undefined;
w.confirm = () => false;
w.prompt = () => null;
w.open = () => null;
w.scrollTo = () => undefined;
w.matchMedia = query => ({ matches: false, media: query, onchange: null, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {}, dispatchEvent() { return false; } });
w.requestIdleCallback = callback => w.setTimeout(() => callback({ didTimeout: false, timeRemaining: () => 50 }), 0);
w.cancelIdleCallback = id => w.clearTimeout(id);
w.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
w.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} takeRecords() { return []; } };
w.CSS ||= {};
w.CSS.escape ||= value => String(value).replace(/[^a-zA-Z0-9_-]/g, ch => `\\${ch}`);
w.URL.createObjectURL ||= () => 'blob:diagnostic';
w.URL.revokeObjectURL ||= () => undefined;
w.navigator.clipboard = { writeText: async () => undefined };
w.fetch = async () => ({ ok: true, status: 200, json: async () => ({}), text: async () => '', headers: new w.Headers() });
const rect = { x: 0, y: 0, top: 0, left: 0, right: 1100, bottom: 620, width: 1100, height: 620, toJSON() { return this; } };
w.Element.prototype.getBoundingClientRect = function () { return rect; };
w.Element.prototype.getClientRects = function () { return [rect]; };
w.HTMLElement.prototype.scrollIntoView = function () {};
w.addEventListener('error', event => errors.push({ kind: 'window-error', message: event.message, stack: event.error?.stack || '' }));
w.addEventListener('unhandledrejection', event => errors.push({ kind: 'unhandled-rejection', message: String(event.reason), stack: event.reason?.stack || '' }));
let evalError = null;
try {
  w.eval(`${source}\n//# sourceURL=${label}.user.js`);
} catch (error) {
  evalError = { name: error.name, message: error.message, stack: error.stack || '' };
}
const sleep = ms => new Promise(resolve => w.setTimeout(resolve, ms));
(async () => {
  await sleep(3500);
  const control = w.document.getElementById('mc-map-command-toolkit-control');
  const panel = w.document.getElementById('mc-map-command-toolkit-panel');
  const result = {
    label,
    version: (source.match(/^\/\/\s*@version\s+(.+)$/m) || [])[1] || null,
    sourceLines: source.split(/\r?\n/).length,
    evalError,
    asyncErrors: errors,
    controlMounted: Boolean(control),
    panelMounted: Boolean(panel),
    controlOuterHTML: control?.outerHTML?.slice(0, 500) || null,
    bodyChildren: Array.from(w.document.body.children).map(node => ({ id: node.id || null, className: String(node.className || ''), tag: node.tagName })),
    consoleTail: logs.slice(-30),
  };
  process.stdout.write(JSON.stringify(result, null, 2));
  w.close();
})().catch(error => {
  process.stderr.write(error.stack || String(error));
  process.exitCode = 1;
});
'''
    (tmp / "harness.cjs").write_text(harness, encoding="utf-8")
    subprocess.run(["npm", "install", "--no-audit", "--no-fund", "--silent"], cwd=tmp, env=ENV, check=True)

    reports = {}
    for name in ("old", "current"):
        proc = subprocess.run(
            ["node", str(tmp / "harness.cjs"), str(tmp / f"{name}.user.js"), name],
            cwd=tmp,
            env=ENV,
            text=True,
            capture_output=True,
            timeout=30,
        )
        print(f"===== {name.upper()} STDOUT =====")
        print(proc.stdout)
        print(f"===== {name.upper()} STDERR =====")
        print(proc.stderr)
        print(f"===== {name.upper()} RETURN CODE: {proc.returncode} =====")
        if proc.returncode != 0:
            raise SystemExit(f"{name} harness process failed")
        reports[name] = json.loads(proc.stdout)

    print("===== TOP-LEVEL DIFF SUMMARY =====")
    diff = subprocess.run(
        ["git", "diff", "--unified=8", OLD_REF, "--", OLD_PATH],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    interesting = []
    for line in diff.splitlines():
        if line.startswith(("@@", "+    const ", "+    let ", "+    var ", "+    if (", "+    try {", "+    install", "+    schedule", "+    boot", "-    const ", "-    let ", "-    var ", "-    if (", "-    try {", "-    install", "-    schedule", "-    boot")):
            interesting.append(line)
    print("\n".join(interesting[:1200]))

    old = reports["old"]
    current = reports["current"]
    if not old.get("controlMounted"):
        raise SystemExit("Diagnostic harness invalid: v4.20.37 did not mount the launcher")
    if current.get("controlMounted"):
        print("Current v5 mounted in the generic harness; live-DOM-specific fault remains and requires a MissionChief fixture.")
    else:
        print("Current v5 reproduced the missing launcher while v4.20.37 mounted successfully.")
        raise SystemExit("Issue #454 runtime regression reproduced")
