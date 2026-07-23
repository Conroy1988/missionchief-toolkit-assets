#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
SOURCE = ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js'
CHANGELOG = ROOT / 'CHANGELOG.md'
FIXTURE = ROOT / '.github/fixtures/main-style-source-headroom.json'
VALIDATOR = ROOT / '.github/scripts/validate_userscript.py'
TEST = ROOT / '.github/scripts/test_issue464_launcher_settings_contract.py'
text = SOURCE.read_text(encoding='utf-8')


def function_span(source: str, name: str) -> tuple[int, int]:
    match = re.search(rf'(?m)^\s*function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{', source)
    if not match:
        raise SystemExit(f'Missing function: {name}')
    open_pos = source.find('{', match.start(), match.end())
    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = open_pos
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ''
        if line_comment:
            if ch == '\n': line_comment = False
            i += 1; continue
        if block_comment:
            if ch == '*' and nxt == '/': block_comment = False; i += 2
            else: i += 1
            continue
        if quote:
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == quote: quote = None
            i += 1; continue
        if ch == '/' and nxt == '/': line_comment = True; i += 2; continue
        if ch == '/' and nxt == '*': block_comment = True; i += 2; continue
        if ch in "'\"`": quote = ch; i += 1; continue
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: return match.start(), i + 1
        i += 1
    raise SystemExit(f'Unclosed function: {name}')


def replace_function(source: str, name: str, replacement: str) -> str:
    start, end = function_span(source, name)
    return source[:start] + replacement.rstrip() + source[end:]


if '// @version      5.0.5' not in text or "version: '5.0.5'" not in text:
    raise SystemExit('Issue #464 package requires Toolkit v5.0.5')
text = text.replace('// @version      5.0.5', '// @version      5.0.6', 1)
text = text.replace("version: '5.0.5'", "version: '5.0.6'", 1)

marker = '    // Issue #464 resilient launcher and typed operational settings.'
anchor = '    function operationalWindowSettingsMarkup() {'
if marker in text:
    raise SystemExit('Issue #464 implementation already present')
if anchor not in text:
    raise SystemExit('Operational settings markup anchor is missing')

