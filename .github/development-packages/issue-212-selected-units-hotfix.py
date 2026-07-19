#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise AssertionError(f"{label}: expected one exact anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
if "// @version      4.20.3" not in source or "version: '4.20.3'" not in source:
    raise AssertionError("Issue #212 package requires the verified v4.20.3 source")

start = source.index("function missionRequirementsOperationalSelectors")
end = source.index("function missionRequirementsMissionTypeId", start)
replacement = r'''function missionRequirementsOperationalSelectors(mode) { if (mode === 'selected') return ['#vehicle_show_table_body_all .vehicle_checkbox:checked, #occupied .vehicle_checkbox:checked, .vehicle_checkbox:checked']; if (mode === 'onsite') return ['#mission_vehicle_at_mission tbody tr', 'tbody#mission_vehicle_at_mission > tr', '#mission_vehicle_at_mission > tr', '[data-mcms-vehicle-state="onsite"]']; return ['#mission_vehicle_driving tbody tr', 'tbody#mission_vehicle_driving > tr', '#mission_vehicle_driving > tr', '[data-mcms-vehicle-state="responding"]']; }
function missionRequirementsOperationalWindowScopes(candidate, context = missionRequirementsPatientContext(candidate)) { const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog'; const scopes = []; const addChain = origin => { let current = origin?.closest?.(windowSelector) || null; while (current && !scopes.includes(current)) { scopes.push(current); const parent = current.parentElement || current.parentNode; current = parent?.closest?.(windowSelector) || null; } }; [candidate?.root, candidate?.mount, candidate?.source, missionRequirementsCandidateRoot(candidate), context?.activeWindow].forEach(addChain); if (context?.activeWindow && !scopes.includes(context.activeWindow)) scopes.unshift(context.activeWindow); return scopes; }
function missionRequirementsOperationalElementActive(element, candidate, context = missionRequirementsPatientContext(candidate), mode = '') { if (!element || element.isConnected === false) return false; if (mode !== 'selected' && !isVisible(element)) return false; if (mode === 'selected' && typeof element.checked === 'boolean' && !element.checked) return false; const row = element.matches?.('tr') ? element : element.closest?.('tr') || element; if (context.activeWindow && !(context.activeWindow === row || context.activeWindow.contains?.(row) || row.closest?.('#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog') === context.activeWindow)) return false; const expectedMission = missionRequirementsMissionIdentity(candidate, candidate?.source); const explicitMission = missionRequirementsOptionalNumber(row?.getAttribute?.('data-mission-id') ?? row?.dataset?.missionId); if (expectedMission > 0 && explicitMission !== null && explicitMission !== expectedMission) return false; const missionRoot = row.closest?.('#mission_form, form[action*="/missions/"], #mission_content, .mission_content, [data-mission-content]'); if (expectedMission > 0 && missionRoot) { const actualMission = missionRequirementsMissionIdentity({ root: missionRoot, mount: missionRoot }, null); if (actualMission > 0 && actualMission !== expectedMission) return false; } return true; }
function missionRequirementsCollectUnits(candidate, mode) { const root = candidate?.root; const context = missionRequirementsPatientContext(candidate); const doc = context.doc || candidate?.source?.ownerDocument || root?.ownerDocument; if (!root?.querySelectorAll && !doc?.querySelectorAll) return []; const selectors = missionRequirementsOperationalSelectors(mode); const windowScopes = missionRequirementsOperationalWindowScopes(candidate, context); const anchorSelector = mode === 'selected' ? '#vehicle_show_table_body_all, #occupied, .vehicle_checkbox' : mode === 'onsite' ? '#mission_vehicle_at_mission, [data-mcms-vehicle-state="onsite"]' : '#mission_vehicle_driving, [data-mcms-vehicle-state="responding"]'; let activeWindow = context.activeWindow || null; for (const scope of windowScopes) { if (scope?.querySelector?.(anchorSelector)) { activeWindow = scope; break; } } const operationalContext = { ...context, activeWindow }; const elements = []; const seenElements = new Set(); const localScopes = Array.from(new Set([root, candidate?.mount, activeWindow, ...windowScopes].filter(scope => scope?.querySelectorAll))); const search = scope => { for (const selector of selectors) { for (const element of Array.from(scope?.querySelectorAll?.(selector) || [])) { if (seenElements.has(element) || !missionRequirementsOperationalElementActive(element, candidate, operationalContext, mode)) continue; seenElements.add(element); elements.push(element); } } }; localScopes.forEach(search); if (!elements.length && doc?.querySelectorAll && !localScopes.includes(doc)) search(doc); const units = new Map(); elements.forEach((element, index) => { const row = element.matches?.('tr') ? element : element.closest?.('tr'); const vehicleElement = mode === 'selected' ? element : (element.querySelector?.('[vehicle_type_id], [data-vehicle-type-id], [data-vehicle_type_id], [data-vehicle-id], a[href*="/vehicles/"]') || element); const typeId = missionRequirementsVehicleType(vehicleElement); const vehicleId = missionRequirementsVehicleId(vehicleElement); const tractiveId = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('tractive_vehicle_id') ?? vehicleElement?.getAttribute?.('data-tractive-vehicle-id') ?? row?.getAttribute?.('tractive_vehicle_id') ?? row?.getAttribute?.('data-tractive-vehicle-id') ?? row?.dataset?.tractiveVehicleId); const trailerId = missionRequirementsOptionalNumber(vehicleElement?.getAttribute?.('trailer_id') ?? vehicleElement?.getAttribute?.('data-trailer-id') ?? row?.getAttribute?.('trailer_id') ?? row?.getAttribute?.('data-trailer-id') ?? row?.dataset?.trailerId); let contributionKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : `element:${index}`; const pairedId = tractiveId !== null && tractiveId >= 0 ? tractiveId : trailerId; if (vehicleId >= 0 && pairedId !== null && pairedId >= 0) contributionKey = `pair:${Math.min(vehicleId, pairedId)}:${Math.max(vehicleId, pairedId)}`; const identityKey = vehicleId >= 0 ? `vehicle:${vehicleId}` : contributionKey; const labels = missionRequirementsMetadataValues(vehicleElement, 'labels'); const training = missionRequirementsMetadataValues(vehicleElement, 'training'); const knownDefinitionKeys = missionRequirementsKnownDefinitionKeys(labels); const rowText = missionRequirementsCapabilityLabel(`${row?.textContent || ''} ${row?.innerText || ''}`); if (rowText) { for (const definition of MISSION_REQUIREMENT_DEFINITIONS) { const aliases = Array.from(definition?.training || []).map(missionRequirementsCapabilityLabel).filter(Boolean); if (!aliases.some(alias => rowText.includes(alias))) continue; aliases.forEach(alias => training.add(alias)); knownDefinitionKeys.add(definition.key); } } const unit = { typeId, vehicleId, tractiveId, equipment: missionRequirementsEquipmentTypes(vehicleElement), staff: missionRequirementsStaffCapacity(vehicleElement), labels, training, knownDefinitionKeys, contributionKey }; const existing = units.get(identityKey); if (!existing) { units.set(identityKey, unit); return; } if (existing.typeId < 0 && unit.typeId >= 0) existing.typeId = unit.typeId; for (const equipment of unit.equipment) existing.equipment.add(equipment); for (const label of unit.labels) existing.labels.add(label); for (const qualification of unit.training) existing.training.add(qualification); for (const key of unit.knownDefinitionKeys) existing.knownDefinitionKeys.add(key); if ((!existing.staff || !existing.staff.known) && unit.staff?.known) existing.staff = unit.staff; if (existing.contributionKey.startsWith('element:') && !unit.contributionKey.startsWith('element:')) existing.contributionKey = unit.contributionKey; }); return Array.from(units.values()); }

    '''
