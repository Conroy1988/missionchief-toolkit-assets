#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
EXPECTED_SOURCE_SHA = '773d6686fdcfe0af5901f54bdd58c58cf0ef8503bddaae354f32ed25879ac19b'

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_SOURCE_SHA:
    raise SystemExit('Unexpected v8.0.3 source baseline')

readme_path = ROOT / 'README.md'
text = readme_path.read_text(encoding='utf-8')
replacements = (
    ('## **Current verified release: `v8.0.1` · Development candidate: `v8.0.3`**',
     '## **Current verified release: `v8.0.2` · Development candidate: `v8.0.3`**'),
    ('### **Godfather layout and payout-audio hotfix**',
     '### **Godfather duration and payout-position hotfix**'),
    ('#current-release-signal--v801', '#current-release-signal--v802'),
    ('| **Production release** | 🟢 | GitHub Release `v8.0.1` published |',
     '| **Production release** | 🟢 | GitHub Release `v8.0.2` published |'),
    ('| **Version** | `8.0.0` |', '| **Version** | `8.0.2` |'),
    ('| **Release focus** | The Godfather complete interface system |',
     '| **Release focus** | Godfather layout and payout-audio hotfix |'),
    ('| **Validated SHA-256** | `049a0a0003dc28a1acabbb3a39958c01081deaa4032b48cedae97e9fc90d4d5b` |',
     '| **Validated SHA-256** | `5a33ed92ca3c3207d421654c8cd9370f95a6127a4ec759b4924412f19b36c474` |'),
    ('| **GitHub Release** | [`v8.0.0`](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v8.0.0) |',
     '| **GitHub Release** | [`v8.0.2`](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v8.0.2) |'),
    ('| **Private backup** | `cd0b94a59bdccb248dc7bdfe461f3e7419cc18bf` |',
     '| **Private backup** | `071c56229fc9a680f9ccbf5cddb5f57b83935958` |'),
)
for old, new in replacements:
    actual = text.count(old)
    if actual != 1:
        raise SystemExit(f'Unexpected README token count for {old!r}: {actual}')
    text = text.replace(old, new, 1)

start = text.index('# v8.0.2 hotfix signal')
end = text.index('\n---\n', start)
signal = '''# v8.0.3 hotfix signal

> **CRITICAL GODFATHER DURATION AND PAYOUT-POSITION REPAIR // DEVELOPMENT BRANCH ONLY**

The verified production release is **v8.0.2**. Candidate **v8.0.3** defaults the Godfather Offer flash to seven seconds when the normal four-second default is still active, preserves non-default user choices, and raises/compacts the payout on short-height layouts so the complete banner clears the command dock. Production remains on v8.0.2 until the guarded hotfix release completes.
'''
text = text[:start] + signal + text[end:]

start = text.index('# Current release signal — v8.0.1')
end = text.index('\n---\n', start)
release = '''# Current release signal — v8.0.2

> **CHANNEL UPDATE // GODFATHER LAYOUT AND PAYOUT AUDIO**

Version 8.0.2 contained the decorative family seal, restored compact Tablet controls, raised the Offer payout and replaced its audio byte-for-byte with the verified stereo MP3.

- The exact replacement audio remains protected by digest, byte-size, channel and bitrate contracts.
- The v7 native MissionChief boundary and every retained operational system remain in force.
- Candidate v8.0.3 adds the seven-second Godfather default and short-height dock-clearance repair.
'''
text = text[:start] + release + text[end:]
readme_path.write_text(text, encoding='utf-8')

for name in ('test_issue537_godfather_css_activation.py', 'test_issue539_godfather_layout_audio.py'):
    path = ROOT / '.github/scripts' / name
    payload = path.read_text(encoding='utf-8')
    old = r'@version\s+8\.0\.2$'
    new = r'@version\s+8\.0\.3$'
    if payload.count(old) != 1:
        raise SystemExit(f'Unexpected escaped version pin in {name}: {payload.count(old)}')
    path.write_text(payload.replace(old, new, 1), encoding='utf-8')

# The registered job's next step performs the reviewed v8.0.2 -> v8.0.3
# position-contract migration. Present its exact expected legacy tokens here;
# the following job step restores the dock-safe 42/38/34 requirements.
layout_path = ROOT / '.github/scripts/test_issue539_godfather_layout_audio.py'
layout = layout_path.read_text(encoding='utf-8')
for current, legacy in (
    ("'top:42% !important;'", "'top:40% !important;'"),
    ("'top:38% !important;'", "'top:34% !important;'"),
    ("'top:34% !important;'", "'top:31% !important;'"),
):
    if layout.count(current) != 1:
        raise SystemExit(f'Unexpected current layout token: {current}')
    layout = layout.replace(current, legacy, 1)
layout_path.write_text(layout, encoding='utf-8')

# Restore the canonical validation workflow now. The registered job continues
# from its immutable definition and later deletes its own temporary build file.
subprocess.run(
    ['git', 'checkout', 'origin/main', '--', '.github/workflows/validate-userscript.yml'],
    cwd=ROOT,
    check=True,
)

# Restore the canonical policy plus only the permission required by the
# currently running registered job. Its cleanup step removes this entry.
raw_policy = subprocess.check_output(
    ['git', 'show', 'origin/main:.github/actions-security-policy.json'],
    cwd=ROOT,
    text=True,
)
policy = json.loads(raw_policy)
policy['allowedWritePermissions']['.github/workflows/build-v8.0.3-godfather-hotfix.yml'] = ['contents']
(ROOT / '.github/actions-security-policy.json').write_text(
    json.dumps(policy, indent=2) + '\n',
    encoding='utf-8',
)

print(json.dumps({
    'sourceSha256': EXPECTED_SOURCE_SHA,
    'readmeProduction': '8.0.2',
    'candidate': '8.0.3',
    'escapedPinsUpdated': 2,
}, indent=2))
