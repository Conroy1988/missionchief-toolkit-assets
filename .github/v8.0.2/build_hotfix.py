#!/usr/bin/env python3
'''Build the exact Toolkit v8.0.2 Godfather layout and audio hotfix.'''
from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATHS = (
    ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt',
)
AUDIO_PARTS = ROOT / '.github/v8.0.2/audio-parts'
AUDIO_PATH = ROOT / 'themes/godfather/audio/godfather-flash-payout.mp3'

BASE_SOURCE_SHA = 'f64d180da6fabbbe775353e914529a7353427f6dafe3ee2da84cc96d5fc6f525'
SOURCE_SHA = '5a33ed92ca3c3207d421654c8cd9370f95a6127a4ec759b4924412f19b36c474'
AUDIO_SHA = '53160bd03bacf043ea3b0ffbd202163c2621e16a47ecd0f7090bfeacaf00b0d4'
AUDIO_BYTES = 136254

EXPECTED_METRICS = {
    'sourceBytes': 1603031,
    'sourceLines': 24164,
    'sourceSha256': SOURCE_SHA,
    'templateBytes': 682308,
    'templateLines': 7833,
    'templateSha256': 'a3681e77153ad29050058f5ed2c691dfa88892d66d38074f26c2129601956a6b',
    'canonicalCssSha256': 'f16e1ce9b8f6e1a3fd095833205fd5ba48650508e2b67d6ff87f68deec26cf5b',
}

HOTFIX_CSS = r'''        /* v8.0.2 — Godfather launcher, dock and payout placement hotfix. */
        html[data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} .mcms-shell::before {
            width:22px !important;
            height:22px !important;
            left:-5px !important;
            top:-7px !important;
            opacity:.92 !important;
        }
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} {
            grid-template-columns:109px minmax(0,1fr) !important;
            column-gap:5px !important;
            row-gap:5px !important;
        }
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} .mcms-launch-row {
            width:109px !important;
            gap:5px !important;
        }
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} .mcms-shell {
            width:52px !important;
            height:44px !important;
            min-height:44px !important;
            flex-direction:column !important;
        }
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} .mcms-menu-btn {
            min-width:0 !important;
            min-height:0 !important;
            height:auto !important;
            flex:1 1 auto !important;
            font-size:19px !important;
        }
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} .mcms-dock-toggle-btn {
            width:100% !important;
            min-width:0 !important;
            height:14px !important;
            min-height:14px !important;
            flex:0 0 14px !important;
            border-left:0 !important;
            border-top:1px solid rgba(190,147,66,.42) !important;
            font-size:10px !important;
        }
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} .mcms-floating-filter {
            gap:5px !important;
        }
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} .mcms-float-btn {
            height:44px !important;
            min-height:44px !important;
            padding:0 5px !important;
            border-radius:9px !important;
        }
        html[data-mcms-tablet-active="true"][data-mcms-ui-theme="godfather"] #${SCRIPT.controlId} .mcms-float-label-tablet {
            font-size:clamp(8.5px,1vw,9.75px) !important;
            line-height:1 !important;
        }
        #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {
            top:40% !important;
        }
        html[data-mcms-tablet-active="true"] #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {
            top:34% !important;
        }
        html[data-mcms-mobile-active="true"] #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {
            top:31% !important;
        }

'''


def require_count(text: str, token: str, count: int = 1) -> None:
    actual = text.count(token)
    if actual != count:
        raise SystemExit(f'Expected {count} occurrence(s) of {token!r}, found {actual}')


def source_metrics(text: str) -> dict[str, int | str]:
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
            line for index, line in enumerate(lines)
            if not (0 < index < len(lines) - 1 and not line.strip())
        ),
    )
    return {
        'sourceBytes': len(text.encode()),
        'sourceLines': len(text.splitlines()),
        'sourceSha256': hashlib.sha256(text.encode()).hexdigest(),
        'templateBytes': len(raw.encode()),
        'templateLines': len(lines),
        'templateSha256': hashlib.sha256(raw.encode()).hexdigest(),
        'canonicalCssSha256': hashlib.sha256(canonical.encode()).hexdigest(),
    }


payloads = [path.read_text(encoding='utf-8') for path in SOURCE_PATHS]
if len(set(payloads)) != 1:
    raise SystemExit('Canonical source and distribution mirrors are not byte-identical')
source = payloads[0]
if hashlib.sha256(source.encode()).hexdigest() != BASE_SOURCE_SHA:
    raise SystemExit('v8.0.1 source does not match the guarded hotfix baseline')

