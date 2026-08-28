#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
text=(ROOT/'src'/'MissionChief_Map_Command_Toolkit.user.js').read_text(encoding='utf-8')
required={
'visual viewport geometry':'function applyVisualViewportGeometry(',
'visual viewport stabilisation':'function scheduleVisualViewportStabilisation(',
'left visual offset':"'--mcms-visual-offset-left'",
'bottom visual gap':"'--mcms-visual-gap-bottom'",
'visual viewport height':"'--mcms-visual-height'",
'keyboard state':"'data-mcms-keyboard-open'",
'boot viewport refresh':"scheduleVisualViewportStabilisation('boot-viewport')",
'window focus recovery':"scheduleVisualViewportStabilisation('window-focus')",
'visual resize recovery':"scheduleVisualViewportStabilisation('visual-viewport-resize')",
'visual scroll recovery':"scheduleVisualViewportStabilisation('visual-viewport-scroll')",
'orientation recovery':"scheduleVisualViewportStabilisation('orientationchange')",
'mobile 44px pin':'height:44px!important;min-height:44px!important;scroll-snap-align:start',
'mobile seven-section navigation':'grid-template-columns:repeat(12,minmax(0,1fr))!important;',
'mobile balanced two-row navigation':'grid-template-rows:repeat(2,48px)!important;',
'mobile primary row spans':'grid-column:span 3!important;',
'mobile secondary row spans':'.mcms-tab-btn:nth-child(n+5){grid-column:span 4!important}',
'mobile 44px tab':'height:44px !important;\n            min-height:44px !important;',
'touch press feedback':'filter:brightness(1.16) saturate(1.06)!important;opacity:.88!important',
'visual bottom safe edge':'var(--mcms-visual-gap-bottom,0px)',
'visual right safe edge':'var(--mcms-visual-gap-right,0px)',
'single launcher mobile geometry':'height:44px !important;\n            min-height:44px !important;',
'tablet launcher geometry':'const menuWidth = 104;',
'mobile launcher accounting':"const launchSlotCount = control.querySelector('.mcms-economy-btn') ? 3 : 2;",
'44px pin floor':'let pinHeight = 44;',
'multi-frame WebKit settling':'delays=isTouchLayoutActive()?[0,80,220,420]:[0]',
'unmanaged timer budget protection':'pageWindow.setTimeout(()=>{if(runtime.destroyed||generation!==visualViewportRefreshGeneration)return'
}
missing=[name for name,token in required.items() if token not in text]
if missing: raise SystemExit('IOS SAFARI CONTRACT ERROR: missing '+', '.join(missing))
forbidden={
'38px mobile tabs':'height:38px !important; padding:0 4px !important;',
'38px critical controls':'mcms-critical-summary-card) { min-height:38px !important;',
'30px mobile pins':'let pinHeight = 30;',
'28px mobile fallback':'pinHeight = 28;',
'29px tablet fallback':'pinHeight = 29;'
}
present=[name for name,token in forbidden.items() if token in text]
if present: raise SystemExit('IOS SAFARI CONTRACT ERROR: '+', '.join(present))
for retired in ('mcms-mobile-more', 'mcms-mobile-nav', 'toggle-mobile-more', 'data-mobile-tab'):
    if retired in text: raise SystemExit('IOS SAFARI CONTRACT ERROR: blocking mobile navigation overlay returned: '+retired)
create=text[text.index('    function createControl(mapEl)'):text.index('    function commandSectionSlug(')]
if 'mcms-dock-toggle-btn' in create: raise SystemExit('IOS SAFARI CONTRACT ERROR: retired arrow launcher returned')
print('iOS/Safari usability contract passed')
