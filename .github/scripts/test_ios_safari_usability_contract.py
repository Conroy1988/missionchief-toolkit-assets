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
'focus-in recovery':"runtimeListen(document,'focusin',scheduleFocusedViewportRefresh,true)",
'focus-out recovery':"runtimeListen(document,'focusout',scheduleFocusedViewportRefresh,true)",
'visual resize recovery':"scheduleVisualViewportStabilisation('visual-viewport-resize')",
'visual scroll recovery':"scheduleVisualViewportStabilisation('visual-viewport-scroll')",
'orientation recovery':"scheduleVisualViewportStabilisation('orientationchange')",
'mobile 44px pin':'height:44px!important;min-height:44px!important;scroll-snap-align:start',
'mobile 44px tab':'min-width:88px!important;height:44px!important;min-height:44px!important',
'horizontal touch rail':'scroll-snap-type:x proximity!important',
'touch press feedback':'filter:brightness(1.16) saturate(1.06)!important;opacity:.88!important',
'visual bottom safe edge':'var(--mcms-visual-gap-bottom,0px)',
'visual right safe edge':'var(--mcms-visual-gap-right,0px)',
'full-height launcher toggle':'flex:0 0 44px!important;border-top:0!important',
'tablet launcher geometry':'const menuWidth = 145;',
'mobile launcher accounting':"const launchSlotCount = control.querySelector('.mcms-economy-btn') ? 3 : 2;",
'44px pin floor':'let pinHeight = 44;',
'multi-frame WebKit settling':'delays=isTouchLayoutActive()?[0,80,220,420]:[0]'
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
print('iOS/Safari usability contract passed')
