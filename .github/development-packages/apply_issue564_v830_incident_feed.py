#!/usr/bin/env python3
"""Issue #564 / Toolkit v8.3.0: exclude personally attended missions from Incident Command Wire."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
EXPECTED_SOURCE_SHA = "f686888356d3a8498782a1e656c855db7ce445f38a11a4c68909b0163e5adc38"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace_once(value: str, old: str, new: str, label: str) -> str:
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return value.replace(old, new, 1)


source = SOURCE_PATH.read_text(encoding="utf-8")
if hashlib.sha256(source.encode()).hexdigest() != EXPECTED_SOURCE_SHA:
    raise RuntimeError("Released v8.2.7 source authority moved")

source = replace_once(source, "// @version      8.2.7", "// @version      8.3.0", "metadata version")
source = replace_once(source, "version: '8.2.7'", "version: '8.3.0'", "runtime version")

entry_anchor = """    function majorIncidentFeedEntries(now = Date.now()) {
"""
entry_helpers = """    function majorIncidentFeedMissionAttended(snapshot) {
        return Math.max(0, Number(snapshot?.units?.onScene) || 0) > 0;
    }

    function majorIncidentFeedResolvedIndex(feed, count = majorIncidentFeedEntryCount(feed)) {
        const total = Math.max(0, Number(count) || 0);
        if (total <= 0) return 0;
        const animation = majorIncidentFeedAnimation(feed);
        const duration = Number(animation?.effect?.getTiming?.().duration) || 0;
        if (duration > 0) {
            const currentTime = ((Number(animation?.currentTime) || 0) % duration + duration) % duration;
            return Math.min(total - 1, Math.floor(currentTime / (duration / total)));
        }
        return ((Number(majorIncidentFeedCurrentIndex) || 0) % total + total) % total;
    }

    function majorIncidentFeedCurrentMissionId(feed, index = majorIncidentFeedResolvedIndex(feed)) {
        const items = Array.from(feed?.querySelectorAll?.(
            '.mcms-incident-feed-group[data-mcms-reel-copy="primary"] [data-mcms-major-mission-id]'
        ) || []);
        if (!items.length) return '';
        const normalised = ((Number(index) || 0) % items.length + items.length) % items.length;
        return String(items[normalised]?.dataset?.mcmsMajorMissionId || '');
    }

    function majorIncidentFeedRetainedIndex(entries, previousMissionId, previousIndex = 0) {
        const list = Array.isArray(entries) ? entries : [];
        if (!list.length) return 0;
        const missionId = String(previousMissionId || '');
        if (missionId) {
            const retained = list.findIndex(entry => String(entry?.snapshot?.missionId ?? '') === missionId);
            if (retained >= 0) return retained;
        }
        return ((Number(previousIndex) || 0) % list.length + list.length) % list.length;
    }

""" + entry_anchor
source = replace_once(source, entry_anchor, entry_helpers, "Incident Feed attended/index helpers")

source = replace_once(
    source,
    """        if (snapshot.source === 'personal' && !state.visibility.myMissions) continue;
        if (snapshot.source === 'alliance' && !state.visibility.allianceMissions) continue;

        const credits = Number(snapshot.averageCredits);
""",
    """        if (snapshot.source === 'personal' && !state.visibility.myMissions) continue;
        if (snapshot.source === 'alliance' && !state.visibility.allianceMissions) continue;
        if (majorIncidentFeedMissionAttended(snapshot)) continue;

        const credits = Number(snapshot.averageCredits);
""",
    "Incident Feed eligibility extension",
)

source = replace_once(
    source,
    """        if (forceRestart) {
            track.style.setProperty('animation', 'none', 'important');
            void track.offsetWidth;
            track.style.removeProperty('animation');
            majorIncidentFeedCurrentIndex = 0;
        }
        majorIncidentFeedSyncControls(feed);
        majorIncidentFeedSyncReelState(feed);
""",
    """        if (forceRestart) {
            track.style.setProperty('animation', 'none', 'important');
            void track.offsetWidth;
            track.style.removeProperty('animation');
        }
        if (count > 0) majorIncidentFeedApplyIndex(feed, majorIncidentFeedCurrentIndex);
        else majorIncidentFeedSyncControls(feed);
        majorIncidentFeedSyncReelState(feed);
""",
    "Incident Feed motion index preservation",
)

source = replace_once(
    source,
    """        const feed = ensureMajorIncidentFeed();
        if (!feed) return;
        const entries = state.economyMode ? majorIncidentFeedEntries().slice(0, 1) : majorIncidentFeedEntries();
""",
    """        const feed = ensureMajorIncidentFeed();
        if (!feed) return;
        const previousCount = majorIncidentFeedEntryCount(feed);
        const previousIndex = majorIncidentFeedResolvedIndex(feed, previousCount);
        const previousMissionId = majorIncidentFeedCurrentMissionId(feed, previousIndex);
        const entries = state.economyMode ? majorIncidentFeedEntries().slice(0, 1) : majorIncidentFeedEntries();
""",
    "Incident Feed current mission capture",
)

source = replace_once(
    source,
    """            track.replaceChildren(document.createRange().createContextualFragment(`<div class="mcms-incident-feed-group" data-mcms-reel-copy="primary">${primary}</div><div class="mcms-incident-feed-group" data-mcms-reel-copy="duplicate" aria-hidden="true">${duplicate}</div>`));
            list.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'list', false)).join('')));
            majorIncidentFeedCurrentIndex = 0;
            majorIncidentFeedSyncControls(feed);
            scheduleMajorIncidentFeedMotion(feed, true, 70);
