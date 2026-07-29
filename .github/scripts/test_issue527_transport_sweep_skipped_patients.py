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
 assert version >= (7,1,5)
 for marker in ['skippedPatientKeys: new Set()','function recordTransportSweepSkippedPatient(skipKey, message)','transportSweepRuntime.skippedPatientKeys = new Set();']:
  assert marker in source,marker
 helper=section(source,'    function recordTransportSweepSkippedPatient(','    const TRANSPORT_SWEEP_NATIVE_RELEASE_LABELS')
 processor=re.search(r'async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep',source);assert processor
 body=processor.group(1)
 assert source.count('transportSweepRuntime.skipped += 1')==1
 assert source.count('transportSweepRuntime.processed += 1')==2
 assert 'confirmedReleaseKeys.has(key)' in helper and 'skippedPatientKeys.has(key)' in helper
 assert 'renderTransportSweepPanel();' in helper and "transportSweepLog(message, 'warn');" in helper
 assert 'recordTransportSweepSkippedPatient(' in body
 assert 'transportSweepReleaseKey(missionId, candidate.vehicleId)' in body
 assert 'no usable Cancel Transport or Discharge patient control was available' in body
 assert 'transportSweepRuntime.skipped += 1' not in body
 assert 'clearedHere === 0' not in body
 assert 'no patient skip was recorded' in body
 assert '${transportSweepRuntime.skipped} skipped' in source
 print('Issue #527 skipped-patient static contract passed.')
 return 0
if __name__=='__main__':raise SystemExit(main())
