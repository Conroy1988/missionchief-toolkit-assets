#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
RUNTIME = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP_INDEX = ROOT / "help" / "index.html"
HELP_MANIFEST = ROOT / "help" / "manifest.json"
SITE_DATA = ROOT / "docs" / "site-data.json"
PATIENT_FRAGMENT = ROOT / ".github" / "development-packages" / "issue-186-patient-runtime.jsfrag"
FIXTURE_FRAGMENT = ROOT / ".github" / "development-packages" / "issue-186-runtime-fixture.jsfrag"

PREVIOUS = "4.19.0"
VERSION = "4.19.1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = SOURCE.read_text(encoding="utf-8")
source = replace_once(source, f"// @version      {PREVIOUS}", f"// @version      {VERSION}", "metadata version")
source = replace_once(source, f"        version: '{PREVIOUS}',", f"        version: '{VERSION}',", "runtime version")

old_definitions = """        { key: 'hems', label: 'HEMS', aliases: ['HEMS'], types: [9] },
        { key: 'police-helicopter', label: 'Police Helicopter', aliases: ['Police helicopter', 'Police helicopters', 'Policehelicopter', 'Policehelicopters'], types: [11] },"""
new_definitions = """        { key: 'hems', label: 'HEMS', aliases: ['HEMS'], types: [9] },
        { key: 'critical-care-patient', label: 'Critical Care', aliases: ['Critical Care'], group: 'other', types: [], countable: true, patientCondition: true },
        { key: 'patient-transport', label: 'Patient Transport', aliases: ['Patient Transport'], group: 'other', types: [], countable: true, patientCondition: true },
        { key: 'police-helicopter', label: 'Police Helicopter', aliases: ['Police helicopter', 'Police helicopters', 'Policehelicopter', 'Policehelicopters'], types: [11] },"""
source = replace_once(source, old_definitions, new_definitions, "patient condition definitions")

patient_start = source.index("    // Issue #181: patient-derived ambulance demand.")
patient_end = source.index("\n    function missionRequirementsVehicleType(element)", patient_start)
patient_block = PATIENT_FRAGMENT.read_text(encoding="utf-8").rstrip("\n")
source = source[:patient_start] + patient_block + source[patient_end:]

resolve_anchor = "return parsed.requirements.map(requirement => { if (requirement.definition?.countable === false)"
resolve_replacement = "return parsed.requirements.map(requirement => { if (requirement.patientCondition === true) { const requiredValue = Math.max(0, Number(requirement.patientConditionRequired ?? requirement.patientRequired ?? requirement.missing) || 0); const fulfilledValue = Math.max(0, Number(requirement.patientConditionFulfilled) || 0); const fulfilledKnown = requirement.patientConditionFulfilledKnown === true; const zero = missionRequirementsCapacity(0, 0, true); const fulfilled = fulfilledKnown ? missionRequirementsCapacity(fulfilledValue, fulfilledValue, true) : missionRequirementsCapacity(fulfilledValue, null, false); const row = missionRequirementsCoverageRow(requirement, zero, zero, fulfilled, missionRequirementsCapacity(requiredValue, requiredValue, true)); if (!fulfilledKnown && !row.covered) { row.definitelyOpen = false; row.uncertain = true; row.coverageKnown = false; } return { ...row, conditionKnown: true, conditionMatched: true, requirementAuthority: 'patient-details' }; } if (requirement.definition?.countable === false)"
source = replace_once(source, resolve_anchor, resolve_replacement, "patient condition resolver")

mutation_anchor = "#patient_button_form, #patient_button_text, #patient_button_text strong, [data-patient-count]"
mutation_replacement = "#patient_button_form, #patient_button_text, #patient_button_text strong, [id^=\"patient_\"], [data-patient-id], [data-patient], [class*=\"patient\"], [data-patient-count]"
if mutation_anchor not in source:
    raise AssertionError("patient mutation selector: no matches")
