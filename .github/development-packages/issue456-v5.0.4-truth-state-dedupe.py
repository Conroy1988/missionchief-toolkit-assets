#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
COPIES = (
    SOURCE,
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
)
CHANGELOG = ROOT / "CHANGELOG.md"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
TEST = ROOT / ".github" / "scripts" / "test_issue456_requirements_truth_runtime.js"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
DIAGNOSTICS = (
    ROOT / ".github" / "diagnostics" / "issue456-operational-requirements-block.txt",
    ROOT / ".github" / "diagnostics" / "issue456-context-registry.txt",
    ROOT / ".github" / "diagnostics" / "issue456-context-core.txt",
)


def replace_exact(text: str, old: str, new: str, label: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{label}: expected {count}, found {actual}")
    return text.replace(old, new, count)


def replace_function(text: str, name: str, next_name: str, replacement: str) -> str:
    start = text.index(f"    function {name}(")
    end = text.index(f"    function {next_name}(", start)
    return text[:start] + replacement.rstrip() + "\n\n" + text[end:]


source = SOURCE.read_text(encoding="utf-8")
old_line_count = len(source.splitlines())
source = replace_exact(source, "// @version      5.0.3", "// @version      5.0.4", "metadata version")
source = replace_exact(source, "version: '5.0.3',", "version: '5.0.4',", "runtime version")

covered_style = '            .${OPERATIONAL_REQUIREMENTS_PANEL_CLASS}[data-covered="true"]{border-color:rgba(40,167,69,.78);background:linear-gradient(180deg,rgba(20,82,39,.97),rgba(9,42,21,.97))}'
source = replace_exact(
    source,
    covered_style,
    covered_style + '\n            .${OPERATIONAL_REQUIREMENTS_PANEL_CLASS}[data-requirement-state="pending"],.${OPERATIONAL_REQUIREMENTS_PANEL_CLASS}[data-requirement-state="unparsed"]{border-color:rgba(255,193,7,.78);background:linear-gradient(180deg,rgba(92,70,12,.97),rgba(48,36,6,.97))}',
    "requirements pending-state style",
)

source_state_and_input = r'''    function operationalRequirementsSourceState(requirementRoot, texts, progress) {
        const raw = operationalRequirementNormaliseText(requirementRoot?.textContent || '');
        const groupedEvidence = OPERATIONAL_REQUIREMENT_GROUPS.some(group =>
            Boolean(operationalRequirementNormaliseText(texts?.[group]?.raw || ''))
        );
        const progressEvidence = Object.keys(progress || {}).length > 0;
        return {
            state: groupedEvidence || progressEvidence ? 'available' : raw ? 'unparsed' : 'pending',
            raw,
            evidenceCount: Number(groupedEvidence) + Object.keys(progress || {}).length
        };
    }

    function operationalRequirementsInput(context, requirementRoot) {
        const doc = context.doc;
        const texts = operationalRequirementsTexts(requirementRoot);
        const progress = operationalRequirementsProgress(requirementRoot);
        return {
            texts,
            catalog: operationalRequirementsRuntimeCatalog(),
            vehicleTypes: operationalRequirementsVehicleTypes(),
            driving: operationalRequirementsDrivingSnapshot(doc),
            selected: operationalRequirementsSelectedSnapshot(doc),
            progress,
            missionAdditional: {},
            source: operationalRequirementsSourceState(requirementRoot, texts, progress)
        };
    }'''
source = replace_function(source, "operationalRequirementsInput", "operationalRequirementsEscapeHtml", source_state_and_input)

panel_function = r'''    function operationalRequirementsPanelHtml(rows, model, settings, minified, source = null) {
        const sorted = operationalRequirementsSortRows(rows, settings);
        const open = sorted.filter(row => !row.covered);
        const unresolved = OPERATIONAL_REQUIREMENT_GROUPS
            .map(group => model?.requirementTexts?.[group]?.remaining)
            .filter(Boolean);
        const sourceState = String(source?.state || 'pending');
        const hasParsedRows = sorted.length > 0;
        const unknown = !hasParsedRows && unresolved.length === 0;
        const allCovered = sourceState === 'available' && hasParsedRows && open.length === 0 && unresolved.length === 0;
        const bodyRows = sorted.map(row => {
            const stillNeeded = Math.max(0, Number(row.remainingOnMission) - Number(row.selectedValue));
            return `<tr class="mcms-operational-suite-row" data-covered="${row.covered ? 'true' : 'false'}"><td data-label="Requirement">${operationalRequirementsEscapeHtml(row.requirement || row.key)}</td><td data-label="Required">${Math.max(0, Number(row.missing) || 0).toLocaleString('en-GB')}</td><td data-label="Responding">${Math.max(0, Number(row.driving) || 0).toLocaleString('en-GB')}</td><td data-label="Selected">${operationalRequirementsEscapeHtml(operationalRequirementsSelectedText(row, settings?.calcMaxStaff === true))}</td><td class="mcms-operational-suite-needed" data-label="Still needed">${stillNeeded.toLocaleString('en-GB')}</td></tr>`;
        }).join('');
        const unresolvedHtml = unresolved.length
            ? `<div class="mcms-operational-suite-unresolved"><strong>Unresolved MissionChief requirement</strong><br>${unresolved.map(operationalRequirementsEscapeHtml).join('<br>')}</div>`
            : '';
        const unknownMessage = sourceState === 'pending'
            ? 'Waiting for MissionChief requirement data.'
            : 'MissionChief requirement data could not be interpreted safely.';
        const emptyHtml = unknown
            ? `<div class="mcms-operational-suite-unresolved"><strong>Requirement status not confirmed</strong><br>${unknownMessage}</div>`
            : '';
        const summary = allCovered
            ? 'All displayed requirements covered'
            : unknown
                ? (sourceState === 'pending' ? 'Waiting for requirement data' : 'Requirement status unresolved')
                : `${open.length} requirement${open.length === 1 ? '' : 's'} still open${unresolved.length ? ` · ${unresolved.length} unresolved` : ''}`;
        return {
            allCovered,
            state: allCovered ? 'covered' : unknown ? sourceState : 'open',
            html: `<div class="mcms-operational-suite-header"><div class="mcms-operational-suite-title">Operational Requirements</div><div class="mcms-operational-suite-summary">${summary}</div><button type="button" class="mcms-operational-suite-toggle" aria-expanded="${minified ? 'false' : 'true'}" aria-label="${minified ? 'Expand' : 'Collapse'} operational requirements">${minified ? '＋' : '−'}</button></div><div class="mcms-operational-suite-body"><table class="mcms-operational-suite-table"><thead><tr><th>Requirement</th><th>Required</th><th>Responding</th><th>Selected</th><th>Still needed</th></tr></thead><tbody>${bodyRows}</tbody></table>${unresolvedHtml}${emptyHtml}</div>`
        };
    }'''
source = replace_function(source, "operationalRequirementsPanelHtml", "operationalRequirementsMount", panel_function)

mount_function = r'''    function operationalRequirementsMount(context, requirementRoot) {
        const doc = context.doc;
        operationalRequirementsEnsureStyle(doc);
        const selector = '[data-mcms-operational-suite="requirements"]';
        const mounted = Array.from(doc.querySelectorAll?.(selector) || []).filter(candidate => candidate?.isConnected);
        let panel = context.panel;
        if (!panel?.isConnected) panel = mounted[0] || null;
        for (const duplicate of mounted) {
            if (duplicate !== panel) duplicate.remove?.();
        }
        if (!panel?.isConnected) {
            panel = doc.createElement('section');
            panel.className = OPERATIONAL_REQUIREMENTS_PANEL_CLASS;
            panel.setAttribute('data-mcms-operational-suite', 'requirements');
            panel.setAttribute('aria-live', 'polite');
        }
        if (requirementRoot.parentNode && (panel.parentNode !== requirementRoot.parentNode || panel.nextSibling !== requirementRoot)) {
            requirementRoot.parentNode.insertBefore(panel, requirementRoot);
        }
        context.panel = panel;
        panel.onclick = event => {
            const button = event.target?.closest?.('.mcms-operational-suite-toggle');
            if (!button) return;
            context.minified = !context.minified;
            context.fingerprint = '';
            operationalRequirementsScheduleContext(context, 0);
        };
        return panel;
    }'''
source = replace_function(source, "operationalRequirementsMount", "operationalRequirementsRenderContext", mount_function)

render_function = r'''    function operationalRequirementsRenderContext(context) {
        if (!context?.doc || runtime.destroyed) return;
        if (!operationalRequirementsActive()) {
            context.panel?.remove?.();
            context.panel = null;
            return;
        }
        const requirementRoot = context.doc.querySelector?.('#missing_text');
        if (!requirementRoot?.isConnected || operationalRequirementsEquivalentLssmActive(context.doc)) {
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
            model: operationalRequirementFingerprint(model, { calcMaxStaff: settings.calcMaxStaff === true }),
            source: input.source,
            sort: settings.sort,
            sortDir: settings.sortDir,
            viewMode: settings.viewMode,
            minified: context.minified === true
        });
        if (fingerprint === context.fingerprint && context.panel?.isConnected) return;
        const panel = operationalRequirementsMount(context, requirementRoot);
        const rendered = operationalRequirementsPanelHtml(rows, model, settings, context.minified === true, input.source);
        panel.dataset.covered = rendered.allCovered ? 'true' : 'false';
        panel.dataset.requirementState = rendered.state;
        panel.dataset.minified = context.minified === true ? 'true' : 'false';
        operationalReplaceContent(panel, rendered.html);
        context.fingerprint = fingerprint;
    }'''
source = replace_function(source, "operationalRequirementsRenderContext", "operationalRequirementsScheduleContext", render_function)

new_line_count = len(source.splitlines())
line_delta = new_line_count - old_line_count
if line_delta < 0:
    raise RuntimeError(f"unexpected negative source-line delta: {line_delta}")

for path in COPIES:
    path.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
notes = '''
## [5.0.4] - 2026-07-23

### Critical requirements truth-state recovery
+- Stopped empty, delayed or failed MissionChief requirement parsing from being presented as confirmed green coverage.
+- Added explicit waiting and unresolved states; green coverage now requires positively parsed requirement rows that are all covered.
+- Enforced one Operational Requirements panel per document, reusing the authoritative mounted surface and removing stale duplicates.
+- Added behavioural regression coverage for pending input, unparsed input, covered rows, open rows, unresolved text and repeated duplicate mounts.
+
'''
if "## [5.0.4] - 2026-07-23" not in changelog:
    changelog = replace_exact(changelog, "## [Unreleased]\n", "## [Unreleased]\n" + notes, "changelog anchor")
CHANGELOG.write_text(changelog, encoding="utf-8")

TEST.write_text(r'''#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
function extract(name, nextName) {
    const start = source.indexOf(`    function ${name}(`);
    const end = source.indexOf(`    function ${nextName}(`, start);
    if (start < 0 || end <= start) throw new Error(`Unable to extract ${name}`);
    return source.slice(start, end);
}
const sandbox = {
    console,
    OPERATIONAL_REQUIREMENT_GROUPS: ['vehicles', 'staff', 'other'],
    OPERATIONAL_REQUIREMENTS_PANEL_CLASS: 'mcms-operational-suite-panel',
    operationalRequirementsSortRows: rows => rows.slice(),
    operationalRequirementsEscapeHtml: value => String(value ?? ''),
    operationalRequirementsSelectedText: row => String(row?.selectedValue ?? 0),
    operationalRequirementsEnsureStyle: () => undefined,
    operationalRequirementsScheduleContext: () => undefined,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(`${extract('operationalRequirementsPanelHtml', 'operationalRequirementsMount')}\n${extract('operationalRequirementsMount', 'operationalRequirementsRenderContext')}\nglobalThis.panelHtml = operationalRequirementsPanelHtml; globalThis.mount = operationalRequirementsMount;`, sandbox);
const emptyModel = { requirementTexts: { vehicles: { remaining: '' }, staff: { remaining: '' }, other: { remaining: '' } } };
const pending = sandbox.panelHtml([], emptyModel, {}, false, { state: 'pending' });
if (pending.allCovered || pending.state !== 'pending' || /All displayed requirements covered/.test(pending.html)) throw new Error('pending empty source was falsely covered');
if (!/Waiting for MissionChief requirement data/.test(pending.html)) throw new Error('pending source warning missing');
const unparsed = sandbox.panelHtml([], emptyModel, {}, false, { state: 'unparsed' });
if (unparsed.allCovered || unparsed.state !== 'unparsed' || !/could not be interpreted safely/.test(unparsed.html)) throw new Error('unparsed source was not fail-safe');
const coveredRow = { key: 'fire-engine', requirement: 'Fire Engine', covered: true, remainingOnMission: 0, selectedValue: 0, missing: 1, driving: 1, selected: 0 };
const covered = sandbox.panelHtml([coveredRow], emptyModel, {}, false, { state: 'available' });
if (!covered.allCovered || covered.state !== 'covered') throw new Error('positively parsed covered row did not resolve green');
const openRow = { ...coveredRow, covered: false, remainingOnMission: 1, driving: 0 };
const open = sandbox.panelHtml([openRow], emptyModel, {}, false, { state: 'available' });
if (open.allCovered || open.state !== 'open' || !/1 requirement still open/.test(open.html)) throw new Error('open requirement was falsely covered');
const unresolvedModel = { requirementTexts: { vehicles: { remaining: '1 Unknown Vehicle' }, staff: { remaining: '' }, other: { remaining: '' } } };
const unresolved = sandbox.panelHtml([], unresolvedModel, {}, false, { state: 'available' });
if (unresolved.allCovered || unresolved.state !== 'open' || !/Unresolved MissionChief requirement/.test(unresolved.html)) throw new Error('unresolved text was falsely covered');
function fakePanel(doc) {
    return {
        isConnected: true, dataset: {}, attributes: {}, className: '', parentNode: null, nextSibling: null, ownerDocument: doc,
        setAttribute(name, value) { this.attributes[name] = String(value); },
        remove() { this.isConnected = false; },
    };
}
const doc = {
    panels: [],
    querySelectorAll(selector) { return selector === '[data-mcms-operational-suite="requirements"]' ? this.panels.filter(panel => panel.isConnected) : []; },
    createElement() { const panel = fakePanel(this); this.panels.push(panel); return panel; },
};
const parent = { insertBefore(panel, rootNode) { panel.parentNode = this; panel.nextSibling = rootNode; panel.isConnected = true; if (!doc.panels.includes(panel)) doc.panels.push(panel); } };
const requirementRoot = { parentNode: parent };
const first = fakePanel(doc); const second = fakePanel(doc); first.parentNode = parent; second.parentNode = parent; doc.panels.push(first, second);
const context = { doc, panel: null, minified: false, fingerprint: '' };
const mounted = sandbox.mount(context, requirementRoot);
if (mounted !== first || doc.panels.filter(panel => panel.isConnected).length !== 1) throw new Error('duplicate mounted panels were not reconciled');
if (typeof mounted.onclick !== 'function') throw new Error('authoritative panel toggle handler was not installed');
sandbox.mount(context, requirementRoot);
if (doc.panels.filter(panel => panel.isConnected).length !== 1) throw new Error('repeated mount created a duplicate panel');
console.log('Issue #456 requirements truth-state and dedupe runtime passed.');
''', encoding="utf-8")

validator = VALIDATOR.read_text(encoding="utf-8")
if "ISSUE456_REQUIREMENTS_TRUTH_RUNTIME" not in validator:
    validator = replace_exact(
        validator,
        'ISSUE454_PREBOOT_STATE_CONTRACT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"\n',
        'ISSUE454_PREBOOT_STATE_CONTRACT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"\nISSUE456_REQUIREMENTS_TRUTH_RUNTIME = ROOT / ".github" / "scripts" / "test_issue456_requirements_truth_runtime.js"\n',
        "validator Issue 456 constant",
    )
    validator = replace_exact(
        validator,
        'ISSUE378_OPERATIONAL_FEATURE_RUNTIME]\n',
        'ISSUE378_OPERATIONAL_FEATURE_RUNTIME, ISSUE456_REQUIREMENTS_TRUTH_RUNTIME]\n',
        "validator required runtime",
    )
    validator = replace_exact(
        validator,
        '''        if issue454_preboot_state.returncode != 0:
            fail("Issue #454 preboot state-order contract failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
''',
        '''        if issue454_preboot_state.returncode != 0:
            fail("Issue #454 preboot state-order contract failed")

        issue456_requirements_truth = subprocess.run(
            ["node", str(ISSUE456_REQUIREMENTS_TRUTH_RUNTIME)],
            cwd=ROOT,
        )
        if issue456_requirements_truth.returncode != 0:
            fail("Issue #456 requirements truth-state runtime failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
''',
        "validator Issue 456 execution",
    )
VALIDATOR.write_text(validator, encoding="utf-8")

fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
fixture["candidateVersion"] = "5.0.4"
fixture["candidateSourceSha256"] = hashlib.sha256(source.encode("utf-8")).hexdigest()
changes = fixture.setdefault("approvedNonStyleChanges", [])
if not any(change.get("issue") == 456 for change in changes):
    changes.append({"issue": 456, "phase": "requirements-truth-state-and-panel-dedupe", "lines": line_delta})
fixture["approvedNonStyleSourceLines"] = sum(int(change["lines"]) for change in changes)
fixture["expectedSourceLines"] = fixture["candidateSourceLines"] + fixture["approvedNonStyleSourceLines"] - fixture["retiredNonStyleSourceLines"]
fixture["invariant"] = "The reviewed compact stylesheet retains 504 recovered source lines while Operational Requirements fails safe on empty parsing and enforces one authoritative panel per document."
FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

for diagnostic in DIAGNOSTICS:
    diagnostic.unlink(missing_ok=True)

subprocess.run(["node", str(TEST)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, env=ENV, check=True)
print(f"Prepared v5.0.4 with source-line delta {line_delta} and fail-safe Operational Requirements truth states.")
