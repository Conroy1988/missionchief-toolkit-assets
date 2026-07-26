#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / '.github/scripts/check_audio_alias_contract.py'
text = path.read_text(encoding='utf-8')
old = '        path = match.group("path").rstrip(".,;:")\n'
new = (
    '        path = match.group("path").rstrip(".,;:")\n'
    '        path = path.split("?", 1)[0].split("#", 1)[0]\n'
)
if text.count(old) != 1:
    raise SystemExit(f'Expected one raw audio path parser, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Canonical audio URL parser now ignores cache-version query and fragment components.')
