# Issue #133 — Canonical userscript source inspection

Generated mechanically from the canonical userscript before production changes.

- Source lines: **30,085**
- Source bytes: **1,824,408**

## Anchor inventory

### `#missing_text`

No matches.

### `missing_text`

Matches: 15008, 15010, 19849

#### Context around line 15008

```javascript
14996:         const missionType = item.mission_type ?? item.missionType;
14997:         const filterId = item.filter_id ?? item.filterId;
14998:         const eventId = item.event_id ?? item.eventId;
14999:         const eventFlag = item.sw ?? item.sicherheitswache ?? item.security_watch ?? item.securityWatch ?? item.is_event ?? item.isEvent ?? item.event;
15000:         const eventName = item.event_name ?? item.eventName ?? item.event_title ?? item.eventTitle ?? item.event_caption ?? item.eventCaption;
15001:         const specialEventFlag = item.special_event ?? item.specialEvent ?? item.is_special_event ?? item.isSpecialEvent ?? item.global_event ?? item.globalEvent ?? item.developer_event ?? item.developerEvent;
15002:         const dateEndCalc = parseMissionTimestamp(item.date_end_calc ?? item.dateEndCalc);
15003:         const dateEnd = parseMissionTimestamp(item.date_end ?? item.dateEnd);
15004:         const dateNow = parseMissionTimestamp(item.date_now ?? item.dateNow);
15005:         const dateNowUpdatedAt = dateNow !== null ? Date.now() : null;
15006:         const rawVehicleState = item.vehicle_state ?? item.vehicleState;
15007:         const vehicleState = Number(rawVehicleState);
15008:         const missingTextKeys = ['missing_text', 'missingText', 'missing_text_short', 'missingTextShort'];
15009:         const missingTextKnown = missingTextKeys.some(key => Object.prototype.hasOwnProperty.call(item, key));
15010:         const missingText = item.missing_text ?? item.missingText ?? item.missing_text_short ?? item.missingTextShort ?? '';
15011:         const normalisedMissingText = normaliseMissingRequirementText(missingText);
15012:         const patientsCount = Number(item.patients_count ?? item.patientsCount);
15013:         const possiblePatientsCount = Number(item.possible_patients_count ?? item.possiblePatientsCount);
15014:         const prisonersCount = Number(item.prisoners_count ?? item.prisonersCount);
15015:         const possiblePrisonersCount = Number(item.possible_prisoners_count ?? item.possiblePrisonersCount);
15016:         const liveCurrentValue = Number(item.live_current_value ?? item.liveCurrentValue ?? item.current_value ?? item.currentValue);
15017:         const liveCurrentValueUpdatedAt = Date.now();
15018: 
15019:         return {
15020:             ...existing,
```

#### Context around line 15010

```javascript
14998:         const eventId = item.event_id ?? item.eventId;
14999:         const eventFlag = item.sw ?? item.sicherheitswache ?? item.security_watch ?? item.securityWatch ?? item.is_event ?? item.isEvent ?? item.event;
15000:         const eventName = item.event_name ?? item.eventName ?? item.event_title ?? item.eventTitle ?? item.event_caption ?? item.eventCaption;
15001:         const specialEventFlag = item.special_event ?? item.specialEvent ?? item.is_special_event ?? item.isSpecialEvent ?? item.global_event ?? item.globalEvent ?? item.developer_event ?? item.developerEvent;
15002:         const dateEndCalc = parseMissionTimestamp(item.date_end_calc ?? item.dateEndCalc);
15003:         const dateEnd = parseMissionTimestamp(item.date_end ?? item.dateEnd);
15004:         const dateNow = parseMissionTimestamp(item.date_now ?? item.dateNow);
15005:         const dateNowUpdatedAt = dateNow !== null ? Date.now() : null;
15006:         const rawVehicleState = item.vehicle_state ?? item.vehicleState;
15007:         const vehicleState = Number(rawVehicleState);
15008:         const missingTextKeys = ['missing_text', 'missingText', 'missing_text_short', 'missingTextShort'];
15009:         const missingTextKnown = missingTextKeys.some(key => Object.prototype.hasOwnProperty.call(item, key));
15010:         const missingText = item.missing_text ?? item.missingText ?? item.missing_text_short ?? item.missingTextShort ?? '';
15011:         const normalisedMissingText = normaliseMissingRequirementText(missingText);
15012:         const patientsCount = Number(item.patients_count ?? item.patientsCount);
15013:         const possiblePatientsCount = Number(item.possible_patients_count ?? item.possiblePatientsCount);
15014:         const prisonersCount = Number(item.prisoners_count ?? item.prisonersCount);
15015:         const possiblePrisonersCount = Number(item.possible_prisoners_count ?? item.possiblePrisonersCount);
15016:         const liveCurrentValue = Number(item.live_current_value ?? item.liveCurrentValue ?? item.current_value ?? item.currentValue);
15017:         const liveCurrentValueUpdatedAt = Date.now();
15018: 
15019:         return {
15020:             ...existing,
15021:             ...(credits !== null ? { averageCredits: credits } : {}),
15022:             ...(createdAt !== null ? { createdAt } : {}),
```

#### Context around line 19849

```javascript
19837:         const ownership = missionWatchOwnership(marker, missionId);
19838:         const specialEvent = missionDeveloperEventInfo(marker, missionId);
19839:         const category = missionWatchCategory(marker, missionId, null, specialEvent);
19840:         const unitState = missionPersonalUnitState(marker, missionId);
19841:         const units = {
19842:             ...unitState.commitment,
19843:             markerPresence: Boolean(unitState.hasUnit && Number(unitState.commitment?.total || 0) <= 0)
19844:         };
19845:         const overlay = missionOverlayData.get(missionId) || {};
19846:         const overlayMissingTextKnown = overlay.missingTextKnown === true || Object.prototype.hasOwnProperty.call(overlay, 'missingText');
19847:         const rawMissingText = overlayMissingTextKnown
19848:             ? String(overlay.missingText || '')
19849:             : marker?.missing_text || marker?.missingText || marker?.options?.missing_text || marker?.options?.missingText || '';
19850:         const address = getMissionAddress(marker, missionId);
19851:         const postcode = normaliseMissionPostcode(overlay.postcode || address);
19852:         const area = normaliseMissionCity(overlay.city || address, postcode);
19853:         const liveCurrentValue = resolveMissionLiveCurrentValue(marker, missionId, overlay, now);
19854:         const snapshot = {
19855:             missionId,
19856:             marker,
19857:             caption: getMissionCaption(marker, missionId),
19858:             address,
19859:             postcode,
19860:             city: area,
19861:             area,
```

### `#mission-form`

No matches.

### `mission-form`

No matches.

### `#mission_vehicle_driving`

No matches.

### `mission_vehicle_driving`

No matches.

### `#vehicle_show_table_body_all`

No matches.

### `vehicle_show_table_body_all`

No matches.

### `#vehicle_amount`

No matches.

### `vehicle_amount`

No matches.

### `#occupied`

No matches.

### `tractive_vehicle_id`

No matches.

### `data-equipment-types`

No matches.

### `navbar-alarm-spacer`

Matches: 4220, 21527, 21528, 21536, 21552, 21783, 21817

#### Context around line 4220

```javascript
04208: 
04209: 
04210:         .mcms-mission-value-row {
04211:             display: flex !important;
04212:             align-items: center !important;
04213:             justify-content: flex-end !important;
04214:             min-width: 0 !important;
04215:             box-sizing: border-box !important;
04216:             position: relative !important;
04217:             z-index: 2 !important;
04218:             pointer-events: none !important;
04219:         }
04220:         #navbar-alarm-spacer > .mcms-mission-value-row,
04221:         .mcms-mission-value-row[data-mcms-host="toolbar"] {
04222:             flex: 1 1 auto !important;
04223:             width: 100% !important;
04224:             min-height: 32px !important;
04225:             margin: 0 !important;
04226:             padding: 0 3px 0 6px !important;
04227:             clear: none !important;
04228:             overflow: hidden !important;
04229:         }
04230:         .mcms-mission-value-row[data-mcms-host="fallback"] {
04231:             width: 100% !important;
04232:             min-height: 30px !important;
```

#### Context around line 21527

```javascript
21515:         try { scope.querySelectorAll?.('.mcms-mission-value-row').forEach(row => row.remove()); } catch (err) {}
21516:     }
21517: 
21518:     function clearMissionValueIndicators() {
21519:         for (const context of transportSweepDocumentContexts()) removeMissionValueRows(context.doc);
21520:     }
21521: 
21522: 
21523:         function missionValueToolbarSpacer(root, mount) {
21524:         const scopes = [root, mount].filter(Boolean);
21525:         for (const scope of scopes) {
21526:             try {
21527:                 if (scope.matches?.('#navbar-alarm-spacer')) return scope;
21528:                 const spacer = scope.querySelector?.('#navbar-alarm-spacer');
21529:                 if (spacer) return spacer;
21530:             } catch (err) {}
21531:         }
21532:         const doc = root?.ownerDocument || mount?.ownerDocument || null;
21533:         if (!doc || (root !== doc.body && mount !== doc.body)) return null;
21534:         try {
21535:             return missionValueIdFromUrl(doc.location?.href, location.href) !== null
21536:                 ? doc.getElementById?.('navbar-alarm-spacer') || null
21537:                 : null;
21538:         } catch (err) {
21539:             return null;
```