""",
    """            track.replaceChildren(document.createRange().createContextualFragment(`<div class="mcms-incident-feed-group" data-mcms-reel-copy="primary">${primary}</div><div class="mcms-incident-feed-group" data-mcms-reel-copy="duplicate" aria-hidden="true">${duplicate}</div>`));
            list.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'list', false)).join('')));
            majorIncidentFeedCurrentIndex = majorIncidentFeedRetainedIndex(entries, previousMissionId, previousIndex);
            majorIncidentFeedSyncControls(feed);
            scheduleMajorIncidentFeedMotion(feed, true, 70);
""",
    "Incident Feed retained/next index",
)

source = replace_once(
    source,
    "No qualifying major incidents currently active",
    "No unattended qualifying major incidents currently active",
    "Incident Feed wire empty state",
)
source = replace_once(
    source,
    "No major incidents currently meet the configured threshold.",
    "No unattended major incidents currently meet the configured threshold.",
    "Incident Feed queue empty state",
)

source = replace_once(
    source,
    """                if (state.unitCommitment) scheduleUnitCommitmentRefresh(280);
                scheduleMissionSnapshotRefresh(650);
                if (state.resourceGap.enabled) scheduleResourceGapRefresh(520);
""",
    """                if (state.unitCommitment) scheduleUnitCommitmentRefresh(280);
                scheduleMissionSnapshotRefresh(state.majorIncidentFeed.enabled ? 90 : 650);
                if (state.resourceGap.enabled) scheduleResourceGapRefresh(520);
""",
    "Incident Feed API refresh latency",
)
source = replace_once(
    source,
    """        if (state.unitCommitment) scheduleUnitCommitmentRefresh(500);
        scheduleMissionSnapshotRefresh(850);
        if (state.resourceGap.enabled) scheduleResourceGapRefresh(900);
""",
    """        if (state.unitCommitment) scheduleUnitCommitmentRefresh(500);
        scheduleMissionSnapshotRefresh(state.majorIncidentFeed.enabled ? 90 : 850);
        if (state.resourceGap.enabled) scheduleResourceGapRefresh(900);
""",
    "Incident Feed radio refresh latency",
)

for marker in [
    "function majorIncidentFeedMissionAttended(snapshot)",
    "if (majorIncidentFeedMissionAttended(snapshot)) continue;",
    "function majorIncidentFeedResolvedIndex(feed",
    "function majorIncidentFeedCurrentMissionId(feed",
    "function majorIncidentFeedRetainedIndex(entries",
    "majorIncidentFeedCurrentIndex = majorIncidentFeedRetainedIndex(entries, previousMissionId, previousIndex);",
    "scheduleMissionSnapshotRefresh(state.majorIncidentFeed.enabled ? 90 : 850);",
]:
    if marker not in source:
        raise RuntimeError(f"Missing Issue #564 source marker: {marker}")
write("src/MissionChief_Map_Command_Toolkit.user.js", source)

static_contract = r"""#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js'
def section(text,start,end):
    left=text.index(start);right=text.index(end,left);return text[left:right]
