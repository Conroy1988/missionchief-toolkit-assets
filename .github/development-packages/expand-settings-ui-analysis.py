#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
OUTPUT = ROOT / '.github' / 'development-analysis' / 'settings-ui-expanded-functions.txt'

FUNCTION_NAMES = [
    'defaultState',
    'loadState',
    'saveState',
    'applyLoadedConfiguration',
    'exportToolkitConfig',
    'looksLikeToolkitState',
    'extractImportedToolkitState',
    'extractImportedDiscordWebhook',
    'extractImportedFinancialVaultCredential',
    'extractImportedFinancialVaultStore',
    'normaliseImportedFinanceVaultCredential',
    'normaliseImportedFinanceVaultStore',
    'describePrivateImport',
    'applyImportedToolkitSettings',
    'importToolkitConfigFile',
    'resetToolkitConfiguration',
    'applyUiTheme',
    'applyTheme',
    'setActiveTab',
    'applyPosition',
    'toggleFeature',
    'makeToggleButton',
    'handleAction',
    'handleSettingChange',
    'updateUI',
]


def mask_non_code(source: str) -> str:
    chars = list(source)
    i = 0
    state = 'code'
    quote = ''
    while i < len(chars):
        c = chars[i]
        n = chars[i + 1] if i + 1 < len(chars) else ''
        if state == 'code':
            if c == '/' and n == '/':
                chars[i] = chars[i + 1] = ' '
                i += 2
                state = 'line'
                continue
            if c == '/' and n == '*':
                chars[i] = chars[i + 1] = ' '
                i += 2
                state = 'block'
                continue
            if c in ('"', "'", '`'):
                quote = c
                i += 1
                state = 'string'
                continue
        elif state == 'line':
            if c == '\n':
                state = 'code'
            else:
                chars[i] = ' '
            i += 1
            continue
        elif state == 'block':
            if c == '*' and n == '/':
                chars[i] = chars[i + 1] = ' '
                i += 2
                state = 'code'
                continue
            if c != '\n':
                chars[i] = ' '
            i += 1
            continue
        elif state == 'string':
            if c == '\\':
                if c != '\n':
                    chars[i] = ' '
                if i + 1 < len(chars) and chars[i + 1] != '\n':
                    chars[i + 1] = ' '
                i += 2
                continue
            if c == quote:
                i += 1
                state = 'code'
                continue
            if c != '\n':
                chars[i] = ' '
            i += 1
            continue
        i += 1
    return ''.join(chars)


def matching_brace(masked: str, open_pos: int) -> int:
    depth = 0
    for index in range(open_pos, len(masked)):
        if masked[index] == '{':
            depth += 1
        elif masked[index] == '}':
            depth -= 1
            if depth == 0:
                return index
    raise RuntimeError(f'No closing brace for offset {open_pos}')


def extract_function(source: str, masked: str, name: str) -> tuple[str, int]:
    pattern = re.compile(rf'\b(?:async\s+)?function\s+{re.escape(name)}\s*\(')
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise RuntimeError(f'{name}: expected one declaration, found {len(matches)}')
    match = matches[0]
    open_pos = masked.find('{', match.start())
    close_pos = matching_brace(masked, open_pos)
    line = source.count('\n', 0, match.start()) + 1
    return source[match.start():close_pos + 1], line


def main() -> int:
    source = SOURCE.read_text(encoding='utf-8')
    masked = mask_non_code(source)
    sections = []
    for name in FUNCTION_NAMES:
        body, line = extract_function(source, masked, name)
        sections.append(f'===== {name} @ line {line} =====\n{body}\n')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text('\n'.join(sections), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
