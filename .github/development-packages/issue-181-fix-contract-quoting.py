#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package = root / '.github/development-packages/issue-181-patient-ambulance-demand.py'
text = package.read_text(encoding='utf-8')
old_anchor = '''    '        "function missionRequirementsParseText(rawText, group = 'vehicles')",','''
new_anchor = '''    "        \"function missionRequirementsParseText(rawText, group = 'vehicles')\",",'''
old_replacement = '''    '        "function missionRequirementsParseText(rawText, group = 'vehicles')",\\n        "function missionRequirementsParseSource(source)",\\n        "function missionRequirementsPatientCount(candidate)",\\n        "function missionRequirementsPatientState(record, now = Date.now())",\\n        "function missionRequirementsReconcilePatientDemand(parsed, patientState)",\\n        "MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400",','''
new_replacement = '''    "        \"function missionRequirementsParseText(rawText, group = 'vehicles')\",\\n        \"function missionRequirementsParseSource(source)\",\\n        \"function missionRequirementsPatientCount(candidate)\",\\n        \"function missionRequirementsPatientState(record, now = Date.now())\",\\n        \"function missionRequirementsReconcilePatientDemand(parsed, patientState)\",\\n        \"MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400\",",'''
if text.count(old_anchor) != 1:
    raise AssertionError(f'Expected one invalid contract anchor literal, found {text.count(old_anchor)}')
if text.count(old_replacement) != 1:
    raise AssertionError(f'Expected one invalid contract replacement literal, found {text.count(old_replacement)}')
text = text.replace(old_anchor, new_anchor, 1).replace(old_replacement, new_replacement, 1)
compile(text, str(package), 'exec')
package.write_text(text, encoding='utf-8')
print('Issue 181 contract package quoting corrected')
