#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
SUMS = ROOT / "dist" / "SHA256SUMS.txt"
MANIFEST = ROOT / "dist" / "release-manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
TEST = ROOT / ".github" / "scripts" / "test_mission_value_contract.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")

source = replace_once(source, "// @version      4.13.7", "// @version      4.13.8", "metadata version")
source = replace_once(source, "version: '4.13.7',\n        author:", "version: '4.13.8',\n        author:", "runtime version")
source = replace_once(source, "styleId: 'mc-map-command-toolkit-style-v4137'", "styleId: 'mc-map-command-toolkit-style-v4138'", "style id")
source = replace_once(
    source,
    "pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4137__ = true;",
    "pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4137__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4138__ = true;",
    "version flag",
)
source = replace_once(source, "guideVersion: '4.13.7'", "guideVersion: '4.13.8'", "guide version")

source = replace_once(
    source,
    "    let desktopPanelObservedElements = new Set();\n",
    "    let desktopPanelObservedElements = new Set();\n"
    "    let missionValueScanTimer = null;\n"
    "    let missionValueFeatureInstalled = false;\n"
    "    const missionValueObservedDocuments = new WeakSet();\n"
    "    const missionValueObservedFrames = new WeakSet();\n"
    "    const missionValueRetryState = new WeakMap();\n",
    "mission value runtime state",
)

source = replace_once(
    source,
    "            missionLockAudio: true,\n",
    "            missionLockAudio: true,\n            missionValue: true,\n",
    "default mission value state",
)
source = replace_once(
    source,
    "        merged.missionLockAudio = merged.missionLockAudio !== false;\n",
    "        merged.missionLockAudio = merged.missionLockAudio !== false;\n        merged.missionValue = merged.missionValue !== false;\n",
    "mission value state normalisation",
)

mission_value_css = r'''
        .mcms-mission-value-row {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            width: 100% !important;
            min-height: 30px !important;
            box-sizing: border-box !important;
            margin: 0 0 8px 0 !important;
            padding: 5px 46px 5px 8px !important;
            clear: both !important;
            position: relative !important;
            z-index: 2 !important;
            pointer-events: none !important;
        }
        .mcms-mission-value-badge {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            max-width: min(100%, 260px) !important;
            min-height: 25px !important;
            box-sizing: border-box !important;
            padding: 4px 10px !important;
            border: 1px solid rgba(235,190,64,.72) !important;
            border-radius: 8px !important;
            background: linear-gradient(145deg, rgba(48,39,13,.96), rgba(19,21,24,.96)) !important;
            color: #ffe59a !important;
            box-shadow: 0 2px 8px rgba(0,0,0,.34) !important;
            font: 900 11px/1.25 Arial, Helvetica, sans-serif !important;
            letter-spacing: .15px !important;
            text-align: right !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            pointer-events: none !important;
        }
        @media (max-width: 520px) {
            .mcms-mission-value-row { padding-right: 40px !important; }
            .mcms-mission-value-badge { max-width: 100% !important; font-size: 10px !important; }
        }

'''
source = replace_once(
    source,
    "        .mcms-stuck-mission-icon { pointer-events:none !important; }",
    mission_value_css + "        .mcms-stuck-mission-icon { pointer-events:none !important; }",
    "mission value styles",
)

