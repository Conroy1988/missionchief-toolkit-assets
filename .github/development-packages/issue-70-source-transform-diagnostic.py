#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

package = Path('.github/development-packages/issue-70-source-transform.py')
result = subprocess.run(
    [sys.executable, str(package)],
    cwd=Path.cwd(),
    capture_output=True,
    text=True,
)
if result.returncode == 0:
    package.unlink(missing_ok=True)
    print(result.stdout)
else:
    subprocess.run(['git', 'reset', '--hard', 'HEAD'], check=True)
    package.unlink(missing_ok=True)
    report = Path('.github/audits/issue-70-source-transform-failure.md')
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        '# Issue #70 source transformation failure\n\n'
        '## Standard output\n\n```text\n' + result.stdout + '\n```\n\n'
        '## Standard error\n\n```text\n' + result.stderr + '\n```\n',
        encoding='utf-8',
    )
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
