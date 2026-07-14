#!/usr/bin/env python3
from pathlib import Path

changelog = Path('CHANGELOG.md')
text = changelog.read_text(encoding='utf-8')
anchor = '## [Unreleased]\n'
entry = '''## [Unreleased]

## [4.11.1] - 2026-07-14

### Performance
- Added a two-stage idle bootstrap so MissionChief can finish its own DOM and map construction before the full Toolkit starts.
- Deferred the 789 KB Toolkit stylesheet from `document-start` to the idle startup phase without changing any theme, skin or responsive layout.
- Consolidated the initial vehicle API, mission snapshot and operational overlay work into one coordinated data pass.
- Delayed and narrowed DOM observation to the map, mission list and top-level page changes instead of observing the entire body during initial rendering.

### Changed
- Mission Inspector and Critical View UI are now created on demand rather than eagerly during page load.
- Major Incident Feed, Transport Watcher, Stuck Mission Detector, Resource Gap and related overlays start after the core map controls are usable.
- Startup mutation refreshes use a longer settling debounce and no longer force mission snapshots when no snapshot-dependent feature is active.

### Fixed
- Prevented overlapping startup snapshot refreshes caused by the vehicle API completion timer and the previous 850 ms fallback refresh.
- Added safe recovery for background-tab startup and MissionChief navigation that replaces map or mission-list containers.
- Preserved the early Alliance Buildings map blocker while deferring all unrelated Toolkit work.
'''
if anchor not in text:
    raise SystemExit('CHANGELOG Unreleased anchor is missing')
if '## [4.11.1]' not in text:
    text = text.replace(anchor, entry, 1)
changelog.write_text(text, encoding='utf-8')

readme = Path('README.md')
text = readme.read_text(encoding='utf-8')
text = text.replace('version-4.11.0-2563eb', 'version-4.11.1-2563eb')
text = text.replace('Current validated version | `4.11.0`', 'Current validated version | `4.11.1`')
readme.write_text(text, encoding='utf-8')
