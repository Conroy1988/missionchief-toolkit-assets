#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_USER = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_TEXT = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt'
DIST_SUMS = ROOT / 'dist' / 'SHA256SUMS.txt'
MANIFEST = ROOT / 'dist' / 'release-manifest.json'
CHANGELOG = ROOT / 'CHANGELOG.md'
HELP_INDEX = ROOT / 'help' / 'index.html'
HELP_MANIFEST = ROOT / 'help' / 'manifest.json'
RUNTIME = ROOT / '.github' / 'scripts' / 'test_mission_requirements_runtime.js'
CONTRACT = ROOT / '.github' / 'scripts' / 'test_mission_requirements_contract.py'
DOC = ROOT / 'docs' / 'issue-183-authoritative-mission-requirements-contract.md'
PREVIOUS = '4.18.0'
VERSION = '4.19.0'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f'{label}: expected one match, found {count}')
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding='utf-8')
source = replace_once(source, f'// @version      {PREVIOUS}', f'// @version      {VERSION}', 'metadata version')
source = replace_once(source, f"        version: '{PREVIOUS}',", f"        version: '{VERSION}',", 'runtime version')

anchor = '''        return { requirements, unresolved };
    }

    // Issue #181: patient-derived ambulance demand.'''
addition = '''        return { requirements, unresolved };
    }

    // Issue #183: merge the authoritative "Requirements for this Mission" catalogue into the live model.
    function missionRequirementsReconcileCatalogue(parsed, catalogue, state = 'unavailable', expected = false) {
        const requirements = Array.from(parsed?.requirements || [], item => ({ ...item }));
        const unresolved = Array.from(parsed?.unresolved || [], item => ({ ...item }));
        const byKey = new Map(requirements.map((item, index) => [item.key, index]));
        for (const item of catalogue?.requirements || []) {
            const baseline = missionRequirementsOptionalNumber(item?.baseline ?? item?.missing);
            if (baseline === null) continue;
            const index = byKey.get(item.key);
            if (index !== undefined) {
                requirements[index] = { ...requirements[index], catalogueDerived: true, catalogueBaseline: baseline, catalogueProbability: missionRequirementsOptionalNumber(item.probability) ?? 100 };
                continue;
            }
            const requirement = { ...item, missing: baseline, baseline, statedRequirement: false, catalogueDerived: true, catalogueProbability: missionRequirementsOptionalNumber(item.probability) ?? 100, requirementSource: catalogue?.stale ? 'Cached mission info' : 'Mission info' };
            byKey.set(requirement.key, requirements.length);
            requirements.push(requirement);
        }
        const unresolvedSeen = new Set(unresolved.map(item => String(item?.text || '').toLowerCase()));
        for (const item of catalogue?.unresolved || []) {
            const text = `Mission info: ${item?.label || 'Unmapped requirement'}${item?.value ? ` — ${item.value}` : ''}`;
            if (!unresolvedSeen.has(text.toLowerCase())) { unresolved.push({ group: item?.group || 'other', text, catalogueDerived: true }); unresolvedSeen.add(text.toLowerCase()); }
        }
        if (!catalogue && expected) {
            const text = state === 'loading' || state === 'idle' ? 'Loading Requirements for this Mission…' : 'Requirements for this Mission could not be loaded; verify the mission information manually.';
            if (!unresolvedSeen.has(text.toLowerCase())) unresolved.push({ group: 'other', text, authoritativePending: state === 'loading' || state === 'idle' });
        } else if (catalogue?.stale) unresolved.push({ group: 'other', text: 'Using cached Requirements for this Mission; verify conditional requirements manually.', catalogueDerived: true });
        return { requirements, unresolved };
    }

    // Issue #181: patient-derived ambulance demand.'''
source = replace_once(source, anchor, addition, 'authoritative reconciliation insertion')

source = replace_once(
    source,
    "        const requestToken = Number(record.catalogueRequestToken) || 0;\n        const stillCurrent = () => record?.catalogueDescriptor?.key === descriptor?.key && (Number(record.catalogueRequestToken) || 0) === requestToken;",
    "        const requestToken = Number(record.catalogueRequestToken) || 0;\n        const missionIdentity = missionRequirementsMissionIdentity(record?.candidate, record?.source);\n        const stillCurrent = () => record?.catalogueDescriptor?.key === descriptor?.key && (Number(record.catalogueRequestToken) || 0) === requestToken && missionRequirementsMissionIdentity(record?.candidate, record?.source) === missionIdentity;",
    'stale mission response guard',
)

