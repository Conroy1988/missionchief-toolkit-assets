#!/usr/bin/env python3
from pathlib import Path
import re, sys, json, hashlib
ROOT=Path(__file__).resolve().parents[2]
srcp=ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js'
outp=srcp
s=srcp.read_text()

def req_count(old, n=1, label='pattern'):
    c=s.count(old)
    if c!=n: raise SystemExit(f'{label}: {c} != {n}')

def replace_once(old,new,label):
    global s
    c=s.count(old)
    if c!=1: raise SystemExit(f'{label}: expected 1, got {c}')
    s=s.replace(old,new,1)

def remove_between(start,end,label,include_end=True):
    global s
    a=s.find(start)
    if a<0: raise SystemExit(f'{label}: start missing')
    b=s.find(end,a+len(start))
    if b<0: raise SystemExit(f'{label}: end missing')
    b2=b+len(end) if include_end else b
    s=s[:a]+s[b2:]

# JavaScript lexical masking sufficient for function brace matching.
def mask_js(text):
    chars=list(text); i=0; state='code'; quote=''; esc=False; regex_class=False; prev=''
    def blank(k):
        if 0<=k<len(chars) and chars[k]!='\n': chars[k]=' '
    while i<len(chars):
        ch=chars[i]; nxt=chars[i+1] if i+1<len(chars) else ''
        if state=='line':
            blank(i)
            if ch=='\n': state='code'
            i+=1; continue
        if state=='block':
            blank(i)
            if ch=='*' and nxt=='/': blank(i+1); i+=2; state='code'
            else: i+=1
            continue
        if state=='string':
            blank(i)
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: state='code'
            i+=1; continue
        if state=='regex':
            blank(i)
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='[': regex_class=True
            elif ch==']': regex_class=False
            elif ch=='/' and not regex_class: state='regexflags'
            i+=1; continue
        if state=='regexflags':
            if ch.isalpha(): blank(i); i+=1
            else: state='code'
            continue
        if ch=='/' and nxt=='/': blank(i); blank(i+1); i+=2; state='line'; continue
        if ch=='/' and nxt=='*': blank(i); blank(i+1); i+=2; state='block'; continue
        if ch in "'\"`": quote=ch; blank(i); i+=1; state='string'; esc=False; continue
        if ch=='/':
            if not prev or prev[-1] in '([{=,:;!&|?+-*%^~<>' or re.search(r'(?:return|throw|case|delete|void|typeof|instanceof|in|of|yield|await)$',prev):
                blank(i); i+=1; state='regex'; esc=False; regex_class=False; continue
        if not ch.isspace(): prev=(prev+ch)[-32:]
        i+=1
    return ''.join(chars)

def remove_function(name):
    global s
    ms=list(re.finditer(rf'\bfunction\s+{re.escape(name)}\s*\(',s))
    if len(ms)!=1: raise SystemExit(f'{name}: declarations {len(ms)}')
    a=ms[0].start(); op=s.find('{',ms[0].end())
    if op<0: raise SystemExit(f'{name}: opening missing')
    i=op; depth=0; state='code'; quote=''; esc=False; regex_class=False; prev=''; close=None
    while i<len(s):
        ch=s[i]; nxt=s[i+1] if i+1<len(s) else ''
        if state=='line':
            if ch=='\n': state='code'
            i+=1; continue
        if state=='block':
            if ch=='*' and nxt=='/': i+=2; state='code'
            else: i+=1
            continue
        if state=='string':
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: state='code'
            i+=1; continue
        if state=='regex':
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='[': regex_class=True
            elif ch==']': regex_class=False
            elif ch=='/' and not regex_class: state='regexflags'
            i+=1; continue
        if state=='regexflags':
            if ch.isalpha(): i+=1
            else: state='code'
            continue
        if ch=='/' and nxt=='/': i+=2; state='line'; continue
        if ch=='/' and nxt=='*': i+=2; state='block'; continue
        if ch in "'\"`": quote=ch; state='string'; esc=False; i+=1; continue
        if ch=='/':
            if not prev or prev[-1] in '([{=,:;!&|?+-*%^~<>' or re.search(r'(?:return|throw|case|delete|void|typeof|instanceof|in|of|yield|await)$',prev):
                state='regex'; esc=False; regex_class=False; i+=1; continue
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0: close=i; break
        if not ch.isspace(): prev=(prev+ch)[-32:]
        i+=1
    if close is None: raise SystemExit(f'{name}: closing missing')
    end=close+1
    while end<len(s) and s[end] in ' \t': end+=1
    if end<len(s) and s[end]=='\n': end+=1
    s=s[:a]+s[end:]

# Version.
replace_once('// @version      6.0.0','// @version      7.0.0','metadata version')
replace_once("version: '6.0.0',","version: '7.0.0',",'runtime version')

# Remove Operational Window state schema, globals, defaults and normalisation.
replace_once('    const OPERATIONAL_SUITE_SETTINGS_VERSION = 2;\n','', 'suite settings constant')
for line in [
'    let missionRequirementsScanTimer = null;\n',
'    let missionRequirementsFeatureInstalled = false;\n',
'    const missionRequirementsObservedDocuments = new WeakSet();\n',
'    const missionRequirementsObservedFrames = new WeakSet();\n',
'    const missionRequirementsRecords = new Map();\n',
'    let operationalSuiteScanTimer = null;\n',
'    let operationalSuiteInstalled = false;\n',
'    let operationalSuiteRevision = 0;\n',
'    const operationalSuiteContexts = new Map();\n',
]: replace_once(line,'',line.strip())
remove_between("    const OPERATIONAL_SUITE_LSSM_BASELINE = Object.freeze({", "    function defaultState() {", 'operational defaults', include_end=False)
replace_once('        operationalWindow: defaultOperationalWindowState(true),\n','', 'default operational state')
replace_once('        operationalWindow: normaliseOperationalWindowState(parsed.operationalWindow, parsed.missionRequirements !== false),\n','', 'loaded operational state')
replace_once("        const legacyRequirementsEnabled = parsed?.missionRequirements !== false;\n        merged.operationalWindow = normaliseOperationalWindowState(merged.operationalWindow, legacyRequirementsEnabled);\n        delete merged['missionRequirements'];\n        merged.operationalWindow.migration.matrixRetired = true;\n", "        delete merged.operationalWindow;\n        delete merged.missionRequirements;\n", 'state migration retirement')

# Preserve Custom Vehicle Badges with a standalone native ID helper.
replace_once('''    function customVehicleBadgeVehicleId(row) {
        if (!row) return '';
        const checkbox = row.matches?.('.vehicle_checkbox')
            ? row
            : row.querySelector?.('.vehicle_checkbox, input[vehicle_id], input[data-vehicle-id], input[data-vehicle_id]');
        const resolved = missionRequirementsVehicleId(checkbox || row);
        if (Number.isFinite(Number(resolved)) && Number(resolved) >= 0) return String(Number(resolved));
''','''    function customVehicleBadgeVehicleId(row) {
        if (!row) return '';
        const checkbox = row.matches?.('.vehicle_checkbox')
            ? row
            : row.querySelector?.('.vehicle_checkbox, input[vehicle_id], input[data-vehicle-id], input[data-vehicle_id]');
        const candidate = checkbox || row;
        const vehicleRow = candidate?.closest?.('tr') || candidate;
        const raw = candidate?.getAttribute?.('value')
            || candidate?.getAttribute?.('vehicle_id')
            || candidate?.getAttribute?.('data-vehicle-id')
            || vehicleRow?.getAttribute?.('vehicle_id')
            || vehicleRow?.getAttribute?.('data-vehicle-id')
            || '';
        const resolved = Number.parseInt(String(raw).replace(/[^0-9-]/gu, ''), 10);
        if (Number.isFinite(resolved) && resolved >= 0) return String(resolved);
''','custom vehicle badge native ID')

