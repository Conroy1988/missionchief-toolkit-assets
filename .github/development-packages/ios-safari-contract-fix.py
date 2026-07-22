#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
FIXTURE = ROOT / '.github' / 'fixtures' / 'main-style-source-headroom.json'
TEMP_WORKFLOW = ROOT / '.github' / 'workflows' / 'temporary-ios-preflight-diagnostic.yml'

text = SOURCE.read_text(encoding='utf-8')
old_refresh = "function refreshTouchViewportLayout(){if(runtime.destroyed)return;applyRootAttributes();refreshTabletModeUi();fitControlToMap();const panel=document.getElementById(SCRIPT.panelId);if(panel?.classList.contains('mcms-open'))applyTabletPanelPosition();scheduleCriticalDrawerDock(0);scheduleMajorIncidentFeedLayout();}"
new_refresh = "function refreshTouchViewportLayout(){if(runtime.destroyed)return;applyRootAttributes();applyVisualViewportGeometry();refreshTabletModeUi();fitControlToMap();const panel=document.getElementById(SCRIPT.panelId);if(panel?.classList.contains('mcms-open'))applyTabletPanelPosition();scheduleCriticalDrawerDock(0);scheduleMajorIncidentFeedLayout();}"
if text.count(old_refresh) != 1:
    raise SystemExit('Expected one touch viewport refresh anchor')
text = text.replace(old_refresh, new_refresh, 1)
old_root = "setAttributeIfChanged(root, 'data-mcms-mobile-active', String(Boolean(mobileModeActive))); applyVisualViewportGeometry(root, tabletViewport);"
new_root = "setAttributeIfChanged(root, 'data-mcms-mobile-active', String(Boolean(mobileModeActive)));"
if text.count(old_root) != 1:
    raise SystemExit('Expected one root viewport geometry anchor')
text = text.replace(old_root, new_root, 1)
SOURCE.write_text(text, encoding='utf-8')
for path in (
    ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt',
):
    path.write_text(text, encoding='utf-8')
fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
fixture['candidateSourceSha256'] = 'b4bb8ccd7a1d8e2b211626c83236b63790ff3522e98a250e924cfa3a747cc113'
fixture['invariant'] = 'The reviewed compact stylesheet retains at least 500 recovered source lines while iOS/Safari viewport geometry remains isolated from root-attribute state updates and managed runtime budgets remain unchanged.'
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')
TEMP_WORKFLOW.unlink(missing_ok=True)
print('Separated iOS/Safari viewport geometry from root-attribute updates')