source = replace_once(
    source,
    "const reconcile = parsed => missionRequirementsReconcilePatientDemand(parsed, patientState);",
    "const reconcile = parsed => missionRequirementsReconcilePatientDemand(missionRequirementsReconcileCatalogue(parsed, record.catalogue, record.catalogueState, Boolean(record.catalogueDescriptor)), patientState);",
    'render reconciliation chain',
)

source = replace_once(
    source,
    "const catalogueRequirement = catalogueByKey.get(requirement.key); const baseline = missionRequirementsOptionalNumber(catalogueRequirement?.baseline ?? catalogueRequirement?.missing); const patientKnown",
    "const catalogueRequirement = catalogueByKey.get(requirement.key); const baseline = missionRequirementsOptionalNumber(catalogueRequirement?.baseline ?? catalogueRequirement?.missing); const catalogueOnly = requirement.catalogueDerived === true && requirement.statedRequirement === false; const catalogueProbability = missionRequirementsOptionalNumber(requirement.catalogueProbability ?? catalogueRequirement?.probability) ?? 100; const patientKnown",
    'resolver catalogue-only state',
)
source = replace_once(
    source,
    "let required; if (patientUnknown) { required = missionRequirementsCapacity(Math.max(baseline ?? 0, statedRequiredMin), null, false); } else if (patientKnown)",
    "let required; if (patientUnknown) { required = missionRequirementsCapacity(Math.max(baseline ?? 0, statedRequiredMin), null, false); } else if (catalogueOnly && catalogueProbability < 100) { required = missionRequirementsCapacity(0, baseline ?? 0, false); } else if (patientKnown)",
    'conditional authoritative capacity',
)
source = replace_once(
    source,
    "const row = missionRequirementsCoverageRow(requirement, selected, responding, onSite, required); if (patientUnknown) { row.covered = false; row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } const authorities",
    "const row = missionRequirementsCoverageRow(requirement, selected, responding, onSite, required); if (patientUnknown) { row.covered = false; row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } else if (catalogueOnly && catalogueProbability < 100 && !row.covered) { row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } const authorities",
    'conditional authoritative row state',
)
source = replace_once(
    source,
    "if (baseline !== null) authorities.push('catalogue');",
    "if (baseline !== null) authorities.push('mission-info');",
    'authority label',
)
SOURCE.write_text(source, encoding='utf-8')