#### Context around line 21528

```javascript
21516:     }
21517: 
21518:     function clearMissionValueIndicators() {
21519:         for (const context of transportSweepDocumentContexts()) removeMissionValueRows(context.doc);
21520:     }
21521: 
21522: 
21523:         function missionValueToolbarSpacer(root, mount) {
21524:         const scopes = [root, mount].filter(Boolean);
21525:         for (const scope of scopes) {
21526:             try {
21527:                 if (scope.matches?.('#navbar-alarm-spacer')) return scope;
21528:                 const spacer = scope.querySelector?.('#navbar-alarm-spacer');
21529:                 if (spacer) return spacer;
21530:             } catch (err) {}
21531:         }
21532:         const doc = root?.ownerDocument || mount?.ownerDocument || null;
21533:         if (!doc || (root !== doc.body && mount !== doc.body)) return null;
21534:         try {
21535:             return missionValueIdFromUrl(doc.location?.href, location.href) !== null
21536:                 ? doc.getElementById?.('navbar-alarm-spacer') || null
21537:                 : null;
21538:         } catch (err) {
21539:             return null;
21540:         }
```

#### Context around line 21536

```javascript
21524:         const scopes = [root, mount].filter(Boolean);
21525:         for (const scope of scopes) {
21526:             try {
21527:                 if (scope.matches?.('#navbar-alarm-spacer')) return scope;
21528:                 const spacer = scope.querySelector?.('#navbar-alarm-spacer');
21529:                 if (spacer) return spacer;
21530:             } catch (err) {}
21531:         }
21532:         const doc = root?.ownerDocument || mount?.ownerDocument || null;
21533:         if (!doc || (root !== doc.body && mount !== doc.body)) return null;
21534:         try {
21535:             return missionValueIdFromUrl(doc.location?.href, location.href) !== null
21536:                 ? doc.getElementById?.('navbar-alarm-spacer') || null
21537:                 : null;
21538:         } catch (err) {
21539:             return null;
21540:         }
21541:     }
21542: 
21543:     function missionValueToolbarBar(spacer, root, mount) {
21544:         if (spacer?.isConnected) {
21545:             try {
21546:                 return spacer.closest?.('.navbar-header.flex-row.flex-nowrap.align-items-center, .navbar-header') || spacer.parentElement || null;
21547:             } catch (err) {}
21548:         }
```

#### Context around line 21552

```javascript
21540:         }
21541:     }
21542: 
21543:     function missionValueToolbarBar(spacer, root, mount) {
21544:         if (spacer?.isConnected) {
21545:             try {
21546:                 return spacer.closest?.('.navbar-header.flex-row.flex-nowrap.align-items-center, .navbar-header') || spacer.parentElement || null;
21547:             } catch (err) {}
21548:         }
21549:         for (const scope of [root, mount]) {
21550:             try {
21551:                 const bars = Array.from(scope?.querySelectorAll?.('.navbar-header.flex-row.flex-nowrap.align-items-center, .navbar-header') || []);
21552:                 const bar = bars.find(candidate => candidate.querySelector?.('#navbar-alarm-spacer'));
21553:                 if (bar) return bar;
21554:             } catch (err) {}
21555:         }
21556:         return null;
21557:     }
21558: 
21559:     function missionValueSpacerVisibleWidth(spacer) {
21560:         if (!spacer?.isConnected) return 0;
21561:         try {
21562:             const view = spacer.ownerDocument?.defaultView || pageWindow;
21563:             const style = view?.getComputedStyle?.(spacer);
21564:             if (style?.display === 'none' || style?.visibility === 'hidden' || style?.visibility === 'collapse' || Number(style?.opacity) === 0) return 0;
```

### `Mission Value`

Matches: 8580, 9183, 21577, 21580, 21722, 27393, 28323

#### Context around line 8580

```javascript
08568:         #${SCRIPT.criticalDrawerId} .mcms-summary-aged { border-color:rgba(255,202,40,.55) !important; }
08569:         #${SCRIPT.criticalDrawerId} .mcms-summary-no-scene { border-color:rgba(255,72,72,.72) !important; color:#ff9d9d !important; }
08570:         #${SCRIPT.criticalDrawerId} .mcms-summary-enroute { border-color:rgba(74,190,255,.72) !important; color:#9cddff !important; }
08571:         #${SCRIPT.criticalDrawerId} .mcms-summary-assistance { border-color:rgba(255,143,45,.72) !important; color:#ffc07c !important; }
08572:         #${SCRIPT.criticalDrawerId} .mcms-summary-clearing {
08573:             border-color:rgba(55,222,125,.78) !important;
08574:             background:linear-gradient(135deg,rgba(8,86,44,.52),rgba(5,57,31,.34)) !important;
08575:             color:#bdf7d2 !important;
08576:             box-shadow:inset 0 0 0 1px rgba(55,222,125,.08),0 0 10px rgba(55,222,125,.10) !important;
08577:             animation:mcms-critical-summary-clearing 2.6s ease-in-out infinite !important;
08578:         }
08579: 
08580:         /* Mission Value overview and interactive Mission Age Watch filters. */
08581:         #${SCRIPT.criticalDrawerId} .mcms-critical-values {
08582:             display:block !important;
08583:             margin-top:6px !important;
08584:             padding:6px !important;
08585:             border:1px solid rgba(126,190,235,.24) !important;
08586:             border-radius:8px !important;
08587:             background:linear-gradient(135deg,rgba(7,21,34,.78),rgba(20,29,42,.68)) !important;
08588:             box-shadow:inset 0 0 0 1px rgba(255,255,255,.035) !important;
08589:         }
08590:         #${SCRIPT.criticalDrawerId} .mcms-critical-values-head {
08591:             display:flex !important;
08592:             align-items:center !important;
```

#### Context around line 9183

```javascript
09171:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-label { grid-column:1 / -1 !important; min-height:14px !important; }
09172:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter { min-height:29px !important; padding:4px 5px !important; }
09173:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-type-filter span { font-size:6.8px !important; }
09174:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary { grid-template-columns:repeat(2,minmax(0,1fr)) !important; }
09175:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-summary-card span { font-size:7px !important; }
09176:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-summary-clearing { grid-column:1 / -1 !important; }
09177:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-row { padding:8px !important; }
09178:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-name { font-size:11.5px !important; }
09179:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-lowerline { grid-template-columns:minmax(0,1fr) 106px !important; gap:4px !important; }
09180:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy strong { font-size:8.5px !important; }
09181:         html[data-mcms-mobile-active="true"] #${SCRIPT.criticalDrawerId} .mcms-critical-state-copy small { font-size:7.5px !important; }
09182: 
09183:         /* v3.16.1: compact Mission Value rail inside the Mission Age Watch header. */
09184:         #${SCRIPT.criticalDrawerId} .mcms-drawer-head {
09185:             grid-template-columns:minmax(0,1fr) auto !important;
09186:             grid-template-rows:auto auto !important;
09187:             column-gap:8px !important;
09188:             row-gap:3px !important;
09189:         }
09190:         #${SCRIPT.criticalDrawerId} .mcms-drawer-heading { grid-column:1 !important; grid-row:1 !important; }
09191:         #${SCRIPT.criticalDrawerId} .mcms-drawer-actions { grid-column:2 !important; grid-row:1 !important; }
09192:         #${SCRIPT.criticalDrawerId} .mcms-critical-values {
09193:             grid-column:1 / -1 !important;
09194:             grid-row:2 !important;
09195:             display:grid !important;
```

#### Context around line 21577

```javascript
21565:         } catch (err) {}
21566:         try {
21567:             const rect = spacer.getBoundingClientRect?.();
21568:             return rect && rect.width > 0 ? Math.max(0, Math.floor(rect.width)) : 0;
21569:         } catch (err) {
21570:             return 0;
21571:         }
21572:     }
21573: 
21574:     function missionValuePresentation(availableWidth, formatted) {
21575:         const width = Math.max(0, Number(availableWidth) || 0);
21576:         const value = String(formatted || '');
21577:         if (width >= 176) return { mode: 'full', text: `Mission Value · ${value}` };
21578:         if (width >= 110) return { mode: 'short', text: `Value · ${value}` };
21579:         if (width >= 58) return { mode: 'value', text: value };
21580:         return { mode: 'fallback', text: `Mission Value · ${value}` };
21581:     }
21582: 
21583:     function missionValuePreferredCandidates(candidateList) {
21584:         const groups = new Map();
21585:         for (const candidate of Array.from(candidateList || [])) {
21586:             const missionId = normaliseMissionId(candidate?.missionId);
21587:             if (missionId === null || !candidate?.mount?.isConnected) continue;
21588:             if (!groups.has(missionId)) groups.set(missionId, []);
21589:             groups.get(missionId).push(candidate);
```

#### Context around line 21580