require_count(source, '// @version      8.0.1')
require_count(source, "version: '8.0.1'")
require_count(source, '/* v8.0.1 — The Godfather: complete original old-money command interface. */')
audio_url = 'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/themes/godfather/audio/godfather-flash-payout.mp3'
require_count(source, audio_url)
anchor = '        /* v7.1.0 Incident Command Wire: bounded, theme-aware card navigation. */'
require_count(source, anchor)

source = source.replace('// @version      8.0.1', '// @version      8.0.2', 1)
source = source.replace("version: '8.0.1'", "version: '8.0.2'", 1)
source = source.replace(
    '/* v8.0.1 — The Godfather: complete original old-money command interface. */',
    '/* v8.0.2 — The Godfather: complete original old-money command interface. */',
    1,
)
source = source.replace(audio_url, audio_url + '?v=8.0.2', 1)
source = source.replace(anchor, HOTFIX_CSS + anchor, 1)
actual_metrics = source_metrics(source)
if actual_metrics != EXPECTED_METRICS:
    raise SystemExit(f'Generated source metrics differ from reviewed candidate: {actual_metrics}')
for path in SOURCE_PATHS:
    path.write_text(source, encoding='utf-8')

parts = sorted(AUDIO_PARTS.glob('part-*.b64'))
if len(parts) != 5:
    raise SystemExit(f'Expected 5 audio transport parts, found {len(parts)}')
lengths = [len(part.read_text(encoding='ascii').strip()) for part in parts]
expected_lengths = [12000, 12000, 60000, 60000, 37672]
if lengths != expected_lengths:
    raise SystemExit(f'Unexpected audio transport part lengths: {lengths}')
encoded = ''.join(part.read_text(encoding='ascii').strip() for part in parts)
audio = base64.b64decode(encoded, validate=True)
if len(audio) != AUDIO_BYTES:
    raise SystemExit(f'Replacement audio size mismatch: {len(audio)}')
if hashlib.sha256(audio).hexdigest() != AUDIO_SHA:
    raise SystemExit('Replacement audio SHA-256 mismatch')
AUDIO_PATH.write_bytes(audio)

fixture_path = ROOT / '.github/fixtures/main-style-source-headroom.json'
fixture = json.loads(fixture_path.read_text(encoding='utf-8'))
candidate = fixture['v8Candidate']
candidate.update({
    'issue': 539,
    'version': '8.0.2',
    **EXPECTED_METRICS,
    'approvedGrowth': {
        'sourceBytes': 38134,
        'sourceLines': 581,
        'templateBytes': 35465,
        'templateLines': 553,
    },
    'scope': 'Issue #539 Godfather Tablet control geometry, unobstructed payout placement and exact replacement audio',
})
fixture_path.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

contract_path = ROOT / '.github/scripts/test_v8_godfather_contract.py'
contract = contract_path.read_text(encoding='utf-8')
require_count(contract, BASE_SOURCE_SHA)
old_audio_sha = '6ac631584e9df05ff821a6203ee24d1a6df7cf84d4f946713145a4b3f9502d45'
require_count(contract, old_audio_sha)
contract = contract.replace(BASE_SOURCE_SHA, SOURCE_SHA)
contract = contract.replace(old_audio_sha, AUDIO_SHA)
contract = contract.replace('8.0.1', '8.0.2')
contract = contract.replace('len(payload) == 24903', f'len(payload) == {AUDIO_BYTES}')
contract_path.write_text(contract, encoding='utf-8')

issue537_path = ROOT / '.github/scripts/test_issue537_godfather_css_activation.py'
issue537 = issue537_path.read_text(encoding='utf-8')
issue537 = issue537.replace(BASE_SOURCE_SHA, SOURCE_SHA).replace('8.0.1', '8.0.2')
issue537_path.write_text(issue537, encoding='utf-8')

issue530_path = ROOT / '.github/scripts/test_issue530_transport_sweep_discharge_confirmation.py'
issue530 = issue530_path.read_text(encoding='utf-8')
require_count(issue530, "== '8.0.1'")
issue530_path.write_text(issue530.replace("== '8.0.1'", "== '8.0.2'"), encoding='utf-8')