block = r'''    // Issue #464 resilient launcher and typed operational settings.
    const OP_SETTING_COLOURS = [['success','Green'],['warning','Orange'],['danger','Red'],['primary','Dark blue'],['info','Light blue'],['default','Grey']];
    const OPERATIONAL_SETTINGS_SCHEMA = Object.freeze([
        { id:'requirements', title:'Enhanced Requirements', description:'Live selected, en-route, on-scene and still-needed operational requirements.', settings:[
            {p:'requirements.enabled',t:'boolean',l:'Enabled',d:'Show the Toolkit operational requirements panel.'},{p:'requirements.calcMaxStaff',t:'boolean',l:'Calculate maximum staff',d:'Assume vehicles carry their maximum staff for personnel calculations.',r:'requirements.enabled'},{p:'requirements.hoverTip',t:'boolean',l:'Tooltips',d:'Show explanatory tooltips on Enhanced Requirements controls.',r:'requirements.enabled'},{p:'requirements.viewMode',t:'select',l:'Display mode',d:'Choose the table or compact text presentation.',r:'requirements.enabled',o:[['table','Table'],['text','Text']]},{p:'requirements.sort',t:'select',l:'Sort by',d:'Choose the requirement column used for ordering.',r:'requirements.enabled',o:[['requirement','Requirement'],['missing','Still needed'],['driving','En-route'],['selected','Selected'],['total','Total']]},{p:'requirements.sortDir',t:'select',l:'Direction',d:'Choose ascending or descending requirement order.',r:'requirements.enabled',o:[['asc','Ascending'],['desc','Descending']]}
        ]},
        { id:'callWindow', title:'Extended Call Window', description:'Mission-window information, patients, vehicle list, ARR controls and search.', settings:[
            {p:'callWindow.enabled',t:'boolean',l:'Enabled',d:'Enable Toolkit Extended Call Window features.'},{p:'callWindow.generationDate',t:'boolean',l:'Generation time',d:'Show when the mission was generated.',r:'callWindow.enabled'},{p:'callWindow.yellowBorderHours',t:'number',l:'Yellow border age',d:'Outline generation time after this many hours; 0 disables it.',r:'callWindow.enabled,callWindow.generationDate',min:0,max:48,step:1},{p:'callWindow.redBorder',t:'boolean',l:'Red expiry border',d:'Outline generation time in red when the mission is due to expire.',r:'callWindow.enabled,callWindow.generationDate'},{p:'callWindow.patientSummary',t:'boolean',l:'Patient summary',d:'Show patient count and required rescue-equipment combinations.',r:'callWindow.enabled'},{p:'callWindow.collapsiblePatients',t:'boolean',l:'Minimise patients',d:'Collapse large patient lists into a compact summary.',r:'callWindow.enabled'},{p:'callWindow.collapsiblePatientsMinPatients',t:'number',l:'Minimum patient count',d:'Number of patients required before minimising is activated.',r:'callWindow.enabled,callWindow.collapsiblePatients',min:1,max:250,step:1},{p:'callWindow.arrCounter',t:'boolean',l:'ARR counter',d:'Count how often an ARR or move is selected.',r:'callWindow.enabled'},{p:'callWindow.arrCounterAsBadge',t:'boolean',l:'ARR counter as badge',d:'Display the ARR counter as a badge on each ARR.',r:'callWindow.enabled,callWindow.arrCounter'},{p:'callWindow.arrClickHighlight',t:'boolean',l:'Highlight clicked ARRs',d:'Draw a border around ARRs that have already been clicked.',r:'callWindow.enabled'},{p:'callWindow.arrClickHighlightColor',t:'color',l:'Highlight colour',d:'Choose the border colour used for clicked ARRs.',r:'callWindow.enabled,callWindow.arrClickHighlight'},{p:'callWindow.arrClickHighlightWidth',t:'number',l:'Highlight width',d:'Set the ARR border width in pixels.',r:'callWindow.enabled,callWindow.arrClickHighlight',min:1,max:12,step:1},{p:'callWindow.arrCounterResetSelection',t:'boolean',l:'Reset vehicle selection',d:'Add a reset control for ARR counters, borders and selected vehicles.',r:'callWindow.enabled'},{p:'callWindow.arrMatchHighlight',t:'boolean',l:'Grey out unsuitable ARRs',d:'De-emphasise ARRs that do not match the mission name.',r:'callWindow.enabled'},{p:'callWindow.arrMatchHighlightAllWords',t:'boolean',l:'Use all mission-name words',d:'Require every relevant mission-name word when matching ARRs.',r:'callWindow.enabled,callWindow.arrMatchHighlight'},{p:'callWindow.arrTime',t:'boolean',l:'ARR projected journey time',d:'Show the longest journey time that selecting an ARR would create.',r:'callWindow.enabled'},{p:'callWindow.arrSpecs',t:'boolean',l:'ARR stored request details',d:'Show the vehicle requests stored in an ARR on hover.',r:'callWindow.enabled'},{p:'callWindow.alarmTime',t:'boolean',l:'Alarm-button journey time',d:'Show the longest selected-vehicle journey time beside Alarm.',r:'callWindow.enabled'},{p:'callWindow.stickyHeader',t:'boolean',l:'Sticky header',d:'Keep the mission-window header visible while scrolling.',r:'callWindow.enabled'},{p:'callWindow.loadMoreVehiclesInHeader',t:'boolean',l:'Reload vehicles in header',d:'Move the native Reload vehicles control into the header when available.',r:'callWindow.enabled'},{p:'callWindow.hideVehicleList',t:'boolean',l:'Hide vehicle list',d:'Start with the available-unit list hidden and expose a show button.',r:'callWindow.enabled'},{p:'callWindow.centerMap',t:'boolean',l:'Centre map',d:'Add a control that centres the main map on the mission.',r:'callWindow.enabled'},{p:'callWindow.stagingAreaSelectedCounter',t:'boolean',l:'Staging-area selected counter',d:'Show selected-unit totals beside staging-area alarm controls.',r:'callWindow.enabled'},{p:'callWindow.vehicleTypeInList',t:'boolean',l:'Show vehicle type',d:'Display each vehicle type in the Available Units list.',r:'callWindow.enabled'},{p:'callWindow.remainingPatientTime',t:'boolean',l:'Remaining patient treatment time',d:'Show how long remains until each patient is fully treated.',r:'callWindow.enabled'},{p:'callWindow.vehicleCounter',t:'boolean',l:'Vehicle counter',d:'Show how many vehicles are committed to the mission.',r:'callWindow.enabled'},{p:'callWindow.vehicleCounterColor',t:'select',l:'Vehicle counter colour',d:'Choose the vehicle-counter badge colour.',r:'callWindow.enabled,callWindow.vehicleCounter',o:OP_SETTING_COLOURS},{p:'callWindow.vehicleListPermanentSearch',t:'boolean',l:'Permanent vehicle search',d:'Keep the available-vehicle search field visible.',r:'callWindow.enabled'},{p:'callWindow.playerCounter',t:'boolean',l:'Player counter',d:'Show how many players have dispatched vehicles.',r:'callWindow.enabled'},{p:'callWindow.playerCounterColor',t:'select',l:'Player counter colour',d:'Choose the player-counter badge colour.',r:'callWindow.enabled,callWindow.playerCounter',o:OP_SETTING_COLOURS},{p:'callWindow.selectedVehicleCounter',t:'boolean',l:'Selected vehicle counter',d:'Show an expandable count of selected vehicles by type.',r:'callWindow.enabled'},{p:'callWindow.selectedVehicleCounterVehicleTypes',t:'csv',l:'Quick-counter vehicle types',d:'Comma-separated vehicle type IDs shown directly on the counter button.',r:'callWindow.enabled,callWindow.selectedVehicleCounter',ph:'0, 1, 16'},{p:'callWindow.arrSearch',t:'boolean',l:'ARR search',d:'Add a search field above the ARR list.',r:'callWindow.enabled'},{p:'callWindow.arrSearchDissolveCategories',t:'boolean',l:'Show all ARR categories',d:'Display all ARR categories while searching.',r:'callWindow.enabled,callWindow.arrSearch',f:'callWindow.arrSearchDropdown'},{p:'callWindow.arrSearchCompactResults',t:'boolean',l:'Compact ARR results',d:'Show all matching ARRs in a compact single-row result.',r:'callWindow.enabled,callWindow.arrSearch',f:'callWindow.arrSearchDropdown'},{p:'callWindow.arrSearchSelectOnEnter',t:'boolean',l:'Select first ARR on Enter',d:'Click the first matching ARR when Enter is pressed.',r:'callWindow.enabled,callWindow.arrSearch',f:'callWindow.arrSearchDropdown'},{p:'callWindow.arrSearchClearOnEnter',t:'boolean',l:'Clear search on Enter',d:'Clear the ARR search after Enter is pressed.',r:'callWindow.enabled,callWindow.arrSearch',f:'callWindow.arrSearchDropdown'},{p:'callWindow.arrSearchAutoFocus',t:'boolean',l:'ARR search autofocus',d:'Focus ARR search automatically when the mission opens.',r:'callWindow.enabled,callWindow.arrSearch'},{p:'callWindow.arrSearchDropdown',t:'boolean',l:'ARR search as dropdown',d:'Replace the full ARR grid with a searchable compact dropdown.',r:'callWindow.enabled,callWindow.arrSearch'},{p:'callWindow.arrSearchCloseDropdownOnSelect',t:'boolean',l:'Close dropdown after selection',d:'Close the compact ARR dropdown after choosing an ARR.',r:'callWindow.enabled,callWindow.arrSearchDropdown'},{p:'callWindow.moreReleasePatientButtons',t:'boolean',l:'More patient-release buttons',d:'Add patient-release controls beside transport actions and vehicle headers.',r:'callWindow.enabled'}
        ]},
        { id:'missionList', title:'Extended Mission List', description:'Mission sorting, starring, collapsing, sharing, patient and prisoner indicators.', settings:[
            {p:'missionList.enabled',t:'boolean',l:'Enabled',d:'Enable Toolkit Extended Mission List features.'},{p:'missionList.remainingTime',t:'boolean',l:'Remaining mission time',d:'Show mission countdown information.',r:'missionList.enabled'},{p:'missionList.remainingTimeGreenOnly',t:'boolean',l:'Green countdowns only',d:'Only show countdowns while they remain in the green state.',r:'missionList.enabled,missionList.remainingTime'},{p:'missionList.remainingPatientTime',t:'boolean',l:'Patient treatment time',d:'Show remaining patient treatment time in the mission list.',r:'missionList.enabled'},{p:'missionList.remainingPumpingTime',t:'boolean',l:'Water and foam time',d:'Show remaining pumping or filling time.',r:'missionList.enabled'},{p:'missionList.starrableMissions',t:'boolean',l:'Mission starring',d:'Allow missions to be starred and kept at the top.',r:'missionList.enabled'},{p:'missionList.averageCredits',t:'boolean',l:'Average credits',d:'Show estimated mission credits.',r:'missionList.enabled'},{p:'missionList.collapsibleMissions',t:'boolean',l:'Collapsible missions',d:'Allow mission rows to be collapsed.',r:'missionList.enabled'},{p:'missionList.collapsibleMissionsAllButton',t:'boolean',l:'Collapse-all button',d:'Show a control to collapse or expand all missions.',r:'missionList.enabled,missionList.collapsibleMissions'},{p:'missionList.shareMissions',t:'boolean',l:'Mission sharing controls',d:'Add native alliance-sharing controls to eligible missions.',r:'missionList.enabled'},{p:'missionList.shareMissionTypes',t:'csv',l:'Share mission types',d:'Comma-separated MissionChief mission type identifiers eligible for sharing.',r:'missionList.enabled,missionList.shareMissions'},{p:'missionList.shareMissionsMinCredits',t:'number',l:'Minimum share credits',d:'Only offer sharing at or above this estimated credit value.',r:'missionList.enabled,missionList.shareMissions',min:0,max:10000000,step:1000},{p:'missionList.shareMissionsButtonColor',t:'select',l:'Share button colour',d:'Choose the mission-sharing button colour.',r:'missionList.enabled,missionList.shareMissions',o:OP_SETTING_COLOURS},{p:'missionList.sortMissions',t:'boolean',l:'Mission sorting',d:'Enable persisted mission-list sorting.',r:'missionList.enabled'},{p:'missionList.sortMissionsType',t:'select',l:'Sort by',d:'Choose the mission attribute used for sorting.',r:'missionList.enabled,missionList.sortMissions',o:[['','Default'],['name','Name'],['credits','Credits'],['patients','Patients'],['prisoners','Prisoners'],['time','Time']]},{p:'missionList.sortMissionsDirection',t:'select',l:'Sort direction',d:'Choose ascending or descending mission order.',r:'missionList.enabled,missionList.sortMissions',o:[['','Default'],['asc','Ascending'],['desc','Descending']]},{p:'missionList.sortMissionsButtonColor',t:'select',l:'Sort button colour',d:'Choose the sorting-control colour.',r:'missionList.enabled,missionList.sortMissions',o:OP_SETTING_COLOURS},{p:'missionList.sortMissionsInMissionWindow',t:'boolean',l:'Sort opened mission list',d:'Apply ordering inside opened mission windows.',r:'missionList.enabled,missionList.sortMissions'},{p:'missionList.currentPatients',t:'boolean',l:'Current patients',d:'Show current patient counts.',r:'missionList.enabled'},{p:'missionList.hideZeroCurrentPatients',t:'boolean',l:'Hide zero patients',d:'Hide patient badges when the count is zero.',r:'missionList.enabled,missionList.currentPatients'},{p:'missionList.currentPatientsInTooltips',t:'boolean',l:'Patients in tooltips',d:'Include patient counts in mission tooltips.',r:'missionList.enabled,missionList.currentPatients'},{p:'missionList.currentPrisoners',t:'boolean',l:'Current prisoners',d:'Show current prisoner counts.',r:'missionList.enabled'},{p:'missionList.hideZeroCurrentPrisoners',t:'boolean',l:'Hide zero prisoners',d:'Hide prisoner badges when the count is zero.',r:'missionList.enabled,missionList.currentPrisoners'},{p:'missionList.currentPrisonersInTooltips',t:'boolean',l:'Prisoners in tooltips',d:'Include prisoner counts in mission tooltips.',r:'missionList.enabled,missionList.currentPrisoners'},{p:'missionList.fixedEventInfo',t:'boolean',l:'Fixed event information',d:'Keep event information visible for configured missions.',r:'missionList.enabled'},{p:'missionList.eventMissions',t:'csv',l:'Event mission IDs',d:'Comma-separated mission IDs used by fixed event information.',r:'missionList.enabled,missionList.fixedEventInfo'}
        ]},
        { id:'transport', title:'Enhanced Transport Requests', description:'Safety-checked patient, prisoner and vehicle transport automation. Automation remains opt-in.', settings:[
            {p:'transport.enabled',t:'boolean',l:'Enabled',d:'Enable Toolkit transport-request enhancements.'},{p:'transport.autoOpenTransportRequest',t:'boolean',l:'Open transport requests automatically',d:'Open a transport request only when exactly one safe candidate exists.',r:'transport.enabled'},{p:'transport.autoClickSuccessButtons',t:'boolean',l:'Confirm successful transport actions',d:'Allow validated success controls to be activated after an opted-in transport action.',r:'transport.enabled'}
        ]}
    ]);
    const OP_OPERATIONAL_EDITORS = Object.freeze([
        {p:'callWindow.tailoredTabs',l:'Vehicle categories',d:'Create custom vehicle tabs for the mission insert window.',r:'enabled,callWindow.enabled',v:{name:'',color:'#505050',vehicleTypes:[]},f:[{k:'name',l:'Name',t:'string'},{k:'color',l:'Colour',t:'color'},{k:'vehicleTypes',l:'Vehicle type IDs',t:'csv'}]},
        {p:'callWindow.missionKeywords',l:'Mission keywords',d:'Display configured keywords beside matching mission names.',r:'enabled,callWindow.enabled',v:{keyword:'',color:'#777777',autotextcolor:true,textcolor:'#ffffff',prefix:false,missions:[]},f:[{k:'keyword',l:'Keyword',t:'string'},{k:'color',l:'Background',t:'color'},{k:'autotextcolor',l:'Automatic text colour',t:'boolean'},{k:'textcolor',l:'Text colour',t:'color'},{k:'prefix',l:'Show before mission name',t:'boolean'},{k:'missions',l:'Mission IDs',t:'csv'}]},
        {p:'callWindow.alarmIcons',l:'Alarm icons',d:'Show Font Awesome icon names on Alarm controls for selected vehicle types.',r:'enabled,callWindow.enabled',v:{icon:'',type:'fas',vehicleTypes:[]},f:[{k:'icon',l:'Icon name',t:'string'},{k:'type',l:'Icon type',t:'select',o:[['fas','Solid'],['far','Regular'],['fab','Brand']]},{k:'vehicleTypes',l:'Vehicle type IDs',t:'csv'}]},
        {p:'callWindow.arrCategoryColors',l:'ARR category colours',d:'Assign background and text colours to named ARR categories.',r:'enabled,callWindow.enabled',v:{categoryName:'',bgColor:'#505050',color:'#ffffff'},f:[{k:'categoryName',l:'Category name',t:'string'},{k:'bgColor',l:'Background',t:'color'},{k:'color',l:'Text',t:'color'}]}
    ]);
    function toolkitControlHost(mapEl, doc = document) { return mapEl || doc?.body || doc?.documentElement || null; }
    function operationalWindowDependenciesMet(requires, forbids, getter = operationalFeatureValue, suiteEnabled = state.operationalWindow?.enabled !== false) { if (!suiteEnabled) return false; const required = String(requires || '').split(',').filter(Boolean); const blocked = String(forbids || '').split(',').filter(Boolean); return required.every(path => getter(path) === true) && !blocked.some(path => getter(path) === true); }
    function operationalWindowSettingId(path, suffix = '') { return `mcms-op-${String(path).replace(/[^a-z0-9]+/giu, '-')}${suffix}`; }
    function operationalWindowSettingAttrs(def) { const req = def.r ? ` data-operational-requires="${operationalEscape(def.r)}"` : ''; const forbid = def.f ? ` data-operational-forbids="${operationalEscape(def.f)}"` : ''; return `${req}${forbid}`; }
    function operationalWindowControlMarkup(def) { const id = operationalWindowSettingId(def.p); const type = def.t === 'boolean' ? 'boolean' : def.t; const attrs = `id="${id}" data-operational-setting="${operationalEscape(def.p)}" data-operational-type="${type}"`; let control = ''; if (def.t === 'boolean') control = `<span class="mcms-op-switch"><input type="checkbox" ${attrs}><span aria-hidden="true"></span></span>`; else if (def.t === 'select') control = `<select class="mcms-select mcms-op-control" ${attrs}>${def.o.map(([value,label]) => `<option value="${operationalEscape(value)}">${operationalEscape(label)}</option>`).join('')}</select>`; else if (def.t === 'number') control = `<input class="mcms-input mcms-op-control" type="number" ${attrs} min="${def.min}" max="${def.max}" step="${def.step}">`; else if (def.t === 'color') control = `<input class="mcms-op-colour" type="color" ${attrs}>`; else control = `<input class="mcms-input mcms-op-control" type="text" ${attrs}${def.ph ? ` placeholder="${operationalEscape(def.ph)}"` : ''}>`; return `<label class="mcms-op-card" data-operational-row${operationalWindowSettingAttrs(def)} for="${id}"><span class="mcms-op-copy"><strong>${operationalEscape(def.l)}</strong><small>${operationalEscape(def.d)}</small></span>${control}</label>`; }
    function operationalWindowSectionMarkup(section) { return `<details class="mcms-op-section" open><summary><span>${operationalEscape(section.title)}</span><small>${operationalEscape(section.description)}</small></summary><div class="mcms-op-grid">${section.settings.map(operationalWindowControlMarkup).join('')}</div></details>`; }
    function operationalWindowEditorField(editor, index, field, value) { const id = operationalWindowSettingId(editor.p, `-${index}-${field.k}`); const attrs = `id="${id}" data-operational-array-path="${operationalEscape(editor.p)}" data-operational-array-index="${index}" data-operational-array-field="${operationalEscape(field.k)}" data-operational-type="${field.t}"`; let control = ''; if (field.t === 'boolean') control = `<span class="mcms-op-switch mcms-op-switch-small"><input type="checkbox" ${attrs}><span aria-hidden="true"></span></span>`; else if (field.t === 'select') control = `<select class="mcms-select" ${attrs}>${field.o.map(([v,l]) => `<option value="${operationalEscape(v)}">${operationalEscape(l)}</option>`).join('')}</select>`; else if (field.t === 'color') control = `<input class="mcms-op-colour" type="color" ${attrs}>`; else control = `<input class="mcms-input" type="text" ${attrs} value="${operationalEscape(field.t === 'csv' && Array.isArray(value) ? value.join(', ') : value ?? '')}">`; return `<label class="mcms-op-editor-field" for="${id}"><span>${operationalEscape(field.l)}</span>${control}</label>`; }
    function operationalWindowEditorMarkup(editor) { const values = operationalFeatureValue(editor.p); const rows = (Array.isArray(values) ? values : []).map((item,index) => `<div class="mcms-op-editor-row"><div class="mcms-op-editor-toolbar"><strong>${operationalEscape(editor.l)} ${index + 1}</strong><span><button type="button" data-operational-action="up" data-operational-path="${editor.p}" data-operational-index="${index}" aria-label="Move up">↑</button><button type="button" data-operational-action="down" data-operational-path="${editor.p}" data-operational-index="${index}" aria-label="Move down">↓</button><button type="button" data-operational-action="remove" data-operational-path="${editor.p}" data-operational-index="${index}" aria-label="Remove">×</button></span></div><div class="mcms-op-editor-grid">${editor.f.map(field => operationalWindowEditorField(editor,index,field,item?.[field.k])).join('')}</div></div>`).join(''); return `<section class="mcms-op-editor" data-operational-editor="${editor.p}" data-operational-requires="${editor.r}"><header><span><strong>${operationalEscape(editor.l)}</strong><small>${operationalEscape(editor.d)}</small></span><button type="button" data-operational-action="add" data-operational-path="${editor.p}">Add</button></header>${rows || '<div class="mcms-op-empty">No entries configured.</div>'}</section>`; }
    function operationalWindowSettingsInnerMarkup() { const suite = {p:'enabled',t:'boolean',l:'Operational Window Suite enabled',d:'Master switch for Enhanced Requirements, Extended Call Window, Extended Mission List and Enhanced Transport Requests.'}; return `<div class="mcms-section-label">Operational Window Suite</div><div class="mcms-status">Typed Toolkit-native controls mapped to the authorised feature settings. Transport automation remains opt-in.</div><div class="mcms-op-grid mcms-op-master">${operationalWindowControlMarkup(suite)}</div>${OPERATIONAL_SETTINGS_SCHEMA.map(operationalWindowSectionMarkup).join('')}<details class="mcms-op-section mcms-op-editors"><summary><span>Custom lists and appearance</span><small>Structured editors for vehicle categories, mission keywords, alarm icons and ARR category colours.</small></summary>${OP_OPERATIONAL_EDITORS.map(operationalWindowEditorMarkup).join('')}</details>`; }
    function operationalWindowEnsureSettingsStyle(doc = document) { const id = 'mcms-operational-settings-style'; if (doc.getElementById?.(id)) return; const style = doc.createElement('style'); style.id = id; style.textContent = `#${SCRIPT.panelId} .mcms-op-root{display:grid;gap:10px;min-width:0}#${SCRIPT.panelId} .mcms-op-section{min-width:0;border:1px solid rgba(127,127,127,.35);border-radius:10px;overflow:hidden;background:rgba(255,255,255,.025)}#${SCRIPT.panelId} .mcms-op-section>summary{display:grid;gap:2px;padding:10px 12px;cursor:pointer;list-style:none;background:rgba(255,255,255,.04)}#${SCRIPT.panelId} .mcms-op-section>summary::-webkit-details-marker{display:none}#${SCRIPT.panelId} .mcms-op-section>summary span{font-weight:800}#${SCRIPT.panelId} .mcms-op-section>summary small,#${SCRIPT.panelId} .mcms-op-copy small,#${SCRIPT.panelId} .mcms-op-editor small{display:block;line-height:1.35;opacity:.78;overflow-wrap:anywhere}#${SCRIPT.panelId} .mcms-op-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;padding:9px;min-width:0}#${SCRIPT.panelId} .mcms-op-master{padding:0}#${SCRIPT.panelId} .mcms-op-card{display:grid;grid-template-columns:minmax(0,1fr) minmax(46px,auto);gap:10px;align-items:center;min-width:0;padding:10px;border:1px solid rgba(127,127,127,.22);border-radius:8px;background:rgba(0,0,0,.08);overflow:hidden}#${SCRIPT.panelId} .mcms-op-copy{min-width:0}#${SCRIPT.panelId} .mcms-op-copy strong{display:block;overflow-wrap:anywhere}#${SCRIPT.panelId} .mcms-op-control{width:min(210px,100%)!important;min-width:0!important;justify-self:end}#${SCRIPT.panelId} .mcms-op-colour{width:54px!important;height:34px!important;padding:2px!important;border-radius:7px!important;justify-self:end}#${SCRIPT.panelId} .mcms-op-switch{position:relative;display:inline-flex;width:44px;height:24px;justify-self:end;flex:0 0 auto}#${SCRIPT.panelId} .mcms-op-switch input{position:absolute!important;opacity:0!important;pointer-events:none!important;width:1px!important;height:1px!important}#${SCRIPT.panelId} .mcms-op-switch>span{display:block;width:44px;height:24px;border-radius:999px;background:#68727d;box-shadow:inset 0 0 0 1px rgba(255,255,255,.25);transition:.18s}#${SCRIPT.panelId} .mcms-op-switch>span:after{content:'';display:block;width:18px;height:18px;margin:3px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.45);transition:.18s}#${SCRIPT.panelId} .mcms-op-switch input:checked+span{background:#2fbf71}#${SCRIPT.panelId} .mcms-op-switch input:checked+span:after{transform:translateX(20px)}#${SCRIPT.panelId} .mcms-op-switch input:focus-visible+span{outline:2px solid #59a8ff;outline-offset:2px}#${SCRIPT.panelId} .mcms-op-disabled{opacity:.46}#${SCRIPT.panelId} .mcms-op-disabled .mcms-op-copy small:after{content:' · Enable the parent option first';font-weight:700}#${SCRIPT.panelId} .mcms-op-editor{margin:9px;padding:10px;border:1px solid rgba(127,127,127,.25);border-radius:9px;min-width:0}#${SCRIPT.panelId} .mcms-op-editor>header,#${SCRIPT.panelId} .mcms-op-editor-toolbar{display:flex;align-items:center;justify-content:space-between;gap:8px}#${SCRIPT.panelId} .mcms-op-editor button{min-height:32px;border-radius:7px;border:1px solid rgba(127,127,127,.4);background:rgba(255,255,255,.08);color:inherit;font-weight:700}#${SCRIPT.panelId} .mcms-op-editor-row{margin-top:8px;padding:8px;border:1px solid rgba(127,127,127,.22);border-radius:8px}#${SCRIPT.panelId} .mcms-op-editor-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:7px}#${SCRIPT.panelId} .mcms-op-editor-field{display:grid;gap:4px;min-width:0}#${SCRIPT.panelId} .mcms-op-editor-field input,#${SCRIPT.panelId} .mcms-op-editor-field select{width:100%!important;min-width:0!important}#${SCRIPT.panelId} .mcms-op-empty{padding:9px;margin-top:8px;border:1px dashed rgba(127,127,127,.35);border-radius:8px;opacity:.72}#${SCRIPT.controlId}.mcms-control-fallback{position:fixed!important;top:calc(env(safe-area-inset-top,0px) + 8px)!important;left:calc(env(safe-area-inset-left,0px) + 8px)!important;right:auto!important;bottom:auto!important;transform:none!important;z-index:2147483000!important}@media(max-width:900px){#${SCRIPT.panelId} .mcms-op-grid,#${SCRIPT.panelId} .mcms-op-editor-grid{grid-template-columns:minmax(0,1fr)}}@media(max-width:760px){#${SCRIPT.panelId} .mcms-op-card{grid-template-columns:minmax(0,1fr) auto;padding:9px}#${SCRIPT.panelId} .mcms-op-control,#${SCRIPT.panelId} .mcms-op-editor input,#${SCRIPT.panelId} .mcms-op-editor select{font-size:16px!important}#${SCRIPT.panelId} .mcms-op-editor>header{align-items:flex-start}#${SCRIPT.controlId}.mcms-control-fallback{top:auto!important;bottom:calc(env(safe-area-inset-bottom,0px) + 8px)!important;max-width:calc(100vw - env(safe-area-inset-left,0px) - env(safe-area-inset-right,0px) - 16px)!important}}`; (doc.head || doc.documentElement)?.appendChild(style); }
    function operationalWindowSettingsMarkup() { operationalWindowEnsureSettingsStyle(document); return `<div class="mcms-op-root" data-operational-settings-root>${operationalWindowSettingsInnerMarkup()}</div>`; }
    function operationalWindowApplyDependencies(panel) { const root = operationalQuery(panel, '[data-operational-settings-root]'); if (!root) return; operationalQueryAll(root, '[data-operational-row],[data-operational-editor]').forEach(row => { const path = operationalQuery(row, '[data-operational-setting]')?.dataset?.operationalSetting; const enabled = path === 'enabled' || operationalWindowDependenciesMet(row.dataset.operationalRequires,row.dataset.operationalForbids); row.classList.toggle('mcms-op-disabled',!enabled); row.setAttribute('aria-disabled',String(!enabled)); operationalQueryAll(row,'input,select,textarea,button').forEach(control => { control.disabled = !enabled; }); }); }
    function operationalWindowSyncSettingsUi(panel = operationalQuery(document, `#${SCRIPT.panelId}`)) { operationalWindowEnsureSettingsStyle(document); operationalQueryAll(panel, '[data-operational-setting]').forEach(control => { const value = operationalFeatureValue(control.dataset.operationalSetting); const type = control.dataset.operationalType; if (type === 'boolean') control.checked = value === true; else if (document.activeElement !== control) control.value = type === 'csv' && Array.isArray(value) ? value.join(', ') : value ?? ''; }); operationalQueryAll(panel,'[data-operational-array-path]').forEach(control => { const item = operationalFeatureValue(control.dataset.operationalArrayPath)?.[Number(control.dataset.operationalArrayIndex)] || {}; const value = item[control.dataset.operationalArrayField]; const type = control.dataset.operationalType; if (type === 'boolean') control.checked = value === true; else if (document.activeElement !== control) control.value = type === 'csv' && Array.isArray(value) ? value.join(', ') : value ?? ''; }); operationalWindowApplyDependencies(panel); }
    function operationalWindowParseValue(type, value, checked = false) { if (type === 'boolean') return checked === true; if (type === 'number') return Number(value); if (type === 'csv') return String(value || '').split(',').map(item => item.trim()).filter(Boolean); return String(value ?? ''); }
    function operationalWindowCommit(message = 'Operational Window setting saved') { state.operationalWindow = normaliseOperationalWindowState(state.operationalWindow,state.operationalWindow?.requirements?.enabled !== false); saveState(); scheduleOperationalSuiteScan(0); updateUI(); showToast(message); }
    function operationalWindowRefreshSettingsPanel(panel = operationalQuery(document, `#${SCRIPT.panelId}`)) { const root = operationalQuery(panel,'[data-operational-settings-root]'); if (!root) return; const scroll = panel.scrollTop; operationalReplaceContent(root,operationalWindowSettingsInnerMarkup()); operationalWindowSyncSettingsUi(panel); panel.scrollTop = scroll; }
    function handleOperationalWindowSettingChange(target) { const path = target?.dataset?.operationalSetting; const arrayPath = target?.dataset?.operationalArrayPath; if (!path && !arrayPath) return false; try { const value = operationalWindowParseValue(target.dataset.operationalType,target.value,target.checked); if (arrayPath) { const list = [...(operationalFeatureValue(arrayPath) || [])]; const index = Number(target.dataset.operationalArrayIndex); const item = {...(list[index] || {})}; item[target.dataset.operationalArrayField] = value; list[index] = item; operationalFeatureSet(arrayPath,list); } else operationalFeatureSet(path,value); operationalWindowCommit(); } catch (error) { showToast('Operational Window setting could not be saved'); } return true; }
    function handleOperationalWindowAction(button) { const action = button?.dataset?.operationalAction; const path = button?.dataset?.operationalPath; if (!action || !path) return false; const editor = OP_OPERATIONAL_EDITORS.find(item => item.p === path); if (!editor) return false; const list = [...(operationalFeatureValue(path) || [])]; const index = Number(button.dataset.operationalIndex); if (action === 'add') list.push(JSON.parse(JSON.stringify(editor.v))); else if (action === 'remove' && Number.isInteger(index)) list.splice(index,1); else if (action === 'up' && index > 0) [list[index-1],list[index]] = [list[index],list[index-1]]; else if (action === 'down' && index >= 0 && index < list.length - 1) [list[index+1],list[index]] = [list[index],list[index+1]]; else return true; operationalFeatureSet(path,list); operationalWindowCommit(`${editor.l} updated`); operationalWindowRefreshSettingsPanel(); return true; }
    // Issue #464 end resilient launcher and typed operational settings.
'''
text = text.replace(anchor, block + '\n' + anchor, 1)

