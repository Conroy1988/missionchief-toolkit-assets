#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / '.github' / 'development-packages' / 'uk-requirement-capability-port.py'
V3 = ROOT / '.github' / 'development-packages' / 'uk-requirement-capability-port-v3.py'
text = ORIGINAL.read_text(encoding='utf-8')
anchor = 'CONTRACT.write_text(contract, encoding="utf-8")\n'
insert = r'''contract = contract.replace(
    r''' + "'''" + r'''r"key:\s*['\"]railway-police-officer['\"][^\n]*training:\s*\[[^\]]*Railway Police"''' + "'''" + r''',
    r''' + "'''" + r'''r"(?:key|['\"]key['\"])\s*:\s*['\"]railway-police-officer['\"][^\n]*(?:training|['\"]training['\"])\s*:\s*\[[^\]]*Railway Police"''' + "'''" + r''',
)
contract = contract.replace(
    r''' + "'''" + r'''r"key:\s*['\"]ambulance['\"][^\n]*types:\s*\[5,\s*9\]"''' + "'''" + r''',
    r''' + "'''" + r'''r"(?:key|['\"]key['\"])\s*:\s*['\"]ambulance['\"][^\n]*(?:types|['\"]types['\"])\s*:\s*\[5,\s*9\]"''' + "'''" + r''',
)
contract = contract.replace(
    r''' + "'''" + r'''r"key:\s*['\"]hems['\"][^\n]*types:\s*\[9\]"''' + "'''" + r''',
    r''' + "'''" + r'''r"(?:key|['\"]key['\"])\s*:\s*['\"]hems['\"][^\n]*(?:types|['\"]types['\"])\s*:\s*\[9\]"''' + "'''" + r''',
)
contract = contract.replace(
    r''' + "'''" + r'''rf"types:\s*\[[^\]]*\b{vehicle_type}\b"''' + "'''" + r''',
    r''' + "'''" + r'''rf"(?:types|['\"]types['\"])\s*:\s*\[[^\]]*\b{vehicle_type}\b"''' + "'''" + r''',
)
CONTRACT.write_text(contract, encoding="utf-8")
'''
if text.count(anchor) != 1:
    raise AssertionError(f'expected one contract write anchor, found {text.count(anchor)}')
ORIGINAL.write_text(text.replace(anchor, insert, 1), encoding='utf-8')
result = subprocess.run(['python3', str(V3.relative_to(ROOT))], cwd=ROOT)
if result.returncode != 0:
    raise SystemExit(result.returncode)
Path(__file__).unlink()
print('Applied JSON-compatible UK requirement capability contracts')
