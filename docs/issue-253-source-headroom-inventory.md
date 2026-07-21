# Issue #253 — source headroom structural inventory

- Version: `4.20.20`
- SHA-256: `281f1635a8aacced565d7211956ba7d9a4a87e7c6de99f2fd18ade2acedc5832`
- Source: **31,671 lines** / 32,000
- Remaining headroom: **329 lines**
- Source bytes: **2,036,855**
- Blank physical lines: **1,612**
- Comment-only physical lines: **259**

## Largest functions and templates

| Function | Lines | Bytes | Flow | Reads | Writes |
|---|---|---|---|---|---|
| installMainStyles | 12224 | 831639 | 1 | 1 | 0 |
| createPanel | 371 | 38185 | 5 | 7 | 7 |
| boot | 309 | 18057 | 7 | 0 | 0 |
| createCriticalDrawer | 233 | 14315 | 1 | 1 | 4 |
| triggerPayoutFlash | 208 | 14918 | 47 | 22 | 10 |
| updateUI | 204 | 14574 | 57 | 52 | 49 |
| handleSettingChange | 202 | 10543 | 64 | 0 | 0 |
| fetchFinancialLedger | 199 | 12909 | 43 | 0 | 0 |
| animateAdditionalPayoutTemplate | 169 | 11933 | 20 | 0 | 0 |
| summariseFinancialTransactions | 164 | 8501 | 27 | 0 | 0 |
| processTransportSweepMission | 148 | 8576 | 28 | 0 | 0 |
| drawer.addEventListener callback@21278 | 137 | 7100 | 31 | 1 | 0 |
| toggleFeature | 118 | 8161 | 83 | 0 | 0 |
| normaliseLoadedState | 117 | 10339 | 30 | 0 | 0 |
| particleElements.forEach callback | 114 | 8441 | 14 | 0 | 0 |
| buildFinancialReport | 113 | 6533 | 18 | 0 | 0 |
| ensurePayoutFlashOverlay | 111 | 7735 | 15 | 15 | 6 |
| updateMissionAgeLabels | 110 | 5111 | 33 | 0 | 0 |
| playSynthPayoutSound | 109 | 4876 | 19 | 0 | 0 |
| buildFinancialChartBlob | 104 | 5886 | 5 | 0 | 0 |
| updateCoverageHeatmap | 103 | 5203 | 19 | 1 | 0 |
| toggleCommandBar | 102 | 5425 | 10 | 2 | 0 |
| renderCriticalDrawer | 89 | 12717 | 12 | 14 | 4 |
| resolveFinancialPeriod | 89 | 4201 | 21 | 0 | 0 |
| toggleCriticalView | 88 | 4084 | 8 | 2 | 3 |
| getCriticalMissionEntries | 87 | 4879 | 7 | 0 | 0 |
| findLeafletMapInstance | 86 | 3383 | 19 | 0 | 0 |
| updateStuckMissionLabels | 85 | 4075 | 26 | 0 | 0 |
| updateTransportWatcherLabels | 85 | 4105 | 26 | 0 | 0 |
| updateAllianceCreditLabels | 84 | 3712 | 22 | 0 | 0 |

| Template owner | Type | Line | Bytes | Rules/braces |
|---|---|---|---|---|
| installMainStyles | css | 1831 | 831307 | 6394 |
| createPanel | css | 29854 | 31412 | 40 |
| missionRequirementsDocumentCss | css | 23080 | 13120 | 139 |
| createCriticalDrawer | html | 21205 | 4770 | 0 |
| ensureVersionStatusStyle | css | 29684 | 4603 | 39 |
| ensurePayoutFlashOverlay | html | 25570 | 3270 | 0 |
| renderedEntries.map callback | html | 23803 | 2916 | 0 |
| createControl | html | 29746 | 2806 | 0 |
| criticalSummaryHtml | html | 23622 | 2610 | 0 |
| patchHelpGuideDocument | html | 29421 | 2547 | 0 |
| createHelpCenter | html | 29489 | 2349 | 0 |
| installAllianceBuildingsEarlyStyle | css | 137 | 2333 | 5 |
| customVehicleBadgeDocumentCss | css | 15730 | 1997 | 19 |
| ensureMissionValueDocumentStyle | css | 22066 | 1782 | 8 |
| createVehicleCodeStatus | html | 20896 | 1706 | 0 |
| patchHelpGuideDocument | html | 29431 | 1662 | 0 |
| renderOperationalPanels | html | 20801 | 1372 | 0 |
| protectHelpGuideDocument | html | 29443 | 1259 | 0 |
| state.bookmarks.map callback@30206 | html | 30213 | 1228 | 0 |
| createMissionLockOnReticle | html | 24089 | 1223 | 0 |