def main():
    source=SOURCE.read_text(encoding='utf-8')
    metadata=re.search(r'(?m)^//\s*@version\s+([^\s]+)$',source);runtime=re.search(r"version:\s*'([^']+)'",source)
    assert metadata and runtime and metadata.group(1)==runtime.group(1)=='8.3.0'
    for name in ['majorIncidentFeedMissionAttended','majorIncidentFeedResolvedIndex','majorIncidentFeedCurrentMissionId','majorIncidentFeedRetainedIndex']:
        assert source.count(f'function {name}(')==1,name
    entries=section(source,'    function majorIncidentFeedEntries(','    function findLocationSearchInput(')
    assert entries.index('if (majorIncidentFeedMissionAttended(snapshot)) continue;') < entries.index('const credits = Number(snapshot.averageCredits);')
    attended=section(source,'    function majorIncidentFeedMissionAttended(','    function majorIncidentFeedResolvedIndex(')
    assert 'snapshot?.units?.onScene' in attended
    assert 'snapshot?.vehicleState' not in attended and 'snapshot?.source' not in attended
    render=section(source,'    function renderMajorIncidentFeed(','    function scheduleMajorIncidentFeedRender(')
    for marker in ['const previousIndex = majorIncidentFeedResolvedIndex(feed, previousCount);','const previousMissionId = majorIncidentFeedCurrentMissionId(feed, previousIndex);','majorIncidentFeedCurrentIndex = majorIncidentFeedRetainedIndex(entries, previousMissionId, previousIndex);']:
        assert marker in render,marker
    assert 'majorIncidentFeedManualPaused =' not in render
    assert 'majorIncidentFeedExpanded =' not in render
    assert 'No unattended qualifying major incidents currently active' in render
    motion=section(source,'    function refreshMajorIncidentFeedMotion(','    function scheduleMajorIncidentFeedMotion(')
    assert 'majorIncidentFeedCurrentIndex = 0;' not in motion
    assert 'majorIncidentFeedApplyIndex(feed, majorIncidentFeedCurrentIndex)' in motion
    radio=section(source,'    function captureRadioVehicleMessage(','    function installRadioMessageHook(')
    assert 'scheduleMissionSnapshotRefresh(state.majorIncidentFeed.enabled ? 90 : 850);' in radio
    print('Issue #564 Incident Feed attended-exclusion static contract passed.')
    return 0
if __name__=='__main__':raise SystemExit(main())
"""
write(".github/scripts/test_issue564_incident_feed_attended.py", static_contract)

runtime_contract = r"""#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const marker=`    function ${name}(`;const start=source.indexOf(marker);assert.ok(start>=0,`${name} missing`);const open=source.indexOf('{',start);let depth=0,quote='',escaped=false;for(let i=open;i<source.length;i++){const c=source[i];if(quote){if(escaped)escaped=false;else if(c==='\\')escaped=true;else if(c===quote)quote='';continue;}if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;if(c==='}'&&--depth===0)return source.slice(start,i+1);}throw new Error(`Could not extract ${name}`);}
const functions=['majorIncidentFeedMissionAttended','majorIncidentFeedRetainedIndex','majorIncidentFeedEntries'];
const now=Date.parse('2026-07-29T12:00:00Z');
const make=(missionId,sourceName='alliance',units={onScene:0,travelling:0})=>({missionId,caption:`Mission ${missionId}`,source:sourceName,lat:55.95,lng:-3.19,averageCredits:30000,createdAt:now-60000,patientsCount:0,possiblePatientsCount:0,prisonersCount:0,possiblePrisonersCount:0,missingText:'',postcode:'EH1 1AA',address:'Edinburgh EH1 1AA',units});
const sandbox={console,Date,Math,Number,String,Array,Map,
 state:{majorIncidentFeed:{minimumCredits:25000},visibility:{myMissions:true,allianceMissions:true}},
 liveMissionSnapshots:new Map(),missionStuckRecord:()=>null,MAJOR_INCIDENT_MASS_CASUALTY_PATIENTS:10,MAJOR_INCIDENT_MASS_CASUALTY_PRISONERS:10,
 majorIncidentOperationalState:snapshot=>snapshot.units?.travelling?{key:'responding',label:'1 RESPONDING'}:{key:'major',label:'AWAITING RESPONSE'},
 normaliseMissionPostcode:()=>'',MAJOR_INCIDENT_FEED_MAX_ITEMS:20};
