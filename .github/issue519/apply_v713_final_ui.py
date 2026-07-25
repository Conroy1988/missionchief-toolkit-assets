#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
STATIC = ROOT / ".github" / "scripts" / "test_issue517_incident_command_wire.py"
RUNTIME = ROOT / ".github" / "scripts" / "test_issue517_incident_command_wire_runtime.js"
FIXTURE = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help" / "index.html"
SELF = ROOT / ".github" / "issue519" / "apply_v713_final_ui.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue519-v713-final-ui.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


def append_css_properties(source: str, selector_fragment: str, properties: str, label: str) -> str:
    pattern = re.compile(rf"({re.escape(selector_fragment)}\{{)([^}}]*)(\}})")
    source, count = pattern.subn(lambda match: f"{match.group(1)}{match.group(2)}{properties}{match.group(3)}", source, count=1)
    if count != 1:
        raise SystemExit(f"Expected one {label} CSS block, found {count}")
    return source


def update_headroom(source: str) -> None:
    start = source.index("function installMainStyles()")
    template_start = source.index("addStyle(`", start) + len("addStyle(`")
    metric = source.index("recordStartupMetric('stylesheetInstallMs'", template_start)
    template_end = source.rfind("`);", template_start, metric)
    raw = source[template_start:template_end]
    lines = raw.split("\n")
    canonical = re.sub(
        r"\n[\t ]*}",
        "}",
        "\n".join(
            line
            for index, line in enumerate(lines)
            if not (0 < index < len(lines) - 1 and not line.strip())
        ),
    )
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture["v7Candidate"].update({
        "issue": 519,
        "version": "7.1.3",
        "sourceBytes": len(source.encode("utf-8")),
        "sourceLines": len(source.splitlines()),
        "sourceSha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "templateBytes": len(raw.encode("utf-8")),
        "templateLines": len(lines),
        "templateSha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "canonicalCssSha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    })
    FIXTURE.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")

    # Remove only the three rejected controls from the command-surface template.
    for action in ("previous", "pause", "next"):
        pattern = re.compile(
            rf'<button\b(?=[^>]*data-mcms-incident-action="{action}")[^>]*>.*?</button>',
            re.S,
        )
        source, count = pattern.subn("", source, count=1)
        if count != 1:
            raise SystemExit(f"Expected one {action} control button, found {count}")

    # Narrow the control rail to the retained dropdown only.
    source = append_css_properties(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls',
        'width:38px!important;min-width:38px!important;max-width:38px!important;flex-basis:38px!important;padding:0 4px!important;',
        "single dropdown rail",
    )

    # Correct the vertical centreline without adding new stylesheet blocks.
    source = append_css_properties(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item',
        'display:flex!important;align-items:center!important;justify-content:flex-start!important;line-height:1!important;padding-top:0!important;padding-bottom:0!important;vertical-align:middle!important;',
        "reel item alignment",
    )
    source = append_css_properties(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-copy,#${SCRIPT.majorIncidentFeedId} .mcms-incident-meta',
        'align-self:center!important;height:100%!important;line-height:1!important;margin-block:0!important;transform:none!important;',
        "reel copy alignment",
    )
    source = append_css_properties(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label-title,#${SCRIPT.majorIncidentFeedId} .mcms-incident-name,#${SCRIPT.majorIncidentFeedId} .mcms-incident-state',
        'align-self:center!important;line-height:1!important;margin-block:0!important;transform:none!important;',
        "reel text alignment",
    )
    source = append_css_properties(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-count',
        'align-self:center!important;margin-block:0!important;transform:none!important;',
        "live count alignment",
    )
    source = append_css_properties(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label',
        'align-items:center!important;line-height:1!important;',
        "fixed label alignment",
    )
    source = append_css_properties(
        source,
        '#${SCRIPT.majorIncidentFeedId} .mcms-incident-level',
        'align-self:center!important;line-height:1!important;margin-block:0!important;transform:none!important;',
        "priority badge alignment",
    )

    SOURCE.write_text(source, encoding="utf-8")

    static = STATIC.read_text(encoding="utf-8")
    static = replace_once(
        static,
        " for action in ['previous','pause','next','expand']: assert f'data-mcms-incident-action=\"{action}\"' in ensure\n",
        " template=ensure[ensure.index('feed.innerHTML = `'):ensure.index('`;',ensure.index('feed.innerHTML = `'))]\n"
        " assert 'data-mcms-incident-action=\"expand\"' in template\n"
        " for action in ['previous','pause','next']: assert f'data-mcms-incident-action=\"{action}\"' not in template\n"
        " assert 'width:38px!important' in source and 'flex-basis:38px!important' in source\n"
        " assert 'display:flex!important;align-items:center!important;justify-content:flex-start!important;line-height:1!important' in source\n"
        " assert source.count('align-self:center!important') >= 5\n",
        "single-control static contract",
    )
    STATIC.write_text(static, encoding="utf-8")

    RUNTIME.write_text("""#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const marker=`    function ${name}(`;const start=source.indexOf(marker);assert.ok(start>=0,`${name} missing`);const open=source.indexOf('{',start);let depth=0,quote='',escaped=false;for(let i=open;i<source.length;i++){const c=source[i];if(quote){if(escaped)escaped=false;else if(c==='\\\\')escaped=true;else if(c===quote)quote='';continue;}if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;if(c==='}'&&--depth===0)return source.slice(start,i+1);}throw new Error(`Could not extract ${name}`);}
const functions=['majorIncidentFeedEntryCount','majorIncidentFeedSyncControls','majorIncidentFeedAnimation','majorIncidentFeedSyncReelState','majorIncidentFeedSetExpanded'];
function classList(){return{values:new Set(),toggle(n,on){if(on)this.values.add(n);else this.values.delete(n);},contains(n){return this.values.has(n);},add(n){this.values.add(n);},remove(n){this.values.delete(n);}};}
function button(){return{disabled:false,attrs:{},textContent:'',title:'',setAttribute(n,v){this.attrs[n]=String(v);}};}
const animation={animationName:'mcmsIncidentWireReel',currentTime:0,playState:'running',effect:{getTiming:()=>({duration:12000})},play(){this.playState='running';},pause(){this.playState='paused';}};
const track={getAnimations:()=>[animation]};const counter={textContent:''};const panel={hidden:true};const expand=button();
const feed={isConnected:true,dataset:{mcmsEntryCount:'3'},classList:classList(),querySelector(selector){if(selector==='.mcms-incident-feed-track')return track;if(selector==='.mcms-incident-feed-count')return counter;if(selector==='.mcms-incident-feed-panel')return panel;if(selector.includes('data-mcms-incident-action="expand"'))return expand;return null;},querySelectorAll(){return[];}};
const sandbox={console,Date,Math,Number,Boolean,String,document:{hidden:false},state:{economyMode:false},majorIncidentFeedCurrentIndex:0,majorIncidentFeedManualPaused:false,majorIncidentFeedExpanded:false};
vm.createContext(sandbox);vm.runInContext(`${functions.map(extractFunction).join('\\n\\n')}\\nthis.api={${functions.join(',')}};`,sandbox);const api=sandbox.api;
assert.equal(api.majorIncidentFeedEntryCount(feed),3);api.majorIncidentFeedSyncControls(feed);assert.equal(counter.textContent,'3 LIVE');
assert.equal(source.includes('data-mcms-incident-action="previous"'),false);assert.equal(source.includes('data-mcms-incident-action="pause"'),false);assert.equal(source.includes('data-mcms-incident-action="next"'),false);assert.equal(source.includes('data-mcms-incident-action="expand"'),true);
api.majorIncidentFeedSetExpanded(feed,true);assert.equal(panel.hidden,false);assert.equal(animation.playState,'paused');assert.equal(expand.attrs['aria-expanded'],'true');
api.majorIncidentFeedSetExpanded(feed,false);assert.equal(panel.hidden,true);assert.equal(animation.playState,'running');assert.equal(expand.attrs['aria-expanded'],'false');
feed.classList.add('mcms-feed-interacting');api.majorIncidentFeedSyncReelState(feed);assert.equal(animation.playState,'paused');feed.classList.remove('mcms-feed-interacting');api.majorIncidentFeedSyncReelState(feed);assert.equal(animation.playState,'running');
console.log('Issue #519 dropdown-only continuous reel runtime contract passed.');
""", encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    changelog = replace_once(
        changelog,
        "- Made Pause freeze the reel at its exact position; Play resumes from that position, and previous/next nudge by one incident.",
        "- Removed the previous, pause/play and next controls; the reel now runs continuously with only the expanded-queue dropdown retained.",
        "v7.1.3 control changelog",
    )
    changelog = replace_once(
        changelog,
        "- Retained the unique expanded priority queue, click-to-open behaviour, all seven themes and Desktop, Tablet/iPad and iOS layouts.",
        "- Vertically centred the fixed label, live count, priority badge, mission title, metadata and response state across all seven themes and supported layouts.",
        "v7.1.3 alignment changelog",
    )
    CHANGELOG.write_text(changelog, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = replace_once(
        help_text,
        "The Incident Command Wire now moves as a continuous broadcast news reel. Incidents travel right-to-left at a constant speed with a seamless off-screen loop; Pause freezes the reel exactly where it is.",
        "The Incident Command Wire now moves as a continuous broadcast news reel with a single expanded-queue dropdown. Its labels, badges and incident text are vertically centred throughout the command bar.",
        "Help Centre final wire notice",
    )
    HELP.write_text(help_text, encoding="utf-8")

    update_headroom(source)

    for path in (SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print("v7.1.3 final Incident Command Wire UI cleanup applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
