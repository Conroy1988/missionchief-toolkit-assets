#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package = root / '.github/development-packages/issue-181-patient-ambulance-demand.py'
lines = package.read_text(encoding='utf-8').splitlines()
indices = [i for i, line in enumerate(lines) if 'function missionRequirementsParseText(rawText' in line and i > 500]
if len(indices) != 2:
    raise AssertionError(f'Expected two contract literal lines, found {len(indices)} at {indices}')
anchor = '        "function missionRequirementsParseText(rawText, group = \'vehicles\')",'
replacement = '\n'.join([
    anchor,
    '        "function missionRequirementsParseSource(source)",',
    '        "function missionRequirementsPatientCount(candidate)",',
    '        "function missionRequirementsPatientState(record, now = Date.now())",',
    '        "function missionRequirementsReconcilePatientDemand(parsed, patientState)",',
    '        "MISSION_REQUIREMENTS_PATIENT_TRANSITION_MS = 1400",',
])
lines[indices[0]] = f'    {anchor!r},'
lines[indices[1]] = f'    {replacement!r},'
text = '\n'.join(lines) + '\n'
compile(text, str(package), 'exec')
package.write_text(text, encoding='utf-8')
print('Issue 181 contract literals repaired')
