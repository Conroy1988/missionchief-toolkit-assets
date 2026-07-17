# Issue 92 label and responsive CSS audit

## Lines 2384-2392

```text
02384:             overflow: visible !important;
02385:             transform: none !important;
02386:         }
02387:         html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack .mcms-header,
02388:         html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-panel-sticky-stack .mcms-tabs {
02389:             flex: none !important;
02390:         }
02391:         html[data-mcms-device-layout="desktop"] body #${SCRIPT.panelId} > .mcms-tab-panel {
02392:             grid-row: 2 !important;
```

## Lines 2421-2431

```text
02421:             width: 24px !important; height: 24px !important; border: 0 !important; border-radius: 8px !important; background: rgba(255,255,255,.10) !important;
02422:             color: rgba(255,255,255,.88) !important; cursor: pointer !important; font-size: 15px !important; line-height: 24px !important; text-align: center !important; padding: 0 !important;
02423:         }
02424:         #${SCRIPT.panelId} .mcms-close:hover, #${SCRIPT.panelId} .mcms-reset-panel:hover, #${SCRIPT.panelId} .mcms-help-button:hover, #${SCRIPT.panelId} .mcms-help-button:focus-visible { background: rgba(58,174,232,.28) !important; color:#fff !important; }
02425:         #${SCRIPT.panelId} .mcms-tabs { display: grid !important; grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 5px !important; margin-bottom: 8px !important; }
02426:         #${SCRIPT.panelId} .mcms-tab-btn { height: 26px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 8px !important; background: rgba(255,255,255,.06) !important; color: rgba(255,255,255,.78) !important; cursor: pointer !important; font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important; padding: 0 !important; overflow: hidden !important; }
02427:         #${SCRIPT.panelId} .mcms-tab-btn.mcms-active, #${SCRIPT.panelId} .mcms-theme-btn.mcms-active, #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on, #${SCRIPT.panelId} .mcms-position-btn.mcms-active, #${SCRIPT.panelId} .mcms-pin-btn.mcms-on { background: rgba(25,118,210,.42) !important; border-color: rgba(120,190,255,.78) !important; color: #fff !important; }
02428:         #${SCRIPT.panelId} .mcms-tab-panel { display: none !important; }
02429:         #${SCRIPT.panelId} .mcms-tab-panel.mcms-active { display: block !important; }
02430:         #${SCRIPT.panelId} .mcms-grid-2 { display: grid !important; grid-template-columns: repeat(2, minmax(0,1fr)) !important; gap: 7px !important; width: 100% !important; min-width: 0 !important; overflow: hidden !important; }
02431:         #${SCRIPT.panelId} .mcms-theme-btn, #${SCRIPT.panelId} .mcms-toggle-btn, #${SCRIPT.panelId} .mcms-place-main {
```

## Lines 2435-2453

```text
02435:         }
02436:         #${SCRIPT.panelId} .mcms-theme-btn:hover, #${SCRIPT.panelId} .mcms-toggle-btn:hover, #${SCRIPT.panelId} .mcms-place-main:hover { background: rgba(255,255,255,.14) !important; border-color: rgba(255,255,255,.30) !important; }
02437:         #${SCRIPT.panelId} .mcms-iconbox { width: 20px !important; height: 20px !important; min-width: 20px !important; border-radius: 7px !important; background: rgba(255,255,255,.11) !important; display: flex !important; align-items: center !important; justify-content: center !important; color: rgba(255,255,255,.86) !important; font-size: 10px !important; line-height: 1 !important; font-weight: 900 !important; overflow: hidden !important; }
02438:         #${SCRIPT.panelId} .mcms-text { display: block !important; min-width: 0 !important; max-width: 100% !important; overflow: hidden !important; }
02439:         #${SCRIPT.panelId} .mcms-label { display: block !important; width: 100% !important; color: #f4f7ff !important; font-size: 10.5px !important; line-height: 1.05 !important; font-weight: 900 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
02440:         #${SCRIPT.panelId} .mcms-pill { display: inline-block !important; margin-top: 4px !important; max-width: 78px !important; padding: 1px 5px !important; border-radius: 999px !important; background: rgba(255,255,255,.13) !important; color: rgba(255,255,255,.82) !important; font-size: 7.5px !important; line-height: 1.05 !important; font-weight: 900 !important; white-space: nowrap !important; overflow: hidden !important; }
02441:         #${SCRIPT.panelId} .mcms-section-label { margin: 9px 0 6px 0 !important; color: rgba(233,238,245,.62) !important; font-size: 9px !important; line-height: 1 !important; font-weight: 900 !important; letter-spacing: .55px !important; text-transform: uppercase !important; }
02442:         #${SCRIPT.panelId} .mcms-row { display: grid !important; grid-template-columns: minmax(0,1fr) 100px !important; gap: 7px !important; align-items: center !important; margin-bottom: 7px !important; }
02443:         #${SCRIPT.panelId} .mcms-row-label { color: rgba(255,255,255,.82) !important; font-size: 10px !important; font-weight: 800 !important; overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; }
02444:         #${SCRIPT.panelId} .mcms-input, #${SCRIPT.panelId} .mcms-select { width: 100% !important; height: 27px !important; border: 1px solid rgba(255,255,255,.14) !important; border-radius: 8px !important; background: rgba(255,255,255,.08) !important; color: #fff !important; font-size: 10px !important; font-weight: 800 !important; padding: 0 7px !important; }
02445:         #${SCRIPT.panelId} .mcms-select option { color: #111 !important; }
02446:         #${SCRIPT.panelId} .mcms-position-grid, #${SCRIPT.panelId} .mcms-nudge-grid { display: grid !important; grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 6px !important; width: 100% !important; }
02447:         #${SCRIPT.panelId} .mcms-nudge-grid { grid-template-columns: repeat(5, minmax(0,1fr)) !important; }
02448:         #${SCRIPT.panelId} .mcms-position-btn, #${SCRIPT.panelId} .mcms-small-btn, #${SCRIPT.panelId} .mcms-bookmark-btn, #${SCRIPT.panelId} .mcms-pin-btn { width: 100% !important; min-width: 0 !important; height: 28px !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: 9px !important; background: rgba(255,255,255,.065) !important; color: rgba(255,255,255,.84) !important; cursor: pointer !important; font-size: 9px !important; line-height: 28px !important; font-weight: 900 !important; text-align: center !important; padding: 0 !important; overflow: hidden !important; }
02449:         #${SCRIPT.panelId} .mcms-position-btn:hover, #${SCRIPT.panelId} .mcms-small-btn:hover, #${SCRIPT.panelId} .mcms-bookmark-btn:hover, #${SCRIPT.panelId} .mcms-pin-btn:hover { background: rgba(255,255,255,.14) !important; }
02450:         #${SCRIPT.panelId} .mcms-quick-row { display: grid !important; grid-template-columns: minmax(0,1fr) 44px !important; gap: 6px !important; margin-bottom: 6px !important; }
02451:         #${SCRIPT.panelId} .mcms-bookmark-row { display: grid !important; grid-template-columns: minmax(0,1fr) 32px 38px 34px 26px !important; gap: 5px !important; align-items: center !important; margin-bottom: 5px !important; }
02452:         #${SCRIPT.panelId} .mcms-bookmark-name { color: rgba(255,255,255,.86) !important; font-size: 10px !important; font-weight: 850 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
02453:         #${SCRIPT.panelId} .mcms-status { margin-top: 8px !important; padding: 7px !important; border-radius: 9px !important; border: 1px solid rgba(255,255,255,.12) !important; background: rgba(255,255,255,.055) !important; color: rgba(255,255,255,.68) !important; font-size: 9px !important; line-height: 1.25 !important; }
```

