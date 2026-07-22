#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src" / "data" / "mission-requirements-en_GB.json"
CROSS_SOURCE = ROOT / ".github" / "fixtures" / "mission-requirements-cross-source-en_GB.json"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
OLD_VERSION = "4.20.35"
NEW_VERSION = "4.20.36"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


# Canonical UK recovery capability.
data = json.loads(DATA.read_text(encoding="utf-8"))
vehicle_requirements = data["vehicleRequirements"]
if any(entry.get("key") == "car-recovery" for entry in vehicle_requirements):
    raise RuntimeError("car-recovery already exists in canonical capability data")
anchor_index = next(
    index for index, entry in enumerate(vehicle_requirements)
    if entry.get("key") == "mountain-rescue-4x4"
)
vehicle_requirements.insert(anchor_index + 1, {
    "key": "car-recovery",
    "aliases": ["car to tow", "cars to tow"],
    "types": [104, 105],
    "factors": {"105": 2},
})
DATA.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

# Runtime definition, strict semantic qualification badges, ARR refresh and version.
source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {OLD_VERSION}", f"// @version      {NEW_VERSION}", "userscript metadata version")
source = replace_once(source, f"version: '{OLD_VERSION}'", f"version: '{NEW_VERSION}'", "runtime version")

runtime_anchor = '{"key":"mountain-4x4","label":"Mountain Rescue 4x4","aliases":["Mountain Rescue 4x4","Mountain Rescue 4x4s"],"types":[99]},'
runtime_definition = '{"key":"car-recovery","label":"Car Recovery","aliases":["car to tow","cars to tow"],"types":[104,105],"factors":{"105":2}},'
source = replace_once(source, runtime_anchor, runtime_anchor + runtime_definition, "Car Recovery runtime definition")

# Only explicitly semantic training/education/schooling/qualification elements may
# contribute their title or exact text. Whole-row captions remain excluded.
direct_line_pattern = re.compile(r"^(\s*)function missionRequirementsDirectTrainingValues\(element\) \{.*\}$", re.MULTILINE)
direct_match = direct_line_pattern.search(source)
if not direct_match:
    raise RuntimeError("missionRequirementsDirectTrainingValues line not found")
indent = direct_match.group(1)
direct_replacement = indent + "function missionRequirementsDirectTrainingValues(element) { const values = new Set(); const add = raw => { const visit = value => { if (Array.isArray(value)) return value.forEach(visit); if (value && typeof value === 'object') return ['key', 'name', 'caption', 'title', 'education', 'training'].forEach(field => visit(value[field])); String(value || '').split(/[,;|]/u).map(missionRequirementsCapabilityLabel).filter(Boolean).forEach(value => values.add(value)); }; visit(raw); }; const attributes = ['data-personnel-training', 'data-training', 'data-trainings', 'data-education', 'data-educations', 'data-education-name', 'data-education-key', 'data-filterable-by']; for (const attribute of attributes) add(element?.getAttribute?.(attribute)); const semanticClass = String(element?.className || element?.getAttribute?.('class') || ''); if (/(?:^|[-_\\s])(?:personnel|training|education|schooling|qualification)(?:[-_\\s]|$)/iu.test(semanticClass)) for (const raw of [element?.getAttribute?.('title'), element?.getAttribute?.('aria-label'), element?.getAttribute?.('data-original-title'), element?.textContent, element?.innerText]) add(raw); return values; }"
source = source[:direct_match.start()] + direct_replacement + source[direct_match.end():]

old_training_selector = "const selector = '[data-personnel-training], [data-training], [data-trainings], [data-education], [data-educations], [data-education-name], [data-education-key], [data-filterable-by]';"
new_training_selector = "const selector = '[data-personnel-training], [data-training], [data-trainings], [data-education], [data-educations], [data-education-name], [data-education-key], [data-filterable-by], [class*=\"personnel\"], [class*=\"training\"], [class*=\"education\"], [class*=\"schooling\"], [class*=\"qualification\"]';"
source = replace_once(source, old_training_selector, new_training_selector, "specialist semantic badge selector")

change_listener = """        runtimeListen(doc, 'change', event => {
            if (!event.target?.matches?.('.vehicle_checkbox, input[type=\"checkbox\"][vehicle_type_id]')) return;
            missionRequirementsScheduleDocumentRecords(doc);
        }, true);
        const root = doc.documentElement || doc.body;"""
