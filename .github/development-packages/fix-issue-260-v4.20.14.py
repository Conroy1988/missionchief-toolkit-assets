#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src/data/mission-requirements-en_GB.json"
RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CONTRACT_TEST = ROOT / ".github/scripts/test_mission_requirements_contract.py"
CATALOGUE_FIXTURE = ROOT / ".github/fixtures/mission-catalogue-pages.json"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
DIST_JS = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
SUMS = ROOT / "dist/SHA256SUMS.txt"
MANIFEST = ROOT / "dist/release-manifest.json"
CONTRACT_DOC = ROOT / "docs/issue-260-clean-matrix-contract.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def update_source() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, "// @version      4.20.13", "// @version      4.20.14", "metadata version")
    source = replace_once(source, "version: '4.20.13'", "version: '4.20.14'", "runtime version")
    source = replace_once(source, '{"key":"public-order-level-2","label":"Level 2 Public Order Officer","aliases":["Level 2 Public Order Officer","Level 2 Public Order Officers"],"group":"staff","types":[],"countable":false}', '{"key":"public-order-level-2","label":"Level 2 Public Order Officer","aliases":["Level 2 Public Order Officer","Level 2 Public Order Officers"],"group":"staff","types":[],"training":["Level 2 Public Order Officer","Level 2 Public Order","level_2_public_order"],"countable":true}', "Level 2 Public Order definition")
    source = replace_once(source, '{"key":"police-sergeant-personnel","label":"Police Sergeant","aliases":["Police Sergeant","Police Sergeants"],"group":"staff","types":[],"countable":false}', '{"key":"police-sergeant-personnel","label":"Police Sergeant","aliases":["Police Sergeant","Police Sergeants"],"group":"staff","types":[],"training":["Police Sergeant","Police Sergeant Training","police_sergeant"],"countable":true}', "Police Sergeant definition")

    old_panel = '''            const sourceBadge = row.requirementSource ? `<small class="mcms-req-source">${escapeHtml(row.requirementSource)}</small>` : '';
            return `<tr data-row-state="${rowState}" title="${escapeHtml(`${row.requirement}: ${status}`)}"><td><span>${escapeHtml(row.requirement)}</span>${sourceBadge}</td><td data-label="Required">${escapeHtml(requiredText)}</td><td data-label="On site">${escapeHtml(onSiteText)}</td><td data-label="Respond.">${escapeHtml(respondingText)}</td><td data-label="Selected">${escapeHtml(selectedText)}</td><td class="mcms-req-still" data-label="Need">${escapeHtml(stillText)}</td></tr>`;'''
    new_panel = '''            const sourceKey = String(row.requirementSource || '').trim().toLowerCase().replace(/[^a-z0-9]+/gu, '-').replace(/^-|-$/gu, '');
            return `<tr data-row-state="${rowState}" data-requirement-key="${escapeHtml(row.key || '')}" data-requirement-source="${escapeHtml(sourceKey)}" data-required="${escapeHtml(requiredText)}" data-on-site="${escapeHtml(onSiteText)}" data-responding="${escapeHtml(respondingText)}" data-selected="${escapeHtml(selectedText)}" data-still-needed="${escapeHtml(stillText)}" title="${escapeHtml(`${row.requirement}: ${status}`)}"><td><span class="mcms-matrix-requirement-name">${escapeHtml(row.requirement)}</span></td><td data-label="Required">${escapeHtml(requiredText)}</td><td data-label="On site">${escapeHtml(onSiteText)}</td><td data-label="Respond.">${escapeHtml(respondingText)}</td><td data-label="Selected">${escapeHtml(selectedText)}</td><td class="mcms-req-still" data-label="Need">${escapeHtml(stillText)}</td></tr>`;'''
    source = replace_once(source, old_panel, new_panel, "clean Matrix row renderer")

    old_personnel = "function missionRequirementsCataloguePersonnelRequirements(label, value) { const rawLabel = missionRequirementsCatalogueText({ textContent: label }); if (!/^Required\\s+Personnel(?:\\s+Available)?$/iu.test(rawLabel)) return { recognized: false, requirements: [], unresolved: [] }; const text = missionRequirementsCatalogueText({ textContent: value }).replace(/\\s*(?:\\+|\\/|\\band\\b)\\s*(?=\\d+\\s*x?\\s*[A-Za-z])/giu, '; '); const parsed = missionRequirementsParseText(text, 'staff'); return { recognized: true, requirements: parsed.requirements.map(requirement => ({ ...requirement, baseline: requirement.missing, baselineText: requirement.missing.toLocaleString('en-GB'), probability: 100, catalogueLabel: rawLabel, catalogueValue: value, catalogueKnown: true })), unresolved: parsed.remaining ? [{ label: rawLabel, value: parsed.remaining, group: 'staff' }] : [] }; }"
    new_personnel = "function missionRequirementsCataloguePersonnelRequirements(label, value, kind = null) { const rawLabel = missionRequirementsCatalogueText({ textContent: label }); const available = /^Required\\s+Personnel\\s+Available$/iu.test(rawLabel); const required = /^Required\\s+Personnel$/iu.test(rawLabel); if (!available && !required) return { recognized: false, classification: null, requirements: [], unresolved: [] }; if (available || kind === 'preconditions') return { recognized: true, classification: 'spawn-prerequisite', requirements: [], unresolved: [] }; const text = missionRequirementsCatalogueText({ textContent: value }).replace(/\\s+(?=(?:\\d+\\s*x|x\\s*\\d+)\\s*[A-Za-z])/giu, '; ').replace(/\\s*(?:\\+|\\/|\\band\\b)\\s*(?=\\d+\\s*x?\\s*[A-Za-z])/giu, '; '); const parsed = missionRequirementsParseText(text, 'staff'); return { recognized: true, classification: 'operational', requirements: parsed.requirements.map(requirement => ({ ...requirement, baseline: requirement.missing, baselineText: requirement.missing.toLocaleString('en-GB'), probability: 100, catalogueLabel: rawLabel, catalogueValue: value, catalogueKnown: true, catalogueClassification: 'operational' })), unresolved: parsed.remaining ? [{ label: parsed.remaining, value: '', group: 'staff', classification: 'operational' }] : [] }; }"
    source = replace_once(source, old_personnel, new_personnel, "typed personnel catalogue classification")

    old_personnel_block = "const personnel = missionRequirementsCataloguePersonnelRequirements(label, value); if (personnel.recognized) { sawAuthoritativeRequirement = true; personnel.requirements.forEach(requirement => missionRequirementsCatalogueMergeRequirement(requirements, requirement)); unresolved.push(...personnel.unresolved); if (kind === 'preconditions') preconditions[label] = value; else if (kind === 'other') other[label] = value; continue; }"
    new_personnel_block = "const personnel = missionRequirementsCataloguePersonnelRequirements(label, value, kind); if (personnel.recognized) { if (personnel.classification === 'spawn-prerequisite') { if (kind === 'preconditions') preconditions[label] = value; continue; } sawAuthoritativeRequirement = true; personnel.requirements.forEach(requirement => missionRequirementsCatalogueMergeRequirement(requirements, requirement)); unresolved.push(...personnel.unresolved); if (kind === 'other') other[label] = value; continue; }"
    source = replace_once(source, old_personnel_block, new_personnel_block, "catalogue personnel classification routing")
    source = replace_once(source, "else unresolved.push({ label, value });", "else unresolved.push({ label, value, classification: 'operational' });", "operational unresolved classification")

    old_reconcile = "const text = `Mission info: ${item?.label || 'Unmapped requirement'}${item?.value ? ` — ${item.value}` : ''}`;"
    new_reconcile = "const cleanLabel = missionRequirementsSafeDiagnostic(item?.label || 'Unmapped requirement', 180); const cleanValue = missionRequirementsSafeDiagnostic(item?.value || '', 180); const text = item?.classification === 'operational' ? `${cleanLabel}${cleanValue ? ` — ${cleanValue}` : ''}` : `Mission info: ${cleanLabel}${cleanValue ? ` — ${cleanValue}` : ''}`;"
    source = replace_once(source, old_reconcile, new_reconcile, "clean operational unresolved text")

    old_catalogue_unresolved = "const unresolvedHtml = unresolved.length ? `<div class=\"mcms-req-unknown\"><b>Unmapped catalogue entries</b>${unresolved.map(item => `<span>${escapeHtml(`${item.label}: ${item.value}`)}</span>`).join('')}</div>` : '';"
    new_catalogue_unresolved = "const unresolvedHtml = unresolved.length ? `<div class=\"mcms-req-unknown\"><b>Unmapped catalogue entries</b>${unresolved.map(item => { const text = item.value ? `${item.label}: ${item.value}` : item.label; return `<span>${escapeHtml(text)}</span>`; }).join('')}</div>` : '';"
    source = replace_once(source, old_catalogue_unresolved, new_catalogue_unresolved, "clean catalogue unresolved presentation")
    SOURCE.write_text(source, encoding="utf-8")


