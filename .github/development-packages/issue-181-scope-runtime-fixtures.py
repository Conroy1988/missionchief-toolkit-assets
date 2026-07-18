#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package = root / '.github/development-packages/issue-181-patient-ambulance-demand.py'
text = package.read_text(encoding='utf-8')
old_start = "patient_tests = r'''\n\nfunction attachPatientSummary"
new_start = "patient_tests = r'''\n\n{\nfunction attachPatientSummary"
old_end = "api.clear();\ncandidates = [];\n'''\nruntime = replace_once(runtime, \"\\nconst directDoc = new FakeDocument();\""
new_end = "api.clear();\ncandidates = [];\n}\n'''\nruntime = replace_once(runtime, \"\\nconst directDoc = new FakeDocument();\""
if text.count(old_start) != 1:
    raise AssertionError(f'Expected one patient fixture start, found {text.count(old_start)}')
if text.count(old_end) != 1:
    raise AssertionError(f'Expected one patient fixture end, found {text.count(old_end)}')
text = text.replace(old_start, new_start, 1).replace(old_end, new_end, 1)
compile(text, str(package), 'exec')
package.write_text(text, encoding='utf-8')
print('Issue 181 runtime fixtures scoped')
