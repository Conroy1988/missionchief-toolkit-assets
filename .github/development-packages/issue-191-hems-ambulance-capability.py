#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
SITE_DATA = ROOT / "docs" / "site-data.json"

PREVIOUS = "4.19.1"
VERSION = "4.19.2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {PREVIOUS}", f"// @version      {VERSION}", "metadata version")
source = replace_once(source, f"        version: '{PREVIOUS}',", f"        version: '{VERSION}',", "runtime version")
source = replace_once(
    source,
    "        { key: 'ambulance', label: 'Ambulance', aliases: ['Ambulance', 'Ambulances'], types: [5] },",
    "        { key: 'ambulance', label: 'Ambulance', aliases: ['Ambulance', 'Ambulances'], types: [5, 9] },",
    "HEMS ambulance capability inheritance",
)
SOURCE.write_text(source, encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.19.1'", "version: '4.19.2'", "runtime fixture version")
fixture_anchor = "const factorRequirement = { group: 'vehicles', definition: { types: [5], equipment: [], factors: { 5: 2 } } };"
fixture_block = """const ambulanceDefinition = api.definitions.find(item => item.key === 'ambulance');
const hemsDefinition = api.definitions.find(item => item.key === 'hems');
const selectedHemsUnit = { typeId: 9, equipment: new Set(), staff: null, contributionKey: 'vehicle:hems-9001' };
const duplicateSelectedHemsUnit = { ...selectedHemsUnit };
const selectedRoadAmbulance = { typeId: 5, equipment: new Set(), staff: null, contributionKey: 'vehicle:ambulance-5001' };
const hemsAsAmbulance = api.aggregate({ group: 'vehicles', definition: ambulanceDefinition }, [selectedHemsUnit]);
assert.strictEqual(hemsAsAmbulance.min, 1, 'selected HEMS contributes one Ambulance capability');
assert.strictEqual(hemsAsAmbulance.max, 1, 'selected HEMS has exact Ambulance capacity');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: hemsDefinition }, [selectedHemsUnit]).min, 1, 'selected HEMS retains HEMS capability');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: ambulanceDefinition }, [selectedHemsUnit, duplicateSelectedHemsUnit]).min, 1, 'same HEMS contribution key is not duplicated within the Ambulance row');
assert.strictEqual(api.aggregate({ group: 'vehicles', definition: hemsDefinition }, [selectedRoadAmbulance]).min, 0, 'road Ambulance does not satisfy HEMS');

"""
runtime = replace_once(runtime, fixture_anchor, fixture_block + fixture_anchor, "HEMS capability runtime fixtures")
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    "    assert re.search(r\"key:\\s*['\\\"]ambulance['\\\"][^\\n]*types:\\s*\\[5\\]\", source), \"patient demand must use the conservative UK transport ambulance mapping\"",
    "    assert re.search(r\"key:\\s*['\\\"]ambulance['\\\"][^\\n]*types:\\s*\\[5,\\s*9\\]\", source), \"Ambulance capability must include road Ambulance and HEMS vehicle types\"\n    assert re.search(r\"key:\\s*['\\\"]hems['\\\"][^\\n]*types:\\s*\\[9\\]\", source), \"HEMS must retain its dedicated capability mapping\"",
    "HEMS capability contract",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [Unreleased]

## [4.19.2] - 2026-07-19

### Fixed
- Classified HEMS as Ambulance-capable in the Mission Requirements Matrix, so a selected, responding or on-site HEMS now contributes one unit to the Ambulance row while retaining its HEMS capability.
- Preserved contribution-key de-duplication so the same HEMS cannot be counted twice within one requirement row, and normal road ambulances still do not satisfy HEMS requirements.

### Validation
- Added deterministic aggregate fixtures covering HEMS-to-Ambulance capability inheritance, retained HEMS capability, duplicate suppression and the one-way road-Ambulance boundary.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_index = HELP_INDEX.read_text(encoding="utf-8")
help_index = replace_once(help_index, "Guide for Toolkit v4.19.1", "Guide for Toolkit v4.19.2", "help guide version")
HELP_INDEX.write_text(help_index, encoding="utf-8")

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-19"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.19.2 makes HEMS contribute Ambulance capacity in every Mission Requirements unit state while retaining its dedicated HEMS capability and existing de-duplication."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Mission Requirements":
            details = feature.setdefault("details", [])
            detail = "HEMS contributes to both HEMS and Ambulance capacity without duplicate counting"
            if detail not in details:
                details.insert(2, detail)
SITE_DATA.write_text(json.dumps(site_data, indent=2) + "\n", encoding="utf-8")

Path(__file__).unlink(missing_ok=True)
print(f"Prepared Toolkit {VERSION} HEMS Ambulance-capability patch")
