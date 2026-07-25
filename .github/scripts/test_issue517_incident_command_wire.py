#!/usr/bin/env python3
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
 template=ensure[ensure.index('feed.innerHTML = `'):ensure.index('`;',ensure.index('feed.innerHTML = `'))]
 assert 'data-mcms-incident-action="expand"' in template
 for action in ['previous','pause','next']: assert f'data-mcms-incident-action="{action}"' not in template
 assert 'width:38px!important' in source and 'flex-basis:38px!important' in source
 assert 'display:flex!important;align-items:center!important;justify-content:flex-start!important;line-height:1!important' in source
 assert source.count('align-self:center!important') >= 5
 assert 'transform:translateY(-2px)!important' not in source
 assert source.count('padding-bottom:14px!important') == 2
 assert source.count('padding-top:0!important') >= 2
 assert source.count('box-sizing:border-box!important') >= 4
 assert '.mcms-incident-level' in source and '.mcms-incident-meta' in source
 for theme in ['cyberpunk','fallout4','umbrella','factorio','bond007','hyrule']: assert f'html[data-mcms-ui-theme="{theme}"] #${{SCRIPT.majorIncidentFeedId}}' in source
 assert 'width:78vw!important' in source and 'width:86vw!important' in source
 token='ls'+'sm';assert token not in source.lower()
 print('Issue #519 continuous Incident Command Wire reel contract passed.')
 return 0
if __name__=='__main__':raise SystemExit(main())
