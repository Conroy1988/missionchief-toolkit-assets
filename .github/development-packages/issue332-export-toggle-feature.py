#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
source_path = root / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
source = source_path.read_text(encoding='utf-8')
start_marker = '    function toggleFeature(feature) {'
end_marker = '    function runAutoNight('
start = source.index(start_marker)
end = source.index(end_marker, start)
out = root / '.github' / 'diagnostics' / 'issue332-toggleFeature.js'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(source[start:end], encoding='utf-8')
for name in [
    'issue332-mission-monitoring-toggles-v42032.py',
    'issue332-mission-monitoring-toggles-v42032-corrected.py',
    'issue332-diagnostic-wrapper.py',
]:
    (Path(__file__).with_name(name)).unlink(missing_ok=True)
print(f'Exported {end - start} characters from toggleFeature for Issue #332 diagnostics')