issue539_path = ROOT / '.github/scripts/test_issue539_godfather_layout_audio.py'
issue539_path.write_text(f'''#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
SOURCE = SOURCE_PATH.read_text(encoding='utf-8')
EXPECTED_SOURCE_SHA = '{SOURCE_SHA}'
EXPECTED_AUDIO_SHA = '{AUDIO_SHA}'
EXPECTED_AUDIO_BYTES = {AUDIO_BYTES}

assert hashlib.sha256(SOURCE.encode()).hexdigest() == EXPECTED_SOURCE_SHA
assert re.search(r'(?m)^//\\s*@version\\s+8\\.0\\.2$', SOURCE)
assert 'godfather-flash-payout.mp3?v=8.0.2' in SOURCE

marker = '/* v8.0.2 — Godfather launcher, dock and payout placement hotfix. */'
start = SOURCE.index(marker)
end = SOURCE.index('/* v7.1.0 Incident Command Wire:', start)
css = SOURCE[start:end]
assert start > SOURCE.rfind('html[data-mcms-tablet-active="true"] #${{SCRIPT.controlId}} .mcms-float-btn', 0, start)
for token in (
    'width:22px !important;',
    'height:22px !important;',
    'left:-5px !important;',
    'top:-7px !important;',
    'grid-template-columns:109px minmax(0,1fr) !important;',
    'width:52px !important;',
    'height:44px !important;',
    'min-height:44px !important;',
    'top:40% !important;',
    'top:34% !important;',
    'top:31% !important;',
):
    assert token in css, token
assert css.count('height:44px !important;') >= 2
seal = SOURCE[SOURCE.index('.mcms-shell::before', SOURCE.index('/* v8.0.2 — The Godfather')):start]
assert 'pointer-events:none !important;' in seal

audio_path = ROOT / 'themes/godfather/audio/godfather-flash-payout.mp3'
audio = audio_path.read_bytes()
assert len(audio) == EXPECTED_AUDIO_BYTES
assert hashlib.sha256(audio).hexdigest() == EXPECTED_AUDIO_SHA
assert audio[:2] in (b'\\xff\\xfb', b'\\xff\\xf3', b'\\xff\\xf2') or audio.startswith(b'ID3')

manifest = json.loads((ROOT / 'themes/godfather/manifest.json').read_text(encoding='utf-8'))
assert manifest['toolkitVersion'] == '8.0.2'
assert manifest['audio']['sha256'] == EXPECTED_AUDIO_SHA
assert manifest['audio']['channels'] == 2
assert manifest['audio']['bitRateBps'] == 128000
assert manifest['audio']['byteSize'] == EXPECTED_AUDIO_BYTES

for path in (
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt',
):
    assert path.read_bytes() == SOURCE_PATH.read_bytes(), path

print('Issue #539 Godfather layout and replacement-audio contract passed.')
''', encoding='utf-8')

preflight_path = ROOT / '.github/scripts/run_userscript_preflight.sh'
preflight = preflight_path.read_text(encoding='utf-8')
anchor_contract = '.github/scripts/test_issue537_godfather_css_activation.py'
require_count(preflight, anchor_contract)
if '.github/scripts/test_issue539_godfather_layout_audio.py' not in preflight:
    preflight = preflight.replace(
        anchor_contract,
        anchor_contract + ' .github/scripts/test_issue539_godfather_layout_audio.py',
    )
preflight_path.write_text(preflight, encoding='utf-8')

manifest_path = ROOT / 'themes/godfather/manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest.update({'packageVersion': '1.0.2', 'toolkitVersion': '8.0.2'})
manifest['audio'] = {
    'durationSeconds': 8.515875,
    'sampleRateHz': 44100,
    'channels': 2,
    'bitRateBps': 128000,
    'byteSize': AUDIO_BYTES,
    'sha256': AUDIO_SHA,
    'loading': 'Lazy; requested only when the Godfather Offer payout is played.',
}
manifest['notes'] = (
    'Original Toolkit-made old-money command system. v8.0.2 contains the launcher decoration, '
    'restores compact Tablet control geometry, raises the payout clear of the command dock and '
    'uses the user-supplied payout MP3 without processing.'
)
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

help_manifest_path = ROOT / 'help/manifest.json'
help_manifest = json.loads(help_manifest_path.read_text(encoding='utf-8'))
help_manifest['guideVersion'] = '8.0.2'
help_manifest['toolkitVersion'] = '8.0.2'
help_manifest['runtimeGuidePatch'] = (
    'Toolkit v8.0.2 contains the Godfather launcher decoration, restores compact Tablet controls, '
    'raises the Offer payout above the command dock and replaces its audio byte-for-byte.'
)
help_manifest_path.write_text(json.dumps(help_manifest, indent=2) + '\n', encoding='utf-8')

