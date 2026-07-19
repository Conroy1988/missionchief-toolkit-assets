#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DIST_FILES = [
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def replace_function(text: str, name: str, replacement: str) -> str:
    marker = f"function {name}"
    start = text.find(marker)
    if start < 0:
        raise AssertionError(f"{marker} not found")
    brace = text.find("{", start)
    if brace < 0:
        raise AssertionError(f"{marker} opening brace not found")
    depth = 0
    quote = None
    escaped = False
    for index in range(brace, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"', '`'):
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[:start] + replacement + text[index + 1:]
    raise AssertionError(f"{marker} closing brace not found")


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.20.7", "// @version      4.20.8", "metadata version")
source = replace_once(source, "version: '4.20.7'", "version: '4.20.8'", "runtime version")

new_panel_html = r'''function missionRequirementsPanelHtml(rows, unresolved) {
        const visibleRows = rows.filter(row => !row.covered);
        const definiteOutstanding = visibleRows.filter(row => row.definitelyOpen).length;
        const uncertain = visibleRows.filter(row => row.uncertain).length + unresolved.length;
        const fulfilled = rows.length - visibleRows.length;
        const stateName = missionRequirementsOverallState(rows, unresolved);
        const summary = stateName === 'success'
            ? `All ${rows.length} covered`
            : stateName === 'warning'
                ? `${uncertain} need confirmation · ${fulfilled}/${rows.length} covered`
                : `${definiteOutstanding} outstanding · ${fulfilled}/${rows.length} covered`;
        const rowHtml = visibleRows.map(row => {
            const rowState = row.uncertain ? 'unresolved' : row.partial ? 'partial' : 'open';
            const requiredText = row.requiredText || (Number.isFinite(Number(row.missing)) ? Number(row.missing).toLocaleString('en-GB') : '?');
            const onSiteText = row.onSiteText || '?';
            const respondingText = row.respondingText || row.enRouteText || '?';
            const selectedText = row.selectedText || '?';
            const stillText = row.stillNeededText || '?';
            const status = row.uncertain ? 'requires confirmation' : row.partial ? 'partially fulfilled' : 'outstanding';
            const sourceBadge = row.requirementSource ? `<small class="mcms-req-source">${escapeHtml(row.requirementSource)}</small>` : '';
            return `<tr data-row-state="${rowState}" title="${escapeHtml(`${row.requirement}: ${status}`)}"><td><span>${escapeHtml(row.requirement)}</span>${sourceBadge}</td><td data-label="Required">${escapeHtml(requiredText)}</td><td data-label="On site">${escapeHtml(onSiteText)}</td><td data-label="Respond.">${escapeHtml(respondingText)}</td><td data-label="Selected">${escapeHtml(selectedText)}</td><td class="mcms-req-still" data-label="Need">${escapeHtml(stillText)}</td></tr>`;
        }).join('');
        const tableHtml = visibleRows.length
            ? `<table aria-label="Live mission requirements"><colgroup><col class="mcms-req-name-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"><col class="mcms-req-number-col"></colgroup><thead><tr><th scope="col">Requirement</th><th scope="col">Required</th><th scope="col">On site</th><th scope="col">Responding</th><th scope="col">Selected</th><th scope="col">Still needed</th></tr></thead><tbody>${rowHtml}</tbody></table>`
            : '';
        const allCoveredHtml = rows.length && !visibleRows.length && !unresolved.length
            ? '<div class="mcms-req-fallback mcms-req-all-covered" role="status"><span class="mcms-req-fallback-message">All currently known requirements are covered.</span></div>'
            : '';
        const unknownHtml = unresolved.length
            ? `<div class="mcms-req-unknown"><b>Unresolved MissionChief requirement</b>${unresolved.map(item => `<span>${escapeHtml(item.text)}</span>`).join('')}<button type="button" class="mcms-req-report" data-mcms-report-mission>Report Mission</button></div>`
            : '';
        return {
            stateName,
            widthMode: missionRequirementsWidthMode(visibleRows, unresolved),
            html: `<div class="mcms-req-head"><div class="mcms-req-title"><i aria-hidden="true"></i><span>Mission Requirements</span></div><span class="mcms-req-summary">${escapeHtml(summary)}</span><button type="button" class="mcms-req-collapse" data-mcms-requirements-collapse aria-label="Collapse mission requirements" aria-expanded="true">⌃</button></div><div class="mcms-req-body">${tableHtml}${allCoveredHtml}${unknownHtml}</div>`
        };
    }'''
source = replace_function(source, "missionRequirementsPanelHtml", new_panel_html)
SOURCE.write_text(source, encoding="utf-8")
for distribution in DIST_FILES:
    distribution.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.7'", "version: '4.20.8'", "runtime fixture version")
old_panel_test = r'''const html = api.panelHtml([
    api.coverageRow(
        { key: 'ambulance', requirement: 'Ambulance', missing: 1, group: 'vehicles', definition: {} },
        { min: 1, max: 1, known: true },
        { min: 0, max: 0, known: true }
    )
], []);
for (const header of fixture.layout.requiredHeaders) assert(html.html.includes(header), `missing table header: ${header}`);
assert.strictEqual(html.stateName, 'success', 'covered panel state');'''
new_panel_test = r'''const fulfilledAmbulanceRow = api.coverageRow(
    { key: 'ambulance', requirement: 'Ambulance', missing: 1, group: 'vehicles', definition: {} },
    { min: 1, max: 1, known: true },
    { min: 0, max: 0, known: true }
);
const openPoliceRow = api.coverageRow(
    { key: 'police-car', requirement: 'Police Car', missing: 2, group: 'vehicles', definition: {} },
    { min: 0, max: 0, known: true },
    { min: 0, max: 0, known: true }
);
const coveredPanel = api.panelHtml([fulfilledAmbulanceRow], []);
assert.strictEqual(coveredPanel.stateName, 'success', 'covered panel state');
assert(coveredPanel.html.includes('All currently known requirements are covered.'), 'all-covered panel retains explicit success state');
assert(!coveredPanel.html.includes('<table'), 'all-covered panel hides the empty requirement table');
assert(!coveredPanel.html.includes('Ambulance'), 'fulfilled row is hidden from the rendered list');

const mixedPanel = api.panelHtml([fulfilledAmbulanceRow, openPoliceRow], []);
for (const header of fixture.layout.requiredHeaders) assert(mixedPanel.html.includes(header), `missing table header: ${header}`);
assert(mixedPanel.html.includes('Police Car'), 'outstanding requirement remains visible');
assert(!mixedPanel.html.includes('Ambulance'), 'fulfilled requirement is hidden beside an outstanding row');
assert(!mixedPanel.html.includes('All currently known requirements are covered.'), 'mixed panel does not show all-covered success');

const renewedAmbulanceRow = api.coverageRow(
    { key: 'ambulance', requirement: 'Ambulance', missing: 2, group: 'vehicles', definition: {} },
    { min: 1, max: 1, known: true },
    { min: 0, max: 0, known: true }
);
const renewedPanel = api.panelHtml([renewedAmbulanceRow], []);
assert(renewedPanel.html.includes('Ambulance'), 'hidden row returns when an upgrade or re-entry creates a positive shortage');
assert(renewedPanel.html.includes('data-row-state="partial"'), 'renewed shortage keeps its live partial state');

const unresolvedPanel = api.panelHtml(
    [fulfilledAmbulanceRow],
    [{ group: 'vehicles', text: 'Unknown specialist response requirement' }]
);
assert(unresolvedPanel.html.includes('Unknown specialist response requirement'), 'unresolved authority remains visible');
assert(!unresolvedPanel.html.includes('All currently known requirements are covered.'), 'unresolved authority overrides all-covered success');
assert.strictEqual(unresolvedPanel.stateName, 'warning', 'unresolved authority remains warning state');'''
runtime = replace_once(runtime, old_panel_test, new_panel_test, "fulfilled row runtime fixtures")
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract_anchor = '    assert source.count("function missionRequirementsPatientContext(candidate)") == 1\n'
contract_addition = '''    assert "const visibleRows = rows.filter(row => !row.covered);" in source, "fulfilled Matrix rows must be presentation-filtered"
    assert "All currently known requirements are covered." in source, "all-covered Matrix state must remain explicit"
    assert "missionRequirementsWidthMode(visibleRows, unresolved)" in source, "fulfilled rows must not inflate rendered width"
'''
contract = replace_once(contract, contract_anchor, contract_anchor + contract_addition, "fulfilled row contract assertions")
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [4.20.8] - 2026-07-20

### Fixed
- Fulfilled Mission Requirements Matrix rows are now hidden whenever their reconciled **Still needed** value is definitively zero.
- Hidden rows immediately return when selection, responding, on-site, patient, personnel or upgraded mission demand creates a positive shortage.
- All-covered missions retain a compact explicit success state instead of showing an empty table.

### Safety
- Unresolved, uncertain, loading and unavailable requirements remain visible and continue to block false success states.
- Requirement calculations, authoritative reconciliation, unit de-duplication and MissionChief/LSSM coexistence are unchanged.

### Validation
- Added deterministic fixtures for fulfilled-row suppression, mixed outstanding/fulfilled rows, renewed shortages after upgrade or re-entry, and unresolved-authority precedence.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog release entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run(["node", str(RUNTIME.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(CONTRACT.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", str(DIST_FILES[0].relative_to(ROOT)), str(DIST_FILES[1].relative_to(ROOT))], cwd=ROOT, check=True)
print("Fulfilled Mission Matrix row visibility hotfix validated")