# Remove the old generated settings renderer/helper functions now replaced by the
# typed Issue #464 implementation.
text = replace_function(text, 'operationalWindowSettingsMarkup', "    function operationalWindowSettingsMarkup() { operationalWindowEnsureSettingsStyle(document); return `<div class=\"mcms-op-root\" data-operational-settings-root>${operationalWindowSettingsInnerMarkup()}</div>`; }")
text = replace_function(text, 'operationalWindowSyncSettingsUi', "    function operationalWindowSyncSettingsUi(panel = operationalQuery(document, `#${SCRIPT.panelId}`)) { operationalWindowEnsureSettingsStyle(document); operationalQueryAll(panel, '[data-operational-setting]').forEach(control => { const value = operationalFeatureValue(control.dataset.operationalSetting); const type = control.dataset.operationalType; if (type === 'boolean') control.checked = value === true; else if (document.activeElement !== control) control.value = type === 'csv' && Array.isArray(value) ? value.join(', ') : value ?? ''; }); operationalQueryAll(panel,'[data-operational-array-path]').forEach(control => { const item = operationalFeatureValue(control.dataset.operationalArrayPath)?.[Number(control.dataset.operationalArrayIndex)] || {}; const value = item[control.dataset.operationalArrayField]; const type = control.dataset.operationalType; if (type === 'boolean') control.checked = value === true; else if (document.activeElement !== control) control.value = type === 'csv' && Array.isArray(value) ? value.join(', ') : value ?? ''; }); operationalWindowApplyDependencies(panel); }")
text = replace_function(text, 'handleOperationalWindowSettingChange', "    function handleOperationalWindowSettingChange(target) { const path = target?.dataset?.operationalSetting; const arrayPath = target?.dataset?.operationalArrayPath; if (!path && !arrayPath) return false; try { const value = operationalWindowParseValue(target.dataset.operationalType,target.value,target.checked); if (arrayPath) { const list = [...(operationalFeatureValue(arrayPath) || [])]; const index = Number(target.dataset.operationalArrayIndex); const item = {...(list[index] || {})}; item[target.dataset.operationalArrayField] = value; list[index] = item; operationalFeatureSet(arrayPath,list); } else operationalFeatureSet(path,value); operationalWindowCommit(); } catch (error) { showToast('Operational Window setting could not be saved'); } return true; }")