runtime = RUNTIME.read_text(encoding='utf-8')
runtime = runtime.replace("version: '4.18.0'", "version: '4.19.0'")
runtime = replace_once(
    runtime,
    "    reconcilePatientDemand: missionRequirementsReconcilePatientDemand,",
    "    reconcilePatientDemand: missionRequirementsReconcilePatientDemand,\n    reconcileCatalogue: missionRequirementsReconcileCatalogue,",
    'runtime API exposure',
)
fixture_block = r'''

// Issue #183 authoritative Requirements for this Mission reconciliation.
{
const authoritativeMajor = parsedCatalogues.get('personnel-heavy major incident');
const authoritativeOnly = api.reconcileCatalogue({ requirements: [], unresolved: [] }, authoritativeMajor, 'ready', true);
assert.strictEqual(authoritativeOnly.requirements.filter(item => item.key === 'fire-engine').length, 1, 'catalogue-only vehicle requirement is added once');
assert.strictEqual(authoritativeOnly.requirements.filter(item => item.key === 'otl').length, 1, 'catalogue-only personnel requirement is added once');
assert.strictEqual(authoritativeOnly.requirements.filter(item => item.key === 'ambulance-officer').length, 1, 'catalogue-only specialist personnel requirement is retained');
assert(authoritativeOnly.requirements.every(item => item.requirementSource === 'Mission info'), 'catalogue-only rows identify the mission-info source');

const authoritativeDoc = new FakeDocument();
authoritativeDoc.defaultView = { MutationObserver: FakeMutationObserver };
const authoritativeCandidate = makeMissionCandidate(authoritativeDoc, '');
const authoritativeRows = api.resolve(authoritativeCandidate, authoritativeOnly, authoritativeMajor);
assert.strictEqual(authoritativeRows.find(item => item.key === 'fire-engine').requiredText, '10', 'authoritative vehicle baseline becomes Required');
assert.strictEqual(authoritativeRows.find(item => item.key === 'otl').requiredText, '1', 'authoritative personnel baseline becomes Required');
assert(api.panelHtml(authoritativeRows, []).html.includes('Mission info'), 'normal Matrix displays the compact mission-info source badge');

const fireDefinition = api.definitions.find(item => item.key === 'fire-engine');
const overlapping = api.reconcileCatalogue({ requirements: [{ key: 'fire-engine', requirement: 'Fire Engine', missing: 2, group: 'vehicles', definition: fireDefinition }], unresolved: [] }, authoritativeMajor, 'ready', true);
assert.strictEqual(overlapping.requirements.filter(item => item.key === 'fire-engine').length, 1, 'live and authoritative rows are not duplicated');
const overlappingRow = api.resolve(authoritativeCandidate, overlapping, authoritativeMajor).find(item => item.key === 'fire-engine');
assert.strictEqual(overlappingRow.requiredText, '10', 'larger authoritative baseline wins over a lower live reconstruction');

const conditionalCatalogue = parsedCatalogues.get('alternative and conditional requirements');
const conditionalParsed = api.reconcileCatalogue({ requirements: [], unresolved: [] }, conditionalCatalogue, 'ready', true);
const conditionalRow = api.resolve(authoritativeCandidate, conditionalParsed, conditionalCatalogue).find(item => item.key === 'police-car');
assert.strictEqual(conditionalRow.uncertain, true, 'probabilistic mission-info requirement remains uncertain when not covered');
assert.strictEqual(conditionalRow.definitelyOpen, false, 'probabilistic mission-info requirement is not falsely reported as definitely required');

const loadingAuthority = api.reconcileCatalogue({ requirements: [{ key: 'fire-engine', requirement: 'Fire Engine', missing: 1, group: 'vehicles', definition: fireDefinition }], unresolved: [] }, null, 'loading', true);
assert(loadingAuthority.unresolved.some(item => item.authoritativePending), 'Matrix fails closed while Requirements for this Mission is loading');
const failedAuthority = api.reconcileCatalogue({ requirements: [], unresolved: [] }, null, 'error', true);
assert(failedAuthority.unresolved.some(item => /could not be loaded/.test(item.text)), 'failed authoritative source remains visible for manual verification');

const patientCoexistence = api.reconcilePatientDemand(authoritativeOnly, { present: true, known: true, count: 12, source: 'fixture' });
assert.strictEqual(patientCoexistence.requirements.filter(item => item.key === 'ambulance').length, 1, 'patient Ambulance authority coexists without duplication');
assert.strictEqual(patientCoexistence.requirements.find(item => item.key === 'ambulance').patientRequired, 12, 'patient-derived Ambulance demand remains authoritative');

const staleAuthority = api.reconcileCatalogue({ requirements: [], unresolved: [] }, { ...authoritativeMajor, stale: true }, 'stale', true);
assert(staleAuthority.unresolved.some(item => /cached Requirements for this Mission/.test(item.text)), 'stale authoritative data is explicitly identified');
}
'''
runtime = replace_once(runtime, "\nconsole.log('Mission requirements runtime fixtures passed');", fixture_block + "\nconsole.log('Mission requirements runtime fixtures passed');", 'authoritative runtime fixtures')
RUNTIME.write_text(runtime, encoding='utf-8')

