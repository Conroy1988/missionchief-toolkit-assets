#!/usr/bin/env python3
from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / '.github' / 'development-packages' / 'issue-226-operational-capacity-fix.py'

text = PACKAGE.read_text(encoding='utf-8')
old = "const issue226Parsed = { requirements: [{ key: 'police-car', requirement: 'Police Car', missing: 1, group: 'vehicles', definition: issue226PoliceDefinition }], unresolved: [] };"
new = "const issue226Parsed = { requirements: [{ key: 'police-car', requirement: 'Police Car', missing: 1, group: 'vehicles', definition: issue226PoliceDefinition, statedRequirement: false, catalogueDerived: true, catalogueProbability: 100 }], unresolved: [] };"
if text.count(old) != 1:
    raise AssertionError(f'expected one Issue #226 fixture match, found {text.count(old)}')
PACKAGE.write_text(text.replace(old, new, 1), encoding='utf-8')
py_compile.compile(str(PACKAGE), doraise=True)
print('Issue #226 authoritative baseline fixture corrected')