source = source.replace(mutation_anchor, mutation_replacement)
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME.read_text(encoding="utf-8")
runtime = replace_once(runtime, "version: '4.19.0'", "version: '4.19.1'", "runtime fixture version")
runtime = replace_once(
    runtime,
    "    patientCount: missionRequirementsPatientCount,\n    patientState: missionRequirementsPatientState,",
    "    patientCount: missionRequirementsPatientCount,\n    patientDetails: missionRequirementsPatientDetails,\n    patientState: missionRequirementsPatientState,",
    "runtime patient details API",
)
fixture_anchor = "\nconst directDoc = new FakeDocument();"
fixture_block = FIXTURE_FRAGMENT.read_text(encoding="utf-8").rstrip("\n")
runtime = replace_once(runtime, fixture_anchor, "\n" + fixture_block + fixture_anchor, "issue 186 runtime fixtures")
RUNTIME.write_text(runtime, encoding="utf-8")

contract = CONTRACT.read_text(encoding="utf-8")
contract = replace_once(
    contract,
    '        "function missionRequirementsPatientCount(candidate)",\n        "function missionRequirementsPatientState(record, now = Date.now())",',
    '        "function missionRequirementsPatientContext(candidate)",\n        "function missionRequirementsPatientCount(candidate)",\n        "function missionRequirementsPatientDetails(candidate)",\n        "function missionRequirementsPatientState(record, now = Date.now())",',
    "contract patient markers",
)
contract = replace_once(
    contract,
    '    assert source.count("function missionRequirementsPatientCount(candidate)") == 1\n    assert source.count("function missionRequirementsReconcilePatientDemand(parsed, patientState)") == 1',
    '    assert source.count("function missionRequirementsPatientContext(candidate)") == 1\n    assert source.count("function missionRequirementsPatientCount(candidate)") == 1\n    assert source.count("function missionRequirementsPatientDetails(candidate)") == 1\n    assert source.count("function missionRequirementsReconcilePatientDemand(parsed, patientState)") == 1\n    assert "patientConditionFulfilledKnown" in source\n    assert "critical-care-patient" in source\n    assert "patient-transport" in source',
    "contract patient assertions",
)
CONTRACT.write_text(contract, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## [Unreleased]

## [4.19.1] - 2026-07-19

### Fixed
- Corrected live patient discovery when MissionChief renders the patient summary and details outside the resolved mission form, preventing the Mission Requirements Matrix from falsely reporting no outstanding requirements.
- Restored the one-transport-ambulance-per-current-patient requirement on the real mission-window layout.

### Added
- Added patient-detail reconciliation for affirmative **Critical Care required**, **HEMS required** and **Requires Transport** fields.
- Added fulfilment handling for **Ambulance with the patient** and **Critical Care with the patient** without double-counting vehicle demand.

### Validation
- Added deterministic outside-form patient DOM fixtures, affirmative/negative patient-flag fixtures and false-green prevention checks.

"""
changelog = replace_once(changelog, "## [Unreleased]\n\n", entry, "changelog entry")
CHANGELOG.write_text(changelog, encoding="utf-8")

help_index = HELP_INDEX.read_text(encoding="utf-8").replace("Guide for Toolkit v4.19.0", "Guide for Toolkit v4.19.1")
HELP_INDEX.write_text(help_index, encoding="utf-8")

help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-19"
help_manifest["runtimeGuidePatch"] = "Toolkit v4.19.1 restores live patient discovery outside the mission form, enforces one ambulance per patient, and adds affirmative Critical Care, HEMS and transport conditions to the Mission Requirements Matrix."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

site_data = json.loads(SITE_DATA.read_text(encoding="utf-8"))
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Mission Requirements":
            feature["summary"] = "Shows live required, on-site, responding, selected and still-needed capacity, including patient-derived ambulance and direct patient requirements."
            details = feature.setdefault("details", [])
            patient_detail = "One ambulance per current patient plus affirmative Critical Care, HEMS and transport conditions"
            if patient_detail not in details:
                details.insert(1, patient_detail)
SITE_DATA.write_text(json.dumps(site_data, indent=2) + "\n", encoding="utf-8")

PATIENT_FRAGMENT.unlink(missing_ok=True)
FIXTURE_FRAGMENT.unlink(missing_ok=True)
print(f"Prepared Toolkit {VERSION} patient requirements patch")
