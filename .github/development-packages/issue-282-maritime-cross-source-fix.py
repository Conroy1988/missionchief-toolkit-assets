#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src/data/mission-requirements-en_GB.json"
RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github/scripts/test_mission_requirements_contract.py"
AUDIT = ROOT / ".github/scripts/audit_lssm_requirement_compatibility.py"
CROSS_FIXTURE = ROOT / ".github/fixtures/mission-requirements-cross-source-en_GB.json"
WORKFLOW = ROOT / ".github/workflows/mission-requirements-cross-source-audit.yml"
DOC = ROOT / "docs/issue-282-cross-source-capability-audit.md"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"
DIST_JS = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TXT = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
SUMS = ROOT / "dist/SHA256SUMS.txt"
AUDIT_TEMPLATE = ROOT / ".github/development-packages/issue-282-audit-template.py"
WORKFLOW_TEMPLATE = ROOT / ".github/development-packages/issue-282-workflow-template.yml"
DOC_TEMPLATE = ROOT / ".github/development-packages/issue-282-doc-template.md"
PINNED_LSSM = "4f731e1d6d009cbf2129530fb31d10177b21a52a"
OLD_VERSION = "4.20.18"
NEW_VERSION = "4.20.19"

HELPER_CAPABILITY_KEYS = {
    "airport_command": "airfield-operations-supervisor",
    "airport_equipment": "airfield-operations-vehicle",
    "ambulances": "ambulance",
    "arff": "major-foam-tender",
    "atv_carrier": "atv-carrier",
    "battalion_chief_vehicles": "fire-officer",
    "bomb_disposal_command": "eod-commander",
    "bomb_disposal_crew": "eod-response-vehicle",
    "bomb_disposal_diver_crew": "marine-eod-response-vehicle",
    "bomb_disposal_diver_equipment": "marine-eod-equipment-van",
    "bomb_disposal_equipment": "eod-medium-equipment-van",
    "bomb_disposal_heavy_equipment": "eod-heavy-equipment-vehicle",
    "coastal_boat": "boat-trailer-or-inland-rescue-boat",
    "coastal_boat_hover": "hovercraft-trailer",
    "coastal_command": "coastguard-commander",
    "coastal_guard_boat": "alb",
    "coastal_helicopter": "coastguard-rescue-helicopter",
    "coastal_jetski": "rescue-watercraft-trailer",
    "coastal_mud_rescue": "coastguard-mud-rescue-unit",
    "coastal_rescue": "crv",
    "coastal_support": "support-unit",
    "elw_airport": "airfield-firefighting-command-vehicle",
    "emergency_welfare": "welfare-vehicle",
    "ems_mobile_command": "ambulance-officer",
    "firetrucks": "fire-engine",
    "flood_equipment": "flood-rescue-unit",
    "foam": "foam-unit",
    "hazard_response_primary": "primary-response-vehicle",
    "hazard_response_secondary": "secondary-response-vehicle",
    "hazmat_vehicles": "hazmat-unit-or-cbrn-vehicle",
    "heavy_rescue_vehicles": "rescue-support-unit-or-rescue-pump",
    "height_rescue_units": "coastguard-rope-rescue-unit",
    "helicopter": "hems",
    "k9": "dog-support-unit",
    "kdow_orgl": "operational-team-leader",
    "large_coastal_boat": "ilb",
    "mass_casualty_equipment": "mass-casualty-equipment",
    "midwife": "community-midwife",
    "mobile_air_vehicles": "basu",
    "mobile_command_vehicles": "iccu-or-ambulance-control-unit",
    "mud_rescue": "mud-decontamination-unit",
    "oneof_airport_fire_engine_or_engine_large": "riv-or-major-foam-tender",
    "oneof_coastal_guard_boat_or_boat_large": "ilb-or-alb",
    "oneof_fire_command_advanced_or_airport_fire_command": "iccu-or-ambulance-control-unit",
    "oneof_fire_command_or_airport_fire_command": "fire-officer",
    "oneof_fire_engine_or_airport_fire_engine": "fire-engine-or-riv",
    "oneof_fire_engine_or_airport_fire_engine_large": "fire-engine-or-major-foam-tender",
    "oneof_fire_engine_or_airport_fire_engine_or_engine_large": "fire-engine-riv-or-major-foam-tender",
    "oneof_fire_engine_or_rescue": "fire-engine-or-rescue-support-vehicle",
    "oneof_fire_engine_or_rescue_or_ladder": "fire-engine-rescue-support-vehicle-or-aerial-appliance-truck",
    "oneof_fire_ladder_or_rescue_stairs": "aerial-appliance-truck-or-rescue-stairs",
    "oneof_mountain_atv_or_search_and_rescue_atv": "mountain-rescue-4x4-or-sar-4x4",
    "oneof_paramedic_or_paramedic_advanced": "rrv-or-specialist-paramedic-rrv",
    "oneof_police_drone_or_helicopter": "police-helicopter-or-drone",
    "oneof_police_patrol_or_swat": "police-car-or-armed-response-vehicle",
    "platform_trucks": "aerial-appliance-truck",
    "police_cars": "police-car",
    "police_helicopters": "policehelicopter",
    "police_horse": "mounted-unit",
    "railway_police": "eiu",
    "rescue_dogs": "rescue-dog",
    "rettungstreppe": "rescue-stair",
    "riv": "riv",
    "rth": "hems",
    "search_and_rescue": "operational-support-van-trailer-or-personal-sar-vehicle",
    "search_and_rescue_command": "control-van",
    "swat_suv": "armed-response",
    "traffic_car": "traffic-car",
    "two_way": "road-rail-unit",
    "water_rescue": "4x4-vehicle",
    "water_tankers": "water-carrier",
}
REVIEWED_UNSUPPORTED_HELPER_TOKENS = {"mountain_cave_rescue"}
PARSER_REQUIRED_HELPER_TOKENS = {
    "coastal_boat",
    "coastal_guard_boat",
    "large_coastal_boat",
    "oneof_coastal_guard_boat_or_boat_large",
    "oneof_coastal_guard_boat_large_coastal_boat",
}
PAIR_DATA_KEYS = {
    "boat-trailer-or-inland-rescue-boat",
    "operational-support-van-trailer-or-personal-sar-vehicle",
    "rescue-watercraft-trailer",
    "hovercraft-trailer",
    "medical-equipment-trailer",
}


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def append_unique(values: list[str], additions: list[str]) -> None:
    folded = {re.sub(r"\s+", " ", value).strip().casefold() for value in values}
    for addition in additions:
        key = re.sub(r"\s+", " ", addition).strip().casefold()
        if key not in folded:
            values.append(addition)
            folded.add(key)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_caption(value: object) -> list[str]:
    return [part.strip() for part in str(value or "").split("|") if part.strip()]