help_path = ROOT / 'help/index.html'
help_text = help_path.read_text(encoding='utf-8').replace('v8.0.1', 'v8.0.2')
help_text = re.sub(
    r'<section class="notice"><h2>What changed in v8\.0\.2</h2><p>.*?</p></section>',
    '<section class="notice"><h2>What changed in v8.0.2</h2><p>The Godfather launcher decoration is contained, Tablet controls return to compact 44px geometry, the Offer payout sits above the command dock, and the newly supplied stereo MP3 is used byte-for-byte.</p></section>',
    help_text,
    count=1,
)
help_path.write_text(help_text, encoding='utf-8')

changelog_path = ROOT / 'CHANGELOG.md'
changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## [8.0.2] - 2026-07-26

### Godfather layout and payout-audio hotfix

- Contained the decorative family seal so it no longer overlaps the launcher or adjacent controls.
- Restored compact Godfather Tablet controls with 44px safe touch targets and reduced visual footprint.
- Raised the Godfather Offer payout on Desktop, Tablet and mobile so the command dock no longer obstructs it.
- Replaced the payout MP3 byte-for-byte with the user-supplied 8.516-second stereo 128 kbps file and versioned its URL to prevent stale audio caching.
- Added permanent launcher geometry, payout placement and exact audio digest/byte-size contracts.

'''
if '## [8.0.2]' not in changelog:
    changelog = changelog.replace('# Changelog\n\n', '# Changelog\n\n' + entry, 1)
changelog_path.write_text(changelog, encoding='utf-8')

readme_path = ROOT / 'README.md'
readme = readme_path.read_text(encoding='utf-8')
require_count(readme, '## **Current verified release: `v8.0.0` · Development candidate: `v8.0.1`**')
readme = readme.replace(
    '## **Current verified release: `v8.0.0` · Development candidate: `v8.0.1`**\n### **Critical Godfather interface activation hotfix**',
    '## **Current verified release: `v8.0.1` · Development candidate: `v8.0.2`**\n### **Godfather layout and payout-audio hotfix**',
    1,
)
readme = readme.replace('#current-release-signal--v800', '#current-release-signal--v801')
readme = readme.replace('GitHub Release `v8.0.0` published', 'GitHub Release `v8.0.1` published', 1)

signal_start = readme.index('# v8.0.1 hotfix signal')
signal_end = readme.index('\n---\n', signal_start)
signal = '''# v8.0.2 hotfix signal

> **CRITICAL GODFATHER LAYOUT AND AUDIO REPAIR // DEVELOPMENT BRANCH ONLY**

The verified production release is **v8.0.1**. Candidate **v8.0.2** contains the decorative family seal, restores compact Tablet controls, raises the Offer payout above the command dock and replaces the payout audio byte-for-byte with the newly supplied stereo MP3. Production remains on v8.0.1 until the guarded hotfix release completes.
'''
readme = readme[:signal_start] + signal + readme[signal_end:]

release_start = readme.index('# Current release signal — v8.0.0')
release_end = readme.index('\n---\n', release_start)
release_section = '''# Current release signal — v8.0.1

> **CHANNEL UPDATE // GODFATHER STYLESHEET ACTIVATION**

Version 8.0.1 restored the complete Godfather stylesheet boundary and added permanent top-level CSS-depth validation.

- The Godfather command system now activates as a complete interface.
- The v7 native MissionChief boundary and every retained operational system remain in force.
- Candidate v8.0.2 addresses the remaining Tablet layout, payout placement and replacement-audio defects.
'''
readme = readme[:release_start] + release_section + readme[release_end:]
readme = readme.replace('| **Version** | `7.1.6` |', '| **Version** | `8.0.1` |', 1)
readme = readme.replace(
    '| **Release focus** | Native Discharge patient confirmation handling |',
    '| **Release focus** | Godfather stylesheet activation hotfix |',
    1,
)
readme = readme.replace(
    '| **Validated SHA-256** | `6358f5b25b6b278fac409a78d2b7b1c0bfd88bb808810dbf484dcd86f1f99386` |',
    '| **Validated SHA-256** | `f64d180da6fabbbe775353e914529a7353427f6dafe3ee2da84cc96d5fc6f525` |',
    1,
)
readme = readme.replace(
    '| **GitHub Release** | [`v7.1.6`](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v7.1.6) |',
    '| **GitHub Release** | [`v8.0.1`](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v8.0.1) |',
    1,
)
readme = readme.replace(
    '| **Private backup** | `e4b2617762ca4a09c569966861660cab55712f32` |',
    '| **Private backup** | `5b565f5766a429888c0aea809532ec5e3773d792` |',
    1,
)
readme_path.write_text(readme, encoding='utf-8')

print(json.dumps({
    'sourceSha256': SOURCE_SHA,
    'audioSha256': AUDIO_SHA,
    'sourceMetrics': actual_metrics,
}, indent=2))