contract = CONTRACT.read_text(encoding='utf-8')
contract = replace_once(
    contract,
    '        "function missionRequirementsReconcilePatientDemand(parsed, patientState)",',
    '        "function missionRequirementsReconcilePatientDemand(parsed, patientState)",\n        "function missionRequirementsReconcileCatalogue(parsed, catalogue, state = \'unavailable\', expected = false)",',
    'contract reconciliation marker',
)
contract = replace_once(
    contract,
    '        "function missionRequirementsCatalogueEnsure(record)",',
    '        "function missionRequirementsCatalogueEnsure(record)",\n        "Loading Requirements for this Mission",\n        "Mission info",',
    'contract authoritative markers',
)
contract = replace_once(
    contract,
    '    assert source.count("function missionRequirementsReconcilePatientDemand(parsed, patientState)") == 1',
    '    assert source.count("function missionRequirementsReconcilePatientDemand(parsed, patientState)") == 1\n    assert source.count("function missionRequirementsReconcileCatalogue(parsed, catalogue, state = \'unavailable\', expected = false)") == 1\n    assert "return parsed.requirements.map(requirement =>" in source, "resolver must retain one pass over the reconciled union"\n    assert "catalogueOnly && catalogueProbability < 100" in source, "probabilistic authoritative requirements must remain uncertain"',
    'contract authoritative assertions',
)
CONTRACT.write_text(contract, encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
entry = '''## [Unreleased]\n\n## [4.19.0] - 2026-07-19\n\n### Fixed\n- Promoted MissionChief's **Requirements for this Mission** vehicle and personnel data from fallback-only planning information into an authoritative Mission Requirements Matrix source.\n- Added authoritative-only rows that were absent from `#missing_text`, while reconciling overlaps with the strongest non-duplicated requirement.\n- Preserved patient-derived Ambulance demand as an independent authority and rejected stale mission responses during AJAX navigation.\n\n### Behaviour\n- Deterministic requirements are counted normally; probability-based requirements remain visible as uncertain until MissionChief confirms them or sufficient units cover the maximum.\n- The Matrix now fails closed while authoritative mission information is loading or unavailable, preventing a false green state.\n- Official mission definitions remain cached by definition URL, with active mission-instance tokens preventing stale response application.\n\n### Validation\n- Added fixtures for catalogue-only vehicles, personnel, overlapping sources, conditional requirements, patient coexistence, loading failures and cached authoritative data.\n\n'''
changelog = replace_once(changelog, '## [Unreleased]\n\n', entry, 'changelog entry')
CHANGELOG.write_text(changelog, encoding='utf-8')

DOC.write_text('''# Issue #183 — Authoritative Requirements for this Mission contract\n\nThe Mission Requirements Matrix automatically reads the official MissionChief `/einsaetze/<definition>` page linked by **Requirements for this Mission**. Vehicle and personnel rows are parsed through the existing UK requirement definitions and merged into the live Matrix model.\n\nThe reconciliation contract is a key-based union. Existing live rows are retained and receive the official baseline; rows present only in mission information are added once with a compact `Mission info` source badge. Required capacity uses the largest supported authority rather than summing duplicate sources. Patient-derived Ambulance demand remains independent and can raise the Ambulance minimum above mission information.\n\nRequirements with a probability below 100% are displayed as uncertain capacity rather than being falsely declared definitely outstanding. Unknown or unmapped mission-information rows remain unresolved, and a pending or failed authoritative request prevents a false complete state.\n\nDefinitions are cached by official definition URL because all mission instances of that definition share the same baseline. Each record also captures the active mission-instance identity, so a delayed response cannot apply after AJAX navigation. No polling, automatic selection or dispatch is introduced. Desktop, Tablet, iOS and LSSM use the existing single Matrix panel.\n''', encoding='utf-8')

help_html = HELP_INDEX.read_text(encoding='utf-8').replace('Toolkit v4.18.0', 'Toolkit v4.19.0')
HELP_INDEX.write_text(help_html, encoding='utf-8')
help_manifest = json.loads(HELP_MANIFEST.read_text(encoding='utf-8'))
help_manifest['guideVersion'] = VERSION
help_manifest['toolkitVersion'] = VERSION
help_manifest['updated'] = '2026-07-19'
help_manifest['runtimeGuidePatch'] = 'Toolkit v4.19.0 makes Requirements for this Mission an authoritative Matrix source, adding missing vehicle and personnel baselines without duplication while retaining patient-derived Ambulance demand.'
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

for path in [
    ROOT / '.github' / 'development-packages' / 'issue-183-resolver-format.py',
    ROOT / '.github' / 'development-packages' / 'issue-183-resolver-probe.py',
    ROOT / '.github' / 'development-packages' / 'issue-183-resolver-map.py',
    ROOT / '.github' / 'diagnostics' / 'issue-183-source-map.txt',
    ROOT / '.github' / 'diagnostics' / 'issue-183-target-map.txt',
    ROOT / '.github' / 'diagnostics' / 'issue-183-function-map.txt',
    ROOT / '.github' / 'diagnostics' / 'issue-183-resolver-map.txt',
    ROOT / '.github' / 'diagnostics' / 'issue-183-resolver-probe.txt',
    ROOT / '.github' / 'diagnostics' / 'issue-183-resolver-formatted.txt',
]:
    path.unlink(missing_ok=True)

DIST_USER.write_text(source, encoding='utf-8')
DIST_TEXT.write_text(source, encoding='utf-8')
digest = hashlib.sha256(source.encode('utf-8')).hexdigest()
DIST_SUMS.write_text(f'{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n', encoding='utf-8')
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
manifest['version'] = VERSION
manifest['sha256'] = digest
manifest['bytes'] = len(source.encode('utf-8'))
manifest['lines'] = len(source.splitlines())
manifest['metadata']['runtimeVersion'] = VERSION
manifest['metadata']['warnings'] = []
manifest['baselineHashMatch'] = None
manifest['distributionStatus'] = 'dry-run-not-yet-greasyfork-source'
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

subprocess.run(['node', '--check', str(SOURCE)], cwd=ROOT, check=True)
subprocess.run(['node', str(RUNTIME)], cwd=ROOT, check=True)
subprocess.run(['python3', str(CONTRACT)], cwd=ROOT, check=True)
assert SOURCE.read_bytes() == DIST_USER.read_bytes() == DIST_TEXT.read_bytes()
assert len(source.splitlines()) <= 32000, f'userscript line budget exceeded: {len(source.splitlines())}'
print(f'Issue #183 v{VERSION} candidate SHA-256: {digest} ({len(source.splitlines())} lines)')