source = source[:start] + replacement + source[end:]
source = replace_once(source, "// @version      4.20.3", "// @version      4.20.4", "userscript metadata version")
source = replace_once(source, "version: '4.20.3'", "version: '4.20.4'", "runtime version")
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME_TEST.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.20.3'", "version: '4.20.4'", "runtime fixture version")
runtime = replace_once(runtime, "    get firstChild() { return this.children[0] || null; }\n", "    get firstChild() { return this.children[0] || null; }\n    get parentElement() { return this.parentNode?.tagName ? this.parentNode : null; }\n", "FakeElement parentElement")
fixture_anchor = "assert.strictEqual(policeResolved.selectedMin, 1, 'deselecting one police car updates Selected back to one');\n"
fixture = r'''

// Issue #212: checked Available Units can be siblings of the narrow mission content root.
{
const issue212Doc = new FakeDocument();
issue212Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk', pathname: '/missions/21201' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const issue212Candidate = makeMissionCandidate(issue212Doc, '');
issue212Candidate.missionId = 21201;
const issue212WindowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
const issue212OuterWindow = new FakeElement('div', issue212Doc);
issue212OuterWindow.id = 'lightbox_box';
const issue212InnerWindow = new FakeElement('div', issue212Doc);
issue212InnerWindow.className = 'lightbox_content';
issue212OuterWindow.closestMap.set(issue212WindowSelector, issue212OuterWindow);
issue212InnerWindow.closestMap.set(issue212WindowSelector, issue212InnerWindow);
issue212Candidate.root.closestMap.set(issue212WindowSelector, issue212InnerWindow);
issue212Candidate.source.closestMap.set(issue212WindowSelector, issue212InnerWindow);
issue212Doc.body.appendChild(issue212OuterWindow);
issue212OuterWindow.appendChild(issue212InnerWindow);
issue212InnerWindow.appendChild(issue212Candidate.root);
const issue212Available = new FakeElement('tbody', issue212Doc);
issue212Available.id = 'vehicle_show_table_body_all';
issue212OuterWindow.appendChild(issue212Available);
const issue212Police = makeVehicleElement(issue212Doc, 212011, 8, { typeOnRow: true });
const issue212DsuDefinition = api.definitions.find(definition => definition.key === 'dsu');
const issue212Dsu = makeVehicleElement(issue212Doc, 212012, issue212DsuDefinition.types[0], { typeOnRow: true });
const issue212Railway = makeVehicleElement(issue212Doc, 212013, 116, { typeOnRow: true, staff: 2 });
for (const item of [issue212Police, issue212Dsu, issue212Railway]) {
    item.vehicle.checked = true;
    item.vehicle._visible = false;
    item.row.appendChild(item.vehicle);
    issue212Available.appendChild(item.row);
}
issue212Railway.row.setAttribute('data-current-personnel', '2');
issue212Railway.row.textContent = issue212Railway.row.innerText = 'Craigleith Railway-PC-5 [Railway Police Officer]';
let issue212Selected = [issue212Police.vehicle, issue212Dsu.vehicle, issue212Railway.vehicle];
issue212OuterWindow.queryHandler = selector => selector.includes('#vehicle_show_table_body_all') || selector.includes('.vehicle_checkbox') ? issue212Available : null;
issue212OuterWindow.queryAllHandler = selector => selector.includes('.vehicle_checkbox:checked') ? issue212Selected : [];
const issue212Requirements = [
    ['police-car', 'Police Car', 4],
    ['dsu', 'Dog Support Unit (DSU)', 1],
    ['railway-police-officer', 'Railway Police Officer', 8]
].map(([key, requirement, missing]) => ({ key, requirement, missing, group: key === 'railway-police-officer' ? 'staff' : 'vehicles', definition: api.definitions.find(item => item.key === key) }));
const issue212Parsed = { requirements: issue212Requirements, unresolved: [] };
const issue212Catalogue = { requirements: issue212Requirements.map(item => ({ key: item.key, baseline: item.missing, missing: item.missing })) };
let issue212Rows = api.resolve(issue212Candidate, issue212Parsed, issue212Catalogue);
assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 1, 'outer Available Units Police Car is selected');
assert.strictEqual(issue212Rows.find(item => item.key === 'dsu').selectedMin, 1, 'outer Available Units DSU is selected');
assert.strictEqual(issue212Rows.find(item => item.key === 'railway-police-officer').selectedMin, 2, 'Railway Police badge and current crew contribute selected trained personnel');
issue212Police.vehicle.checked = false;
issue212Selected = [issue212Dsu.vehicle, issue212Railway.vehicle];
issue212Rows = api.resolve(issue212Candidate, issue212Parsed, issue212Catalogue);
assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 0, 'deselecting the outer-window Police Car immediately clears Selected');
assert.strictEqual(issue212Rows.find(item => item.key === 'dsu').selectedMin, 1, 'other selected units remain stable after deselection');
}
'''
runtime = replace_once(runtime, fixture_anchor, fixture_anchor + fixture, "Issue #212 runtime fixture anchor")
RUNTIME_TEST.write_text(runtime, encoding="utf-8")