```javascript
21568:             return rect && rect.width > 0 ? Math.max(0, Math.floor(rect.width)) : 0;
21569:         } catch (err) {
21570:             return 0;
21571:         }
21572:     }
21573: 
21574:     function missionValuePresentation(availableWidth, formatted) {
21575:         const width = Math.max(0, Number(availableWidth) || 0);
21576:         const value = String(formatted || '');
21577:         if (width >= 176) return { mode: 'full', text: `Mission Value · ${value}` };
21578:         if (width >= 110) return { mode: 'short', text: `Value · ${value}` };
21579:         if (width >= 58) return { mode: 'value', text: value };
21580:         return { mode: 'fallback', text: `Mission Value · ${value}` };
21581:     }
21582: 
21583:     function missionValuePreferredCandidates(candidateList) {
21584:         const groups = new Map();
21585:         for (const candidate of Array.from(candidateList || [])) {
21586:             const missionId = normaliseMissionId(candidate?.missionId);
21587:             if (missionId === null || !candidate?.mount?.isConnected) continue;
21588:             if (!groups.has(missionId)) groups.set(missionId, []);
21589:             groups.get(missionId).push(candidate);
21590:         }
21591:         const selected = [];
21592:         for (const group of groups.values()) {
```

#### Context around line 21722

```javascript
21710:         if (badge.parentNode !== row) row.appendChild(badge);
21711: 
21712:         if (useToolbar) {
21713:             if (row.parentNode !== toolbarSpacer) toolbarSpacer.appendChild(row);
21714:         } else if (toolbar?.parentNode) {
21715:             if (row.parentNode !== toolbar.parentNode || row.previousElementSibling !== toolbar) {
21716:                 toolbar.parentNode.insertBefore(row, toolbar.nextSibling);
21717:             }
21718:         } else if (row.parentNode !== mount || row !== mount.firstElementChild) {
21719:             mount.insertBefore(row, mount.firstChild || null);
21720:         }
21721: 
21722:         const fullLabel = `Mission Value · ${formatted}`;
21723:         const text = useToolbar ? presentation.text : fullLabel;
21724:         if (badge.textContent !== text) badge.textContent = text;
21725:         badge.title = `${fullLabel} · ${details.source}`;
21726:         badge.setAttribute('aria-label', fullLabel);
21727:         row.setAttribute('aria-label', fullLabel);
21728:         return row;
21729:     }
21730: 
21731:     function scheduleMissionValueScan(delay = 80) {
21732:         runtimeClearTimeout(missionValueScanTimer);
21733:         missionValueScanTimer = runtimeSetTimeout(() => {
21734:             missionValueScanTimer = null;
```

### `missionValue`

Matches: 1369, 1370, 1371, 1372, 1373, 1374, 1416, 1508, 21412, 21423, 21427, 21435, 21464, 21471, 21478, 21489, 21493, 21495, 21497, 21498
Additional matches omitted: 41

#### Context around line 1369

```javascript
01357:     let financeArchiveScanBusy = false;
01358:     let financeArchiveScanCancelled = false;
01359:     let financeRuleRefreshPromise = null;
01360:     let financePolicyRefreshPromise = null;
01361:     let tabletModeActive = false;
01362:     let mobileModeActive = false;
01363:     let activeDeviceLayout = 'desktop';
01364:     let tabletLayoutTimer = null;
01365:     let tabletDockResizeObserver = null;
01366:     let tabletDockObservedMap = null;
01367:     let desktopPanelResizeObserver = null;
01368:     let desktopPanelObservedElements = new Set();
01369:     let missionValueScanTimer = null;
01370:     let missionValueFeatureInstalled = false;
01371:     const missionValueObservedDocuments = new WeakSet();
01372:     const missionValueObservedFrames = new WeakSet();
01373:     const missionValueHostObservers = new Map();
01374:     const missionValueRetryState = new WeakMap();
01375:     let commandBarAnimationTimer = null;
01376:     let commandBarAnimating = false;
01377:     let helpGuideDocumentCache = '';
01378:     let helpGuideLoadedAt = 0;
01379:     let helpGuideLoadPromise = null;
01380:     let helpCenterReturnFocus = null;
01381: 
```

#### Context around line 1370

```javascript
01358:     let financeArchiveScanCancelled = false;
01359:     let financeRuleRefreshPromise = null;
01360:     let financePolicyRefreshPromise = null;
01361:     let tabletModeActive = false;
01362:     let mobileModeActive = false;
01363:     let activeDeviceLayout = 'desktop';
01364:     let tabletLayoutTimer = null;
01365:     let tabletDockResizeObserver = null;
01366:     let tabletDockObservedMap = null;
01367:     let desktopPanelResizeObserver = null;
01368:     let desktopPanelObservedElements = new Set();
01369:     let missionValueScanTimer = null;
01370:     let missionValueFeatureInstalled = false;
01371:     const missionValueObservedDocuments = new WeakSet();
01372:     const missionValueObservedFrames = new WeakSet();
01373:     const missionValueHostObservers = new Map();
01374:     const missionValueRetryState = new WeakMap();
01375:     let commandBarAnimationTimer = null;
01376:     let commandBarAnimating = false;
01377:     let helpGuideDocumentCache = '';
01378:     let helpGuideLoadedAt = 0;
01379:     let helpGuideLoadPromise = null;
01380:     let helpCenterReturnFocus = null;
01381: 
01382:     function defaultState() {
```

#### Context around line 1371

```javascript
01359:     let financeRuleRefreshPromise = null;
01360:     let financePolicyRefreshPromise = null;
01361:     let tabletModeActive = false;
01362:     let mobileModeActive = false;
01363:     let activeDeviceLayout = 'desktop';
01364:     let tabletLayoutTimer = null;
01365:     let tabletDockResizeObserver = null;
01366:     let tabletDockObservedMap = null;
01367:     let desktopPanelResizeObserver = null;
01368:     let desktopPanelObservedElements = new Set();
01369:     let missionValueScanTimer = null;
01370:     let missionValueFeatureInstalled = false;
01371:     const missionValueObservedDocuments = new WeakSet();
01372:     const missionValueObservedFrames = new WeakSet();
01373:     const missionValueHostObservers = new Map();
01374:     const missionValueRetryState = new WeakMap();
01375:     let commandBarAnimationTimer = null;
01376:     let commandBarAnimating = false;
01377:     let helpGuideDocumentCache = '';
01378:     let helpGuideLoadedAt = 0;
01379:     let helpGuideLoadPromise = null;
01380:     let helpCenterReturnFocus = null;
01381: 
01382:     function defaultState() {
01383:         return {
```

#### Context around line 1372

```javascript
01360:     let financePolicyRefreshPromise = null;
01361:     let tabletModeActive = false;
01362:     let mobileModeActive = false;
01363:     let activeDeviceLayout = 'desktop';
01364:     let tabletLayoutTimer = null;
01365:     let tabletDockResizeObserver = null;
01366:     let tabletDockObservedMap = null;
01367:     let desktopPanelResizeObserver = null;
01368:     let desktopPanelObservedElements = new Set();
01369:     let missionValueScanTimer = null;
01370:     let missionValueFeatureInstalled = false;
01371:     const missionValueObservedDocuments = new WeakSet();
01372:     const missionValueObservedFrames = new WeakSet();
01373:     const missionValueHostObservers = new Map();
01374:     const missionValueRetryState = new WeakMap();
01375:     let commandBarAnimationTimer = null;
01376:     let commandBarAnimating = false;
01377:     let helpGuideDocumentCache = '';
01378:     let helpGuideLoadedAt = 0;
01379:     let helpGuideLoadPromise = null;
01380:     let helpCenterReturnFocus = null;
01381: 
01382:     function defaultState() {
01383:         return {
01384:             uiTheme: 'mapCommand',
```

#### Context around line 1373

```javascript
01361:     let tabletModeActive = false;
01362:     let mobileModeActive = false;
01363:     let activeDeviceLayout = 'desktop';
01364:     let tabletLayoutTimer = null;
01365:     let tabletDockResizeObserver = null;
01366:     let tabletDockObservedMap = null;
01367:     let desktopPanelResizeObserver = null;
01368:     let desktopPanelObservedElements = new Set();
01369:     let missionValueScanTimer = null;
01370:     let missionValueFeatureInstalled = false;
01371:     const missionValueObservedDocuments = new WeakSet();
01372:     const missionValueObservedFrames = new WeakSet();
01373:     const missionValueHostObservers = new Map();
01374:     const missionValueRetryState = new WeakMap();
01375:     let commandBarAnimationTimer = null;
01376:     let commandBarAnimating = false;
01377:     let helpGuideDocumentCache = '';
01378:     let helpGuideLoadedAt = 0;
01379:     let helpGuideLoadPromise = null;
01380:     let helpCenterReturnFocus = null;
01381: 
01382:     function defaultState() {
01383:         return {
01384:             uiTheme: 'mapCommand',
01385:             theme: getLegacyTheme(),
```

### `runtimeOnCleanup`

Matches: 771, 796, 839, 16616, 21804, 21834, 29386, 30009

#### Context around line 771

