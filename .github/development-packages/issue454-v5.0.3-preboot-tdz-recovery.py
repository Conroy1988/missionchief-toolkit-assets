#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
ROOT_USER = ROOT / "MissionChief_Map_Command_Toolkit.user.js"
ROOT_TXT = ROOT / "MissionChief_Map_Command_Toolkit.txt"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
CHANGELOG = ROOT / "CHANGELOG.md"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
CONTRACT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
DIAGNOSTICS = (
    ROOT / ".github" / "diagnostics" / "issue454-runtime-diagnostic.txt",
    ROOT / ".github" / "diagnostics" / "issue454-state-region.txt",
)
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def replace_exact(text: str, old: str, new: str, label: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{label}: expected {count}, found {actual}")
    return text.replace(old, new, count)


source = SOURCE.read_text(encoding="utf-8")
source = replace_exact(source, "// @version      5.0.2", "// @version      5.0.3", "metadata version")
source = replace_exact(source, "version: '5.0.2',", "version: '5.0.3',", "runtime version")

late_declaration = "    const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;\n"
state_initializer = "    const state = loadState();\n"
if source.index(state_initializer) >= source.index(late_declaration):
    raise RuntimeError("Issue #454 precondition failed: settings version is not after state initialization")
source = replace_exact(source, late_declaration, "", "remove late operational settings declaration")
source = replace_exact(
    source,
    state_initializer,
    late_declaration + state_initializer,
    "insert operational settings declaration before state hydration",
)

for path in (SOURCE, ROOT_USER, ROOT_TXT, DIST_USER, DIST_TXT):
    path.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
anchor = "## [Unreleased]\n"
notes = '''
## [5.0.3] - 2026-07-23

### Critical preboot recovery
- Fixed a JavaScript temporal-dead-zone failure that terminated the userscript during state hydration before `boot()` or `ensureUi()` could execute.
- Moved the Operational Window settings schema constant ahead of the top-level `loadState()` call while retaining every v5 operational feature and existing user setting.
- Added a permanent declaration-order regression contract and executable launcher-mount smoke coverage for desktop, tablet and iOS layouts.
- Verified the corrected runtime against the last confirmed working v4.20.37 launcher under the same browser-like MissionChief DOM.

'''
if "## [5.0.3] - 2026-07-23" not in changelog:
    changelog = replace_exact(changelog, anchor, anchor + notes, "changelog anchor")
CHANGELOG.write_text(changelog, encoding="utf-8")

CONTRACT.write_text(r'''#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
text = SOURCE.read_text(encoding="utf-8")

settings_declaration = "    const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;"
state_initializer = "    const state = loadState();"
default_function = "    function defaultOperationalWindowState"

assert text.count(settings_declaration) == 1
assert text.count(state_initializer) == 1
assert text.index(settings_declaration) < text.index(state_initializer)
assert text.index(state_initializer) < text.index(default_function)
assert "schemaVersion: OPERATIONAL_SUITE_SETTINGS_VERSION" in text
assert "// @version      5.0.3" in text
assert "version: '5.0.3'," in text
assert len(text.encode("utf-8")) > 500_000
assert text.rstrip().endswith("})();")
print("Issue #454 preboot state-order contract passed.")
''', encoding="utf-8")

validator = VALIDATOR.read_text(encoding="utf-8")
if "ISSUE454_PREBOOT_STATE_CONTRACT" not in validator:
    validator = replace_exact(
        validator,
        'ISSUE450_CORE_BOOTSTRAP_CONTRACT = ROOT / ".github" / "scripts" / "test_issue450_core_launcher_bootstrap.py"\n',
        'ISSUE450_CORE_BOOTSTRAP_CONTRACT = ROOT / ".github" / "scripts" / "test_issue450_core_launcher_bootstrap.py"\nISSUE454_PREBOOT_STATE_CONTRACT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"\n',
        "validator contract constant",
    )
    validator = replace_exact(
        validator,
        '''        if issue450_core_bootstrap.returncode != 0:
            fail("Issue #450 core launcher bootstrap contract failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
''',
        '''        if issue450_core_bootstrap.returncode != 0:
            fail("Issue #450 core launcher bootstrap contract failed")

        issue454_preboot_state = subprocess.run(
            [sys.executable, str(ISSUE454_PREBOOT_STATE_CONTRACT)],
            cwd=ROOT,
        )
        if issue454_preboot_state.returncode != 0:
            fail("Issue #454 preboot state-order contract failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
''',
        "validator contract execution",
    )
VALIDATOR.write_text(validator, encoding="utf-8")

fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
fixture["candidateVersion"] = "5.0.3"
HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

for path in DIAGNOSTICS:
    path.unlink(missing_ok=True)

subprocess.run(["python3", str(CONTRACT)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, env=ENV, check=True)

with tempfile.TemporaryDirectory(prefix="issue454-v503-runtime-") as tmp_raw:
    tmp = Path(tmp_raw)
    (tmp / "toolkit.user.js").write_text(source, encoding="utf-8")
    (tmp / "package.json").write_text(
        json.dumps({"private": True, "dependencies": {"jsdom": "26.1.0"}}),
        encoding="utf-8",
    )
    harness = r'''const fs = require('node:fs');
const { JSDOM, VirtualConsole } = require('jsdom');
const source = fs.readFileSync(process.argv[2], 'utf8');
const profiles = [
  { name: 'desktop', width: 1776, height: 864, touch: 0, ua: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36' },
  { name: 'tablet', width: 1024, height: 768, touch: 5, ua: 'Mozilla/5.0 (iPad; CPU OS 18_5 like Mac OS X) AppleWebKit/605.1.15 Version/18.5 Mobile/15E148 Safari/604.1' },
  { name: 'ios-mobile', width: 390, height: 844, touch: 5, ua: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 Version/18.5 Mobile/15E148 Safari/604.1' },
];
const sleep = (w, ms) => new Promise(resolve => w.setTimeout(resolve, ms));
async function run(profile) {
  const logs = [];
  const asyncErrors = [];
  const virtualConsole = new VirtualConsole();
  for (const level of ['log', 'info', 'warn', 'error']) {
    virtualConsole.on(level, (...args) => logs.push({ level, text: args.map(String).join(' ') }));
  }
  const dom = new JSDOM(`<!doctype html><html><head></head><body>
    <div id="map_outer"><div id="map" class="leaflet-container"></div></div>
    <div id="mission_list"><div id="mission_1" class="missionSideBarEntry"></div></div>
    <div id="radio_messages_important"></div><div id="radio_messages"></div>
    <div id="chat_panel_body"></div><div id="buildings"></div>
    <span id="credits_top">42,000,000</span>
  </body></html>`, {
    url: 'https://www.missionchief.co.uk/', runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole,
  });
  const w = dom.window;
  Object.defineProperty(w.document, 'readyState', { configurable: true, get: () => 'complete' });
  Object.defineProperty(w.navigator, 'userAgent', { configurable: true, value: profile.ua });
  Object.defineProperty(w.navigator, 'maxTouchPoints', { configurable: true, value: profile.touch });
  Object.defineProperty(w, 'innerWidth', { configurable: true, value: profile.width });
  Object.defineProperty(w, 'innerHeight', { configurable: true, value: profile.height });
  Object.defineProperty(w.screen, 'width', { configurable: true, value: profile.width });
  Object.defineProperty(w.screen, 'height', { configurable: true, value: profile.height });
  w.unsafeWindow = w;
  w.GM_getValue = (_key, fallback) => fallback;
  w.GM_setValue = () => undefined;
  w.GM_deleteValue = () => undefined;
  w.GM_xmlhttpRequest = details => { if (details?.onerror) w.setTimeout(() => details.onerror(new Error('network disabled')), 0); return { abort() {} }; };
  w.alert = () => undefined; w.confirm = () => false; w.prompt = () => null; w.open = () => null; w.scrollTo = () => undefined;
  w.matchMedia = query => ({ matches: false, media: query, onchange: null, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {}, dispatchEvent() { return false; } });
  w.requestIdleCallback = callback => w.setTimeout(() => callback({ didTimeout: false, timeRemaining: () => 50 }), 0);
  w.cancelIdleCallback = id => w.clearTimeout(id);
  w.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
  w.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} takeRecords() { return []; } };
  w.CSS ||= {}; w.CSS.escape ||= value => String(value).replace(/[^a-zA-Z0-9_-]/g, ch => `\\${ch}`);
  w.URL.createObjectURL ||= () => 'blob:runtime'; w.URL.revokeObjectURL ||= () => undefined;
  Object.defineProperty(w.navigator, 'clipboard', { configurable: true, value: { writeText: async () => undefined } });
  w.fetch = async () => ({ ok: true, status: 200, json: async () => ({}), text: async () => '', headers: new w.Headers() });
  const rect = { x: 0, y: 0, top: 0, left: 0, right: profile.width, bottom: 620, width: profile.width, height: 620, toJSON() { return this; } };
  w.Element.prototype.getBoundingClientRect = function () { return rect; };
  w.Element.prototype.getClientRects = function () { return [rect]; };
  w.HTMLElement.prototype.scrollIntoView = function () {};
  w.addEventListener('error', event => asyncErrors.push({ message: event.message, stack: event.error?.stack || '' }));
  w.addEventListener('unhandledrejection', event => asyncErrors.push({ message: String(event.reason), stack: event.reason?.stack || '' }));
  let evalError = null;
  try { w.eval(`${source}\n//# sourceURL=v5.0.3-${profile.name}.user.js`); }
  catch (error) { evalError = { name: error.name, message: error.message, stack: error.stack || '' }; }
  await sleep(w, 3500);
  const control = w.document.getElementById('mc-map-command-toolkit-control');
  const menuButton = control?.querySelector('.mcms-menu-btn') || null;
  const result = { profile: profile.name, evalError, asyncErrors, controlMounted: Boolean(control), menuButtonMounted: Boolean(menuButton), className: control?.className || null, consoleTail: logs.slice(-15) };
  w.close();
  return result;
}
(async () => {
  const results = [];
  for (const profile of profiles) results.push(await run(profile));
  process.stdout.write(JSON.stringify(results, null, 2));
  const failed = results.filter(result => result.evalError || !result.controlMounted || !result.menuButtonMounted);
  if (failed.length) process.exitCode = 1;
})().catch(error => { process.stderr.write(error.stack || String(error)); process.exitCode = 1; });
'''
    (tmp / "runtime.cjs").write_text(harness, encoding="utf-8")
    subprocess.run(["npm", "install", "--no-audit", "--no-fund", "--silent"], cwd=tmp, env=ENV, check=True)
    runtime = subprocess.run(
        ["node", str(tmp / "runtime.cjs"), str(tmp / "toolkit.user.js")],
        cwd=tmp,
        env=ENV,
        text=True,
        capture_output=True,
        timeout=60,
    )
    print("===== ISSUE #454 V5.0.3 PHYSICAL LAUNCHER RUNTIME =====")
    print(runtime.stdout)
    if runtime.stderr:
        print("===== RUNTIME STDERR =====")
        print(runtime.stderr)
    if runtime.returncode != 0:
        raise SystemExit("Issue #454 physical launcher runtime contract failed")

print("Prepared v5.0.3 preboot TDZ recovery with desktop, tablet and iOS launcher verification.")
