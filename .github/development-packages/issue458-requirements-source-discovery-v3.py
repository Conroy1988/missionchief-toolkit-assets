#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / '.github/development-packages/issue458-requirements-source-discovery.py'
V2 = ROOT / '.github/development-packages/issue458-requirements-source-discovery-v2.py'
payload = ORIGINAL.read_text(encoding='utf-8')
old = '        const model = operationalRequirementCreateModel(operationalRequirementsInput(context, requirementRoot));'
new = '        const input = operationalRequirementsInput(context, requirementRoot);\n        const model = operationalRequirementCreateModel(input);'
if payload.count(old) != 2:
    raise SystemExit(f'Expected two v5.0.3 renderer expressions in reviewed package, found {payload.count(old)}')
payload = payload.replace(old, new)
namespace = {'__file__': str(ORIGINAL), '__name__': '__main__'}
exec(compile(payload, str(ORIGINAL), 'exec'), namespace)
ORIGINAL.unlink(missing_ok=True)
V2.unlink(missing_ok=True)