# The insertion above intentionally defined the replacement functions; remove the
# duplicate copies inside the marker block, retaining its constants and helpers.
first = text.index(marker)
for duplicate in ('operationalWindowSettingsMarkup','operationalWindowSyncSettingsUi','handleOperationalWindowSettingChange'):
    starts = [m.start() for m in re.finditer(rf'(?m)^\s*function\s+{duplicate}\s*\(', text)]
    if len(starts) != 2:
        raise SystemExit(f'Expected two temporary {duplicate} definitions, found {len(starts)}')
    start, end = function_span(text, duplicate)
    if start < first:
        raise SystemExit(f'Unexpected {duplicate} ordering')
    text = text[:start] + text[end:]

# Make launcher creation map-independent and idempotently reparent it when the map
# appears or MissionChief replaces the map container.
old = """    function createControl(mapEl) {
        if (!mapEl || document.getElementById(SCRIPT.controlId)) return;"""
new = """    function createControl(mapEl) {
        const host = toolkitControlHost(mapEl, document);
        if (!host) return null;
        const existing = document.getElementById(SCRIPT.controlId);
        if (existing) {
            if (existing.parentElement !== host) host.appendChild(existing);
            existing.classList.toggle('mcms-control-fallback', !mapEl);
            return existing;
        }"""
