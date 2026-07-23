#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
text=(ROOT/'src/MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
def section(start,end):
    left=text.index(start);right=text.index(end,left);return text[left:right]
block=section('// Issue #464 resilient launcher and typed operational settings.','// Issue #464 end resilient launcher and typed operational settings.')
for path in ['requirements.enabled','requirements.calcMaxStaff','requirements.hoverTip','requirements.viewMode','requirements.sort','requirements.sortDir','callWindow.enabled','callWindow.generationDate','callWindow.yellowBorderHours','callWindow.redBorder','callWindow.patientSummary','callWindow.collapsiblePatients','callWindow.collapsiblePatientsMinPatients','callWindow.arrCounter','callWindow.arrCounterAsBadge','callWindow.arrClickHighlight','callWindow.arrClickHighlightColor','callWindow.arrClickHighlightWidth','callWindow.arrCounterResetSelection','callWindow.arrMatchHighlight','callWindow.arrMatchHighlightAllWords','callWindow.arrTime','callWindow.arrSpecs','callWindow.alarmTime','callWindow.stickyHeader','callWindow.loadMoreVehiclesInHeader','callWindow.hideVehicleList','callWindow.centerMap','callWindow.stagingAreaSelectedCounter','callWindow.vehicleTypeInList','callWindow.remainingPatientTime','callWindow.vehicleCounter','callWindow.vehicleCounterColor','callWindow.vehicleListPermanentSearch','callWindow.playerCounter','callWindow.playerCounterColor','callWindow.selectedVehicleCounter','callWindow.selectedVehicleCounterVehicleTypes','callWindow.arrSearch','callWindow.arrSearchDissolveCategories','callWindow.arrSearchCompactResults','callWindow.arrSearchSelectOnEnter','callWindow.arrSearchClearOnEnter','callWindow.arrSearchAutoFocus','callWindow.arrSearchDropdown','callWindow.arrSearchCloseDropdownOnSelect','callWindow.moreReleasePatientButtons','missionList.enabled','missionList.remainingPumpingTime','missionList.shareMissionsMinCredits','missionList.shareMissionsButtonColor','missionList.sortMissionsButtonColor','transport.enabled','transport.autoOpenTransportRequest','transport.autoClickSuccessButtons']:
    assert f"p:'{path}'" in block,path
for hidden in ['requirements.overlay','requirements.minified','requirements.pushRight','requirements.drag','missionList.starredMissions','missionList.collapsedMissions']:
    assert f"p:'{hidden}'" not in block,hidden
for editor in ['callWindow.tailoredTabs','callWindow.missionKeywords','callWindow.alarmIcons','callWindow.arrCategoryColors']:
    assert editor in block
assert 'data-operational-type="json"' not in block and 'mcms-operational-json-row' not in block
assert 'operationalArrMatchesText' in block and 'operationalMissionShareEligible' in block and 'operationalMissionAgeRefreshPlan' in block
control=section('    function createControl(','    function createPanel(')
assert 'const host = toolkitControlHost(mapEl, document);' in control and "existing.classList.toggle('mcms-control-fallback', !mapEl);" in control and 'return control;' in control
ensure=section('    function ensureUi()','    function mutationBelongsToToolkit')
assert ensure.index('const control = createControl(mapEl);')<ensure.index('if (mapEl) {')
assert 'return Boolean(control || document.getElementById(SCRIPT.controlId));' in ensure
boot=section('    function boot()','    function scheduleBoot()')
assert boot.index('const removesToolkitUi = mutationRemovesToolkitUi(mutation);')<boot.index('mutationBelongsToToolkit(mutation)')
maintenance=section('    function registerBootMaintenanceTasks()','    function boot()')
assert "runtimeRegisterTask('ui-integrity'" in maintenance
call=section('    function operationalCallWindowApply(','    function operationalMissionListRoot(')
for token in ['yellowBorderHours','arrCounterAsBadge','arrClickHighlightWidth','arrSearchDropdown','arrSearchCloseDropdownOnSelect','tailoredTabs','missionKeywords','alarmIcons','arrCategoryColors','moreReleasePatientButtons']:
    assert token in call,token
mission_list=section('    function operationalMissionListApply(','    function operationalTransportChooseAction(')
for token in ['operationalMissionShareEligible','remainingPumpingTime','currentPatientsInTooltips','fixedEventInfo','sortMissionsButtonColor']:
    assert token in mission_list,token
assert 'shareMissionsMinCredits' in block
age=section('    function updateMissionAgeLabels()','    function scheduleMissionAgeRefresh(')
assert 'scanInlineMissionMarkerData(true)' in age and 'operationalMissionAgeRefreshPlan' in age and 'captureMissionMarkerData(marker)' in age
assert re.search(r'function\s+scanInlineMissionMarkerData\s*\(\s*force\s*=\s*false\s*\)', text)
assert 'inlineMissionDataScanned=captured>0' in text
assert 'if(settings.arrSearchAutoFocus)queueMicrotask(()=>select.focus());' in call
assert 'if(settings.arrSearchAutoFocus)queueMicrotask(()=>input.focus());' in call
assert not re.search(r'arrSearchAutoFocus\s*\)\s*runtimeSetTimeout', call)
assert "runtimeSetTimeout(()=>{if(state.missionAge)scheduleMissionAgeRefresh(0);},250)" in text
assert "runtimeSetTimeout(()=>{if(state.missionAge)scheduleMissionAgeRefresh(0);},1000)" in text
runtime_timeout_sites = len(re.findall(r'runtimeSetTimeout\s*\(', text)) - len(re.findall(r'function\s+runtimeSetTimeout\s*\(', text))
assert runtime_timeout_sites <= 99
visibility=section('    function applyMapVisibilityToggleEffects(','    function toggleFeature(')
assert "feature==='missionAge'" in visibility and 'scheduleMissionAgeRefresh(0)' in visibility and 'clearMissionAgeLabels()' in visibility
feature_block=section('    // Issue #378 complete operational feature suite.','    // Issue #378 end complete operational feature suite.')
assert '.addEventListener(' not in feature_block and 'new MutationObserver(' not in feature_block and 'setInterval(' not in feature_block
meta=re.search(r'^//\s*@version\s+([^\s]+)',text,re.M).group(1);runtime=re.search(r"version:\s*'([^']+)'",text).group(1)
assert meta==runtime=='5.0.6'
assert len(text.splitlines())<=32000
print('Issue #464 complete launcher, settings, runtime and Mission Age contract passed.')