## Static literal candidates across all scopes

| Name | Owner | Kind | Lines | Bytes | Entries | JSON-like | Estimated recovered lines |
|---|---|---|---|---|---|---|---|
| SCRIPT | <anonymous@47> | ObjectExpression | 47 | 2613 | 33 | true | 44 |
| themedTitles | payoutTitleForTemplate | ObjectExpression | 47 | 2405 | 15 | true | 44 |
| runtime | <anonymous@47> | ObjectExpression | 44 | 2195 | 14 | false | — |
| fields | missionRequirementsReportUrl | ArrayExpression | 40 | 2612 | 38 | false | — |
| PAYOUT_MEDIA_SOUNDS | <anonymous@47> | ObjectExpression | 38 | 2085 | 9 | true | 35 |
| report | buildFinancialReport | ObjectExpression | 38 | 1742 | 36 | false | — |
| toggleValues | updateUI | ObjectExpression | 33 | 1586 | 30 | false | — |
| snapshot | missionSnapshotFromMarker | ObjectExpression | 32 | 2672 | 30 | false | — |
| navigationGuard | protectHelpGuideDocument | TemplateLiteral | 31 | 1279 | 1 | true | 28 |
| transportSweepRuntime | <anonymous@47> | ObjectExpression | 30 | 816 | 28 | false | — |
| THEME_ASSETS | <anonymous@47> | ObjectExpression | 23 | 3218 | 21 | true | 20 |
| merged | normaliseLoadedState | ObjectExpression | 21 | 1431 | 19 | false | — |
| executive | buildDiscordFinancialPayload | ObjectExpression | 20 | 1877 | 6 | false | — |
| PAYOUT_TEMPLATES | <anonymous@47> | ObjectExpression | 17 | 1908 | 15 | true | 14 |
| BUILTIN_FINANCIAL_RULES | <anonymous@47> | ArrayExpression | 16 | 3670 | 14 | true | 13 |
| customVehicleClassificationApi | <anonymous@47> | ObjectExpression | 16 | 714 | 4 | false | — |
| layer | createSuppressedAllianceLayer | ObjectExpression | 16 | 553 | 14 | false | — |
| BUILTIN_FINANCIAL_POLICY | <anonymous@47> | ObjectExpression | 16 | 544 | 4 | true | 13 |
| FOOTBALL_SPECIAL_EVENT_MISSIONS | <anonymous@47> | ArrayExpression | 16 | 537 | 14 | true | 13 |
| semanticSelectors | missionRequirementsStaffCapacity | ArrayExpression | 14 | 492 | 12 | true | 11 |
| audit | buildDiscordFinancialPayload | ObjectExpression | 13 | 1113 | 4 | false | — |
| SMART_BOOKMARK_WORDS | <anonymous@47> | ObjectExpression | 13 | 1013 | 53 | true | 10 |
| THEMES | <anonymous@47> | ObjectExpression | 13 | 999 | 11 | true | 10 |
| labels | missingRequirementKeyLabel | ObjectExpression | 13 | 345 | 11 | true | 10 |
| controlToggleValues | updateUI | ObjectExpression | 11 | 534 | 9 | false | — |
| visibilityShortcut | handleKeyboard | ObjectExpression | 11 | 370 | 9 | true | 8 |
| candidate | collectTransportSweepStaticCandidates | ObjectExpression | 11 | 330 | 9 | false | — |
| activeAnimations | triggerPayoutFlash | ArrayExpression | 10 | 698 | 3 | false | — |
| VEHICLE_CODE_STATUS_DEFINITIONS | <anonymous@47> | ArrayExpression | 10 | 548 | 8 | true | 7 |
| candidates | extractImportedFinancialVaultCredential | ArrayExpression | 10 | 525 | 8 | false | — |
| candidates | extractImportedFinancialVaultStore | ArrayExpression | 10 | 437 | 8 | false | — |
| UI_THEMES | <anonymous@47> | ObjectExpression | 9 | 1647 | 7 | true | 6 |
| html | renderOperationalPanels | TemplateLiteral | 9 | 1381 | 1 | false | — |
| data | criticalMissionStableData | ObjectExpression | 9 | 180 | 7 | false | — |
| definitions | applyCriticalQuickView | ObjectExpression | 8 | 570 | 6 | true | 5 |
| definitions | criticalQuickViewsHtml | ArrayExpression | 8 | 568 | 6 | true | 5 |
| counts | criticalQuickViewsHtml | ObjectExpression | 8 | 450 | 6 | false | — |
| labels | majorIncidentThemeLabel | ObjectExpression | 8 | 261 | 6 | true | 5 |
| statusLabels | criticalAdvancedFilterSummaryText | ObjectExpression | 8 | 245 | 6 | true | 5 |
| labels | criticalOperationalFilterLabel | ObjectExpression | 8 | 213 | 6 | true | 5 |
| analysis | analyseResourceGap | ObjectExpression | 8 | 209 | 6 | false | — |
| financialSection | patchHelpGuideDocument | TemplateLiteral | 7 | 2568 | 1 | true | 4 |
| QUICK_PLACES | <anonymous@47> | ArrayExpression | 7 | 488 | 5 | true | 4 |
| candidates | missionValueIdFromElement | ArrayExpression | 7 | 231 | 5 | false | — |
| labels | missionLockOnThemeLabel | ObjectExpression | 7 | 229 | 5 | true | 4 |
| candidates | extractImportedToolkitState | ArrayExpression | 7 | 184 | 5 | false | — |
| economySection | patchHelpGuideDocument | TemplateLiteral | 6 | 1681 | 1 | true | 3 |
| CRITICAL_AGE_FILTERS | <anonymous@47> | ObjectExpression | 6 | 774 | 4 | false | — |
| safe | saveFinanceVaultCredential | ObjectExpression | 6 | 418 | 4 | false | — |
| preferredSelectors | findMissionListDockRect | ArrayExpression | 6 | 387 | 15 | true | 3 |
| wording | payoutPresentation | ObjectExpression | 6 | 364 | 4 | true | 3 |
| HELP_CENTER | <anonymous@47> | ObjectExpression | 6 | 319 | 4 | true | 3 |
| selectors | transportSweepWindowCloseControl | ArrayExpression | 6 | 309 | 11 | true | 3 |
| SUPPRESSION_SELECTORS | <anonymous@47> | ArrayExpression | 6 | 308 | 12 | true | 3 |
| tracking | playMissionLockTrackingSound | ArrayExpression | 6 | 257 | 4 | true | 3 |
| POSITIONS | <anonymous@47> | ObjectExpression | 6 | 218 | 4 | true | 3 |
| accents | payoutPresentation | ObjectExpression | 5 | 415 | 3 | true | 2 |
| selectors | transportSweepVisibleWindowRoots | ArrayExpression | 5 | 306 | 13 | true | 2 |
| entry | recordCreditGain | ObjectExpression | 5 | 288 | 6 | false | — |
| names | findLeafletMapInstance | ArrayExpression | 5 | 214 | 13 | true | 2 |

