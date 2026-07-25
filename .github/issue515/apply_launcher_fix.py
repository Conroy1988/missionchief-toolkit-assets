#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
CHANGELOG = ROOT / "CHANGELOG.md"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
V7_CONTRACT = ROOT / ".github" / "scripts" / "test_v7_retirement.py"
STATIC_TEST = ROOT / ".github" / "scripts" / "test_issue515_launcher_restoration.py"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_issue515_launcher_runtime.js"
SELF = ROOT / ".github" / "issue515" / "apply_launcher_fix.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue515-launcher-fix.yml"

HELPERS = r'''    // Issue #515: restore the generic Toolkit launcher shell removed during v7 retirement.
    function toolkitTopLevelDocument(doc = document) {
        try {
            const view = doc?.defaultView;
            return !view || view.top === view;
        } catch (error) {
            return true;
        }
    }
    function toolkitPrimaryMapElement(mapEl, doc = document) {
        const missionSelector = '#mission-form,.mission-window,.mission_window,.modal,.modal-content,.lightbox,[data-mission-id]';
        const candidates = [
            doc?.querySelector?.('#map'),
            mapEl,
            ...Array.from(doc?.querySelectorAll?.('[data-leaflet-map="main"],.leaflet-container') || [])
        ];
        for (const candidate of candidates) {
            if (!candidate || candidate.ownerDocument !== doc || candidate.isConnected === false) continue;
            if (candidate.closest?.(missionSelector)) continue;
            return candidate;
        }
        return null;
    }
    function toolkitControlHost(mapEl, doc = document) {
        if (!toolkitTopLevelDocument(doc)) return null;
        return toolkitPrimaryMapElement(mapEl, doc) || doc?.body || doc?.documentElement || null;
    }
    function toolkitApplyCommandBarState(control = null) {
        control ||= document.querySelector?.(`#${SCRIPT.controlId}`) || null;
        if (!control) return false;
        const open = state.commandBarOpen !== false;
        control.setAttribute('data-mcms-command-bar-open', String(open));
        for (const selector of ['.mcms-floating-filter', '.mcms-screen-pins']) {
            const element = control.querySelector?.(selector);
            if (!element) continue;
            if (open) element.style.removeProperty('display');
            else element.style.setProperty('display', 'none', 'important');
        }
        const button = control.querySelector?.('.mcms-dock-toggle-btn');
        if (button) {
            const label = open ? 'Collapse command bar' : 'Expand command bar';
            button.classList.toggle('mcms-open', open);
            button.setAttribute('aria-expanded', String(open));
            button.setAttribute('aria-label', label);
            button.title = label;
            const icon = button.querySelector?.('.mcms-dock-toggle-icon');
            if (icon) icon.textContent = open ? '▴' : '▾';
        }
        return open;
    }

'''

STATIC_TEST_TEXT = r'''#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    metadata = re.search(r"(?m)^//\s*@version\s+([^\s]+)$", source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == "7.0.1"

    helpers = [
        "toolkitTopLevelDocument",
        "toolkitPrimaryMapElement",
        "toolkitControlHost",
        "toolkitApplyCommandBarState",
    ]
    for helper in helpers:
        assert source.count(f"function {helper}(") == 1, f"{helper} declaration count changed"

    toggle = source.index("    function toggleCommandBar()")
    for helper in helpers:
        assert source.index(f"    function {helper}(") < toggle, f"{helper} must exist before launcher use"

    create = section(source, "    function createControl(mapEl)", "    function createPanel()")
    assert "const primaryMap = toolkitPrimaryMapElement(mapEl, document);" in create
    assert "const host = toolkitControlHost(primaryMap, document);" in create
    assert "if (!host) return null;" in create
    assert "if (menuButton) { togglePanel(); return; }" in create
    assert "toolkitApplyCommandBarState(control);" in create
    assert "host.appendChild(control);" in create

    ensure = section(source, "    function ensureUi()", "    function mutationBelongsToToolkit")
    assert "if (!toolkitTopLevelDocument(document)) return true;" in ensure
    assert "const mapEl = toolkitPrimaryMapElement(discoveredMap, document);" in ensure
    assert "const control = createControl(mapEl);" in ensure
    assert "toolkitApplyCommandBarState(control);" in ensure
    assert "return Boolean(control || document.getElementById(SCRIPT.controlId));" in ensure

    assert "return toolkitPrimaryMapElement(mapEl, doc) || doc?.body || doc?.documentElement || null;" in source
    assert "#mission-form,.mission-window,.mission_window,.modal,.modal-content,.lightbox,[data-mission-id]" in source
    token = "ls" + "sm"
    assert token not in source.lower(), "retired integration reference returned"
    print("Issue #515 launcher restoration static contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

RUNTIME_TEST_TEXT = r'''#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');