if text.count(old) != 1:
    raise SystemExit('createControl opening anchor changed')
text = text.replace(old, new, 1)
old = """        mapEl.appendChild(control);
        renderScreenPins();
        updateUI();
    }"""
new = """        host.appendChild(control);
        control.classList.toggle('mcms-control-fallback', !mapEl);
        renderScreenPins();
        updateUI();
        return control;
    }"""
if text.count(old) != 1:
    raise SystemExit('createControl closing anchor changed')
text = text.replace(old, new, 1)

text = replace_function(text, 'ensureUi', """    function ensureUi() {
        operationalWindowEnsureSettingsStyle(document);
        const mapEl = getLargestLeafletMap();
        const control = createControl(mapEl);
        if (settingsPanelActivated && !document.getElementById(SCRIPT.panelId)) createPanel();
        if (control) ensureVersionStatusButton();
        if (mapEl) {
            const map = findLeafletMapInstance(false);
            if (state.economyMode && map) { applyLeafletEconomyPolicy(map); scheduleEconomyLayerSync(0); }
            if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(0);
            else if (!state.majorIncidentFeed.enabled) removeMajorIncidentFeed();
            const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
            if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay, mapEl);
        }
        return Boolean(control || document.getElementById(SCRIPT.controlId));
    }""")

