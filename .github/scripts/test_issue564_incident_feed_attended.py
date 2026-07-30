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
    assert metadata and runtime and metadata.group(1)==runtime.group(1)
    version=tuple(int(part) for part in metadata.group(1).split('.'))
    assert version >= (8,3,0)
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
    assert motion.count('majorIncidentFeedApplyIndex(feed, majorIncidentFeedCurrentIndex)') == 1
    restart = motion.index('if (forceRestart) {')
    seek = motion.index('majorIncidentFeedApplyIndex(feed, majorIncidentFeedCurrentIndex)')
    ordinary = motion.index('Layout, resize and unchanged-render reconciliation must not seek a')
    assert restart < seek < ordinary
    radio=section(source,'    function captureRadioVehicleMessage(','    function installRadioMessageHook(')
    assert 'scheduleMissionSnapshotRefresh(state.majorIncidentFeed.enabled ? 90 : 850);' in radio
    print('Issue #564 Incident Feed attended-exclusion static contract passed.')
    return 0
if __name__=='__main__':raise SystemExit(main())
