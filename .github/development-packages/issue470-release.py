#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
CHANGELOG = ROOT / 'CHANGELOG.md'
FIXTURE = ROOT / '.github/fixtures/main-style-source-headroom.json'
VALIDATOR = ROOT / '.github/scripts/validate_userscript.py'
TEST = ROOT / '.github/scripts/test_issue470_menu_requirements_runtime.js'
MANIFEST = ROOT / 'dist/release-manifest.json'
SUMS = ROOT / 'dist/SHA256SUMS.txt'

text = SOURCE.read_text(encoding='utf-8')


def function_span(source: str, name: str) -> tuple[int, int]:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\(', source)
    if not match:
        raise SystemExit(f'Missing function: {name}')
    paren = source.find('(', match.start())
    pdepth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    body_open = -1
    i = paren
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ''
        if line_comment:
            if ch == '\n':
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == '/' and nxt == '/':
            line_comment = True
            i += 2
            continue
        if ch == '/' and nxt == '*':
            block_comment = True
            i += 2
            continue
        if ch in "'\"`":
            quote = ch
            i += 1
            continue
        if ch == '(':
            pdepth += 1
        elif ch == ')':
            pdepth -= 1
            if pdepth == 0:
                body_open = source.find('{', i + 1)
                break
        i += 1
    if body_open < 0:
        raise SystemExit(f'Missing body for function: {name}')
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = body_open
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ''
        if line_comment:
            if ch == '\n':
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == '/' and nxt == '/':
            line_comment = True
            i += 2
            continue
        if ch == '/' and nxt == '*':
            block_comment = True
            i += 2
            continue
        if ch in "'\"`":
            quote = ch
            i += 1
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return match.start(), i + 1
        i += 1
    raise SystemExit(f'Unclosed function: {name}')


def replace_function(source: str, name: str, replacement: str) -> str:
    start, end = function_span(source, name)
    return source[:start] + replacement.rstrip() + source[end:]


if '// @version      5.0.6' not in text or "version: '5.0.6'" not in text:
    raise SystemExit('Issue #470 package requires Toolkit v5.0.6')
text = text.replace('// @version      5.0.6', '// @version      5.0.7', 1)
text = text.replace("version: '5.0.6'", "version: '5.0.7'", 1)

old_host = "    function toolkitControlHost(mapEl, doc = document) { return mapEl || doc?.body || doc?.documentElement || null; }"
new_host = r'''    function toolkitPrimaryMapElement(mapEl, doc = document) {
        const missionSelector = '#mission-form,.mission-window,.mission_window,.modal,.modal-content,.lightbox,[data-mission-id]';
        const candidates = [doc?.getElementById?.('map'), mapEl, ...Array.from(doc?.querySelectorAll?.('[data-leaflet-map="main"],.leaflet-container') || [])];
        for (const candidate of candidates) {
            if (!candidate || candidate.ownerDocument !== doc || candidate.isConnected === false) continue;
            if (candidate.closest?.(missionSelector)) continue;
            return candidate;
        }
        return null;
    }
    function toolkitControlHost(mapEl, doc = document) { return toolkitPrimaryMapElement(mapEl, doc) || doc?.body || doc?.documentElement || null; }
    function toolkitApplyCommandBarState(control = document.getElementById(SCRIPT.controlId)) {
        if (!control) return false;
        const open = state.commandBarOpen !== false;
        control.setAttribute('data-mcms-command-bar-open', String(open));
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
    }'''
if text.count(old_host) != 1:
    raise SystemExit(f'Toolkit host anchor count changed: {text.count(old_host)}')
text = text.replace(old_host, new_host, 1)

old_css = '''        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins { display: none !important; }'''
new_css = '''        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-floating-filter,
        html[data-mcms-command-bar-open="false"] #${SCRIPT.controlId} .mcms-screen-pins,
        #${SCRIPT.controlId}[data-mcms-command-bar-open="false"] .mcms-floating-filter,
        #${SCRIPT.controlId}[data-mcms-command-bar-open="false"] .mcms-screen-pins { display: none !important; }'''
if text.count(old_css) != 1:
    raise SystemExit(f'Command-bar CSS anchor count changed: {text.count(old_css)}')
text = text.replace(old_css, new_css, 1)

create_start, create_end = function_span(text, 'createControl')
create_body = text[create_start:create_end]
old_create_open = '''function createControl(mapEl) {
        const host = toolkitControlHost(mapEl, document);
        if (!host) return null;
        const existing = document.getElementById(SCRIPT.controlId);
        if (existing) {
            if (existing.parentElement !== host) host.appendChild(existing);
            existing.classList.toggle('mcms-control-fallback', !mapEl);
            return existing;
        }'''
new_create_open = '''function createControl(mapEl) {
        const primaryMap = toolkitPrimaryMapElement(mapEl, document);
        const host = primaryMap || document.body || document.documentElement;
        if (!host) return null;
        const existing = document.getElementById(SCRIPT.controlId);
        if (existing) {
            if (existing.parentElement !== host) host.appendChild(existing);
            existing.classList.toggle('mcms-control-fallback', !primaryMap);
            toolkitApplyCommandBarState(existing);
            return existing;
        }'''
if create_body.count(old_create_open) != 1:
    raise SystemExit(f'createControl opening anchor count changed: {create_body.count(old_create_open)}')
create_body = create_body.replace(old_create_open, new_create_open, 1)
old_create_close = '''        host.appendChild(control);
        control.classList.toggle('mcms-control-fallback', !mapEl);
        renderScreenPins();
        updateUI();
        return control;'''
new_create_close = '''        toolkitApplyCommandBarState(control);
        host.appendChild(control);
        control.classList.toggle('mcms-control-fallback', !primaryMap);
        renderScreenPins();
        updateUI();
        return control;'''
if create_body.count(old_create_close) != 1:
    raise SystemExit(f'createControl closing anchor count changed: {create_body.count(old_create_close)}')
create_body = create_body.replace(old_create_close, new_create_close, 1)
text = text[:create_start] + create_body + text[create_end:]

text = replace_function(text, 'toggleCommandBar', r'''    function toggleCommandBar() {
        const control = document.getElementById(SCRIPT.controlId);
        const opening = state.commandBarOpen === false;
        runtimeClearTimeout(commandBarAnimationTimer);
        commandBarAnimationTimer = null;
        commandBarAnimating = false;
        for (const item of Array.from(control?.querySelectorAll?.('.mcms-float-btn, .mcms-screen-pin-btn') || [])) {
            item.style.removeProperty('opacity');
            item.style.removeProperty('transform');
            item.style.removeProperty('transition');
            item.style.removeProperty('transition-delay');
            item.style.removeProperty('will-change');
            delete item.dataset.mcmsCollapseDelay;
        }
        state.commandBarOpen = opening;
        saveState();
        updateUI();
        fitControlToMap();
        showToast(opening ? 'Command bar expanded' : 'Command bar collapsed');
    }''')

text = replace_function(text, 'ensureUi', r'''    function ensureUi() {
        operationalWindowEnsureSettingsStyle(document);
        const discoveredMap = getLargestLeafletMap();
        const mapEl = toolkitPrimaryMapElement(discoveredMap, document);
        const control = createControl(mapEl);
        if (settingsPanelActivated && !document.getElementById(SCRIPT.panelId)) createPanel();
        if (control) ensureVersionStatusButton();
        if (mapEl) {
            const map = findLeafletMapInstance(false);
            if (state.economyMode && map) { applyLeafletEconomyPolicy(map); scheduleEconomyLayerSync(0); }
            if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(0);
            else if (!state.majorIncidentFeed.enabled) removeMajorIncidentFeed();
            const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
            if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay, mapEl);
        }
        toolkitApplyCommandBarState(control);
        return Boolean(control || document.getElementById(SCRIPT.controlId));
    }''')

update_start, update_end = function_span(text, 'updateUI')
update_body = text[update_start:update_end]
nudge_anchor = "            control.style.setProperty('--mcms-nudge-y', `${state.nudge.y}px`);\n"
if update_body.count(nudge_anchor) != 1:
    raise SystemExit('updateUI nudge anchor changed')
update_body = update_body.replace(nudge_anchor, nudge_anchor + "            toolkitApplyCommandBarState(control);\n", 1)
old_dock = r'''            const dockToggleButton = control.querySelector('.mcms-dock-toggle-btn');
            if (dockToggleButton) {
                const open = state.commandBarOpen !== false;
                const label = open ? 'Collapse command bar' : 'Expand command bar';
                dockToggleButton.classList.toggle('mcms-open', open);
                dockToggleButton.setAttribute('aria-expanded', String(open));
                dockToggleButton.setAttribute('aria-label', label);
                dockToggleButton.title = label;
                const icon = dockToggleButton.querySelector('.mcms-dock-toggle-icon');
                if (icon) icon.textContent = open ? '▴' : '▾';
            }
'''
if update_body.count(old_dock) != 1:
    raise SystemExit(f'updateUI dock block count changed: {update_body.count(old_dock)}')
update_body = update_body.replace(old_dock, '', 1)
text = text[:update_start] + update_body + text[update_end:]

cache_anchor = "    let operationalRequirementsCatalogCache = null;\n"
cache_block = r'''    let operationalRequirementsCatalogCache = null;
    const OPERATIONAL_REQUIREMENTS_NATIVE_SELECTOR = '[id="missing_text"],[data-mission-requirements],[data-missing-requirements],[data-missing-vehicles],.mission-requirements,.mission_requirements,.missing-vehicles,.missing_vehicles';
    const OPERATIONAL_REQUIREMENTS_REMOTE_TTL_MS = 60000;
    const OPERATIONAL_REQUIREMENTS_REMOTE_ERROR_BACKOFF_MS = 5000;
    const operationalRequirementsRemoteCache = new Map();
'''
if text.count(cache_anchor) != 1:
    raise SystemExit('Operational requirements cache anchor changed')
text = text.replace(cache_anchor, cache_block, 1)

text = replace_function(text, 'operationalRequirementsMissionContainer', r'''    function operationalRequirementsMissionContainer(node, doc = node?.ownerDocument) {
        const selector = '#mission-form,.mission-window,.mission_window,.modal-content';
        const direct = node?.closest?.(selector);
        if (direct) return direct;
        const candidates = Array.from(doc?.querySelectorAll?.(selector) || []);
        return candidates.find(operationalRequirementsCandidateVisible) || candidates[0] || null;
    }''')

remote_helpers = r'''    function operationalRequirementsMissionKey(doc) {
        const values = [
            doc?.defaultView?.location?.pathname,
            doc?.defaultView?.location?.href,
            doc?.URL,
            doc?.baseURI,
            doc?.querySelector?.('#mission-form[action*="/missions/"],form[action*="/missions/"]')?.getAttribute?.('action')
        ];
        for (const value of values) {
            const match = String(value || '').match(/\/missions\/(\d+)(?:\/|[?#]|$)/u);
            if (match) return match[1];
        }
        const input = doc?.querySelector?.('#mission-form input[name="mission_id"],input[name="mission_id"]');
        const inputValue = String(input?.value ?? input?.getAttribute?.('value') ?? '').match(/\d+/u)?.[0];
        if (inputValue) return inputValue;
        const container = operationalRequirementsMissionContainer(null, doc);
        const dataValue = String(container?.getAttribute?.('data-mission-id') || '').match(/\d+/u)?.[0];
        return dataValue || '';
    }
    function operationalRequirementsRemoteAnchor(doc, nativeRoots = []) {
        const connected = nativeRoots.find(root => root?.isConnected !== false && root?.parentNode && operationalRequirementsCandidateVisible(root))
            || nativeRoots.find(root => root?.isConnected !== false && root?.parentNode);
        if (connected) return connected;
        const mission = operationalRequirementsMissionContainer(null, doc);
        return mission?.querySelector?.('#mission_general_info,.mission_general_info,#vehicle_show_table,.available-vehicles')
            || mission?.firstElementChild
            || mission
            || null;
    }
    function operationalRequirementsEnsureRemoteSource(doc, missionKey) {
        const key = String(missionKey || '');
        if (!key || runtime.destroyed) return null;
        const now = Date.now();
        const current = operationalRequirementsRemoteCache.get(key);
        if (current?.state === 'pending') return current;
        if (current?.state === 'ready' && now - Number(current.updatedAt || 0) < OPERATIONAL_REQUIREMENTS_REMOTE_TTL_MS) return current;
        if (current?.state === 'error' && now - Number(current.updatedAt || 0) < OPERATIONAL_REQUIREMENTS_REMOTE_ERROR_BACKOFF_MS) return current;
        const entry = { state: 'pending', missionKey: key, root: current?.root || null, fingerprint: current?.fingerprint || '', updatedAt: now };
        operationalRequirementsRemoteCache.set(key, entry);
        void (async () => {
            const Parser = doc?.defaultView?.DOMParser || pageWindow.DOMParser || globalThis.DOMParser;
            if (typeof Parser !== 'function') throw new Error('Mission requirement HTML parser is unavailable.');
            const url = new URL(`/missions/${encodeURIComponent(key)}`, doc?.baseURI || pageWindow.location.href);
            if (url.origin !== pageWindow.location.origin) throw new Error('Mission requirement recovery URL is not same-origin.');
            const requestModes = [
                { Accept: 'text/html,application/xhtml+xml' },
                { Accept: 'text/html,application/xhtml+xml', 'X-Requested-With': 'XMLHttpRequest' }
            ];
            let recovered = null;
            for (const headers of requestModes) {
                try {
                    const response = await runtimeFetch(url.href, {
                        method: 'GET',
                        credentials: 'same-origin',
                        cache: 'no-store',
                        headers
                    });
                    if (!response.ok) continue;
                    const html = await response.text();
                    if (!html || html.length < 40) continue;
                    const fetchedDoc = new Parser().parseFromString(html, 'text/html');
                    const source = operationalRequirementsResolveSource(fetchedDoc, { includeRemote: false });
                    if (source && (source.groupedCount > 0 || source.raw)) {
                        recovered = source;
                        break;
                    }
                } catch (error) {}
            }
            if (operationalRequirementsRemoteCache.get(key) !== entry) return;
            if (!recovered) {
                operationalRequirementsRemoteCache.set(key, { state: 'error', missionKey: key, root: null, fingerprint: '', updatedAt: Date.now() });
            } else {
                operationalRequirementsRemoteCache.set(key, {
                    state: 'ready',
                    missionKey: key,
                    root: recovered.root,
                    fingerprint: `remote:${key}:${recovered.fingerprint}`,
                    updatedAt: Date.now()
                });
            }
            scheduleOperationalSuiteScan(0);
        })().catch(() => {
            if (operationalRequirementsRemoteCache.get(key) === entry) {
                operationalRequirementsRemoteCache.set(key, { state: 'error', missionKey: key, root: null, fingerprint: '', updatedAt: Date.now() });
                scheduleOperationalSuiteScan(0);
            }
        });
        return entry;
    }
    function operationalRequirementsRemoteCandidate(doc, nativeRoots, index) {
        const missionKey = operationalRequirementsMissionKey(doc);
        if (!missionKey) return null;
        const cached = operationalRequirementsRemoteCache.get(missionKey);
        if (cached?.state === 'ready' && cached.root) {
            if (Date.now() - Number(cached.updatedAt || 0) >= OPERATIONAL_REQUIREMENTS_REMOTE_TTL_MS) {
                operationalRequirementsEnsureRemoteSource(doc, missionKey);
            }
            const anchor = operationalRequirementsRemoteAnchor(doc, nativeRoots);
            if (!anchor) return null;
            const record = operationalRequirementsCandidateRecord(cached.root, anchor, 'remote', index, {
                missionKey,
                missionContainer: operationalRequirementsMissionContainer(anchor, doc)
            });
            if (!record) return null;
            record.score += 1400;
            record.fingerprint = cached.fingerprint || `remote:${missionKey}:${record.fingerprint}`;
            record.remote = true;
            return record;
        }
        operationalRequirementsEnsureRemoteSource(doc, missionKey);
        return null;
    }
'''
insert_anchor = "    function operationalRequirementsCandidateRecord("
insert_at = text.find(insert_anchor)
if insert_at < 0:
    raise SystemExit('Operational candidate record insertion anchor missing')
text = text[:insert_at] + remote_helpers + text[insert_at:]

text = replace_function(text, 'operationalRequirementsCandidateRecord', r'''    function operationalRequirementsCandidateRecord(root, anchor, kind, index, options = {}) {
        if (!root || !anchor || root.closest?.('[data-mcms-operational-suite="requirements"]')) return null;
        const grouped = Array.from(root.querySelectorAll?.('[data-requirement-type]') || []);
        const raw = operationalRequirementNormaliseText(root.textContent || '');
        const missionContainer = options.missionContainer || operationalRequirementsMissionContainer(anchor);
        const missionVisible = operationalRequirementsCandidateVisible(missionContainer);
        const visible = operationalRequirementsCandidateVisible(anchor);
        const score = grouped.length * 300 + (raw ? 100 : 0) + (missionVisible ? 400 : 0)
            + (visible ? 60 : 0) + (anchor.id === 'missing_text' ? 20 : 0)
            + (kind === 'lssm-raw' ? 10 : 0) + (kind === 'remote' ? 400 : 0);
        return {
            root, anchor, kind, index, groupedCount: grouped.length, raw, visible, missionContainer, score,
            missionKey: options.missionKey || operationalRequirementsMissionKey(anchor.ownerDocument),
            fingerprint: `${kind}:${index}:${grouped.length}:${raw}`
        };
    }''')

text = replace_function(text, 'operationalRequirementsSourceCandidates', r'''    function operationalRequirementsSourceCandidates(doc, options = {}) {
        if (!doc?.querySelectorAll) return [];
        const candidates = [];
        const seenRoots = new Set();
        const nativeRoots = Array.from(doc.querySelectorAll(OPERATIONAL_REQUIREMENTS_NATIVE_SELECTOR) || []);
        const add = (root, anchor = root, kind = 'native', extra = {}) => {
            if (!root || !anchor || seenRoots.has(root)) return;
            const record = operationalRequirementsCandidateRecord(root, anchor, kind, candidates.length, extra);
            if (!record) return;
            seenRoots.add(root);
            candidates.push(record);
        };
        nativeRoots.forEach(root => add(root, root, 'native'));
        for (const group of Array.from(doc.querySelectorAll('[data-requirement-type]') || [])) {
            const root = group.closest?.(`${OPERATIONAL_REQUIREMENTS_NATIVE_SELECTOR},.alert-missing-vehicles`) || group.parentElement;
            add(root, root, 'grouped');
        }
        for (const carrier of Array.from(doc.querySelectorAll('[data-raw-html]') || [])) {
            if (carrier.closest?.('[data-mcms-operational-suite="requirements"]')) continue;
            const rawHtml = String(carrier.getAttribute?.('data-raw-html') || '').trim();
            if (!rawHtml || !/data-requirement-type\s*=/iu.test(rawHtml)) continue;
            const equivalentLssm = carrier.matches?.('.alert-missing-vehicles');
            if (equivalentLssm && operationalRequirementsCandidateVisible(carrier)) {
                candidates.push({
                    root: carrier, anchor: carrier, kind: 'lssm-live', index: candidates.length,
                    groupedCount: 0, raw: rawHtml, visible: true,
                    missionContainer: operationalRequirementsMissionContainer(carrier), score: Number.POSITIVE_INFINITY,
                    missionKey: operationalRequirementsMissionKey(doc),
                    fingerprint: `lssm-live:${rawHtml}`, suppressesToolkit: true
                });
                continue;
            }
            const root = operationalRequirementsRawHtmlRoot(doc, carrier);
            const preferredAnchor = operationalRequirementsRemoteAnchor(doc, nativeRoots) || carrier;
            add(root, preferredAnchor, equivalentLssm ? 'lssm-raw' : 'raw-html');
        }
        const localEvidence = candidates.some(candidate => candidate.suppressesToolkit === true || candidate.groupedCount > 0 || candidate.raw);
        if (options.includeRemote !== false && !localEvidence) {
            const remote = operationalRequirementsRemoteCandidate(doc, nativeRoots, candidates.length);
            if (remote) candidates.push(remote);
        }
        return candidates;
    }''')

text = replace_function(text, 'operationalRequirementsResolveSource', r'''    function operationalRequirementsResolveSource(doc, options = {}) {
        const candidates = operationalRequirementsSourceCandidates(doc, options);
        const activeLssm = candidates.find(candidate => candidate.suppressesToolkit === true);
        if (activeLssm) return { ...activeLssm, suppressed: true, candidates };
        const evidenced = candidates.filter(candidate => candidate.groupedCount > 0 || candidate.raw);
        const pool = evidenced.length ? evidenced : candidates;
        const selected = pool.slice().sort((left, right) => right.score - left.score || right.index - left.index)[0] || null;
        return selected ? { ...selected, suppressed: false, candidates } : null;
    }''')

text = replace_function(text, 'operationalRequirementsRenderContext', r'''    function operationalRequirementsRenderContext(context) {
        if (!context?.doc || runtime.destroyed) return;
        if (!operationalRequirementsActive()) {
            context.panel?.remove?.();
            context.panel = null;
            return;
        }
        const missionKey = operationalRequirementsMissionKey(context.doc);
        if (context.requirementMissionKey !== missionKey) {
            context.requirementMissionKey = missionKey;
            context.fingerprint = '';
            context.boundRequirementRoot = null;
            context.boundRequirementSource = '';
            context.boundRequirementMissionKey = '';
        }
        const requirementSource = operationalRequirementsResolveSource(context.doc);
        const requirementRoot = requirementSource?.root;
        if (!requirementRoot || requirementSource?.suppressed === true) {
            context.panel?.remove?.();
            context.panel = null;
            context.fingerprint = '';
            return;
        }
        const settings = state.operationalWindow?.requirements || {};
        const input = operationalRequirementsInput(context, requirementRoot);
        const model = operationalRequirementCreateModel(input);
        const rows = operationalRequirementRows(model, { calcMaxStaff: settings.calcMaxStaff === true });
        const fingerprint = JSON.stringify({
            mission: missionKey,
            model: operationalRequirementFingerprint(model, { calcMaxStaff: settings.calcMaxStaff === true }),
            sourceState: input.source,
            sort: settings.sort,
            sortDir: settings.sortDir,
            viewMode: settings.viewMode,
            minified: context.minified === true,
            sourceFingerprint: requirementSource.fingerprint
        });
        if (fingerprint === context.fingerprint && context.panel?.isConnected) return;
        const panel = operationalRequirementsMount(context, requirementSource.anchor || requirementRoot);
        const rendered = operationalRequirementsPanelHtml(rows, model, settings, context.minified === true, input.source);
        panel.dataset.covered = rendered.allCovered ? 'true' : 'false';
        panel.dataset.requirementState = rendered.state;
        panel.dataset.minified = context.minified === true ? 'true' : 'false';
        panel.dataset.missionKey = missionKey;
        operationalReplaceContent(panel, rendered.html);
        context.fingerprint = fingerprint;
    }''')

text = replace_function(text, 'operationalRequirementsBindContext', r'''    function operationalRequirementsBindContext(context) {
        const doc = context?.doc;
        if (!doc?.querySelector || !operationalRequirementsActive()) return;
        const missionKey = operationalRequirementsMissionKey(doc);
        const requirementSource = operationalRequirementsResolveSource(doc);
        const requirementRoot = requirementSource?.root || null;
        const candidateAnchors = requirementSource?.candidates?.map(candidate => candidate.anchor) || [];
        const missionHost = requirementSource?.missionContainer
            || operationalRequirementsMissionContainer(requirementSource?.anchor, doc);
        const roots = Array.from(new Set([
            ...candidateAnchors,
            missionHost,
            doc.querySelector('#mission_vehicle_driving'),
            doc.querySelector('#vehicle_show_table_body_all'),
            doc.querySelector('#occupied'),
            ...operationalFeatureObservationRoots(doc)
        ].filter(root => root && root.isConnected !== false)));
        if (!roots.length) return;
        const sourceFingerprint = requirementSource?.fingerprint || '';
        if (context.boundRequirementRoot === requirementSource?.anchor
            && context.boundRequirementSource === sourceFingerprint
            && context.boundRequirementMissionKey === missionKey
            && context.observer
            && context.observedRootCount === roots.length) return;
        try { context.observer?.disconnect?.(); } catch (error) {}
        context.boundRequirementRoot = requirementSource?.anchor || null;
        context.boundRequirementSource = sourceFingerprint;
        context.boundRequirementMissionKey = missionKey;
        context.observedRootCount = roots.length;
        const OperationalMutationObserver = doc.defaultView?.MutationObserver || pageWindow.MutationObserver;
        context.observer = new OperationalMutationObserver(() => operationalRequirementsScheduleContext(context, 25));
        for (const root of roots) {
            context.observer.observe(root, {
                childList: true,
                subtree: true,
                characterData: true,
                attributes: true,
                attributeFilter: ['checked', 'vehicle_type_id', 'data-vehicle-type-id', 'data-equipment-types', 'data-equipment-type', 'tractive_vehicle_id', 'tractive_random', 'sortvalue', 'value', 'data-raw-html', 'data-mission-id']
            });
        }
        if (!context.changeHandler) {
            context.changeHandler = event => {
                if (event.target?.matches?.('.vehicle_checkbox, #vehicle_show_table_body_all input, #occupied input')) {
                    operationalRequirementsScheduleContext(context, 0);
                }
            };
            doc.addEventListener('change', context.changeHandler, true);
        }
    }''')

cleanup_anchor = '''            clearOperationalSuiteContexts();
            if (runtime.operationalSuite?.phase === 'operational-suite') delete runtime.operationalSuite;'''
cleanup_replacement = '''            clearOperationalSuiteContexts();
            operationalRequirementsRemoteCache.clear();
            if (runtime.operationalSuite?.phase === 'operational-suite') delete runtime.operationalSuite;'''
if text.count(cleanup_anchor) != 1:
    raise SystemExit(f'Operational cleanup anchor count changed: {text.count(cleanup_anchor)}')
text = text.replace(cleanup_anchor, cleanup_replacement, 1)

TEST.write_text(r'''#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const required = [
  "function toolkitPrimaryMapElement(",
  "candidate.closest?.(missionSelector)",
  "control.setAttribute('data-mcms-command-bar-open', String(open))",
  '#${SCRIPT.controlId}[data-mcms-command-bar-open="false"] .mcms-floating-filter',
  'state.commandBarOpen = opening;',
  'function operationalRequirementsMissionKey(',
  'function operationalRequirementsEnsureRemoteSource(',
  "credentials: 'same-origin'",
  "new URL(`/missions/${encodeURIComponent(key)}`",
  "doc.querySelectorAll('[data-raw-html]')",
  'context.boundRequirementMissionKey === missionKey',
  'panel.dataset.missionKey = missionKey'
];
for (const token of required) if (!source.includes(token)) throw new Error(`Missing Issue #470 contract token: ${token}`);
const toggleStart = source.indexOf('    function toggleCommandBar()');
const toggleEnd = source.indexOf('    function handleMapVisibilityToggle(', toggleStart);
const toggle = source.slice(toggleStart, toggleEnd);
if (!(toggle.indexOf('state.commandBarOpen = opening;') < toggle.indexOf('saveState();') && toggle.indexOf('saveState();') < toggle.indexOf('updateUI();'))) throw new Error('Command-bar state is not committed before UI reconciliation');
if (/commandBarAnimationTimer\s*=\s*runtimeSetTimeout/u.test(toggle)) throw new Error('Command-bar collapse still depends on a delayed state commit');
const resolverStart = source.indexOf('    function operationalRequirementsCandidateVisible(');
const resolverEnd = source.indexOf('    function operationalRequirementsRuntimeCatalog(', resolverStart);
if (resolverStart < 0 || resolverEnd <= resolverStart) throw new Error('Requirements resolver block is missing');
class Node {
  constructor({id='', text='', visible=true, cls='', attrs={}, mission=null, toolkit=false}={}) {
    Object.assign(this,{id,textContent:text,visible,className:cls,attrs,mission,toolkit,groups:[],isConnected:true,hidden:false,parentNode:{},parentElement:null,ownerDocument:null,firstElementChild:null});
  }
  getAttribute(name){ return this.attrs[name] ?? null; }
  setAttribute(name,value){ this.attrs[name]=String(value); }
  matches(selector){ return selector === '.alert-missing-vehicles' && this.className.includes('alert-missing-vehicles'); }
  getBoundingClientRect(){ return {width:this.visible?300:0,height:this.visible?60:0}; }
  getClientRects(){ return this.visible?[1]:[]; }
  querySelectorAll(selector){ return selector==='[data-requirement-type]'?this.groups:[]; }
  querySelector(selector){ return selector==='[data-requirement-type]'?(this.groups[0]||null):null; }
  closest(selector){
    if(selector==='[data-mcms-operational-suite="requirements"]') return this.toolkit?this:null;
    if(selector.includes('#mission-form')||selector.includes('.mission-window')) return this.mission;
    if(selector.includes('[id="missing_text"]')&&this.id==='missing_text') return this;
    if(selector.includes('.alert-missing-vehicles')&&this.className.includes('alert-missing-vehicles')) return this;
    return null;
  }
}
const mission = new Node({id:'mission-form',visible:true});
mission.querySelector = () => null;
const empty = new Node({id:'missing_text',visible:true,mission});
const remote = new Node({id:'missing_text',visible:false,text:'Needed 3 Fire Engines'});
const remoteGroup = new Node({text:'Needed 3 Fire Engines',attrs:{'data-requirement-type':'vehicles'}});
remoteGroup.querySelector = selector => selector==='b'?new Node({text:'Needed'}):null;
remote.groups=[remoteGroup];
function makeDoc(pathname='/missions/42') {
  const value={
    native:[empty],carriers:[],groups:[],missionRoot:mission,
    baseURI:`https://www.missionchief.co.uk${pathname}`,
    URL:`https://www.missionchief.co.uk${pathname}`,
    defaultView:{location:{pathname,href:`https://www.missionchief.co.uk${pathname}`},getComputedStyle(node){return{display:node.visible?'block':'none',visibility:'visible'};}},
    querySelectorAll(selector){
      if(selector.includes('[id="missing_text"]')) return this.native;
      if(selector==='[data-requirement-type]') return this.groups;
      if(selector==='[data-raw-html]') return this.carriers;
      if(selector.includes('#mission-form')||selector.includes('.mission-window')) return [this.missionRoot];
      return [];
    },
    querySelector(selector){
      if(selector.includes('#mission-form[action')) return null;
      if(selector.includes('#mission-form')||selector.includes('.mission-window')) return this.missionRoot;
      if(selector.includes('input[name="mission_id"]')) return null;
      return null;
    },
    createRange(){ return {createContextualFragment(){return null;}}; }
  };
  [empty,mission,...value.native,...value.carriers,...value.groups].forEach(node=>{if(node)node.ownerDocument=value;});
  return value;
}
const sandbox={
  console,
  runtime:{destroyed:false},
  runtimeFetch(){return Promise.reject(new Error('not expected'));},
  scheduleOperationalSuiteScan(){},
  pageWindow:{location:{origin:'https://www.missionchief.co.uk',href:'https://www.missionchief.co.uk/'},DOMParser:function(){}},
  operationalRequirementNormaliseText:value=>String(value||'').replace(/\s+/gu,' ').trim(),
  URL, encodeURIComponent, Date, Map, Set, Array, Object, String, Number, RegExp, Promise, globalThis:null
};
sandbox.globalThis=sandbox;
vm.createContext(sandbox);
vm.runInContext(`${source.slice(resolverStart,resolverEnd)}
globalThis.resolveSource=operationalRequirementsResolveSource;
globalThis.remoteCache=operationalRequirementsRemoteCache;
globalThis.missionKey=operationalRequirementsMissionKey;`, sandbox);
const doc42=makeDoc('/missions/42');
remote.ownerDocument={defaultView:null};
remoteGroup.ownerDocument=remote.ownerDocument;
sandbox.remoteCache.set('42',{state:'ready',missionKey:'42',root:remote,fingerprint:'remote:42:test',updatedAt:Date.now()});
const selected=sandbox.resolveSource(doc42);
if(selected?.kind!=='remote'||selected.root!==remote||selected.anchor!==empty||selected.missionKey!=='42') throw new Error('Mission-scoped remote requirement evidence was not selected');
if(sandbox.missionKey(makeDoc('/missions/43'))!=='43') throw new Error('Mission identity extraction failed');
if(!source.includes('// @version      5.0.7')||!source.includes("version: '5.0.7'")) throw new Error('v5.0.7 version metadata is incomplete');
console.log('Issue #470 menu-state and requirement-source runtime passed.');
''', encoding='utf-8')

validator = VALIDATOR.read_text(encoding='utf-8')
constant_anchor = 'ISSUE464_OPERATIONAL_RUNTIME = ROOT / ".github" / "scripts" / "test_issue464_operational_runtime.js"\n'
constant_add = constant_anchor + 'ISSUE470_MENU_REQUIREMENTS_RUNTIME = ROOT / ".github" / "scripts" / "test_issue470_menu_requirements_runtime.js"\n'
if constant_anchor not in validator:
    raise SystemExit('Validator Issue #464 constant anchor missing')
validator = validator.replace(constant_anchor, constant_add, 1)
required_anchor = 'ISSUE458_REQUIREMENTS_SOURCE_RUNTIME, ISSUE464_LAUNCHER_SETTINGS_CONTRACT, ISSUE464_OPERATIONAL_RUNTIME]'
if required_anchor not in validator:
    raise SystemExit('Validator required-list anchor missing')
validator = validator.replace(required_anchor, 'ISSUE458_REQUIREMENTS_SOURCE_RUNTIME, ISSUE464_LAUNCHER_SETTINGS_CONTRACT, ISSUE464_OPERATIONAL_RUNTIME, ISSUE470_MENU_REQUIREMENTS_RUNTIME]', 1)
run_anchor = '''        if issue464_operational_runtime.returncode != 0:
            fail("Issue #464 operational runtime fixtures failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))'''
run_add = '''        if issue464_operational_runtime.returncode != 0:
            fail("Issue #464 operational runtime fixtures failed")

        issue470_menu_requirements = subprocess.run(
            ["node", str(ISSUE470_MENU_REQUIREMENTS_RUNTIME)], cwd=ROOT,
        )
        if issue470_menu_requirements.returncode != 0:
            fail("Issue #470 menu/requirements runtime fixtures failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))'''
if run_anchor not in validator:
    raise SystemExit('Validator Issue #464 runtime anchor missing')
validator = validator.replace(run_anchor, run_add, 1)
VALIDATOR.write_text(validator, encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
entry = '''## [5.0.7] - 2026-07-23

### Critical mission-window recovery

- Preserved the user's command-bar open or closed choice before any UI reconciliation, preventing mission-window creation or launcher reparenting from reopening collapsed buttons.
- Anchored the Toolkit launcher to the primary top-document map or body and rejected mission-window, modal and foreign-document map containers.
- Added a control-local command-bar state contract so Desktop, Tablet/iPad and iOS layouts remain collapsed even during MissionChief DOM replacement.
- Broadened native and LSSM requirement-source discovery and recovered grouped requirement markup from any compatible `data-raw-html` carrier.
- Added mission-scoped same-origin `/missions/<id>` HTML recovery when the live `#missing_text` placeholder is empty, with caching, backoff and source rebinding when missions change.
- Kept empty or unavailable data amber, retained visible LSSM coexistence suppression and continued to require positive parsed evidence before displaying green coverage.

'''
if '## [5.0.7]' in changelog:
    raise SystemExit('v5.0.7 changelog already exists')
insert_at = changelog.find('## [')
if insert_at < 0:
    raise SystemExit('Changelog release anchor missing')
CHANGELOG.write_text(changelog[:insert_at] + entry + changelog[insert_at:], encoding='utf-8')

SOURCE.write_text(text, encoding='utf-8')
for target in [
    ROOT / 'MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'MissionChief_Map_Command_Toolkit.txt',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt',
]:
    target.write_text(text, encoding='utf-8')

source_bytes = text.encode('utf-8')
source_sha = hashlib.sha256(source_bytes).hexdigest()
SUMS.write_text(
    f'{source_sha}  MissionChief_Map_Command_Toolkit.user.js\n'
    f'{source_sha}  MissionChief_Map_Command_Toolkit.txt\n',
    encoding='utf-8'
)
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
manifest['version'] = '5.0.7'
manifest['sha256'] = source_sha
manifest['bytes'] = len(source_bytes)
manifest['lines'] = len(text.splitlines())
manifest.setdefault('metadata', {})['runtimeVersion'] = '5.0.7'
manifest['distributionStatus'] = 'dry-run-not-yet-greasyfork-source'
MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
old_expected = int(fixture['expectedSourceLines'])
source_lines = len(text.splitlines())
delta = source_lines - old_expected
changes = [item for item in fixture.get('approvedNonStyleChanges', []) if item.get('issue') != 470]
changes.append({'issue': 470, 'phase': 'persistent-command-state-and-mission-scoped-requirement-recovery', 'lines': delta})
fixture['approvedNonStyleChanges'] = changes
fixture['approvedNonStyleSourceLines'] = sum(int(item['lines']) for item in changes)
fixture['expectedSourceLines'] = source_lines
fixture['candidateVersion'] = '5.0.7'
fixture['candidateSourceSha256'] = source_sha
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

for path in (ROOT / '.github/diagnostics').glob('issue470-*'):
    path.unlink(missing_ok=True)
for path in (ROOT / '.github/development-packages').glob('issue470-*'):
    if path.resolve() != SELF.resolve():
        path.unlink(missing_ok=True)

SELF.unlink(missing_ok=True)
print(json.dumps({
    'version': '5.0.7',
    'sha256': source_sha,
    'sourceLines': source_lines,
    'lineDelta': delta,
    'remoteRecovery': True,
    'commandStateImmediate': True,
}, indent=2))
