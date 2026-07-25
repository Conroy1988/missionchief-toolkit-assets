#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
STATIC = ROOT / '.github' / 'scripts' / 'test_issue517_incident_command_wire.py'
RUNTIME = ROOT / '.github' / 'scripts' / 'test_issue517_incident_command_wire_runtime.js'
FIXTURE = ROOT / '.github' / 'fixtures' / 'main-style-source-headroom.json'
CHANGELOG = ROOT / 'CHANGELOG.md'
README = ROOT / 'README.md'
HELP = ROOT / 'help' / 'index.html'
SELF = ROOT / '.github' / 'issue519' / 'apply_v713_candidate.py'
WORKFLOW = ROOT / '.github' / 'workflows' / 'apply-issue519-v713-candidate.yml'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected one {label}, found {count}')
    return text.replace(old, new, 1)


def update_headroom(source: str) -> None:
    start = source.index('function installMainStyles()')
    a = source.index('addStyle(`', start) + len('addStyle(`')
    metric = source.index("recordStartupMetric('stylesheetInstallMs'", a)
    b = source.rfind('`);', a, metric)
    raw = source[a:b]
    lines = raw.split('\n')
    canonical = re.sub(
        r'\n[\t ]*}',
        '}',
        '\n'.join(line for i, line in enumerate(lines) if not (0 < i < len(lines) - 1 and not line.strip())),
    )
    payload = json.loads(FIXTURE.read_text(encoding='utf-8'))
    candidate = payload['v7Candidate']
    candidate.update({
        'issue': 519,
        'version': '7.1.3',
        'sourceBytes': len(source.encode('utf-8')),
        'sourceLines': len(source.splitlines()),
        'sourceSha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
        'templateBytes': len(raw.encode('utf-8')),
        'templateLines': len(lines),
        'templateSha256': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
        'canonicalCssSha256': hashlib.sha256(canonical.encode('utf-8')).hexdigest(),
    })
    FIXTURE.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    source = SOURCE.read_text(encoding='utf-8')
    source = replace_once(source, '// @version      7.1.2', '// @version      7.1.3', 'metadata version')
    source = replace_once(source, "version: '7.1.2',", "version: '7.1.3',", 'runtime version')

    old_gate = """        const reducedMotion = Boolean(pageWindow.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);
        if (!feed?.isConnected || count <= 1 || state.economyMode || reducedMotion || majorIncidentFeedManualPaused || majorIncidentFeedExpanded || document.hidden) {"""
    new_gate = """        if (!feed?.isConnected || count <= 1 || state.economyMode || majorIncidentFeedManualPaused || majorIncidentFeedExpanded || document.hidden) {"""
    source = replace_once(source, old_gate, new_gate, 'reduced-motion scheduler blockade')

    track_rule = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-track{display:flex!important;align-items:stretch!important;width:100%!important;min-width:100%!important;height:100%!important;animation:none!important;will-change:transform;transition:transform .46s cubic-bezier(.22,.75,.18,1)!important}'
    instant_rule = track_rule + '\n        @media (prefers-reduced-motion:reduce){#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-track{transition:none!important}}'
    source = replace_once(source, track_rule, instant_rule, 'reduced-motion instant transition rule')
    SOURCE.write_text(source, encoding='utf-8')

    static = STATIC.read_text(encoding='utf-8')
    static = replace_once(static, "== '7.1.2'", "== '7.1.3'", 'static contract version')
    static = replace_once(
        static,
        "    assert 'pageWindow.matchMedia' in source and 'prefers-reduced-motion: reduce' in source\n",
        "    assert 'prefers-reduced-motion:reduce' in source\n"
        "    assert 'reducedMotion' not in schedule\n"
        "    assert \"state.economyMode || majorIncidentFeedManualPaused\" in schedule\n"
        "    assert '@media (prefers-reduced-motion:reduce)' in source\n"
        "    assert '.mcms-incident-feed-track{transition:none!important}' in source\n",
        'reduced-motion static assertions',
    )
    STATIC.write_text(static, encoding='utf-8')

    runtime = RUNTIME.read_text(encoding='utf-8')
    runtime = replace_once(
        runtime,
        'pageWindow:{ matchMedia:()=>({matches:false}) },',
        'pageWindow:{ matchMedia:()=>({matches:true}) },',
        'runtime reduced-motion browser state',
    )
    runtime = replace_once(
        runtime,
        "console.log('Issue #517 Incident Command Wire runtime contract passed.');",
        "assert.equal(sandbox.pageWindow.matchMedia('(prefers-reduced-motion: reduce)').matches, true);\n"
        "console.log('Issue #517 Incident Command Wire runtime contract passed with reduced motion enabled.');",
        'runtime reduced-motion evidence',
    )
    RUNTIME.write_text(runtime, encoding='utf-8')

    changelog = CHANGELOG.read_text(encoding='utf-8')
    marker = '## [7.1.2] - 2026-07-25'
    section = """## [7.1.3] - 2026-07-25

### Incident Command Wire reduced-motion autoplay recovery

- Removed the browser reduced-motion preference from the automatic card scheduling blockade.
- Continued discrete incident progression at the normal cadence while respecting manual Pause, hidden-tab, Economy Mode, expanded-queue and interaction gates.
- Disabled the sliding track transition under reduced motion so cards change instantly without motion animation.
- Changed the executable runtime contract to run with `prefers-reduced-motion: reduce` enabled and prove Play plus continued automatic progression.
- Kept previous/next navigation, queue expansion, theme styling and responsive control containment unchanged.

"""
    if marker not in changelog or '## [7.1.3]' in changelog:
        raise SystemExit('Unexpected changelog state')
    CHANGELOG.write_text(changelog.replace(marker, section + marker, 1), encoding='utf-8')

    readme = README.read_text(encoding='utf-8')
    readme, count = re.subn(
        r'## \*\*Current verified release: `v[^`]+`[^\n]*\*\*',
        '## **Current verified release: `v7.1.2` · Development candidate: `v7.1.3` — Reduced-motion autoplay recovery**',
        readme,
        count=1,
    )
    if count != 1:
        raise SystemExit(f'Expected one README release marker, found {count}')
    README.write_text(readme, encoding='utf-8')

    help_text = HELP.read_text(encoding='utf-8')
    help_text = help_text.replace('v7.1.2 candidate', 'v7.1.3 candidate')
    help_text = help_text.replace('Incident Command Wire live rotation recovery', 'Incident Command Wire reduced-motion autoplay recovery')
    help_text, count = re.subn(
        r'<main><section class="notice"><h2>.*?</p></section>',
        '<main><section class="notice"><h2>What changed in v7.1.3</h2><p>Reduced-motion mode now removes the sliding animation without disabling automatic incident progression. Play remains active and cards change instantly at the normal cadence.</p></section>',
        help_text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit(f'Expected one Help Centre notice, found {count}')
    HELP.write_text(help_text, encoding='utf-8')

    update_headroom(source)

    for path in (SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print('v7.1.3 reduced-motion autoplay candidate applied.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
