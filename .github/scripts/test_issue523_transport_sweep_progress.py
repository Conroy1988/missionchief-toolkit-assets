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
 assert version >= (7,1,4)
 for marker in ['completedMissionCount: 0','function transportSweepMissionProgress()','function setTransportSweepMissionProgress(','function completeTransportSweepMissionProgress(','function finaliseTransportSweepMissionProgress(']: assert marker in source,marker
 hud=section(source,'    function renderTransportSweepHud()','    function renderTransportSweepPanel()')
 panel_start=source.index('    function renderTransportSweepPanel()')
 panel_end=source.index('\n    function ',panel_start+1)
 panel=source[panel_start:panel_end]
 processor=re.search(r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',source);assert processor
 start=section(source,'    async function startTransportSweep()','    function stopTransportSweep(')
 assert 'const progress = transportSweepMissionProgress();' in hud and 'escapeHtml(progress.text)' in hud
 assert 'const missionProgress = transportSweepMissionProgress();' in panel and 'escapeHtml(missionProgress.text)' in panel and 'Mission progress' in panel
 assert 'setTransportSweepMissionProgress(queue.length ? 1 : 0, queue.length' in start
 assert 'setTransportSweepMissionProgress(missionNumber, queue.length' in start
 assert 'completeTransportSweepMissionProgress(missionNumber, { forceRender: true })' in start
 assert 'finally {' in start and "recovering from a mission error" in start
 assert 'finaliseTransportSweepMissionProgress(wasStopped)' in start
 assert 'missionProgress.text' in start
 assert 'transportSweepRuntime.missionIndex = missionOffset + 1' not in source
 patient_body=processor.group(1)
 for forbidden in ['missionIndex','setTransportSweepMissionProgress','completeTransportSweepMissionProgress','finaliseTransportSweepMissionProgress']: assert forbidden not in patient_body,forbidden
 assert "if (!wasStopped && progress.total > 0)" in source
 assert 'transportSweepRuntime.missionIndex = progress.total;' in source
 assert 'transportSweepRuntime.completedMissionCount = progress.total;' in source
 print('Issue #523 Transport Sweep mission-progress static contract passed.')
 return 0
if __name__=='__main__':raise SystemExit(main())
