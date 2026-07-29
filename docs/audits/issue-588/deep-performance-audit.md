# MissionChief Toolkit deep performance audit

> AST-backed static structural evidence only. Runtime gains require equivalent browser-profiler scenarios and deterministic behaviour parity.

## Baseline

- Parser: `acorn`
- Version: `8.3.1`
- SHA-256: `363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089`
- Source: `1,654,208` bytes, `25,228` lines
- Functions/callbacks: `1450`
- Scheduler calls: `100`
- MutationObserver constructions: `11`
- ResizeObserver constructions: `4`
- Resolved observer registrations: `15`
- Broad subtree registrations: `9`
- Locally resolved broad registrations: `7`
- Cross-function broad registrations: `2`

## Trusted-baseline cross-check

| Metric | Trusted baseline | AST inventory |
|---|---|---|
| MutationObserver constructions | 11 | 11 |
| ResizeObserver constructions | 4 | 4 |
| Broad subtree registrations | 9 | 9 |
| Unresolved observe calls | manual review | 3 |

## Findings

- **HIGH · style-parse** — The largest embedded CSS template exceeds 500 KB; live timing and visual contracts are required before changing style delivery.
- **MEDIUM · observer-scope** — 9 observer registrations use subtree:true (7 locally resolved and 2 cross-function); ownership and callback evidence are required before narrowing or merging them.
- **MEDIUM · observer-ownership** — 2 resolved registrations lack an AST-visible disconnect, runtimeTrackObserver or observer-registry signal and require manual lifecycle verification.
- **REVIEW · observer-linkage** — 3 .observe() calls could not be linked to a constructor by local AST ownership and remain manual-review items.
- **LOW · selector-repetition** — Repeated literal selectors exist; cache only inside proven document/window lifetimes with invalidation fixtures.

## Highest structural hotspot scores

| Function | Lines | Bytes | Flow | Reads | Writes | Schedulers | Observers | Network | Score |
|---|---|---|---|---|---|---|---|---|---|
| installMainStyles | 7864 | 683890 | 1 | 1 | 0 | 0 | 0 | 0 | 7875 |
| updateUI | 175 | 12455 | 46 | 42 | 39 | 0 | 0 | 0 | 973 |
| triggerPayoutFlash | 208 | 14918 | 47 | 22 | 10 | 3 | 0 | 0 | 698 |
| createPanel | 346 | 34279 | 5 | 7 | 7 | 0 | 0 | 0 | 467 |
| fetchFinancialLedger | 199 | 12909 | 43 | 0 | 0 | 0 | 0 | 0 | 457 |
| handleAction | 57 | 4561 | 46 | 3 | 0 | 0 | 0 | 0 | 348 |
| summariseFinancialTransactions | 164 | 8501 | 27 | 0 | 0 | 0 | 0 | 0 | 326 |
| ensurePayoutFlashOverlay | 111 | 7735 | 15 | 15 | 6 | 0 | 0 | 0 | 324 |
| reconcileFinancialOverview | 142 | 7880 | 27 | 0 | 0 | 0 | 0 | 0 | 304 |
| boot | 228 | 13570 | 8 | 0 | 0 | 2 | 1 | 0 | 298 |
| stopPayoutFlashAnimation | 75 | 4085 | 19 | 17 | 2 | 0 | 0 | 0 | 290 |
| animateAdditionalPayoutTemplate | 169 | 11933 | 20 | 0 | 0 | 0 | 0 | 0 | 289 |
| buildFinancialReport | 141 | 8643 | 20 | 0 | 0 | 0 | 0 | 0 | 261 |
| installAllianceMemberManager | 134 | 5729 | 4 | 0 | 12 | 0 | 0 | 0 | 254 |
| normaliseLoadedState | 104 | 8190 | 23 | 0 | 0 | 0 | 0 | 0 | 242 |
| toggleFeature | 62 | 3744 | 29 | 0 | 0 | 1 | 0 | 0 | 242 |
| playSynthPayoutSound | 115 | 5168 | 20 | 0 | 0 | 1 | 0 | 0 | 241 |
| updateStuckMissionLabels | 85 | 4075 | 26 | 0 | 0 | 0 | 0 | 0 | 241 |
| processTransportSweepMission | 112 | 6709 | 21 | 0 | 0 | 0 | 0 | 0 | 238 |
| syncMissionValueCandidate | 60 | 3471 | 17 | 1 | 8 | 0 | 0 | 0 | 231 |

## DOM-write concentration

