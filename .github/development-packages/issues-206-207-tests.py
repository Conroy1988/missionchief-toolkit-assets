#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CATALOGUE_FIXTURE = ROOT / ".github" / "fixtures" / "mission-catalogue-pages.json"

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = runtime.replace("version: '4.19.2'", "version: '4.20.3'", 1)
runtime = runtime.replace("    URLSearchParams,\n", "    URL,\n    URLSearchParams,\n", 1)
runtime = runtime.replace(
    "    equipmentTypes: missionRequirementsEquipmentTypes,\n",
    "    equipmentTypes: missionRequirementsEquipmentTypes,\n    metadataValues: missionRequirementsMetadataValues,\n    operationalSelectors: missionRequirementsOperationalSelectors,\n    operationalActive: missionRequirementsOperationalElementActive,\n    cataloguePersonnel: missionRequirementsCataloguePersonnelRequirements,\n",
    1,
)
runtime = runtime.replace(
    "const descriptorLink = { getAttribute(name) { return name === 'href' ? '/einsaetze/34?overlay_index=2' : null; } };",
    "const descriptorLink = { textContent: 'Requirements for this Mission', innerText: 'Requirements for this Mission', getAttribute(name) { return name === 'href' ? '/einsaetze/34?additive_overlays=7&overlay_index=2' : null; } };",
    1,
)
runtime = runtime.replace(
    "assert.deepStrictEqual(JSON.parse(JSON.stringify({ id: descriptor.id, overlayIndex: descriptor.overlayIndex, path: descriptor.path })), { id: 34, overlayIndex: 2, path: '/einsaetze/34?overlay_index=2' }, 'catalogue descriptor preserves mission variation');",
    "assert.deepStrictEqual(JSON.parse(JSON.stringify({ id: descriptor.id, overlayIndex: descriptor.overlayIndex, additiveOverlays: descriptor.additiveOverlays, path: descriptor.path })), { id: 34, overlayIndex: 2, additiveOverlays: ['7'], path: '/einsaetze/34?overlay_index=2&additive_overlays=7' }, 'catalogue descriptor preserves mission variation and additive overlays');",
    1,
)
fixture_block = r'''

// Issues #206 and #207: responding-unit acquisition and authoritative Fight on Train baseline.
{
const windowSelector = '#lightbox_box, #lightbox, .lightbox_content, .modal-body, .modal, [role="dialog"], .ui-dialog-content, .ui-dialog';
const issue206Doc = new FakeDocument();
issue206Doc.defaultView = { MutationObserver: FakeMutationObserver, location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk', pathname: '/missions/6206' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const issue206Candidate = makeMissionCandidate(issue206Doc, '2 Police cars');
issue206Candidate.missionId = 6206;
const issue206Window = new FakeElement('div', issue206Doc);
issue206Candidate.root.closestMap.set(windowSelector, issue206Window);
issue206Candidate.source.closestMap.set(windowSelector, issue206Window);
issue206Window.appendChild(issue206Candidate.root);
const issue206Police = makeVehicleElement(issue206Doc, 620601, 8, { typeOnRow: true });
issue206Police.row.matchSet.add('tr');
issue206Police.row.setAttribute('data-vehicle-id', '620601');
issue206Window.appendChild(issue206Police.row);
let issue206RespondingRows = [issue206Police.row];
issue206Window.queryAllHandler = selector => selector === 'tbody#mission_vehicle_driving > tr' ? issue206RespondingRows : [];
const issue206PoliceDefinition = api.definitions.find(definition => definition.key === 'police-car');
const issue206Parsed = { requirements: [{ key: 'police-car', requirement: 'Police Car', missing: 2, group: 'vehicles', definition: issue206PoliceDefinition }], unresolved: [] };
const issue206Catalogue = { requirements: [{ key: 'police-car', baseline: 2, missing: 2 }] };
let issue206Row = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(issue206Row.respondingMin, 1, 'tbody-ID responding table contributes one eligible Police Car');
assert.strictEqual(issue206Row.stillNeededText, '1', 'one responding Police Car reduces two required to one still needed');
issue206RespondingRows = [issue206Police.row, issue206Police.row];
issue206Row = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(issue206Row.respondingMin, 1, 'duplicate responding representation of one vehicle counts once');
issue206RespondingRows = [];
issue206Candidate.root.selectedUnits = [issue206Police.vehicle];
let transitionRow = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(transitionRow.selectedMin + transitionRow.respondingMin + transitionRow.onSiteMin, 1, 'Selected state fulfils one unit');
issue206Candidate.root.selectedUnits = [];
issue206RespondingRows = [issue206Police.row];
transitionRow = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(transitionRow.selectedMin + transitionRow.respondingMin + transitionRow.onSiteMin, 1, 'Selected to Responding preserves fulfilled capacity');
issue206RespondingRows = [];
issue206Candidate.root.onSiteRows = [issue206Police.row];
transitionRow = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(transitionRow.selectedMin + transitionRow.respondingMin + transitionRow.onSiteMin, 1, 'Responding to On site preserves fulfilled capacity');
issue206Candidate.root.onSiteRows = [];
const unknownRow = new FakeElement('tr', issue206Doc);
unknownRow.matchSet.add('tr');
const unknownVehicle = new FakeElement('a', issue206Doc);
unknownVehicle.setAttribute('data-vehicle-id', '620699');
unknownVehicle.closestMap.set('tr', unknownRow);
unknownRow.queryHandler = selector => selector.includes('data-vehicle-id') || selector.includes('/vehicles/') ? unknownVehicle : null;
issue206Window.appendChild(unknownRow);
issue206RespondingRows = [unknownRow];
issue206Row = api.resolve(issue206Candidate, issue206Parsed, issue206Catalogue)[0];
assert.strictEqual(issue206Row.uncertain, true, 'unclassified responding unit produces an amber bounded state instead of false red or green');
const railwayUnit = makeVehicleElement(issue206Doc, 620607, 116, { typeOnRow: true, staff: 4 });
railwayUnit.row.matchSet.add('tr');
railwayUnit.row.setAttribute('data-vehicle-id', '620607');
railwayUnit.row.setAttribute('data-current-personnel', '4');
railwayUnit.row.setAttribute('data-personnel-training', 'Railway Police Officer');
issue206Window.appendChild(railwayUnit.row);
issue206RespondingRows = [railwayUnit.row];
const railwayDefinition = api.definitions.find(definition => definition.key === 'railway-police-officer');
const railwayParsed = { requirements: [{ key: 'railway-police-officer', requirement: 'Railway Police Officer', missing: 8, group: 'staff', definition: railwayDefinition }], unresolved: [] };
const railwayCatalogue = { requirements: [{ key: 'railway-police-officer', baseline: 8, missing: 8 }] };
const railwayRow = api.resolve(issue206Candidate, railwayParsed, railwayCatalogue)[0];
assert.strictEqual(railwayRow.respondingMin, 4, 'responding trained Railway Police personnel contribute their current crew');
assert.strictEqual(railwayRow.stillNeededText, '4', 'four qualified responding personnel leave four still needed');

const fightCatalogue = parsedCatalogues.get('fight on train');
assert(fightCatalogue, 'Fight on Train authoritative fixture is parsed');
const fightQuantities = Object.fromEntries(fightCatalogue.requirements.map(item => [item.key, item.baseline]));
assert.strictEqual(fightQuantities['police-car'], 4, 'Fight on Train requires four Police Cars');
assert.strictEqual(fightQuantities.dsu, 1, 'Fight on Train requires one DSU');
assert.strictEqual(fightQuantities['railway-police-officer'], 8, 'Fight on Train requires eight Railway Police Officers from personnel metadata');
const fightCandidate = makeMissionCandidate(new FakeDocument(), '');
fightCandidate.root.ownerDocument.defaultView = { MutationObserver: FakeMutationObserver };
const fightParsed = api.reconcileCatalogue({ requirements: [], unresolved: [] }, fightCatalogue, 'ready', true);
const fightRows = api.resolve(fightCandidate, fightParsed, fightCatalogue);
assert.strictEqual(fightRows.find(item => item.key === 'police-car').requiredText, '4', 'authoritative Police Car baseline reaches Matrix');
assert.strictEqual(fightRows.find(item => item.key === 'dsu').requiredText, '1', 'authoritative DSU baseline reaches Matrix');
assert.strictEqual(fightRows.find(item => item.key === 'railway-police-officer').requiredText, '8', 'authoritative trained-personnel baseline reaches Matrix');
assert(!api.panelHtml(fightRows, fightParsed.unresolved).html.includes('No outstanding requirements'), 'authoritative Fight on Train data cannot render a false empty state');

const pendingDoc = new FakeDocument();
pendingDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { origin: 'https://www.missionchief.co.uk', protocol: 'https:', host: 'www.missionchief.co.uk', pathname: '/missions/6207' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const pendingCandidate = makeMissionCandidate(pendingDoc, '');
pendingCandidate.missionId = 6207;
const pendingLink = { textContent: 'Requirements for this Mission', innerText: 'Requirements for this Mission', getAttribute(name) { return name === 'href' ? '/einsaetze/465' : null; } };
const pendingOriginalQueryAll = pendingCandidate.root.queryAllHandler;
pendingCandidate.root.queryAllHandler = selector => selector === 'a[href*="/einsaetze/"]' ? [pendingLink] : pendingOriginalQueryAll(selector);
candidates = [pendingCandidate];
api.scan();
flushAnimationFrames();
const pendingRecord = api.records.get(pendingCandidate.source);
assert(pendingRecord.panel.innerHTML.includes('Requirements for this Mission could not be loaded'), 'unavailable authority renders unresolved amber content');
assert(!pendingRecord.panel.innerHTML.includes('No outstanding requirements reported by MissionChief'), 'empty live text cannot overwrite pending or failed authoritative source');
api.clear();
}
'''
runtime = runtime.replace("\nconsole.log('Mission requirements runtime fixtures passed');", fixture_block + "\nconsole.log('Mission requirements runtime fixtures passed');", 1)
RUNTIME.write_text(runtime, encoding="utf-8")

