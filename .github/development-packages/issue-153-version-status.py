#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
FRAGMENT = ROOT / ".github" / "development-packages" / "issue-153-version-status.jsfrag"
DIAGNOSTIC = ROOT / ".github" / "development-packages" / "issue-153-diagnostic.txt"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_version_status_runtime.js"
CONTRACT_TEST = ROOT / ".github" / "scripts" / "test_version_status_contract.py"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release-toolkit.yml"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
SITE_DATA = ROOT / "docs" / "site-data.json"
DASHBOARD = ROOT / "status" / "release-dashboard.json"
UPDATE_MANIFEST = ROOT / "status" / "update-manifest.json"

PREVIOUS = "4.19.2"
VERSION = "4.20.0"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {PREVIOUS}", f"// @version      {VERSION}", "metadata version")
source = replace_once(source, f"        version: '{PREVIOUS}',", f"        version: '{VERSION}',", "runtime version")
fragment = FRAGMENT.read_text(encoding="utf-8").rstrip("\n")
source = replace_once(source, "    function createCleanExit() {", fragment + "\n\n    function createCleanExit() {", "version-status runtime insertion")
source = replace_once(source, "            createControl(mapEl);\n            const map = findLeafletMapInstance(false);", "            createControl(mapEl);\n            ensureVersionStatusButton();\n            const map = findLeafletMapInstance(false);", "version-status control mount")
source = replace_once(source, "                scheduleDeferredOperationalStartup();\n                runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);", "                scheduleDeferredOperationalStartup();\n                scheduleVersionStatusCheck(VERSION_STATUS.bootDelayMs, false);\n                runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);", "delayed boot check")
source = replace_once(source, "            runtimeWakeTaskScheduler(0);\n            ensureUi();\n            refreshSuppression();", "            runtimeWakeTaskScheduler(0);\n            ensureUi();\n            scheduleVersionStatusCheck(0, false);\n            refreshSuppression();", "visibility stale refresh")
source = replace_once(source, "            closeHelpCenter({ restoreFocus: false });\n            helpGuideDocumentCache = '';", "            closeHelpCenter({ restoreFocus: false });\n            disposeVersionStatus();\n            helpGuideDocumentCache = '';", "version-status cleanup")
if len(source.splitlines()) > 32000:
    raise AssertionError(f"v{VERSION} source exceeds 32,000-line release ceiling: {len(source.splitlines())}")