| Function | Lines | Reads | Writes | Schedulers | Score |
|---|---|---|---|---|---|
| updateUI | 175 | 42 | 39 | 0 | 973 |
| installAllianceMemberManager | 134 | 0 | 12 | 0 | 254 |
| loadHelpCenterGuide | 25 | 3 | 12 | 0 | 184 |
| triggerPayoutFlash | 208 | 22 | 10 | 3 | 698 |
| syncMissionValueCandidate | 60 | 1 | 8 | 0 | 231 |
| renderAllianceBuildingsMapPreference | 29 | 1 | 8 | 0 | 146 |
| majorIncidentFeedSyncControls | 25 | 4 | 8 | 0 | 175 |
| createPanel | 346 | 7 | 7 | 0 | 467 |
| renderMajorIncidentFeed | 49 | 4 | 7 | 0 | 167 |
| refreshTabletModeUi | 24 | 7 | 7 | 0 | 193 |
| applyMarkerType | 21 | 2 | 7 | 0 | 171 |
| ensurePayoutFlashOverlay | 111 | 15 | 6 | 0 | 324 |
| createControl | 87 | 1 | 6 | 0 | 158 |
| createHelpCenter | 55 | 1 | 6 | 0 | 114 |
| allianceMemberManagerLoadAll | 37 | 0 | 6 | 0 | 145 |
| createMissionLockOnReticle | 71 | 0 | 5 | 5 | 183 |
| positionMajorIncidentFeed | 37 | 3 | 5 | 0 | 128 |
| toolkitApplyCommandBarState | 23 | 4 | 5 | 0 | 131 |
| updateAllianceMemberManagerMenuControl | 23 | 3 | 5 | 0 | 126 |
| ensureTransportSweepHud | 18 | 0 | 5 | 0 | 82 |

## Scheduler concentration

| Function | Calls |
|---|---|
| createMissionLockOnReticle | 5 |
| installAllianceBuildingsPageOptimisation | 3 |
| triggerPayoutFlash | 3 |
| animateMissionSpawn | 2 |
| boot | 2 |
| installMissionValueWindows | 2 |
| recoverUiAfterNavigation | 2 |
| runtimeRequestAnimationFrame callback@17007 | 2 |
| runtimeRunWhenIdle | 2 |
| scheduleMajorIncidentFeedLayout | 2 |
| animateMissionFocus | 1 |
| animatePayoutAmount | 1 |
| applyMapVisibilityToggleEffects | 1 |
| closeHelpCenter | 1 |
| closePanel | 1 |
| control.addEventListener callback | 1 |
| downloadToolkitSettingsBlob | 1 |
| endPanelDrag | 1 |
| feed.addEventListener callback@15550 | 1 |
| finishLockOn | 1 |

## Resolved observer registrations

| Line | Function | Type | Target | Options | Tracked | Registry | Disconnect |
|---|---|---|---|---|---|---|---|
| 431 | begin | MutationObserver | root | { childList: true, subtree: true } | false | false | false |
| 9970 | observeDesktopPanelWorkspace | ResizeObserver | element |  | true | false | true |
| 10134 | observeTabletMapArea | ResizeObserver | mapEl |  | true | false | true |
| 11397 | observeCustomVehicleBadgeDocument | MutationObserver | root | { childList: true, subtree: true, attributes: true, attributeFilter: ['id', 'class', 'vehicle_id', 'data-vehicle-id', 'data-vehicle_id', 'vehicle_type_id', 'data-vehicle-type-id', 'data-vehicle_type_id'] } | true | false | true |
| 15574 | ensureMajorIncidentFeed | ResizeObserver | feed |  | true | false | true |
| 15576 | ensureMajorIncidentFeed | ResizeObserver | viewport |  | true | false | true |
| 16560 | observeMissionValueHost | ResizeObserver | spacer |  | true | false | true |
| 16564 | observeMissionValueHost | MutationObserver | toolbar | { childList: true, subtree: false } | true | false | true |
| 16731 | observeMissionValueDocument | MutationObserver | root | { childList: true, subtree: true } | true | false | true |
| 18771 | observeCreditValue | MutationObserver | element | { childList: true, subtree: true, characterData: true } | true | false | true |
| 23759 | installAllianceBuildingsPageOptimisation | MutationObserver | document.body | { childList: true, subtree: true } | true | false | true |
| 23964 | observeAutoLoadAllVehiclesRoot | MutationObserver | root | { attributes: true, attributeFilter: ['class', 'style', 'hidden', 'aria-hidden'] } | true | false | true |
| 23982 | observeAutoLoadAllVehiclesLink | MutationObserver | link | { attributes: true, attributeFilter: ['href', 'class', 'style', 'hidden', 'aria-hidden', 'aria-disabled'] } | true | false | true |
| 24097 | installAutoLoadAllVehicles | MutationObserver | document.body | { childList: true, subtree: true } | true | false | true |
| 24689 | allianceMemberManagerEnsureMountObserver | MutationObserver | root | { childList: true, subtree: true } | false | false | false |

## Unresolved observe calls