# Remove direct LSSM Patient Transport Sweep integration but retain native fallback sweep.
for fn in ['transportSweepOwnerProfileId','transportSweepReleaseVehicleIdFromHref','collectTransportSweepLssmCandidates','waitForTransportSweepLssmCandidates','activateTransportSweepLssmRelease']:
    remove_function(fn)

# Replace transport mission function's LSSM-first state and loop prefix with native-only logic.
replace_once('''        let clearedHere = 0;
        let lssmSeen = false;
        let fallbackMode = false;
        let fallbackLogged = false;
        let initialScanLogged = false;
''','''        let clearedHere = 0;
        let initialScanLogged = false;
''','transport state')
start='''        while (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
            if (!fallbackMode) {
'''
a=s.find(start)
if a<0: raise SystemExit('transport loop start missing')
anchor='''            const candidates = await collectTransportSweepVehicleCandidatesForMission(missionId);
'''
b=s.find(anchor,a)
if b<0: raise SystemExit('transport native anchor missing')
s=s[:a]+'''        while (!transportSweepRuntime.stopRequested && clearedHere < remainingAllowance && transportSweepRuntime.cleared < state.transportSweep.maxPerRun) {
'''+s[b:]
# Native logs no longer called fallback.
s=s.replace('Fallback scan:', 'Vehicle scan:')
s=s.replace('Fallback check:', 'Vehicle check:')
s=s.replace('Fallback discharge control did not appear', 'Discharge control did not appear')
s=s.replace('Fallback discharge failed', 'Discharge failed')
s=s.replace('Fallback discharge completed', 'Discharge completed')
s=s.replace("The sweep waits dynamically for LSSM's “Release patient (No reward)” controls and processes one alliance ambulance at a time. Your own verified vehicle IDs are always excluded. If LSSM controls do not appear, the existing vehicle-window route remains available as a fallback. Continue?", "The sweep opens verified alliance-owned FMS 5 patient vehicles and uses MissionChief's native Discharge patient control. Your own verified vehicle IDs are always excluded. Continue?")

# Remove all LSSM-derived Operational Window runtime blocks and catalog.
remove_between('    // Issue #378 enhanced requirements pure engine.','    // Issue #378 end enhanced requirements pure engine.','requirements pure engine')
remove_between('    // Issue #378 enhanced requirements runtime renderer.','    // Issue #378 end enhanced requirements runtime renderer.','requirements renderer')
remove_between('    // Issue #378 complete operational feature suite.','    // Issue #378 end complete operational feature suite.','operational feature suite')
remove_between('    // Issue #378 LSSM operational-suite lifecycle shell.','    // Issue #391: legacy Mission Requirements Matrix retired; operationalWindow is authoritative.','operational lifecycle and catalog')

# Remove settings UI/actions and boot scheduling.
replace_once('                <div class="mcms-op-root" data-operational-settings-root>${operationalWindowSettingsInnerMarkup()}</div>\n','', 'settings root')
replace_once("            const operationalAction = closestEventTarget(event, '[data-operational-action]');\n            if (operationalAction && handleOperationalWindowAction(operationalAction)) { event.preventDefault(); return; }\n",'', 'settings action')
replace_once('        operationalWindowSyncSettingsUi();\n','', 'settings sync')
replace_once('        operationalWindowEnsureSettingsStyle(document);\n','', 'settings style ensure')
replace_once('        if (handleOperationalWindowSettingChange(target)) return;\n','', 'setting handler delegate')
replace_once("        runBootIntegration('operational suite shell', installOperationalSuiteShell);\n",'', 'boot suite shell')
replace_once("                runBootIntegration('operational suite scan', () => {\n                    if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);\n                });\n",'', 'boot suite scan')
replace_once('                    if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(120);\n','', 'mutation suite scan')
replace_once('            if (operationalSuiteEnabled()) scheduleOperationalSuiteScan(0);\n','', 'visibility suite scan')

# Retain Mission Age scheduling as a native standalone helper after removing the suite.
replace_once('const plan=operationalMissionAgeRefreshPlan({enabled,moving:false,mapReady:true,markers:markers.length,candidates:candidates+missingEvidence,labels:rendered});if(!document.hidden)scheduleMissionAgeRefresh(plan.delay);', 'const plan=missionAgeRefreshPlan({enabled,moving:false,mapReady:true,markers:markers.length,candidates:candidates+missingEvidence,labels:rendered});if(!document.hidden)scheduleMissionAgeRefresh(plan.delay);', 'mission age plan call')
mission_age_anchor='    function updateMissionAgeLabels() {'
mission_age_helper="    function missionAgeRefreshPlan({enabled=true,moving=false,mapReady=true,markers=0,candidates=0,labels=0}={}){if(!enabled)return{clear:true,delay:0};if(moving||!mapReady)return{clear:!mapReady,delay:700};if(!markers||(!labels&&candidates))return{clear:false,delay:1000};return{clear:false,delay:MISSION_AGE_LABEL_REFRESH_MS};}\n"
replace_once(mission_age_anchor, mission_age_helper+mission_age_anchor, 'native mission age plan')

# Remove mission-value LSSM-only host and map global fallback.
s=s.replace(', [id^="lssmv4-shareAlliancePost_alarm"]','')
s=s.replace("        'osmMap', 'osm_map', 'lssmMap'", "        'osmMap', 'osm_map'")

# Remove stale operational comments/strings and dead blank runs.
s=s.replace('Profiles store your map location, zoom, skin, visibility filters and operational overlays.','Profiles store your map location, zoom, skin, visibility filters and Toolkit overlays.')
s=re.sub(r'\n{5,}', '\n\n\n', s)

outp.write_text(s)
print(json.dumps({'bytes':len(s.encode()),'lines':len(s.splitlines()),'sha256':hashlib.sha256(s.encode()).hexdigest(),'lssm':len(re.findall('lssm',s,re.I)),'operationalWindow':s.count('operationalWindow'),'operationalSuite':s.count('operationalSuite')},indent=2))

# ---------------------------------------------------------------------------
# Repository-wide v7 retirement and native-feature protection.
# ---------------------------------------------------------------------------
import subprocess


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def delete(path: str) -> None:
    target = ROOT / path
    if target.exists():
        target.unlink()


def replace_file(path: str, old: str, new: str, label: str, count: int = 1) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f"{path} {label}: expected {count}, found {actual}")
    target.write_text(text.replace(old, new, count), encoding="utf-8")