## Lines 3673-3681

```text
03673:         #${SCRIPT.panelId}.mcms-map-small { width: 292px !important; }
03674:         #${SCRIPT.panelId}.mcms-map-small .mcms-grid-2 { gap: 6px !important; }
03675:         #${SCRIPT.panelId}.mcms-map-small .mcms-theme-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-toggle-btn, #${SCRIPT.panelId}.mcms-map-small .mcms-place-main { height: 40px !important; padding: 5px !important; grid-template-columns: 18px minmax(0,1fr) !important; gap: 5px !important; }
03676:         #${SCRIPT.panelId}.mcms-map-small .mcms-iconbox { width: 18px !important; height: 18px !important; min-width: 18px !important; font-size: 9px !important; }
03677:         #${SCRIPT.panelId}.mcms-map-small .mcms-label { font-size: 10px !important; }
03678:         #${SCRIPT.panelId}.mcms-map-small .mcms-footer { display: none !important; }
03679: 
03680: 
03681:         /* v3.3.0 Tablet Mode: map-aware responsive dock, unmistakable enabled states, fitted labels and bottom-sheet panel,
```

## Lines 3825-3838

```text
03825:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-help-button {
03826:             width: 44px !important; height: 44px !important; border-radius: 11px !important; font-size: 20px !important; line-height: 44px !important;
03827:         }
03828:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-close { font-size:24px !important; }
03829:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tabs {
03830:             position: sticky !important; top: 42px !important; z-index: 7 !important;
03831:             grid-template-columns: repeat(4, minmax(0,1fr)) !important; gap: 8px !important;
03832:             margin: 0 -4px 12px !important; padding: 8px 4px !important; background: rgba(8,12,18,.985) !important;
03833:         }
03834:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
03835:             height: 44px !important; border-radius: 11px !important; font-size: 11.5px !important; padding: 0 6px !important;
03836:         }
03837:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap: 9px !important; }
03838:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
```

## Lines 3844-3867

```text
03844:         }
03845:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-iconbox {
03846:             width: 30px !important; height: 30px !important; min-width: 30px !important; border-radius: 9px !important; font-size: 13px !important;
03847:         }
03848:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-label { font-size: 12.5px !important; line-height: 1.15 !important; }
03849:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top: 5px !important; max-width: 120px !important; padding: 3px 7px !important; font-size: 9px !important; }
03850:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin: 14px 0 8px !important; font-size: 10.5px !important; letter-spacing: .8px !important; }
03851:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row {
03852:             grid-template-columns: minmax(0,1fr) minmax(170px, 42%) !important; gap: 10px !important; margin-bottom: 10px !important;
03853:         }
03854:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 120px minmax(0,1fr) !important; }
03855:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size: 12px !important; }
03856:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-input,
03857:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-select {
03858:             height: 44px !important; border-radius: 10px !important; padding: 0 11px !important; font-size: 13px !important;
03859:         }
03860:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
03861:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap: 8px !important; }
03862:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
03863:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
03864:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
03865:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-pin-btn {
03866:             min-height: 44px !important; height: 44px !important; border-radius: 10px !important;
03867:             font-size: 11.5px !important; line-height: 44px !important; padding: 0 8px !important;
```

## Lines 3915-3923

```text
03915:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns: 1fr !important; }
03916:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-grid-2 [data-toggle="criticalView"] { grid-column: auto !important; }
03917:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row,
03918:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns: 1fr !important; }
03919:             html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-row-label { white-space: normal !important; }
03920:         }
03921: 
03922: 
03923:         /* v3.3.1 iOS Safari Mobile Mode: map-aware command grid, safe-area bottom sheet,
```

## Lines 4040-4050

```text
04040:             box-shadow:0 -12px 38px rgba(0,0,0,.58),inset 0 1px rgba(255,255,255,.06) !important;
04041:             backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
04042:         }
04043:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId}::-webkit-scrollbar,
04044:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs::-webkit-scrollbar { display:none !important; width:0 !important; height:0 !important; }
04045:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId},
04046:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { scrollbar-width:none !important; }
04047:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header {
04048:             position:sticky !important; top:-8px !important; z-index:8 !important; min-height:48px !important; margin:-8px -8px 7px !important;
04049:             grid-template-columns:minmax(0,1fr) 44px 44px !important; gap:6px !important;
04050:             padding:8px 8px 6px !important; border-radius:16px 16px 0 0 !important; background:rgba(7,11,17,.985) !important;
```

## Lines 4055-4089

```text
04055:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { margin-top:3px !important; font-size:9px !important; }
04056:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-reset-panel { display:none !important; }
04057:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-close,
04058:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-help-button { width:44px !important; height:44px !important; border-radius:12px !important; font-size:20px !important; line-height:42px !important; }
04059:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs {
04060:             position:sticky !important; top:40px !important; z-index:7 !important; display:flex !important; gap:5px !important;
04061:             margin:0 -2px 7px !important; padding:2px 2px 6px !important; overflow-x:auto !important; overflow-y:hidden !important;
04062:             overscroll-behavior-x:contain !important; -webkit-overflow-scrolling:touch !important; background:rgba(6,10,15,.96) !important;
04063:         }
04064:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn {
04065:             flex:0 0 auto !important; min-width:74px !important; height:40px !important; padding:0 10px !important; border-radius:10px !important;
04066:             font-size:10px !important; line-height:1 !important;
04067:         }
04068:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { gap:6px !important; }
04069:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
04070:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
04071:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-place-main { min-height:48px !important; height:auto !important; padding:7px !important; border-radius:11px !important; }
04072:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-iconbox { width:22px !important; height:22px !important; min-width:22px !important; }
04073:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-label { font-size:11px !important; }
04074:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pill { margin-top:4px !important; max-width:110px !important; font-size:8px !important; }
04075:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-section-label { margin:12px 0 7px !important; font-size:9.5px !important; }
04076:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:minmax(0,1fr) minmax(132px,44%) !important; gap:7px !important; margin-bottom:7px !important; }
04077:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { font-size:10.5px !important; white-space:normal !important; }
04078:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-input,
04079:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-select {
04080:             min-height:44px !important; height:44px !important; border-radius:10px !important; padding:0 9px !important;
04081:             font-size:16px !important; line-height:1.2 !important;
04082:         }
04083:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} input[type="range"].mcms-input { min-height:44px !important; }
04084:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-btn,
04085:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-small-btn,
04086:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-btn,
04087:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-pin-btn { min-height:44px !important; height:44px !important; line-height:42px !important; border-radius:10px !important; font-size:10px !important; }
04088:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-position-grid,
04089:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-nudge-grid { gap:6px !important; }
```