| Line | Function | Observer expression | Target | Options |
|---|---|---|---|---|
| 23797 | connectMainMutationObserver | mainMutationObserver | document.body | { childList: true, subtree: true } |
| 23801 | connectMainMutationObserver | mainMutationObserver | root | { childList: true, subtree: true } |
| 23802 | connectMainMutationObserver | mainMutationObserver | document.body | { childList: true, subtree: false } |

## Observer constructions without a matched registration

| Line | Function | Type | Variable | Tracked | Registry | Disconnect |
|---|---|---|---|---|---|---|
| 24226 | boot | MutationObserver | observer | true | false | true |

## Largest embedded templates

| Line | Function | Type | Bytes | Brace/rule estimate |
|---|---|---|---|---|
| 1781 | installMainStyles | css | 683558 | 5379 |
| 22713 | createPanel | css | 27506 | 34 |
| 24727 | allianceMemberManagerStyle | css | 5201 | 47 |
| 22533 | ensureVersionStatusStyle | css | 4603 | 39 |
| 18095 | ensurePayoutFlashOverlay | html | 3270 | 0 |
| 22604 | createControl | html | 2464 | 0 |
| 22264 | patchHelpGuideDocument | html | 2434 | 0 |
| 22331 | createHelpCenter | html | 2349 | 0 |
| 137 | installAllianceBuildingsEarlyStyle | css | 2333 | 5 |
| 11321 | customVehicleBadgeDocumentCss | css | 2251 | 21 |
| 16684 | ensureMissionValueDocumentStyle | css | 1782 | 8 |
| 16189 | createVehicleCodeStatus | html | 1706 | 0 |
| 22273 | patchHelpGuideDocument | html | 1640 | 0 |
| 22285 | protectHelpGuideDocument | html | 1259 | 0 |
| 23047 | state.bookmarks.map callback | html | 1228 | 0 |
| 16925 | createMissionLockOnReticle | html | 1223 | 0 |
| 16113 | renderOperationalPanels | html | 1166 | 0 |
| 15471 | majorIncidentFeedItemHtml | html | 1008 | 0 |

## Repeated literal selectors

| Count | Selector | Functions |
|---|---|---|
| 7 | iframe, frame | MutationObserver callback@16721, Observer callback, add, closeTransportSweepWindows, observeCustomVehicleBadgeDocument, observeMissionValueDocument, visit |
| 7 | table | allianceBuildingsTables, allianceMemberManagerTable, candidates.find callback, find callback, isAllianceBuildingsMapTarget, parseCreditOverviewDocument, siblings.find callback |
| 5 | .mcms-incident-feed-track | majorIncidentFeedAnimation, majorIncidentFeedDomComplete, refreshMajorIncidentFeedMotion, renderMajorIncidentFeed |
| 5 | .mcms-payout-banner | ensurePayoutFlashOverlay, fitPayoutFlashAroundToolkitControls, fitPayoutFlashContent, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-economy-btn | applyMobileDockLayout, ensureVersionStatusButton, updateUI |
| 3 | .mcms-incident-feed-viewport | ensureMajorIncidentFeed, majorIncidentFeedDomComplete, refreshMajorIncidentFeedMotion |
| 3 | .mcms-mission-value-row | missionValueRowsForCandidate, removeMissionValueRows, scanMissionValueWindows |
| 3 | .mcms-payout-bc-dust | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-bc-embers | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-bc-hud | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-blue | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-cinematic | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-red | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-theme-fx-a | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-theme-fx-b | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-theme-fx-c | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-theme-particles | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-vc-grid | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-payout-vc-sunset | ensurePayoutFlashOverlay, stopPayoutFlashAnimation, triggerPayoutFlash |
| 3 | .mcms-tab-btn | createPanel, panel.addEventListener callback, updateUI |
| 3 | a[href*="/buildings/"] | candidates.find callback, filter callback, isAllianceBuildingsMapTarget |
| 3 | a[href*="/vehicles/"] | customVehicleBadgeVehicleId, transportSweepFetchMissionCandidates, transportSweepVehicleAnchorsWithin |
| 3 | img | getStrongMarkerSignal, map callback@15138, optimiseAllianceBuildingsCourseTableEarly |
| 2 | .credits-value | observeCreditValue, readCurrentCreditTotal |
| 2 | .leaflet-marker-icon | classifyMarkersNow, mutationAddsLeafletMarkerIcon |

## Safety interpretation

- A large function or repeated selector is a profiling target, not proof of a defect.
- Observer count must not be reduced by merging different lifecycle owners.
- Cached DOM references require explicit invalidation when MissionChief replaces documents, dialogs, frames or controls.
- CSS extraction requires visual contracts and first-paint evidence.
- Every runtime optimisation must be isolated, benchmarked and reversible.
