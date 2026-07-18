#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / '.github' / 'scripts' / 'test_mission_requirements_runtime.js'
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-173-package-result.txt'

text = RUNTIME.read_text(encoding='utf-8')
old_start = '''const missingDoc = new FakeDocument();
missingDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9901' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const missingCandidate = makeMissionCandidateWithoutSource(missingDoc);
candidates = [missingCandidate];
api.scan();
flushAnimationFrames();
let missingRecord = Array.from(api.records.values())[0];
assert(missingRecord.panel.innerHTML.includes('Loading mission requirements'), 'source-less mission initially shows a bounded loading state');
missingRecord.startedAt = Date.now() - 2000;
api.scan();
flushAnimationFrames();
missingRecord = Array.from(api.records.values())[0];
assert(missingRecord.panel.innerHTML.includes('Unable to pull mission requirements'), 'source-less mission shows an explicit failure state');
assert(missingRecord.panel.innerHTML.includes('Report Mission'), 'failure state exposes Report Mission');

const unsafeSource = new FakeElement('div', missingDoc);'''
new_start = '''const missingDoc = new FakeDocument();
missingDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9901' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const missingCandidate = makeMissionCandidateWithoutSource(missingDoc);
candidates = [missingCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'source-less mission waits for a valid header or native requirements source');

const unsafeSource = new FakeElement('div', missingDoc);'''
if text.count(old_start) != 1:
    raise AssertionError('source-less fixture start not found exactly once')
text = text.replace(old_start, new_start, 1)
old_recovery = 'missingRecord.candidate.source = unsafeSource;'
new_recovery = '''api.scan();
flushAnimationFrames();
let missingRecord = Array.from(api.records.values())[0];
assert(missingRecord, 'native requirements source creates a record after the source-less wait');'''
if text.count(old_recovery) != 1:
    raise AssertionError('source-less fixture recovery anchor not found exactly once')
text = text.replace(old_recovery, new_recovery, 1)
RUNTIME.write_text(text, encoding='utf-8')
if REPORT.exists():
    REPORT.unlink()
print('Issue 173 source-less fixture corrected')