def update_dataset() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    staff = [entry for entry in data.get("staffRequirements", []) if entry.get("key") not in {"public-order-level-2", "police-sergeant-personnel"}]
    staff.extend([
        {"key":"public-order-level-2","aliases":["Level 2 Public Order Officer","Level 2 Public Order Officers"],"types":[],"training":["Level 2 Public Order Officer","Level 2 Public Order","level_2_public_order"]},
        {"key":"police-sergeant-personnel","aliases":["Police Sergeant","Police Sergeants"],"types":[],"training":["Police Sergeant","Police Sergeant Training","police_sergeant"]},
    ])
    data["staffRequirements"] = staff
    DATA.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")


def update_catalogue_fixture() -> None:
    data = json.loads(CATALOGUE_FIXTURE.read_text(encoding="utf-8"))
    fight = next(page for page in data["pages"] if page["name"] == "fight on train")
    fight["expected"].pop("railway-police-officer", None)
    name = "operational personnel versus spawn prerequisites"
    data["pages"] = [page for page in data["pages"] if page.get("name") != name]
    data["pages"].append({"name":name,"sourceUrl":"https://www.missionchief.co.uk/einsaetze/fixture-operational-personnel","id":99992,"title":"Recorded operational personnel fixture","sections":{"reward":[["Average credits","7500"],["Required Police Stations","8"],["Required Personnel Available","40x Level 2 Public Order Officer 5x Police Sergeant"]],"requirements":[["Required Police Cars","5"]],"other":[["Required Personnel","18x Level 2 Public Order Officer 1x Police Sergeant"]]},"variations":[],"expected":{"police-car":5,"public-order-level-2":18,"police-sergeant-personnel":1}})
    CATALOGUE_FIXTURE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def update_runtime_tests() -> None:
    text = RUNTIME_TEST.read_text(encoding="utf-8")
    text = text.replace("version: '4.20.12'", "version: '4.20.14'", 1)
    text = replace_once(text, "assert(patientRecord.panel.innerHTML.includes('Patients'), 'patient-derived row identifies its source');", "assert(!patientRecord.panel.innerHTML.includes('>Patients<'), 'patient-derived row has no visible source badge');\nassert(patientRecord.panel.innerHTML.includes('data-requirement-source=\"patients\"'), 'patient-derived row keeps machine-readable provenance');", "existing patient source assertion")
    old_badge = "assert(api.panelHtml(authoritativeRows, []).html.includes('Mission info'), 'normal Matrix displays the compact mission-info source badge');"
    new_badge = "const cleanAuthoritativePanel = api.panelHtml(authoritativeRows, []).html;\nassert(!cleanAuthoritativePanel.includes('>Mission info<'), 'normal Matrix does not render mission-info provenance as label text');\nassert(cleanAuthoritativePanel.includes('data-requirement-source=\"mission-info\"'), 'mission-info provenance remains machine-readable outside the label');\nassert(cleanAuthoritativePanel.includes('class=\"mcms-matrix-requirement-name\">Fire Engine</span>'), 'canonical requirement label remains structurally clean');"
    text = replace_once(text, old_badge, new_badge, "source badge runtime assertion")
    text = replace_once(text, "assert.strictEqual(fightQuantities['railway-police-officer'], 8, 'Fight on Train requires eight Railway Police Officers from personnel metadata');", "assert.strictEqual(fightQuantities['railway-police-officer'], undefined, 'Fight on Train spawn-availability personnel do not become operational catalogue demand');", "Fight on Train prerequisite assertion")
    text = replace_once(text, "assert.strictEqual(fightRows.find(item => item.key === 'railway-police-officer').requiredText, '8', 'authoritative trained-personnel baseline reaches Matrix');", "assert.strictEqual(fightRows.some(item => item.key === 'railway-police-officer'), false, 'spawn-availability trained personnel never reach Matrix rows');", "Fight on Train Matrix assertion")

    anchor = "const parsedCatalogues = new Map();"
    block = r'''// Issue #260: clean labels and typed Mission Info personnel classification.
{
const issue260Page = { title: 'Recorded Issue 260 fixture', sections: { reward: [['Average credits','7500'],['Required Police Stations','8'],['Required Personnel Available','40x Level 2 Public Order Officer 5x Police Sergeant']], requirements: [['Required Police Cars','5']], other: [['Required Personnel','18x Level 2 Public Order Officer 1x Police Sergeant']] }, variations: [] };
const issue260Catalogue = api.parseCatalogueDocument(makeCatalogueDocument(issue260Page), { id: 26000 });
const issue260ByLabel = Object.fromEntries(issue260Catalogue.requirements.map(item => [item.requirement, item.baseline]));
assert.strictEqual(issue260ByLabel['Level 2 Public Order Officer'], 18, 'operational Required Personnel becomes a canonical Level 2 Public Order Officer row');
assert.strictEqual(issue260ByLabel['Police Sergeant'], 1, 'operational Required Personnel becomes a canonical Police Sergeant row');
assert.strictEqual(issue260Catalogue.requirements.some(item => item.baseline === 40), false, 'Required Personnel Available count is excluded completely');
assert.strictEqual(issue260Catalogue.requirements.some(item => item.baseline === 5 && item.group === 'staff'), false, 'spawn-prerequisite Police Sergeant count is not merged with operational demand');
assert.strictEqual(issue260Catalogue.unresolved.some(item => /Personnel Available|40x|5x Police Sergeant/i.test(`${item.label || ''} ${item.value || ''}`)), false, 'spawn prerequisites never enter unresolved output');
assert.strictEqual(issue260Catalogue.preconditions['Required Personnel Available'], '40x Level 2 Public Order Officer 5x Police Sergeant', 'spawn prerequisite remains typed catalogue metadata');
const issue260Reconciled = api.reconcileCatalogue({ requirements: [], unresolved: [] }, issue260Catalogue, 'ready', true);
assert.strictEqual(issue260Reconciled.unresolved.length, 0, 'supported operational personnel reconcile without raw Mission info text');
const issue260Level2 = issue260Catalogue.requirements.find(item => item.key === 'public-order-level-2');
const issue260Sergeant = issue260Catalogue.requirements.find(item => item.key === 'police-sergeant-personnel');
assert.strictEqual(issue260Level2?.definition?.countable, true, 'Level 2 Public Order personnel is live-countable');
assert.strictEqual(issue260Sergeant?.definition?.countable, true, 'Police Sergeant personnel is live-countable');
for (const bucketName of ['Selected','Responding','On site']) {
    const level2Capacity = api.aggregate(issue260Level2, [{ typeId: -1, equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), training: new Set(['level 2 public order']), staff: { min: 1, max: 1, known: true }, contributionKey: `issue260-level2-${bucketName}` }]);
    const sergeantCapacity = api.aggregate(issue260Sergeant, [{ typeId: -1, equipment: new Set(), labels: new Set(), knownDefinitionKeys: new Set(), training: new Set(['police sergeant']), staff: { min: 1, max: 1, known: true }, contributionKey: `issue260-sergeant-${bucketName}` }]);
    assert.strictEqual(level2Capacity.min, 1, `Level 2 Public Order counts in ${bucketName}`);
    assert.strictEqual(sergeantCapacity.min, 1, `Police Sergeant counts in ${bucketName}`);
}
const unsupportedPage = { title: 'Recorded unsupported operational personnel fixture', sections: { reward: [], requirements: [], other: [['Required Personnel','2x Unsupported Tactical Specialist']] }, variations: [] };
const unsupportedCatalogue = api.parseCatalogueDocument(makeCatalogueDocument(unsupportedPage), { id: 26001 });
const unsupportedReconciled = api.reconcileCatalogue({ requirements: [], unresolved: [] }, unsupportedCatalogue, 'ready', true);
assert(unsupportedReconciled.unresolved.some(item => /Unsupported Tactical Specialist/.test(item.text)), 'unsupported operational personnel remain visible');
assert(unsupportedReconciled.unresolved.every(item => !/^Mission info:/i.test(item.text)), 'unsupported operational personnel omit the raw Mission info prefix');
const patientRows = [{ key:'ambulance', requirement:'Ambulance', requirementSource:'Patients', covered:false, definitelyOpen:true, uncertain:false, partial:false, requiredText:'1', onSiteText:'0', respondingText:'0', selectedText:'0', stillNeededText:'1' },{ key:'patient-transport', requirement:'Patient Transport', requirementSource:'Patient details', covered:false, definitelyOpen:true, uncertain:false, partial:false, requiredText:'1', onSiteText:'0', respondingText:'0', selectedText:'0', stillNeededText:'1' }];
const cleanPatientPanel = api.panelHtml(patientRows, []).html;
assert(!cleanPatientPanel.includes('>Patients<') && !cleanPatientPanel.includes('>Patient details<'), 'patient provenance badges are structurally absent');
assert(cleanPatientPanel.includes('data-requirement-source="patients"') && cleanPatientPanel.includes('data-requirement-source="patient-details"'), 'patient provenance remains machine-readable');
assert(cleanPatientPanel.includes('class="mcms-matrix-requirement-name">Ambulance</span>'), 'Ambulance label contains no provenance child');
assert(cleanPatientPanel.includes('class="mcms-matrix-requirement-name">Patient Transport</span>'), 'Patient Transport label contains no provenance child');
}

'''
    text = replace_once(text, anchor, block + anchor, "Issue 260 runtime fixtures")
    RUNTIME_TEST.write_text(text, encoding="utf-8")