# External removal of Toolkit UI must be detected before Toolkit-owned mutation
# filtering; otherwise a MissionChief map replacement can permanently remove it.
old = """            for (const mutation of mutations) {
                if (mutationBelongsToToolkit(mutation)) continue;
                externalMutationFound = true;"""
new = """            for (const mutation of mutations) {
                const removesToolkitUi = mutationRemovesToolkitUi(mutation);
                if (removesToolkitUi) toolkitUiRemoved = true;
                if (mutationBelongsToToolkit(mutation) && !removesToolkitUi) continue;
                externalMutationFound = true;"""
if text.count(old) != 1:
    raise SystemExit('main mutation loop anchor changed')
text = text.replace(old, new, 1)

# Permanent low-cost launcher integrity task. This remains independent of all
# operational modules and repairs/reparents the control without duplicating it.
old = "    function registerBootMaintenanceTasks() {\n"
new = """    function registerBootMaintenanceTasks() {
        runtimeRegisterTask('ui-integrity', 2500, () => { if (!document.hidden) return ensureUi(); }, { intervalResolver: () => document.hidden ? 30000 : 2500, economyIntervalMs: 5000, economyIntervalResolver: () => document.hidden ? 30000 : 5000 });
"""
if text.count(old) != 1:
    raise SystemExit('maintenance-task anchor changed')