def parse_vehicle_captions(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    captions: dict[str, str] = {}
    pattern = re.compile(r"^\s*(\d+):\s*\{[\s\S]*?^\s*caption:\s*'([^']+)'", re.MULTILINE)
    for match in pattern.finditer(text):
        captions[str(int(match.group(1)))] = match.group(2)
    return captions


def parse_tractive_map(source: str) -> dict[str, list[int]]:
    match = re.search(r"const MISSION_REQUIREMENTS_TRACTIVE_TYPES = Object\.freeze\((\{[^\n]+\})\);", source)
    if not match:
        raise RuntimeError("unable to parse tractive compatibility map")
    parsed = json.loads(match.group(1))
    return {str(key): [int(value) for value in values] for key, values in parsed.items()}


def capability_snapshot(entry: dict) -> dict:
    return {
        "key": entry["key"],
        "aliases": list(entry.get("aliases", [])),
        "types": [int(value) for value in entry.get("types", [])],
        "equipment": list(entry.get("equipment", [])),
        "conditionalVehicles": entry.get("conditionalVehicles", {}),
        "factors": entry.get("factors", {}),
        "pair": bool(entry.get("pair", False)),
    }


def build_cross_source_fixture(dataset: dict, source: str) -> dict:
    temporary = Path(tempfile.mkdtemp(prefix="issue-282-lssm-"))
    checkout = temporary / "LSSM-V.4"
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", "dev", "https://github.com/LSS-Manager/LSSM-V.4.git", str(checkout)],
            check=True,
        )
        actual_commit = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
        if actual_commit != PINNED_LSSM:
            raise RuntimeError(f"LSSM dev moved from reviewed commit {PINNED_LSSM} to {actual_commit}; stop for review")

        emv_path = checkout / "src/modules/extendedCallWindow/i18n/en_GB.json"
        helper_path = checkout / "src/modules/missionHelper/i18n/en_GB.json"
        vehicles_path = checkout / "src/i18n/en_GB/vehicles.ts"
        expected_hashes = {
            "emv": "ead0cb0e7f215ab843496d65ff90209044c736a08eeed6d5e19a312d775b5c8f",
            "missionHelper": "9c36aa6d408a432fea4169218a03ad3b4f8285c7",
            "vehicles": "76dac4116b0c8b85d73eb879ed9521c2acdad787360a174cddfedee2d9c96cd1",
        }
        actual_hashes = {"emv": sha256(emv_path), "missionHelper": sha256(helper_path), "vehicles": sha256(vehicles_path)}
        if actual_hashes != expected_hashes:
            raise RuntimeError(f"reviewed upstream file hashes changed: {actual_hashes}")

        helper = json.loads(helper_path.read_text(encoding="utf-8"))
        helper_captions = helper.get("vehicles", {}).get("captions", {})
        helper_tokens = set(helper_captions)
        missing_review = sorted(helper_tokens - set(HELPER_CAPABILITY_KEYS) - REVIEWED_UNSUPPORTED_HELPER_TOKENS)
        stale_review = sorted(set(HELPER_CAPABILITY_KEYS) - helper_tokens)
        if missing_review or stale_review:
            raise RuntimeError(f"Mission Helper mapping review incomplete: missing={missing_review}, stale={stale_review}")

        mappings = []
        for token, capability in sorted(HELPER_CAPABILITY_KEYS.items()):
            mappings.append({
                "source": "missionHelper.vehicles.captions",
                "token": token,
                "capability": capability,
                "labels": split_caption(helper_captions[token]),
                "requireParserAlias": token in PARSER_REQUIRED_HELPER_TOKENS,
            })
        prerequisite_label = helper.get("prerequisites", {}).get("oneof_coastal_guard_boat_large_coastal_boat")
        if not prerequisite_label:
            raise RuntimeError("Mission Helper maritime prerequisite caption is missing")
        mappings.append({
            "source": "missionHelper.prerequisites",
            "token": "oneof_coastal_guard_boat_large_coastal_boat",
            "capability": "ilb-or-alb",
            "labels": split_caption(prerequisite_label),
            "requireParserAlias": True,
        })

        entries = [*dataset.get("vehicleRequirements", []), *dataset.get("staffRequirements", [])]
        fixture = {
            "schemaVersion": 1,
            "locale": "en_GB",
            "pinnedLssmCommit": PINNED_LSSM,
            "files": {
                "emv": {"path": "src/modules/extendedCallWindow/i18n/en_GB.json", "sha256": actual_hashes["emv"]},
                "missionHelper": {"path": "src/modules/missionHelper/i18n/en_GB.json", "sha256": actual_hashes["missionHelper"]},
                "vehicles": {"path": "src/i18n/en_GB/vehicles.ts", "sha256": actual_hashes["vehicles"]},
            },
            "capabilities": [capability_snapshot(entry) for entry in entries],
            "authoritativeLabels": [
                {
                    "capability": "boat-trailer-or-inland-rescue-boat",
                    "canonicalLabel": "Inland Rescue Boat (Trailer)",
                    "labels": [
                        "Inland Rescue Boat (Trailer)",
                        "Inland Rescue Boats (Trailer)",
                        "Inland Rescue Boat (Trailers)",
                        "Inland Rescue Boats (Trailers)",
                    ],
                    "types": [67, 74],
                    "pair": True,
                    "sources": ["missionchief.missionInfo", "lssm.missionHelper", "lssm.vehicleCaption"],
                },
                {
                    "capability": "ilb-or-alb",
                    "canonicalLabel": "Seagoing Vessel",
                    "labels": ["Seagoing Vessel", "Seagoing Vessels"],
                    "types": [68, 69],
                    "pair": False,
                    "sources": ["missionchief.missionInfo"],
                },
            ],
            "missionHelperVehicleTokens": sorted(helper_tokens),
            "missionHelperVehicleCaptions": helper_captions,
            "missionHelperMappings": mappings,
            "reviewedUnsupportedMissionHelperTokens": sorted(REVIEWED_UNSUPPORTED_HELPER_TOKENS),
            "vehicleCaptions": parse_vehicle_captions(vehicles_path),
            "tractiveTypes": parse_tractive_map(source),
        }
        return fixture
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def main() -> int:
    for path in (AUDIT_TEMPLATE, WORKFLOW_TEMPLATE, DOC_TEMPLATE):
        if not path.exists():
            raise RuntimeError(f"missing reviewed template: {path.relative_to(ROOT)}")

    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    by_key = {entry["key"]: entry for entry in [*dataset["vehicleRequirements"], *dataset["staffRequirements"]]}
    inland = by_key["boat-trailer-or-inland-rescue-boat"]
    append_unique(inland["aliases"], [
        "Inland Rescue Boat (Trailer)",
        "Inland Rescue Boats (Trailer)",
        "Inland Rescue Boat (Trailers)",
        "Inland Rescue Boats (Trailers)",
    ])
    seagoing = by_key["ilb-or-alb"]
    append_unique(seagoing["aliases"], ["Seagoing Vessel", "Seagoing Vessels", "ALB or ILB", "ALBs or ILBs"])
    for key in PAIR_DATA_KEYS:
        by_key[key]["pair"] = True
    DATA.write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    source = SOURCE.read_text(encoding="utf-8")
    source = replace_once(source, f"// @version      {OLD_VERSION}", f"// @version      {NEW_VERSION}", "metadata version")
    source = replace_once(source, f"version: '{OLD_VERSION}'", f"version: '{NEW_VERSION}'", "runtime version")

    definition_marker = "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze("
    definition_start = source.find(definition_marker)
    definition_end = source.find(");", definition_start + len(definition_marker))
    if definition_start < 0 or definition_end < 0:
        raise RuntimeError("unable to locate embedded Mission Requirements definitions")
    payload_start = definition_start + len(definition_marker)
    definitions = json.loads(source[payload_start:definition_end])
    runtime_by_key = {entry["key"]: entry for entry in definitions}
    runtime_inland = runtime_by_key["boat-or-inland"]
    runtime_inland["label"] = "Inland Rescue Boat (Trailer)"
    append_unique(runtime_inland["aliases"], inland["aliases"])
    runtime_seagoing = runtime_by_key["ilb-or-alb"]
    runtime_seagoing["label"] = "Seagoing Vessel"
    append_unique(runtime_seagoing["aliases"], seagoing["aliases"])
    source = source[:payload_start] + json.dumps(definitions, separators=(",", ":"), ensure_ascii=False) + source[definition_end:]
    source = replace_once(
        source,
        "const tractiveEligible = compatibleTractiveTypes.length > 0 && compatibleTractiveTypes.every(type => definitionTypes.includes(type));",
        "const tractiveEligible = definition.pair !== true && compatibleTractiveTypes.length > 0 && compatibleTractiveTypes.every(type => definitionTypes.includes(type));",
        "pair-only tractive eligibility guard",
    )
    SOURCE.write_text(source, encoding="utf-8")

    cross_fixture = build_cross_source_fixture(dataset, source)
    CROSS_FIXTURE.write_text(json.dumps(cross_fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    runtime = RUNTIME_TEST.read_text(encoding="utf-8")
    runtime = replace_once(
        runtime,
        "const ukCapabilityFixture = JSON.parse(fs.readFileSync(path.join(root, 'src', 'data', 'mission-requirements-en_GB.json'), 'utf8'));",
        "const ukCapabilityFixture = JSON.parse(fs.readFileSync(path.join(root, 'src', 'data', 'mission-requirements-en_GB.json'), 'utf8'));\nconst crossSourceFixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-requirements-cross-source-en_GB.json'), 'utf8'));",
        "cross-source runtime fixture load",
    )
    runtime = runtime.replace("version: '4.20.17'", f"version: '{NEW_VERSION}'", 1)

    generic_anchor = "\nfor (const testCase of fixture.coverageCases) {"
    generic_block = r'''

// Issue #282: every accepted vehicle alias and eligible type executes through
// the production parser, aggregator and all three operational buckets.
for (const entry of ukCapabilityFixture.vehicleRequirements) {
    const firstAlias = entry.aliases[0];
    const parsed = api.parseText(`1 ${firstAlias}`, 'vehicles');
    const parsedRequirement = parsed.requirements.find(requirement => requirement.missing === 1);
    assert.ok(parsedRequirement, `runtime audit parses ${firstAlias}`);
    const definition = api.definitions.find(candidate => candidate.key === parsedRequirement.key && candidate.group === 'vehicles');
    assert.ok(definition, `runtime audit resolves ${entry.key}`);
    for (const typeId of entry.types) {
        const factor = Number(definition.factors?.[typeId] ?? definition.factors?.[String(typeId)] ?? 1);
        const expected = Number.isFinite(factor) && factor > 0 ? factor : 1;
        const unit = {
            typeId,
            vehicleId: 282000 + typeId,
            equipment: new Set(),
            labels: new Set(),
            training: new Set(),
            arrCapabilities: new Set(),
            arrCapabilityKnown: true,
            knownDefinitionKeys: new Set(),
            compatibleTractiveTypes: new Set(),
            staff: null,
            contributionKey: `vehicle:282-${entry.key}-${typeId}`
        };
        const capacity = api.aggregate({ group: 'vehicles', definition }, [unit]);
        assert.strictEqual(capacity.min, expected, `${entry.key}: type ${typeId} contributes expected minimum`);
        assert.strictEqual(capacity.max, expected, `${entry.key}: type ${typeId} contributes expected maximum`);
        const zero = api.capacity(0, 0, true);
        const required = api.capacity(expected, expected, true);
        for (const [bucket, selected, responding, onSite] of [
            ['selected', capacity, zero, zero],
            ['responding', zero, capacity, zero],
            ['on-site', zero, zero, capacity]
        ]) {
            const row = api.coverageRow(
                { key: definition.key, requirement: definition.label, missing: expected, group: 'vehicles', definition },
                selected,
                responding,
                onSite,
                required
            );
            assert.strictEqual(row.covered, true, `${entry.key}: type ${typeId} covers ${bucket}`);
            assert.strictEqual(row.stillNeededText, '0', `${entry.key}: type ${typeId} clears ${bucket}`);
        }
        const duplicate = api.aggregate({ group: 'vehicles', definition }, [unit, { ...unit }]);
        assert.strictEqual(duplicate.min, expected, `${entry.key}: duplicate contribution key is counted once`);
    }
    const ineligible = api.aggregate({ group: 'vehicles', definition }, [{
        typeId: 99999,
        vehicleId: 99999,
        equipment: new Set(),
        labels: new Set(),
        training: new Set(),
        arrCapabilities: new Set(),
        arrCapabilityKnown: true,
        knownDefinitionKeys: new Set(),
        compatibleTractiveTypes: new Set(),
        staff: null,
        contributionKey: `vehicle:ineligible-${entry.key}`
    }]);
    assert.strictEqual(ineligible.min, 0, `${entry.key}: ineligible type contributes zero`);
    assert.strictEqual(ineligible.max, 0, `${entry.key}: ineligible type is definitively excluded`);
}

for (const group of crossSourceFixture.authoritativeLabels) {
    for (const label of group.labels) {
        const parsed = api.parseText(`1 ${label}`, 'vehicles');
        const requirement = parsed.requirements.find(item => item.missing === 1);
        assert.ok(requirement, `authoritative label parses: ${label}`);
        assert.strictEqual(parsed.remaining, '', `authoritative label is consumed: ${label}`);
        for (const typeId of group.types) {
            assert.ok(requirement.definition.types.includes(typeId), `${label}: supports type ${typeId}`);
        }
    }
}
'''
    runtime = replace_once(runtime, generic_anchor, generic_block + generic_anchor, "generic runtime audit insertion")

    maritime_anchor = "\n\nconst issue169Doc = new FakeDocument();"
    maritime_block = r'''

// Issue #282: maritime authoritative labels, trailer identity and screenshot regression.
{
const maritimeDoc = new FakeDocument();
maritimeDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/282' } };
const inlandDefinition = api.definitions.find(definition => definition.key === 'boat-or-inland');
const seagoingDefinition = api.definitions.find(definition => definition.key === 'ilb-or-alb');
assert.strictEqual(inlandDefinition.label, 'Inland Rescue Boat (Trailer)', 'authoritative inland label is canonical');
assert.strictEqual(seagoingDefinition.label, 'Seagoing Vessel', 'authoritative seagoing label is canonical');

const zero = api.capacity(0, 0, true);
const one = api.capacity(1, 1, true);
const three = api.capacity(3, 3, true);
const inlandRequirement = { key: 'boat-or-inland', requirement: 'Inland Rescue Boat (Trailer)', missing: 3, group: 'vehicles', definition: inlandDefinition };
const screenshotRow = api.coverageRow(inlandRequirement, one, zero, zero, three);
assert.strictEqual(screenshotRow.covered, false, 'Required 3 with Selected 1 is not covered');
assert.strictEqual(screenshotRow.definitelyOpen, true, 'known maritime shortage is definitely open');
assert.strictEqual(screenshotRow.stillNeededText, '2', 'screenshot shortage remains two');
const screenshotPanel = api.panelHtml([screenshotRow], []);
assert(screenshotPanel.html.includes('1 outstanding · 0/1 covered'), 'screenshot summary reports zero covered');
assert(!screenshotPanel.html.includes('1/1 covered'), 'screenshot summary never reports the open row as covered');

const towOnlyUnit = {
    typeId: 66,
    vehicleId: 28201,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(),
    arrCapabilities: new Set(),
    arrCapabilityKnown: true,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set([67]),
    staff: null,
    contributionKey: 'pair:28201:28202'
};
const trailerUnit = {
    ...towOnlyUnit,
    typeId: 67,
    vehicleId: 28202,
    compatibleTractiveTypes: new Set(),
    contributionKey: 'pair:28201:28202'
};
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [towOnlyUnit]).min, 0, 'tow-only selection contributes no inland boat capacity');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [towOnlyUnit]).max, 0, 'tow-only exclusion is exact');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [towOnlyUnit, trailerUnit]).min, 1, 'trailer and tow pair contributes exactly one');
const randomTowOnly = { ...towOnlyUnit, compatibleTractiveTypes: new Set([67, 74]), contributionKey: 'vehicle:28203' };
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [randomTowOnly]).min, 0, 'random tractive compatibility cannot replace the maritime asset');

const maritimeCandidate = makeMissionCandidate(maritimeDoc, '3 Inland Rescue Boats (Trailer)');
const selected67 = makeVehicleElement(maritimeDoc, 28211, 67);
selected67.row.textContent = selected67.row.innerText = 'Custom Harbour Asset';
const responding74 = makeVehicleElement(maritimeDoc, 28212, 74, { typeOnRow: true });
responding74.row.setAttribute('data-vehicle-id', '28212');
const onSite67 = makeVehicleElement(maritimeDoc, 28213, 67, { typeOnRow: true });
onSite67.row.setAttribute('data-vehicle-id', '28213');
maritimeCandidate.root.selectedUnits = [selected67.vehicle];
maritimeCandidate.root.enRouteRows = [responding74.row];
maritimeCandidate.root.onSiteRows = [onSite67.row];
const inlandParsed = { requirements: [inlandRequirement], unresolved: [] };
const inlandCatalogue = { requirements: [{ key: 'boat-or-inland', baseline: 3, missing: 3 }] };
let maritimeRow = api.resolve(maritimeCandidate, inlandParsed, inlandCatalogue)[0];
assert.strictEqual(maritimeRow.selectedMin, 1, 'custom-caption type 67 selected capacity resolves');
assert.strictEqual(maritimeRow.respondingMin, 1, 'type 74 responding capacity resolves');
assert.strictEqual(maritimeRow.onSiteMin, 1, 'type 67 on-site capacity resolves');
assert.strictEqual(maritimeRow.stillNeededText, '0', 'mixed type 67/74 buckets satisfy quantity three');
assert.strictEqual(maritimeRow.covered, true, 'mixed maritime assets cover requirement');

const seagoingCandidate = makeMissionCandidate(maritimeDoc, '1 Seagoing Vessel');
const ilb = makeVehicleElement(maritimeDoc, 28221, 68);
const alb = makeVehicleElement(maritimeDoc, 28222, 69, { typeOnRow: true });
alb.row.setAttribute('data-vehicle-id', '28222');
const seagoingRequirement = { key: 'ilb-or-alb', requirement: 'Seagoing Vessel', missing: 1, group: 'vehicles', definition: seagoingDefinition };
const seagoingParsed = { requirements: [seagoingRequirement], unresolved: [] };
const seagoingCatalogue = { requirements: [{ key: 'ilb-or-alb', baseline: 1, missing: 1 }] };
seagoingCandidate.root.selectedUnits = [ilb.vehicle];
maritimeRow = api.resolve(seagoingCandidate, seagoingParsed, seagoingCatalogue)[0];
assert.strictEqual(maritimeRow.selectedMin, 1, 'selected ILB satisfies Seagoing Vessel');
assert.strictEqual(maritimeRow.stillNeededText, '0', 'selected ILB clears Seagoing Vessel');
seagoingCandidate.root.selectedUnits = [];
seagoingCandidate.root.enRouteRows = [alb.row];
maritimeRow = api.resolve(seagoingCandidate, seagoingParsed, seagoingCatalogue)[0];
assert.strictEqual(maritimeRow.respondingMin, 1, 'responding ALB satisfies Seagoing Vessel');
seagoingCandidate.root.enRouteRows = [];
seagoingCandidate.root.onSiteRows = [alb.row];
maritimeRow = api.resolve(seagoingCandidate, seagoingParsed, seagoingCatalogue)[0];
assert.strictEqual(maritimeRow.onSiteMin, 1, 'on-site ALB satisfies Seagoing Vessel');

const unknownMaritime = api.aggregate({ group: 'vehicles', definition: inlandDefinition }, [{
    typeId: -1,
    vehicleId: -1,
    equipment: new Set(),
    labels: new Set(),
    training: new Set(),
    arrCapabilities: new Set(),
    arrCapabilityKnown: false,
    knownDefinitionKeys: new Set(),
    compatibleTractiveTypes: new Set(),
    staff: null,
    contributionKey: 'element:unknown-maritime'
}]);
assert.strictEqual(unknownMaritime.min, 0, 'malformed maritime evidence contributes no confirmed capacity');
assert.strictEqual(unknownMaritime.max, null, 'malformed maritime evidence remains fail-closed');
}
'''
    runtime = replace_once(runtime, maritime_anchor, maritime_block + maritime_anchor, "maritime runtime fixture insertion")
    RUNTIME_TEST.write_text(runtime, encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    contract = replace_once(
        contract,
        'UK_CAPABILITY_FIXTURE = ROOT / "src/data/mission-requirements-en_GB.json"',
        'UK_CAPABILITY_FIXTURE = ROOT / "src/data/mission-requirements-en_GB.json"\nCROSS_SOURCE_FIXTURE = ROOT / ".github/fixtures/mission-requirements-cross-source-en_GB.json"\nCROSS_SOURCE_WORKFLOW = ROOT / ".github/workflows/mission-requirements-cross-source-audit.yml"',
        "cross-source contract constants",
    )
    contract = replace_once(
        contract,
        'uk_capabilities = json.loads(UK_CAPABILITY_FIXTURE.read_text(encoding="utf-8"))',
        'uk_capabilities = json.loads(UK_CAPABILITY_FIXTURE.read_text(encoding="utf-8"))\n    cross_source = json.loads(CROSS_SOURCE_FIXTURE.read_text(encoding="utf-8"))',
        "cross-source fixture load",
    )
    contract = replace_once(
        contract,
        'assert len(uk_capabilities["staffRequirements"]) >= 2',
        'assert len(uk_capabilities["staffRequirements"]) >= 2\n    assert cross_source["schemaVersion"] == 1\n    assert cross_source["locale"] == "en_GB"\n    assert cross_source["pinnedLssmCommit"] == "4f731e1d6d009cbf2129530fb31d10177b21a52a"\n    assert CROSS_SOURCE_WORKFLOW.exists()\n    assert any(group["canonicalLabel"] == "Inland Rescue Boat (Trailer)" for group in cross_source["authoritativeLabels"])\n    assert any(group["canonicalLabel"] == "Seagoing Vessel" for group in cross_source["authoritativeLabels"])',
        "cross-source fixture assertions",
    )
    contract = replace_once(
        '["python3", str(LSSM_COMPATIBILITY_AUDIT)]',
        '["python3", str(LSSM_COMPATIBILITY_AUDIT), "--skip-runtime"]',
        "avoid duplicate runtime audit",
    )
    contract = replace_once(
        '"MISSION_REQUIREMENTS_TRACTIVE_TYPES",',
        '"MISSION_REQUIREMENTS_TRACTIVE_TYPES",\n        "definition.pair !== true && compatibleTractiveTypes.length > 0",\n        "Inland Rescue Boat (Trailer)",\n        "Seagoing Vessel",',
        "cross-source source markers",
    )
    CONTRACT.write_text(contract, encoding="utf-8")

    AUDIT.write_text(AUDIT_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    WORKFLOW.write_text(WORKFLOW_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    DOC.write_text(DOC_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    release_notes = f'''## [{NEW_VERSION}] - 2026-07-21

### Fixed
- `Inland Rescue Boat (Trailer)` now resolves against reviewed UK maritime vehicle types 67 and 74 across Selected, Responding and On site.
- `Seagoing Vessel` now resolves against the ILB/ALB capability union, vehicle types 68 and 69.
- Compatible towing vehicles no longer satisfy trailer-capable requirements without the actual eligible trailer or maritime asset.
- Trailer and towing-vehicle pairs retain one contribution identity through dispatch and arrival transitions.
- A Required 3 / Selected 1 maritime row remains outstanding with Still needed 2 and reports `0/1 covered`.

### Audit
- Expanded the pinned LSSM compatibility audit across Enhanced Missing Vehicles, Mission Helper captions, UK vehicle captions and MissionChief authoritative labels.
- Added runtime-backed parser, Selected, Responding, On-site, ineligible-type and contribution-deduplication checks for every supported UK vehicle capability.
- Added a dedicated cross-source audit workflow with machine-readable and Markdown artefacts.

'''
    changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + release_notes, "changelog release insertion")
    CHANGELOG.write_text(changelog, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = replace_once(help_text, f"Guide for Toolkit v{OLD_VERSION}", f"Guide for Toolkit v{NEW_VERSION}", "help guide version")
    HELP.write_text(help_text, encoding="utf-8")

    for path in (
        ROOT / "docs/issue-282-maritime-source-inspection.txt",
        ROOT / "docs/issue-282-lssm-upstream-inspection.txt",
        AUDIT_TEMPLATE,
        WORKFLOW_TEMPLATE,
        DOC_TEMPLATE,
    ):
        path.unlink(missing_ok=True)

    raw = SOURCE.read_bytes()
    DIST_JS.write_bytes(raw)
    DIST_TXT.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    SUMS.write_text(f"{digest}  {DIST_JS.name}\n{digest}  {DIST_TXT.name}\n", encoding="utf-8")

    subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)
    subprocess.run(["node", "--check", str(SOURCE.relative_to(ROOT))], cwd=ROOT, check=True)
    subprocess.run(["bash", ".github/scripts/run_userscript_preflight.sh", "--contracts"], cwd=ROOT, check=True)
    with tempfile.TemporaryDirectory(prefix="issue-282-audit-output-") as temporary:
        subprocess.run([
            "python3", str(AUDIT.relative_to(ROOT)),
            "--json-output", str(Path(temporary) / "audit.json"),
            "--markdown-output", str(Path(temporary) / "audit.md"),
        ], cwd=ROOT, check=True)
    print(f"Issue #282 validated Toolkit {NEW_VERSION} candidate prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
