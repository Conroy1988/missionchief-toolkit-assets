#!/usr/bin/env python3
from pathlib import Path

changelog = Path('CHANGELOG.md')
text = changelog.read_text(encoding='utf-8')
anchor = '## [Unreleased]\n'
entry = '''## [Unreleased]

## [4.11.2] - 2026-07-14

### Fixed
- Restored the full Toolkit stylesheet to the sparse `document-start` phase so Chrome no longer rematches thousands of selectors against an already-rendered MissionChief page.
- Changed the complete settings panel to first-open construction instead of building hundreds of controls during every page startup.
- Prevented Major Incident Feed rendering from bypassing the deferred operational-startup gate through the general UI refresh path.

### Performance
- Preserved the deferred vehicle API, mission snapshot and operational monitor startup introduced in v4.11.1.
- Reduced initial Toolkit construction to the core map command control and persistent shortcut bar.
- Added lightweight startup timings for stylesheet installation, core UI readiness, settings-panel construction and operational startup under `window.__MCMS_STARTUP_METRICS__`.

### Compatibility
- Preserved Smart Bookmark Labels, all interface themes, responsive modes and the early Alliance Buildings map blocker.
'''
if anchor not in text:
    raise SystemExit('CHANGELOG Unreleased anchor is missing')
if '## [4.11.2]' not in text:
    text = text.replace(anchor, entry, 1)
changelog.write_text(text, encoding='utf-8')

readme = Path('README.md')
text = readme.read_text(encoding='utf-8')
text = text.replace('version-4.11.1-2563eb', 'version-4.11.2-2563eb')
text = text.replace('Current validated version | `4.11.1`', 'Current validated version | `4.11.2`')
readme.write_text(text, encoding='utf-8')