function extractFunction(name) {
    const marker = `    function ${name}(`;
    const start = source.indexOf(marker);
    assert.ok(start >= 0, `${name} is missing`);
    const open = source.indexOf('{', start);
    let depth = 0;
    let quote = '';
    let escaped = false;
    for (let index = open; index < source.length; index += 1) {
        const char = source[index];
        if (quote) {
            if (escaped) escaped = false;
            else if (char === '\\') escaped = true;
            else if (char === quote) quote = '';
            continue;
        }
        if (char === '"' || char === "'" || char === '`') { quote = char; continue; }
        if (char === '{') depth += 1;
        if (char === '}') {
            depth -= 1;
            if (depth === 0) return source.slice(start, index + 1);
        }
    }
    throw new Error(`Could not extract ${name}`);
}

const helperSource = [
    'toolkitTopLevelDocument',
    'toolkitPrimaryMapElement',
    'toolkitControlHost',
    'toolkitApplyCommandBarState',
    'ensureUi',
].map(extractFunction).join('\n\n');

function styleNode() {
    return {
        values: new Map(),
        removeProperty(name) { this.values.delete(name); },
        setProperty(name, value, priority) { this.values.set(name, { value, priority }); },
    };
}

const filter = { style: styleNode() };
const pins = { style: styleNode() };
const icon = { textContent: '' };
const dock = {
    title: '',
    attrs: {},
    classList: { state: false, toggle(_name, value) { this.state = value; } },
    setAttribute(name, value) { this.attrs[name] = String(value); },
    querySelector(selector) { return selector === '.mcms-dock-toggle-icon' ? icon : null; },
};
const control = {
    attrs: {},
    setAttribute(name, value) { this.attrs[name] = String(value); },
    querySelector(selector) {
        if (selector === '.mcms-floating-filter') return filter;
        if (selector === '.mcms-screen-pins') return pins;
        if (selector === '.mcms-dock-toggle-btn') return dock;
        return null;
    },
};

function mapNode(doc, { mission = false, id = '' } = {}) {
    return {
        id,
        ownerDocument: doc,
        isConnected: true,
        closest() { return mission ? {} : null; },
    };
}

const view = {}; view.top = view;
const body = { name: 'body' };
const documentStub = {
    defaultView: view,
    body,
    documentElement: { name: 'html' },
    mainMap: null,
    maps: [],
    querySelector(selector) {
        if (selector === '#map') return this.mainMap;
        if (selector === '#control') return null;
        return null;
    },
    querySelectorAll() { return this.maps; },
    getElementById() { return null; },
};

const calls = [];
const sandbox = {
    console,
    Array,
    Boolean,
    String,
    document: documentStub,
    SCRIPT: { controlId: 'control', payoutFlashId: 'payout' },
    state: { commandBarOpen: true, economyMode: false, majorIncidentFeed: { enabled: false } },
    settingsPanelActivated: false,
    operationalStartupComplete: true,
    getLargestLeafletMap: () => null,
    createControl: map => { calls.push(map); return control; },
    createPanel() {},
    ensureVersionStatusButton() {},
    findLeafletMapInstance: () => null,
    applyLeafletEconomyPolicy() {},
    scheduleEconomyLayerSync() {},
    scheduleMajorIncidentFeedRender() {},
    removeMajorIncidentFeed() {},
    positionPayoutFlashOverlay() {},
};
vm.createContext(sandbox);
vm.runInContext(`${helperSource}\nthis.helpers={toolkitTopLevelDocument,toolkitPrimaryMapElement,toolkitControlHost,toolkitApplyCommandBarState,ensureUi};`, sandbox);
const helpers = sandbox.helpers;

assert.equal(helpers.toolkitTopLevelDocument(documentStub), true);
const childView = { top: view };
assert.equal(helpers.toolkitTopLevelDocument({ defaultView: childView }), false);
assert.equal(helpers.toolkitControlHost(null, documentStub), body, 'document fallback host must remain available before map discovery');

const missionMap = mapNode(documentStub, { mission: true });
const mainMap = mapNode(documentStub, { id: 'map' });
documentStub.mainMap = mainMap;
documentStub.maps = [missionMap, mainMap];
assert.equal(helpers.toolkitPrimaryMapElement(missionMap, documentStub), mainMap, 'main map must win over mission-window maps');
assert.equal(helpers.toolkitControlHost(missionMap, documentStub), mainMap);

