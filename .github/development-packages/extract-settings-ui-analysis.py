#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
OUT_DIR = ROOT / '.github' / 'development-analysis'
FUNCTION_OUT = OUT_DIR / 'settings-ui-functions.txt'
INVENTORY_OUT = OUT_DIR / 'settings-ui-inventory.json'

FUNCTION_NAMES = [
    'loadState',
    'saveState',
    'toggleFeature',
    'createPanel',
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


def extract_object_candidates(source: str, masked: str) -> list[dict]:
    results: list[dict] = []
    patterns = [
        re.compile(r'\bconst\s+([A-Za-z_$][\w$]*(?:DEFAULT|Default|default)[A-Za-z_$\w]*)\s*=\s*(?:Object\.freeze\s*\()?\s*\{'),
        re.compile(r'\bconst\s+([A-Za-z_$][\w$]*(?:STATE|State|state)[A-Za-z_$\w]*)\s*=\s*(?:Object\.freeze\s*\()?\s*\{'),
    ]
    seen: set[tuple[str, int]] = set()
    for pattern in patterns:
        for match in pattern.finditer(masked):
            name = match.group(1)
            open_pos = masked.find('{', match.start())
            close_pos = matching_brace(masked, open_pos)
            key = (name, match.start())
            if key in seen:
                continue
            seen.add(key)
            text = source[match.start():close_pos + 1]
            line = source.count('\n', 0, match.start()) + 1
            if len(text) <= 60000:
                results.append({'name': name, 'line': line, 'source': text})
    return results


def literal_values(text: str, patterns: list[str]) -> list[str]:
    values: set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            value = next((group for group in match.groups() if group is not None), None)
            if value:
                values.add(value)
    return sorted(values)


def main() -> int:
    source = SOURCE.read_text(encoding='utf-8')
    masked = mask_non_code(source)
    functions: dict[str, dict] = {}
    sections: list[str] = []
    for name in FUNCTION_NAMES:
        body, line = extract_function(source, masked, name)
        functions[name] = {'line': line, 'source': body}
        sections.append(f'===== {name} @ line {line} =====\n{body}\n')

    create_panel = functions['createPanel']['source']
    handler_text = '\n'.join(functions[name]['source'] for name in ('createPanel', 'toggleFeature', 'handleSettingChange'))

    data_actions = literal_values(create_panel, [
        r'data-action\s*=\s*"([^"]+)"',
        r"data-action\s*=\s*'([^']+)'",
        r'dataset\.action\s*=\s*"([^"]+)"',
        r"dataset\.action\s*=\s*'([^']+)'",
    ])
    data_settings = literal_values(create_panel, [
        r'data-setting\s*=\s*"([^"]+)"',
        r"data-setting\s*=\s*'([^']+)'",
        r'dataset\.setting\s*=\s*"([^"]+)"',
        r"dataset\.setting\s*=\s*'([^']+)'",
    ])
    route_literals = literal_values(handler_text, [
        r'\bcase\s+["\']([^"\']+)["\']\s*:',
        r'\b(?:action|name|key|setting|feature)\s*===\s*["\']([^"\']+)["\']',
        r'["\']([^"\']+)["\']\s*===\s*(?:action|name|key|setting|feature)\b',
        r'\.includes\s*\(\s*["\']([^"\']+)["\']\s*\)',
    ])

    object_candidates = extract_object_candidates(source, masked)
    inventory = {
        'version': re.search(r'^//\s*@version\s+(.+)$', source, re.MULTILINE).group(1).strip(),
        'functions': {name: {'line': item['line'], 'characters': len(item['source'])} for name, item in functions.items()},
        'dataActions': data_actions,
        'dataSettings': data_settings,
        'routeLiterals': route_literals,
        'objectCandidates': object_candidates,
        'storageKeys': sorted(set(re.findall(r'["\'](mc_[A-Za-z0-9_:-]+)["\']', source))),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FUNCTION_OUT.write_text('\n'.join(sections), encoding='utf-8')
    INVENTORY_OUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
