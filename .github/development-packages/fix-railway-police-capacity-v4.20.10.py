#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
DOC = ROOT / "docs" / "issue-242-railway-police-capacity-contract.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, "// @version      4.20.9", "// @version      4.20.10", "metadata version")
source = replace_once(source, "version: '4.20.9',", "version: '4.20.10',", "runtime version")
source = replace_once(source, "guideVersion: '4.20.9',", "guideVersion: '4.20.10',", "help guide version")
source = replace_once(
    source,
    '"training":["Railway Police Officer","Railway Police"]',
    '"training":["Railway Police Officer","railway_police"]',
    "Railway Police explicit education key",
)
source = replace_once(
    source,
    "const attributes = kind === 'training' ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name'] :",
    "const attributes = kind === 'training' ? ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name', 'data-education-key', 'data-filterable-by'] :",
    "training metadata attributes",
)
source = replace_once(
    source,
    "function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }",
    "function missionRequirementsKnownDefinitionKeys(labels) { const keys = new Set(); for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { if ((definition?.group || 'vehicles') === 'staff') continue; if (missionRequirementsDefinitionMatchesValues(definition, labels)) keys.add(definition.key); } return keys; }",
    "role-specific labels cannot prove staff qualification",
)
row_text_training = "const rowText = missionRequirementsCapabilityLabel(`${row?.textContent || ''} ${row?.innerText || ''}`); if (rowText) { for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { const aliases = Array.from(definition?.training || []).map(missionRequirementsCapabilityLabel).filter(Boolean); if (!aliases.some(alias => rowText.includes(alias))) continue; aliases.forEach(alias => training.add(alias)); knownDefinitionKeys.add(definition.key); } } "
source = replace_once(source, row_text_training, "", "remove generic row-text training inference")

resolve_marker = "function missionRequirementsResolve(candidate, parsed, catalogue = null)"
if source.count(resolve_marker) != 1:
    raise AssertionError("resolve marker must occur exactly once")
helper = r'''function missionRequirementsReconcileCommittedDelta(requirement, baselineValue, selectedCapacity, respondingCapacity, onSiteCapacity) {
        const baseline = missionRequirementsOptionalNumber(baselineValue);
        const selected = missionRequirementsCapacity(selectedCapacity?.min ?? selectedCapacity?.value ?? 0, selectedCapacity?.max, selectedCapacity?.known);
        const responding = missionRequirementsCapacity(respondingCapacity?.min ?? respondingCapacity?.value ?? 0, respondingCapacity?.max, respondingCapacity?.known);
        const onSite = missionRequirementsCapacity(onSiteCapacity?.min ?? onSiteCapacity?.value ?? 0, onSiteCapacity?.max, onSiteCapacity?.known);
        if (baseline === null || requirement?.statedRequirement === false) return { selected, responding, onSite };

        const liveMissing = Math.max(0, Number(requirement?.missing) || 0);
        const committed = Math.max(0, baseline - liveMissing);
        const operationalMin = onSite.min + responding.min;
        const operationalMax = onSite.max === null || responding.max === null ? null : onSite.max + responding.max;
        const inferredSelectedMin = operationalMax === null ? 0 : Math.max(0, committed - operationalMax);
        const inferredSelectedMax = Math.max(0, committed - operationalMin);
        if (inferredSelectedMax <= selected.min) return { selected, responding, onSite };

        const selectedMin = Math.max(selected.min, inferredSelectedMin);
        const selectedMax = selected.max === null ? inferredSelectedMax : Math.max(selected.max, inferredSelectedMax);
        const selectedKnown = selectedMax !== null && selectedMin === selectedMax && onSite.known && responding.known;
        return {
            selected: missionRequirementsCapacity(selectedMin, selectedMax, selectedKnown),
            responding,
            onSite
        };
    }

    '''
source = source.replace(resolve_marker, helper + resolve_marker, 1)
old_inference = "if (baseline !== null && hasStatedRequirement) { const inferredOnSite = Math.max(0, baseline - Math.max(0, Number(requirement.missing) || 0)); if (inferredOnSite > onSite.min) { const inferredMax = onSite.max === null ? null : Math.max(onSite.max, inferredOnSite); onSite = missionRequirementsCapacity(inferredOnSite, inferredMax, onSite.known && inferredMax === inferredOnSite); } }"
new_inference = "if (baseline !== null && hasStatedRequirement) { ({ selected, responding, onSite } = missionRequirementsReconcileCommittedDelta(requirement, baseline, selected, responding, onSite)); }"
source = replace_once(source, old_inference, new_inference, "allocate authoritative committed delta")

SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.9'", "version: '4.20.10'", "runtime fixture version")
runtime = replace_once(
    runtime,
    "    metadataValues: missionRequirementsMetadataValues,\n",
    "    metadataValues: missionRequirementsMetadataValues,\n    knownDefinitionKeys: missionRequirementsKnownDefinitionKeys,\n    reconcileCommittedDelta: missionRequirementsReconcileCommittedDelta,\n",
    "runtime helper exports",
)
railway_anchor = "assert.strictEqual(railwaySelectedCapacity.max, 1, 'one selected Railway Police Officer remains exact');\n"
railway_tests = r'''

const issue242ExplicitEducationRow = new FakeElement('tr');
const issue242ExplicitEducation = new FakeElement('span');
issue242ExplicitEducation.setAttribute('data-education-key', 'railway_police');
issue242ExplicitEducation.closestMap.set('tr', issue242ExplicitEducationRow);
issue242ExplicitEducationRow.queryAllHandler = selector => selector.includes('[data-education-key]') ? [issue242ExplicitEducation] : [];
const issue242EducationValues = api.metadataValues(issue242ExplicitEducation, 'training');
assert(issue242EducationValues.has('railway police'), 'explicit railway_police education key is recognised');

const issue242CommandEducation = new FakeElement('span');
issue242CommandEducation.setAttribute('data-education-key', 'railway_police_command');
issue242CommandEducation.closestMap.set('tr', issue242ExplicitEducationRow);
const issue242CommandValues = api.metadataValues(issue242CommandEducation, 'training');
assert(issue242CommandValues.has('railway police command'), 'command education key is preserved exactly');
assert(!issue242CommandValues.has('railway police'), 'railway_police_command does not collapse into railway_police');

const issue242CategoryKeys = api.knownDefinitionKeys(new Set(['railway police officer']));
assert(!issue242CategoryKeys.has('railway-police-officer'), 'custom vehicle category cannot prove trained-personnel qualification');
const issue242CategoryOnlyUnit = {
    typeId: 8,
    equipment: new Set(),
    labels: new Set(['railway police officer']),
    training: new Set(),
    knownDefinitionKeys: issue242CategoryKeys,
    staff: api.capacity(4, 4, true),
    contributionKey: 'vehicle:category-only'
};
assert.strictEqual(
    api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [issue242CategoryOnlyUnit]).min,
    0,
    'generic category text and four crew do not create four Railway Police Officers'
);
const issue242CommandUnit = {
    ...issue242CategoryOnlyUnit,
    labels: new Set(),
    training: new Set(['railway police command']),
    knownDefinitionKeys: new Set(),
    contributionKey: 'vehicle:command-only'
};
assert.strictEqual(
    api.aggregate({ group: 'staff', definition: railwayPoliceDefinition }, [issue242CommandUnit]).min,
    0,
    'Mobile Operations Manager training does not satisfy Railway Police Officer demand'
);

const issue242Zero = api.capacity(0, 0, true);
let issue242Delta = api.reconcileCommittedDelta(
    { missing: 4, statedRequirement: true },
    8,
    issue242Zero,
    issue242Zero,
    issue242Zero
);
assert.strictEqual(issue242Delta.selected.min, 4, 'baseline minus live missing is assigned to Selected');
assert.strictEqual(issue242Delta.selected.max, 4, 'authoritative selected delta is exact');
assert.strictEqual(issue242Delta.onSite.min, 0, 'selected delta is not falsely assigned On site');
assert.strictEqual(issue242Delta.responding.min, 0, 'selected delta is not falsely assigned Responding');

issue242Delta = api.reconcileCommittedDelta(
    { missing: 4, statedRequirement: true },
    8,
    issue242Zero,
    issue242Zero,
    api.capacity(4, 4, true)
);
assert.strictEqual(issue242Delta.selected.min, 0, 'actual on-site capacity is subtracted before selected inference');
assert.strictEqual(issue242Delta.onSite.min, 4, 'actual on-site capacity remains On site');

issue242Delta = api.reconcileCommittedDelta(
    { missing: 4, statedRequirement: true },
    8,
    issue242Zero,
    api.capacity(2, 2, true),
    issue242Zero
);
assert.strictEqual(issue242Delta.responding.min, 2, 'actual responding capacity remains Responding');
assert.strictEqual(issue242Delta.selected.min, 2, 'remaining committed delta becomes Selected');

issue242Delta = api.reconcileCommittedDelta(
    { missing: 8, statedRequirement: true },
    8,
    issue242Zero,
    issue242Zero,
    issue242Zero
);
assert.strictEqual(issue242Delta.selected.min, 0, 'restored live demand removes inferred Selected capacity after deselection');
'''
runtime = replace_once(runtime, railway_anchor, railway_anchor + railway_tests, "Issue 242 runtime fixtures")
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '        "function missionRequirementsResolve(candidate, parsed, catalogue = null)",\n',
    '        "function missionRequirementsReconcileCommittedDelta(requirement, baselineValue, selectedCapacity, respondingCapacity, onSiteCapacity)",\n        "function missionRequirementsResolve(candidate, parsed, catalogue = null)",\n',
    "contract helper marker",
)
contract = replace_once(
    contract,
    '        "data-personnel-training",\n',
    '        "data-personnel-training",\n        "data-education-key",\n        "data-filterable-by",\n',
    "explicit education metadata markers",
)
contract_anchor = '    assert re.search(r"(?:key|[\'\"]key[\'\"])\\s*:\\s*[\'\"]railway-police-officer[\'\"][^\\n]*(?:training|[\'\"]training[\'\"])\\s*:\\s*\\[[^\\]]*Railway Police", source), "Railway Police personnel must require explicit training evidence"\n'
contract_extra = '''    assert '"training":["Railway Police Officer","railway_police"]' in source, "Railway Police must use the explicit MissionChief education key"\n    assert "const inferredOnSite =" not in source, "baseline-minus-live delta must never be labelled On site"\n    assert "missionRequirementsReconcileCommittedDelta(requirement, baseline, selected, responding, onSite)" in source, "authoritative committed delta must be reconciled"\n    assert "const inferredSelectedMin" in source and "const inferredSelectedMax" in source, "committed delta must be allocated to Selected after operational capacity"\n    assert "if ((definition?.group || 'vehicles') === 'staff') continue" in source, "custom categories must not prove staff roles"\n    assert "const rowText = missionRequirementsCapabilityLabel" not in source, "generic row text must not become training evidence"\n'''
contract = replace_once(contract, contract_anchor, contract_anchor + contract_extra, "Issue 242 contract assertions")
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
section = """## [4.20.10] - 2026-07-20

### Fixed
- Corrected Railway Police Officer reconciliation when MissionChief's live missing count changes after personnel are selected.
- Mission Info baseline minus live missing demand is no longer falsely displayed as On-site capacity.
- After actual On-site and Responding capacity is accounted for, the remaining authoritative committed delta is displayed as Selected.
- Explicit `railway_police` education metadata is recognised while `railway_police_command` remains a separate Mobile Operations Manager qualification.
- Custom vehicle categories and generic vehicle-row text no longer prove role-specific personnel training.

### Validation
- Added deterministic Railway Police selected-delta, true On-site/Responding precedence, deselection, custom-category rejection and command-training separation fixtures.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + section, "v4.20.10 changelog")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8")
if "4.20.9" not in help_text:
    raise AssertionError("Help Centre has no v4.20.9 marker to reconcile")
HELP.write_text(help_text.replace("4.20.9", "4.20.10"), encoding="utf-8")

DOC.write_text("""# Issue #242 — Railway Police Officer capacity contract

Railway Policing uses MissionChief education key `railway_police`. The separate key `railway_police_command` represents Mobile Operations Manager and does not satisfy Railway Police Officer demand.

The Matrix treats canonical Vehicles on Scene and Units Responding rows as the only direct evidence for On-site and Responding state. It must not infer On-site personnel from the difference between Mission Info baseline and the live missing count.

When MissionChief's live missing requirement decreases after selection, the authoritative committed delta is reconciled in this order:

1. subtract actual On-site capacity;
2. subtract actual Responding capacity;
3. attribute the remainder to Selected.

Generic vehicle names, custom categories and row captions are not personnel-training evidence. Explicit education metadata may identify a qualification, but total vehicle crew is never assumed to equal the number holding that qualification.
""", encoding="utf-8")

subprocess.run(["node", ".github/scripts/test_mission_requirements_runtime.js"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_mission_requirements_contract.py"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/check_documentation_drift.py"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/test_documentation_version_states.py"], cwd=ROOT, check=True)
subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/MissionChief_Map_Command_Toolkit.user.js"], cwd=ROOT, check=True)
subprocess.run(["cmp", "--silent", "dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"], cwd=ROOT, check=True)
print("Railway Police Officer capacity v4.20.10 hotfix validated")