```javascript
00759:                 } else {
00760:                     task.running = false;
00761:                 }
00762:             } catch (err) {
00763:                 task.running = false;
00764:                 console.debug(`[${SCRIPT.name}] Scheduled task ${task.name} failed.`, err);
00765:             }
00766:         }
00767: 
00768:         runtimeTaskTimer = runtimeSetTimeout(runtimeRunScheduledTasks, Math.max(50, Math.min(hidden ? 5 * 60 * 1000 : 60000, nextDelay)));
00769:     }
00770: 
00771:     function runtimeOnCleanup(callback) {
00772:         if (typeof callback === 'function') runtime.cleanupCallbacks.push(callback);
00773:         return callback;
00774:     }
00775: 
00776: 
00777:     function runtimeRunWhenIdle(callback, timeout = STARTUP_IDLE_TIMEOUT_MS) {
00778:         if (runtime.destroyed || typeof callback !== 'function') return null;
00779:         const maxWait = Math.max(50, Number(timeout) || STARTUP_IDLE_TIMEOUT_MS);
00780:         let settled = false;
00781:         let idleId = null;
00782:         let fallbackTimer = null;
00783: 
```

#### Context around line 796

```javascript
00784:         const run = deadline => {
00785:             if (settled || runtime.destroyed) return;
00786:             settled = true;
00787:             if (fallbackTimer !== null) runtimeClearTimeout(fallbackTimer);
00788:             fallbackTimer = null;
00789:             callback(deadline || { didTimeout: true, timeRemaining: () => 0 });
00790:         };
00791: 
00792:         if (typeof pageWindow.requestIdleCallback === 'function') {
00793:             try {
00794:                 idleId = pageWindow.requestIdleCallback(run, { timeout: maxWait });
00795:                 fallbackTimer = runtimeSetTimeout(() => run(null), maxWait + 120);
00796:                 runtimeOnCleanup(() => {
00797:                     if (settled || idleId === null || typeof pageWindow.cancelIdleCallback !== 'function') return;
00798:                     try { pageWindow.cancelIdleCallback(idleId); } catch (err) {}
00799:                 });
00800:                 return idleId;
00801:             } catch (err) {}
00802:         }
00803: 
00804:         fallbackTimer = runtimeSetTimeout(() => run(null), Math.min(350, maxWait));
00805:         return fallbackTimer;
00806:     }
00807: 
00808:     function startupClock() {
```

#### Context around line 839

```javascript
00827:         const controller = typeof Controller === 'function' ? new Controller() : null;
00828:         if (controller) runtime.fetchControllers.add(controller);
00829:         const fetchFunction = pageWindow.fetch || globalThis.fetch;
00830:         if (typeof fetchFunction !== 'function') {
00831:             if (controller) runtime.fetchControllers.delete(controller);
00832:             return Promise.reject(new Error('Browser fetch is unavailable.'));
00833:         }
00834:         const options = controller ? { ...init, signal: controller.signal } : init;
00835:         return Promise.resolve(fetchFunction.call(pageWindow, input, options))
00836:             .finally(() => { if (controller) runtime.fetchControllers.delete(controller); });
00837:     }
00838: 
00839:     runtimeOnCleanup(() => {
00840:         runtimeTasks.clear();
00841:         runtimeClearTimeout(runtimeTaskTimer);
00842:         runtimeTaskTimer = null;
00843:     });
00844: 
00845:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4100__ = true;
00846:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V3130__ = true;
00847:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V3121__ = true;
00848:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V380__ = true;
00849:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V341__ = true;
00850:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V340__ = true;
00851:     pageWindow.__MC_MAP_COMMAND_TOOLKIT_V318__ = true;
```

#### Context around line 16616