contract = CONTRACT_TEST.read_text(encoding="utf-8")
contract = replace_once(contract, '        "function missionRequirementsOperationalSelectors(mode)",\n', '        "function missionRequirementsOperationalSelectors(mode)",\n        "function missionRequirementsOperationalWindowScopes(candidate, context = missionRequirementsPatientContext(candidate))",\n        "mode !== \'selected\' && !isVisible(element)",\n        "missionRequirementsOperationalElementActive(element, candidate, operationalContext, mode)",\n', "Issue #212 contract markers")
contract = replace_once(contract, '    assert "#mission_vehicle_driving > tr" in source and "tbody#mission_vehicle_driving > tr" in source\n', '    assert "#mission_vehicle_driving > tr" in source and "tbody#mission_vehicle_driving > tr" in source\n    assert "#vehicle_show_table_body_all, #occupied, .vehicle_checkbox" in source, "selected-unit scope must locate the Available Units container"\n    assert "missionRequirementsOperationalWindowScopes(candidate, context)" in source, "selected-unit acquisition must expand beyond the narrow mission root"\n', "Issue #212 contract assertions")
CONTRACT_TEST.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [4.20.4] - 2026-07-19\n\n### Fixed\n- Restored live **Selected** counts when MissionChief renders **Available Units** outside the nested mission content root but inside the same active lightbox.\n- Selected Police Cars, Dog Support Units and trained Railway Police crew now contribute immediately, including hidden duplicate table representations, while vehicle-ID de-duplication and mission-window isolation remain intact.\n- Added visible-row training badge fallback so `[Railway Police Officer]` personnel labels contribute their current selected crew when MissionChief does not expose a dedicated training attribute.\n\n### Validation\n- Added deterministic nested-lightbox fixtures covering sibling Available Units tables, checked-but-hidden checkbox representations, Police Car/DSU/Railway Police classification and live deselection.\n\n"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "v4.20.4 changelog")
CHANGELOG.write_text(changelog, encoding="utf-8")

for diagnostic in [
    ROOT / ".github" / "diagnostics" / "issue-212-selected-runtime.txt",
    ROOT / ".github" / "diagnostics" / "issue-212-observer-runtime.txt",
]:
    diagnostic.unlink(missing_ok=True)

subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
subprocess.run(["node", ".github/scripts/test_mission_requirements_runtime.js"], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/test_mission_requirements_contract.py"], cwd=ROOT, check=True)
subprocess.run([sys.executable, ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)

if SOURCE.stat().st_size > 3_000_000:
    raise AssertionError("v4.20.4 exceeds the owner-authorized 3,000,000-byte source ceiling")
if len(SOURCE.read_text(encoding="utf-8").splitlines()) > 32_000:
    raise AssertionError("v4.20.4 exceeds the 32,000-line source ceiling")

Path(__file__).unlink()
print("Prepared v4.20.4 selected-unit hotfix with full validation")
