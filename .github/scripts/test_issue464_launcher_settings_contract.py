#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
def section(start,end): a=text.index(start);b=text.index(end,a);return text[a:b]
control=section('    function createControl(','    function createPanel(');assert 'const primaryMap = toolkitPrimaryMapElement(mapEl, document);' in control
ensure=section('    function ensureUi()','    function mutationBelongsToToolkit');assert 'return Boolean(control || document.getElementById(SCRIPT.controlId));' in ensure
boot=section('    function boot()','    function scheduleBoot()');assert 'installMissionMarkerAddHook' in boot and 'installCustomVehicleBadges' in boot and 'installOperationalSuiteShell' not in boot
age=section('    function updateMissionAgeLabels()','    function scheduleMissionAgeRefresh(');assert 'missionAgeRefreshPlan' in age
meta=re.search(r'^//\s*@version\s+([^\s]+)',text,re.M).group(1);runtime=re.search(r"version:\s*'([^']+)'",text).group(1);assert meta==runtime;assert tuple(int(part) for part in meta.split('.')[:3]) >= (7,0,0);assert len(text.splitlines())<=24000
print('v7 launcher, boot and Mission Age contract passed.')
