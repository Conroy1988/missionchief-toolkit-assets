#!/usr/bin/env python3
from __future__ import annotations

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
BASE_SOURCE_SHA = '5a33ed92ca3c3207d421654c8cd9370f95a6127a4ec759b4924412f19b36c474'
SOURCE_SHA = '773d6686fdcfe0af5901f54bdd58c58cf0ef8503bddaae354f32ed25879ac19b'
EXPECTED_METRICS = {
    'sourceBytes': 1604731,
    'sourceLines': 24195,
    'sourceSha256': SOURCE_SHA,
    'templateBytes': 683558,
    'templateLines': 7858,
    'templateSha256': 'cddf2bf9536cc8ca186415693ea7399c2734e60fcbe48890d20afec3dd06a898',
    'canonicalCssSha256': '313b4564e5d7225ac222c86e6886345a3c866940d53dff624f400e7b961e3c68',
}


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
    raise SystemExit('v8.0.2 source does not match guarded baseline')

for old, new in (
    ('// @version      8.0.2', '// @version      8.0.3'),
    ("version: '8.0.2'", "version: '8.0.3'"),
    ('godfather-flash-payout.mp3?v=8.0.2', 'godfather-flash-payout.mp3?v=8.0.3'),
    ('/* v8.0.2 — The Godfather: complete original old-money command interface. */', '/* v8.0.3 — The Godfather: complete original old-money command interface. */'),
    ('/* v8.0.2 — Godfather launcher, dock and payout placement hotfix. */', '/* v8.0.3 — Godfather launcher, dock and payout placement hotfix. */'),
):
    require_count(source, old)
    source = source.replace(old, new, 1)

require_count(source, 'const PAYOUT_FLASH_STEP_MS = 2000;')
source = source.replace('const PAYOUT_FLASH_STEP_MS = 2000;', 'const PAYOUT_FLASH_STEP_MS = 1000;', 1)

old = """        merged.payoutFlash.durationMs = normalisePayoutFlashDuration(merged.payoutFlash.durationMs);\n        merged.payoutFlash.template = PAYOUT_TEMPLATES[merged.payoutFlash.template] ? merged.payoutFlash.template : 'gta5';"""
new = """        const loadedPayoutDuration = Number(parsed?.payoutFlash?.durationMs);\n        merged.payoutFlash.durationMs = normalisePayoutFlashDuration(merged.payoutFlash.durationMs);\n        if (merged.uiTheme === 'godfather' && (!Number.isFinite(loadedPayoutDuration) || loadedPayoutDuration === 4000)) {\n        merged.payoutFlash.durationMs = 7000;\n        }\n        merged.payoutFlash.template = PAYOUT_TEMPLATES[merged.payoutFlash.template] ? merged.payoutFlash.template : 'gta5';"""
require_count(source, old)
source = source.replace(old, new, 1)

old = """        const pairedPayoutChanged = Boolean(pairedTemplate && state.payoutFlash.template !== pairedTemplate);\n        state.uiTheme = nextTheme;\n        if (pairedPayoutChanged) state.payoutFlash.template = pairedTemplate;"""
new = """        const pairedPayoutChanged = Boolean(pairedTemplate && state.payoutFlash.template !== pairedTemplate);\n        const godfatherDurationChanged = nextTheme === 'godfather' && state.payoutFlash.durationMs === 4000;\n        state.uiTheme = nextTheme;\n        if (pairedPayoutChanged) state.payoutFlash.template = pairedTemplate;\n        if (godfatherDurationChanged) state.payoutFlash.durationMs = 7000;"""
require_count(source, old)
source = source.replace(old, new, 1)

require_count(source, "godfather: 'The Godfather interface and Offer payout active'")
source = source.replace(
    "godfather: 'The Godfather interface and Offer payout active'",
    "godfather: 'The Godfather interface and 7-second Offer payout active'",
    1,
)

require_count(source, 'type="number" min="2" max="30" step="2" data-setting="payout-duration"')
source = source.replace(
    'type="number" min="2" max="30" step="2" data-setting="payout-duration"',
    'type="number" min="2" max="30" step="1" data-setting="payout-duration"',
    1,
)

old = """        #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n            top:40% !important;\n        }\n        html[data-mcms-tablet-active="true"] #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n            top:34% !important;\n        }\n        html[data-mcms-mobile-active="true"] #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n            top:31% !important;\n        }\n"""
new = """        #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n            top:42% !important;\n            margin-top:-24px !important;\n        }\n        html[data-mcms-tablet-active="true"] #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n            top:38% !important;\n            margin-top:-32px !important;\n        }\n        html[data-mcms-mobile-active="true"] #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n            top:34% !important;\n            margin-top:-28px !important;\n        }\n        @media (max-height:560px) {\n            #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n                top:50% !important;\n                margin-top:-48px !important;\n                min-height:210px !important;\n                padding:24px 38px 20px !important;\n            }\n            #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-title {\n                font-size:clamp(30px,4.5vw,52px) !important;\n            }\n            #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-amount {\n                font-size:clamp(34px,5vw,50px) !important;\n            }\n            html[data-mcms-tablet-active="true"] #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n                margin-top:-58px !important;\n            }\n            html[data-mcms-mobile-active="true"] #${SCRIPT.payoutFlashId}[data-template="godfatherOffer"] .mcms-payout-banner {\n                margin-top:-52px !important;\n                min-height:196px !important;\n                padding:34px 20px 20px !important;\n            }\n        }\n"""
require_count(source, old)
source = source.replace(old, new, 1)

actual = source_metrics(source)
if actual != EXPECTED_METRICS:
    raise SystemExit(f'Generated source metrics differ from reviewed candidate: {actual}')
