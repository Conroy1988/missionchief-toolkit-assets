from pathlib import Path
import re

path=Path('/tmp/v6-phase1.user.js')
s=path.read_text()


def replace_once(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    s=s.replace(old,new,1)


def remove_function(name):
    global s
    m=re.search(rf'(?m)^    function {re.escape(name)}\s*\(',s)
    if not m:
        raise SystemExit(f'function not found: {name}')
    start=m.start()
    brace=s.find('{',m.end())
    if brace<0: raise SystemExit(f'opening brace missing: {name}')
    depth=0; quote=None; escape=False; template_depth=0; i=brace
    # JS-aware enough for normal function declarations; handle strings/templates/comments.
    state='code'
    while i<len(s):
        c=s[i]; n=s[i+1] if i+1<len(s) else ''
        if state=='line':
            if c=='\n': state='code'
        elif state=='block':
            if c=='*' and n=='/': state='code'; i+=1
        elif state in ('single','double'):
            q="'" if state=='single' else '"'
            if escape: escape=False
            elif c=='\\': escape=True
            elif c==q: state='code'
        elif state=='template':
            if escape: escape=False
            elif c=='\\': escape=True
            elif c=='`' and template_depth==0: state='code'
            elif c=='$' and n=='{': template_depth+=1; i+=1
            elif c=='}' and template_depth: template_depth-=1
        else:
            if c=='/' and n=='/': state='line'; i+=1
            elif c=='/' and n=='*': state='block'; i+=1
            elif c=="'": state='single'
            elif c=='"': state='double'
            elif c=='`': state='template'; template_depth=0
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    end=i+1
                    if end<len(s) and s[end]=='\n': end+=1
                    s=s[:start]+s[end:]
                    return
        i+=1
    raise SystemExit(f'closing brace missing: {name}')


# Version and obsolete high-overhead defaults/settings.
replace_once("        autoNight: { enabled: false, nightStart: '20:00', dayStart: '06:00', nightTheme: 'nightshift', dayTheme: 'default' },\n",'', 'autoNight default')
replace_once("        heatmap: { enabled: false, radiusMi: 25, opacity: 0.34, service: 'all', source: 'all' },\n",'', 'heatmap default')
replace_once("        missionInspector: false,\n",'', 'missionInspector default')
replace_once("        criticalView: false,\n",'', 'criticalView default')

# Remove retired UI controls/settings/routes.
for fragment,label in [
("${makeToggleButton('autoNight','Automatic day / night', state.autoNight.enabled)}",'autoNight toggle'),
("${makeToggleButton('heatmap','Coverage Heat Map', state.heatmap.enabled)}",'heatmap toggle'),
("${makeToggleButton('criticalView','Critical View', state.criticalView)}",'critical view toggle'),
("${makeToggleButton('missionInspector','Mission Inspector', state.missionInspector)}",'inspector toggle'),
("<button type=\"button\" class=\"mcms-btn\" data-action=\"open-critical-drawer\">Open Critical View</button>",'critical drawer action'),
]:
    if fragment in s: s=s.replace(fragment,'',1)

# Settings rows and setting families.
for setting in ['auto-day-start','auto-day-theme','auto-night-start','auto-night-theme','heatmap-opacity','heatmap-radius','heatmap-service','heatmap-source']:
    s=re.sub(rf'(?s)\s*<label[^>]*>.*?data-setting="{re.escape(setting)}".*?</label>','',s,count=1)

# Remove settings family handling blocks.
s=re.sub(r"(?ms)^        if \(setting\.startsWith\('auto-'\)\) \{.*?^        \}\n",'',s,count=1)
s=re.sub(r"(?ms)^        if \(setting\.startsWith\('heatmap-'\)\) \{.*?^        \}\n",'',s,count=1)

# Remove direct toggle state/effects.
for old in [
"        else if (feature === 'autoNight') state.autoNight.enabled = !state.autoNight.enabled;\n",
"        else if (feature === 'heatmap') state.heatmap.enabled = !state.heatmap.enabled;\n",
"        else if (feature === 'criticalView') state.criticalView = !state.criticalView;\n",
"        else if (feature === 'missionInspector') state.missionInspector = !state.missionInspector;\n",
"        else if (feature === 'autoNight') applyAutomaticTheme();\n",
"        else if (feature === 'heatmap') scheduleHeatmapRefresh(0);\n",
"        else if (feature === 'criticalView') toggleCriticalView();\n",
"        else if (feature === 'missionInspector') refreshVisibleMissionInspector();\n",
]:
    if old in s: s=s.replace(old,'',1)

# Remove recurring task registrations.
s=re.sub(r"(?ms)^        runtimeRegisterTask\('auto-night'.*?^        \}\);\n",'',s,count=1)
s=re.sub(r"(?ms)^        runtimeRegisterTask\('critical-countdowns'.*?^        \}\);\n",'',s,count=1)

# Remove obsolete lifecycle functions.
for name in [
'applyAutomaticTheme','scheduleHeatmapRefresh','clearCoverageHeatmap','renderCoverageHeatmap',
'coverageHeatMapColor','coverageHeatMapPoints','coverageHeatMapOpacity','coverageHeatMapRadius',
'openMissionInspector','closeMissionInspector','renderMissionInspector','refreshVisibleMissionInspector',
'scheduleMissionInspectorRefresh','installMissionInspectorPointerListeners',
'openCriticalView','closeCriticalView','toggleCriticalView','renderCriticalView','refreshCriticalView',
'scheduleCriticalDrawerDock','positionCriticalDrawer','closeCriticalViewControls',
'criticalMissionData','criticalMissionRows','criticalMissionMatches','criticalMissionSort',
'criticalMissionAgeBucket','criticalMissionStatus','criticalMissionCategory','criticalMissionOwnership',
'criticalMissionValue','criticalMissionDistance','criticalMissionActions','criticalMissionTitle',
'criticalMissionUnits','criticalMissionPatients','criticalMissionRequirementSummary',
'criticalMissionCard','criticalMissionDrawerMarkup','criticalMissionFiltersMarkup',
'criticalMissionFilterOptions','criticalMissionFilterLabel','criticalMissionStableRecord',
'criticalMissionApiRecord','criticalMissionSnapshotRecord','criticalMissionMergedRecord',
'criticalMissionPageRecord','criticalMissionRefreshData','criticalMissionEnsureData',
'criticalMissionLoadPage','criticalMissionPageUrl','criticalMissionNormalizeHtml',
'criticalMissionExtractPageData','criticalMissionNextPageLink','criticalMissionListRoot',
'criticalMissionListRows','criticalMissionFindRow','criticalMissionRowMissionId',
'criticalMissionMissionLink','criticalMissionClearState','criticalMissionFocus',
'criticalMissionRemoveFocus','criticalMissionSetMapFocus','criticalMissionNavigationTarget',
'criticalMissionCurrentFilter','criticalMissionSaveFilters','criticalMissionRestoreFilters',
'criticalMissionUpdateCounts','criticalMissionRenderEmpty','criticalMissionRenderLoading',
'criticalMissionRenderError','criticalMissionApplyFilters','criticalMissionDrawerElement',
'criticalMissionDrawerOpen','criticalMissionDrawerClose','criticalMissionDrawerToggle',
'criticalMissionDrawerKeydown','criticalMissionDrawerClick','criticalMissionDrawerChange',
'criticalMissionDrawerInput','criticalMissionDrawerScroll','criticalMissionDrawerResize',
'criticalMissionDrawerTeardown','criticalMissionDrawerSetup','criticalMissionScheduleRender',
'criticalMissionRender','criticalMissionRefresh','criticalMissionRefreshVisible',
]:
    if re.search(rf'(?m)^    function {re.escape(name)}\s*\(',s): remove_function(name)

# Remove common retired global declarations.
s=re.sub(r"(?m)^    let (?:heatmap|coverageHeatmap|missionInspector|criticalDrawer|criticalMission)[A-Za-z0-9_]*.*?;\n",'',s)
s=re.sub(r"(?m)^    const (?:HEATMAP|MISSION_INSPECTOR|CRITICAL_)[A-Z0-9_]*.*?;\n",'',s)

# Safe legacy-state migration: stale keys are dropped rather than executed.
needle="        const merged = deepMerge(defaultState(), raw || {});\n"
if needle in s and "delete merged.autoNight" not in s:
    s=s.replace(needle, needle+"        delete merged.autoNight;\n        delete merged.heatmap;\n",1)

path.write_text(s)
print('patched',len(s),s.count('\n')+1)
