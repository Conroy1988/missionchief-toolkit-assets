#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package = root / '.github' / 'development-packages' / 'issue-212-selected-units-hotfix.py'
v2_package = root / '.github' / 'development-packages' / 'issue-212-selected-units-hotfix-v2.py'
text = package.read_text(encoding='utf-8')
replacements = {
    "assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 1, 'outer Available Units Police Car is selected');": "assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 3, 'all selected police-family vehicles contribute to the broad Police Car requirement');",
    "assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 0, 'deselecting the outer-window Police Car immediately clears Selected');": "assert.strictEqual(issue212Rows.find(item => item.key === 'police-car').selectedMin, 2, 'deselecting the IRV immediately removes one broad Police Car contribution');",
    '    ROOT / ".github" / "diagnostics" / "issue-212-observer-runtime.txt",\n': '    ROOT / ".github" / "diagnostics" / "issue-212-observer-runtime.txt",\n    ROOT / ".github" / "diagnostics" / "issue-212-hotfix-report.txt",\n    ROOT / ".github" / "diagnostics" / "issue-212-hotfix-v2-report.txt",\n',
    'subprocess.run(["node", ".github/scripts/test_mission_requirements_runtime.js"], cwd=ROOT, check=True)\n': 'for distribution in [ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js", ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"]:\n    distribution.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")\nsubprocess.run(["node", ".github/scripts/test_mission_requirements_runtime.js"], cwd=ROOT, check=True)\n',
}
for old, new in replacements.items():
    if text.count(old) != 1:
        raise AssertionError(f'Issue #212 v3 wrapper expected one package anchor: {old[:100]}')
    text = text.replace(old, new, 1)
package.write_text(text, encoding='utf-8')
subprocess.run(['python3', str(package.relative_to(root))], cwd=root, check=True)
v2_package.unlink(missing_ok=True)
Path(__file__).unlink()
print('Prepared fully validated v4.20.4 selected-unit hotfix')