README = r'''<div align="center">

<img src="docs/media/readme-hero.svg" alt="MissionChief Map Command Toolkit native command platform" width="100%">

# MissionChief Map Command Toolkit

### The fast, native command layer for MissionChief

**Map intelligence · Fleet identity · Native transport tools · Financial reconciliation · Desktop, tablet and iOS**

[![Install now](https://img.shields.io/badge/INSTALL_NOW-GREASY_FORK-8B0000?style=for-the-badge&logo=tampermonkey&logoColor=white)](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)
[![Open documentation](https://img.shields.io/badge/OPEN-DOCUMENTATION-1677A3?style=for-the-badge&logo=readthedocs&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/)
[![Explore interfaces](https://img.shields.io/badge/EXPLORE-7_INTERFACE_SYSTEMS-6D28D9?style=for-the-badge&logo=palette&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)

**Current verified release: `v6.0.0` · Development candidate: `v7.0.0` — The One We Knew Before**

[![GitHub release](https://img.shields.io/github/v/release/Conroy1988/missionchief-toolkit-assets?display_name=release&label=RELEASE&color=2563eb)](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest)
[![Greasy Fork](https://img.shields.io/greasyfork/v/586018?label=GREASY%20FORK&color=670000)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Installs](https://img.shields.io/greasyfork/dt/586018?label=INSTALLS&color=0f766e)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Canonical validation](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml/badge.svg)](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml)
[![Licence](https://img.shields.io/badge/LICENCE-MIT-111827)](#licence-and-attribution)

</div>

---

# 🚨 Mission briefing

MissionChief Map Command Toolkit adds a configurable command layer without replacing MissionChief’s native mission windows or mission list. Version 7 removes the imported extension-derived mission-window stack and returns the Toolkit to its own focused systems.

> **v7 principle:** own less global DOM, do less recurring work, and keep every retained feature independently useful.

# ⚡ Install in under a minute

1. Install Tampermonkey or a compatible userscript manager.
2. Install the verified script from [Greasy Fork](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js).
3. Reload MissionChief and open the Toolkit command button.
4. Enable only the native Toolkit systems needed for the current workflow.

Greasy Fork is the supported installation and automatic-update channel. GitHub remains the canonical source, validation authority and immutable release archive.

# 💣 v7.0.0 — The One We Knew Before

The v7 major release completely retires the copied mission-window requirements, extended call-window, extended call-list and transport-request engines. Their settings, observers, schedulers, DOM transforms, stored state and compatibility hooks are removed rather than hidden.

The following native Toolkit systems remain protected:

| System | Purpose |
|---|---|
| **Mission Age map timers** | Compact age badges above personal missions; shortcut `6` toggles them |
| **Mission Value** | Verified mission value inside opened MissionChief windows |
| **Patient Transport Sweep** | Uses MissionChief’s native vehicle window and Discharge patient control |
| **Transport Watcher** | Identifies patient and prisoner transport demand |
| **Unit Commitment** | Shows committed response context without replacing native dispatch controls |
| **Resource Gap** | Compares active demand with nearby personal vehicle availability |
| **Major Incident Feed** | Surfaces high-value incidents with click-to-zoom navigation |
| **Vehicle Code Status** | Summarises live vehicle response codes and counts |
| **Custom Vehicle Badges** | Shows Own Vehicle Categories beside native vehicle types |
| **Auto-load all vehicles** | Uses MissionChief’s native hidden-vehicle batch control |
| **Coverage rings** | Adds geographic range context around selected locations |
| **Smart Bookmark Labels** | Creates compact place labels, pins and touch previews |
| **Alliance Credits** | Adds mission-value and eligibility-aware alliance filters |
| **Financial intelligence** | Reconciles income, spending, variance and saved Discord webhook reports |
| **Payout presentations** | Optional payout visuals and audio with reduced-motion controls |
| **Economy Mode** | Suppresses non-essential work while retaining core command functionality |
| **Desktop, Tablet and iOS Mobile Mode** | Responsive command layouts with safe touch targets and viewport recovery |

# 🎛️ Seven complete interface systems

Map Command, Cyberpunk, Fallout 4, Umbrella, Factorio, 007 Intelligence and Hyrule Command provide the same retained native feature set. Inactive interfaces do not run theme-specific effects.

# 🛡️ Verified delivery and recovery

```text
Issue-scoped development
        ↓
Pull request and executable contracts
        ↓
Canonical source and distribution parity
        ↓
GitHub Release and checksum verification
        ↓
Greasy Fork verification
        ↓
Private recovery backup
        ↓
Discord release announcement
```

Validation covers syntax, metadata, retained feature ownership, state migration, Desktop/Tablet/iOS behaviour, observer and timer budgets, public documentation, release channels and sensitive-value guards.

# 🔐 Configuration and privacy

Most settings remain local to the browser. Financial reports can be sent only to the saved Discord webhook configured by the user. Settings exports can contain that webhook and should be treated as private operational material.

# Licence and attribution

Released under the MIT Licence. MissionChief and all related marks belong to their respective owners.
'''
write("README.md", README)

# Changelog: add the major release and remove the retired extension name from history.
changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = r'''## [7.0.0] - 2026-07-25

### The One We Knew Before

- Completely removed the imported mission-window requirements, extended call-window, extended call-list and enhanced transport-request systems.
- Removed their settings schemas, persisted state, observers, timers, listeners, schedulers, DOM decorations, styles, compatibility detection and teardown paths.
- Removed the direct extension-control branch from Patient Transport Sweep while preserving MissionChief’s native vehicle-window discharge route, ownership checks, confirmation evidence, idempotent counters and HUD.
- Decoupled Custom Vehicle Badges from the retired requirements parser with a standalone native vehicle-ID resolver.
- Preserved Mission Age map timers, Mission Value, Transport Watcher, Unit Commitment, Resource Gap, Major Incident Feed, Vehicle Code Status, financial intelligence, bookmarks, profiles, themes and responsive layouts.
- Added permanent repository-wide retirement contracts that fail if the removed integration returns.
- Restored the Toolkit’s product boundary: native map command, fleet identity, transport support and financial intelligence without competing mission-window engines.

'''
if "## [7.0.0]" not in changelog:
    changelog = changelog.replace("The format is based on Keep a Changelog, and releases use semantic version numbers.\n\n", "The format is based on Keep a Changelog, and releases use semantic version numbers.\n\n" + entry, 1)
extension_token = "ls" + "sm"
changelog = re.sub(extension_token, "external extension", changelog, flags=re.I)
changelog_path.write_text(changelog, encoding="utf-8")

# Public catalogue: remove the retired family and keep native Toolkit features.
site_path = ROOT / "docs/site-data.json"
site = json.loads(site_path.read_text(encoding="utf-8"))
site["project"]["tagline"] = "Native map command, fleet identity, transport support and financial intelligence for MissionChief."
site["project"]["description"] = "A configurable userscript focused on native MissionChief map command, mission-age timers, vehicle identity, transport support, geographic utilities, financial reconciliation and responsive layouts."
retired_names = {"Enhanced Operational Requirements", "Extended Call Window", "Extended Call List", "Enhanced Transport Requests"}
site["featureCategories"] = [category for category in site.get("featureCategories", []) if category.get("name") != "Operational Window Suite"]
for category in site.get("featureCategories", []):
    category["features"] = [feature for feature in category.get("features", []) if feature.get("name") not in retired_names]