mission_value_functions = r'''
    function missionValueCurrencyMeta(hostname = location.hostname) {
        const host = String(hostname || '').trim().toLowerCase();
        if (/(?:^|\.)missionchief\.com$/u.test(host)) return { locale: 'en-US', symbol: '$' };
        if (/(?:^|\.)leitstellenspiel\.de$/u.test(host)) return { locale: 'de-DE', symbol: '€' };
        if (/(?:^|\.)meldkamerspel\.com$/u.test(host)) return { locale: 'nl-NL', symbol: '€' };
        return { locale: 'en-GB', symbol: '£' };
    }

    function formatMissionWindowValue(value, hostname = location.hostname) {
        const amount = Number(value);
        if (!Number.isFinite(amount) || amount < 0) return '';
        const { locale, symbol } = missionValueCurrencyMeta(hostname);
        return `${symbol}${Math.round(amount).toLocaleString(locale)}`;
    }

    function missionValueIdFromUrl(value, baseUrl = location.href) {
        let pathname = String(value || '').trim();
        if (!pathname) return null;
        try { pathname = new URL(pathname, baseUrl).pathname; } catch (err) {}
        const match = pathname.match(/\/missions\/(\d+)(?:\/|$)/u);
        return match ? normaliseMissionId(match[1]) : null;
    }

    function missionValueIdFromElement(root) {
        if (!root) return null;
        const doc = root.ownerDocument || document;
        const directNodes = [root];
        try {
            directNodes.push(...root.querySelectorAll('[data-mission-id], [data-mission_id], input[name="mission_id"], input[name="mission[id]"]'));
        } catch (err) {}
        for (const node of directNodes) {
            const candidates = [
                node?.dataset?.missionId,
                node?.dataset?.mission_id,
                node?.getAttribute?.('data-mission-id'),
                node?.getAttribute?.('data-mission_id'),
                node?.value
            ];
            for (const candidate of candidates) {
                const id = normaliseMissionId(candidate);
                if (id !== null) return id;
            }
            const idMatch = String(node?.id || '').match(/(?:^|_)(?:mission|mission_content|mission_panel)_(\d+)(?:$|_)/u);
            if (idMatch) return normaliseMissionId(idMatch[1]);
        }

        let routeNodes = [];
        try {
            routeNodes = Array.from(root.querySelectorAll('a[href*="/missions/"], form[action*="/missions/"], [data-url*="/missions/"], [data-href*="/missions/"]'));
        } catch (err) {}
        for (const node of routeNodes) {
            for (const attribute of ['href', 'action', 'data-url', 'data-href']) {
                const id = missionValueIdFromUrl(node.getAttribute?.(attribute), doc.location?.href || location.href);
                if (id !== null) return id;
            }
        }

        if (doc !== document) {
            try {
                const id = missionValueIdFromUrl(doc.location?.href, location.href);
                if (id !== null) return id;
            } catch (err) {}
        }
        return null;
    }

    function missionValueMountForRoot(root) {
        if (!root) return null;
        const selector = '.lightbox_content, .modal-body, #mission_content, .mission_content, [data-mission-content]';
        try {
            if (root.matches?.(selector)) return root;
            return root.querySelector?.(selector) || root;
        } catch (err) {
            return root;
        }
    }

    function missionValueWindowCandidates() {
        const candidates = new Map();
        const add = root => {
            if (!root?.isConnected) return;
            const missionId = missionValueIdFromElement(root);
            if (missionId === null) return;
            const mount = missionValueMountForRoot(root);
            if (!mount?.isConnected || mount.closest?.(`#${SCRIPT.panelId}, #${SCRIPT.helpCenterId}`)) return;
            if (!candidates.has(mount)) candidates.set(mount, { root, mount, missionId });
        };

        transportSweepVisibleWindowRoots().forEach(add);
        for (const context of transportSweepDocumentContexts()) {
            observeMissionValueDocument(context.doc);
            if (context.doc !== document) {
                try {
                    if (missionValueIdFromUrl(context.doc.location?.href, location.href) !== null) add(context.doc.body);
                } catch (err) {}
            }
        }
        return Array.from(candidates.values());
    }

    function removeMissionValueRows(scope = document) {
        try { scope.querySelectorAll?.('.mcms-mission-value-row').forEach(row => row.remove()); } catch (err) {}
    }

    function clearMissionValueIndicators() {
        for (const context of transportSweepDocumentContexts()) removeMissionValueRows(context.doc);
    }

    function syncMissionValueCandidate(candidate) {
        const { mount, missionId } = candidate || {};
        if (!mount?.isConnected || missionId === null) return false;
        const marker = getMissionMarkerIndex().byId.get(missionId) || getMissionMarkerIndex().byId.get(String(missionId)) || null;
        const snapshot = liveMissionSnapshots.get(missionId) || liveMissionSnapshots.get(String(missionId)) || missionSnapshotCache.get(missionId) || missionSnapshotCache.get(String(missionId)) || null;
        const details = criticalMissionValueDetails({ missionId, marker, snapshot });
        const formatted = formatMissionWindowValue(details.value);

        let rows = [];
        try { rows = Array.from(mount.querySelectorAll(':scope > .mcms-mission-value-row')); } catch (err) {
            try { rows = Array.from(mount.children || []).filter(child => child.classList?.contains('mcms-mission-value-row')); } catch (innerErr) {}
        }
        const row = rows.shift() || null;
        rows.forEach(extra => extra.remove());
        if (!formatted) {
            row?.remove();
            return false;
        }

        const doc = mount.ownerDocument || document;
        const nextRow = row || doc.createElement('div');
        if (!row) {
            nextRow.className = 'mcms-mission-value-row';
            nextRow.setAttribute('data-mcms-mission-value', 'true');
            const badge = doc.createElement('span');
            badge.className = 'mcms-mission-value-badge';
            nextRow.appendChild(badge);
            mount.insertBefore(nextRow, mount.firstChild || null);
        }
        nextRow.dataset.mcmsMissionId = String(missionId);
        const badge = nextRow.querySelector('.mcms-mission-value-badge');
        if (!badge) return false;
        const text = `Mission Value · ${formatted}`;
        if (badge.textContent !== text) badge.textContent = text;
        badge.title = `Mission Value · ${formatted} · ${details.source}`;
        return true;
    }

    function scheduleMissionValueScan(delay = 80) {
        runtimeClearTimeout(missionValueScanTimer);
        missionValueScanTimer = runtimeSetTimeout(() => {
            missionValueScanTimer = null;
            scanMissionValueWindows();
        }, Math.max(0, Number(delay) || 0));
    }

    function scanMissionValueWindows() {
        if (!state.missionValue) {
            clearMissionValueIndicators();
            return;
        }
        let needsRetry = false;
        for (const candidate of missionValueWindowCandidates()) {
            const rendered = syncMissionValueCandidate(candidate);
            if (rendered) {
                missionValueRetryState.delete(candidate.mount);
                continue;
            }
            const previous = missionValueRetryState.get(candidate.mount);
            const attempts = previous?.missionId === candidate.missionId ? previous.attempts : 0;
            if (attempts < 3) {
                missionValueRetryState.set(candidate.mount, { missionId: candidate.missionId, attempts: attempts + 1 });
                needsRetry = true;
            }
        }
        if (needsRetry) runtimeSetTimeout(() => scheduleMissionValueScan(0), 650);
    }

    function observeMissionValueFrame(frame) {
        if (!frame || missionValueObservedFrames.has(frame)) return;
        missionValueObservedFrames.add(frame);
        const onLoad = () => scheduleMissionValueScan(40);
        frame.addEventListener('load', onLoad);
        runtimeOnCleanup(() => frame.removeEventListener('load', onLoad));
    }

    function observeMissionValueDocument(doc) {
        if (!doc || missionValueObservedDocuments.has(doc)) return;
        missionValueObservedDocuments.add(doc);
        let frames = [];
        try { frames = Array.from(doc.querySelectorAll('iframe, frame')); } catch (err) {}
        frames.forEach(observeMissionValueFrame);
        const root = doc.documentElement || doc.body;
        if (!root) return;
        const activitySelector = '#lightbox_box, #lightbox, .lightbox_content, .modal, [role="dialog"], .ui-dialog, iframe, frame, a[href*="/missions/"], form[action*="/missions/"]';
        const observer = runtimeTrackObserver(new MutationObserver(mutations => {
            const relevant = mutations.some(mutation => Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || [])).some(node => {
                if (node?.nodeType !== 1) return false;
                if (node.matches?.(activitySelector)) return true;
                return Boolean(node.querySelector?.(activitySelector));
            }));
            if (!relevant) return;
            try { doc.querySelectorAll('iframe, frame').forEach(observeMissionValueFrame); } catch (err) {}
            scheduleMissionValueScan(50);
        }));
        observer.observe(root, { childList: true, subtree: true });
    }

    function installMissionValueWindows() {
        if (!missionValueFeatureInstalled) {
            missionValueFeatureInstalled = true;
            runtimeOnCleanup(() => {
                runtimeClearTimeout(missionValueScanTimer);
                missionValueScanTimer = null;
                clearMissionValueIndicators();
            });
        }
        for (const context of transportSweepDocumentContexts()) observeMissionValueDocument(context.doc);
        scheduleMissionValueScan(0);
        runtimeSetTimeout(() => scheduleMissionValueScan(0), 180);
        runtimeSetTimeout(() => scheduleMissionValueScan(0), 800);
    }

'''
source = replace_once(
    source,
    "    function criticalMissionValueForEntry(entry) {",
    mission_value_functions + "    function criticalMissionValueForEntry(entry) {",
    "mission value functions",
)

