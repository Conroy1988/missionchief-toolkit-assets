#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
fixture = json.loads((ROOT / '.github/fixtures/main-style-source-headroom.json').read_text(encoding='utf-8'))
candidate = fixture['v8Candidate']
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
actual = {
    'sourceBytes': len(text.encode()),
    'sourceLines': len(text.splitlines()),
    'sourceSha256': hashlib.sha256(text.encode()).hexdigest(),
    'templateBytes': len(raw.encode()),
    'templateLines': len(lines),
    'templateSha256': hashlib.sha256(raw.encode()).hexdigest(),
    'canonicalCssSha256': hashlib.sha256(canonical.encode()).hexdigest(),
}
assert all(actual[key] == candidate[key] for key in actual), (actual, candidate)
assert actual['sourceBytes'] <= candidate['maxSourceBytes'], (actual, candidate)
assert actual['sourceLines'] <= candidate['maxSourceLines'], (actual, candidate)
assert actual['templateBytes'] >= candidate['minTemplateBytes'], (actual, candidate)
print('Main-style source-headroom contract passed for v8.')
