#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package = root / '.github/development-packages/issue-181-compact-source.py'
text = package.read_text(encoding='utf-8')
old = """    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker))
    if start < 0 or end < 0 or end <= start:
        raise AssertionError(f'{label}: region markers not found')
"""
new = """    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        fallback = {
            'patient-aware resolver': '    function missionRequirementsOverallState',
            'patient-aware renderer': '    function missionRequirementsScheduleRecord'
        }.get(label)
        if fallback:
            end = text.find(fallback, start + len(start_marker))
    if start < 0 or end < 0 or end <= start:
        raise AssertionError(f'{label}: region markers not found')
"""
if text.count(old) != 1:
    raise AssertionError(f'Expected one compaction boundary block, found {text.count(old)}')
text = text.replace(old, new, 1)
compile(text, str(package), 'exec')
package.write_text(text, encoding='utf-8')
print('Issue 181 compaction boundaries corrected')