vm.createContext(sandbox);vm.runInContext(`${functions.map(extractFunction).join('\n\n')}\nthis.api={${functions.join(',')}};`,sandbox);const api=sandbox.api;
assert.equal(api.majorIncidentFeedMissionAttended(make(1,'alliance',{onScene:0,travelling:1})),false,'responding must remain');
assert.equal(api.majorIncidentFeedMissionAttended(make(1,'alliance',{onScene:1,travelling:0})),true,'personal FMS 4 must suppress');
const waiting=make(1);const responding=make(2,'alliance',{onScene:0,travelling:1});const attended=make(3,'alliance',{onScene:1,travelling:0});const allianceOnly=make(4);allianceOnly.allianceOnScene=8;
sandbox.liveMissionSnapshots=new Map([[1,waiting],[2,responding],[3,attended],[4,allianceOnly]]);
let entries=api.majorIncidentFeedEntries(now);
assert.deepEqual(Array.from(entries,e=>e.snapshot.missionId),[1,2,4],'only personal on-scene attendance suppresses');
attended.units={onScene:0,travelling:0};sandbox.liveMissionSnapshots.set(3,attended);
entries=api.majorIncidentFeedEntries(now);
assert.deepEqual(Array.from(entries,e=>e.snapshot.missionId),[1,2,3,4],'last personal on-scene unit leaving allows one re-entry');
const list=entries.map(entry=>({snapshot:{missionId:entry.snapshot.missionId}}));
assert.equal(api.majorIncidentFeedRetainedIndex(list,'2',1),1,'retained mission follows its new index');
const withoutTwo=list.filter(entry=>entry.snapshot.missionId!==2);
assert.equal(api.majorIncidentFeedRetainedIndex(withoutTwo,'2',1),1,'removed current mission advances to next item');
assert.equal(withoutTwo[1].snapshot.missionId,3);
const withoutLast=list.filter(entry=>entry.snapshot.missionId!==4);
assert.equal(api.majorIncidentFeedRetainedIndex(withoutLast,'4',3),0,'removed final item wraps to first');
assert.equal(api.majorIncidentFeedRetainedIndex([], '1', 4),0);
console.log('Issue #564 runtime passed: personal on-scene exclusion, alliance/responding safety, re-entry and stable next-index behaviour.');
"""
write(".github/scripts/test_issue564_incident_feed_attended_runtime.js", runtime_contract)

preflight = read(".github/scripts/run_userscript_preflight.sh")
preflight = replace_once(
    preflight,
    ".github/scripts/test_issue517_incident_command_wire.py .github/scripts/test_v7_retirement.py",
    ".github/scripts/test_issue517_incident_command_wire.py .github/scripts/test_issue564_incident_feed_attended.py .github/scripts/test_v7_retirement.py",
    "Issue #564 static preflight registration",
)
preflight = replace_once(
    preflight,
    "node .github/scripts/test_issue517_incident_command_wire_runtime.js\n",
    "node .github/scripts/test_issue517_incident_command_wire_runtime.js\nnode .github/scripts/test_issue564_incident_feed_attended_runtime.js\n",
    "Issue #564 runtime preflight registration",
)
write(".github/scripts/run_userscript_preflight.sh", preflight)

wire_workflow = read(".github/workflows/v7-incident-command-wire.yml")
wire_workflow = replace_once(
    wire_workflow,
    "      - run: python3 .github/scripts/test_issue517_incident_command_wire.py\n      - run: node .github/scripts/test_issue517_incident_command_wire_runtime.js\n",
    "      - run: python3 .github/scripts/test_issue517_incident_command_wire.py\n      - run: python3 .github/scripts/test_issue564_incident_feed_attended.py\n      - run: node .github/scripts/test_issue517_incident_command_wire_runtime.js\n      - run: node .github/scripts/test_issue564_incident_feed_attended_runtime.js\n",
    "Incident Command Wire workflow coverage",
)
write(".github/workflows/v7-incident-command-wire.yml", wire_workflow)

performance = json.loads(read(".github/performance-budget.json"))
performance["revision"] = "2026-07-29-issue-564-incident-feed-personal-on-scene"
performance["rationale"] = "Exclude missions from Incident Command Wire using the existing personal mission commitment index and coalesced snapshot refresh path."
performance["transitionApproval"] = {
    "issue": 564,
    "version": "8.3.0",
    "approvedNetworkRequestDelta": 0,
    "scope": "Mission-scoped personal FMS 4 exclusion, stable current-card advancement and dynamic re-entry.",
    "approvedMutationObserverDelta": 0,
}
if not any(item.get("version") == "8.3.0" for item in performance.setdefault("approvalHistory", [])):
    performance["approvalHistory"].append(dict(performance["transitionApproval"]))
write(".github/performance-budget.json", json.dumps(performance, indent=2) + "\n")

changelog = read("CHANGELOG.md")
entry = """## [8.3.0] - 2026-07-29