catalogue = json.loads(CATALOGUE_FIXTURE.read_text(encoding="utf-8"))
if not any(page.get("name") == "fight on train" for page in catalogue.get("pages", [])):
    catalogue.setdefault("index", []).append({"title": "Fight on Train", "href": "/einsaetze/465"})
    catalogue.setdefault("pages", []).append({
        "name": "fight on train",
        "sourceUrl": "https://www.missionchief.co.uk/einsaetze/465",
        "id": 465,
        "title": "Fight on Train",
        "sections": {
            "reward": [["Average credits", "2500"], ["Required Personnel Available", "8x Railway Police Officer"]],
            "requirements": [["Required Police Cars", "4"], ["Required Dog Support Units (DSUs)", "1"]],
            "other": []
        },
        "variations": [],
        "expected": {"police-car": 4, "dsu": 1, "railway-police-officer": 8}
    })
CATALOGUE_FIXTURE.write_text(json.dumps(catalogue, indent=2) + "\n", encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = contract.replace(
    '        "function missionRequirementsCollectUnits(candidate, mode)",\n',
    '        "function missionRequirementsCollectUnits(candidate, mode)",\n        "function missionRequirementsOperationalSelectors(mode)",\n        "tbody#mission_vehicle_driving > tr",\n        "function missionRequirementsMetadataValues(element, kind = \'labels\')",\n        "data-personnel-training",\n        "function missionRequirementsCataloguePersonnelRequirements(label, value)",\n        "additive_overlays",\n',
    1,
)
contract = contract.replace(
    '    assert "catalogueOnly && catalogueProbability < 100" in source, "probabilistic authoritative requirements must remain uncertain"\n',
    '    assert "catalogueOnly && catalogueProbability < 100" in source, "probabilistic authoritative requirements must remain uncertain"\n    assert re.search(r"key:\\s*[\'\\\"]railway-police-officer[\'\\\"][^\\n]*training:\\s*\\[[^\\]]*Railway Police", source), "Railway Police personnel must require explicit training evidence"\n    assert "!reconciled.requirements.length && !reconciled.unresolved.length" in source, "unresolved authority must not collapse to an empty success state"\n    assert "#mission_vehicle_driving > tr" in source and "tbody#mission_vehicle_driving > tr" in source\n',
    1,
)
CONTRACT.write_text(contract, encoding="utf-8")

print("Added v4.20.3 Matrix regression fixtures")