helpers.toolkitApplyCommandBarState(control);
assert.equal(control.attrs['data-mcms-command-bar-open'], 'true');
assert.equal(dock.attrs['aria-expanded'], 'true');
assert.equal(icon.textContent, '▴');
sandbox.state.commandBarOpen = false;
helpers.toolkitApplyCommandBarState(control);
assert.equal(control.attrs['data-mcms-command-bar-open'], 'false');
assert.equal(filter.style.values.get('display').value, 'none');
assert.equal(pins.style.values.get('display').priority, 'important');
assert.equal(icon.textContent, '▾');

sandbox.state.commandBarOpen = true;
documentStub.mainMap = null;
documentStub.maps = [];
calls.length = 0;
assert.equal(helpers.ensureUi(), true);
assert.equal(calls.length, 1);
assert.equal(calls[0], null, 'launcher must mount through the document fallback before a map exists');

documentStub.mainMap = mainMap;
calls.length = 0;
assert.equal(helpers.ensureUi(), true);
assert.equal(calls[0], mainMap, 'launcher must bind to the primary map when available');

console.log('Issue #515 launcher runtime contract passed.');
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    for helper in (
        "toolkitTopLevelDocument",
        "toolkitPrimaryMapElement",
        "toolkitControlHost",
        "toolkitApplyCommandBarState",
    ):
        if f"function {helper}(" in source:
            raise SystemExit(f"Unexpected existing declaration: {helper}")
        if helper not in source:
            raise SystemExit(f"Expected live reference is missing: {helper}")

    source = replace_once(source, "// @version      7.0.0", "// @version      7.0.1", "metadata version")
    source = replace_once(source, "version: '7.0.0'", "version: '7.0.1'", "runtime version")
    anchor = "    function toggleCommandBar() {"
    if anchor not in source:
        raise SystemExit("Launcher insertion anchor is missing")
    source = source.replace(anchor, HELPERS + anchor, 1)
    SOURCE.write_text(source, encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    release = """## [7.0.1] - 2026-07-25\n\n### Emergency launcher restoration\n\n- Restored the four generic Toolkit launcher-shell helpers accidentally removed during the v7 retirement.\n- Restored primary-map ownership, safe document fallback mounting and command-bar open/collapsed reconciliation.\n- Prevented child frames and mission-window maps from stealing the Toolkit launcher.\n- Added permanent static and executable runtime contracts for launcher declarations, fallback mounting and menu ownership.\n- No retired integration runtime, settings, observers or selectors were restored.\n\n"""
    if "## [7.0.1]" not in changelog:
        changelog = replace_once(changelog, "## [7.0.0]", release + "## [7.0.0]", "v7.0.0 changelog heading")
    CHANGELOG.write_text(changelog, encoding="utf-8")

    v7 = V7_CONTRACT.read_text(encoding="utf-8")
    v7 = replace_once(
        v7,
        '    assert re.search(r"(?m)^// @version\\s+7\\.0\\.0$", source)\n    assert "version: \'7.0.0\'" in source',
        '    metadata = re.search(r"(?m)^// @version\\s+([0-9]+)\\.([0-9]+)\\.([0-9]+)$", source)\n    runtime = re.search(r"version:\\s*\'([^\']+)\'", source)\n    assert metadata and runtime and metadata.group(0).split()[-1] == runtime.group(1)\n    assert tuple(map(int, metadata.groups())) >= (7, 0, 0)',
        "v7 version assertions",
    )
    V7_CONTRACT.write_text(v7, encoding="utf-8")

    STATIC_TEST.write_text(STATIC_TEST_TEXT, encoding="utf-8")
    RUNTIME_TEST.write_text(RUNTIME_TEST_TEXT, encoding="utf-8")

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    preflight = replace_once(
        preflight,
        ".github/scripts/test_v7_retirement.py .github/scripts/test_mission_age_retention.py",
        ".github/scripts/test_issue515_launcher_restoration.py .github/scripts/test_v7_retirement.py .github/scripts/test_mission_age_retention.py",
        "Python preflight contract route",
    )
    preflight = replace_once(
        preflight,
        "node .github/scripts/test_transport_sweep_runtime.js",
        "node .github/scripts/test_transport_sweep_runtime.js\nnode .github/scripts/test_issue515_launcher_runtime.js",
        "JavaScript preflight contract route",
    )
    PREFLIGHT.write_text(preflight, encoding="utf-8")

    SELF.unlink(missing_ok=True)
    WORKFLOW.unlink(missing_ok=True)
    issue_dir = SELF.parent
    try:
        issue_dir.rmdir()
    except OSError:
        pass
    print("Issue #515 launcher restoration applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