for path in SOURCE_PATHS:
    path.write_text(source, encoding='utf-8')

fixture_path = ROOT / '.github/fixtures/main-style-source-headroom.json'
fixture = json.loads(fixture_path.read_text(encoding='utf-8'))
candidate = fixture['v8Candidate']
candidate.update({
    'issue': 541,
    'version': '8.0.3',
    **EXPECTED_METRICS,
    'approvedGrowth': {
        'sourceBytes': 39834,
        'sourceLines': 612,
        'templateBytes': 36715,
        'templateLines': 578,
    },
    'scope': 'Issue #541 Godfather seven-second default and dock-safe payout placement',
})
fixture_path.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

contract_path = ROOT / '.github/scripts/test_v8_godfather_contract.py'
contract = contract_path.read_text(encoding='utf-8')
require_count(contract, BASE_SOURCE_SHA)
contract = contract.replace(BASE_SOURCE_SHA, SOURCE_SHA)
contract = contract.replace('8.0.2', '8.0.3')
contract_path.write_text(contract, encoding='utf-8')

for test_name in (
    'test_issue537_godfather_css_activation.py',
    'test_issue539_godfather_layout_audio.py',
    'test_issue530_transport_sweep_discharge_confirmation.py',
):
    path = ROOT / '.github/scripts' / test_name
    text = path.read_text(encoding='utf-8')
    text = text.replace(BASE_SOURCE_SHA, SOURCE_SHA).replace('8.0.2', '8.0.3')
    path.write_text(text, encoding='utf-8')

issue541 = ROOT / '.github/scripts/test_issue541_godfather_duration_position.py'
issue541.write_text(f'''#!/usr/bin/env python3
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
SOURCE = SOURCE_PATH.read_text(encoding='utf-8')
assert hashlib.sha256(SOURCE.encode()).hexdigest() == '{SOURCE_SHA}'
assert re.search(r'(?m)^//\\s*@version\\s+8\\.0\\.3$', SOURCE)
for token in (
    'const PAYOUT_FLASH_STEP_MS = 1000;',
    "merged.uiTheme === 'godfather'",
    'merged.payoutFlash.durationMs = 7000;',
    "nextTheme === 'godfather' && state.payoutFlash.durationMs === 4000",
    "if (godfatherDurationChanged) state.payoutFlash.durationMs = 7000;",
    'step="1" data-setting="payout-duration"',
    'margin-top:-24px !important;',
    'margin-top:-32px !important;',
    'margin-top:-58px !important;',
    '@media (max-height:560px)',
    'min-height:210px !important;',
):
    assert token in SOURCE, token
for legacy in (
    'top:40% !important;',
    'top:34% !important;\n        }\n        html[data-mcms-tablet-active',
    'step="2" data-setting="payout-duration"',
):
    assert legacy not in SOURCE, legacy
for path in (
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt',
):
    assert path.read_bytes() == SOURCE_PATH.read_bytes(), path
print('Issue #541 Godfather duration and payout-position contract passed.')
''', encoding='utf-8')

preflight_path = ROOT / '.github/scripts/run_userscript_preflight.sh'
preflight = preflight_path.read_text(encoding='utf-8')
anchor = '.github/scripts/test_issue539_godfather_layout_audio.py'
require_count(preflight, anchor)
if '.github/scripts/test_issue541_godfather_duration_position.py' not in preflight:
    preflight = preflight.replace(anchor, anchor + ' .github/scripts/test_issue541_godfather_duration_position.py')
preflight_path.write_text(preflight, encoding='utf-8')

manifest_path = ROOT / 'themes/godfather/manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest.update({'packageVersion': '1.0.3', 'toolkitVersion': '8.0.3'})
manifest['notes'] = (
    'Original Toolkit-made old-money command system. v8.0.3 defaults the Godfather Offer payout '
    'to seven seconds when the global default is still active and keeps the full banner clear of the command dock.'
)
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

help_manifest_path = ROOT / 'help/manifest.json'
help_manifest = json.loads(help_manifest_path.read_text(encoding='utf-8'))
help_manifest['guideVersion'] = '8.0.3'
help_manifest['toolkitVersion'] = '8.0.3'
help_manifest['runtimeGuidePatch'] = (
    'Toolkit v8.0.3 defaults the Godfather Offer flash to seven seconds when the normal default is active '
    'and raises/compacts the payout on short viewports so it remains clear of the command dock.'
)
help_manifest_path.write_text(json.dumps(help_manifest, indent=2) + '\n', encoding='utf-8')

help_path = ROOT / 'help/index.html'
help_text = help_path.read_text(encoding='utf-8').replace('v8.0.2', 'v8.0.3')
help_path.write_text(help_text, encoding='utf-8')

changelog_path = ROOT / 'CHANGELOG.md'
changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## [8.0.3] - 2026-07-26

### Godfather duration and payout-position hotfix

- Defaults the Godfather Offer flash to seven seconds when the normal four-second default is still active.
- Allows one-second payout-duration steps so seven seconds remains a valid persisted value.
- Raises the Godfather payout and adds short-viewport compaction so the full banner clears the command dock.
- Adds a permanent Godfather duration and dock-clearance regression contract.

'''
if '## [8.0.3]' not in changelog:
    changelog = changelog.replace('# Changelog\n\n', '# Changelog\n\n' + entry, 1)
changelog_path.write_text(changelog, encoding='utf-8')

readme_path = ROOT / 'README.md'
readme = readme_path.read_text(encoding='utf-8')
readme = readme.replace('Development candidate: `v8.0.2`', 'Development candidate: `v8.0.3`')
readme_path.write_text(readme, encoding='utf-8')

print(json.dumps({'sourceSha256': SOURCE_SHA, 'sourceMetrics': actual}, indent=2))
