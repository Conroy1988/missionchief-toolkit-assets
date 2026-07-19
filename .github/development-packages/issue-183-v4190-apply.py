#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / '.github' / 'development-packages' / 'issue-183-authoritative-requirements.py'

text = PACKAGE.read_text(encoding='utf-8')
start = text.index("anchor = '''")
end_marker = "source = replace_once(source, anchor, addition, 'authoritative reconciliation insertion')"
end = text.index(end_marker, start) + len(end_marker)
addition_start = text.index("addition = '''", start) + len("addition = '''")
addition_end = text.index("'''\nsource = replace_once(source, anchor, addition", addition_start)
full_addition = text[addition_start:addition_end]
function_start = full_addition.index('    // Issue #183:')
function_end = full_addition.rindex("\n\n    // Issue #181:")
function_text = full_addition[function_start:function_end]
replacement = (
    'authoritative_function = ' + repr(function_text) + '\n'
    "parse_start = source.index('function missionRequirementsParseSource(source)')\n"
    "return_at = source.index('        return { requirements, unresolved };', parse_start)\n"
    "insert_at = source.index('\\n    }', return_at) + len('\\n    }')\n"
    "source = source[:insert_at] + '\\n\\n' + authoritative_function + source[insert_at:]"
)
text = text[:start] + replacement + text[end:]
PACKAGE.write_text(text, encoding='utf-8')

subprocess.run(['python3', str(PACKAGE)], cwd=ROOT, check=True)
PACKAGE.unlink(missing_ok=True)
for path in [
    ROOT / '.github' / 'diagnostics' / 'issue-183-package-result.txt',
    ROOT / '.github' / 'diagnostics' / 'issue-183-v4190-result.txt',
]:
    path.unlink(missing_ok=True)