## Lines 4121-4137

```text
04121:         }
04122:         @media (max-width: 430px) {
04123:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
04124:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row { grid-template-columns:1fr !important; }
04125:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-row-label { margin-bottom:-2px !important; }
04126:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-bookmark-row { grid-template-columns:minmax(0,1fr) repeat(4,40px) !important; }
04127:         }
04128:         @media (orientation: landscape) and (max-height: 500px) {
04129:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} { border-radius:12px !important; padding-top:6px !important; }
04130:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header { min-height:42px !important; padding-top:5px !important; }
04131:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-subtitle { display:none !important; }
04132:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { top:34px !important; }
04133:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn { height:36px !important; }
04134:         }
04135: 
04136:         /* v3.4.2: collapse after the exit animation and override later tablet/mobile layout rules. */
04137:         #${SCRIPT.controlId} {
```

## Lines 4229-4237

```text
04229:         #${SCRIPT.panelId} .mcms-profile-main strong,#${SCRIPT.panelId} .mcms-profile-main span { display:block !important; min-width:0 !important; overflow:hidden !important; white-space:nowrap !important; text-overflow:ellipsis !important; }
04230:         #${SCRIPT.panelId} .mcms-profile-main strong { color:#edf4fb !important; font-size:9px !important; }
04231:         #${SCRIPT.panelId} .mcms-profile-main span { color:#8393a5 !important; font-size:7px !important; margin-top:2px !important; }
04232:         #${SCRIPT.panelId} .mcms-config-actions { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)) !important; gap:5px !important; }
04233:         #${SCRIPT.panelId} .mcms-config-actions .mcms-small-btn { min-width:0 !important; white-space:nowrap !important; text-overflow:ellipsis !important; }
04234:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
04235:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-config-actions [data-action="reset-config"] { grid-column:1 / -1 !important; }
04236:         #${SCRIPT.panelId} .mcms-hidden-file { display:none !important; }
04237: 
```

## Lines 4580-4616

```text
04580:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-close:hover {
04581:             background: var(--mcms-cp-red) !important;
04582:             color: #fff !important;
04583:         }
04584:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tabs {
04585:             gap: 4px !important;
04586:             border-bottom: 1px solid rgba(0,240,255,.20) !important;
04587:             padding-bottom: 7px !important;
04588:         }
04589:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn {
04590:             position: relative !important;
04591:             border: 1px solid rgba(0,240,255,.34) !important;
04592:             border-radius: 0 !important;
04593:             background: rgba(0,240,255,.045) !important;
04594:             color: #9fdce0 !important;
04595:             letter-spacing: .55px !important;
04596:             clip-path: polygon(0 0, calc(100% - 5px) 0, 100% 5px, 100% 100%, 0 100%) !important;
04597:         }
04598:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn:hover {
04599:             border-color: var(--mcms-cp-cyan) !important;
04600:             color: #fff !important;
04601:             background: rgba(0,240,255,.12) !important;
04602:         }
04603:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
04604:             border-color: var(--mcms-cp-yellow) !important;
04605:             background: var(--mcms-cp-yellow) !important;
04606:             color: var(--mcms-cp-ink) !important;
04607:             box-shadow: inset 0 -3px 0 var(--mcms-cp-red), 0 0 10px rgba(252,238,10,.20) !important;
04608:         }
04609:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
04610:             animation: mcmsCyberTabIn 150ms steps(3,end) both !important;
04611:         }
04612:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-section-label {
04613:             position: relative !important;
04614:             margin-top: 11px !important;
04615:             padding: 5px 7px 5px 16px !important;
04616:             border: 0 !important;
```

## Lines 4621-4629

```text
04621:             font-weight: 1000 !important;
04622:             letter-spacing: 1px !important;
04623:             text-transform: uppercase !important;
04624:         }
04625:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-section-label::before {
04626:             content: '' !important;
04627:             position: absolute !important;
04628:             left: 4px !important;
04629:             top: 7px !important;
```

## Lines 4636-4644

```text
04636:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn,
04637:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn,
04638:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-place-main,
04639:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-position-btn,
04640:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-small-btn,
04641:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-bookmark-btn,
04642:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-pin-btn,
04643:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
04644:             border-color: rgba(0,240,255,.38) !important;
```

## Lines 4651-4659

```text
04651:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
04652:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
04653:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-place-main:hover,
04654:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-position-btn:hover,
04655:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-small-btn:hover,
04656:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-bookmark-btn:hover,
04657:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-pin-btn:hover,
04658:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
04659:             border-color: var(--mcms-cp-yellow) !important;
```

## Lines 4691-4699

```text
04691:             background: rgba(252,238,10,.07) !important;
04692:             color: var(--mcms-cp-yellow) !important;
04693:             letter-spacing: .5px !important;
04694:         }
04695:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-row-label,
04696:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-bookmark-name,
04697:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-title,
04698:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main strong {
04699:             color: #d8edef !important;
```

## Lines 4837-4846

```text
04837:             --mcms-cp-muted: #b7c9cf;
04838:             --mcms-cp-soft: #d8e7ea;
04839:             --mcms-cp-ink: #05070b;
04840:         }
04841:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-label,
04842:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-row-label,
04843:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-bookmark-name,
04844:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ops-entry-title,
04845:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-profile-main strong,
04846:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-sweep-title,
```

## Lines 4898-4916

```text
04898:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label,
04899:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-desktop,
04900:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-tablet,
04901:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-mobile,
04902:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-label,
04903:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-text,
04904:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-label,
04905:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-text,
04906:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy strong,
04907:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy small {
04908:             color: var(--mcms-cp-ink) !important;
04909:             text-shadow: none !important;
04910:         }
04911:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-label,
04912:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-label,
04913:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy strong {
04914:             font-weight: 1000 !important;
04915:         }
04916:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy small {
```

## Lines 4945-4953

```text
04945:             text-shadow: none !important;
04946:             cursor: not-allowed !important;
04947:             animation: none !important;
04948:         }
04949:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled .mcms-label,
04950:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled .mcms-text,
04951:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled strong,
04952:         html[data-mcms-ui-theme="cyberpunk"] #${SCRIPT.panelId} button:disabled small {
04953:             color: #9dafb5 !important;
```

