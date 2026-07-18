#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package = root / '.github/development-packages/issue-181-patient-ambulance-demand.py'
text = package.read_text(encoding='utf-8')
old = '''contract = replace_once(
    contract,
    '        "function missionRequirementsParseSource(source)",',
    '        "function missionRequirementsParseSource(source)",\\n        "function missionRequirementsPatientCount(candidate)",\\n        "function missionRequirementsPatientState(record, now = Date.now())",\\n        "function missionRequirementsReconcilePatientDemand(parsed, patientState)",\\n        "MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400",',
    "patient contract markers",
)'''
new = '''contract = replace_once(
    contract,
    '        "function missionRequirementsParseText(rawText, group = \'vehicles\')",',
    '        "function missionRequirementsParseText(rawText, group = \'vehicles\')",\\n        "function missionRequirementsParseSource(source)",\\n        "function missionRequirementsPatientCount(candidate)",\\n        "function missionRequirementsPatientState(record, now = Date.now())",\\n        "function missionRequirementsReconcilePatientDemand(parsed, patientState)",\\n        "MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400",',
    "patient contract markers",
)'''
if text.count(old) != 1:
    raise AssertionError(f'Expected one patient contract marker block, found {text.count(old)}')
package.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Issue 181 contract marker anchor corrected')
