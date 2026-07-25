#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
def section(start,end): a=text.index(start);b=text.index(end,a);return text[a:b]
helper=section('    function runBootIntegration','    function startBootAttemptCoordinator');boot=section('    function boot()','    function scheduleBoot()')
assert 'failed without blocking the Toolkit launcher' in helper;assert "runBootIntegration('custom vehicle badges', installCustomVehicleBadges);" in boot;assert 'installOperationalSuiteShell' not in boot
print('Core menu boot remains fail-open after v7 retirement.')