### Incident Command Wire — hide missions already attended by you

- Qualifying missions now leave the compact wire and expanded queue as soon as one of the signed-in player's own vehicles reaches MissionChief's authoritative FMS 4 on-scene state.
- Selected and responding vehicles remain visible; alliance-member attendance alone does not suppress a mission.
- A mission may re-enter once the last personal on-scene vehicle leaves and it still satisfies the normal major-incident rules.
- Removing the currently displayed incident advances to the next valid card, preserves Pause/Play and expanded state, keeps the counter synchronized and wraps safely at the end of the queue.
- Reuses the existing personal vehicle commitment index, radio-message hook, mission snapshot cache and coalesced refresh timer.
- Adds no network request, observer, interval, broad DOM scan or Toolkit-managed timer.

"""
if "## [8.3.0] - 2026-07-29" not in changelog:
    changelog = replace_once(changelog, "# Changelog\n\n", "# Changelog\n\n" + entry, "changelog insertion")
write("CHANGELOG.md", changelog)

write(
    "docs/issue-564-incident-feed-attended-exclusion.md",
    """# Issue #564 — unattended Incident Command Wire

Toolkit v8.3.0 keeps the Incident Command Wire focused on major missions that still need the signed-in player's initial attendance.

A mission is excluded only when the existing personal vehicle commitment index confirms at least one of the player's own units at MissionChief FMS 4 for that mission. Selected units, FMS 3 responding units and alliance-member units do not trigger exclusion.

The normal feed predicate, score ordering and maximum-item bound remain authoritative. When the final personal on-scene unit leaves, the mission can re-enter once if it still qualifies. Current-card removal retains Pause/Play and expanded state, advances at the same queue index, wraps safely and updates the compact reel, counter and expanded queue together.