inspector_button = "                    ${makeToggleButton('missionInspector', 'ⓘ', 'Inspector', 'Hover a mission marker for a live mission summary.')}"
source = replace_once(
    source,
    inspector_button,
    inspector_button + "\n                    ${makeToggleButton('missionValue', '£', 'Mission Value', 'Show a formatted mission value in opened MissionChief windows.')}",
    "mission value Ops control",
)
source = replace_once(
    source,
    "        if (feature === 'missionInspector') state.missionInspector = !state.missionInspector;",
    "        if (feature === 'missionInspector') state.missionInspector = !state.missionInspector;\n        if (feature === 'missionValue') state.missionValue = !state.missionValue;",
    "mission value toggle",
)
source = replace_once(
    source,
    "        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });\n",
    "        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });\n"
    "        if (feature === 'missionValue') {\n"
    "            if (state.missionValue) installMissionValueWindows();\n"
    "            else clearMissionValueIndicators();\n"
    "            showToast(state.missionValue ? 'Mission Value on' : 'Mission Value off');\n"
    "        }\n",
    "mission value toggle effects",
)
source = replace_once(
    source,
    "            missionInspector: state.missionInspector,\n",
    "            missionInspector: state.missionInspector,\n            missionValue: state.missionValue,\n",
    "mission value UI state",
)
source = replace_once(
    source,
    "        installRadioMessageHook();\n",
    "        installRadioMessageHook();\n        if (state.missionValue) installMissionValueWindows();\n",
    "mission value startup",
)

