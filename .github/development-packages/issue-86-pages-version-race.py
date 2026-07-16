#!/usr/bin/env python3
from pathlib import Path

checker = Path('.github/scripts/check_pages_live.py')
text = checker.read_text(encoding='utf-8')
old = '    version = str(dashboard.get("currentVersion") or dashboard.get("latestRelease", {}).get("version") or "")\n'
new = '    version = str(dashboard.get("latestRelease", {}).get("version") or dashboard.get("currentVersion") or "")\n'
count = text.count(old)
if count != 1:
    raise RuntimeError(f'Expected one Pages version-selection line, found {count}')
checker.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Issue #86 Pages monitor now follows the verified public release version.')
