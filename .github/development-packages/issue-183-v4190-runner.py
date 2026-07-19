#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REL = Path('.github/development-packages/issue-183-authoritative-requirements.py')
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-183-v4190-result.txt'


def patch_package(package: Path) -> None:
    text = package.read_text(encoding='utf-8')
    start = text.index("anchor = '''")
    end_marker = "source = replace_once(source, anchor, addition, 'authoritative reconciliation insertion')"
    end = text.index(end_marker, start) + len(end_marker)
    addition_start = text.index("addition = '''", start) + len("addition = '''")
    addition_end = text.index("'''\nsource = replace_once(source, anchor, addition", addition_start)
    full_addition = text[addition_start:addition_end]
    function_start = full_addition.index('    // Issue #183:')
    function_end = full_addition.rindex("\n\n    // Issue #181:")
    function_text = full_addition[function_start:function_end]
    replacement_lines = [
        'authoritative_function = ' + repr(function_text),
        "parse_start = source.index('function missionRequirementsParseSource(source)')",
        "return_at = source.index('        return { requirements, unresolved };', parse_start)",
        "insert_at = source.index('\\n    }', return_at) + len('\\n    }')",
        "source = source[:insert_at] + '\\n\\n' + authoritative_function + source[insert_at:]",
    ]
    package.write_text(text[:start] + '\n'.join(replacement_lines) + text[end:], encoding='utf-8')


with tempfile.TemporaryDirectory(prefix='issue-183-v4190-') as directory:
    work = Path(directory) / 'repository'
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('.git'))
    package = work / PACKAGE_REL
    patch_package(package)
    completed = subprocess.run(['python3', str(package)], cwd=work, text=True, capture_output=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        f'exit_code={completed.returncode}\n\n--- STDOUT ---\n{completed.stdout}\n--- STDERR ---\n{completed.stderr}',
        encoding='utf-8',
    )
print(REPORT.relative_to(ROOT))