## Lines 5190-5218

```text
05190:             text-shadow: none !important;
05191:         }
05192: 
05193:         /* Tabs and section navigation. */
05194:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tabs {
05195:             gap: 4px !important;
05196:             padding: 0 1px 7px 1px !important;
05197:             border-bottom: 1px solid rgba(185,255,114,.24) !important;
05198:         }
05199:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-btn {
05200:             border: 1px solid #405b38 !important;
05201:             border-radius: 3px !important;
05202:             background: linear-gradient(180deg, #162318, #0a130c) !important;
05203:             color: #cfe8bc !important;
05204:             letter-spacing: .25px !important;
05205:             box-shadow: inset 0 1px rgba(222,255,201,.045) !important;
05206:             text-shadow: 0 0 4px rgba(185,255,114,.16) !important;
05207:         }
05208:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-btn:hover,
05209:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-btn:focus-visible {
05210:             border-color: var(--mcms-fo-green-mid) !important;
05211:             background: #243a22 !important;
05212:             color: #f0ffe4 !important;
05213:         }
05214:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
05215:             border-color: var(--mcms-fo-green-strong) !important;
05216:             background: var(--mcms-fo-green-strong) !important;
05217:             color: var(--mcms-fo-ink) !important;
05218:             text-shadow: none !important;
```

## Lines 5220-5228

```text
05220:         }
05221:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
05222:             animation: mcmsFalloutDataIn 190ms steps(4,end) both !important;
05223:         }
05224:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-section-label {
05225:             position: relative !important;
05226:             margin: 11px 0 6px 0 !important;
05227:             padding: 5px 8px 5px 18px !important;
05228:             border: 1px solid rgba(118,171,82,.34) !important;
```

## Lines 5235-5243

```text
05235:             letter-spacing: .7px !important;
05236:             text-transform: uppercase !important;
05237:             text-shadow: 0 0 5px rgba(185,255,114,.25) !important;
05238:         }
05239:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-section-label::before {
05240:             content: '▸' !important;
05241:             position: absolute !important;
05242:             left: 6px !important;
05243:             top: 4px !important;
```

## Lines 5249-5257

```text
05249:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-theme-btn,
05250:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-toggle-btn,
05251:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-place-main,
05252:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-position-btn,
05253:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-small-btn,
05254:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-bookmark-btn,
05255:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-pin-btn,
05256:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
05257:             border: 1px solid #45643c !important;
```

## Lines 5266-5274

```text
05266:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
05267:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
05268:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-place-main:hover,
05269:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-position-btn:hover,
05270:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-small-btn:hover,
05271:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-bookmark-btn:hover,
05272:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-pin-btn:hover,
05273:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
05274:             border-color: var(--mcms-fo-green-mid) !important;
```

## Lines 5309-5318

```text
05309:             background: rgba(255,211,106,.07) !important;
05310:             color: #ffe2a0 !important;
05311:             letter-spacing: .45px !important;
05312:         }
05313:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-label,
05314:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-row-label,
05315:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-bookmark-name,
05316:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ops-entry-title,
05317:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-profile-main strong,
05318:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-sweep-title,
```

## Lines 5584-5594

```text
05584:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label,
05585:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-desktop,
05586:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-tablet,
05587:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-mobile,
05588:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-label,
05589:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-text,
05590:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-label,
05591:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-text,
05592:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy strong,
05593:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy small {
05594:             color: var(--mcms-fo-ink) !important;
```

## Lines 5630-5638

```text
05630:             text-shadow: none !important;
05631:             cursor: not-allowed !important;
05632:             animation: none !important;
05633:         }
05634:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} button:disabled .mcms-label,
05635:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} button:disabled .mcms-text,
05636:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} button:disabled strong,
05637:         html[data-mcms-ui-theme="fallout4"] #${SCRIPT.panelId} button:disabled small {
05638:             color: #a9b7a1 !important;
```

## Lines 5912-5940

```text
05912:             text-shadow: none !important;
05913:         }
05914: 
05915:         /* Tabs and section navigation. */
05916:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tabs {
05917:             gap: 4px !important;
05918:             padding: 0 1px 7px 1px !important;
05919:             border-bottom: 1px solid rgba(216,25,63,.24) !important;
05920:         }
05921:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn {
05922:             border: 1px solid #424852 !important;
05923:             border-radius: 3px !important;
05924:             background: linear-gradient(180deg, #191d24, #0e1117) !important;
05925:             color: #dfe3e8 !important;
05926:             letter-spacing: .25px !important;
05927:             box-shadow: inset 0 1px rgba(255,255,255,.045) !important;
05928:             text-shadow: 0 0 4px rgba(216,25,63,.16) !important;
05929:         }
05930:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn:hover,
05931:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn:focus-visible {
05932:             border-color: var(--mcms-um-red) !important;
05933:             background: #2b3039 !important;
05934:             color: #ffffff !important;
05935:         }
05936:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
05937:             border-color: var(--mcms-um-white-strong) !important;
05938:             background: var(--mcms-um-white-strong) !important;
05939:             color: var(--mcms-um-ink) !important;
05940:             text-shadow: none !important;
```

## Lines 5942-5950

```text
05942:         }
05943:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
05944:             animation: mcmsUmbrellaDataIn 190ms steps(4,end) both !important;
05945:         }
05946:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label {
05947:             position: relative !important;
05948:             margin: 11px 0 6px 0 !important;
05949:             padding: 5px 8px 5px 18px !important;
05950:             border: 1px solid rgba(118,171,82,.34) !important;
```

## Lines 5957-5965

```text
05957:             letter-spacing: .7px !important;
05958:             text-transform: uppercase !important;
05959:             text-shadow: 0 0 5px rgba(216,25,63,.25) !important;
05960:         }
05961:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label::before {
05962:             content: '▸' !important;
05963:             position: absolute !important;
05964:             left: 6px !important;
05965:             top: 4px !important;
```

## Lines 5971-5979

```text
05971:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn,
05972:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-toggle-btn,
05973:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-place-main,
05974:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-position-btn,
05975:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-small-btn,
05976:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-bookmark-btn,
05977:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-pin-btn,
05978:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
05979:             border: 1px solid #45643c !important;
```

## Lines 5988-5996

```text
05988:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
05989:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
05990:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-place-main:hover,
05991:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-position-btn:hover,
05992:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-small-btn:hover,
05993:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-bookmark-btn:hover,
05994:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-pin-btn:hover,
05995:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
05996:             border-color: var(--mcms-um-red) !important;
```

## Lines 6031-6040

```text
06031:             background: rgba(255,211,106,.07) !important;
06032:             color: #ffe49a !important;
06033:             letter-spacing: .45px !important;
06034:         }
06035:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-label,
06036:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-row-label,
06037:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-bookmark-name,
06038:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-title,
06039:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main strong,
06040:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-sweep-title,
```

