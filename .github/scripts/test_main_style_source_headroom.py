#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
fixture = json.loads((ROOT / '.github/fixtures/main-style-source-headroom.json').read_text(encoding='utf-8'))
candidate = fixture['v10Candidate']
fingerprint = json.loads((ROOT / '.github/fixtures/current-toolkit-candidate.json').read_text(encoding='utf-8'))['source']
start = text.index('function installMainStyles()')
template_start = text.index('addStyle(`', start) + len('addStyle(`')
metric = text.index("recordStartupMetric('stylesheetInstallMs'", template_start)
template_end = text.rfind('`);', template_start, metric)
raw = text[template_start:template_end]
lines = raw.split('\n')
canonical = re.sub(
    r'\n[\t ]*}',
    '}',
    '\n'.join(
        line
        for index, line in enumerate(lines)
        if not (0 < index < len(lines) - 1 and not line.strip())
    ),
)
actual_source = {
    'bytes': len(text.encode()),
    'lines': len(text.splitlines()),
    'path': 'src/MissionChief_Map_Command_Toolkit.user.js',
    'sha256': hashlib.sha256(text.encode()).hexdigest(),
    'version': re.search(r'^//\s*@version\s+([^\s]+)\s*$', text, re.MULTILINE).group(1),
}
actual_template = {
    'templateBytes': len(raw.encode()),
    'templateLines': len(lines),
    'templateSha256': hashlib.sha256(raw.encode()).hexdigest(),
    'canonicalCssSha256': hashlib.sha256(canonical.encode()).hexdigest(),
}
assert actual_source == fingerprint, (actual_source, fingerprint)
assert all(actual_template[key] == candidate[key] for key in actual_template), (actual_template, candidate)
assert actual_source['bytes'] <= candidate['maxSourceBytes'], (actual_source, candidate)
assert actual_source['lines'] <= candidate['maxSourceLines'], (actual_source, candidate)
assert actual_template['templateBytes'] >= candidate['minTemplateBytes'], (actual_template, candidate)
print('Main-style source-headroom contract passed for v10.')