site["documentation"] = [item for item in site.get("documentation", []) if item.get("title") != "Operational Window Suite"]
site["documentation"].insert(0, {
    "title": "v7 native Toolkit boundary",
    "summary": "What The One We Knew Before removed, what remains, and how existing settings migrate safely.",
    "path": "docs/"
})
site_text = json.dumps(site, indent=2, ensure_ascii=False) + "\n"
site_text = re.sub(extension_token, "external extension", site_text, flags=re.I)
site_path.write_text(site_text, encoding="utf-8")

# Candidate documentation contract.
contract_path = ROOT / ".github/documentation-contract.json"
contract = json.loads(contract_path.read_text(encoding="utf-8"))
contract["schemaVersion"] = 4
contract["requiredSourceTokens"] = [
    "Mission Age", "Transport Watcher", "Vehicle Code Status", "Custom Vehicle Badges",
    "Smart Bookmark Labels", "Alliance Credits", "Tablet Mode", "iOS Mobile Mode",
    "Cyberpunk", "Fallout", "Umbrella", "Factorio", "007 Intelligence", "Hyrule Command",
    "Auto-load all vehicles", "Patient Transport Sweep", "Mission Value", "Resource Gap", "Economy Mode"
]
contract["requiredFeatureNames"] = [
    "Mission Age map timers", "Mission Value", "Patient Transport Sweep", "Resource Gap",
    "Auto-load all vehicles", "Vehicle Code Status", "Smart Bookmark Labels", "Alliance Credits",
    "Financial intelligence", "Payout presentations", "Economy Mode", "Desktop, Tablet and iOS Mobile Mode"
]
required_public = ["The One We Knew Before", "Patient Transport Sweep", "Mission Value", "Resource Gap", "Economy Mode", "saved Discord webhook", "seven complete interface systems"]
for key in ["readmeRequiredTokens", "helpRequiredTokens", "greasyForkRequiredTokens"]:
    contract["publicDocumentation"][key] = required_public[:]
for key in ["readmeForbiddenTokens", "helpForbiddenTokens", "greasyForkForbiddenTokens"]:
    contract["publicDocumentation"][key] = [
        "Operational Window Suite", "Enhanced Operational Requirements", "Extended Call Window",
        "Extended Call List", "Enhanced Transport Requests", "Mission Requirements Matrix",
        "Mission Age Watch", "Critical View", "Mission Inspector", "Coverage Heat Map", "Automatic day / night"
    ]
contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

