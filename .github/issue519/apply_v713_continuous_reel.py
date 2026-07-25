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
README = ROOT / "README.md"
HELP = ROOT / "help" / "index.html"
SELF = ROOT / ".github" / "issue519" / "apply_v713_continuous_reel.py"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-issue519-v713-continuous-reel.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


def function_bounds(source: str, name: str) -> tuple[int, int]:
    marker = f"    function {name}("
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 0
    quote = ""
    escaped = False
    index = opening
    while index < len(source):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char in {'"', "'", "`"}:
            quote = char
            index += 1
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
        index += 1
    raise SystemExit(f"Could not locate end of {name}")


def replace_function(source: str, name: str, replacement: str) -> str:
    start, end = function_bounds(source, name)
    return source[:start] + replacement.rstrip() + source[end:]


def remove_function(source: str, name: str) -> str:
    start, end = function_bounds(source, name)
    while end < len(source) and source[end] == "\n":
        end += 1
        if end < len(source) and source[end] != "\n":
            break
    return source[:start] + source[end:]


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

    source = replace_once(
        source,
        "    let majorIncidentFeedMotionRevision = 0;\n    let majorIncidentFeedAdvanceTimer = null;\n    let majorIncidentFeedAdvanceRevision = 0;",
        "    let majorIncidentFeedMotionRevision = 0;",
        "obsolete automatic-advance timer state",
    )

    old_track = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-track{display:flex!important;align-items:stretch!important;width:100%!important;min-width:100%!important;height:100%!important;animation:none!important;will-change:transform;transition:transform .85s cubic-bezier(.22,.75,.18,1)!important}'
    new_track = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-track{display:flex!important;align-items:stretch!important;width:max-content!important;min-width:200%!important;height:100%!important;will-change:transform;animation:mcmsIncidentWireReel var(--mcms-incident-feed-duration,90s) linear infinite!important;transition:none!important}'
    source = replace_once(source, old_track, new_track, "carousel track style")
    source = replace_once(
        source,
        '@media (prefers-reduced-motion:reduce){#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-track{transition:transform .85s cubic-bezier(.22,.75,.18,1)!important}}',
        '@keyframes mcmsIncidentWireReel{from{transform:translate3d(0,0,0)}to{transform:translate3d(-50%,0,0)}}',
        "reduced-motion slide override",
    )
    old_item = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item{flex:0 0 100%!important;width:100%!important;min-width:100%!important;height:100%!important;padding:0 12px!important;gap:9px!important;overflow:hidden!important;border:0!important;border-left:3px solid var(--mcms-wire-accent)!important;background:linear-gradient(90deg,rgba(104,207,255,.08),transparent 30%)!important}'
    new_item = '#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-group{display:flex!important;align-items:stretch!important;flex:0 0 auto!important;width:max-content!important;min-width:max-content!important;height:100%!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item{flex:0 0 auto!important;width:clamp(520px,52vw,820px)!important;min-width:clamp(520px,52vw,820px)!important;max-width:820px!important;height:100%!important;padding:0 12px!important;gap:9px!important;overflow:hidden!important;border:0!important;border-left:3px solid var(--mcms-wire-accent)!important;background:linear-gradient(90deg,rgba(104,207,255,.08),transparent 30%)!important}#${SCRIPT.majorIncidentFeedId}.mcms-feed-paused .mcms-incident-feed-track,#${SCRIPT.majorIncidentFeedId}.mcms-feed-interacting .mcms-incident-feed-track,#${SCRIPT.majorIncidentFeedId}.mcms-feed-expanded .mcms-incident-feed-track,#${SCRIPT.majorIncidentFeedId}.mcms-feed-static .mcms-incident-feed-track{animation-play-state:paused!important}'
    source = replace_once(source, old_item, new_item, "carousel item style")
    source = replace_once(
        source,
        '@media (max-width:760px){#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label{min-width:104px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-meta{display:none}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{width:30px!important;height:30px!important;min-width:30px!important;min-height:30px!important;max-width:30px!important;max-height:30px!important}}',
        '@media (max-width:760px){#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label{min-width:104px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-meta{display:none}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item{width:78vw!important;min-width:78vw!important;max-width:78vw!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-controls button{width:30px!important;height:30px!important;min-width:30px!important;min-height:30px!important;max-width:30px!important;max-height:30px!important}}',
        "tablet reel item width",
    )
    source = replace_once(
        source,
        '@media (max-width:480px){#${SCRIPT.majorIncidentFeedId}{height:42px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label-title{display:none}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label{min-width:42px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-state{max-width:92px}}',
        '@media (max-width:480px){#${SCRIPT.majorIncidentFeedId}{height:42px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label-title{display:none}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-label{min-width:42px!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-item{width:86vw!important;min-width:86vw!important;max-width:86vw!important}#${SCRIPT.majorIncidentFeedId} .mcms-incident-feed-state{max-width:92px}}',
        "mobile reel item width",
    )

    sync_controls = """    function majorIncidentFeedSyncControls(feed) {
        if (!feed) return;
        const count = majorIncidentFeedEntryCount(feed);
        feed.dataset.mcmsIncidentIndex = String(majorIncidentFeedCurrentIndex);
        const counter = feed.querySelector('.mcms-incident-feed-count');
        if (counter) counter.textContent = count ? `${count} LIVE` : '0';
        feed.querySelectorAll('[data-mcms-incident-action="previous"],[data-mcms-incident-action="next"]').forEach(button => {
            button.disabled = count <= 1;
        });
        const pauseButton = feed.querySelector('[data-mcms-incident-action="pause"]');
        if (pauseButton) {
            pauseButton.setAttribute('aria-pressed', String(majorIncidentFeedManualPaused));
            pauseButton.setAttribute('aria-label', majorIncidentFeedManualPaused ? 'Resume incident reel' : 'Pause incident reel');
            pauseButton.title = majorIncidentFeedManualPaused ? 'Resume incident reel' : 'Pause incident reel';
            pauseButton.textContent = majorIncidentFeedManualPaused ? '▶' : 'Ⅱ';
            pauseButton.disabled = count <= 1;
        }
        const expandButton = feed.querySelector('[data-mcms-incident-action="expand"]');
        if (expandButton) {
            expandButton.setAttribute('aria-expanded', String(majorIncidentFeedExpanded));
            expandButton.setAttribute('aria-label', majorIncidentFeedExpanded ? 'Collapse incident queue' : 'Expand incident queue');
            expandButton.title = majorIncidentFeedExpanded ? 'Collapse incident queue' : 'Expand incident queue';
            expandButton.textContent = majorIncidentFeedExpanded ? '⌃' : '⌄';
        }
    }"""
    source = replace_function(source, "majorIncidentFeedSyncControls", sync_controls)

    apply_index = """    function majorIncidentFeedApplyIndex(feed, index = majorIncidentFeedCurrentIndex) {
        const count = majorIncidentFeedEntryCount(feed);
        if (!feed || count <= 0) {
            majorIncidentFeedCurrentIndex = 0;
            majorIncidentFeedSyncControls(feed);
            return false;
        }
        const normalised = ((Number(index) || 0) % count + count) % count;
        majorIncidentFeedCurrentIndex = normalised;
        const animation = majorIncidentFeedAnimation(feed);
        const duration = Number(animation?.effect?.getTiming?.().duration) || 0;
        if (animation && duration > 0) animation.currentTime = (duration / count) * normalised;
        majorIncidentFeedSyncControls(feed);
        return true;
    }"""
    source = replace_function(source, "majorIncidentFeedApplyIndex", apply_index)

    source = remove_function(source, "majorIncidentFeedCancelAdvance")
    source = remove_function(source, "majorIncidentFeedScheduleAdvance")
    animation_helpers = """    function majorIncidentFeedAnimation(feed) {
        const track = feed?.querySelector?.('.mcms-incident-feed-track');
        if (!track || typeof track.getAnimations !== 'function') return null;
        const animations = track.getAnimations();
        return animations.find(animation => animation.animationName === 'mcmsIncidentWireReel') || animations[0] || null;
    }

    function majorIncidentFeedSyncReelState(feed) {
        if (!feed) return false;
        const count = majorIncidentFeedEntryCount(feed);
        const shouldPause = Boolean(
            count <= 1 ||
            state.economyMode ||
            majorIncidentFeedManualPaused ||
            majorIncidentFeedExpanded ||
            document.hidden ||
            feed.classList.contains('mcms-feed-interacting')
        );
        feed.classList.toggle('mcms-feed-static', count <= 1 || state.economyMode);
        const animation = majorIncidentFeedAnimation(feed);
        if (animation) {
            try {
                if (shouldPause) animation.pause();
                else animation.play();
            } catch (err) {}
        }
        return !shouldPause;
    }

"""
    insert_at = source.index("    function majorIncidentFeedSetPaused(")
    source = source[:insert_at] + animation_helpers + source[insert_at:]

    set_paused = """    function majorIncidentFeedSetPaused(feed, paused) {
        majorIncidentFeedManualPaused = Boolean(paused);
        feed?.classList?.toggle('mcms-feed-paused', majorIncidentFeedManualPaused);
        majorIncidentFeedSyncControls(feed);
        majorIncidentFeedSyncReelState(feed);
    }"""
    source = replace_function(source, "majorIncidentFeedSetPaused", set_paused)

    set_expanded = """    function majorIncidentFeedSetExpanded(feed, expanded) {
        majorIncidentFeedExpanded = Boolean(expanded);
        feed?.classList?.toggle('mcms-feed-expanded', majorIncidentFeedExpanded);
        const panel = feed?.querySelector?.('.mcms-incident-feed-panel');
        if (panel) panel.hidden = !majorIncidentFeedExpanded;
        majorIncidentFeedSyncControls(feed);
        majorIncidentFeedSyncReelState(feed);
    }"""
    source = replace_function(source, "majorIncidentFeedSetExpanded", set_expanded)

    advance = """    function majorIncidentFeedAdvance(feed, delta, manual = false) {
        const count = majorIncidentFeedEntryCount(feed);
        if (count <= 1) return false;
        const animation = majorIncidentFeedAnimation(feed);
        const duration = Number(animation?.effect?.getTiming?.().duration) || 0;
        const currentTime = duration > 0 ? ((Number(animation?.currentTime) || 0) % duration + duration) % duration : 0;
        const currentIndex = duration > 0 ? Math.floor(currentTime / (duration / count)) : majorIncidentFeedCurrentIndex;
        const changed = majorIncidentFeedApplyIndex(feed, currentIndex + Number(delta || 0));
        if (!majorIncidentFeedManualPaused) majorIncidentFeedSyncReelState(feed);
        return changed;
    }"""
    source = replace_function(source, "majorIncidentFeedAdvance", advance)

    source = replace_once(
        source,
        "        majorIncidentFeedCancelAdvance();\n        majorIncidentFeedCurrentIndex = 0;",
        "        majorIncidentFeedCurrentIndex = 0;",
        "removed reel advance cancellation during teardown",
    )

    refresh = """    function refreshMajorIncidentFeedMotion(feed = document.getElementById(SCRIPT.majorIncidentFeedId), forceRestart = false, attempt = 0, revision = majorIncidentFeedMotionRevision) {
        if (!feed || revision !== majorIncidentFeedMotionRevision || !feed.isConnected || !state.majorIncidentFeed.enabled) return false;
        const viewport = feed.querySelector('.mcms-incident-feed-viewport');
        const track = feed.querySelector('.mcms-incident-feed-track');
        const firstGroup = track?.querySelector('.mcms-incident-feed-group');
        if (!viewport || !track || !firstGroup) return false;
        const groupWidth = Math.max(firstGroup.scrollWidth || 0, firstGroup.getBoundingClientRect?.().width || 0);
        if (groupWidth < 20 && attempt < 6) {
            runtimeClearTimeout(majorIncidentFeedMotionTimer);
            majorIncidentFeedMotionTimer = runtimeSetTimeout(() => {
                majorIncidentFeedMotionTimer = null;
                refreshMajorIncidentFeedMotion(feed, true, attempt + 1, revision);
            }, 70 + (attempt * 55));
            return false;
        }
        const count = majorIncidentFeedEntryCount(feed);
        const duration = Math.round(clamp(groupWidth / 85, 28, 240, 90));
        feed.style.setProperty('--mcms-incident-feed-duration', `${duration}s`);
        if (forceRestart) {
            track.style.setProperty('animation', 'none', 'important');
            void track.offsetWidth;
            track.style.removeProperty('animation');
            majorIncidentFeedCurrentIndex = 0;
        }
        majorIncidentFeedSyncControls(feed);
        majorIncidentFeedSyncReelState(feed);
        return count > 1;
    }"""
    source = replace_function(source, "refreshMajorIncidentFeedMotion", refresh)

    item_html = """    function majorIncidentFeedItemHtml(entry, mode = 'wire', duplicate = false) {
        const snapshot = entry.snapshot;
        const source = snapshot.source === 'alliance' ? 'ALLIANCE' : 'PERSONAL';
        const creditText = Number.isFinite(entry.credits) ? `≈${formatOperationalCompactCredits(entry.credits)} CR` : 'VALUE UNKNOWN';
        const ageText = entry.ageMs >= 8 * 60 * 60 * 1000 ? `${formatElapsedCompact(entry.ageMs)} OLD` : '';
        const casualtyText = entry.patients >= MAJOR_INCIDENT_MASS_CASUALTY_PATIENTS ? `${entry.patients} PATIENTS` : entry.prisoners >= MAJOR_INCIDENT_MASS_CASUALTY_PRISONERS ? `${entry.prisoners} PRISONERS` : '';
        const caption = snapshot.caption || `Mission ${snapshot.missionId}`;
        const details = [entry.postcode, creditText, source, ageText, casualtyText].filter(Boolean);
        const title = `${caption} · ${details.join(' · ')} · Click to open the mission`;
        const modeClass = mode === 'list' ? ' mcms-incident-feed-list-item' : '';
        const accessibility = duplicate ? ' aria-hidden="true" tabindex="-1"' : '';
        return `<button class="mcms-incident-feed-item${modeClass} mcms-incident-${escapeHtml(entry.operational.key)}" type="button" data-mcms-major-mission-id="${escapeHtml(snapshot.missionId)}" title="${escapeHtml(title)}" aria-label="Open ${escapeHtml(caption)} at ${escapeHtml(entry.postcode)}"${accessibility}>
            <span class="mcms-incident-level">MAJOR</span>
            <span class="mcms-incident-feed-copy">
                <span class="mcms-incident-name">${allianceAwareHtml(caption)}</span>
                <span class="mcms-incident-meta"><span class="mcms-incident-postcode">${escapeHtml(entry.postcode)}</span><span>${escapeHtml(creditText)}</span><span class="${source === 'ALLIANCE' ? 'mcms-alliance-text' : ''}">${escapeHtml(source)}</span>${ageText ? `<span>${escapeHtml(ageText)}</span>` : ''}${casualtyText ? `<span>${escapeHtml(casualtyText)}</span>` : ''}</span>
            </span>
            <span class="mcms-incident-state">${escapeHtml(entry.operational.label)}</span>
        </button>`;
    }"""
    source = replace_function(source, "majorIncidentFeedItemHtml", item_html)

    render = """    function renderMajorIncidentFeed(force = false) {
        if (!state.majorIncidentFeed.enabled || isAllianceBuildingsContext()) {
            removeMajorIncidentFeed();
            return;
        }
        const feed = ensureMajorIncidentFeed();
        if (!feed) return;
        const entries = state.economyMode ? majorIncidentFeedEntries().slice(0, 1) : majorIncidentFeedEntries();
        const signature = JSON.stringify({
            theme: state.uiTheme,
            minimum: state.majorIncidentFeed.minimumCredits,
            entries: entries.map(entry => [entry.snapshot.missionId, entry.snapshot.caption, entry.postcode, entry.operational.key, entry.operational.label, entry.credits, Math.floor(entry.ageMs / 60000)])
        });
        const existingTrack = feed.querySelector('.mcms-incident-feed-track');
        const hasRenderedContent = Boolean(existingTrack?.childElementCount);
        if (!force && signature === majorIncidentFeedRenderSignature && hasRenderedContent) {
            scheduleMajorIncidentFeedLayout();
            scheduleMajorIncidentFeedMotion(feed, false, 60);
            return;
        }
        majorIncidentFeedRenderSignature = signature;
        const label = feed.querySelector('.mcms-incident-feed-label-title');
        const track = feed.querySelector('.mcms-incident-feed-track');
        const list = feed.querySelector('.mcms-incident-feed-list');
        if (label) label.textContent = majorIncidentThemeLabel();
        if (!track || !list) return;
        feed.classList.toggle('mcms-feed-empty', entries.length === 0);
        feed.classList.toggle('mcms-feed-static', entries.length <= 1 || state.economyMode);
        feed.dataset.mcmsEntryCount = String(entries.length);
        if (!entries.length) {
            track.replaceChildren(document.createRange().createContextualFragment('<div class="mcms-incident-feed-empty">No qualifying major incidents currently active</div>'));
            list.replaceChildren(document.createRange().createContextualFragment('<div class="mcms-incident-feed-list-empty">No major incidents currently meet the configured threshold.</div>'));
            majorIncidentFeedCurrentIndex = 0;
            majorIncidentFeedSetExpanded(feed, false);
            majorIncidentFeedSyncControls(feed);
        } else {
            const primary = entries.map(entry => majorIncidentFeedItemHtml(entry, 'wire', false)).join('');
            const duplicate = entries.map(entry => majorIncidentFeedItemHtml(entry, 'wire', true)).join('');
            track.replaceChildren(document.createRange().createContextualFragment(`<div class="mcms-incident-feed-group" data-mcms-reel-copy="primary">${primary}</div><div class="mcms-incident-feed-group" data-mcms-reel-copy="duplicate" aria-hidden="true">${duplicate}</div>`));
            list.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'list', false)).join('')));
            majorIncidentFeedCurrentIndex = 0;
            majorIncidentFeedSyncControls(feed);
            scheduleMajorIncidentFeedMotion(feed, true, 70);
        }
        scheduleMajorIncidentFeedLayout();
    }"""
    source = replace_function(source, "renderMajorIncidentFeed", render)

    source = source.replace("                majorIncidentFeedCancelAdvance();", "                majorIncidentFeedSyncReelState(feed);")
    source = source.replace("                majorIncidentFeedInteractionPauseUntil = Date.now() + 1200;\n                majorIncidentFeedScheduleAdvance(feed, 1500, true);", "                majorIncidentFeedInteractionPauseUntil = 0;\n                majorIncidentFeedSyncReelState(feed);")
    source = source.replace("                    majorIncidentFeedInteractionPauseUntil = Date.now() + 1200;\n                    majorIncidentFeedScheduleAdvance(feed, 1500, true);", "                    majorIncidentFeedInteractionPauseUntil = 0;\n                    majorIncidentFeedSyncReelState(feed);")
    source = source.replace("                majorIncidentFeedInteractionPauseUntil = Date.now() + MAJOR_INCIDENT_FEED_INTERACTION_PAUSE_MS;", "                majorIncidentFeedInteractionPauseUntil = 0;")
    if "majorIncidentFeedCancelAdvance" in source or "majorIncidentFeedScheduleAdvance" in source or "majorIncidentFeedAdvanceTimer" in source:
        raise SystemExit("Obsolete card-advance scheduler remains after continuous-reel transform")

    SOURCE.write_text(source, encoding="utf-8")

    STATIC.write_text("""#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js'
def section(text,start,end):
 left=text.index(start);right=text.index(end,left);return text[left:right]
def main():
 source=SOURCE.read_text(encoding='utf-8')
 metadata=re.search(r'(?m)^//\\s*@version\\s+([^\\s]+)$',source);runtime=re.search(r"version:\\s*'([^']+)'",source)
 assert metadata and runtime and metadata.group(1)==runtime.group(1)=='7.1.3'
 for name in ['majorIncidentFeedEntryCount','majorIncidentFeedSyncControls','majorIncidentFeedApplyIndex','majorIncidentFeedAnimation','majorIncidentFeedSyncReelState','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance']:
  assert source.count(f'function {name}(')==1,name
 render=section(source,'    function renderMajorIncidentFeed(','    function scheduleMajorIncidentFeedRender(')
 motion=section(source,'    function refreshMajorIncidentFeedMotion(','    function scheduleMajorIncidentFeedMotion(')
 ensure=section(source,'    function ensureMajorIncidentFeed(','    function renderMajorIncidentFeed(')
 assert '@keyframes mcmsIncidentWireReel' in source
 assert 'animation:mcmsIncidentWireReel var(--mcms-incident-feed-duration,90s) linear infinite!important' in source
 assert 'transition:none!important' in source
 assert source.count('data-mcms-reel-copy=')==2
 assert 'data-mcms-reel-copy="primary"' in render and 'data-mcms-reel-copy="duplicate"' in render
 assert 'aria-hidden="true" tabindex="-1"' in source
 assert 'groupWidth / 85' in motion and "--mcms-incident-feed-duration" in motion
 assert 'translate3d(-50%,0,0)' in source
 assert 'translate3d(${-normalised * 100}%' not in source
 assert 'majorIncidentFeedScheduleAdvance' not in source and 'majorIncidentFeedAdvanceTimer' not in source
 assert "`${count} LIVE`" in source
 assert 'animation-play-state:paused!important' in source
 for action in ['previous','pause','next','expand']: assert f'data-mcms-incident-action="{action}"' in ensure
 for theme in ['cyberpunk','fallout4','umbrella','factorio','bond007','hyrule']: assert f'html[data-mcms-ui-theme="{theme}"] #${{SCRIPT.majorIncidentFeedId}}' in source
 assert 'width:78vw!important' in source and 'width:86vw!important' in source
 token='ls'+'sm';assert token not in source.lower()
 print('Issue #519 continuous Incident Command Wire reel contract passed.')
 return 0
if __name__=='__main__':raise SystemExit(main())
""", encoding="utf-8")

    RUNTIME.write_text("""#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const vm=require('node:vm');
const root=path.resolve(__dirname,'..','..');const source=fs.readFileSync(path.join(root,'src','MissionChief_Map_Command_Toolkit.user.js'),'utf8');
function extractFunction(name){const marker=`    function ${name}(`;const start=source.indexOf(marker);assert.ok(start>=0,`${name} missing`);const open=source.indexOf('{',start);let depth=0,quote='',escaped=false;for(let i=open;i<source.length;i++){const c=source[i];if(quote){if(escaped)escaped=false;else if(c==='\\\\')escaped=true;else if(c===quote)quote='';continue;}if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;if(c==='}'&&--depth===0)return source.slice(start,i+1);}throw new Error(`Could not extract ${name}`);}
const functions=['majorIncidentFeedEntryCount','majorIncidentFeedSyncControls','majorIncidentFeedAnimation','majorIncidentFeedSyncReelState','majorIncidentFeedApplyIndex','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance'];
function classList(){return{values:new Set(),toggle(n,on){if(on)this.values.add(n);else this.values.delete(n);},contains(n){return this.values.has(n);},add(n){this.values.add(n);},remove(n){this.values.delete(n);}};}
function button(){return{disabled:false,attrs:{},textContent:'',title:'',setAttribute(n,v){this.attrs[n]=String(v);}};}
const animation={animationName:'mcmsIncidentWireReel',currentTime:0,playState:'running',effect:{getTiming:()=>({duration:12000})},play(){this.playState='running';},pause(){this.playState='paused';}};
const track={getAnimations:()=>[animation]};const counter={textContent:''};const panel={hidden:true};const controls={previous:button(),pause:button(),next:button(),expand:button()};
const feed={isConnected:true,dataset:{mcmsEntryCount:'3'},classList:classList(),querySelector(selector){if(selector==='.mcms-incident-feed-track')return track;if(selector==='.mcms-incident-feed-count')return counter;if(selector==='.mcms-incident-feed-panel')return panel;const m=selector.match(/data-mcms-incident-action="([^"]+)"/);return m?controls[m[1]]:null;},querySelectorAll(selector){return selector.includes('previous')?[controls.previous,controls.next]:[];}};
const sandbox={console,Date,Math,Number,Boolean,String,document:{hidden:false},state:{economyMode:false},majorIncidentFeedCurrentIndex:0,majorIncidentFeedManualPaused:false,majorIncidentFeedExpanded:false};
vm.createContext(sandbox);vm.runInContext(`${functions.map(extractFunction).join('\\n\\n')}\\nthis.api={${functions.join(',')},state:()=>({index:majorIncidentFeedCurrentIndex,paused:majorIncidentFeedManualPaused,expanded:majorIncidentFeedExpanded})};`,sandbox);const api=sandbox.api;
assert.equal(api.majorIncidentFeedEntryCount(feed),3);api.majorIncidentFeedSyncControls(feed);assert.equal(counter.textContent,'3 LIVE');
api.majorIncidentFeedSetPaused(feed,true);assert.equal(animation.playState,'paused');assert.equal(controls.pause.textContent,'▶');
api.majorIncidentFeedSetPaused(feed,false);assert.equal(animation.playState,'running');assert.equal(controls.pause.textContent,'Ⅱ');
assert.equal(api.majorIncidentFeedAdvance(feed,1,true),true);assert.equal(animation.currentTime,4000);
assert.equal(api.majorIncidentFeedAdvance(feed,-1,true),true);assert.equal(animation.currentTime,0);
api.majorIncidentFeedSetExpanded(feed,true);assert.equal(panel.hidden,false);assert.equal(animation.playState,'paused');
api.majorIncidentFeedSetExpanded(feed,false);assert.equal(panel.hidden,true);assert.equal(animation.playState,'running');
feed.classList.add('mcms-feed-interacting');api.majorIncidentFeedSyncReelState(feed);assert.equal(animation.playState,'paused');feed.classList.remove('mcms-feed-interacting');api.majorIncidentFeedSyncReelState(feed);assert.equal(animation.playState,'running');
console.log('Issue #519 continuous Incident Command Wire reel runtime contract passed.');
""", encoding="utf-8")

    changelog = CHANGELOG.read_text(encoding="utf-8")
    start = changelog.index("## [7.1.3] - 2026-07-25")
    end = changelog.index("## [7.1.2] - 2026-07-25", start)
    section = """## [7.1.3] - 2026-07-25

### Continuous Incident Command news reel

- Replaced card-by-card carousel transitions with a constant-speed broadcast ticker reel that moves continuously from right to left.
- Rendered two accessibility-safe copies of the unique incident sequence so the loop resets off-screen without a visible jump or empty gap.
- Kept the title block and controls fixed while only the incident reel moves.
- Made Pause freeze the reel at its exact position; Play resumes from that position, and previous/next nudge by one incident.
- Retained the unique expanded priority queue, click-to-open behaviour, all seven themes and Desktop, Tablet/iPad and iOS layouts.
- Added static and executable contracts for linear infinite motion, seamless duplication, dynamic speed, pause ownership and manual reel seeking.

"""
    CHANGELOG.write_text(changelog[:start] + section + changelog[end:], encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    readme = re.sub(r"## \*\*Current verified release: `v7\.1\.2` · Development candidate: `v7\.1\.3`[^\n]*\*\*", "## **Current verified release: `v7.1.2` · Development candidate: `v7.1.3` — Continuous Incident Command news reel**", readme, count=1)
    README.write_text(readme, encoding="utf-8")

    help_text = HELP.read_text(encoding="utf-8")
    help_text = re.sub(r'<main><section class="notice"><h2>What changed in v7\.1\.3</h2><p>.*?</p></section>', '<main><section class="notice"><h2>What changed in v7.1.3</h2><p>The Incident Command Wire now moves as a continuous broadcast news reel. Incidents travel right-to-left at a constant speed with a seamless off-screen loop; Pause freezes the reel exactly where it is.</p></section>', help_text, count=1, flags=re.S)
    HELP.write_text(help_text, encoding="utf-8")

    update_headroom(source)

    for path in (SELF, WORKFLOW):
        path.unlink(missing_ok=True)
    try:
        SELF.parent.rmdir()
    except OSError:
        pass

    print("v7.1.3 continuous Incident Command news reel candidate applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