```javascript
16604:         if (!hud) return;
16605:         const total = Math.max(0, Number(sweep.missionTotal) || Number(sweep.queue?.length) || 0);
16606:         const index = total ? Math.min(total, Math.max(1, Number(sweep.missionIndex) || 1)) : 0;
16607:         const phase = sweep.hudFinal ? (sweep.statusLevel === 'error' ? 'Finished with errors' : 'Sweep complete')
16608:             : sweep.stopRequested ? 'Stopping'
16609:             : 'Sweep running';
16610:         const current = String(sweep.currentItem || '').trim();
16611:         const message = String(sweep.statusMessage || (sweep.running ? 'Preparing patient transport sweep' : phase)).trim();
16612:         hud.dataset.state = sweep.hudFinal ? (sweep.errors ? 'error' : 'complete') : sweep.stopRequested ? 'stopping' : 'running';
16613:         hud.innerHTML = `<div class="mcms-sweep-hud-head"><span><i></i>Patient Transport Sweep</span><b>${escapeHtml(phase)}</b></div><div class="mcms-sweep-hud-status">${escapeHtml(message)}</div>${current ? `<div class="mcms-sweep-hud-current">${escapeHtml(current)}</div>` : ''}<div class="mcms-sweep-hud-stats"><span><b>${index}/${total}</b><small>Missions</small></span><span class="mcms-sweep-hud-cleared"><b>${Math.max(0, Number(sweep.cleared) || 0)}</b><small>Patients cleared</small></span><span><b>${Math.max(0, Number(sweep.skipped) || 0)}</b><small>Skipped</small></span><span><b>${Math.max(0, Number(sweep.errors) || 0)}</b><small>Errors</small></span></div><div class="mcms-sweep-hud-foot"><span>${escapeHtml(transportSweepHudElapsed())} elapsed</span><span>${Math.max(0, Number(sweep.processed) || 0)} processed</span></div>`;
16614:     }
16615: 
16616:     runtimeOnCleanup(removeTransportSweepHud);
16617: 
16618:     function renderTransportSweepPanel() {
16619:         renderTransportSweepHud();
16620:         const host = document.querySelector(`#${SCRIPT.panelId} [data-transport-sweep]`);
16621:         if (!host) return;
16622:         const runtime = transportSweepRuntime;
16623:         const queue = runtime.queue || [];
16624:         const currentId = normaliseMissionId(runtime.currentMissionId);
16625:         const status = runtime.running ? 'RUNNING' : runtime.stopRequested ? 'STOPPING' : queue.length ? 'READY' : 'IDLE';
16626:         const list = queue.length ? queue.map((item, index) => {
16627:             const current = currentId !== null && normaliseMissionId(item.missionId) === currentId;
16628:             return `<div class="mcms-sweep-entry ${current ? 'mcms-current' : ''}"><div><span class="mcms-sweep-title">${escapeHtml(`${index + 1}. ${item.caption}`)}</span><span class="mcms-sweep-meta">Mission ${escapeHtml(item.missionId)} · ${escapeHtml(item.requirement)}</span></div><span class="mcms-sweep-count">${escapeHtml(item.count)} req</span></div>`;
```

#### Context around line 21804

```javascript
21792:     function clearMissionValueDocumentStyles() {
21793:         for (const context of transportSweepDocumentContexts()) {
21794:             if (context.doc === document) continue;
21795:             try { context.doc.getElementById?.('mcms-mission-value-document-style')?.remove(); } catch (err) {}
21796:         }
21797:     }
21798: 
21799:     function observeMissionValueFrame(frame) {
21800:         if (!frame || missionValueObservedFrames.has(frame)) return;
21801:         missionValueObservedFrames.add(frame);
21802:         const onLoad = () => scheduleMissionValueScan(40);
21803:         frame.addEventListener('load', onLoad);
21804:         runtimeOnCleanup(() => frame.removeEventListener('load', onLoad));
21805:     }
21806: 
21807:         function observeMissionValueDocument(doc) {
21808:         if (!doc) return;
21809:         ensureMissionValueDocumentStyle(doc);
21810:         if (missionValueObservedDocuments.has(doc)) return;
21811:         missionValueObservedDocuments.add(doc);
21812:         let frames = [];
21813:         try { frames = Array.from(doc.querySelectorAll('iframe, frame')); } catch (err) {}
21814:         frames.forEach(observeMissionValueFrame);
21815:         const root = doc.documentElement || doc.body;
21816:         if (!root) return;
```

### `runtimeTrackObserver`

Matches: 661, 14389, 14568, 19586, 21656, 21660, 21818, 24584, 29363, 29581, 29599, 29717, 29776

#### Context around line 661

```javascript
00649:         if (id === null || id === undefined) return;
00650:         runtime.animationFrames.delete(id);
00651:         try { pageWindow.cancelAnimationFrame(id); } catch (err) {}
00652:     }
00653: 
00654:     function runtimeListen(target, type, listener, options) {
00655:         if (!target?.addEventListener || runtime.destroyed) return listener;
00656:         target.addEventListener(type, listener, options);
00657:         runtime.listeners.push({ target, type, listener, options });
00658:         return listener;
00659:     }
00660: 
00661:     function runtimeTrackObserver(observer) {
00662:         if (!observer) return observer;
00663:         if (runtime.destroyed) {
00664:             try { observer.disconnect(); } catch (err) {}
00665:             return observer;
00666:         }
00667:         runtime.observers.add(observer);
00668:         return observer;
00669:     }
00670: 
00671:     function runtimeUntrackObserver(observer, disconnect = true) {
00672:         if (!observer) return;
00673:         if (disconnect) {
```

#### Context around line 14389

```javascript
14377:         }
14378:         stopDesktopPanelWorkspaceObservation();
14379:     }
14380: 
14381:     function observeDesktopPanelWorkspace(mapEl) {
14382:         if (activeDeviceLayout !== 'desktop') {
14383:             stopDesktopPanelWorkspaceObservation();
14384:             return;
14385:         }
14386:         const ResizeObserverCtor = pageWindow.ResizeObserver;
14387:         if (typeof ResizeObserverCtor !== 'function') return;
14388:         if (!desktopPanelResizeObserver) {
14389:             desktopPanelResizeObserver = runtimeTrackObserver(new ResizeObserverCtor(() => {
14390:                 if (runtime.destroyed || activeDeviceLayout !== 'desktop') return;
14391:                 const panel = document.getElementById(SCRIPT.panelId);
14392:                 if (!panel) return;
14393:                 applyDesktopPanelSizing(panel, getLargestLeafletMap());
14394:                 if (!dragState && panel.classList.contains('mcms-open')) schedulePanelPosition(true, 20);
14395:             }));
14396:         }
14397: 
14398:         const viewport = getViewportMetrics();
14399:         const panel = document.getElementById(SCRIPT.panelId);
14400:         const obstructionElements = collectDesktopWorkspaceObstructions(viewport, mapEl, panel)
14401:             .map(item => item.element);
```

#### Context around line 14568

```javascript
14556:         if (tabletDockResizeObserver && tabletDockObservedMap) {
14557:             try { tabletDockResizeObserver.unobserve(tabletDockObservedMap); } catch (err) {}
14558:             tabletDockObservedMap = null;
14559:         }
14560:     }
14561: 
14562:     function observeTabletMapArea(mapEl) {
14563:         if (!isTouchLayoutActive() || !mapEl) return;
14564:         const ResizeObserverCtor = pageWindow.ResizeObserver;
14565:         if (typeof ResizeObserverCtor !== 'function') return;
14566: 
14567:         if (!tabletDockResizeObserver) {
14568:             tabletDockResizeObserver = runtimeTrackObserver(new ResizeObserverCtor(entries => {
14569:                 if (!isTouchLayoutActive() || runtime.destroyed) return;
14570:                 if (entries.some(entry => entry?.target === tabletDockObservedMap)) fitControlToMap();
14571:             }));
14572:         }
14573: 
14574:         if (tabletDockObservedMap === mapEl) return;
14575:         if (tabletDockObservedMap) {
14576:             try { tabletDockResizeObserver.unobserve(tabletDockObservedMap); } catch (err) {}
14577:         }
14578:         tabletDockObservedMap = mapEl;
14579:         try { tabletDockResizeObserver.observe(mapEl); } catch (err) {}
14580:     }
```

#### Context around line 19586

```javascript
19574:             feed.addEventListener('pointerdown', () => {
19575:                 feed.classList.add('mcms-feed-paused');
19576:                 runtimeSetTimeout(() => feed?.classList?.remove('mcms-feed-paused'), 1800);
19577:             }, { passive: true });
19578:             document.body.appendChild(feed);
19579:         }
19580: 
19581:         if (state.economyMode) {
19582:             resetMajorIncidentFeedObserver();
19583:         } else if (majorIncidentFeedObservedElement !== feed && typeof pageWindow.ResizeObserver === 'function') {
19584:             resetMajorIncidentFeedObserver();
19585:             majorIncidentFeedObservedElement = feed;
19586:             majorIncidentFeedResizeObserver = runtimeTrackObserver(new pageWindow.ResizeObserver(() => {
19587:                 if (feed.isConnected) scheduleMajorIncidentFeedMotion(feed, false, 70);
19588:                 else recoverMajorIncidentFeed('header replacement');
19589:             }));
19590:             majorIncidentFeedResizeObserver.observe(feed);
19591:             const viewport = feed.querySelector('.mcms-incident-feed-viewport');
19592:             if (viewport) majorIncidentFeedResizeObserver.observe(viewport);
19593:         }
19594: 
19595:         scheduleMajorIncidentFeedLayout();
19596:         return feed;
19597:     }
19598: 
```

#### Context around line 21656

```javascript
21644:         if (!spacer?.isConnected || !toolbar?.isConnected) return;
21645:         const existing = missionValueHostObservers.get(spacer);
21646:         if (existing?.toolbar === toolbar) return;
21647:         if (existing) {
21648:             try { existing.resizeObserver?.disconnect?.(); } catch (err) {}
21649:             try { existing.mutationObserver?.disconnect?.(); } catch (err) {}
21650:         }
21651:         const view = spacer.ownerDocument?.defaultView || pageWindow;
21652:         const ResizeObserverCtor = view?.ResizeObserver || pageWindow.ResizeObserver;
21653:         const MutationObserverCtor = view?.MutationObserver || pageWindow.MutationObserver || MutationObserver;
21654:         const record = { toolbar, resizeObserver: null, mutationObserver: null };
21655:         if (typeof ResizeObserverCtor === 'function') {
21656:             record.resizeObserver = runtimeTrackObserver(new ResizeObserverCtor(() => scheduleMissionValueScan(24)));
21657:             record.resizeObserver.observe(spacer);
21658:         }
21659:         if (typeof MutationObserverCtor === 'function') {
21660:             record.mutationObserver = runtimeTrackObserver(new MutationObserverCtor(() => scheduleMissionValueScan(24)));
21661:             record.mutationObserver.observe(toolbar, { childList: true, subtree: false });
21662:         }
21663:         missionValueHostObservers.set(spacer, record);
21664:     }
21665: 
21666:     
21667: 
21668:     
```

### `createPanel`

Matches: 27693, 28174, 29113

#### Context around line 27693

```javascript
27681:             suppressNextOutsideClick = true;
27682:             showToast('Menu position saved');
27683:             runtimeSetTimeout(() => { suppressNextOutsideClick = false; }, 250);
27684:         }
27685: 
27686:         if (event) {
27687:             event.preventDefault();
27688:             event.stopPropagation();
27689:         }
27690:     }
27691: 
27692:     function openPanel() {
27693:         const panel = document.getElementById(SCRIPT.panelId) || createPanel();
27694:         if (!panel) return;
27695:         applyRootAttributes();
27696:         refreshTabletModeUi(panel);
27697:         panel.classList.add('mcms-open');
27698:         panel.setAttribute('aria-hidden', 'false');
27699:         const menuButton = document.querySelector(`#${SCRIPT.controlId} .mcms-menu-btn`);
27700:         menuButton?.setAttribute('aria-expanded', 'true');
27701:         fitControlToMap();
27702:         runtimeSetTimeout(() => positionPanelOverlay(true), 0);
27703:     }
27704: 
27705:     function closePanel({ restoreFocus = false } = {}) {
```

#### Context around line 28174

```javascript
28162:             if (dockToggleButton) { toggleCommandBar(); return; }
28163:             if (toggleButton) { toggleFeature(toggleButton.dataset.toggle); return; }
28164:             if (actionButton) handleAction(actionButton);
28165:         });
28166: 
28167:         control.addEventListener('contextmenu', event => { event.preventDefault(); openPanel(); });
28168: 
28169:         mapEl.appendChild(control);
28170:         renderScreenPins();
28171:         updateUI();
28172:     }
28173: 
28174:     function createPanel() {
28175:         const existingPanel = document.getElementById(SCRIPT.panelId);
28176:         if (existingPanel) { settingsPanelActivated = true; return existingPanel; }
28177:         const panelStartedAt = startupClock();
28178:         settingsPanelActivated = true;
28179:         const panel = document.createElement('div');
28180:         panel.id = SCRIPT.panelId;
28181:         panel.setAttribute('role', 'dialog');
28182:         panel.setAttribute('aria-modal', 'false');
28183:         panel.setAttribute('aria-hidden', 'true');
28184:         panel.setAttribute('aria-label', `${SCRIPT.name} menu`);
28185: 
28186:         const buildUiThemeButtons = () => UI_THEME_ORDER.map(key => {
```

#### Context around line 29113

```javascript
29101:         const economyStatus = panel.querySelector('.mcms-economy-status');
29102:         if (economyStatus) economyStatus.textContent = state.economyMode
29103:             ? 'Economy Mode is ON: static visual effects, adaptive refresh intervals and off-screen vehicle/building layer culling are active.'
29104:             : 'Economy Mode is OFF. Use the leaf button beside the map-menu opener to reduce CPU, GPU and marker workload.';
29105:         const nudge = panel.querySelector('.mcms-nudge-value');
29106:         if (nudge) nudge.textContent = `X ${state.nudge.x} / Y ${state.nudge.y}`;
29107:         if (panel.classList.contains('mcms-open') && state.activeTab === 'settings') renderProfiles();
29108:         if ((panel.classList.contains('mcms-open') && state.activeTab === 'ops') || operationalUiIsVisible()) renderOperationalPanels();
29109:     }
29110: 
29111:     function ensureUi() {
29112:         const mapEl = getLargestLeafletMap();
29113:         if (settingsPanelActivated && !document.getElementById(SCRIPT.panelId)) createPanel();
29114:         if (mapEl) {
29115:             createControl(mapEl);
29116:             const map = findLeafletMapInstance(false);
29117:             if (state.economyMode && map) { applyLeafletEconomyPolicy(map); scheduleEconomyLayerSync(0); }
29118:             if (state.majorIncidentFeed.enabled && operationalStartupComplete) scheduleMajorIncidentFeedRender(0);
29119:             else if (!state.majorIncidentFeed.enabled) removeMajorIncidentFeed();
29120:             const payoutOverlay = document.getElementById(SCRIPT.payoutFlashId);
29121:             if (payoutOverlay?.classList.contains('mcms-payout-active')) positionPayoutFlashOverlay(payoutOverlay, mapEl);
29122:         }
29123:         return Boolean(mapEl && document.getElementById(SCRIPT.controlId));
29124:     }
29125: 
```

### `function boot(`

Matches: 29759

#### Context around line 29759

```javascript
29747:                 scheduleMarkerStateSync(0, false);
29748:                 scheduleDeferredOperationalStartup();
29749:                 runtimeSetTimeout(() => runtimeRunWhenIdle(connectMainMutationObserver, STARTUP_OBSERVER_DELAY_MS), STARTUP_OBSERVER_DELAY_MS);
29750:                 return;
29751:             }
29752:             if (attempts >= 90 || runtime.destroyed) return;
29753:             const delay = attempts < 12 ? 350 : attempts < 30 ? 700 : 1400;
29754:             runtimeSetTimeout(runBootAttempt, delay);
29755:         };
29756:         runtimeSetTimeout(runBootAttempt, 250);
29757:     }
29758: 
29759:     function boot() {
29760:         if (runtime.destroyed || bootStarted) return;
29761:         bootStarted = true;
29762:         bootStartedAt = Date.now();
29763:         const bootPerformanceStartedAt = startupClock();
29764:         applyRootAttributes();
29765:         if (installAllianceBuildingsPageOptimisation()) return;
29766:         createCleanExit();
29767:         if (state.autoLoadAllVehicles) installAutoLoadAllVehicles();
29768:         installMissionMarkerAddHook();
29769:         installRadioMessageHook();
29770:         lastObservedCredits = readCurrentCreditTotal();
29771:         installCreditsUpdateHook();
```

### `data-section="ops"`

No matches.

### `section: 'ops'`

No matches.

### `Ops`

Matches: 20560, 28229, 28342

#### Context around line 20560

```javascript
20548:                     const latest = payoutHistory.slice(0, 3);
20549:                     const older = payoutHistory.slice(3, PAYOUT_HISTORY_LIMIT);
20550:                     html = `
20551:                         <div class="mcms-history-latest">${latest.map(historyEntryHtml).join('')}</div>
20552:                         ${older.length ? `<details class="mcms-history-older" data-ops-history-older>
20553:                             <summary>Earlier payouts (${older.length})</summary>
20554:                             <div class="mcms-history-scroll">${older.map(historyEntryHtml).join('')}</div>
20555:                         </details>` : ''}`;
20556:                 }
20557:                 setInnerHtmlIfChanged(history, html, `history:${payoutHistory.map(entry => entry.id).join('|')}`);
20558:             }
20559:         }
20560:         // Keep Mission Age Watch independent from the personal-only Ops preview.
20561:         // The drawer rebuilds its full Personal/Event/Alliance dataset only when open.
20562:         if (criticalDrawerVisible) renderCriticalDrawer(null, criticalRenderOptions || {});
20563:     }
20564: 
20565:     function vehicleCodeStatusSnapshot() {
20566:         const counts = new Map();
20567:         const seen = new Set();
20568:         let total = 0;
20569: 
20570:         for (const vehicle of getPersonalVehicleRecords()) {
20571:             const vehicleId = vehicleRecordId(vehicle) || `anonymous:${seen.size}`;
20572:             if (seen.has(vehicleId)) continue;
```

#### Context around line 28229

```javascript
28217:                     <div class="mcms-drag-handle" title="Hold left-click and drag this bar to move the menu">
28218:                         <span class="mcms-title">☰ DRAG MENU HERE</span>
28219:                         <span class="mcms-subtitle">Hold left-click on this title area. Position saves.</span>
28220:                     </div>
28221:                     <button class="mcms-reset-panel" type="button" data-action="panel-reset" title="Reset menu position">↺</button>
28222:                     <button class="mcms-help-button" type="button" data-action="open-help-center" title="Open searchable Help Centre" aria-label="Open searchable Help Centre">?</button>
28223:                     <button class="mcms-close" type="button" title="Close">×</button>
28224:                 </div>
28225:                 <div class="mcms-tabs">
28226:                     <button class="mcms-tab-btn" type="button" data-tab="skins">Skins</button>
28227:                     <button class="mcms-tab-btn" type="button" data-tab="tools">Tools</button>
28228:                     <button class="mcms-tab-btn" type="button" data-tab="resources">Resources</button>
28229:                     <button class="mcms-tab-btn" type="button" data-tab="ops">Ops</button>
28230:                     <button class="mcms-tab-btn" type="button" data-tab="payouts">Payouts</button>
28231:                     <button class="mcms-tab-btn" type="button" data-tab="discord">Finance</button>
28232:                     <button class="mcms-tab-btn" type="button" data-tab="places">Places</button>
28233:                     <button class="mcms-tab-btn" type="button" data-tab="settings">Settings</button>
28234:                 </div>
28235:             </div>
28236:             <section class="mcms-tab-panel" data-panel="skins">
28237:                 <div class="mcms-section-label">Interface theme</div>
28238:                 <div class="mcms-ui-theme-grid">${uiThemeButtons}</div>
28239:                 <div class="mcms-status mcms-ui-theme-status">Interface themes restyle the complete toolkit without changing your selected operational map skin.</div>
28240:                 <div class="mcms-section-label">Core skins</div>
28241:                 <div class="mcms-grid-2">${coreThemeButtons}</div>
```

#### Context around line 28342

```javascript
28330:                         <span class="mcms-text"><span class="mcms-label">Vehicle Codes</span><span class="mcms-pill">VIEW</span></span>
28331:                     </button>
28332:                 </div>
28333:                 <div class="mcms-row"><span class="mcms-row-label">Stuck after</span><select class="mcms-select" data-setting="stuck-threshold"><option value="10">10 minutes</option><option value="15">15 minutes</option><option value="20">20 minutes</option><option value="30">30 minutes</option><option value="45">45 minutes</option><option value="60">60 minutes</option></select></div>
28334:                 <div class="mcms-status">Stuck detection resets its timer whenever missing requirements, patients, prisoners, progress value or your assigned-unit state changes.</div>
28335:                 <div class="mcms-section-label">Session Performance</div>
28336:                 <div data-ops-session></div>
28337:                 <div class="mcms-section-label">Mission Age Workflow</div>
28338:                 <div class="mcms-grid-2">
28339:                     <button class="mcms-small-btn" type="button" data-action="open-critical-drawer">Open Mission Drawer (W)</button>
28340:                     <button class="mcms-small-btn" type="button" data-action="fit-critical">Frame Aged</button>
28341:                 </div>
28342:                 <div class="mcms-status">Mission Age and Critical View remain under Tools as the canonical shortcut controls for 6 and 9. Ops provides the mission workflow and dashboard actions.</div>
28343:                 <div class="mcms-section-label">Mission Age Watch · 8H Amber · 16H Orange · 24H Red</div>
28344:                 <div class="mcms-ops-list" data-ops-critical-preview></div>
28345:                 <div class="mcms-section-label">Completion History</div>
28346:                 <div class="mcms-ops-list" data-ops-history></div>
28347:                 <div class="mcms-grid-2" style="margin-top:7px !important">
28348:                     <button class="mcms-small-btn" type="button" data-action="reset-session">Reset Session</button>
28349:                     <button class="mcms-small-btn" type="button" data-action="clear-payout-history">Clear History</button>
28350:                 </div>
28351:             </section>
28352:             <section class="mcms-tab-panel" data-panel="payouts">
28353:                 <div class="mcms-section-label">Emergency Payout Flash</div>
28354:                 <div class="mcms-grid-2">
```

## Function declarations containing mission/window terminology

- line 375: `function repairVisibleMissionChiefMapAfterAllianceExit() {`
- line 587: `function runtimeSetTimeout(callback, delay = 0, ...args) {`
- line 598: `function runtimeClearTimeout(id) {`
- line 604: `function runtimeDelay(delay = 0) {`
- line 622: `function runtimeSetInterval(callback, delay = 0, ...args) {`
- line 631: `function runtimeClearInterval(id) {`
- line 637: `function runtimeRequestAnimationFrame(callback) {`
- line 648: `function runtimeCancelAnimationFrame(id) {`
- line 654: `function runtimeListen(target, type, listener, options) {`
- line 661: `function runtimeTrackObserver(observer) {`
- line 671: `function runtimeUntrackObserver(observer, disconnect = true) {`
- line 682: `function runtimeWakeTaskScheduler(delay = 0) {`
- line 687: `function runtimeRegisterTask(name, intervalMs, callback, options = {}) {`
- line 707: `function runtimeTaskInterval(task) {`
- line 722: `function runtimeRescheduleTasks(runSoon = false) {`
- line 728: `function runtimeRunScheduledTasks() {`
- line 771: `function runtimeOnCleanup(callback) {`
- line 777: `function runtimeRunWhenIdle(callback, timeout = STARTUP_IDLE_TIMEOUT_MS) {`
- line 824: `function runtimeFetch(input, init = {}) {`
- line 1718: `function decodeMissionTextEntities(value) {`
- line 1738: `function normaliseMissionCaption(value) {`
- line 14166: `function schedulePanelPosition(useSavedPosition = true, delay = 80) {`
- line 14295: `function resolveDesktopPanelBounds(`
- line 14349: `function clampDesktopPanelPoint(left, top, panelWidth, panelHeight, bounds) {`
- line 14363: `function stopDesktopPanelWorkspaceObservation() {`
- line 14372: `function clearDesktopPanelSizing(panel = document.getElementById(SCRIPT.panelId)) {`
- line 14381: `function observeDesktopPanelWorkspace(mapEl) {`
- line 14420: `function applyDesktopPanelSizing(panel = document.getElementById(SCRIPT.panelId), mapEl = getLargestLeafletMap()) {`
- line 14516: `function refreshTabletModeUi(panel = document.getElementById(SCRIPT.panelId)) {`
- line 14716: `function applyTabletPanelPosition() {`
- line 14749: `function clearTabletPanelSizing(panel = document.getElementById(SCRIPT.panelId)) {`
- line 14868: `function isAllianceMissionSignal(signal) {`
- line 14872: `function getMissionMarkerLayers() {`
- line 14876: `function normaliseMissionId(value) {`
- line 14881: `function missionIdFromMarker(marker) {`
- line 14885: `function getMissionMarkerIndex() {`
- line 14910: `function setMissionOverlayRecord(missionId, record) {`
- line 14921: `function deleteMissionOverlayRecord(missionId) {`
- line 14930: `function missionOverlayVersion(missionId) {`
- line 14934: `function getMissionPanelElement(missionId) {`
- line 14964: `function normaliseMissionBoolean(value) {`
- line 14971: `function parseMissionTimestamp(value) {`
- line 14990: `function normaliseMissionOverlayRecord(item, existing) {`
- line 15046: `function captureMissionMarkerData(payload) {`
- line 15088: `function captureMissionMarkerDataFromSource(source) {`
- line 15108: `function captureMissionMarkerDataFromDocument(doc) {`
- line 15114: `function scanInlineMissionMarkerData() {`
- line 15120: `async function refreshMissionProgressFromPage(force = false, minimumIntervalMs = MISSION_PROGRESS_PAGE_REFRESH_MS) {`
- line 15164: `function installMissionMarkerAddHook() {`
- line 15209: `function creditsFromMissionPanel(missionId) {`
- line 15238: `function getMissionAverageCredits(marker, missionId) {`
- line 15257: `function missionOwnerId(marker, missionId) {`
- line 15266: `function currentMissionUserId() {`
- line 15270: `function missionStructuredTypeSignal(marker, missionId, snapshot = null) {`
- line 15317: `function missionHasExplicitPersonalOwner(marker, missionId) {`
- line 15323: `function missionHasExplicitAllianceOwner(marker, missionId) {`
- line 15329: `function isAllianceMissionLayer(marker, missionId, snapshot = null) {`
- line 15351: `function isPersonalMissionLayer(marker, missionId) {`
- line 15359: `function missionIsEvent(marker, missionId, snapshot = null) {`
- line 15423: `function normaliseDeveloperEventMissionTitle(value) {`
- line 15431: `function knownDeveloperEventFallback(marker, missionId, snapshot = null) {`
- line 15450: `function missionDeveloperEventInfo(marker, missionId, snapshot = null) {`
- line 15475: `function missionWatchOwnership(marker, missionId, snapshot = null) {`
- line 15487: `function missionWatchCategory(marker, missionId, snapshot = null, specialEvent = null) {`
- line 15496: `function missionWatchOwnershipLabel(type) {`
- line 15501: `function missionWatchCategoryLabel(category) {`
- line 15517: `function ensureMissionFloatPane(map) {`
- line 15542: `function missionVehicleStateFromObject(source) {`
- line 15554: `function vehicleAssignedMissionId(vehicle) {`
- line 15574: `function vehicleOwnerId(vehicle) {`
- line 15586: `function vehicleRecordId(vehicle) {`
- line 15597: `function normaliseVehicleApiPayload(payload) {`
- line 15604: `function getPersonalVehicleRecords() {`
- line 15637: `function invalidateMissionCommitmentIndex() {`
- line 15641: `function rebuildMissionCommitmentIndex() {`
- line 15704: `function refreshPersonalVehicleData(force = false) {`
- line 15756: `function captureRadioVehicleMessage(message) {`
- line 15814: `function missionPersonalUnitState(marker, missionId) {`
- line 15830: `function missionHasPersonalUnit(marker, missionId) {`
- line 15934: `function exactMissionTimestampFromObject(source) {`
- line 15948: `function timestampFromMissionPanel(missionId) {`
- line 15968: `function getMissionCreatedAt(marker, missionId) {`
- line 15987: `function formatMissionAge(createdAt, now = Date.now()) {`
- line 15996: `function clearMissionAgeLabels() {`
- line 16004: `function makeMissionAgeIcon(ageText, severity = missionAgeSeverity(0)) {`
- line 16015: `function updateMissionAgeLabels() {`
- line 16126: `function scheduleMissionAgeRefresh(delay = 220) {`
- line 16131: `function missionAgeSeverity(ageMs) {`
- line 16139: `function missionKnownPersonal(marker, missionId) {`
- line 16150: `function personalMissionAgeRecord(marker, missionId, now = Date.now()) {`
- line 16166: `function unitCommitmentAnchor(marker, missionId) {`
- line 16308: `function renderedMissionFloatWidth(label, selector, fallback) {`
- line 16317: `function transportWatcherPlacement(map, marker, missionId, requirement) {`
- line 16618: `function renderTransportSweepPanel() {`
- line 16644: `function transportSweepVehicleIdFromHref(href) {`
- line 16652: `function transportSweepReleaseVehicleIdFromHref(href) {`
- line 16704: `function transportSweepVehicleAnchorsWithin(root = null, requireUsable = true) {`
- line 16714: `function transportSweepVisibleVehicleAnchors() {`
- line 16757: `function transportSweepRootScore(root, missionId = null) {`
- line 16775: `function transportSweepFindMissionWindowRoot(missionId = null) {`
- line 16795: `function transportSweepAnchorBelongsToMissionWindow(anchor) {`
- line 16804: `function transportSweepOwnVehicleIdSet() {`
- line 16817: `function collectTransportSweepStaticCandidates(anchors, source = 'mission HTML', preserveAnchors = false) {`
- line 16883: `async function transportSweepFetchMissionCandidates(missionId) {`
- line 16917: `async function collectTransportSweepVehicleCandidatesForMission(missionId) {`
- line 16936: `function collectTransportSweepVehicleCandidates() {`
- line 16948: `function collectTransportSweepLssmCandidates(excludedVehicleIds = null) {`
- line 17026: `async function waitForTransportSweepLssmCandidates(excludedVehicleIds = null, timeoutMs = 18000) {`
- line 17303: `async function openTransportSweepVehicle(candidate) {`
- line 17319: `async function processTransportSweepMission(item, remainingAllowance) {`
- line 17559: `function vehicleTargetInfo(vehicle) {`
- line 17575: `function vehicleSearchSignal(vehicle) {`
- line 17587: `function vehicleStatusBucket(vehicle) {`
- line 17664: `function buildResourceGapVehicleContext() {`
- line 17689: `function preparedVehicleMatchesRequirement(prepared, parts) {`
- line 17698: `function vehicleCoordinates(vehicle, markerById = null) {`
- line 17715: `function analyseResourceGap(snapshot, context = buildResourceGapVehicleContext(), requirements = resourceRequirementsFromSnapshot(snapshot)) {`
- line 18042: `function getVehicleMarkerLayers() {`
- line 18193: `function getVehicleMarkerIcons() {`
- line 18204: `function markVehicleIcon(icon) {`
- line 18208: `function synchroniseVehicleMarkerClasses() {`
- line 18214: `function getMissionIconsByOwnership() {`
- line 18328: `function vehicleDataNeeded() {`
- line 18338: `function missionSnapshotsNeeded() {`
- line 18388: `function scheduleEnabledMapRefreshes({ includeSnapshots = true, positionPanel = false, refreshOperational = true, mapOnly = false } = {}) {`
- line 18398: `function reconcileFeatureRefreshes({ includeSnapshots = true, positionPanel = false } = {}) {`
- line 19278: `function findMissionChiefBrandElement(bar) {`
- line 19383: `function resetMajorIncidentFeedObserver() {`
- line 19652: `function getMissionCaption(marker, missionId) {`
- line 19676: `function normaliseMissionPostcode(value) {`
- line 19684: `function normaliseMissionCity(value, postcode = '') {`
- line 19705: `function getMissionAddress(marker, missionId) {`
- line 19727: `function vehicleStatusCode(vehicle) {`
- line 19738: `function personalUnitCommitmentForMission(missionId) {`
- line 19769: `function normaliseMissionLiveCurrentValue(value) {`
- line 19774: `function missionLiveCurrentValueFromMarker(marker) {`
- line 19784: `function missionLiveCurrentValueFromDom(missionId) {`
- line 19803: `function resolveMissionLiveCurrentValue(marker, missionId, overlay, now = Date.now()) {`
- line 19818: `function missionSnapshotFromMarker(marker, now = Date.now()) {`
- line 19898: `function refreshMissionSnapshots() {`
- line 19962: `function scheduleMissionSnapshotRefresh(delay = 600) {`
- line 20057: `function criticalMissionClearingProgress(snapshot) {`
- line 20064: `function criticalMissionOperationalState(units, snapshot, stuckRecord) {`
- line 20130: `function criticalMissionStableData(marker, missionId, snapshot, ownership, category, specialEvent) {`
- line 20166: `function getCriticalMissionEntries(minAgeMs = CRITICAL_VIEW_MIN_AGE_MS, missionTypes = ['personal']) {`
- line 20322: `function criticalMissionDistanceReference() {`
- line 20456: `function qualifiedAllianceMissionCount() {`
- line 20479: `function scheduleOperationalPanelsRender(delay = 500, force = false) {`
- line 20488: `function renderOperationalPanels(force = false, criticalRenderOptions = null) {`
- line 20565: `function vehicleCodeStatusSnapshot() {`
- line 20603: `function createVehicleCodeStatus() {`
- line 20656: `function renderVehicleCodeStatus() {`
- line 20681: `function refreshVehicleCodeStatus(force = false) {`
- line 20698: `function closeVehicleCodeStatus() {`
- line 20707: `function toggleVehicleCodeStatus() {`
- line 20734: `function findMissionListDockRect() {`
- line 20865: `function positionCriticalDrawerOverMissionList() {`
- line 21151: `function missionAgeWatchHasNonDefaultState() {`
- line 21394: `function criticalMissionValueDetails(entry) {`
- line 21412: `function missionValueCurrencyMeta(hostname = location.hostname) {`
- line 21420: `function formatMissionWindowValue(value, hostname = location.hostname) {`
- line 21427: `function missionValueIdFromUrl(value, baseUrl = location.href) {`
- line 21435: `function missionValueIdFromElement(root) {`
- line 21478: `function missionValueMountForRoot(root) {`
- line 21489: `function missionValueWindowCandidates() {`
- line 21514: `function removeMissionValueRows(scope = document) {`
- line 21518: `function clearMissionValueIndicators() {`
- line 21523: `function missionValueToolbarSpacer(root, mount) {`
- line 21543: `function missionValueToolbarBar(spacer, root, mount) {`
- line 21559: `function missionValueSpacerVisibleWidth(spacer) {`
- line 21574: `function missionValuePresentation(availableWidth, formatted) {`
- line 21583: `function missionValuePreferredCandidates(candidateList) {`
- line 21606: `function missionValueCandidateScopes(candidate) {`
- line 21620: `function missionValueRowsForCandidate(candidate) {`
- line 21631: `function pruneMissionValueHostObservers(activeSpacers = null) {`
- line 21641: `function observeMissionValueHost(candidate) {`
- line 21670: `function syncMissionValueCandidate(candidate) {`
- line 21731: `function scheduleMissionValueScan(delay = 80) {`
- line 21739: `function scanMissionValueWindows() {`
- line 21774: `function ensureMissionValueDocumentStyle(doc) {`
- line 21792: `function clearMissionValueDocumentStyles() {`
- line 21799: `function observeMissionValueFrame(frame) {`
- line 21807: `function observeMissionValueDocument(doc) {`
- line 21831: `function installMissionValueWindows() {`
- line 21847: `function criticalMissionValueForEntry(entry) {`
- line 21964: `function nativeMissionCountdownText(missionId) {`
- line 21973: `function formatMissionCountdown(ms) {`
- line 21982: `function normaliseMissionTimestampMs(value) {`
- line 21988: `function missionGameNowMs(snapshot = null) {`
- line 22003: `function clearingMissionCountdownText(entry) {`
- line 22242: `function missionLockOnReducedMotion() {`
- line 22247: `function missionLockOnThemeLabel() {`
- line 22258: `function playMissionLockTrackingSound() {`
- line 22309: `function clearMissionLockOnEffect() {`
- line 22334: `function createMissionLockOnTravelOverlay(map) {`
- line 22345: `function resolveMissionLockOnMarker(marker, missionId) {`
- line 22354: `function missionLockOnContainerPoint(map, marker, fallbackLatLng) {`
- line 22378: `function positionMissionLockOnDom(map, marker, fallbackLatLng, element) {`
- line 22387: `function createMissionLockOnReticle(map, marker, missionId, latLng, token) {`
- line 22459: `function animateMissionFocus(marker, missionId, latLng, map) {`
- line 22505: `function focusMissionById(missionId, openMission = false) {`
- line 22540: `function fitCriticalMissions() {`
- line 22646: `function loadMissionProgressState() {`
- line 22664: `function saveMissionProgressState(delay = 1200) {`
- line 22678: `function missionProgressSignature(snapshot) {`
- line 22692: `function updateMissionProgressState(snapshot, now = Date.now()) {`
- line 22719: `function missionStuckRecord(missionId, now = Date.now()) {`
- line 22738: `function clearStuckMissionLabels() {`
- line 22746: `function stuckMissionAnchor(marker, missionId) {`
- line 22755: `function makeStuckMissionIcon(stuckForMs, anchor) {`
- line 22765: `function updateStuckMissionLabels() {`
- line 22851: `function scheduleStuckMissionRefresh(delay = 300) {`
- line 22856: `function createMissionInspector() {`
- line 22866: `function missionMarkerFromIcon(icon) {`
- line 22879: `function positionMissionInspector(event) {`
- line 22933: `function renderMissionInspector(marker, event = missionInspectorPointer) {`
- line 22992: `function hideMissionInspector() {`
- line 23007: `function refreshVisibleMissionInspector() {`
- line 23013: `function handleMissionInspectorPointerOver(event) {`
- line 23025: `function handleMissionInspectorPointerMove(event) {`
- line 23035: `function handleMissionInspectorPointerOut(event) {`
- line 23044: `function extractMissionIdsFromPayload(payload, target = new Set(), seen = new WeakSet()) {`
- line 23061: `function animateMissionSpawn(missionId, attempt = 0) {`
- line 23105: `function handleMissionSpawnArguments(args) {`
- line 23117: `function primeMissionSpawnDetector() {`
- line 27517: `function setPanelCssPosition(left, top) {`
- line 27530: `function clampPanelPosition(left, top) {`
- line 27540: `function getDefaultPanelPosition() {`
- line 27558: `function positionPanelOverlay(useSavedPosition = true) {`
- line 27581: `function resetPanelPosition() {`
- line 27589: `function nudgePanel(dx, dy) {`
- line 27601: `function startPanelDrag(event) {`
- line 27637: `function movePanelDrag(event) {`
- line 27655: `function endPanelDrag(event) {`
- line 27692: `function openPanel() {`
- line 27705: `function closePanel({ restoreFocus = false } = {}) {`
- line 27715: `function togglePanel() {`
- line 28174: `function createPanel() {`
- line 29206: `function mutationAffectsMissionData(mutation) {`
- line 29300: `function pruneRuntimeCaches(now = Date.now()) {`
- line 29401: `function connectMainMutationObserver() {`
- line 29499: `function autoLoadAllVehiclesLinkInfo(link) {`
- line 29516: `function autoLoadAllVehiclesElementVisible(element) {`
- line 29529: `function autoLoadAllVehiclesResolveMissionRoot(link) {`
- line 29533: `function autoLoadAllVehiclesCandidateLinks() {`
- line 29544: `function clearAutoLoadAllVehiclesReleaseTimer() {`
- line 29549: `function disconnectAutoLoadAllVehiclesLinkObserver() {`
- line 29554: `function disconnectAutoLoadAllVehiclesRootObserver() {`
- line 29559: `function releaseAutoLoadAllVehiclesRequest({ schedule = true } = {}) {`
- line 29568: `function resetAutoLoadAllVehiclesMission() {`
- line 29578: `function observeAutoLoadAllVehiclesRoot(root) {`
- line 29596: `function observeAutoLoadAllVehiclesLink(link) {`
- line 29614: `function scheduleAutoLoadAllVehiclesScan(delay = 0) {`
- line 29623: `function scanAutoLoadAllVehicles() {`
- line 29684: `function autoLoadAllVehiclesMutationRelevant(mutation) {`
- line 29699: `function stopAutoLoadAllVehicles() {`
- line 29707: `function installAutoLoadAllVehicles() {`

## Guardrails

This report is inspection-only. It does not alter the userscript, distribution, version, settings or runtime behaviour.