The implementation reuses existing vehicle radio events, API reconciliation, mission snapshot invalidation and the single coalesced snapshot timer. It introduces no request, observer, interval, broad scan or additional Toolkit-managed timer.
""",
)

manifest = json.loads(read("help/manifest.json"))
manifest.update(
    guideVersion="8.3.0",
    toolkitVersion="8.3.0",
    updated="2026-07-29",
    runtimeGuidePatch="Toolkit v8.3.0 removes personally attended FMS 4 missions from Incident Command Wire and permits deterministic re-entry after the final personal on-scene unit leaves.",
)
write("help/manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

help_html = read("help/index.html")
help_html = help_html.replace("v8.2.7", "v8.3.0")
help_html = replace_once(
    help_html,
    "<div class=\"card\"><h3>Incident Command Wire</h3><p>Shows one complete priority incident at a time with previous, pause, next and expanded-queue controls.</p></div>",
    "<div class=\"card\"><h3>Incident Command Wire</h3><p>Shows priority incidents that still need your attendance. A mission leaves when one of your own units reaches FMS 4 and can re-enter after your final on-scene unit leaves.</p></div>",
    "Incident Command Wire help card",
)
help_html = help_html.replace(
    "</main>",
    "<section id=\"incident-wire-unattended\"><h2>Incident Command Wire — unattended missions</h2><p>The wire excludes a qualifying mission only after one of your own vehicles reaches MissionChief’s FMS 4 on-scene state. Selection and FMS 3 responding do not remove it, alliance-only attendance is ignored, and the mission can re-enter when your final on-scene unit leaves. The current card advances safely while Pause/Play, the counter and expanded queue remain synchronized.</p></section>\n</main>",
    1,
)
write("help/index.html", help_html)

site_data = json.loads(read("docs/site-data.json"))
found = False
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Incident Command Wire":
            feature["summary"] = "Presents priority-ordered major incidents that still require the signed-in player's initial attendance."
            feature["details"] = [
                "Personal FMS 4 on-scene exclusion",
                "Responding and alliance-only attendance remain visible",
                "Dynamic re-entry after the final personal on-scene unit leaves",
                "Stable current-card advancement and synchronized queue",
                "Pause/Play and expanded-state preservation",
                "No additional polling or observer",
            ]
            found = True
if not found:
    raise RuntimeError("Incident Command Wire site-data entry missing")
write("docs/site-data.json", json.dumps(site_data, indent=2, ensure_ascii=False) + "\n")

headroom = json.loads(read(".github/fixtures/main-style-source-headroom.json"))
text = read("src/MissionChief_Map_Command_Toolkit.user.js")
style_start = text.index("function installMainStyles()")
template_start = text.index("addStyle(`", style_start) + len("addStyle(`")
metric = text.index("recordStartupMetric('stylesheetInstallMs'", template_start)
template_end = text.rfind("`);", template_start, metric)
css = text[template_start:template_end]
css_lines = css.split("\n")
canonical = re.sub(
    r"\n[\t ]*}",
    "}",
    "\n".join(line for index, line in enumerate(css_lines) if not (0 < index < len(css_lines) - 1 and not line.strip())),
)
candidate = headroom["v8Candidate"]
previous_bytes = int(candidate["sourceBytes"])
previous_lines = int(candidate["sourceLines"])
previous_growth_bytes = int(candidate["approvedGrowth"]["sourceBytes"])
previous_growth_lines = int(candidate["approvedGrowth"]["sourceLines"])
source_bytes = len(text.encode())
source_lines = len(text.splitlines())
candidate.update(
    issue=564,
    version="8.3.0",
    sourceBytes=source_bytes,
    sourceLines=source_lines,
    sourceSha256=hashlib.sha256(text.encode()).hexdigest(),
    templateBytes=len(css.encode()),
    templateLines=len(css_lines),
    templateSha256=hashlib.sha256(css.encode()).hexdigest(),
    canonicalCssSha256=hashlib.sha256(canonical.encode()).hexdigest(),
    maxSourceBytes=source_bytes + 20000,
    maxSourceLines=source_lines + 250,
    baseline="8.2.7",
    scope="Issue #564 personal FMS 4 attended-mission exclusion and stable Incident Command Wire re-entry/index lifecycle",
)
candidate["approvedGrowth"] = {
    "sourceBytes": previous_growth_bytes + source_bytes - previous_bytes,
    "sourceLines": previous_growth_lines + source_lines - previous_lines,
    "templateBytes": 0,
    "templateLines": 0,
}
write(".github/fixtures/main-style-source-headroom.json", json.dumps(headroom, indent=2) + "\n")

print(json.dumps({
    "version": "8.3.0",
    "issue": 564,
    "sourceBytes": source_bytes,
    "sourceLines": source_lines,
    "sourceSha256": candidate["sourceSha256"],
    "newRequests": 0,
    "newObservers": 0,
    "newIntervals": 0,
    "newTimers": 0,
}, indent=2))
