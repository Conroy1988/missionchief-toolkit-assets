#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD_VERSION = "4.20.14"
NEW_VERSION = "4.20.15"

SOURCE_PATH = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA_PATH = ROOT / "src/data/mission-requirements-en_GB.json"
RUNTIME_TEST_PATH = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CATALOGUE_FIXTURE_PATH = ROOT / ".github/fixtures/mission-catalogue-pages.json"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
HELP_PATH = ROOT / "help/index.html"
DIST_USER_PATH = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT_PATH = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
SHA_PATH = ROOT / "dist/SHA256SUMS.txt"
MANIFEST_PATH = ROOT / "dist/release-manifest.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def append_aliases(entry: dict, aliases: list[str]) -> None:
    existing = entry.setdefault("aliases", [])
    folded = {str(value).casefold() for value in existing}
    for alias in aliases:
        if alias.casefold() not in folded:
            existing.append(alias)
            folded.add(alias.casefold())


def update_definitions(source: str) -> str:
    marker = "const MISSION_REQUIREMENT_DEFINITIONS = Object.freeze("
    marker_index = source.index(marker)
    json_start = marker_index + len(marker)
    json_end = source.index(");", json_start)
    definitions = json.loads(source[json_start:json_end])
    primary = 0
    secondary = 0
    for definition in definitions:
        key = str(definition.get("key", ""))
        label = str(definition.get("label", ""))
        if key in {"primary-response", "primary-response-vehicle"} or label == "Primary Response Vehicle":
            append_aliases(definition, ["PRV", "PRVs"])
            primary += 1
        if key in {"secondary-response", "secondary-response-vehicle"} or label == "Secondary Response Vehicle":
            append_aliases(definition, ["SRV", "SRVs"])
            secondary += 1
    if primary < 1 or secondary < 1:
        raise RuntimeError(f"canonical PRV/SRV definitions not found: primary={primary}, secondary={secondary}")
    encoded = json.dumps(definitions, separators=(",", ":"), ensure_ascii=False)
    return source[:json_start] + encoded + source[json_end:]