## Lines 6306-6316

```text
06306:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label,
06307:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-desktop,
06308:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-tablet,
06309:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-mobile,
06310:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-label,
06311:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-text,
06312:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-label,
06313:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-text,
06314:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy strong,
06315:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-btn.mcms-active .mcms-ui-theme-copy small {
06316:             color: var(--mcms-um-ink) !important;
```

## Lines 6352-6360

```text
06352:             text-shadow: none !important;
06353:             cursor: not-allowed !important;
06354:             animation: none !important;
06355:         }
06356:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} button:disabled .mcms-label,
06357:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} button:disabled .mcms-text,
06358:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} button:disabled strong,
06359:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} button:disabled small {
06360:             color: #b7bdc6 !important;
```

## Lines 6539-6574

```text
06539:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-subtitle {
06540:             color: #d3d8df !important;
06541:             text-shadow: none !important;
06542:         }
06543:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tabs {
06544:             gap: 3px !important;
06545:             border-bottom: 1px solid #646b75 !important;
06546:         }
06547:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn {
06548:             border-radius: 1px !important;
06549:             border-color: #555c66 !important;
06550:             background: linear-gradient(180deg, #252932, #11141a) !important;
06551:             color: #e8ebef !important;
06552:             text-shadow: none !important;
06553:             clip-path: polygon(0 0, calc(100% - 5px) 0, 100% 5px, 100% 100%, 0 100%) !important;
06554:         }
06555:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn:hover,
06556:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn:focus-visible {
06557:             border-color: #ffffff !important;
06558:             background: #363b45 !important;
06559:             color: #ffffff !important;
06560:         }
06561:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
06562:             border-color: #8e0c28 !important;
06563:             background: linear-gradient(180deg, #d81d43, #a10d2d) !important;
06564:             color: #ffffff !important;
06565:             box-shadow: inset 0 -3px 0 #ffffff, 0 0 9px rgba(216,25,63,.20) !important;
06566:         }
06567:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
06568:             animation: mcmsUmbrellaRecordIn 180ms ease-out both !important;
06569:         }
06570:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label {
06571:             min-height: 24px !important;
06572:             padding: 5px 8px 5px 23px !important;
06573:             border: 1px solid #aeb4bd !important;
06574:             border-left: 6px solid #c8102e !important;
```

## Lines 6581-6589

```text
06581:             text-shadow: none !important;
06582:             box-shadow: inset 0 -1px rgba(0,0,0,.10) !important;
06583:             clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 0 100%) !important;
06584:         }
06585:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label::before {
06586:             content: '☣' !important;
06587:             left: 7px !important;
06588:             color: #a60d2c !important;
06589:             font-size: 11px !important;
```

## Lines 6593-6601

```text
06593:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn,
06594:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-toggle-btn,
06595:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-place-main,
06596:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-position-btn,
06597:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-small-btn,
06598:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main,
06599:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
06600:             border-radius: 1px !important;
06601:             border-color: #555c66 !important;
```

## Lines 6608-6616

```text
06608:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
06609:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
06610:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-place-main:hover,
06611:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-position-btn:hover,
06612:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-small-btn:hover,
06613:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
06614:             border-color: #ffffff !important;
06615:             background: #343943 !important;
06616:             color: #ffffff !important;
```

## Lines 6784-6794

```text
06784:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label,
06785:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-desktop,
06786:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-tablet,
06787:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on .mcms-float-label-mobile,
06788:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-label,
06789:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-theme-btn.mcms-active .mcms-text,
06790:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-label,
06791:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-toggle-btn.mcms-on .mcms-text {
06792:             color: #ffffff !important;
06793:             text-shadow: none !important;
06794:         }
```

## Lines 7108-7135

```text
07108:             color: var(--mcms-fac-ink) !important;
07109:             text-shadow: none !important;
07110:         }
07111: 
07112:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tabs {
07113:             gap: 3px !important;
07114:             padding: 4px !important;
07115:             border-bottom: 1px solid #4d5048 !important;
07116:             background: #181a17 !important;
07117:         }
07118:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-btn {
07119:             border: 1px solid #494c45 !important;
07120:             border-radius: 2px !important;
07121:             background: linear-gradient(180deg, #343731, #222420) !important;
07122:             color: #d5c49d !important;
07123:             box-shadow: inset 0 1px rgba(255,255,255,.05) !important;
07124:         }
07125:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-btn:hover,
07126:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-btn:focus-visible {
07127:             border-color: #bd6b2a !important;
07128:             color: #f4d7a1 !important;
07129:             background: linear-gradient(180deg, #47453e, #2b2923) !important;
07130:         }
07131:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
07132:             border-color: #f0aa5a !important;
07133:             background: linear-gradient(180deg, #f0a04b, #cb6d28) !important;
07134:             color: var(--mcms-fac-ink) !important;
07135:             box-shadow: inset 0 1px rgba(255,255,255,.28), inset 0 -4px 8px rgba(96,40,9,.18) !important;
```

## Lines 7137-7145

```text
07137:         }
07138:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active {
07139:             animation: mcmsFactorioRecordIn 190ms ease-out both !important;
07140:         }
07141:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-section-label {
07142:             position: relative !important;
07143:             min-height: 25px !important;
07144:             padding: 7px 10px 6px 28px !important;
07145:             border: 1px solid #5b5e56 !important;
```

## Lines 7154-7162

```text
07154:             letter-spacing: .8px !important;
07155:             text-transform: uppercase !important;
07156:             box-shadow: inset 0 1px rgba(255,255,255,.06) !important;
07157:         }
07158:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-section-label::before {
07159:             content: "⚙" !important;
07160:             position: absolute !important;
07161:             left: 8px !important;
07162:             top: 50% !important;
```

## Lines 7168-7176

```text
07168:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-theme-btn,
07169:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-toggle-btn,
07170:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-place-main,
07171:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-position-btn,
07172:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-small-btn,
07173:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-bookmark-btn,
07174:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-pin-btn,
07175:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
07176:             border: 1px solid #55584f !important;
```

## Lines 7184-7192

```text
07184:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
07185:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
07186:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-place-main:hover,
07187:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-position-btn:hover,
07188:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-small-btn:hover,
07189:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-bookmark-btn:hover,
07190:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-pin-btn:hover,
07191:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
07192:             border-color: #d27a2c !important;
```

## Lines 7315-7323

```text
07315:             border-color: #9c5a26 !important;
07316:             background: linear-gradient(145deg, #3e392f, #24231e) !important;
07317:             color: #f0d6a1 !important;
07318:         }
07319:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-row-label,
07320:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-bookmark-name,
07321:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-entry-title,
07322:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-profile-main strong,
07323:         html[data-mcms-ui-theme="factorio"] #${SCRIPT.panelId} .mcms-ops-stat-value,
```

## Lines 10264-10303