SOURCE.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
release_notes = """## [4.13.8] - 2026-07-16

### Added
- Added a compact Mission Value indicator to dynamically opened MissionChief mission windows.
- Mission Value is enabled by default and can be turned on or off persistently from the Ops section on Desktop, Tablet and iOS.
- Values reuse the Toolkit's verified live marker, mission snapshot, captured overlay and mission-list data sources; unavailable values remain hidden rather than guessed.

### Compatibility
- The indicator uses normal document flow with reserved close-control space, preventing overlap with native mission controls.
- Existing themes, settings import/export, Economy Mode and mission-window behaviour are preserved.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + release_notes, "changelog")
CHANGELOG.write_text(changelog, encoding="utf-8")

test_source = r'''#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"


def extract_function(source: str, masked: str, name: str) -> str:
    matches = list(re.finditer(rf"\bfunction\s+{re.escape(name)}\s*\(", masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    opening = masked.find("{", start)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Could not extract {name}")
    return source[start:closing + 1]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    masked = audit.mask_non_code(source)
    required = [
        "missionValue: true",
        "merged.missionValue = merged.missionValue !== false",
        "makeToggleButton('missionValue', '£', 'Mission Value'",
        "if (feature === 'missionValue') state.missionValue = !state.missionValue",
        "missionValue: state.missionValue",
        "criticalMissionValueDetails({ missionId, marker, snapshot })",
        "installMissionValueWindows()",
        "clearMissionValueIndicators()",
        "transportSweepVisibleWindowRoots()",
        "transportSweepDocumentContexts()",
        "data-mcms-mission-value",
        ".mcms-mission-value-row",
        ".mcms-mission-value-badge",
    ]
    missing = [fragment for fragment in required if fragment not in source]
    assert not missing, f"Mission Value contract fragments missing: {missing}"

    row_rule = re.search(r"\.mcms-mission-value-row\s*\{(?P<body>.*?)\n\s*\}", source, re.S)
    assert row_rule, "Mission Value row style missing"
    row_body = row_rule.group("body")
    assert "position: absolute" not in row_body
    assert "justify-content: flex-end" in row_body
    assert "padding: 5px 46px 5px 8px" in row_body
    assert "pointer-events: none" in row_body

    functions = "\n\n".join(extract_function(source, masked, name) for name in [
        "missionValueCurrencyMeta",
        "formatMissionWindowValue",
        "missionValueIdFromUrl",
    ])
    harness = r'''"use strict";
const assert = require("node:assert/strict");
global.location = { hostname: "missionchief.co.uk", href: "https://missionchief.co.uk/" };
function normaliseMissionId(value) {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : null;
}
''' + functions + r'''
assert.equal(formatMissionWindowValue(12345, "missionchief.co.uk"), "£12,345");
assert.equal(formatMissionWindowValue(12345, "www.missionchief.com"), "$12,345");
assert.equal(formatMissionWindowValue(12345, "leitstellenspiel.de"), "€12.345");
assert.equal(formatMissionWindowValue(12345, "meldkamerspel.com"), "€12.345");
assert.equal(formatMissionWindowValue(-1, "missionchief.co.uk"), "");
assert.equal(formatMissionWindowValue("not-a-value", "missionchief.co.uk"), "");
assert.equal(missionValueIdFromUrl("/missions/98765"), 98765);
assert.equal(missionValueIdFromUrl("https://missionchief.co.uk/missions/42/missing_vehicles"), 42);
assert.equal(missionValueIdFromUrl("/vehicles/42"), null);
console.log("Mission Value formatting and route contract passed.");
'''
    with tempfile.TemporaryDirectory(prefix="mcms-mission-value-") as temp:
        path = Path(temp) / "contract.js"
        path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(path)], check=True, cwd=ROOT)
    print("Mission Value static integration contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
TEST.write_text(test_source, encoding="utf-8")
subprocess.run(["python3", str(TEST)], check=True, cwd=ROOT)
subprocess.run(["node", "--check", str(SOURCE)], check=True, cwd=ROOT)

payload = SOURCE.read_bytes()
DIST_USER.write_bytes(payload)
DIST_TEXT.write_bytes(payload)
digest = hashlib.sha256(payload).hexdigest()
SUMS.write_text(
    f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest = {
    "project": "MissionChief Map Command Toolkit",
    "version": "4.13.8",
    "source": "src/MissionChief_Map_Command_Toolkit.user.js",
    "distributionFiles": [
        "dist/MissionChief_Map_Command_Toolkit.user.js",
        "dist/MissionChief_Map_Command_Toolkit.txt",
    ],
    "sha256": digest,
    "bytes": len(payload),
    "lines": len(source.splitlines()),
    "metadata": {
        "name": "MissionChief Map Command Toolkit",
        "runtimeVersion": "4.13.8",
        "author": "Conroy1988",
        "license": "MIT",
        "missionChiefRules": [
            "*://missionchief.co.uk/*",
            "*://www.missionchief.co.uk/*",
            "*://*.missionchief.co.uk/*",
        ],
        "warnings": [],
    },
    "baselineHashMatch": None,
    "distributionStatus": "dry-run-not-yet-greasyfork-source",
}
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(f"Prepared Mission Value v4.13.8 candidate: {digest}")
