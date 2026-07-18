#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package = root / '.github/development-packages/issue-181-patient-ambulance-demand.py'
text = package.read_text(encoding='utf-8')
old_name = "const ambulanceDefinition = api.definitions.find(definition => definition.key === 'ambulance');"
new_name = "const patientAmbulanceDefinition = api.definitions.find(definition => definition.key === 'ambulance');"
old_use = "definition: ambulanceDefinition }]"
new_use = "definition: patientAmbulanceDefinition }]"
if text.count(old_name) != 1:
    raise AssertionError(f'Expected one declaration, found {text.count(old_name)}')
if text.count(old_use) != 1:
    raise AssertionError(f'Expected one usage, found {text.count(old_use)}')
text = text.replace(old_name, new_name, 1).replace(old_use, new_use, 1)
compile(text, str(package), 'exec')
package.write_text(text, encoding='utf-8')
print('Issue 181 fixture variable renamed')
