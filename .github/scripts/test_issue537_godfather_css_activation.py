#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'


def version_tuple(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)', value)
    assert match, value
    return tuple(map(int, match.groups()))


def css_depth(text: str, stop: int) -> int:
    depth = 0
    quote = ''
    escaped = False
    comment = False
    index = 0
    while index < stop:
        char = text[index]
        nxt = text[index + 1] if index + 1 < stop else ''
        if comment:
            if char == '*' and nxt == '/':
                comment = False
                index += 2
                continue
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = ''
            index += 1
            continue
        if char == '/' and nxt == '*':
            comment = True
            index += 2
            continue
        if char in ("'", '"'):
            quote = char
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            assert depth >= 0, 'stylesheet closes below top-level depth'
        index += 1
    return depth


source = SOURCE.read_text(encoding='utf-8')
metadata = re.search(r'(?m)^//\s*@version\s+([^\s]+)$', source)
runtime = re.search(r"version:\s*'([^']+)'", source)
assert metadata and runtime
current_version = metadata.group(1)
assert current_version == runtime.group(1)
assert version_tuple(current_version) >= (8, 0, 4)
install = source.index('function installMainStyles()')
css_start = source.index('addStyle(`', install) + len('addStyle(`')
metric = source.index("recordStartupMetric('stylesheetInstallMs'", css_start)
css_end = source.rfind('`);', css_start, metric)
css = source[css_start:css_end]
godfather = css.index('/* v8.0.4 — The Godfather: complete original old-money command interface. */')
responsive = css.index('html[data-mcms-mobile-active="true"],', godfather)
assert css_depth(css, godfather) == 0, 'Godfather stylesheet starts inside another CSS rule'
assert css_depth(css, responsive) == 0, 'responsive stylesheet starts inside the Godfather block'
assert css_depth(css, len(css)) == 0, 'main stylesheet has unbalanced rule braces'
assert 'display:none !important;\n        }\n        /* v8.0.4 — The Godfather' in css
assert '}html[data-mcms-mobile-active="true"],' not in css
assert css.count('html[data-mcms-ui-theme="godfather"]') >= 100
for path in (ROOT / 'dist/MissionChief_Map_Command_Toolkit.user.js', ROOT / 'dist/MissionChief_Map_Command_Toolkit.txt'):
    assert path.read_bytes() == SOURCE.read_bytes(), f'distribution parity failed: {path}'
print(f'Issue #537 Godfather stylesheet activation contract passed for Toolkit {current_version}.')