## Exact repeated source blocks

| Width | Occurrences | Potential lines | Locations | Preview |
|---|---|---|---|---|
| 8 | 3 | 16 | 25613, 25682, 26003 | const red = overlay.querySelector('.mcms-payout-red'); / const blue = overlay.querySelector('.mcms-payout-blue'); / const cinematic = overlay.querySelector('.mcms-payout-cinematic'); |
| 6 | 3 | 12 | 16491, 16700, 24476 | for (const marker of getMissionMarkerIndex().markers) { / const missionId = normaliseMissionId(marker?.mission_id ?? marker?.missionId ?? marker?.options?.mission_id ?? marker?.options?.missionId); / if (missionId === null) continue; |
| 6 | 3 | 12 | 25613, 25682, 26003 | const red = overlay.querySelector('.mcms-payout-red'); / const blue = overlay.querySelector('.mcms-payout-blue'); / const cinematic = overlay.querySelector('.mcms-payout-cinematic'); |
| 6 | 3 | 12 | 25614, 25683, 26004 | const blue = overlay.querySelector('.mcms-payout-blue'); / const cinematic = overlay.querySelector('.mcms-payout-cinematic'); / const viceSunset = overlay.querySelector('.mcms-payout-vc-sunset'); |
| 6 | 3 | 12 | 25615, 25684, 26005 | const cinematic = overlay.querySelector('.mcms-payout-cinematic'); / const viceSunset = overlay.querySelector('.mcms-payout-vc-sunset'); / const viceGrid = overlay.querySelector('.mcms-payout-vc-grid'); |
| 8 | 2 | 8 | 1360, 21456 | ownershipFilter: 'personal', / categoryFilter: 'all', / primaryStatus: 'all', |
| 8 | 2 | 8 | 1361, 21457 | categoryFilter: 'all', / primaryStatus: 'all', / advancedFiltersOpen: false, |
| 8 | 2 | 8 | 6297, 6775 | } / html[data-mcms-ui-theme="umbrella"] .mcms-alliance-credit-badge, / html[data-mcms-ui-theme="umbrella"] .mcms-mission-age-badge, |
| 8 | 2 | 8 | 6384, 6838 | html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small, / html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span, / html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label, |
| 8 | 2 | 8 | 6385, 6839 | html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span, / html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label, / html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta { |
| 8 | 2 | 8 | 6386, 6840 | html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-stat-label, / html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta { / font-size: 9px !important; |
| 8 | 2 | 8 | 6387, 6841 | html[data-mcms-tablet-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ops-entry-meta { / font-size: 9px !important; / } |
| 8 | 2 | 8 | 6388, 6842 | font-size: 9px !important; / } / html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small, |
| 8 | 2 | 8 | 6389, 6843 | } / html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-ui-theme-copy small, / html[data-mcms-mobile-active="true"][data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-profile-main span, |
| 8 | 2 | 8 | 6420, 6873 | } / @media (prefers-reduced-motion: reduce) { / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId}.mcms-open, |
| 8 | 2 | 8 | 6421, 6874 | @media (prefers-reduced-motion: reduce) { / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId}.mcms-open, / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active, |
| 8 | 2 | 8 | 6422, 6875 | html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId}.mcms-open, / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active, / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header::after, |
| 8 | 2 | 8 | 6423, 6876 | html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-tab-panel.mcms-active, / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header::after, / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on { |
| 8 | 2 | 8 | 6424, 6877 | html[data-mcms-ui-theme="umbrella"] #${SCRIPT.panelId} .mcms-header::after, / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on { / animation: none !important; |
| 8 | 2 | 8 | 6425, 6878 | html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn.mcms-on { / animation: none !important; / } |
| 8 | 2 | 8 | 6426, 6879 | animation: none !important; / } / html[data-mcms-ui-theme="umbrella"] #${SCRIPT.controlId} .mcms-float-btn, |
| 8 | 2 | 8 | 8322, 9889 | display:flex !important; / align-items:center !important; / justify-content:center !important; |
| 8 | 2 | 8 | 8323, 9890 | align-items:center !important; / justify-content:center !important; / padding:0 3px !important; |
| 8 | 2 | 8 | 8423, 11010 | display:flex !important; / align-items:center !important; / justify-content:center !important; |
| 8 | 2 | 8 | 8424, 11011 | align-items:center !important; / justify-content:center !important; / min-width:46px !important; |

## First-pass safety decision

- Do not touch stylesheet delivery, CSS selector grouping, observer scope, scheduler timing or network sequencing in the first source-headroom PR.
- Prefer a JSON-like static catalogue with deterministic serialization and an exact runtime-value parity contract.
- Keep the readable source catalogue in `src/data`; generate one compact literal in the canonical single-file userscript.
- Use one subsystem and one rollback boundary.

## Candidate ranking

| Name | Owner | Lines | Bytes | Entries | Estimated recovered lines |
|---|---|---|---|---|---|
| SCRIPT | <anonymous@47> | 47 | 2613 | 33 | 44 |
| themedTitles | payoutTitleForTemplate | 47 | 2405 | 15 | 44 |
| PAYOUT_MEDIA_SOUNDS | <anonymous@47> | 38 | 2085 | 9 | 35 |
| navigationGuard | protectHelpGuideDocument | 31 | 1279 | 1 | 28 |
| THEME_ASSETS | <anonymous@47> | 23 | 3218 | 21 | 20 |

This inventory is static structural evidence. A production change still requires exact generated-value parity and the complete repository test suite.
