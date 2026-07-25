#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
def section(text: str, start: str, end: str) -> str:
    left = text.index(start); right = text.index(end, left); return text[left:right]
def main() -> int:
    source = SOURCE.read_text(encoding='utf-8')
    metadata = re.search(r'(?m)^//\s*@version\s+([^\s]+)$', source)
    runtime = re.search(r"version:\s*'([^']+)'", source)
    assert metadata and runtime and metadata.group(1) == runtime.group(1) == '7.1.2'
    for name in ['majorIncidentFeedEntryCount','majorIncidentFeedInteractionActive','majorIncidentFeedSyncControls','majorIncidentFeedApplyIndex','majorIncidentFeedCancelAdvance','majorIncidentFeedScheduleAdvance','majorIncidentFeedSetPaused','majorIncidentFeedSetExpanded','majorIncidentFeedAdvance']:
        assert source.count(f'function {name}(') == 1, name
    render = section(source, '    function renderMajorIncidentFeed(', '    function scheduleMajorIncidentFeedRender(')
    ensure = section(source, '    function ensureMajorIncidentFeed(', '    function renderMajorIncidentFeed(')
    motion = section(source, '    function refreshMajorIncidentFeedMotion(', '    function scheduleMajorIncidentFeedMotion(')
    cancel = section(source, '    function majorIncidentFeedCancelAdvance(', '    function majorIncidentFeedScheduleAdvance(')
    schedule = section(source, '    function majorIncidentFeedScheduleAdvance(', '    function majorIncidentFeedSetPaused(')
    pause = section(source, '    function majorIncidentFeedSetPaused(', '    function majorIncidentFeedSetExpanded(')
    assert "track.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'wire')).join('')));" in render
    assert "list.replaceChildren(document.createRange().createContextualFragment(entries.map(entry => majorIncidentFeedItemHtml(entry, 'list')).join('')));" in render
    assert '${group}${group}' not in render and 'mcms-incident-feed-group' not in render
    assert 'mcmsIncidentWireScroll' not in render
    assert 'innerHTML = entries.map' not in render
    for action in ['previous','pause','next','expand']:
        assert f'data-mcms-incident-action="{action}"' in ensure
    assert 'mcms-incident-feed-panel' in ensure and 'mcms-incident-feed-list' in ensure
    assert "focusMissionById(item.dataset.mcmsMajorMissionId, false);" in ensure
    assert "feed.addEventListener('pointerover'" in ensure
    assert "feed.addEventListener('pointerout'" in ensure
    assert "if (closestEventTarget(event, '[data-mcms-incident-action]')) return;" in ensure
    assert "feed.addEventListener('focusin'" in ensure
    assert 'pageWindow.matchMedia' in source and 'prefers-reduced-motion: reduce' in source
    assert 'state.economyMode' in motion
    assert 'majorIncidentFeedInteractionPauseUntil = 0;' in pause
    assert source.count('let majorIncidentFeedAdvanceTimer = null;') == 1
    assert source.count('let majorIncidentFeedAdvanceRevision = 0;') == 1
    assert 'majorIncidentFeedAdvanceTimer' in cancel and 'majorIncidentFeedMotionTimer' not in cancel
    assert 'majorIncidentFeedAdvanceTimer' in schedule and 'majorIncidentFeedMotionTimer' not in schedule
    assert 'if (majorIncidentFeedAdvanceTimer !== null && !restart) return true;' in schedule
    assert 'majorIncidentFeedScheduleAdvance(feed, forceRestart ? 1200 : MAJOR_INCIDENT_FEED_ROTATION_MS, forceRestart);' in motion
    assert "feed?.classList?.remove('mcms-feed-interacting');" in pause
    assert 'majorIncidentFeedScheduleAdvance(feed, 650, true);' in pause
    assert 'align-self:center!important' in source and 'height:calc(100% - 4px)!important' in source
    assert 'box-sizing:border-box!important' in source and 'margin:0!important' in source
    assert 'width:26px!important' in source and 'max-height:26px!important' in source
    assert 'width:30px!important' in source and 'max-height:30px!important' in source
    assert 'overflow:hidden!important' in source
    for theme in ['cyberpunk','fallout4','umbrella','factorio','bond007','hyrule']:
        assert f'html[data-mcms-ui-theme="{theme}"] #${{SCRIPT.majorIncidentFeedId}}' in source, theme
    for marker in ['Incident Command Wire','mcms-incident-feed-controls','mcms-incident-feed-panel-head','mcms-incident-feed-list-item','@media (max-width:760px)','@media (max-width:480px)']:
        assert marker in source, marker
    token = 'ls' + 'sm'
    assert token not in source.lower()
    print('Issue #517 Incident Command Wire static contract passed.')
    return 0
if __name__ == '__main__': raise SystemExit(main())
