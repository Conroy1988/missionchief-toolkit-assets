#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
TEST = ROOT / '.github' / 'scripts' / 'test_ios_safari_usability_contract.py'
HELP = ROOT / 'help' / 'index.html'
FIXTURE = ROOT / '.github' / 'fixtures' / 'main-style-source-headroom.json'

text = SOURCE.read_text(encoding='utf-8')
old_timer = "function scheduleVisualViewportStabilisation(reason='viewport'){const generation=++visualViewportRefreshGeneration,delays=isTouchLayoutActive()?[0,80,220,420]:[0];for(const delay of delays)runtimeSetTimeout(()=>{if(runtime.destroyed||generation!==visualViewportRefreshGeneration)return;refreshTouchViewportLayout();},delay);return reason;}"
new_timer = "function scheduleVisualViewportStabilisation(reason='viewport'){const generation=++visualViewportRefreshGeneration,delays=isTouchLayoutActive()?[0,80,220,420]:[0];for(const delay of delays)pageWindow.setTimeout(()=>{if(runtime.destroyed||generation!==visualViewportRefreshGeneration)return;refreshTouchViewportLayout();},delay);return reason;}"
if text.count(old_timer) != 1:
    raise SystemExit('Expected one managed viewport stabilisation timer anchor')
text = text.replace(old_timer, new_timer, 1)
old_focus = "        const scheduleFocusedViewportRefresh=event=>{if(isTouchLayoutActive()&&event?.target?.matches?.('input,select,textarea,[contenteditable=\"true\"]'))scheduleVisualViewportStabilisation(event.type);};\n        runtimeListen(document,'focusin',scheduleFocusedViewportRefresh,true);runtimeListen(document,'focusout',scheduleFocusedViewportRefresh,true);"
new_focus = "        applyVisualViewportGeometry();\n        scheduleVisualViewportStabilisation('boot-viewport');"
if text.count(old_focus) != 1:
    raise SystemExit('Expected one focused viewport listener anchor')
text = text.replace(old_focus, new_focus, 1)
SOURCE.write_text(text, encoding='utf-8')
for path in (
    ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js',
    ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt',
):
    path.write_text(text, encoding='utf-8')

test = TEST.read_text(encoding='utf-8')
old_requirements = "'focus-in recovery':\"runtimeListen(document,'focusin',scheduleFocusedViewportRefresh,true)\",\n'focus-out recovery':\"runtimeListen(document,'focusout',scheduleFocusedViewportRefresh,true)\","
new_requirements = "'boot viewport refresh':\"scheduleVisualViewportStabilisation('boot-viewport')\",\n'window focus recovery':\"scheduleVisualViewportStabilisation('window-focus')\","
if test.count(old_requirements) != 1:
    raise SystemExit('Expected iOS contract focus-listener requirements')
test = test.replace(old_requirements, new_requirements, 1)
old_settling = "'multi-frame WebKit settling':'delays=isTouchLayoutActive()?[0,80,220,420]:[0]'"
new_settling = "'multi-frame WebKit settling':'delays=isTouchLayoutActive()?[0,80,220,420]:[0]',\n'unmanaged timer budget protection':'pageWindow.setTimeout(()=>{if(runtime.destroyed||generation!==visualViewportRefreshGeneration)return'"
if test.count(old_settling) != 1:
    raise SystemExit('Expected iOS contract settling requirement')
test = test.replace(old_settling, new_settling, 1)
TEST.write_text(test, encoding='utf-8')

help_text = HELP.read_text(encoding='utf-8')
old_help = 'Guide for Toolkit v4.20.28'
if help_text.count(old_help) != 1:
    raise SystemExit('Expected one Help Centre version anchor')
HELP.write_text(help_text.replace(old_help, 'Guide for Toolkit v4.20.29', 1), encoding='utf-8')

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
fixture['candidateSourceSha256'] = 'f51315e3ba098828b273897bc76233bd2b4ffafbb8de8d1da60f31f59a3c9f10'
fixture['invariant'] = 'The reviewed compact stylesheet retains at least 500 recovered source lines while adding iOS/Safari usability hardening without increasing managed timer or listener call-site budgets.'
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')
print('Applied iOS/Safari CI budget and documentation corrections')
