#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = "4.20.14"
NEW = "4.20.15"
source_path = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
data_path = ROOT / "src/data/mission-requirements-en_GB.json"
test_path = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
fixture_path = ROOT / ".github/fixtures/mission-catalogue-pages.json"


def required_replace(text: str, old: str, new: str, label: str, *, all_matches: bool = False) -> str:
    count = text.count(old)
    if count < 1:
        raise RuntimeError(f"{label}: marker not found")
    print(f"{label}: {count} match(es)")
    return text.replace(old, new) if all_matches else text.replace(old, new, 1)


def add_aliases(entry: dict, additions: list[str]) -> None:
    aliases = entry.setdefault("aliases", [])
    folded = {str(alias).casefold() for alias in aliases}
    for alias in additions:
        if alias.casefold() not in folded:
            aliases.append(alias)
            folded.add(alias.casefold())


def main() -> None:
    source = source_path.read_text(encoding="utf-8")
    source = required_replace(source, f"// @version      {OLD}", f"// @version      {NEW}", "metadata version")
    source = required_replace(source, f"version: '{OLD}'", f"version: '{NEW}'", "runtime version")
    source = required_replace(
        source,
        '"aliases":["Primary Response Vehicle","Primary Response Vehicles"]',
        '"aliases":["Primary Response Vehicle","Primary Response Vehicles","PRV","PRVs"]',
        "Primary Response Vehicle aliases",
        all_matches=True,
    )
    source = required_replace(
        source,
        '"aliases":["Secondary Response Vehicle","Secondary Response Vehicles"]',
        '"aliases":["Secondary Response Vehicle","Secondary Response Vehicles","SRV","SRVs"]',
        "Secondary Response Vehicle aliases",
        all_matches=True,
    )

    ranges = {0:[1,9],1:[1,5],2:[1,3],3:[1,3],4:[1,5],5:[1,2],6:[1,3],7:[1,6],8:[1,2],9:[3,5],12:[1,2],13:[1,4],14:[1,3],15:[1,6],16:[1,9],17:[1,6],18:[1,1],19:[1,3],20:[1,1],23:[1,12],24:[1,2],25:[1,2],26:[1,3],27:[1,2],28:[1,2],31:[1,2],34:[1,1],35:[1,2],36:[1,2],37:[2,9],38:[2,9],39:[1,6],40:[1,2],51:[1,9],52:[1,9],53:[1,4],55:[1,8],56:[1,6],81:[0,0],82:[1,2],83:[1,1],86:[1,3],87:[0,0],92:[1,1],93:[1,1],95:[1,2],96:[1,2],99:[1,4],101:[1,1],102:[1,1],116:[1,5]}
    runtime = (
        f"const MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE = Object.freeze({json.dumps(ranges, separators=(',', ':'))});\n"
        "function missionRequirementsDefaultStaffCapacity(typeId, element = null) { const range = MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE[typeId] || MISSION_REQUIREMENTS_DEFAULT_STAFF_BY_TYPE[String(typeId)]; if (!Array.isArray(range) || range.length < 2) return null; const row = element?.closest?.('tr') || element; const scopes = Array.from(new Set([element, row].filter(Boolean))); const overrideAttributes = ['data-max-personnel-override', 'data-personnel-max-override', 'data-max-crew-override']; let maximumOverride = null; for (const scope of scopes) { for (const attribute of overrideAttributes) { const value = missionRequirementsOptionalNumber(scope?.getAttribute?.(attribute)); if (value !== null) { maximumOverride = value; break; } } if (maximumOverride !== null) break; } const minimum = Math.max(0, Number(range[0]) || 0); const configuredMaximum = Math.max(minimum, Number(range[1]) || 0); const maximum = maximumOverride === null ? configuredMaximum : Math.max(minimum, maximumOverride); return missionRequirementsCapacity(minimum, maximum, minimum === maximum); }\n"
    )
    source = required_replace(source, "function missionRequirementsStaffCapacity(element) {", runtime + "function missionRequirementsStaffCapacity(element) {", "crew fallback insertion")
    source = required_replace(source, "staff: missionRequirementsStaffCapacity(vehicleElement),", "staff: missionRequirementsStaffCapacity(vehicleElement) || missionRequirementsDefaultStaffCapacity(typeId, vehicleElement),", "selected unit crew fallback")
    source = required_replace(source, "return { eligible: true, unknown: !capacity.known, capacity };", "return { eligible: true, unknown: capacity.max === null, capacity };", "bounded crew preservation")
    source_path.write_text(source, encoding="utf-8")

    dataset = json.loads(data_path.read_text(encoding="utf-8"))
    primary = secondary = False
    for entry in dataset.get("vehicleRequirements", []):
        if entry.get("key") == "primary-response-vehicle":
            add_aliases(entry, ["PRV", "PRVs"])
            primary = True
        elif entry.get("key") == "secondary-response-vehicle":
            add_aliases(entry, ["SRV", "SRVs"])
            secondary = True
    if not primary or not secondary:
        raise RuntimeError("canonical UK response vehicle entries missing")
    data_path.write_text(json.dumps(dataset, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    test = test_path.read_text(encoding="utf-8")
    test = required_replace(test, f"version: '{OLD}'", f"version: '{NEW}'", "test runtime version")
    test = required_replace(test, "    staffCapacity: missionRequirementsStaffCapacity,\n    equipmentTypes: missionRequirementsEquipmentTypes,", "    staffCapacity: missionRequirementsStaffCapacity,\n    defaultStaffCapacity: missionRequirementsDefaultStaffCapacity,\n    equipmentTypes: missionRequirementsEquipmentTypes,", "test API export")
    marker = "const factorRequirement = { group: 'vehicles', definition: { types: [5], equipment: [], factors: { 5: 2 } } };"
    checks = r'''
// Issue #269 vehicle crew fallback and canonical PRV/SRV aliases.
{
const policeStaff = api.defaultStaffCapacity(8, null);
assert.strictEqual(policeStaff.min, 1, 'Police Car contributes at least one officer');
assert.strictEqual(policeStaff.max, 2, 'Police Car preserves its two-officer maximum');
const overrideElement = { getAttribute(name) { return name === 'data-max-personnel-override' ? '1' : null; }, closest() { return null; } };
const overriddenStaff = api.defaultStaffCapacity(8, overrideElement);
assert.strictEqual(overriddenStaff.min, 1, 'override preserves minimum crew');
assert.strictEqual(overriddenStaff.max, 1, 'native override narrows maximum crew');
const policeDefinition = api.definitions.find(definition => definition.key === 'police-officers');
const selectedPoliceCar = { typeId: 8, equipment: new Set(), labels: new Set(), training: new Set(), knownDefinitionKeys: new Set(), staff: policeStaff, contributionKey: 'vehicle:26901' };
const selectedPoliceCapacity = api.aggregate({ group: 'staff', definition: policeDefinition }, [selectedPoliceCar]);
assert.strictEqual(selectedPoliceCapacity.min, 1, 'selected Police Car credits one confirmed Police Officer');
assert.strictEqual(selectedPoliceCapacity.max, 2, 'selected Police Car retains bounded officer capacity');
const coveredPoliceRow = api.coverageRow({ key: 'police-officers', requirement: 'Police Officers', missing: 1, group: 'staff', definition: policeDefinition }, selectedPoliceCapacity, api.capacity(0, 0, true), api.capacity(0, 0, true), api.capacity(1, 1, true));
assert.strictEqual(coveredPoliceRow.stillNeededText, '0', 'selected Police Car clears a one-officer shortage');
for (const [text, key, label] of [['2 PRVs', 'primary-response', 'Primary Response Vehicle'], ['2 SRVs', 'secondary-response', 'Secondary Response Vehicle']]) {
    const parsed = api.parseText(text, 'vehicles');
    const requirement = parsed.requirements.find(item => item.missing === 2);
    assert(requirement, `${text} parses as a requirement`);
    assert.strictEqual(requirement.key, key, `${text} uses the canonical key`);
    assert.strictEqual(requirement.definition.label, label, `${text} uses the full canonical label`);
    assert.strictEqual(parsed.remaining, '', `${text} is consumed without unresolved residue`);
}
}

'''
    test = required_replace(test, marker, checks + marker, "Issue 269 runtime checks")
    test_path.write_text(test, encoding="utf-8")

    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    major = next(page for page in fixture["pages"] if page.get("id") == 34)
    major["expected"]["primary-response"] = 2
    major["expected"]["secondary-response"] = 2
    fixture_path.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    changelog_path = ROOT / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")
    entry = """## [4.20.15] - 2026-07-20

### Fixed
- Selected Police Cars and other supported vehicles now contribute reviewed UK minimum/maximum crew capacity to generic personnel requirements when MissionChief exposes no semantic crew field.
- Known bounded personnel ranges remain bounded rather than becoming completely unknown.
- `PRV`/`PRVs` and `SRV`/`SRVs` now merge into the canonical Primary Response Vehicle and Secondary Response Vehicle rows, with only the full names rendered.

### Validation
- Added deterministic crew fallback, override, selected Police Officer and response-vehicle alias regressions.

"""
    changelog = required_replace(changelog, "## [Unreleased]\n\n", "## [Unreleased]\n\n" + entry, "changelog")
    changelog_path.write_text(changelog, encoding="utf-8")

    help_path = ROOT / "help/index.html"
    help_text = help_path.read_text(encoding="utf-8").replace(f"Guide for Toolkit v{OLD}", f"Guide for Toolkit v{NEW}")
    help_path.write_text(help_text, encoding="utf-8")

    final = source_path.read_text(encoding="utf-8")
    for target in [ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js", ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"]:
        target.write_text(final, encoding="utf-8")
    digest = hashlib.sha256(final.encode("utf-8")).hexdigest()
    (ROOT / "dist/SHA256SUMS.txt").write_text(f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n", encoding="utf-8")
    manifest_path = ROOT / "dist/release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update({"version": NEW, "sha256": digest, "bytes": len(final.encode('utf-8')), "lines": len(final.splitlines())})
    manifest.setdefault("metadata", {})["runtimeVersion"] = NEW
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for obsolete in ["issue-269-matrix-crew-alias-hotfix.py", "issue-269-matrix-crew-alias-hotfix-v2.py"]:
        (Path(__file__).with_name(obsolete)).unlink(missing_ok=True)
    print(f"Prepared Toolkit {NEW} Issue #269 hotfix candidate: {digest}")


if __name__ == "__main__":
    main()