text = text.replace(old, new, 1)

# Delegate structured-editor actions through the existing panel click listener.
old = """            const actionButton = closestEventTarget(event, '[data-action]');
            if (closeButton) { closePanel({ restoreFocus: true }); return; }"""
new = """            const actionButton = closestEventTarget(event, '[data-action]');
            const operationalAction = closestEventTarget(event, '[data-operational-action]');
            if (operationalAction && handleOperationalWindowAction(operationalAction)) { event.preventDefault(); return; }
            if (closeButton) { closePanel({ restoreFocus: true }); return; }"""
if text.count(old) != 1:
    raise SystemExit('panel click delegation anchor changed')
text = text.replace(old, new, 1)

SOURCE.write_text(text, encoding='utf-8')
for target in (ROOT / 'MissionChief_Map_Command_Toolkit.user.js', ROOT / 'MissionChief_Map_Command_Toolkit.txt'):
    target.write_text(text, encoding='utf-8')

TEST.write_text(r'''#!/usr/bin/env python3
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[2]
text = (ROOT / 'src/MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
def section(start, end):
    left=text.index(start); right=text.index(end,left); return text[left:right]
block=section('// Issue #464 resilient launcher and typed operational settings.','// Issue #464 end resilient launcher and typed operational settings.')
for path in ['requirements.enabled','requirements.calcMaxStaff','requirements.hoverTip','requirements.viewMode','requirements.sort','requirements.sortDir','callWindow.enabled','callWindow.generationDate','callWindow.yellowBorderHours','callWindow.redBorder','callWindow.patientSummary','callWindow.collapsiblePatients','callWindow.collapsiblePatientsMinPatients','callWindow.arrCounter','callWindow.arrCounterAsBadge','callWindow.arrClickHighlight','callWindow.arrClickHighlightColor','callWindow.arrClickHighlightWidth','callWindow.arrCounterResetSelection','callWindow.arrMatchHighlight','callWindow.arrMatchHighlightAllWords','callWindow.arrTime','callWindow.arrSpecs','callWindow.alarmTime','callWindow.stickyHeader','callWindow.loadMoreVehiclesInHeader','callWindow.hideVehicleList','callWindow.centerMap','callWindow.stagingAreaSelectedCounter','callWindow.vehicleTypeInList','callWindow.remainingPatientTime','callWindow.vehicleCounter','callWindow.vehicleCounterColor','callWindow.vehicleListPermanentSearch','callWindow.playerCounter','callWindow.playerCounterColor','callWindow.selectedVehicleCounter','callWindow.selectedVehicleCounterVehicleTypes','callWindow.arrSearch','callWindow.arrSearchDissolveCategories','callWindow.arrSearchCompactResults','callWindow.arrSearchSelectOnEnter','callWindow.arrSearchClearOnEnter','callWindow.arrSearchAutoFocus','callWindow.arrSearchDropdown','callWindow.arrSearchCloseDropdownOnSelect','callWindow.moreReleasePatientButtons','missionList.enabled','transport.enabled','transport.autoOpenTransportRequest','transport.autoClickSuccessButtons']:
    assert f"p:'{path}'" in block, path
for hidden in ['requirements.overlay','requirements.minified','requirements.pushRight','requirements.drag','missionList.starredMissions','missionList.collapsedMissions']:
    assert f"p:'{hidden}'" not in block, hidden
for editor in ['callWindow.tailoredTabs','callWindow.missionKeywords','callWindow.alarmIcons','callWindow.arrCategoryColors']:
    assert editor in block
assert 'data-operational-type="json"' not in block and 'mcms-operational-json-row' not in block
assert 'mcms-op-switch' in block and 'mcms-op-grid' in block and '@media(max-width:760px)' in block
control=section('    function createControl(', '    function createPanel(')
assert 'const host = toolkitControlHost(mapEl, document);' in control
assert "existing.classList.toggle('mcms-control-fallback', !mapEl);" in control
assert 'return control;' in control
ensure=section('    function ensureUi()', '    function mutationBelongsToToolkit')
assert ensure.index('const control = createControl(mapEl);') < ensure.index('if (mapEl) {')
assert 'return Boolean(control || document.getElementById(SCRIPT.controlId));' in ensure
boot=section('    function boot()', '    function scheduleBoot()')
assert boot.index('const removesToolkitUi = mutationRemovesToolkitUi(mutation);') < boot.index('mutationBelongsToToolkit(mutation)')
maintenance=section('    function registerBootMaintenanceTasks()', '    function boot()')
assert "runtimeRegisterTask('ui-integrity'" in maintenance
assert "intervalResolver: () => document.hidden ? 30000 : 2500" in maintenance
panel=section('    function createPanel()', '    function updateUI()')
assert "closestEventTarget(event, '[data-operational-action]')" in panel
meta=re.search(r'^//\s*@version\s+([^\s]+)',text,re.M).group(1)
runtime=re.search(r"version:\s*'([^']+)'",text).group(1)
assert meta == runtime == '5.0.6'
print('Issue #464 resilient launcher and typed operational settings contract passed.')
''', encoding='utf-8')