click_listener = """        runtimeListen(doc, 'change', event => {
            if (!event.target?.matches?.('.vehicle_checkbox, input[type=\"checkbox\"][vehicle_type_id]')) return;
            missionRequirementsScheduleDocumentRecords(doc);
        }, true); runtimeListen(doc, 'click', event => { if (!event.target?.closest?.('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]')) return; const refresh = () => missionRequirementsScheduleDocumentRecords(doc); runtimeRequestAnimationFrame(refresh); runtimeSetTimeout(refresh, 80); runtimeSetTimeout(refresh, 220); }, true);
        const root = doc.documentElement || doc.body;"""
source = replace_once(source, change_listener, click_listener, "ARR and vehicle-group deferred refresh")

SOURCE.write_text(source, encoding="utf-8")
for path in (
    ROOT / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "MissionChief_Map_Command_Toolkit.txt",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js",
    ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt",
):
    path.write_text(source, encoding="utf-8")

# Cross-source review: MissionChief-only operational label, ahead of pinned LSSM EMV aliases.
cross_source = json.loads(CROSS_SOURCE.read_text(encoding="utf-8"))
if any(item.get("capability") == "car-recovery" for item in cross_source["authoritativeLabels"]):
    raise RuntimeError("car-recovery authoritative label already exists")
cross_source["authoritativeLabels"].append({
    "canonicalLabel": "Car Recovery",
    "capability": "car-recovery",
    "labels": ["car to tow", "cars to tow"],
    "pair": False,
    "sources": ["missionchief.liveRequirements"],
    "types": [104, 105],
})
capabilities = cross_source["capabilities"]
if any(item.get("key") == "car-recovery" for item in capabilities):
    raise RuntimeError("car-recovery cross-source capability already exists")