```text
10264:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-reset-panel:hover {
10265:             border-color:#d5b85f !important;
10266:             color:#f0d47f !important;
10267:         }
10268:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tabs {
10269:             gap:4px !important;
10270:             border-bottom:1px solid rgba(255,255,255,.055) !important;
10271:             padding-bottom:6px !important;
10272:         }
10273:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn {
10274:             border:1px solid #44494f !important;
10275:             border-radius:1px !important;
10276:             background:linear-gradient(180deg,#282b30,#121417) !important;
10277:             color:#c8c9c7 !important;
10278:             letter-spacing:.35px !important;
10279:         }
10280:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn:hover {
10281:             border-color:#a98e48 !important;
10282:             color:#f0d47e !important;
10283:         }
10284:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
10285:             border-color:#e3c875 !important;
10286:             background:linear-gradient(180deg,#e9dfc5,#c8b98e) !important;
10287:             color:#111214 !important;
10288:             box-shadow:0 0 11px rgba(210,181,95,.18) !important;
10289:         }
10290:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label {
10291:             position:relative !important;
10292:             padding:5px 7px 5px 21px !important;
10293:             border-left:2px solid #a71924 !important;
10294:             border-bottom:1px solid rgba(200,170,91,.28) !important;
10295:             background:linear-gradient(90deg,rgba(200,170,91,.09),transparent 72%) !important;
10296:             color:#e2c778 !important;
10297:             letter-spacing:1px !important;
10298:         }
10299:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label::before {
10300:             content:"◉" !important;
10301:             position:absolute !important;
10302:             left:7px !important;
10303:             top:50% !important;
```

## Lines 10309-10317

```text
10309:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-theme-btn,
10310:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-toggle-btn,
10311:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-place-main,
10312:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-position-btn,
10313:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-small-btn,
10314:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-bookmark-btn,
10315:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-pin-btn,
10316:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
10317:             border:1px solid #4c5157 !important;
```

## Lines 10323-10331

```text
10323:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
10324:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
10325:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-place-main:hover,
10326:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-position-btn:hover,
10327:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-small-btn:hover,
10328:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-bookmark-btn:hover,
10329:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-pin-btn:hover,
10330:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
10331:             border-color:#c7a856 !important;
```

## Lines 10760-10768

```text
10760:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-place-main.mcms-active .mcms-pill * {
10761:             color:#f2ead7 !important;
10762:             text-shadow:none !important;
10763:         }
10764:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-row-label,
10765:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-check-label,
10766:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-help,
10767:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-note {
10768:             color:#d9d4c9 !important;
```

## Lines 11375-11388

```text
11375:             text-overflow:ellipsis !important;
11376:             white-space:nowrap !important;
11377:         }
11378: 
11379:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label {
11380:             position:relative !important;
11381:             padding-right:29px !important;
11382:             overflow:hidden !important;
11383:         }
11384:         html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-section-label::after {
11385:             content:"" !important;
11386:             position:absolute !important;
11387:             right:6px !important;
11388:             top:50% !important;
```

## Lines 11836-11844

```text
11836:             margin:0 -12px !important;
11837:             padding:10px 12px 9px !important;
11838:             border-bottom:1px solid rgba(255,255,255,.12) !important;
11839:         }
11840:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} .mcms-panel-sticky-stack .mcms-tabs {
11841:             position:relative !important;
11842:             top:auto !important;
11843:             z-index:1 !important;
11844:             margin:0 -4px !important;
```

## Lines 12027-12035

```text
12027:         #${SCRIPT.controlId} *, #${SCRIPT.panelId} *, #${SCRIPT.criticalDrawerId} *, #${SCRIPT.vehicleStatusId} *,
12028:         #${SCRIPT.majorIncidentFeedId} *, #${SCRIPT.missionInspectorId} *, #${SCRIPT.helpCenterId} * { box-sizing:border-box !important; }
12029:         #${SCRIPT.panelId} :is(.mcms-grid-2,.mcms-row,.mcms-ui-theme-grid,.mcms-profile-row,.mcms-bookmark-row,.mcms-quick-row,.mcms-finance-vault-summary) > *,
12030:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-values-grid,.mcms-critical-type-filters,.mcms-critical-category-filters,.mcms-critical-summary,.mcms-critical-unit-grid) > * { min-width:0 !important; max-width:100% !important; }
12031:         #${SCRIPT.panelId} :is(.mcms-status,.mcms-footer,.mcms-subtitle,.mcms-row-label,.mcms-profile-main,.mcms-bookmark-name,.mcms-ui-theme-copy,.mcms-text),
12032:         #${SCRIPT.criticalDrawerId} :is(.mcms-critical-state-copy,.mcms-critical-location,.mcms-critical-meta,.mcms-critical-list-footer),
12033:         #${SCRIPT.vehicleStatusId} :is(.mcms-vehicle-status-title,.mcms-vehicle-status-body) { overflow-wrap:anywhere !important; word-break:normal !important; }
12034:         #${SCRIPT.panelId}, #${SCRIPT.criticalDrawerId}, #${SCRIPT.vehicleStatusId}, #${SCRIPT.helpCenterId} { overscroll-behavior:contain !important; scrollbar-gutter:stable both-edges; }
12035:         #${SCRIPT.controlId} :is(button,[tabindex]), #${SCRIPT.panelId} :is(button,input,select,[tabindex]),
```

## Lines 12049-12065

```text
12049:         }
12050:         html:not([data-mcms-tablet-active="true"]):not([data-mcms-mobile-active="true"]) #${SCRIPT.panelId} :is(.mcms-reset-panel,.mcms-help-button,.mcms-close) { width:32px !important; height:32px !important; min-width:32px !important; }
12051:         #${SCRIPT.panelId} .mcms-title { min-width:0 !important; white-space:normal !important; font-size:11px !important; line-height:1.15 !important; }
12052:         #${SCRIPT.panelId} .mcms-subtitle { white-space:normal !important; font-size:9px !important; line-height:1.25 !important; }
12053:         #${SCRIPT.panelId} .mcms-tabs { min-width:0 !important; }
12054:         #${SCRIPT.panelId} .mcms-tab-btn { min-width:0 !important; overflow:hidden !important; text-overflow:ellipsis !important; font-size:9px !important; }
12055:         #${SCRIPT.panelId} .mcms-tab-panel[hidden] { display:none !important; }
12056:         #${SCRIPT.panelId} .mcms-section-label { font-size:9.5px !important; line-height:1.25 !important; }
12057:         #${SCRIPT.panelId} .mcms-status { font-size:9.5px !important; line-height:1.42 !important; }
12058:         #${SCRIPT.panelId} .mcms-row-label { font-size:10px !important; line-height:1.3 !important; }
12059:         #${SCRIPT.panelId} :is(.mcms-label,.mcms-bookmark-name,.mcms-profile-main strong,.mcms-ui-theme-copy strong) { font-size:10.5px !important; line-height:1.2 !important; }
12060:         #${SCRIPT.panelId} :is(.mcms-pill,.mcms-heat-key,.mcms-ui-theme-copy small,.mcms-profile-main span,.mcms-build) { font-size:8.5px !important; line-height:1.25 !important; }
12061:         #${SCRIPT.panelId} :is(.mcms-input,.mcms-select,.mcms-small-btn,.mcms-position-btn,.mcms-bookmark-btn,.mcms-pin-btn) { min-height:32px !important; }
12062:         #${SCRIPT.panelId} .mcms-footer { gap:4px !important; font-size:9px !important; line-height:1.35 !important; }
12063:         #${SCRIPT.panelId} .mcms-discord-wide { grid-template-columns:minmax(96px,35%) minmax(0,1fr) !important; }
12064:         #${SCRIPT.panelId} .mcms-finance-vault-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; gap:7px !important; }
12065: 
```