validator = VALIDATOR.read_text(encoding='utf-8')
constant_anchor = "ISSUE458_REQUIREMENTS_SOURCE_RUNTIME = ROOT / \".github\" / \"scripts\" / \"test_issue458_requirements_source_runtime.js\"\n"
constant_add = constant_anchor + "ISSUE464_LAUNCHER_SETTINGS_CONTRACT = ROOT / \".github\" / \"scripts\" / \"test_issue464_launcher_settings_contract.py\"\n"
if constant_anchor not in validator:
    raise SystemExit('Validator constant anchor missing')
validator = validator.replace(constant_anchor, constant_add, 1)
required_anchor = 'ISSUE456_REQUIREMENTS_TRUTH_RUNTIME, ISSUE458_REQUIREMENTS_SOURCE_RUNTIME]'
if required_anchor not in validator:
    raise SystemExit('Validator required-list anchor missing')
validator = validator.replace(required_anchor, 'ISSUE456_REQUIREMENTS_TRUTH_RUNTIME, ISSUE458_REQUIREMENTS_SOURCE_RUNTIME, ISSUE464_LAUNCHER_SETTINGS_CONTRACT]', 1)
run_anchor = """        if issue458_requirements_source.returncode != 0:
            fail("Issue #458 requirements source-discovery runtime failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))"""
run_add = """        if issue458_requirements_source.returncode != 0:
            fail("Issue #458 requirements source-discovery runtime failed")

        issue464_launcher_settings = subprocess.run(
            [sys.executable, str(ISSUE464_LAUNCHER_SETTINGS_CONTRACT)], cwd=ROOT,
        )
        if issue464_launcher_settings.returncode != 0:
            fail("Issue #464 launcher/settings contract failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))"""
if run_anchor not in validator:
    raise SystemExit('Validator runtime anchor missing')
validator = validator.replace(run_anchor, run_add, 1)
VALIDATOR.write_text(validator, encoding='utf-8')

changelog = CHANGELOG.read_text(encoding='utf-8')
entry = '''## [5.0.6] - 2026-07-23

### Fixed

- Made the Toolkit launcher independent of Leaflet map discovery, with a safe fixed fallback that reparents to the live map when available.
- Added a permanent idempotent UI-integrity task and corrected mutation ordering so MissionChief map replacements cannot silently remove the launcher.
- Replaced the Operational Window label dump with typed, persisted switches, number inputs, colour controls, selects, dependency states and structured list editors.
- Mapped the complete Enhanced Requirements, Extended Call Window, Extended Mission List and opt-in Transport settings to their Toolkit runtime state.
- Hid internal overlay, minimised, push-right, drag, starred and collapsed state from user-facing settings.
- Added responsive two-column desktop and single-column Tablet/iOS layouts with safe text wrapping and no horizontal overflow.

'''
if '## [5.0.6]' in changelog:
    raise SystemExit('v5.0.6 changelog already exists')
insert_at = changelog.find('## [')
if insert_at < 0:
    raise SystemExit('Changelog release anchor missing')
changelog = changelog[:insert_at] + entry + changelog[insert_at:]
CHANGELOG.write_text(changelog, encoding='utf-8')

# Remove temporary diagnostic artefacts and superseded diagnostic package.
for path in [
    ROOT / '.github/diagnostics/issue464-runtime-settings.txt',
    ROOT / '.github/diagnostics/issue464-ui-lifecycle.txt',
    ROOT / '.github/diagnostics/issue464-call-window-runtime.txt',
    ROOT / '.github/development-packages/issue464-call-window-runtime-diagnostic.py',
]:
    path.unlink(missing_ok=True)

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
source_lines = len(text.splitlines())
old_expected = int(fixture['expectedSourceLines'])
delta = source_lines - old_expected
changes = [item for item in fixture.get('approvedNonStyleChanges', []) if item.get('issue') != 464]
changes.append({'issue': 464, 'phase': 'resilient-launcher-and-typed-operational-settings', 'lines': delta})
fixture['approvedNonStyleChanges'] = changes
fixture['approvedNonStyleSourceLines'] = sum(int(item['lines']) for item in changes)
fixture['expectedSourceLines'] = source_lines
fixture['candidateVersion'] = '5.0.6'
fixture['candidateSourceSha256'] = hashlib.sha256(text.encode('utf-8')).hexdigest()
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

SELF.unlink(missing_ok=True)
print(json.dumps({'version':'5.0.6','sourceLines':source_lines,'lineDelta':delta,'sha256':fixture['candidateSourceSha256']}, indent=2))