capability_anchor = next(index for index, item in enumerate(capabilities) if item.get("key") == "mountain-rescue-4x4")
capabilities.insert(capability_anchor + 1, {
    "aliases": ["car to tow", "cars to tow"],
    "arrAttributes": [],
    "conditionalVehicles": {},
    "equipment": [],
    "factors": {"105": 2},
    "key": "car-recovery",
    "pair": False,
    "training": [],
    "types": [104, 105],
})
CROSS_SOURCE.write_text(json.dumps(cross_source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Exact Issue #353 regression: recovery capacity, specialist badge evidence and ARR refresh.
runtime_test = RUNTIME_TEST.read_text(encoding="utf-8")
issue353_test = r'''
// Issue #353: Non-Injury RTC with Police Car (Recovery Required).
const issue353RecoverySingular = api.parseText('1 car to tow', 'vehicles');
const issue353RecoveryPlural = api.parseText('2 cars to tow', 'vehicles');
assert.strictEqual(issue353RecoverySingular.requirements[0]?.key, 'car-recovery', 'car to tow resolves to Car Recovery');
assert.strictEqual(issue353RecoverySingular.requirements[0]?.requirement, 'Car Recovery', 'Matrix uses the canonical Car Recovery label');
assert.strictEqual(issue353RecoveryPlural.requirements[0]?.key, 'car-recovery', 'cars to tow resolves to Car Recovery');
assert.strictEqual(issue353RecoveryPlural.requirements[0]?.missing, 2, 'plural recovery quantity is preserved');
const issue353RecoveryDefinition = api.definitions.find(definition => definition.key === 'car-recovery');
assert(issue353RecoveryDefinition, 'Car Recovery definition exists');
assert.deepStrictEqual(JSON.parse(JSON.stringify(issue353RecoveryDefinition.types)), [104, 105]);
assert.strictEqual(Number(issue353RecoveryDefinition.factors?.[105] ?? issue353RecoveryDefinition.factors?.['105']), 2, 'Flatbed Recovery Vehicle contributes two cars');
const issue353RecoveryUnit = typeId => ({
    typeId,
    vehicleId: 353000 + typeId,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(),
    arrCapabilities: new Set(),
    arrCapabilityKnown: true,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set(),
    staff: null,
    contributionKey: `vehicle:353-recovery-${typeId}`
});
const issue353RecoveryRequirement = { key: 'car-recovery', requirement: 'Car Recovery', missing: 1, group: 'vehicles', definition: issue353RecoveryDefinition };
const issue353StandardRecovery = api.aggregate(issue353RecoveryRequirement, [issue353RecoveryUnit(104)]);
const issue353FlatbedRecovery = api.aggregate(issue353RecoveryRequirement, [issue353RecoveryUnit(105)]);
assert.strictEqual(issue353StandardRecovery.min, 1, 'Recovery Vehicle clears one car');
assert.strictEqual(issue353StandardRecovery.max, 1, 'Recovery Vehicle capacity is exact');
assert.strictEqual(issue353FlatbedRecovery.min, 2, 'Flatbed Recovery Vehicle clears two cars');
assert.strictEqual(issue353FlatbedRecovery.max, 2, 'Flatbed Recovery Vehicle capacity is exact');
for (const [bucket, selected, responding, onSite] of [
    ['selected', issue353StandardRecovery, api.capacity(0, 0, true), api.capacity(0, 0, true)],
    ['responding', api.capacity(0, 0, true), issue353StandardRecovery, api.capacity(0, 0, true)],
    ['on-site', api.capacity(0, 0, true), api.capacity(0, 0, true), issue353StandardRecovery]
]) {
    const row = api.coverageRow(issue353RecoveryRequirement, selected, responding, onSite, api.capacity(1, 1, true));
    assert.strictEqual(row.covered, true, `${bucket} Recovery Vehicle covers the requirement`);
    assert.strictEqual(row.stillNeededText, '0', `${bucket} Recovery Vehicle clears still needed`);
}
for (const typeId of [0, 8, 103, 106, 107]) {
    const capacity = api.aggregate(issue353RecoveryRequirement, [issue353RecoveryUnit(typeId)]);
    assert.strictEqual(capacity.min, 0, `type ${typeId} does not satisfy ordinary car recovery`);
    assert.strictEqual(capacity.max, 0, `type ${typeId} exclusion is exact`);
}

const issue353SergeantDefinition = api.definitions.find(definition => definition.key === 'police-sergeant-personnel');
assert(issue353SergeantDefinition, 'Police Sergeant specialist definition exists');
const issue353BadgeDoc = new FakeDocument();
const issue353BadgeRow = new FakeElement('tr', issue353BadgeDoc);
const issue353Badge = new FakeElement('span', issue353BadgeDoc);
issue353Badge.className = 'personnel-training-badge';
issue353Badge.textContent = issue353Badge.innerText = 'Police Sergeant';
issue353BadgeRow.appendChild(issue353Badge);
issue353BadgeRow.queryAllHandler = selector => selector.includes('[class*="training"]') ? [issue353Badge] : [];
const issue353BadgeCheckbox = new FakeElement('input', issue353BadgeDoc);
issue353BadgeCheckbox.closestMap.set('tr', issue353BadgeRow);
const issue353Qualified = api.qualifiedStaffCounts(null, -1, issue353BadgeCheckbox, { counts: new Map() });
assert.strictEqual(issue353Qualified.get('police-sergeant-personnel')?.min, 1, 'explicit selected training badge proves one Police Sergeant');
const issue353CaptionRow = new FakeElement('tr', issue353BadgeDoc);
const issue353Caption = new FakeElement('span', issue353BadgeDoc);
issue353Caption.className = 'vehicle-caption';
issue353Caption.textContent = issue353Caption.innerText = 'Police Sergeant';
issue353CaptionRow.queryAllHandler = () => [issue353Caption];
const issue353CaptionCheckbox = new FakeElement('input', issue353BadgeDoc);
issue353CaptionCheckbox.closestMap.set('tr', issue353CaptionRow);
const issue353CaptionOnly = api.qualifiedStaffCounts(null, -1, issue353CaptionCheckbox, { counts: new Map() });
assert.strictEqual(issue353CaptionOnly.has('police-sergeant-personnel'), false, 'caption-only Police Sergeant text is not qualification evidence');

const issue353RefreshDoc = new FakeDocument();
issue353RefreshDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/353' } };
api.observeDocument(issue353RefreshDoc);
const issue353ClickRegistration = listenedEvents.find(entry => entry.target === issue353RefreshDoc && entry.type === 'click');
assert(issue353ClickRegistration, 'Matrix registers delegated ARR refresh listener');
const issue353AaoControl = new FakeElement('a', issue353RefreshDoc);
const issue353AaoChild = new FakeElement('span', issue353RefreshDoc);
issue353AaoChild.closestMap.set('.aao_btn, [aao_id], .vehicle_group, [vehicle_group_id]', issue353AaoControl);
const issue353QueueBefore = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353AaoChild });
assert.strictEqual(animationQueue.length, issue353QueueBefore + 1, 'ARR click schedules a post-selection Matrix refresh');
const issue353Unrelated = new FakeElement('span', issue353RefreshDoc);
const issue353UnrelatedQueue = animationQueue.length;
issue353ClickRegistration.listener({ target: issue353Unrelated });
assert.strictEqual(animationQueue.length, issue353UnrelatedQueue, 'unrelated clicks do not schedule Matrix refreshes');
flushAnimationFrames();

'''
runtime_test = replace_once(
    runtime_test,
    "for (const group of crossSourceFixture.authoritativeLabels) {",
    issue353_test + "for (const group of crossSourceFixture.authoritativeLabels) {",
    "Issue #353 runtime regression insertion",
)
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

# Release documentation.
changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = f"""## [{NEW_VERSION}] - 2026-07-22

### Critical Mission Requirements fixes
- Added canonical `Car Recovery` handling for MissionChief's `car to tow` and `cars to tow` demand.
- Counted Recovery Vehicle type `104` as one car and Flatbed Recovery Vehicle type `105` as two cars; HGV Recovery Vehicle type `106` remains excluded from ordinary car recovery.
- Added deferred Matrix refresh after ARR and vehicle-group controls programmatically update selected vehicles.
- Added strict semantic specialist-training badge support so an explicitly labelled selected Police Sergeant can be counted without treating vehicle captions or generic Police Officers as qualified Sergeants.

### Benefit
- Recovery requirements now receive complete selected, responding, on-site and still-needed tracking.
- Police Sergeant selection updates immediately after native or ARR-driven vehicle selection.

### Compatibility
- Whole-row captions remain invalid specialist qualification evidence. Existing vehicle, personnel, mission-window, covered-row, theme, payout and notification behaviour is unchanged.

"""
changelog_path.write_text(replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog insertion"), encoding="utf-8")

help_path = ROOT / "help" / "index.html"
help_text = help_path.read_text(encoding="utf-8")
if OLD_VERSION not in help_text:
    raise RuntimeError("help page does not contain the current version")
help_path.write_text(help_text.replace(OLD_VERSION, NEW_VERSION), encoding="utf-8")

# Preserve permanent source-headroom arithmetic: all runtime additions stay on
# existing compact inventory/listener lines.
headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
source_lines = len(source.splitlines())
if source_lines != int(headroom["candidateSourceLines"]):
    raise RuntimeError(f"Issue #353 unexpectedly changed source line count: {source_lines} != {headroom['candidateSourceLines']}")
headroom["candidateVersion"] = NEW_VERSION
headroom["candidateSourceLines"] = source_lines
headroom["recoveredSourceLines"] = headroom["originalSourceLines"] - source_lines
headroom["candidateSourceSha256"] = hashlib.sha256(source.encode()).hexdigest()
headroom["invariant"] = (
    f'The reviewed compact stylesheet retains {headroom["recoveredSourceLines"]} recovered source lines '
    "while Car Recovery and ARR-driven specialist selection remain fixture-backed and managed runtime budgets remain unchanged."
)
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

# Focused contracts before repository-wide workflow validation.
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
subprocess.check_call(["node", str(RUNTIME_TEST)], cwd=ROOT, env=env)
subprocess.check_call([sys.executable, str(ROOT / ".github" / "scripts" / "audit_lssm_requirement_compatibility.py")], cwd=ROOT, env=env)
for cache in ROOT.rglob("__pycache__"):
    shutil.rmtree(cache, ignore_errors=True)

print(
    f"Prepared Toolkit {NEW_VERSION}; Car Recovery types=[104,105], factors={{105:2}}; "
    f"source lines={source_lines}; recovered={headroom['recoveredSourceLines']}"
)