## Lines 12087-12106

```text
12087:         #${SCRIPT.majorIncidentFeedId} :is(.mcms-major-feed-track,.mcms-major-feed-item,.mcms-major-feed-copy) { min-width:0 !important; }
12088:         #${SCRIPT.majorIncidentFeedId} .mcms-major-feed-copy { overflow:hidden !important; text-overflow:ellipsis !important; white-space:nowrap !important; }
12089: 
12090:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} :is(.mcms-pill,.mcms-heat-key,.mcms-ui-theme-copy small,.mcms-profile-main span,.mcms-build) { font-size:9.5px !important; }
12091:         html[data-mcms-tablet-active="true"] #${SCRIPT.panelId} :is(.mcms-status,.mcms-row-label) { font-size:11px !important; }
12092:         html[data-mcms-tablet-active="true"] #${SCRIPT.criticalDrawerId} :is(.mcms-critical-values-label,.mcms-critical-type-label,.mcms-critical-category-label,.mcms-critical-value-mode,.mcms-critical-unit-extra) { font-size:8.5px !important; }
12093: 
12094:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs {
12095:             top:40px !important; display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important;
12096:             gap:5px !important; overflow:visible !important; padding:3px 2px 7px !important;
12097:         }
12098:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tab-btn { width:100% !important; min-width:0 !important; height:38px !important; padding:0 4px !important; font-size:9.5px !important; }
12099:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-panel-sticky-stack { position:sticky !important; top:-8px !important; z-index:9 !important; background:rgba(6,10,15,.985) !important; }
12100:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-header { position:relative !important; top:auto !important; margin:-8px -8px 5px !important; }
12101:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} :is(.mcms-pill,.mcms-heat-key,.mcms-ui-theme-copy small,.mcms-profile-main span,.mcms-build) { font-size:9px !important; }
12102:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} :is(.mcms-status,.mcms-row-label) { font-size:10px !important; }
12103:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-grid-2 { align-items:stretch !important; }
12104:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-theme-btn,
12105:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-toggle-btn,
12106:         html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-ui-theme-btn { min-width:0 !important; overflow:hidden !important; }
```

## Lines 12114-12122

```text
12114:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
12115:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} :is(.mcms-critical-values-label,.mcms-critical-type-label,.mcms-critical-category-label,.mcms-critical-value-mode,.mcms-critical-unit-extra,.mcms-critical-refreshed,.mcms-critical-showing) { font-size:8.5px !important; }
12116:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} :is(button,.mcms-critical-filter,.mcms-critical-type-filter,.mcms-critical-category-filter,.mcms-critical-summary-card) { min-height:38px !important; }
12117:         @media (max-width:380px) {
12118:             html[data-mcms-mobile-active="true"] #${SCRIPT.panelId} .mcms-tabs { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
12119:             html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-values-grid,
12120:             html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-category-filters,
12121:             html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:1fr !important; }
12122:         }
```

## Lines 12124-12142

```text
12124:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-tab-panel { width:100% !important; max-width:100% !important; overflow-x:hidden !important; }
12125:         html[data-mcms-ui-theme] #${SCRIPT.panelId} :is(.mcms-help-button,.mcms-close,.mcms-reset-panel) {
12126:             display:grid !important; place-items:center !important; line-height:1 !important; padding:0 !important;
12127:         }
12128:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-section-label { font-size:9.5px !important; line-height:1.25 !important; }
12129:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-ops-stat-label { font-size:9px !important; line-height:1.2 !important; }
12130:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-sweep-state { font-size:8.5px !important; line-height:1.1 !important; }
12131:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-sweep-log,
12132:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-empty-state { font-size:9px !important; line-height:1.35 !important; }
12133:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-alliance-text { font-size:9px !important; }
12134:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-finance-vault-summary span { font-size:9px !important; line-height:1.2 !important; }
12135:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-finance-vault-summary b { font-size:10px !important; line-height:1.2 !important; white-space:normal !important; }
12136:         html[data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-finance-vault-summary small { font-size:9px !important; line-height:1.4 !important; }
12137:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-section-label,
12138:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} .mcms-section-label { font-size:10px !important; }
12139:         html[data-mcms-tablet-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} :is(.mcms-ops-stat-label,.mcms-sweep-state,.mcms-alliance-text),
12140:         html[data-mcms-mobile-active="true"][data-mcms-ui-theme] #${SCRIPT.panelId} :is(.mcms-ops-stat-label,.mcms-sweep-state,.mcms-alliance-text) { font-size:9.5px !important; }
12141:         html[data-mcms-mobile-active="true"] #${SCRIPT.toastId} { top:calc(max(10px,env(safe-area-inset-top)) + 58px) !important; }
12142: 
```

## Lines 12552-12567

```text
12552:             white-space:normal !important;
12553:             overflow-wrap:anywhere !important;
12554:         }
12555: 
12556:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tabs {
12557:             position:relative !important;
12558:             gap:3px !important;
12559:             padding:5px !important;
12560:             border-bottom:1px solid rgba(214,182,95,.45) !important;
12561:             background:rgba(5,6,8,.88) !important;
12562:         }
12563:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tabs::after {
12564:             content:"" !important;
12565:             position:absolute !important;
12566:             left:8px !important;
12567:             right:8px !important;
```

## Lines 12570-12578

```text
12570:             background:url("${THEME_ASSETS.bond007GoldDivider}") center/100% 100% no-repeat !important;
12571:             opacity:.65 !important;
12572:             pointer-events:none !important;
12573:         }
12574:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn {
12575:             min-width:0 !important;
12576:             min-height:40px !important;
12577:             padding:7px 8px !important;
12578:             border:1px solid #494f55 !important;
```

## Lines 12584-12600