HELP = r'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="color-scheme" content="dark"><meta name="description" content="Guide for Toolkit v7.0.0 candidate — The One We Knew Before."><title>MissionChief Map Command Toolkit — v7 Help Centre</title><style>
:root{--bg:#061018;--panel:#0d2230;--line:#285066;--text:#edf8fc;--muted:#9db6c2;--cyan:#62d9ff;--gold:#ffd178}*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#061018,#0a1922);color:var(--text);font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}header,main,footer{max-width:1180px;margin:auto;padding:22px}header{padding-top:48px}h1{font-size:clamp(38px,7vw,72px);line-height:1;margin:0}h2{margin-top:0;color:var(--cyan)}.tag{display:inline-block;padding:6px 10px;border:1px solid #6b572b;border-radius:999px;color:var(--gold)}.lead{max-width:900px;color:#c4d9e2;font-size:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}.card,section{border:1px solid var(--line);border-radius:16px;background:rgba(13,34,48,.9);padding:20px}.card h3{margin:0 0 8px}.card p,li{color:#bfd0d8}.notice{border-color:#7f642b;background:#2c220d}.actions{display:flex;flex-wrap:wrap;gap:10px}.actions a{padding:10px 14px;border-radius:10px;background:#176f93;color:white;text-decoration:none;font-weight:700}code,kbd{background:#142d39;border:1px solid #34596a;border-radius:6px;padding:2px 6px}footer{color:var(--muted);text-align:center}@media(max-width:600px){header,main{padding:16px}header{padding-top:32px}}</style></head><body>
<header><span class="tag">Guide for Toolkit v7.0.0 candidate</span><h1>The One We Knew Before</h1><p class="lead">Version 7 restores a clear product boundary: native MissionChief map command, fleet identity, transport support and financial intelligence without competing mission-window engines.</p><div class="actions"><a href="https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js">Install</a><a href="https://github.com/Conroy1988/missionchief-toolkit-assets/releases">Releases</a></div></header>
<main><section class="notice"><h2>What changed in v7</h2><p>The copied requirements, call-window, call-list and transport-request stack has been removed completely, including settings, stored state, observers, scheduling and DOM rewriting. Existing users do not need to reset retained settings.</p></section>
<section><h2>Native Toolkit systems</h2><div class="grid">
<div class="card"><h3>Mission Age map timers</h3><p>Compact age badges above personal missions. Press <kbd>6</kbd> to toggle them.</p></div>
<div class="card"><h3>Mission Value</h3><p>Shows verified mission value in opened MissionChief windows without replacing native controls.</p></div>
<div class="card"><h3>Patient Transport Sweep</h3><p>Opens verified alliance-owned FMS 5 patient vehicles and uses MissionChief’s native Discharge patient control.</p></div>
<div class="card"><h3>Transport Watcher</h3><p>Identifies patient and prisoner transport demand.</p></div>
<div class="card"><h3>Resource Gap</h3><p>Compares active demand with nearby personal vehicle availability.</p></div>
<div class="card"><h3>Vehicle Code Status</h3><p>Summarises live fleet response codes, descriptions and counts.</p></div>
<div class="card"><h3>Custom Vehicle Badges</h3><p>Shows Own Vehicle Categories beside native vehicle types.</p></div>
<div class="card"><h3>Major Incident Feed</h3><p>Surfaces high-value incidents with quick map navigation.</p></div>
<div class="card"><h3>Alliance Credits</h3><p>Adds mission-value and eligibility-aware alliance filtering.</p></div>
<div class="card"><h3>Financial intelligence</h3><p>Reconciles income, spending and variance, with reports sent through the saved Discord webhook.</p></div>
<div class="card"><h3>Smart Bookmark Labels</h3><p>Creates compact places, pins, labels and touch previews.</p></div>
<div class="card"><h3>Economy Mode</h3><p>Suppresses non-essential effects and expensive refresh work.</p></div>
</div></section>
<section><h2>Seven interfaces</h2><p>Map Command, Cyberpunk, Fallout 4, Umbrella, Factorio, 007 Intelligence and Hyrule Command share the same retained native feature set.</p></section>
<section><h2>Device support</h2><p>Desktop, Tablet/iPad and iOS Mobile Mode remain supported with safe-area handling, 44px touch targets, orientation recovery and responsive panels.</p></section>
<section><h2>Privacy</h2><p>Most settings stay in the browser. Financial reporting uses only the saved Discord webhook supplied by the user; exported settings containing it should be treated as private.</p></section></main>
<footer>MissionChief Map Command Toolkit · v7.0.0 candidate · The One We Knew Before</footer></body></html>'''
write("help/index.html", HELP)

GREASY = r'''# MissionChief Map Command Toolkit

## v7.0.0 — The One We Knew Before

A native MissionChief map command and operational-support userscript for Desktop, Tablet/iPad and iOS.

Version 7 removes the copied mission-window requirements, extended call-window, call-list and transport-request engines completely. The Toolkit now concentrates on its own features and avoids competing ownership of MissionChief’s mission-window DOM.

### Retained native systems

- Mission Age map timers and shortcut `6`
- Mission Value
- Patient Transport Sweep using MissionChief’s native Discharge patient control
- Transport Watcher
- Unit Commitment
- Resource Gap
- Major Incident Feed
- Vehicle Code Status
- Custom Vehicle Badges
- Auto-load all vehicles
- Coverage rings and Smart Bookmark Labels
- Alliance Credits and financial intelligence
- Payout presentations and Economy Mode
- Seven complete interface systems
- Desktop, Tablet and iOS Mobile Mode

Most settings stay local to the browser. Financial reports can be sent through the saved Discord webhook configured by the user. Settings exports can contain that webhook and should be treated as private.

Install: https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js
Source and releases: https://github.com/Conroy1988/missionchief-toolkit-assets
'''
write("docs/greasyfork-description.md", GREASY)

HERO = r'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="640" viewBox="0 0 1600 640" role="img" aria-labelledby="title desc"><title id="title">MissionChief Map Command Toolkit native command platform</title><desc id="desc">Native map command, fleet identity, transport support and financial intelligence for MissionChief.</desc><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#020812"/><stop offset=".55" stop-color="#082237"/><stop offset="1" stop-color="#170b19"/></linearGradient><linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#43d8ff"/><stop offset="1" stop-color="#e53b52"/></linearGradient></defs><rect width="1600" height="640" rx="32" fill="url(#bg)"/><rect x="2" y="2" width="1596" height="636" rx="30" fill="none" stroke="#fff" stroke-opacity=".14" stroke-width="4"/><g font-family="Segoe UI,Arial,sans-serif"><text x="80" y="150" fill="#75ddff" font-size="18" font-weight="800" letter-spacing="4">MISSIONCHIEF NATIVE COMMAND</text><text x="76" y="230" fill="#fff" font-size="70" font-weight="900">MAP COMMAND TOOLKIT</text><text x="80" y="292" fill="#ffd178" font-size="30" font-weight="850" letter-spacing="2">THE ONE WE KNEW BEFORE</text><text x="80" y="346" fill="#c6d9e4" font-size="21">Map intelligence · Fleet identity · Native transport · Financial command</text><g transform="translate(80 400)"><rect width="300" height="96" rx="18" fill="#0b3044" stroke="#55d9ff" stroke-opacity=".5"/><text x="24" y="37" fill="#78e3ff" font-size="14" font-weight="850">MISSION COMMAND</text><text x="24" y="68" fill="#fff" font-size="18" font-weight="800">Age · Value · Incidents</text></g><g transform="translate(400 400)"><rect width="300" height="96" rx="18" fill="#162c25" stroke="#62e8ad" stroke-opacity=".45"/><text x="24" y="37" fill="#7cf0bc" font-size="14" font-weight="850">FLEET + TRANSPORT</text><text x="24" y="68" fill="#fff" font-size="18" font-weight="800">Badges · Status · Sweep</text></g><g transform="translate(720 400)"><rect width="300" height="96" rx="18" fill="#2c2512" stroke="#ffd178" stroke-opacity=".45"/><text x="24" y="37" fill="#ffe199" font-size="14" font-weight="850">MAP CONTROL</text><text x="24" y="68" fill="#fff" font-size="18" font-weight="800">Coverage · Places · Focus</text></g><g transform="translate(1040 400)"><rect width="480" height="96" rx="18" fill="#2b151f" stroke="#ff7182" stroke-opacity=".45"/><text x="24" y="37" fill="#ff9fac" font-size="14" font-weight="850">FINANCIAL INTELLIGENCE</text><text x="24" y="68" fill="#fff" font-size="18" font-weight="800">Income · Spendings · Variance · Discord</text></g><text x="800" y="574" text-anchor="middle" fill="#dceaf1" font-size="14" font-weight="800" letter-spacing="2">DESKTOP · TABLET/IPAD · iOS MOBILE · VERIFIED DELIVERY</text></g><rect y="630" width="1600" height="10" fill="url(#edge)"/></svg>'''
write("docs/media/readme-hero.svg", HERO)

V7_CONTRACT = r'''#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
TOKEN = "ls" + "sm"
def main() -> int:
    source = SOURCE.read_text(encoding="utf-8"); lower = source.lower()
    assert re.search(r"(?m)^// @version\s+7\.0\.0$", source)
    assert "version: '7.0.0'" in source
    assert TOKEN not in lower
    forbidden = ["Operational Window Suite", "Enhanced Operational Requirements", "Extended Call Window", "Extended Call List", "Enhanced Transport Requests", "operationalSuite", "operationalFeature", "operationalRequirements", "OPERATIONAL_SETTINGS_SCHEMA", "data-operational-settings-root", "installOperationalSuiteShell", "handleOperationalWindowSettingChange"]
    present = [item for item in forbidden if item in source]; assert not present, present
    assert source.count("operationalWindow") == 1 and "delete merged.operationalWindow;" in source
    assert source.count("missionRequirements") == 1 and "delete merged.missionRequirements;" in source
    retained = ["missionAge: false", "function missionAgeRefreshPlan(", "function updateMissionAgeLabels(", "makeToggleButton('missionAge'", "function missionWindowValueDetails(", "function customVehicleBadgeVehicleId(", "function collectTransportSweepVehicleCandidatesForMission(", "async function openTransportSweepVehicle(", "function transportSweepVisibleDischargeButtons(", "function recordTransportSweepConfirmedRelease(", "function renderTransportSweepHud(", "Vehicle Code Status", "Transport Watcher", "Resource Gap", "Major Incident Feed"]
    missing = [item for item in retained if item not in source]; assert not missing, missing
    assert "missionRequirementsVehicleId(checkbox || row)" not in source
    assert "MissionChief's native Discharge patient control" in source
    tracked=[]
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "release-bundle" in path.parts: continue
        if TOKEN in path.as_posix().lower(): tracked.append(path.as_posix())
        try: text=path.read_text(encoding="utf-8")
        except (UnicodeDecodeError,OSError): continue
        if TOKEN in text.lower(): tracked.append(path.as_posix())
    assert not tracked, sorted(set(tracked))
    print("v7 retirement contract passed.")
    return 0
if __name__ == "__main__": raise SystemExit(main())'''
write(".github/scripts/test_v7_retirement.py", V7_CONTRACT)

MISSION_AGE = r'''#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
required=['missionAge: false',"makeToggleButton('missionAge'",'function formatMissionAge(','function makeMissionAgeIcon(','function missionAgeRefreshPlan(','function updateMissionAgeLabels(','function clearMissionAgeLabels(','if (state.missionAge) scheduleMissionAgeRefresh();','if (!state.missionAge) clearMissionAgeLabels();']
missing=[item for item in required if item not in source];assert not missing,missing
print('Mission Age map timers retained under v7.')'''
write(".github/scripts/test_mission_age_retention.py", MISSION_AGE)

NATIVE_SWEEP = r'''#!/usr/bin/env python3
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8');token='ls'+'sm'
assert token not in source.lower()
required=['function collectTransportSweepVehicleCandidatesForMission(missionId)','async function openTransportSweepVehicle(candidate)','function transportSweepVisibleDischargeButtons()','function findVisibleDischargePatientButton(baseline = null)',"const TRANSPORT_SWEEP_RELEASE_CONFIRMATION_TEXT = 'Understood! We have released the patient.';",'function captureTransportSweepReleaseConfirmationBaseline()','function transportSweepReleaseConfirmationVisible(baseline = null)','function recordTransportSweepConfirmedRelease(releaseKey, message)','confirmedReleaseKeys: new Set()',"async function closeTransportSweepWindows(reason = 'navigation')",'activeWindowRoot: null','ownedWindowLayers: new Set()','function ensureTransportSweepHud()','function renderTransportSweepHud()',"MissionChief's native Discharge patient control"]
missing=[item for item in required if item not in source];assert not missing,missing
processor=re.search(r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',source);assert processor
body=processor.group(1)
for item in ['collectTransportSweepVehicleCandidatesForMission(missionId)','openTransportSweepVehicle(candidate)','button.click()','recordTransportSweepConfirmedRelease(']: assert item in body
assert body.index('button.click()') < body.index('recordTransportSweepConfirmedRelease(')
assert source.count('transportSweepRuntime.cleared += 1')==1
assert source.count('transportSweepRuntime.processed += 1')==1
print('Native Patient Transport Sweep contract passed.')'''
write(".github/scripts/test_transport_sweep_native_contract.py", NATIVE_SWEEP)

replace_file(".github/scripts/test_transport_sweep_runtime.js", "const end = source.indexOf('    async function activateTransportSweepLssmRelease(candidate)', start);", "const end = source.indexOf('    function transportSweepVisibleDischargeButtons()', start);", "native helper end anchor")

SETTINGS_TEST = r'''#!/usr/bin/env python3
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];source=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8');fixtures=json.loads((ROOT/'.github/fixtures/settings-ui-contract.json').read_text(encoding='utf-8'))
def section(start,end): a=source.index(start);b=source.index(end,a);return source[a:b]
panel=section('    function createPanel(', '    function ensureControlAndPanel')
actions=sorted(set(re.findall(r'data-action\s*=\s*["\']([^"\']+)',panel)));settings=sorted(set(re.findall(r'data-setting\s*=\s*["\']([^"\']+)',panel)));tabs=sorted(set(re.findall(r'data-tab\s*=\s*["\']([^"\']+)',panel)))
assert actions==sorted(fixtures['actions']);assert settings==sorted(fixtures['settings']);assert tabs==sorted(fixtures['tabs'])
assert 'delete merged.operationalWindow;' in source and 'delete merged.missionRequirements;' in source
assert 'data-operational-setting' not in source and 'handleOperationalWindowSettingChange' not in source
print('Settings/UI contract passed for v7.')'''
write(".github/scripts/test_settings_ui_contract.py", SETTINGS_TEST)

LAUNCHER_TEST = r'''#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
def section(start,end): a=text.index(start);b=text.index(end,a);return text[a:b]
control=section('    function createControl(','    function createPanel(');assert 'const primaryMap = toolkitPrimaryMapElement(mapEl, document);' in control
ensure=section('    function ensureUi()','    function mutationBelongsToToolkit');assert 'return Boolean(control || document.getElementById(SCRIPT.controlId));' in ensure
boot=section('    function boot()','    function scheduleBoot()');assert 'installMissionMarkerAddHook' in boot and 'installCustomVehicleBadges' in boot and 'installOperationalSuiteShell' not in boot
age=section('    function updateMissionAgeLabels()','    function scheduleMissionAgeRefresh(');assert 'missionAgeRefreshPlan' in age
meta=re.search(r'^//\s*@version\s+([^\s]+)',text,re.M).group(1);runtime=re.search(r"version:\s*'([^']+)'",text).group(1);assert meta==runtime=='7.0.0';assert len(text.splitlines())<=24000
print('v7 launcher, boot and Mission Age contract passed.')'''
write(".github/scripts/test_issue464_launcher_settings_contract.py", LAUNCHER_TEST)

BOOT447 = r'''#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
def section(start,end): a=text.index(start);b=text.index(end,a);return text[a:b]
helper=section('    function runBootIntegration','    function startBootAttemptCoordinator');boot=section('    function boot()','    function scheduleBoot()')
assert 'failed without blocking the Toolkit launcher' in helper;assert "runBootIntegration('custom vehicle badges', installCustomVehicleBadges);" in boot;assert 'installOperationalSuiteShell' not in boot
print('Core menu boot remains fail-open after v7 retirement.')'''
write(".github/scripts/test_issue447_menu_boot_fail_open.py", BOOT447)

BOOT450 = r'''#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
def section(start,end): a=text.index(start);b=text.index(end,a);return text[a:b]
helper=section('    function runBootIntegration','    function startBootAttemptCoordinator');coordinator=section('    function startBootAttemptCoordinator','    function registerBootMaintenanceTasks');boot=section('    function boot()','    function scheduleBoot()')
assert 'failed without blocking the Toolkit launcher' in helper;assert 'runtimeSetTimeout(runBootAttempt, delay);' in coordinator
for integration in ['applyRootAttributes','installMissionMarkerAddHook','installRadioMessageHook','installCreditsUpdateHook','observeCreditValue','installCustomVehicleBadges']: assert integration in boot
assert 'installOperationalSuiteShell' not in boot
print('Core launcher bootstrap contract passed after v7 retirement.')'''
write(".github/scripts/test_issue450_core_launcher_bootstrap.py", BOOT450)

PREBOOT = r'''#!/usr/bin/env python3
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8');state=re.search(r'(?m)^\s*(?:const|let|var)\s+state\s*=\s*loadState\(\);\s*$',text);assert state
assert text.index('    function defaultState() {') < state.start();assert text.index('    function normaliseLoadedState(') < state.start();assert 'OPERATIONAL_SUITE_SETTINGS_VERSION' not in text
meta=re.search(r'(?m)^//\s*@version\s+([^\s]+)\s*$',text).group(1);runtime=re.search(r"version:\s*'([^']+)',",text).group(1);assert meta==runtime=='7.0.0';assert text.rstrip().endswith('})();')
print('v7 preboot state-order contract passed.')'''
write(".github/scripts/test_issue454_preboot_state_order.py", PREBOOT)

def canonical_css_formatting(raw: str) -> str:
    lines=raw.split("\n");removable={i for i in range(1,len(lines)-1) if not lines[i].strip()};return re.sub(r"\n[\t ]*}","}","\n".join(line for i,line in enumerate(lines) if i not in removable))
def extract_main_style(text: str) -> str:
    start=text.index("function installMainStyles()");a=text.index("addStyle(`",start)+len("addStyle(`");metric=text.index("recordStartupMetric('stylesheetInstallMs'",a);b=text.rfind("`);",a,metric);return text[a:b]
source_now=srcp.read_text(encoding="utf-8");style=extract_main_style(source_now)
profile={"issue":512,"version":"7.0.0","sourceBytes":len(source_now.encode()),"sourceLines":len(source_now.splitlines()),"sourceSha256":hashlib.sha256(source_now.encode()).hexdigest(),"templateBytes":len(style.encode()),"templateLines":len(style.split("\n")),"templateSha256":hashlib.sha256(style.encode()).hexdigest(),"canonicalCssSha256":hashlib.sha256(canonical_css_formatting(style).encode()).hexdigest(),"maxSourceBytes":1600000,"minTemplateBytes":500000,"retiredSystems":["requirements-engine","call-window-engine","call-list-engine","transport-request-engine"]}
fixture_path=ROOT/".github/fixtures/main-style-source-headroom.json";fixture=json.loads(fixture_path.read_text(encoding="utf-8"));fixture.pop("v6Candidate",None);fixture["schemaVersion"]=7;fixture["v7Candidate"]=profile;fixture_path.write_text(json.dumps(fixture,indent=2)+"\n",encoding="utf-8")
STYLE_TEST = r'''#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8');p=json.loads((ROOT/'.github/fixtures/main-style-source-headroom.json').read_text(encoding='utf-8'))['v7Candidate']
start=text.index('function installMainStyles()');a=text.index('addStyle(`',start)+len('addStyle(`');metric=text.index("recordStartupMetric('stylesheetInstallMs'",a);b=text.rfind('`);',a,metric);raw=text[a:b]
lines=raw.split('\n');canonical=re.sub(r'\n[\t ]*}','}','\n'.join(line for i,line in enumerate(lines) if not (0<i<len(lines)-1 and not line.strip())))
actual={'sourceBytes':len(text.encode()),'sourceLines':len(text.splitlines()),'sourceSha256':hashlib.sha256(text.encode()).hexdigest(),'templateBytes':len(raw.encode()),'templateLines':len(lines),'templateSha256':hashlib.sha256(raw.encode()).hexdigest(),'canonicalCssSha256':hashlib.sha256(canonical.encode()).hexdigest()}
assert all(actual[k]==p[k] for k in actual),(actual,p);print('Main-style source-headroom contract passed for v7.')'''
write(".github/scripts/test_main_style_source_headroom.py", STYLE_TEST)

DOC_TEST = r'''#!/usr/bin/env python3
import json
from pathlib import Path
import check_documentation_drift as drift_audit
ROOT=Path(__file__).resolve().parents[2]
def main():
 manifest=json.loads((ROOT/'dist/release-manifest.json').read_text());dashboard=json.loads((ROOT/'status/release-dashboard.json').read_text());version=str(manifest['version']);production=str(dashboard['latestRelease']['version']);readme=(ROOT/'README.md').read_text();help_text=(ROOT/'help/index.html').read_text();greasy=(ROOT/'docs/greasyfork-description.md').read_text();hero=(ROOT/'docs/media/readme-hero.svg').read_text();site=json.loads((ROOT/'docs/site-data.json').read_text())
 assert f'Current verified release: `v{production}` · Development candidate: `v{version}`' in readme
 assert all('The One We Knew Before' in text for text in [readme,help_text,greasy])
 forbidden=['Operational Window Suite','Enhanced Operational Requirements','Extended Call Window','Extended Call List','Enhanced Transport Requests']
 assert not any(item in text for item in forbidden for text in [readme,help_text,greasy,hero])
 names=[f['name'] for c in site['featureCategories'] for f in c.get('features',[])];assert all(item in names for item in ['Mission Age map timers','Mission Value','Patient Transport Sweep','Resource Gap','Vehicle Code Status','Alliance Credits','Financial intelligence','Economy Mode','Desktop, Tablet and iOS Mobile Mode'])
 report=drift_audit.audit(ROOT,allow_release_candidate=True);assert report['status']=='passed',report['failures'];print('Documentation consistency passed for v7.')
if __name__=='__main__': raise SystemExit(main())'''
write(".github/scripts/test_documentation_consistency.py", DOC_TEST)

validate_path=ROOT/".github/scripts/validate_userscript.py";validate=validate_path.read_text(encoding="utf-8");constant_start=validate.index("ISSUE391_MATRIX_RETIREMENT_CONTRACT");constant_end=validate.index("\n\nREQUIRED_KEYS",constant_start)
constants='''V7_RETIREMENT_CONTRACT = ROOT / ".github" / "scripts" / "test_v7_retirement.py"
MISSION_AGE_RETENTION_CONTRACT = ROOT / ".github" / "scripts" / "test_mission_age_retention.py"
NATIVE_TRANSPORT_SWEEP_CONTRACT = ROOT / ".github" / "scripts" / "test_transport_sweep_native_contract.py"
ISSUE447_MENU_BOOT_CONTRACT = ROOT / ".github" / "scripts" / "test_issue447_menu_boot_fail_open.py"
ISSUE450_CORE_BOOTSTRAP_CONTRACT = ROOT / ".github" / "scripts" / "test_issue450_core_launcher_bootstrap.py"
ISSUE454_PREBOOT_STATE_CONTRACT = ROOT / ".github" / "scripts" / "test_issue454_preboot_state_order.py"
ISSUE464_LAUNCHER_SETTINGS_CONTRACT = ROOT / ".github" / "scripts" / "test_issue464_launcher_settings_contract.py"'''
validate=validate[:constant_start]+constants+validate[constant_end:];run_start=validate.index("def run_integrity_gate() -> None:");run_end=validate.index("\n\ndef main() -> int:",run_start)
new_gate=r'''def run_integrity_gate() -> None:
    required=[INTEGRITY_AUDITOR,INTEGRITY_POLICY,ASSET_AUDITOR,AUDIO_ALIAS_AUDITOR,VERSION_STATUS_CONTRACT,FINANCIAL_OVERVIEW_CONTRACT,MAIN_STYLE_HEADROOM_CONTRACT,V7_RETIREMENT_CONTRACT,MISSION_AGE_RETENTION_CONTRACT,NATIVE_TRANSPORT_SWEEP_CONTRACT,ISSUE447_MENU_BOOT_CONTRACT,ISSUE450_CORE_BOOTSTRAP_CONTRACT,ISSUE454_PREBOOT_STATE_CONTRACT,ISSUE464_LAUNCHER_SETTINGS_CONTRACT]
    missing=[path.relative_to(ROOT) for path in required if not path.exists()]
    if missing: fail("integrity tooling is incomplete: "+", ".join(map(str,missing)))
    with tempfile.TemporaryDirectory(prefix="mcms-integrity-") as temp:
        baseline_path=Path(temp)/"release-baseline.user.js";baseline_ref=latest_release_baseline(baseline_path);integrity_json=Path(temp)/"code-integrity-report.json";integrity_md=Path(temp)/"code-integrity-report.md";asset_json=Path(temp)/"asset-health-report.json";asset_md=Path(temp)/"asset-health-report.md"
        command=[sys.executable,str(INTEGRITY_AUDITOR),"--candidate",str(SOURCE),"--policy",str(INTEGRITY_POLICY),"--json-output",str(integrity_json),"--markdown-output",str(integrity_md)]
        if baseline_ref and baseline_path.exists(): command.extend(["--base",str(baseline_path)])
        if subprocess.run(command,cwd=ROOT).returncode!=0: fail("expanded code-integrity audit failed")
        if subprocess.run([sys.executable,str(ASSET_AUDITOR),"--mode","static","--json-output",str(asset_json),"--markdown-output",str(asset_md)],cwd=ROOT).returncode!=0: fail("static public-asset integrity audit failed")
        for contract in [AUDIO_ALIAS_AUDITOR,VERSION_STATUS_CONTRACT,FINANCIAL_OVERVIEW_CONTRACT,MAIN_STYLE_HEADROOM_CONTRACT,V7_RETIREMENT_CONTRACT,MISSION_AGE_RETENTION_CONTRACT,NATIVE_TRANSPORT_SWEEP_CONTRACT,ISSUE447_MENU_BOOT_CONTRACT,ISSUE450_CORE_BOOTSTRAP_CONTRACT,ISSUE454_PREBOOT_STATE_CONTRACT,ISSUE464_LAUNCHER_SETTINGS_CONTRACT]:
            if subprocess.run([sys.executable,str(contract)],cwd=ROOT).returncode!=0: fail(f"contract failed: {contract.relative_to(ROOT)}")
        report=json.loads(integrity_json.read_text());metrics=report.get("metrics",{});print(f"Code integrity passed: {metrics.get('staticSelectors',0)} selectors.")'''
validate=validate[:run_start]+new_gate+validate[run_end:];validate_path.write_text(validate,encoding="utf-8")

PREFLIGHT='''#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
MODE="${1:---all}"; SOURCE="src/MissionChief_Map_Command_Toolkit.user.js"; DIST_JS="dist/MissionChief_Map_Command_Toolkit.user.js"; DIST_TXT="dist/MissionChief_Map_Command_Toolkit.txt"
if [[ "$MODE" == "--all" ]]; then python3 .github/scripts/validate_userscript.py; fi
node --check "$SOURCE"; cmp --silent "$DIST_JS" "$DIST_TXT"
for contract in .github/scripts/test_financial_ledger_contract.py .github/scripts/test_financial_overview_contract.py .github/scripts/test_financial_discord_image_layout_contract.py .github/scripts/test_mission_marker_ingestion_contract.py .github/scripts/test_boot_lifecycle_contract.py .github/scripts/test_settings_ui_contract.py .github/scripts/test_root_attribute_write_suppression_contract.py .github/scripts/test_ios_safari_usability_contract.py .github/scripts/test_main_style_source_headroom.py .github/scripts/test_desktop_panel_layout_contract.py .github/scripts/test_section_navigation_contract.py .github/scripts/test_mission_value_contract.py .github/scripts/test_v7_retirement.py .github/scripts/test_mission_age_retention.py .github/scripts/test_transport_sweep_native_contract.py; do PYTHONDONTWRITEBYTECODE=1 python3 "$contract"; done
node .github/scripts/test_transport_sweep_runtime.js
echo "[preflight] Complete"'''
write(".github/scripts/run_userscript_preflight.sh",PREFLIGHT)

full_audit_path=ROOT/".github/workflows/full-userscript-audit.yml";full_audit=full_audit_path.read_text()
for stale in ['      - ".github/fixtures/transport-sweep-lssm-contract.json"\n','      - ".github/scripts/test_issue391_matrix_retirement.py"\n','      - ".github/scripts/test_transport_sweep_lssm_contract.py"\n']: full_audit=full_audit.replace(stale,'')
anchor='      - ".github/scripts/test_transport_sweep_runtime.js"\n'
if '.github/scripts/test_v7_retirement.py' not in full_audit: full_audit=full_audit.replace(anchor,anchor+'      - ".github/scripts/test_v7_retirement.py"\n      - ".github/scripts/test_mission_age_retention.py"\n      - ".github/scripts/test_transport_sweep_native_contract.py"\n')
full_audit_path.write_text(full_audit)

V7_WORKFLOW='''name: Validate v7 Native Toolkit Boundary
on:
  pull_request:
    paths:
      - "src/MissionChief_Map_Command_Toolkit.user.js"
      - ".github/scripts/test_v7_retirement.py"
      - ".github/scripts/test_mission_age_retention.py"
      - ".github/scripts/test_transport_sweep_native_contract.py"
      - ".github/workflows/v7-native-toolkit-boundary.yml"
  workflow_dispatch:
permissions:
  contents: read
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
        with:
          persist-credentials: false
      - run: python3 .github/scripts/test_v7_retirement.py
      - run: python3 .github/scripts/test_mission_age_retention.py
      - run: python3 .github/scripts/test_transport_sweep_native_contract.py
      - run: node --check src/MissionChief_Map_Command_Toolkit.user.js
      - run: cmp --silent dist/MissionChief_Map_Command_Toolkit.user.js dist/MissionChief_Map_Command_Toolkit.txt'''
write(".github/workflows/v7-native-toolkit-boundary.yml",V7_WORKFLOW)

for obsolete in [".github/scripts/test_issue378_requirements_renderer.py",".github/scripts/test_issue378_operational_feature_suite.py",".github/scripts/test_issue378_operational_feature_runtime.js",".github/scripts/test_issue391_matrix_retirement.py",".github/scripts/test_issue456_requirements_truth_runtime.js",".github/scripts/test_issue458_requirements_source_runtime.js",".github/scripts/test_issue464_operational_runtime.js",".github/scripts/test_issue470_menu_requirements_runtime.js",".github/scripts/test_transport_sweep_lssm_contract.py",".github/fixtures/transport-sweep-lssm-contract.json",".github/scripts/test_v6_operational_runtime_budget.py",".github/scripts/test_v6_operational_settings_contract.py",".github/scripts/test_v6_feature_retirement.py",".github/scripts/test_v6_mission_age_retention.py",".github/workflows/v6-critical-performance.yml",".github/fixtures/v6-performance-budget.json","docs/audits/v6-critical-performance-baseline.md","docs/audits/v6-critical-performance-evidence.json",".github/scripts/diagnose_issue512_lssm_coexistence.py",".github/workflows/issue512-lssm-coexistence-diagnostic.yml",".github/v7-retirement/apply_v7_retirement.py",".github/workflows/apply-v7-retirement.yml"]: delete(obsolete)

doc_extensions={".md",".html",".svg",".json",".txt",".css"};code_extensions={".py",".js",".sh",".yml",".yaml",".toml",".ini"}
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or "release-bundle" in path.parts: continue
    try: text=path.read_text(encoding="utf-8")
    except (UnicodeDecodeError,OSError): continue
    if extension_token not in text.lower(): continue
    if path.suffix.lower() in doc_extensions: path.write_text(re.sub(extension_token,"external extension",text,flags=re.I),encoding="utf-8")
    elif path.suffix.lower() in code_extensions: raise SystemExit(f"retired extension code reference remains: {path.relative_to(ROOT)}")

subprocess.run([sys.executable,str(ROOT/'.github/scripts/check_documentation_drift.py'),'--allow-release-candidate'],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(ROOT/'.github/scripts/validate_userscript.py')],cwd=ROOT,check=True)
subprocess.run(['node','--check',str(srcp)],cwd=ROOT,check=True)
subprocess.run(['bash',str(ROOT/'.github/scripts/run_userscript_preflight.sh'),'--contracts'],cwd=ROOT,check=True)
print(json.dumps({'version':'7.0.0','sourceSha256':hashlib.sha256(srcp.read_bytes()).hexdigest(),'sourceBytes':srcp.stat().st_size,'sourceLines':len(srcp.read_text().splitlines())},indent=2))
