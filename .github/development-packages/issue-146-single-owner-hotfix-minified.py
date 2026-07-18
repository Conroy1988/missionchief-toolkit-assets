#!/usr/bin/env python3
from __future__ import annotations

import re
import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
RUNTIME_TEST = ROOT / '.github' / 'scripts' / 'test_mission_requirements_runtime.js'
CONTRACT_TEST = ROOT / '.github' / 'scripts' / 'test_mission_requirements_contract.py'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix.py'
SOURCE_COMMIT = '5ab224083e37e5bdde980cb23ab3ffe90a608084'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-single-owner-hotfix.payload.py'
IDENT = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$')


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def minify_js_fragment(fragment: str) -> str:
    out: list[str] = []
    i = 0
    state = 'code'
    quote = ''
    escaped = False
    regex_class = False
    pending_space = False
    previous_significant = ''

    def append_code(char: str) -> None:
        nonlocal pending_space, previous_significant
        previous = out[-1][-1] if out else ''
        if pending_space and previous:
            needs_space = (
                (previous in IDENT and char in IDENT)
                or (previous == '+' and char == '+')
                or (previous == '-' and char == '-')
                or (previous == '/' and char in '/*')
            )
            if needs_space:
                out.append(' ')
        pending_space = False
        out.append(char)
        if not char.isspace():
            previous_significant = (previous_significant + char)[-32:]

    while i < len(fragment):
        ch = fragment[i]
        nxt = fragment[i + 1] if i + 1 < len(fragment) else ''
        if state == 'string':
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                state = 'code'
            i += 1
            continue
        if state == 'regex':
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '[':
                regex_class = True
            elif ch == ']':
                regex_class = False
            elif ch == '/' and not regex_class:
                state = 'regex-flags'
            i += 1
            continue
        if state == 'regex-flags':
            if ch.isalpha():
                out.append(ch)
                i += 1
                continue
            state = 'code'
            continue
        if state == 'line-comment':
            if ch == '\n':
                state = 'code'
                pending_space = True
            i += 1
            continue
        if state == 'block-comment':
            if ch == '*' and nxt == '/':
                i += 2
                state = 'code'
                pending_space = True
            else:
                i += 1
            continue
        if ch.isspace():
            pending_space = True
            i += 1
            continue
        if ch == '/' and nxt == '/':
            state = 'line-comment'
            i += 2
            continue
        if ch == '/' and nxt == '*':
            state = 'block-comment'
            i += 2
            continue
        if ch in "'\"`":
            append_code(ch)
            state = 'string'
            quote = ch
            escaped = False
            i += 1
            continue
        if ch == '/':
            prefix = previous_significant
            if not prefix or prefix[-1] in '([{=,:;!&|?+-*%^~<>' or re.search(
                r'(?:return|throw|case|delete|void|typeof|instanceof|in|of|yield|await)$',
                prefix,
            ):
                append_code(ch)
                state = 'regex'
                escaped = False
                regex_class = False
                i += 1
                continue
        append_code(ch)
        i += 1
    return ''.join(out).strip()


def compact_region(text: str, start_token: str, end_token: str) -> str:
    start = text.find(start_token)
    end = text.find(end_token, start + len(start_token))
    if start < 0 or end < 0:
        raise AssertionError(f'missing compact region: {start_token} -> {end_token}')
    compact = '    ' + minify_js_fragment(text[start:end]) + '\n\n'
    return text[:start] + compact + text[end:]


payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)
old_identity = "    const id = normaliseMissionId(match?.[1] ?? (/^\\d+$/.test(raw) ? raw : null));\n    if (id !== null) return `mission:${id}`;"
new_identity = "    const id = Number(match?.[1] ?? (/^\\d+$/.test(raw) ? raw : NaN));\n    if (Number.isSafeInteger(id) && id > 0) return `mission:${id}`;"
if payload.count(old_identity) != 1:
    raise AssertionError('Issue #146 identity conversion anchor missing or duplicated')
payload = payload.replace(old_identity, new_identity, 1)

duplicate_validation = 'run(sys.executable, str(ROOT / ".github" / "scripts" / "validate_userscript.py"))\n'
if payload.count(duplicate_validation) != 1:
    raise AssertionError('Issue #146 duplicate canonical validation anchor missing or duplicated')
payload = payload.replace(duplicate_validation, '', 1)

budget_index = payload.find('final = SOURCE.read_text(encoding="utf-8")\n')
if budget_index < 0:
    raise AssertionError('Issue #146 original budget block missing')
payload = payload[:budget_index] + "print('Issue #146 transformation and fixture checks passed')\n"

TEMP.write_text(payload, encoding='utf-8')
try:
    runpy.run_path(str(TEMP), run_name='__main__')
finally:
    TEMP.unlink(missing_ok=True)

source = SOURCE.read_text(encoding='utf-8')
source = compact_region(source, '    function missionRequirementsPrimaryRuntime() {', '    function missionRequirementsDocumentCss() {')
source = compact_region(source, '    function missionRequirementsHostPanels(source) {', '    function missionRequirementsRemoveRecord(source) {')
SOURCE.write_text(source, encoding='utf-8')

for relative in (
    '.github/development-packages/issue-146-single-owner-hotfix-corrected.py',
    '.github/development-packages/issue-146-single-owner-hotfix-fast.py',
    '.github/development-packages/issue-146-single-owner-hotfix-budget.py',
    '.github/diagnostics/issue-146-hotfix-failure.txt',
):
    (ROOT / relative).unlink(missing_ok=True)

run('node', '--check', str(SOURCE))
run('node', str(RUNTIME_TEST))
run(sys.executable, str(CONTRACT_TEST))

final = SOURCE.read_text(encoding='utf-8')
final_bytes = len(final.encode('utf-8'))
final_lines = final.count('\n') + 1
if final_bytes > 1_900_000 or final_lines > 31_000:
    raise AssertionError(f'v4.15.3 exceeds source budget after token-aware compaction: {final_bytes} bytes / {final_lines} lines')
print(f'Issue #146 v4.15.3 candidate fits source budget: {final_bytes} bytes / {final_lines} lines')