def main() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    source = replace_once(source, f"// @version      {OLD_VERSION}", f"// @version      {NEW_VERSION}", "metadata version")
    source = replace_once(source, f"version: '{OLD_VERSION}'", f"version: '{NEW_VERSION}'", "runtime version")
    source = update_definitions(source)

    staff_ranges = {
        0: [1, 9], 1: [1, 5], 2: [1, 3], 3: [1, 3], 4: [1, 5],
        5: [1, 2], 6: [1, 3], 7: [1, 6], 8: [1, 2], 9: [3, 5],
        12: [1, 2], 13: [1, 4], 14: [1, 3], 15: [1, 6], 16: [1, 9],
        17: [1, 6], 18: [1, 1], 19: [1, 3], 20: [1, 1], 23: [1, 12],
        24: [1, 2], 25: [1, 2], 26: [1, 3], 27: [1, 2], 28: [1, 2],
        31: [1, 2], 34: [1, 1], 35: [1, 2], 36: [1, 2], 37: [2, 9],
        38: [2, 9], 39: [1, 6], 40: [1, 2], 51: [1, 9], 52: [1, 9],
        53: [1, 4], 55: [1, 8], 56: [1, 6], 81: [0, 0], 82: [1, 2],
        83: [1, 1], 86: [1, 3], 87: [0, 0], 92: [1, 1], 93: [1, 1],
        95: [1, 2], 96: [1, 2], 99: [1, 4], 101: [1, 1], 102: [1, 1],
        116: [1, 5],
    }
    staff_json = json.dumps(staff_ranges, separators=(",", ":"))
    staff_marker = "function missionRequirementsStaffCapacity(element) {"
    staff_runtime = (
        f"const MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE = Object.freeze({staff_json});\n"
        "function missionRequirementsDefaultStaffCapacity(typeId, element = null) { const range = MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE[typeId] || MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE[String(typeId)]; if (!Array.isArray(range) || range.length < 2) return null; const row = element?.closest?.('tr') || element; const scopes = Array.from(new Set([element, row].filter(Boolean))); const overrideAttributes = ['data-max-personnel-override', 'data-personnel-max-override', 'data-max-crew-override']; let maximumOverride = null; for (const scope of scopes) { for (const attribute of overrideAttributes) { const value = missionRequirementsOptionalNumber(scope?.getAttribute?.(attribute)); if (value !== null) { maximumOverride = value; break; } } if (maximumOverride !== null) break; } const minimum = Math.max(0, Number(range[0]) || 0); const configuredMaximum = Math.max(minimum, Number(range[1]) || 0); const maximum = maximumOverride === null ? configuredMaximum : Math.max(minimum, maximumOverride); return missionRequirementsCapacity(minimum, maximum, minimum === maximum); }\n"
    )
    if "MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE" in source:
        raise RuntimeError("default staff range runtime already exists")
    source = replace_once(source, staff_marker, staff_runtime + staff_marker, "staff fallback insertion")
    source = replace_once(
        source,
        "staff: missionRequirementsStaffCapacity(vehicleElement),",
        "staff: missionRequirementsStaffCapacity(vehicleElement) || missionRequirementsDefaultStaffCapacity(typeId, vehicleElement),",
        "unit staff fallback",
    )
    source = replace_once(
        source,
        "return { eligible: true, unknown: !capacity.known, capacity };",
        "return { eligible: true, unknown: capacity.max === null, capacity };",
        "bounded staff contribution",
    )
    SOURCE_PATH.write_text(source, encoding="utf-8")

    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    found_primary = found_secondary = False
    for entry in dataset.get("vehicleRequirements", []):
        if entry.get("key") == "primary-response-vehicle":
            append_aliases(entry, ["PRV", "PRVs"])
            found_primary = True
        if entry.get("key") == "secondary-response-vehicle":
            append_aliases(entry, ["SRV", "SRVs"])
            found_secondary = True
    if not found_primary or not found_secondary:
        raise RuntimeError("UK PRV/SRV dataset entries not found")
    DATA_PATH.write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    runtime_test = RUNTIME_TEST_PATH.read_text(encoding="utf-8")
    runtime_test = replace_once(runtime_test, f"version: '{OLD_VERSION}'", f"version: '{NEW_VERSION}'", "runtime fixture version")
    runtime_test = replace_once(
        runtime_test,
        "    staffCapacity: missionRequirementsStaffCapacity,\n    equipmentTypes: missionRequirementsEquipmentTypes,",
        "    staffCapacity: missionRequirementsStaffCapacity,\n    defaultStaffCapacity: missionRequirementsDefaultStaffCapacity,\n    equipmentTypes: missionRequirementsEquipmentTypes,",
        "runtime API export",
    )
    regression_marker = "const factorRequirement = { group: 'vehicles', definition: { types: [5], equipment: [], factors: { 5: 2 } } };"
    regression = r'''
// Issue #269: generic staff requirements inherit reviewed vehicle-type crew ranges when native rows expose no crew field.
{
const policeStaff = api.defaultStaffCapacity(8, null);
assert.deepStrictEqual(JSON.parse(JSON.stringify(policeStaff)), { min: 1, max: 2, known: false, value: 1 }, 'Police Car type fallback exposes one-to-two officers');
const policeOverrideElement = {
    getAttribute(name) { return name === 'data-max-personnel-override' ? '1' : null; },
    closest() { return null; }
};
assert.deepStrictEqual(JSON.parse(JSON.stringify(api.defaultStaffCapacity(8, policeOverrideElement))), { min: 1, max: 1, known: true, value: 1 }, 'native maximum-personnel override narrows the type range');
const policeOfficersDefinition = api.definitions.find(item => item.key === 'police-officers');
const policeCrewUnit = { typeId: 8, equipment: new Set(), labels: new Set(), training: new Set(), knownDefinitionKeys: new Set(), staff: policeStaff, contributionKey: 'vehicle:26901' };
const policeCrewCapacity = api.aggregate({ group: 'staff', definition: policeOfficersDefinition }, [policeCrewUnit]);
assert.strictEqual(policeCrewCapacity.min, 1, 'selected Police Car contributes at least one Police Officer');
assert.strictEqual(policeCrewCapacity.max, 2, 'selected Police Car preserves the reviewed maximum crew range');
const policeCrewCoverage = api.coverageRow(
    { key: 'police-officers', requirement: 'Police Officers', missing: 1, group: 'staff', definition: policeOfficersDefinition },
    policeCrewCapacity,
    api.capacity(0, 0, true),
    api.capacity(0, 0, true),
    api.capacity(1, 1, true)
);
assert.strictEqual(policeCrewCoverage.covered, true, 'minimum selected Police Car crew covers a one-officer requirement');
assert.strictEqual(policeCrewCoverage.stillNeededText, '0', 'selected crew removes the confirmed one-officer shortage');
}

// Issue #269: official catalogue abbreviations merge into canonical full-name PRV/SRV rows.
{
const prvParsed = api.parseText('2 PRVs', 'vehicles');
const prvRequirement = prvParsed.requirements.find(item => item.missing === 2);
assert(prvRequirement, 'PRVs catalogue alias parses');
assert.strictEqual(prvRequirement.key, 'primary-response', 'PRVs resolves to the canonical Primary Response Vehicle key');
assert.strictEqual(prvRequirement.definition.label, 'Primary Response Vehicle', 'PRVs retains the full canonical display name');
assert.strictEqual(prvParsed.remaining, '', 'PRVs alias is consumed completely');
const srvParsed = api.parseText('2 SRVs', 'vehicles');
const srvRequirement = srvParsed.requirements.find(item => item.missing === 2);
assert(srvRequirement, 'SRVs catalogue alias parses');
assert.strictEqual(srvRequirement.key, 'secondary-response', 'SRVs resolves to the canonical Secondary Response Vehicle key');
assert.strictEqual(srvRequirement.definition.label, 'Secondary Response Vehicle', 'SRVs retains the full canonical display name');
assert.strictEqual(srvParsed.remaining, '', 'SRVs alias is consumed completely');
const zero = api.capacity(0, 0, true);
const two = api.capacity(2, 2, true);
const prvRow = api.coverageRow({ ...prvRequirement, requirement: prvRequirement.definition.label }, zero, zero, zero, two);
const srvRow = api.coverageRow({ ...srvRequirement, requirement: srvRequirement.definition.label }, zero, zero, zero, two);
const aliasPanel = api.panelHtml([prvRow, srvRow], []);
assert(aliasPanel.html.includes('Primary Response Vehicle'), 'Matrix renders the full Primary Response Vehicle name');
assert(aliasPanel.html.includes('Secondary Response Vehicle'), 'Matrix renders the full Secondary Response Vehicle name');
assert(!aliasPanel.html.includes('>PRVs<'), 'Matrix does not render a separate PRVs row');
assert(!aliasPanel.html.includes('>SRVs<'), 'Matrix does not render a separate SRVs row');
}

'''
    runtime_test = replace_once(runtime_test, regression_marker, regression + regression_marker, "Issue 269 runtime regressions")
    RUNTIME_TEST_PATH.write_text(runtime_test, encoding="utf-8")

    catalogue_fixture = json.loads(CATALOGUE_FIXTURE_PATH.read_text(encoding="utf-8"))
    major = next((page for page in catalogue_fixture.get("pages", []) if page.get("id") == 34), None)
    if not major:
        raise RuntimeError("major incident catalogue fixture not found")
    major.setdefault("expected", {})["primary-response"] = 2
    major.setdefault("expected", {})["secondary-response"] = 2
    CATALOGUE_FIXTURE_PATH.write_text(json.dumps(catalogue_fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
    changelog_entry = f"""## [{NEW_VERSION}] - 2026-07-20

### Fixed
- Selected Police Cars and other supported vehicles now contribute their reviewed UK minimum/maximum crew capacity to generic personnel requirements when MissionChief exposes no semantic crew field.
- Known bounded personnel ranges remain bounded instead of becoming completely unknown.
- Official `PRV`/`PRVs` and `SRV`/`SRVs` catalogue labels now merge into the canonical Primary Response Vehicle and Secondary Response Vehicle rows.
- The Matrix renders only the full canonical response-vehicle names.

### Validation
- Added deterministic crew-range, native override, selected Police Officer, abbreviation, canonical-key and rendered-label regressions.

"""
    changelog = replace_once(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + changelog_entry, "changelog insertion")
    CHANGELOG_PATH.write_text(changelog, encoding="utf-8")

    help_html = HELP_PATH.read_text(encoding="utf-8")
    help_html = help_html.replace(f"Guide for Toolkit v{OLD_VERSION}", f"Guide for Toolkit v{NEW_VERSION}")
    HELP_PATH.write_text(help_html, encoding="utf-8")

    final_source = SOURCE_PATH.read_text(encoding="utf-8")
    DIST_USER_PATH.write_text(final_source, encoding="utf-8")
    DIST_TEXT_PATH.write_text(final_source, encoding="utf-8")
    digest = hashlib.sha256(final_source.encode("utf-8")).hexdigest()
    SHA_PATH.write_text(
        f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
        encoding="utf-8",
    )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["version"] = NEW_VERSION
    manifest["sha256"] = digest
    manifest["bytes"] = len(final_source.encode("utf-8"))
    manifest["lines"] = len(final_source.splitlines())
    manifest.setdefault("metadata", {})["runtimeVersion"] = NEW_VERSION
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Prepared Toolkit {NEW_VERSION} Issue #269 hotfix candidate")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