def update_contract_test() -> None:
    text = CONTRACT_TEST.read_text(encoding="utf-8")
    text = replace_once(text, '"function missionRequirementsCataloguePersonnelRequirements(label, value)",', '"function missionRequirementsCataloguePersonnelRequirements(label, value, kind = null)",', "personnel signature marker")
    lines = text.splitlines()
    indices = [i for i, line in enumerate(lines) if "whole-row captions must not prove personnel training" in line]
    if len(indices) != 1:
        raise RuntimeError(f"Issue 260 contract anchor count was {len(indices)}")
    insertion = indices[0] + 1
    lines[insertion:insertion] = [
        '    assert "<small class=\\"mcms-req-source\\">" not in source, "Matrix provenance badges must be structurally absent"',
        '    assert "class=\\"mcms-matrix-requirement-name\\"" in source, "Matrix requirement label needs a clean parser-facing element"',
        '    assert "data-requirement-source=\\"${escapeHtml(sourceKey)}\\"" in source, "Matrix provenance must remain outside label text"',
        '    assert "classification: \'spawn-prerequisite\'" in source, "Mission Info spawn prerequisites need typed exclusion"',
        '    assert "item?.classification === \'operational\'" in source, "operational catalogue unresolved text must be prefix-free"',
        '    assert \'"key":"public-order-level-2"\' in source and \'"level_2_public_order"\' in source, "Level 2 Public Order needs native training evidence"',
        '    assert \'"key":"police-sergeant-personnel"\' in source and \'"police_sergeant"\' in source, "Police Sergeant needs native training evidence"',
    ]
    CONTRACT_TEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_release_files() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    DIST_JS.write_text(source, encoding="utf-8")
    DIST_TXT.write_text(source, encoding="utf-8")
    SUMS.write_text(f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n", encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["version"] = "4.20.14"
    manifest["sha256"] = digest
    manifest["bytes"] = len(source.encode("utf-8"))
    manifest["lines"] = len(source.splitlines())
    manifest["metadata"]["runtimeVersion"] = "4.20.14"
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    changelog = CHANGELOG.read_text(encoding="utf-8")
    entry = """## [4.20.14] - 2026-07-20

### Fixed
- Removed visible Mission Info, Patients and Patient Details provenance badges from Matrix requirement labels while retaining machine-readable row metadata.
- Classified Required Personnel Available as a mission-generation prerequisite so it cannot create rows, unresolved shortages, red state or coverage totals.
- Normalised Other information → Required Personnel into operational trained-personnel rows and removed raw Mission info prefixes from unsupported operational personnel.
- Enabled live Level 2 Public Order Officer and Police Sergeant reconciliation from explicit MissionChief training evidence.

### Compatibility
- Updated the Fight on Train catalogue fixture so spawn-availability Railway Police personnel are no longer treated as operational demand.
- Added deterministic clean-label, prerequisite, operational-personnel and parser-facing row contracts.

"""
    changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog")
    CHANGELOG.write_text(changelog, encoding="utf-8")
    help_text = HELP.read_text(encoding="utf-8")
    help_text = replace_once(help_text, "Guide for Toolkit v4.20.13", "Guide for Toolkit v4.20.14", "help version")
    HELP.write_text(help_text, encoding="utf-8")
    CONTRACT_DOC.write_text("""# Issue #260 — Clean Mission Matrix metadata contract

Toolkit v4.20.14 separates operational labels from provenance and mission-generation metadata.

- Requirement-name text contains only the canonical operational label.
- Provenance is exposed through `data-requirement-source`, never a visible or hidden badge child.
- `Required Personnel Available` is a `spawn-prerequisite` and cannot enter rows, unresolved output, totals or panel colour.
- `Other information → Required Personnel` is operational and produces normal trained-personnel rows.
- Level 2 Public Order Officer and Police Sergeant use explicit MissionChief training evidence for live reconciliation.
- Unsupported operational personnel remain visible without a `Mission info:` prefix.
- Precondition station, extension and organisational unlock metadata remains outside the operational model.
""", encoding="utf-8")


def run_checks() -> None:
    commands = [["node","--check",str(SOURCE)],["node",str(RUNTIME_TEST)],["python3",str(CONTRACT_TEST)],["python3",str(ROOT / ".github/scripts/audit_lssm_requirement_compatibility.py")]]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    source_bytes = SOURCE.read_bytes()
    if DIST_JS.read_bytes() != source_bytes or DIST_TXT.read_bytes() != source_bytes:
        raise RuntimeError("distribution parity failed")


def main() -> None:
    update_source()
    update_dataset()
    update_catalogue_fixture()
    update_runtime_tests()
    update_contract_test()
    update_release_files()
    run_checks()


if __name__ == "__main__":
    main()