SOURCE.write_text(source, encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")

runtime_test = r'''#!/usr/bin/env node
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const startMarker = '    // Issue #153: stable live Toolkit version-status control.';
const endMarker = '    function createCleanExit() {';
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker, start);
assert(start >= 0 && end > start, 'unable to extract Issue #153 runtime block');
const block = source.slice(start, end);

class FakeClassList { constructor() { this.values = new Set(); } contains(value) { return this.values.has(value); } toggle(value, force) { const enabled = force === undefined ? !this.values.has(value) : Boolean(force); if (enabled) this.values.add(value); else this.values.delete(value); return enabled; } }
class FakeElement {
    constructor(tagName = 'div', ownerDocument = null) { this.tagName = String(tagName).toUpperCase(); this.ownerDocument = ownerDocument; this.id = ''; this.type = ''; this.className = ''; this.textContent = ''; this.title = ''; this.dataset = {}; this.attributes = new Map(); this.classList = new FakeClassList(); this.children = []; this.parentNode = null; this.queryMap = new Map(); this.listeners = new Map(); this.isConnected = true; }
    setAttribute(name, value) { this.attributes.set(name, String(value)); if (name === 'id') this.id = String(value); }
    getAttribute(name) { return this.attributes.get(name) || null; }
    querySelector(selector) { return this.queryMap.get(selector) || null; }
    addEventListener(type, listener) { const list = this.listeners.get(type) || []; list.push(listener); this.listeners.set(type, list); }
    appendChild(child) { child.parentNode = this; child.ownerDocument ||= this.ownerDocument; child.isConnected = true; this.children.push(child); child.ownerDocument?.nodes.add(child); return child; }
    insertBefore(child, reference) { if (child.parentNode) child.parentNode.children = child.parentNode.children.filter(item => item !== child); child.parentNode = this; child.ownerDocument ||= this.ownerDocument; child.isConnected = true; const index = this.children.indexOf(reference); if (index >= 0) this.children.splice(index, 0, child); else this.children.push(child); child.ownerDocument?.nodes.add(child); return child; }
    contains(node) { return this === node || this.children.some(child => child.contains?.(node)); }
    remove() { this.isConnected = false; if (this.parentNode) this.parentNode.children = this.parentNode.children.filter(child => child !== this); this.ownerDocument?.nodes.delete(this); }
}
class FakeDocument {
    constructor() { this.nodes = new Set(); this.documentElement = new FakeElement('html', this); this.head = new FakeElement('head', this); this.body = new FakeElement('body', this); this.nodes.add(this.documentElement); this.nodes.add(this.head); this.nodes.add(this.body); }
    createElement(tagName) { return new FakeElement(tagName, this); }
    getElementById(id) { return Array.from(this.nodes).find(node => node.isConnected && node.id === id) || null; }
}

const localValues = new Map();
const openedUrls = [];
const listenedEvents = [];
const document = new FakeDocument();
const context = {
    console, URL, Promise, Date, Object, Array, Number, String, Error, JSON, RegExp, Math, Set,
    queueMicrotask,
    globalThis: null,
    SCRIPT: { name: 'MissionChief Map Command Toolkit', version: '4.20.0', controlId: 'mc-map-command-toolkit-control' },
    pageWindow: { localStorage: { getItem: key => localValues.has(key) ? localValues.get(key) : null, setItem: (key, value) => localValues.set(key, String(value)), removeItem: key => localValues.delete(key) }, open: url => { openedUrls.push(url); return { opener: {} }; }, fetch: null, AbortController },
    document,
    runtime: { destroyed: false, requests: new Set(), fetchControllers: new Set() },
    runtimeListen: (target, type, listener, options) => { target.addEventListener(type, listener, options); listenedEvents.push({ target, type, listener, options }); },
    runtimeSetTimeout: (callback, delay) => setTimeout(callback, delay),
    runtimeClearTimeout: timer => clearTimeout(timer),
    showToast: () => {},
};
context.globalThis = context;
vm.createContext(context);
vm.runInContext(block + `\nthis.__versionStatusApi = { constants: VERSION_STATUS, parse: versionStatusParse, compare: versionStatusCompare, validate: versionStatusValidateManifest, presentation: versionStatusPresentation, cacheFresh: versionStatusCacheIsFresh, failureCooling: versionStatusFailureCooling, ensureButton: ensureVersionStatusButton, requestManifest: versionStatusRequestManifest, runCheck: runVersionStatusCheck, render: versionStatusRender, model: () => versionStatusModel, reset: () => { versionStatusModel = { state: 'idle', manifest: null, checkedAt: 0, error: '' }; versionStatusCheckPromise = null; versionStatusHydrationPromise = null; versionStatusTimer = null; versionStatusRequest = null; } };` , context);
const api = context.__versionStatusApi;
const manifest = version => ({ schemaVersion: 1, channel: 'stable', version, releaseNotesUrl: `https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v${version}`, updateUrl: 'https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js', publishedAt: '2026-07-19T13:08:02Z' });

(async () => {
    assert.deepStrictEqual(Array.from(api.parse('4.15.10')), [4, 15, 10], 'stable semantic version parses numerically');
    assert.strictEqual(api.parse('4.15'), null, 'malformed installed version is rejected');
    assert.strictEqual(api.parse('4.20.0-beta.1'), null, 'prerelease version is not accepted as stable');
    assert.strictEqual(api.compare('4.15.10', '4.15.9'), 1, 'multi-digit patch versions compare numerically');
    assert.strictEqual(api.compare('4.16.0', '4.15.99'), 1, 'minor update compares numerically');
    assert.strictEqual(api.compare('bad', '4.15.9'), null, 'malformed comparison fails safely');

    const current = api.validate(manifest('4.20.0'));
    assert.strictEqual(api.presentation('4.20.0', current).state, 'latest', 'equal stable version displays LATEST');
    assert.strictEqual(api.presentation('4.20.0', current).destination, current.releaseNotesUrl, 'LATEST opens matching GitHub release notes');
    const patch = api.validate(manifest('4.20.1'));
    assert.strictEqual(api.presentation('4.20.0', patch).state, 'update', 'published patch update displays UPDATE');
    assert.strictEqual(api.presentation('4.20.0', patch).destination, patch.updateUrl, 'UPDATE opens Greasy Fork update URL');
    assert.throws(() => api.validate({ ...manifest('4.20.1-beta.1'), version: '4.20.1-beta.1' }), /stable semantic version/, 'draft or prerelease manifest is rejected');
    assert.throws(() => api.validate({ ...manifest('4.20.1'), releaseNotesUrl: 'https://example.com/release' }), /canonical/, 'non-canonical release URL is rejected');

    const now = 10_000_000;
    assert.strictEqual(api.cacheFresh({ checkedAt: now - (29 * 60 * 1000), manifest: current }, now), true, '29-minute successful cache is fresh');
    assert.strictEqual(api.cacheFresh({ checkedAt: now - (30 * 60 * 1000), manifest: current }, now), false, '30-minute successful cache is stale');
    assert.strictEqual(api.failureCooling({ failedAt: now - (9 * 60 * 1000) }, now), true, '9-minute failure remains in cooldown');
    assert.strictEqual(api.failureCooling({ failedAt: now - (10 * 60 * 1000) }, now), false, '10-minute failure cooldown expires');

    const control = document.createElement('div'); control.id = context.SCRIPT.controlId;
    const row = document.createElement('div'); const shell = document.createElement('div'); const economy = document.createElement('button'); economy.className = 'mcms-economy-btn';
    control.queryMap.set('.mcms-launch-row', row); row.queryMap.set('.mcms-economy-btn', economy);
    document.body.appendChild(control); control.appendChild(row); row.appendChild(shell); row.appendChild(economy);
    const first = api.ensureButton(); const second = api.ensureButton();
    assert.strictEqual(first, second, 'repeated Toolkit UI recovery does not duplicate version control');
    assert.strictEqual(document.getElementById(api.constants.buttonId), first, 'version control uses one collision-resistant ID');
    assert.strictEqual(row.children.indexOf(first), row.children.indexOf(economy) - 1, 'version control is placed immediately before Economy beside the main Toolkit shell');
    const styleText = document.getElementById(api.constants.styleId).textContent;
    assert(styleText.includes('data-mcms-tablet-active'), 'Tablet-specific version-control styling is present');
    assert(styleText.includes('data-mcms-mobile-active'), 'iOS/Mobile-specific version-control styling is present');

    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.ontimeout()); return { abort() {} }; };
    await assert.rejects(api.requestManifest(), /timed out/, 'network timeout rejects without reporting LATEST');
    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onerror()); return { abort() {} }; };
    api.reset(); await api.runCheck(true); assert.strictEqual(api.model().state, 'error', 'rejected request renders retry/error state');
    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('4.20.1')) })); return { abort() {} }; };
    api.reset(); await api.runCheck(true); assert.strictEqual(api.model().state, 'update', 'successful live response renders UPDATE');

    console.log('Version status runtime fixtures passed');
})().catch(error => { console.error(error); process.exit(1); });
'''
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")
RUNTIME_TEST.chmod(0o755)

contract_test = r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_version_status_runtime.js"
WORKFLOW = ROOT / ".github" / "workflows" / "release-toolkit.yml"
MANIFEST = ROOT / "status" / "update-manifest.json"
DASHBOARD = ROOT / "status" / "release-dashboard.json"


def semver(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(value or ""))
    assert match, f"stable semantic version required: {value!r}"
    return tuple(int(part) for part in match.groups())


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
    start = source.index("    // Issue #153: stable live Toolkit version-status control.")
    end = source.index("    function createCleanExit() {", start)
    block = source[start:end]

    assert source.count("// Issue #153: stable live Toolkit version-status control.") == 1
    assert "cacheMs: 30 * 60 * 1000" in block
    assert "failureCooldownMs: 10 * 60 * 1000" in block
    assert "requestTimeoutMs: 8 * 1000" in block
    assert "bootDelayMs: 15 * 1000" in block
    assert "setInterval(" not in block, "version checker must not poll continuously"
    for marker in [
        "function versionStatusCompare(left, right)",
        "function versionStatusValidateManifest(payload)",
        "function versionStatusCacheIsFresh(cache, now = Date.now())",
        "function ensureVersionStatusButton()",
        "function versionStatusRequestManifest()",
        "function scheduleVersionStatusCheck(delay = VERSION_STATUS.bootDelayMs, force = false)",
        "function disposeVersionStatus()",
        "data-mcms-tablet-active",
        "data-mcms-mobile-active",
        "runtime.requests?.add?.(versionStatusRequest)",
    ]:
        assert marker in block, f"version-status runtime marker missing: {marker}"
    assert "raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/status/update-manifest.json" in block
    assert "scheduleVersionStatusCheck(VERSION_STATUS.bootDelayMs, false);" in source
    assert "scheduleVersionStatusCheck(0, false);" in source
    assert "disposeVersionStatus();" in source
    assert "ensureVersionStatusButton();" in source
    assert source.count("@connect      raw.githubusercontent.com") == 1
    assert len(source.splitlines()) <= 32000, "source exceeds release performance line ceiling"

    assert manifest["schemaVersion"] == 1
    assert manifest["channel"] == "stable"
    assert semver(manifest["version"]) == semver(dashboard["latestRelease"]["version"])
    source_version = re.search(r"// @version\s+([^\s]+)", source).group(1)
    assert semver(manifest["version"]) <= semver(source_version)
    assert manifest["releaseNotesUrl"].endswith(f"/releases/tag/v{manifest['version']}")
    assert manifest["updateUrl"].startswith("https://update.greasyfork.org/scripts/586018/")

    for marker in [
        "status/update-manifest.json",
        "schemaVersion:1,channel:\"stable\"",
        "releaseNotesUrl:$releaseNotesUrl",
        "updateUrl:$updateUrl",
        "publishedAt:$publishedAt",
        "git add status/release-dashboard.json status/README.md status/update-manifest.json",
    ]:
        assert marker in workflow, f"release workflow does not own stable update manifest: {marker}"
    dashboard_index = workflow.index("Record successful release in dashboard")
    manifest_index = workflow.index("status/update-manifest.json", dashboard_index)
    push_index = workflow.index("git push origin HEAD:main", dashboard_index)
    assert dashboard_index < manifest_index < push_index, "manifest must update only inside verified release reconciliation"

    result = subprocess.run(["node", str(RUNTIME)], cwd=ROOT)
    assert result.returncode == 0, "version status runtime fixtures failed"
    print("Version status contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
CONTRACT_TEST.write_text(contract_test, encoding="utf-8")
CONTRACT_TEST.chmod(0o755)

validator = VALIDATOR.read_text(encoding="utf-8")
validator = replace_once(validator, 'MISSION_REQUIREMENTS_CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"\n', 'MISSION_REQUIREMENTS_CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"\nVERSION_STATUS_CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"\n', "validator contract constant")
validator = replace_once(validator, 'required = [INTEGRITY_AUDITOR, INTEGRITY_POLICY, ASSET_AUDITOR, AUDIO_ALIAS_AUDITOR, MISSION_REQUIREMENTS_CONTRACT]', 'required = [INTEGRITY_AUDITOR, INTEGRITY_POLICY, ASSET_AUDITOR, AUDIO_ALIAS_AUDITOR, MISSION_REQUIREMENTS_CONTRACT, VERSION_STATUS_CONTRACT]', "validator required tooling")
validator = replace_once(validator, '        if mission_requirements.returncode != 0:\n            fail("live mission requirements contract failed")\n\n        report = json.loads(integrity_json.read_text(encoding="utf-8"))', '        if mission_requirements.returncode != 0:\n            fail("live mission requirements contract failed")\n\n        version_status = subprocess.run(\n            [sys.executable, str(VERSION_STATUS_CONTRACT)],\n            cwd=ROOT,\n        )\n        if version_status.returncode != 0:\n            fail("live version-status contract failed")\n\n        report = json.loads(integrity_json.read_text(encoding="utf-8"))', "validator version-status execution")
VALIDATOR.write_text(validator, encoding="utf-8")

release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
release = replace_once(release, '           RELEASE_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/releases/tag/v${RELEASE_VERSION}"\n           jq --arg version "$RELEASE_VERSION" --arg hash "$HASH" --arg now "$NOW" \\\n', '           RELEASE_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/releases/tag/v${RELEASE_VERSION}"\n           INSTALL_URL="$(jq -r \' .greasyFork.installUrl\' .github/release-settings.json)"\n           jq -n --arg version "$RELEASE_VERSION" --arg releaseNotesUrl "$RELEASE_URL" --arg updateUrl "$INSTALL_URL" --arg publishedAt "$NOW" \\\n             \'{schemaVersion:1,channel:"stable",version:$version,releaseNotesUrl:$releaseNotesUrl,updateUrl:$updateUrl,publishedAt:$publishedAt}\' \\\n             > status/update-manifest.json\n           jq --arg version "$RELEASE_VERSION" --arg hash "$HASH" --arg now "$NOW" \\\n', "verified manifest generation")
release = release.replace("INSTALL_URL=\"$(jq -r ' .greasyFork.installUrl'", "INSTALL_URL=\"$(jq -r '.greasyFork.installUrl'")
release = replace_once(release, '           git add status/release-dashboard.json status/README.md\n', '           git add status/release-dashboard.json status/README.md status/update-manifest.json\n', "release manifest commit")
RELEASE_WORKFLOW.write_text(release, encoding="utf-8")

release_dashboard = json.loads(DASHBOARD.read_text(encoding="utf-8"))
stable = release_dashboard.get("latestRelease") or {}
stable_version = str(stable.get("version") or PREVIOUS)
if stable_version != PREVIOUS:
    raise AssertionError(f"latest verified release moved during package preparation: {stable_version}")
UPDATE_MANIFEST.write_text(json.dumps({
    "schemaVersion": 1,
    "channel": "stable",
    "version": stable_version,
    "releaseNotesUrl": f"https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v{stable_version}",
    "updateUrl": "https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js",
    "publishedAt": str(stable.get("completedAt") or release_dashboard.get("lastUpdated") or ""),
}, indent=2) + "\n", encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = f'''## [Unreleased]\n\n## [{VERSION}] - 2026-07-19\n\n### Added\n- Added a compact live **LATEST / UPDATE** control beside the main Toolkit map button.\n- Added a guarded repository-owned stable update manifest that is reconciled only after GitHub Release, Greasy Fork, private backup and Discord publication succeed.\n- Added semantic numeric version comparison, canonical release/update destinations and accessible installed/available version labels.\n\n### Behaviour\n- Delays the first automatic check by 15 seconds, caches successful results for 30 minutes and applies a 10-minute cooldown after failures.\n- Rechecks a stale cache when MissionChief becomes visible again, supports Shift-click, right-click and touch long-press manual refresh, and never polls continuously.\n- Fails safely as **RETRY** rather than falsely reporting **LATEST** when the network or manifest is unavailable.\n\n### Validation\n- Added deterministic semantic-version, cache, cooldown, timeout, failure, destination, duplicate-control and responsive-layout fixtures.\n\n'''
changelog = replace_once(changelog, "## [Unreleased]\n\n", entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_index = HELP_INDEX.read_text(encoding="utf-8")
help_index = replace_once(help_index, f"Guide for Toolkit v{PREVIOUS}", f"Guide for Toolkit v{VERSION}", "help guide version")
HELP_INDEX.write_text(help_index, encoding="utf-8")

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-19"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.20.0 adds a live LATEST / UPDATE map control using a verified stable manifest, a 30-minute success cache, a 10-minute failure cooldown and manual rechecking."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
category = next((item for item in site_data.get("featureCategories", []) if item.get("name") == "Toolkit and releases"), None)
if category is None:
    category = {"name": "Toolkit and releases", "description": "Keep the Toolkit current and verify release state without leaving the MissionChief map.", "features": []}
    site_data.setdefault("featureCategories", []).append(category)
if not any(feature.get("name") == "Live Version Status" for feature in category["features"]):
    category["features"].append({"name": "Live Version Status", "summary": "Shows LATEST or UPDATE beside the main map control using the verified production release contract.", "details": ["30-minute successful cache and 10-minute failure cooldown", "15-second delayed boot check with visibility-based stale refresh", "GitHub release notes for LATEST and Greasy Fork installation for UPDATE", "Desktop, Tablet and iOS-safe placement with manual rechecking"], "visual": "version-status", "tags": ["updates", "releases", "status"]})
SITE_DATA.write_text(json.dumps(site_data, indent=2) + "\n", encoding="utf-8")

FRAGMENT.unlink(missing_ok=True)
DIAGNOSTIC.unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
print(f"Prepared Toolkit {VERSION} live version-status implementation")