```text
12584:             letter-spacing:.4px !important;
12585:             white-space:normal !important;
12586:             overflow-wrap:anywhere !important;
12587:         }
12588:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
12589:             border-color:#f0d480 !important;
12590:             border-top:3px solid #a71924 !important;
12591:             background:linear-gradient(180deg,#f2ead5,#c9bb92) !important;
12592:             color:#111214 !important;
12593:             box-shadow:inset 0 0 0 1px rgba(255,255,255,.55),0 0 11px rgba(214,182,95,.22) !important;
12594:         }
12595: 
12596:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label {
12597:             min-height:30px !important;
12598:             padding:8px 12px 8px 38px !important;
12599:             border:1px solid rgba(214,182,95,.55) !important;
12600:             border-left:4px solid #a71924 !important;
```

## Lines 12606-12620

```text
12606:             font:950 9px/1.15 Arial,sans-serif !important;
12607:             letter-spacing:.75px !important;
12608:             white-space:normal !important;
12609:         }
12610:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label::before { display:none !important; }
12611: 
12612:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-theme-btn,
12613:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-toggle-btn,
12614:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-place-main,
12615:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-position-btn,
12616:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-small-btn,
12617:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-bookmark-btn,
12618:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-pin-btn,
12619:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-ui-theme-btn {
12620:             min-width:0 !important;
```

## Lines 12640-12648

```text
12640:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
12641:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
12642:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-place-main:hover,
12643:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-position-btn:hover,
12644:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-small-btn:hover,
12645:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-bookmark-btn:hover,
12646:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-pin-btn:hover,
12647:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
12648:             border-color:#d8b45f !important;
```

## Lines 13160-13168

```text
13160:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-theme-btn strong,
13161:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-toggle-btn strong,
13162:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-ui-theme-btn strong,
13163:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-place-main strong,
13164:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.panelId} .mcms-section-label,
13165:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.criticalDrawerId} button,
13166:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.missionInspectorId} button,
13167:         html[data-mcms-ui-theme="bond007"] #${SCRIPT.vehicleStatusId} button {
13168:             overflow-wrap:anywhere !important;
```

## Lines 13719-13759

```text
13719:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-subtitle,
13720:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.criticalDrawerId} .mcms-drawer-subtitle {
13721:             color:rgba(196,255,240,.72) !important;
13722:         }
13723:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-tabs {
13724:             border-bottom:1px solid rgba(232,193,72,.44) !important;
13725:             background:linear-gradient(180deg,rgba(19,55,42,.82),rgba(5,24,29,.82)) !important;
13726:         }
13727:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-tab-btn {
13728:             border-color:transparent !important;
13729:             color:rgba(239,227,184,.70) !important;
13730:             background:transparent !important;
13731:             font-family:Georgia,"Palatino Linotype",serif !important;
13732:             letter-spacing:.25px !important;
13733:         }
13734:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-tab-btn:hover {
13735:             color:#fff3ad !important;
13736:             background:rgba(63,177,139,.12) !important;
13737:         }
13738:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-tab-btn.mcms-active {
13739:             color:#fff3a1 !important;
13740:             background:linear-gradient(180deg,rgba(86,207,163,.19),rgba(14,62,57,.34)) !important;
13741:             box-shadow:inset 0 -2px #4bf0dd,0 2px 10px rgba(47,226,216,.15) !important;
13742:         }
13743:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-section-label {
13744:             color:#ffe887 !important;
13745:             border-color:rgba(232,191,68,.44) !important;
13746:             background:
13747:                 linear-gradient(90deg,rgba(111,74,25,.45),rgba(26,78,57,.28),transparent) !important;
13748:             text-shadow:0 1px 2px #000 !important;
13749:         }
13750:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-section-label::before { color:#62f4dd !important; }
13751:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-theme-btn,
13752:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-toggle-btn,
13753:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-place-main,
13754:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-position-btn,
13755:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-small-btn,
13756:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-bookmark-btn,
13757:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-pin-btn,
13758:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-ui-theme-btn,
13759:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} input,
```

## Lines 13769-13777

```text
13769:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-theme-btn:hover,
13770:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-toggle-btn:hover,
13771:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-place-main:hover,
13772:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-position-btn:hover,
13773:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-small-btn:hover,
13774:         html[data-mcms-ui-theme="hyrule"] #${SCRIPT.panelId} .mcms-ui-theme-btn:hover {
13775:             border-color:#77f6df !important;
13776:             background:linear-gradient(145deg,rgba(40,98,66,.96),rgba(8,42,47,.96)) !important;
13777:             box-shadow:inset 0 0 0 1px rgba(255,231,132,.24),0 0 12px rgba(57,229,214,.23) !important;
```

## Lines 28113-28123

```text
28113:                 <span class="mcms-build">${SCRIPT.name} v${SCRIPT.version} · MIT · ${SCRIPT.author}</span>
28114:             </div>
28115:         `;
28116: 
28117:         const tabList = panel.querySelector('.mcms-tabs');
28118:         if (tabList) tabList.setAttribute('role', 'tablist');
28119:         panel.querySelectorAll('.mcms-tab-btn').forEach(button => {
28120:             const tab = button.dataset.tab;
28121:             button.id = `mcms-tab-${tab}`;
28122:             button.setAttribute('role', 'tab');
28123:             button.setAttribute('aria-controls', `mcms-tabpanel-${tab}`);
```

## Lines 28132-28142

```text
28132:             tabPanel.hidden = true;
28133:         });
28134: 
28135:         panel.addEventListener('keydown', event => {
28136:             const current = closestEventTarget(event, '.mcms-tab-btn');
28137:             if (!current || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
28138:             const buttons = Array.from(panel.querySelectorAll('.mcms-tab-btn'));
28139:             const currentIndex = Math.max(0, buttons.indexOf(current));
28140:             const nextIndex = event.key === 'Home' ? 0
28141:                 : event.key === 'End' ? buttons.length - 1
28142:                 : (currentIndex + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
```

## Lines 28147-28155

```text
28147:         });
28148: 
28149:         panel.addEventListener('click', event => {
28150:             const closeButton = closestEventTarget(event, '.mcms-close');
28151:             const tabButton = closestEventTarget(event, '.mcms-tab-btn');
28152:             const uiThemeButton = closestEventTarget(event, '.mcms-ui-theme-btn');
28153:             const themeButton = closestEventTarget(event, '.mcms-theme-btn');
28154:             const toggleButton = closestEventTarget(event, '[data-toggle]');
28155:             const positionButton = closestEventTarget(event, '.mcms-position-btn');
```

## Lines 28620-28628

```text
28620: 
28621:         if (!panel) return;
28622: 
28623:         refreshTabletModeUi(panel);
28624:         panel.querySelectorAll('.mcms-tab-btn').forEach(btn => {
28625:             const active = btn.dataset.tab === state.activeTab;
28626:             btn.classList.toggle('mcms-active', active);
28627:             btn.setAttribute('aria-selected', String(active));
28628:             btn.tabIndex = active ? 0 : -1;
```

