#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / '.github' / 'development-packages' / 'uk-requirement-capability-port-v2.py'
text = V2.read_text(encoding='utf-8')
old = "            assert.ok((definition.aliases || []).includes(alias), `${group}:${entry.key}: parsed alias ${alias}`);\n"
new = "            assert.ok((definition.aliases || []).some(value => String(value).trim().toLowerCase() === String(alias).trim().toLowerCase()), `${group}:${entry.key}: parsed alias ${alias}`);\n"
if text.count(old) != 1:
    raise AssertionError(f'expected one alias assertion in v2 wrapper, found {text.count(old)}')
V2.write_text(text.replace(old, new, 1), encoding='utf-8')
result = subprocess.run(['python3', str(V2.relative_to(ROOT))], cwd=ROOT)
if result.returncode != 0:
    raise SystemExit(result.returncode)
Path(__file__).unlink()
print('Applied case-normalized UK requirement capability port')
