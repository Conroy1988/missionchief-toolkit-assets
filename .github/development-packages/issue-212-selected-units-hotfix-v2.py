#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package = root / '.github' / 'development-packages' / 'issue-212-selected-units-hotfix.py'
text = package.read_text(encoding='utf-8')
replacements = {
    "assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 1, 'outer Available Units Police Car is selected');": "assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 3, 'all selected police-family vehicles contribute to the broad Police Car requirement');",
    "assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 0, 'deselecting the outer-window Police Car immediately clears Selected');": "assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 2, 'deselecting the IRV immediately removes one broad Police Car contribution');",
    '    ROOT / ".github" / "diagnostics" / "issue-212-observer-runtime.txt",\n': '    ROOT / ".github" / "diagnostics" / "issue-212-observer-runtime.txt",\n    ROOT / ".github" / "diagnostics" / "issue-212-hotfix-report.txt",\n',
}
for old, new in replacements.items():
    if text.count(old) != 1:
        raise AssertionError(f'Issue #212 v2 wrapper expected one package anchor: {old[:80]}')
    text = text.replace(old, new, 1)
package.write_text(text, encoding='utf-8')
subprocess.run(['python3', str(package.relative_to(root))], cwd=root, check=True)
Path(__file__).unlink()
print('Prepared corrected v4.20.4 selected-unit hotfix')
