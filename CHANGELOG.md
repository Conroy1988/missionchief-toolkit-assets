# Changelog

All notable changes to the MissionChief Map Command Toolkit will be documented in this file.

The format is based on Keep a Changelog, and releases use semantic version numbers.

## [5.0.6] - 2026-07-23

### Fixed

- Made the Toolkit launcher independent of Leaflet map discovery, with a safe fixed fallback that reparents to the live map when available.
- Added a permanent idempotent UI-integrity task and corrected mutation ordering so MissionChief map replacements cannot silently remove the launcher.
- Replaced the Operational Window label dump with typed, persisted switches, number inputs, colour controls, selects, dependency states and structured list editors.
- Mapped the complete Enhanced Requirements, Extended Call Window, Extended Mission List and opt-in Transport settings to their Toolkit runtime state.
- Hid internal overlay, minimised, push-right, drag, starred and collapsed state from user-facing settings.
- Added responsive two-column desktop and single-column Tablet/iOS layouts with safe text wrapping and no horizontal overflow.
- Restored Mission Age labels and shortcut `6` with forced late-data recovery, immediate controlled retries, marker replacement reconciliation and clean teardown.
- Completed the runtime mapping for Extended Call Window and Extended Mission List controls, including ARR counters/search/highlighting, patient and vehicle summaries, structured categories/icons/keywords, sharing gates, sorting and configured badge colours.
- Preserved the established managed-timeout performance budget by moving ARR autofocus onto microtasks while retaining Mission Age late-data recovery retries.

## [Unreleased]

## [5.0.5] - 2026-07-23

### Critical requirement-source discovery recovery
- Replaced first-match `#missing_text` binding with authoritative candidate discovery across active, duplicated, replaced and LSSM-transformed mission markup.
- Added active-mission and visibility scoring so retained empty or stale roots cannot trap the requirements panel in a permanent waiting state.
- Recovered requirement evidence from hidden LSSM `data-raw-html` carriers while continuing to suppress a genuinely visible equivalent LSSM panel.
- Removed native MissionChief requirement headings before parsing, matching the authorised LSSM parser contract.
- Rebound the operational observer whenever the authoritative source changes and added behavioural coverage for duplicate, stale, delayed, LSSM and Toolkit-owned roots.
- Decoded hidden LSSM raw markup with a contextual fragment rather than adding another `innerHTML` assignment site, preserving the established performance ceiling.


## [5.0.4] - 2026-07-23

### Critical requirements truth-state recovery
- Stopped empty, delayed or failed MissionChief requirement parsing from being presented as confirmed green coverage.
- Added explicit waiting and unresolved states; green coverage now requires positively parsed requirement rows that are all covered.
- Enforced one Operational Requirements panel per document, reusing the authoritative mounted surface and removing stale duplicates.
- Added behavioural regression coverage for pending input, unparsed input, covered rows, open rows, unresolved text and repeated duplicate mounts.


## [5.0.3] - 2026-07-23

### Critical preboot recovery
- Fixed a JavaScript temporal-dead-zone failure that terminated the userscript during state hydration before `boot()` or `ensureUi()` could execute.
- Moved the Operational Window settings schema constant ahead of the top-level `loadState()` call while retaining every v5 operational feature and existing user setting.
- Added a permanent declaration-order regression contract and executable launcher-mount smoke coverage for desktop, tablet and iOS layouts.
- Verified the corrected runtime against the last confirmed working v4.20.37 launcher under the same browser-like MissionChief DOM.


## [5.0.2] - 2026-07-23

### Emergency launcher recovery
- Rebuilt startup so the core Toolkit launcher mounts before optional MissionChief hooks and operational integrations.
- Isolated every pre-launch DOM/API integration so one changing MissionChief surface cannot terminate the launcher retry loop.
- Added an immediate first mount attempt and a managed fallback when idle scheduling is unavailable.
- Expanded map discovery to support the live `#map` container when the Leaflet class is delayed or changed.

### Reliability corrections
- Removed an empty `closest()` selector left by Matrix retirement that could throw during DOM mutation handling.
- Restricted Alliance Buildings boot suppression to the exact Alliance Buildings route, preventing normal map pages being misclassified.
- Existing Toolkit and operational-window settings remain intact; no reset is required.


## [5.0.1] - 2026-07-23

### Emergency menu recovery
- Restored the Toolkit launcher and settings menu for users upgrading from v4.20.37 to v5.0.0.
- Made core UI startup fail-open so an operational-suite initialisation or scan error cannot prevent the map command bar from mounting.
- Deferred the first operational DOM scan until after `ensureUi()` has created the launcher.
- Isolated operational scan failures with explicit diagnostics while preserving the rest of the Toolkit runtime.

### Compatibility
- No settings reset is required. Existing v5.0.0 operational-window preferences are retained.
- Enhanced Requirements, Extended Call Window, Extended Call List and Enhanced Transport Requests remain available after the core launcher mounts.


## [5.0.0] - 2026-07-23

### Major operational-window replacement
- Replaced the legacy Mission Requirements Matrix with a Toolkit-native operational suite built from the authorised LSSM Extended Call Window, Extended Call List and Enhanced Transport Requests behaviour.
- Added one versioned `operationalWindow` settings model, one lifecycle coordinator per active document, coalesced rendering and deterministic teardown across MissionChief navigation.
- Migrated the former Matrix preference once into the new requirements setting and permanently retired the old parser, panel, observers, scheduler and toggle.

### Enhanced mission requirements
- Added a fixture-first requirements engine covering vehicle, equipment, personnel, conditional, capacity, trailer and tractive requirements.
- Added selected, en-route and on-scene reconciliation, water/foam/pump progress, unresolved-text preservation and immutable render fingerprints.
- Added a responsive normal-flow requirements surface for Desktop, Tablet and iOS, with LSSM coexistence detection to prevent duplicate panels.

### Extended Call Window
- Added patient and vehicle summaries, selected-unit and ARR counters, generation/alarm information, collapsible patient and vehicle areas, permanent vehicle and ARR search, mission keyword badges, map-centre controls and ARR highlighting.
- Added sticky headers, vehicle-type badges and mobile safe-area handling without creating a second mission-window lifecycle.

### Extended Call List
- Added mission sorting, starring, collapsing, patient/prisoner/credit/time badges and native share controls.
- Preserved deterministic ordering and state across live list refreshes while remaining compatible with MissionChief and equivalent LSSM modules.

### Enhanced Transport Requests
- Added opt-in transport automation with strict route validation, visible/enabled candidate filtering, single-candidate ambiguity rejection and per-route idempotency tokens.
- Kept automatic transport opening disabled by default; successful vehicle transport controls retain their reviewed safe default.

### Performance and validation
- Reduced total observer constructions from twelve to eleven and broad subtree observers from ten to nine compared with v4.20.37.
- Held direct MutationObserver, `getElementById` and `innerHTML` metrics at their existing release ceilings while reducing source bytes, selectors, managed timers, listeners and observer trackers.
- Added deterministic engine, renderer, runtime, Matrix-retirement, structural, performance and mobile compatibility contracts.

### Upgrade compatibility
- Existing Toolkit settings are retained. The former Matrix enablement preference is migrated automatically; no manual reset is required.
- The operational suite supports Desktop, Tablet and iOS/Safari and suppresses equivalent Toolkit surfaces when the matching LSSM module is active.

## [4.20.37] - 2026-07-22

### Critical Mission Requirements fixes
- Distinguished an authoritative empty MissionChief `#missing_text` source from an absent or unavailable source.
- Marked catalogue-only requirements covered when MissionChief confirms that no live requirements remain.
- Enabled exact Level 1 Public Order Officer tracking using the canonical `level_1_public_order` schooling and ARR capability.
- Preserved unknown specialist on-site composition instead of fabricating personnel counts.
- Added exact regressions for Rival Fans Mass Disorder (Medium) and a twenty-one-officer Level 1 Public Order selection.

### Benefit
- Fully satisfied missions no longer retain false specialist shortages or `need confirmation` warnings.
- Selecting qualified Level 1 Public Order units now updates Selected and Still Needed immediately; qualified responding and on-site crews also render numeric totals.

### Compatibility
- Non-empty live requirements, unavailable sources, loading states, explicit specialist training, deselection, patients, prisoners and transports retain their existing authority and tracking behaviour.
- Generic police vehicles and untrained personnel do not satisfy Level 1 Public Order demand.

## [4.20.36] - 2026-07-22

### Critical Mission Requirements fixes
- Added canonical `Car Recovery` handling for MissionChief's `car to tow` and `cars to tow` demand.
- Counted Recovery Vehicle type `104` as one car and Flatbed Recovery Vehicle type `105` as two cars; HGV Recovery Vehicle type `106` remains excluded from ordinary car recovery.
- Reused one delegated selection listener and the existing managed scan scheduler for direct checkbox, ARR and vehicle-group updates without adding lifecycle call sites.
- Added strict semantic specialist-training badge support so an explicitly labelled selected Police Sergeant can be counted without treating vehicle captions or generic Police Officers as qualified Sergeants.

### Benefit
- Recovery requirements now receive complete selected, responding, on-site and still-needed tracking.
- Police Sergeant selection updates immediately after native or ARR-driven vehicle selection.

### Compatibility
- Whole-row captions remain invalid specialist qualification evidence. Existing vehicle, personnel, mission-window, covered-row, theme, payout and notification behaviour is unchanged.

## [4.20.35] - 2026-07-22

### Critical Mission Requirements fix
- Added standalone `Rescue Support Vehicle` and `Rescue Support Vehicles` requirement aliases.
- Mapped the requirement to the reviewed rescue-support vehicle types `4`, `16`, `38`, and `43`.
- Preserved PRV type `27` and SRV type `28` as independent requirement families.
- Added an exact railway-station mission regression covering catalogue parsing, reconciliation, selected, responding, on-site and still-needed counts.

### Benefit
- Rescue Support Vehicle requirements now receive complete Matrix tracking instead of unresolved `?` values.

### Compatibility
- Existing composite rescue-support requirements, covered-row visibility, vehicle selection, dispatch, themes, layout and unrelated mission logic are unchanged.

## [4.20.34] - 2026-07-22

### Core mission-data reliability
- Extracted mission-marker candidate discovery and mission-ID normalization from `captureMissionMarkerData()` into `resolveMissionMarkerCandidates()`.
- Preserved array recursion, payload/params/mission/data ordering, exact ID-key precedence, stringification, duplicate behavior and overlay publication.
- Added direct fixtures for nested containers, arrays, nullish fall-through, empty-ID blocking, zero/negative values and duplicate candidates.

### Benefit
- Mission payload-shape changes are now easier to isolate and support without risking overlay publication, ownership classification or downstream mission windows.

### Compatibility
- No mission ownership, coordinates, timestamps, requirements, patients, prisoners, event state, visual design, device layout, theme, payout, notification, timing or public asset changed.

## [4.20.33] - 2026-07-22

### Internal reliability
- Extracted Clean Mode, Shortcuts and Compact Dock state routing from `toggleFeature()` into a dedicated interface-shell helper.
- Preserved the shared Clean Mode panel-close lifecycle, persistence, root attributes, UI synchronization and feature-reconciliation order.
- Added direct and delegated contracts for all three routes and unknown-route safety.

### Benefit
- Future interface-shell changes are easier to isolate, test and roll back without tracing unrelated operational feature branches.

### Compatibility
- No visual design, layout, theme, notification, timing, public asset or user-facing feature behaviour changed.

## [4.20.32] - 2026-07-22

### Internal reliability
- Extracted Mission Spawn and Stuck Detector state and notification routing from `toggleFeature()` into dedicated mission-monitoring helpers.
- Preserved Mission Spawn arming reset, timer cancellation, known-mission reset and enabled-only detector priming before the shared persistence/UI phase.
- Added direct and delegated contracts proving both monitoring notifications remain after feature reconciliation.

### Compatibility
- No monitoring threshold, timer duration, mission classification, visual design, device layout, theme or public asset changed.

## [4.20.31] - 2026-07-22

### Internal reliability
- Extracted Mobile Mode and Tablet Mode state, layout reconciliation, sizing cleanup, fitting and notification routing from `handleSettingChange()` into a dedicated device-layout handler.
- Added direct and delegated contracts for accepted values, invalid-value normalization, mutual exclusion and Desktop/Tablet/iOS transition ordering.

### Compatibility
- No visual design, breakpoint, viewport, safe-area, touch-target, panel sizing, theme or public asset changed.

## [4.20.30] - 2026-07-22

### Internal reliability
- Extracted Mission Tracking Audio, Emergency Payout Flash and Theme Audio state and notification routing from `toggleFeature()` into dedicated payout/audio helpers.
- Preserved immediate audio unlock/disposal and post-reconciliation notification ordering with direct and delegated contracts.

### Compatibility
- No payout presentation, hosted audio source, threshold, duration, volume, device layout, theme or public asset changed.

## [4.20.29] - 2026-07-22

### Improved
- Hardened the full iPhone and iPad Safari layout against notches, browser chrome, the home indicator, orientation changes, split view and delayed visual-viewport updates.
- Rebuilt touch launcher controls, settings tabs, screen pins, bookmarks, profiles and operational drawers around a 44px minimum interaction target with visible press feedback.
- Added horizontally scrollable mobile tab and screen-pin rails, safe internal scrolling and visual-viewport-constrained panel sizing so menus remain reachable without covering the map.
- Added multi-frame keyboard and Safari toolbar settling after resize, scroll, focus and orientation events while preserving the existing desktop layout.

### Validation
- Added a deterministic iOS/Safari usability contract covering viewport geometry, keyboard recovery, safe edges, touch-target floors and prevention of undersized mobile regressions.

## [4.20.28] - 2026-07-22

### Internal reliability
- Extracted Mission Inspector, Mission Value, Mission Requirements and Custom Vehicle Badges state routing from `toggleFeature()` into `handleMissionWindowToggle()`.
- Extracted their post-reconciliation install, clear and notification effects into `applyMissionWindowToggleEffects()` without changing execution order.
- Added direct and delegated fixture coverage for route inventory, state isolation, unknown-route safety, enabled/disabled effects and update → reconciliation → effect ordering.

### Compatibility
- No mission-window presentation, Desktop/Tablet/iOS behaviour, setting name, theme, payout presentation or public asset changed.

## [4.20.27] - 2026-07-22

### Internal reliability
- Extracted the nine map and visibility state routes from `toggleFeature()` into `handleMapVisibilityToggle()` while preserving all saved-state, root-attribute, UI-refresh and snapshot-reconciliation behaviour.
- Extracted vehicle/building layer synchronization into `applyMapVisibilityToggleEffects()` at the same post-render position, including Economy Mode resynchronization.
- Added direct and delegated fixture coverage for route inventory, unknown-route safety, state parity and the exact update → layer sync → Economy Mode → reconciliation ordering.

### Compatibility
- No map presentation, mission visibility, overlay behaviour, Desktop/Tablet/iOS layout effect, setting name, theme, payout presentation or public asset changed.

## [4.20.26] - 2026-07-21

### Engineering
- Extracted the 14 Discord financial-report and Local Financial Archive setting routes into `handleDiscordFinancialSettingChange()` without changing setting names, normalization, persistence, preview invalidation or asynchronous refresh behaviour.
- Kept `handleSettingChange()` responsible for device, operational, payout and automatic-theme settings while reducing its routing complexity through one independently revertible UI-dispatch stage.

### Validation
- Extended the fixture-backed Settings/UI contract to compile and execute the extracted route family directly and through the main setting router.
- Preserved all 36 rendered settings, intentional no-op handling, route ownership, source/distribution parity and the permanent 500-line source-headroom margin.

## [4.20.25] - 2026-07-21

### Engineering
- Extracted the seven recurring Boot maintenance-task registrations into `registerBootMaintenanceTasks()` without changing callback logic, intervals, economy-mode scheduling or scheduler ownership.
- Kept `boot()` responsible for initialization order while reducing its operational complexity through one independently revertible lifecycle stage.

### Validation
- Extended the fixture-backed Boot lifecycle contract to compile and execute the extracted registration helper directly and through `boot()`.
- Preserved the exact required task set, task count, observer count, listener coverage, teardown behaviour and production source/distribution parity.

## [4.20.24] - 2026-07-21

### Fixed
- Reconciled Financial Advisor daily totals against MissionChief’s `/credits/overview` Revenue, Spendings and Sum checkpoints without adding aggregate values on top of detailed transactions.
- Preserved detailed-ledger categories while exposing unexplained income, spending and net variance instead of inventing transaction classifications.
- Applied overview-confirmed totals to complete covered days across daily, weekly, monthly and custom-period reports, while retaining ledger totals for partial days.
- Kept Financial Advisor, Discord financial reports and generated Financial Command graphics on the same canonical reconciled income, spending and net movement.
- Degraded safely to the existing detailed ledger when the overview page is unavailable, malformed or outside the requested coverage range.

### Validation
- Added deterministic parser, sign handling, pagination, bounded cache, safe-failure, duplicate-date, exact-match, variance, net-negative, partial-period and no-double-counting contracts.

## [4.20.23] - 2026-07-21

### Fixed
- Counted MissionChief's confirmed patient-release state exactly once across direct LSSM and fallback Transport Sweep routes.
- Recognised release confirmation outside the active lightbox, including `Understood! We have released the patient.`, while rejecting stale pre-existing messages.
- Preserved successful patient totals when a later mission-window cleanup or reopen operation fails.
- Kept the persistent HUD, main panel and final summary on the same canonical cleared, processed and error counters.

### Validation
- Added deterministic global-alert, DOM-replacement, stale-message, duplicate-observer and post-success cleanup regression coverage.

## [4.20.22] - 2026-07-21

### Fixed
- Reconciled firefighter capacity using actual responding/on-site crew quantities, assigned personnel and vehicle-specific maximum overrides rather than vehicle count.
- Added qualification-specific Police Sergeant, Police Inspector and Railway Police Officer counts that never infer specialist personnel from generic crew or vehicle captions.
- Added complete Breathing Apparatus Support Unit coverage for BASU, OSU, BASU Pod and OSU Pod with Prime Mover pair de-duplication and explanatory Matrix detail.
- Suppressed generic firefighter range metadata when MissionChief already supplies the exact generated requirement for the active mission.

## [4.20.21] - 2026-07-21

### Engineering
- Recovered source headroom by removing only blank physical lines, standalone full-line CSS comments and 15 newlines immediately before full-line closing braces from the existing `installMainStyles` template.
- Preserved the canonical CSS content byte-for-byte after normalising only parser-ignored comments and whitespace immediately before closing braces.
- Added a permanent fixture and validation contract for the reviewed stylesheet source sequence, formatting categories and recovered-line target.
- Published the Issue #253 structural inventory and rollback boundary.

## [4.20.20] - 2026-07-21

### Fixed
- Mission Info probability values can no longer become vehicle quantities; `75` probability now remains metadata rather than `75 Traffic Cars`.
- `only required, when available` qualifiers no longer appear as Matrix rows or unresolved MissionChief requirements.
- Probability-qualified and availability-only catalogue counts remain dormant until the live mission confirms that the resource is active.
- Patient transport, critical-care and unknown boolean catalogue metadata remain outside operational Matrix demand.

### Validation
- Added deterministic normal-page, parser, catalogue, conditional-activation, mission-isolation and Matrix-summary regressions based on the official LSSM V4 separation of `requirements`, `chances` and `prerequisites`.

## [4.20.19] - 2026-07-21

### Fixed
- `Inland Rescue Boat (Trailer)` now resolves against reviewed UK maritime vehicle types 67 and 74 across Selected, Responding and On site.
- `Seagoing Vessel` now resolves against the ILB/ALB capability union, vehicle types 68 and 69.
- Compatible towing vehicles no longer satisfy trailer-capable requirements without the actual eligible trailer or maritime asset.
- Trailer and towing-vehicle pairs retain one contribution identity through dispatch and arrival transitions.
- A Required 3 / Selected 1 maritime row remains outstanding with Still needed 2 and reports `0/1 covered`.
- Police Sergeant personnel now retain `police_sergeant` ARR capability evidence after dispatch, so Responding and On-site counts update through vehicle identity and exact cached crew.
- Railway Police Officer personnel now retain the native `railway_police` qualification across linked vehicle rows and Units Responding.
- Canonical responding crew `sortvalue` is accepted only inside `#mission_vehicle_driving`; positional numeric cells elsewhere remain rejected.
- `railway_police_command` remains a distinct Mobile Operations Manager qualification and cannot satisfy Railway Police Officer demand.
- Required 5 with On site 3 and Responding 1 now reports Still needed 1.

### Audit
- Expanded the pinned LSSM compatibility audit across Enhanced Missing Vehicles, Mission Helper captions, UK vehicle captions and MissionChief authoritative labels.
- Added runtime-backed parser, Selected, Responding, On-site, ineligible-type and contribution-deduplication checks for every supported UK vehicle capability.
- Integrated the cross-source audit into the canonical Mission Requirements contract and userscript validation gate.

## [4.20.18] - 2026-07-21

### Performance
- Root Toolkit state attributes now mutate only when their string value changes, eliminating 22 redundant DOM mutations from unchanged `updateUI()` passes while preserving every calculation and output value.

### Validation
- Added fixture-backed first-write, unchanged-repeat, changed-state, external-repair, layout-orientation and helper return-value regressions against the extracted production functions.

## [4.20.17] - 2026-07-20

### Fixed
- Level 2 Public Order Officer ARR selections now use each vehicle's exact MissionChief `assigned_personnel_count` from the Toolkit's shared vehicle cache when available, so two nine-officer carriers clear an eighteen-officer requirement.
- Generic Police Officers now use exact assigned personnel across Selected, Responding and On Site units instead of remaining at vehicle-type minimum ranges such as `7+`.
- Live required totals reconstructed from current shortages now become exact as soon as on-scene personnel is known.
- Native exact crew metadata remains authoritative; inaccessible or alliance vehicles retain the reviewed fail-closed type range.

### Validation
- Added deterministic 9 + 9 public-order, deselection, eleven-on-scene police, selected traffic-car, native-priority and zero-personnel regressions.

## [4.20.16] - 2026-07-20

### Fixed
- Search Advisor personnel selected through MissionChief ARR capability `search_and_rescue` now update the Matrix immediately.
- SAR Commander personnel selected through `search_and_rescue_command` now update Selected, Responding and On Site capacity.
- Control Van vehicle types 85 and 100 now provide their reviewed 1–3 SAR Commander personnel range when explicit crew metadata is unavailable.
- Explicit zero or absent ARR capability evidence no longer turns unrelated selected vehicles into unresolved specialist personnel.

### Validation
- Added deterministic selected, responding, on-site, ARR-positive, ARR-zero, Control Van fallback and deselection regressions.

## [4.20.15] - 2026-07-20

### Fixed
- Selected Police Cars and other supported vehicles now contribute reviewed UK minimum/maximum crew capacity to generic personnel requirements when MissionChief exposes no semantic crew field.
- Known bounded personnel ranges remain bounded rather than becoming completely unknown.
- `PRV`/`PRVs` and `SRV`/`SRVs` now merge into the canonical Primary Response Vehicle and Secondary Response Vehicle rows, with only the full names rendered.

### Validation
- Added deterministic crew fallback, override, selected Police Officer and response-vehicle alias regressions.

## [4.20.14] - 2026-07-20

### Fixed
- Removed visible Mission Info, Patients and Patient Details provenance badges from Matrix requirement labels while retaining machine-readable row metadata.
- Classified Required Personnel Available as a mission-generation prerequisite so it cannot create rows, unresolved shortages, red state or coverage totals.
- Normalised Other information → Required Personnel into operational trained-personnel rows and removed raw Mission info prefixes from unsupported operational personnel.
- Enabled live Level 2 Public Order Officer and Police Sergeant reconciliation from explicit MissionChief training evidence.

### Compatibility
- Updated the Fight on Train catalogue fixture so spawn-availability Railway Police personnel are no longer treated as operational demand.
- Added deterministic clean-label, prerequisite, operational-personnel and parser-facing row contracts.

## [4.20.13] - 2026-07-20

### Fixed
- Reconciled water, foam and pumping requirements from MissionChief's authoritative missing, driving and selected progress values without double subtraction.
- Added locally compiled random-tractive capability intersection for trailer selections.
- Removed whole-row caption text as evidence of specialist personnel training.

### Audit
- Completed the pinned LSSM V.4 Enhanced Missing Vehicles compatibility audit.
- Added an offline upstream capability snapshot and drift checker.
- Added resource, nested-equipment, tractive and personnel reliability fixtures.

## [4.20.12] - 2026-07-20

### Fixed
- Resolved official combined Mission Info vehicle requirements through explicit capability unions instead of rendering unknown `?` coverage.
- Police Helicopters or Drones now accepts Police Helicopter type 11, drone vehicle types 89–91 and `drone` equipment across Selected, Responding and On site.
- Added the remaining verified UK combined Fire, Airfield, Mountain/SAR and paramedic vehicle labels so any accepted constituent vehicle updates the same Matrix row.

### Safety
- Existing vehicle-type, equipment, factor and trailer de-duplication remains unchanged.
- Unsupported or probabilistic Mission Info metadata continues to fail closed as unknown rather than being guessed.

### Validation
- Added fixture-backed parser, catalogue, selected, responding, on-site, deselection and dual-evidence de-duplication regressions.

## [4.20.11] - 2026-07-20

### Performance
- Removed redundant presentation-attribute notifications from the document-wide early Alliance Buildings page watcher.
- Child additions and removals, relevant-element matching, navigation detection, map suppression and repair behaviour remain unchanged.

### Validation
- Added an exact production-source invariant proving the watcher remains child-list based and no longer subscribes to attribute-only mutation records.

## [4.20.10] - 2026-07-20

### Fixed
- Corrected Railway Police Officer state reconciliation when MissionChief reduces the live missing count after personnel are selected.
- The difference between the Mission Info baseline and live missing demand is no longer falsely displayed as On-site capacity.
- Proven On-site and Responding capacity is retained first; any remaining committed capacity is displayed as Selected.

### Validation
- Added a deterministic regression for the reported `8 required / 4 live missing / no units on scene` case and deselection restoration.

## [4.20.9] - 2026-07-20

### Fixed
- Restored Mission Requirements Matrix capacity from active **Units Responding** and **Vehicles on Scene** tables when those MissionChief sections are collapsed or relocated within the active mission window.
- Responding and on-site vehicles now fulfil and hide completed requirement rows exactly as selected vehicles do.
- Hidden rows return immediately when a unit is cancelled, redirected, removed from scene or no longer satisfies the requirement.

### Safety
- Visibility is bypassed only for canonical MissionChief operational tables proven to belong to the active mission.
- Hidden stale lightboxes, mismatched mission IDs, template rows and unrelated operational content remain excluded.
- On site, Responding and Selected de-duplication and precedence remain unchanged.

### Validation
- Added deterministic collapsed-table, relocated-lightbox, fulfilled-row, renewed-shortage and stale-mission regression fixtures.

## [4.20.8] - 2026-07-20

### Fixed
- Fulfilled Mission Requirements Matrix rows are now hidden whenever their reconciled **Still needed** value is definitively zero.
- Hidden rows immediately return when selection, responding, on-site, patient, personnel or upgraded mission demand creates a positive shortage.
- All-covered missions retain a compact explicit success state instead of showing an empty table.

### Safety
- Unresolved, uncertain, loading and unavailable requirements remain visible and continue to block false success states.
- Requirement calculations, authoritative reconciliation, unit de-duplication and MissionChief/LSSM coexistence are unchanged.

### Validation
- Added deterministic fixtures for fulfilled-row suppression, mixed outstanding/fulfilled rows, renewed shortages after upgrade or re-entry, and unresolved-authority precedence.

## [4.20.7] - 2026-07-19

### Fixed
- Fixed Railway Police selected personnel showing inflated values such as `239+` when an unrelated table-cell sort value was mistaken for crew capacity.
- Personnel capacity now uses semantically labelled crew metadata or explicit current/maximum crew text; unlabelled positional numeric cells are ignored.

### Validation
- Added deterministic regression coverage proving one selected Railway Police Officer contributes exactly one and an unlabelled `sortvalue=239` contributes nothing.

## [4.20.6] - 2026-07-19

### Added
- Added the complete current UK MissionChief vehicle and personnel requirement capability dataset to the Mission Requirements Matrix.
- Added explicit capability coverage for specialist fire, ambulance, police, coastguard, airfield, mountain rescue, railway and specialist response assets.
- Added dataset-driven parser and vehicle-type regression coverage for every imported UK requirement alias.

### Changed
- Requirement parsing now prioritises the longest recognised phrase so combined requirements are not consumed by shorter generic aliases.
- Existing Toolkit selected, responding, on-site, authoritative-catalogue and patient-demand reconciliation remains unchanged.
- The capability dataset is compiled into the userscript; no external manager service or mission-catalogue host is used at runtime.

## [4.20.5] - 2026-07-19

### Changed
- Added a lightweight automatic version check every 30 minutes while MissionChief remains visible, using a single recursive timeout rather than continuous polling.
- Deferred scheduled checks while the tab is hidden and retained the existing visibility-based stale refresh when play resumes.
- Based the next automatic timeout on the remaining successful-cache lifetime, preventing a manual force-check from causing a redundant network ping.
- Retained the 10-minute automatic retry cooldown after network or manifest failures.

### Validation
- Added deterministic scheduler fixtures for the 30-minute cadence, remaining-cache calculation, failure cooldown and hidden-tab deferral.

## [4.20.4] - 2026-07-19

### Fixed
- Restored live **Selected** counts when MissionChief renders **Available Units** outside the nested mission content root but inside the same active lightbox.
- Selected Police Cars, Dog Support Units and trained Railway Police crew now contribute immediately, including hidden duplicate table representations, while vehicle-ID de-duplication and mission-window isolation remain intact.
- Added visible-row training badge fallback so `[Railway Police Officer]` personnel labels contribute their current selected crew when MissionChief does not expose a dedicated training attribute.

### Validation
- Added deterministic nested-lightbox fixtures covering sibling Available Units tables, checked-but-hidden checkbox representations, Police Car/DSU/Railway Police classification and live deselection.

## [4.20.3] - 2026-07-19

### Fixed
- Restored live responding-unit reconciliation across MissionChief table and lightbox variants, including tbody-ID layouts, stable vehicle de-duplication, current crew capacity and explicit trained-personnel metadata.
- Prevented unreadable responding units from being silently treated as zero capacity; affected Matrix rows now remain bounded and unresolved instead of producing false red or green states.
- Restored the authoritative **Fight on Train** baseline: 4 Police Cars, 1 Dog Support Unit and 8 Railway Police Officers.
- Parsed `Required Personnel Available` and `Required Personnel` rows outside the main vehicle table and preserved mission variation keys including additive overlays.
- Prevented empty live missing text from overwriting a loading, failed or non-empty **Requirements for this Mission** authority.

### Validation
- Added deterministic fixtures for responding table variants, active-lightbox discovery, duplicate and state-transition handling, trained Railway Police crew, Fight on Train authority, additive overlays and unresolved authority rendering.

## [4.20.2] - 2026-07-19

### Fixed
- Eliminated live `LATEST`, `UPDATE`, `CHECK` and `RETRY` label wrapping by moving visible status text out of the raw button text node and into a dedicated single-line label layer.
- Added selector-strength safeguards against MissionChief and theme-level `white-space`, word-break and overflow-wrap rules.

### Changed
- Rebuilt the version-status control to match the existing Menu and Economy control family with the same dark surface, footprint, radius, shadow rhythm and icon-over-label composition, without reusing Economy's behavioural selector.
- Removed the v4.20.1 standalone tile class, grid geometry and bottom accent rail while retaining compact state-specific circular indicators.

### Validation
- Extended runtime and contract fixtures to verify control-family class reuse, empty raw text, pseudo-label rendering, nowrap enforcement and Desktop, Tablet and iOS geometry.

## [4.20.1] - 2026-07-19

### Changed
- Replaced the wide horizontal version-status pill with a compact vertical HUD tile aligned to the primary Toolkit and Economy map controls.
- Moved state emphasis from a large coloured background to a dark theme-neutral surface with a small status badge, accent border and bottom status rail.
- Added distinct non-colour indicators for **LATEST**, **UPDATE**, **CHECK** and **RETRY** while preserving all v4.20.0 checking, caching and manual-refresh behaviour.

### Responsive
- Added dedicated 48px Desktop, 43px Tablet and 46px iOS/Mobile tile geometry with nowrap labels and reliable touch targets.
- Added reduced-motion handling and retained keyboard focus, accessible labels and polite state announcements.

### Validation
- Added deterministic visual-contract fixtures for tile dimensions, state icons, placement, accessibility and removal of the legacy horizontal pill.

## [4.20.0] - 2026-07-19

### Added
- Added a compact live **LATEST / UPDATE** control beside the main Toolkit map button.
- Added a guarded repository-owned stable update manifest that is reconciled only after GitHub Release, Greasy Fork, private backup and Discord publication succeed.
- Added semantic numeric version comparison, canonical release/update destinations and accessible installed/available version labels.

### Behaviour
- Delays the first automatic check by 15 seconds, caches successful results for 30 minutes and applies a 10-minute cooldown after failures.
- Rechecks a stale cache when MissionChief becomes visible again, supports Shift-click, right-click and touch long-press manual refresh, and never polls continuously.
- Fails safely as **RETRY** rather than falsely reporting **LATEST** when the network or manifest is unavailable.

### Validation
- Added deterministic semantic-version, cache, cooldown, timeout, failure, destination, duplicate-control and responsive-layout fixtures.

## [4.19.2] - 2026-07-19

### Fixed
- Classified HEMS as Ambulance-capable in the Mission Requirements Matrix, so a selected, responding or on-site HEMS now contributes one unit to the Ambulance row while retaining its HEMS capability.
- Preserved contribution-key de-duplication so the same HEMS cannot be counted twice within one requirement row, and normal road ambulances still do not satisfy HEMS requirements.

### Validation
- Added deterministic aggregate fixtures covering HEMS-to-Ambulance capability inheritance, retained HEMS capability, duplicate suppression and the one-way road-Ambulance boundary.

## [4.19.1] - 2026-07-19

### Fixed
- Corrected live patient discovery when MissionChief renders the patient summary and details outside the resolved mission form, preventing the Mission Requirements Matrix from falsely reporting no outstanding requirements.
- Restored the one-transport-ambulance-per-current-patient requirement on the real mission-window layout.

### Added
- Added patient-detail reconciliation for affirmative **Critical Care required**, **HEMS required** and **Requires Transport** fields.
- Added fulfilment handling for **Ambulance with the patient** and **Critical Care with the patient** without double-counting vehicle demand.

### Validation
- Added deterministic outside-form patient DOM fixtures, affirmative/negative patient-flag fixtures and false-green prevention checks.
- Compacted the reviewed patient runtime after validation to remain within the established release performance envelope.

## [4.19.0] - 2026-07-19

### Fixed
- Promoted MissionChief's **Requirements for this Mission** vehicle and personnel data from fallback-only planning information into an authoritative Mission Requirements Matrix source.
- Added authoritative-only rows that were absent from `#missing_text`, while reconciling overlaps with the strongest non-duplicated requirement.
- Preserved patient-derived Ambulance demand as an independent authority and rejected stale mission responses during AJAX navigation.

### Behaviour
- Deterministic requirements are counted normally; probability-based requirements remain visible as uncertain until MissionChief confirms them or sufficient units cover the maximum.
- The Matrix now fails closed while authoritative mission information is loading or unavailable, preventing a false green state.
- Official mission definitions remain cached by definition URL, with active mission-instance tokens preventing stale response application.

### Validation
- Added fixtures for catalogue-only vehicles, personnel, overlapping sources, conditional requirements, patient coexistence, loading failures and cached authoritative data.

## [4.18.0] - 2026-07-18

### Fixed
- Mission Requirements now derives Ambulance demand from the live patient total even when MissionChief does not list ambulances in `#missing_text`.
- Patient-derived demand reconciles with stated Ambulance requirements using the larger authoritative total instead of adding both values.
- Unknown patient totals can no longer produce a false covered/green Matrix state.

### Behaviour
- One current patient requires one ordinary UK Ambulance by default.
- On-site, responding and selected Ambulances use the existing exclusive vehicle-ID buckets and are never double-counted.
- Patient counts update through the existing mission-window observer lifecycle, including bounded AJAX replacement recovery and mission-ID isolation.
- The Ambulance row carries a compact `Patients` source marker and remains inside the existing Matrix panel.

### Validation
- Added deterministic singular/plural parsing, zero/unknown state, stated-demand reconciliation, live capacity, transition and mission-navigation fixtures.

## [4.17.0] - 2026-07-18

### Added
- Added **Custom Vehicle Badges**: Available Units now shows each vehicle's MissionChief Own Vehicle Category as a compact badge beside the native vehicle label, for example `IRV [Railway Police Officer]`.
- Added a stable read-only vehicle classification API keyed by vehicle ID for Mission Requirements Matrix capability matching.

### Behaviour
- Reuses the Toolkit's existing `/api/vehicles` cache and never performs a second vehicle-list request.
- Reapplies badges after MissionChief or LSSM replaces, filters or sorts the Available Units DOM, without duplicates, repeat DOM insertion or dispatch-side effects.
- Vehicles without an Own Vehicle Category remain unchanged.

### Validation
- Added fixture-backed classification, duplicate-prevention, category-removal and AJAX-row-replacement tests.

## [4.16.4] - 2026-07-18

### Fixed
- Mission Requirements now waits for the active mission's native requirements source or confirmed title/address before mounting in an AJAX dispatch window.
- Available Units, vehicle/response tables and incident-note regions remain data sources only and can no longer become emergency panel hosts.
- Premature placeholder anchors are removed until a valid header placement exists.

### Validation
- Added staged-AJAX coverage proving vehicle-only loading creates no panel and the completed mission header mounts the panel beneath the address and before `#missing_text`.

## [4.16.3] - 2026-07-18

### Fixed
- Prevented the normal AJAX dispatch window from inserting Mission Requirements inside the Available Units vehicle table.
- Nested vehicle and table candidates now resolve upward to the enclosing mission form or lightbox before source lookup and placement.
- Existing panels that were temporarily mounted in table structure are re-homed beneath the mission header on the next scan.

### Validation
- Added a deterministic normal-dispatch fixture covering nested `tbody` discovery, safe block placement and active panel re-homing.

## [4.16.2] - 2026-07-18

### Fixed
- Kept Mission Requirements bound to the active MissionChief mission in AJAX/lightbox and standalone views.
- Native `#missing_text` now outranks generic lightbox sources, preventing lower-right/footer mounting.
- Visible newly opened missions outrank hidden stale records, and catalogue state resets when the active mission changes.

### Interface
- Mounted the panel directly beneath the mission title/address and before MissionChief's native requirement banner.
- Added compact adaptive Desktop widths: 940px standard, 1140px for longer labels, and full available width only for exceptional content.
- Tablet and iOS remain responsive without horizontal overflow.

### Validation
- Added lightbox source, header placement, delayed source, hidden-record, catalogue-transition and adaptive-width fixtures.

## [4.16.1] - 2026-07-18

### Fixed
- Reworked Mission Requirements into a complete live capacity matrix with **Required**, **On site**, **Responding**, **Selected** and **Still needed** values.
- Selected vehicles now reduce **Still needed** immediately; responding and arrived units move between mutually exclusive buckets without double-counting.
- Added `#mission_vehicle_at_mission` observation so arrivals, departures and cancellations update the matrix dynamically.

### Interface
- Added compact red, amber, green and unresolved row states with tighter headers, rows and responsive five-metric mobile cards.
- Preserved normal-flow mounting, collapse behaviour, Desktop/Tablet/iOS distinctions and equal treatment for all seven interface systems.

### Validation
- Added deterministic selection, dispatch, arrival, removal, cross-bucket de-duplication, uncertainty and compact-layout fixtures.

## [4.16.0] - 2026-07-18

### Added
- Added an on-demand resolver for MissionChief's official Possible Missions catalogue and per-mission `Vehicle and Personnel Requirements` tables.
- Added variation-aware six-hour caching with a bounded stale fallback for temporary catalogue failures.
- Added an explicitly labelled official catalogue baseline when live MissionChief requirement data is absent or unparseable.
- Added catalogue title, definition, patient, variation and live-versus-catalogue diagnostics to **Report Mission**.

### Safety
- Live MissionChief `#missing_text`, en-route units and selected units remain authoritative whenever live data is available.
- Catalogue quantities are never presented as current **Still needed** values.
- Recalibrated the static source-size envelope after v4.15.5 exhausted the original v4.11.2 allowance; runtime, CSS and relative performance limits are unchanged.

## [4.15.5] - 2026-07-18

### Fixed
- Changed **Report Mission** to use a repository-owned GitHub issue form so `Mission Info Missing` is applied for contributor reports as well as maintainer reports.
- Preserved the sanitised diagnostic prefill through the form's canonical `diagnostic` field without storing a GitHub credential in the userscript.

## [4.15.4] - 2026-07-18

### Added
- Mission Requirements now shows bounded loading, explicit empty and explicit unavailable states instead of silently disappearing.
- Added a compact Report Mission control that opens a sanitised, pre-filled GitHub issue composer using the Mission Info Missing label.

### Fixed
- Native MissionChief mission windows are discovered even when `#missing_text` is absent, delayed, empty or moved.
- Fallback panels automatically upgrade to the live matrix when MissionChief later exposes valid requirement data.
- Reporting excludes tokens, webhooks, coordinates, addresses, chat, vehicle IDs and unrelated page HTML.

### Compatibility
- MissionChief remains the sole mission-window and requirement authority; no GitHub token or direct issue-creation credential is embedded in the userscript.
- Single-owner mounting, LSSM coexistence and Desktop, Tablet and iOS layouts remain intact.

## [4.15.3] - 2026-07-18

### Fixed
- Mission Requirements now has one primary top-level runtime owner, preventing same-origin mission frames from mounting a second identical panel.
- Parent and frame representations of the same MissionChief mission are deduplicated by stable mission identity before panel creation.
- Existing Toolkit panels are adopted at the concrete MissionChief host and any stale duplicate panels are removed before observers are attached.
- Repeated scans and AJAX/lightbox replacements remain idempotent, with exactly one Toolkit panel retained per concrete MissionChief mission host.

### Compatibility
- MissionChief remains the sole mission-window, requirements, selection and en-route authority; LSSM remains optional and is used only for explicit duplicate-equivalent detection.
- Desktop, Tablet and iOS normal-flow layouts and the seven equal interface systems are unchanged.

## [4.15.2] - 2026-07-18

### Fixed
- Mission Requirements now discovers MissionChief-owned `#missing_text` roots independently from Mission Value, including alternate AJAX/lightbox mission layouts.
- Unstructured native Missing Personnel, Missing Vehicles and resource banners are classified before parsing instead of defaulting every banner to vehicles.
- Quantity parsing now supports `8x`, `8 x`, `x8`, trailing `x8`, colon and “at least” forms.
- Unknown quantified requirements remain visible as amber, safely unresolved rows and can no longer produce a false green state.
- Selected vehicle counting now recognises vehicle types stored on the MissionChief row and deduplicates one vehicle shown in both normal and occupied lists by stable vehicle ID.
- Selecting and deselecting eligible units recalculates exact Selected counts, including the two-police-car 0 → 1 → 2 → 1 sequence.

### Compatibility
- MissionChief's native mission DOM remains the sole requirements, selection, en-route and layout authority.
- LSSM remains optional and is consulted only through explicit duplicate-panel ownership detection.

## [4.15.1] - 2026-07-18

### Fixed
- Mission Requirements now mounts against MissionChief's native mission window when the game's own missing-vehicle or missing-personnel alert uses the shared `alert-missing-vehicles` class.
- LSSM coexistence detection now requires explicit ownership metadata such as `data-raw-html`; the shared presentation class alone can no longer suppress the Toolkit.

### Compatibility
- The Toolkit remains fully independent of LSSM and continues to use MissionChief's own `#missing_text`, mission form, vehicle lists and en-route table as its data and layout sources.
- Added deterministic coverage for both MissionChief-native alerts and an active LSSM enhanced-missing-vehicles component.

## [4.15.0] - 2026-07-17

### Added
- Added a live Mission Requirements matrix inside opened MissionChief windows, mounted in normal document flow above dispatch controls.
- Missing, en-route, still-needed and selected values now update from the active mission DOM and checked vehicle list without continuous polling.
- Added responsive Desktop, Tablet and iOS layouts, seven equal interface-theme treatments, covered/partial/unresolved row states and a compact collapse control.

### Safety and compatibility
- Unknown requirement wording remains visibly unresolved and can never produce a false all-covered state.
- The Toolkit yields to an active LSSM enhanced-missing-vehicles panel instead of rendering a competing duplicate.
- Mission-window replacement, same-origin frames, checkbox changes, en-route changes and runtime teardown use bounded observers with one owned panel per mission window.
- Added fixture-backed release validation for calculation, ownership, layout, coexistence and lifecycle contracts.

## [4.14.10] - 2026-07-17

### Changed
- Extracted the bounded core-UI boot-attempt loop from `boot()` into the independently testable `startBootAttemptCoordinator()` lifecycle stage.
- `boot()` now delegates once to the coordinator while retaining runtime ownership, listeners, scheduled tasks, mutation observation and teardown registration.

### Compatibility
- Initial delay, retry thresholds, 350/700/1400 ms backoff, 12-attempt map fallback, 90-attempt hard stop and destroyed-runtime cancellation are unchanged.
- No observer, timer, listener, task, theme, setting or public asset behaviour changed.
- Extended the fixture-backed Boot/Lifecycle contract to compile and test the extracted coordinator directly and through `boot()`.

## [4.14.9] - 2026-07-17

### Added
- Ambulance Transport Sweep now displays a compact persistent live HUD while MissionChief and LSSM mission/vehicle windows are opening, processing and closing.
- The HUD shows current sweep status, mission progress, confirmed patients cleared, skipped items, errors, processed count and elapsed time.
- Successful clear totals update immediately after the existing confirmed LSSM or fallback discharge gate succeeds.

### Compatibility
- The HUD is mounted outside sweep-owned lightbox layers, deduplicated, non-blocking and removed on completion, cancellation or Toolkit runtime teardown.
- Desktop uses a top-right presentation; Tablet and iOS use a compact safe-area-aware bottom presentation.
- Manual start, personal-vehicle exclusion, prisoner handling, request sequencing and single-window safeguards remain unchanged.

## [4.14.8] - 2026-07-17

### Fixed
- Financial Command Discord graphics now reserve independent label and value columns throughout the Operating Snapshot card.
- Checkpoint reconciliation now renders as a compact signed variance, reconciled state, reconstructed basis or unavailable state instead of a long sentence that can collide with the row label.
- Long positive and negative multi-million-credit values are measured, reduced only when required and kept clear of neighbouring text.

### Compatibility
- Financial calculations, ledger reconciliation, Discord payloads, image dimensions, visual styling and all non-image report content remain unchanged.
- Added fixture-backed canvas layout coverage for reconciliation states and deliberately oversized labels and values.

## [4.14.7] - 2026-07-17

### Changed
- Migrated all current payout-audio mappings to structured canonical paths owned by their interface system or the shared payout-preset package.
- Added consistent canonical asset namespaces for Map Command, Cyberpunk, Fallout 4 and Factorio, while retaining the existing Umbrella, 007 Intelligence and Hyrule Command packages.
- Removed the remaining “Flagship” wording from Hyrule Command so all seven interface systems remain equally represented.

### Compatibility
- Retained all seven root-level audio files as byte-identical public compatibility aliases for older installed and published Toolkit versions.
- Added a machine-readable alias manifest and validation that fails on missing aliases, hash mismatches, legacy references in the current source, orphaned audio or undeclared duplicates.
- Existing runtime theme IDs, payout template IDs, settings, fallback audio behaviour and Desktop/Tablet/iOS operation remain unchanged.

## [4.14.6] - 2026-07-17

### Changed
- Moved Mission Value into MissionChief's native mission action toolbar spacer so it automatically yields space to MissionChief and LSSM action buttons.
- The toolbar badge now adapts through full, shortened and value-only presentations as the available spacer width changes.

### Fixed
- Removed legacy header/content Mission Value rows and deduplicated by the concrete mission toolbar host and mission ID across lightbox and same-origin iframe contexts.
- Narrow or fully occupied toolbars now use one normal-flow fallback row instead of overlapping dispatch, navigation or Requirements controls.

### Compatibility
- Existing Mission Value settings, currency formatting, verified value sources, import/export behaviour and Desktop/Tablet/iOS feature availability remain unchanged.
- Added fixture-backed toolbar-width, fallback and cross-document deduplication contracts.

## [4.14.5] - 2026-07-17

### Changed
- Audited all command-panel sections and assigned every control one canonical home without changing its internal setting key, shortcut or saved state.
- Moved Auto Night to Skins, Alliance Map Blocker to Tools, vehicle auto-loading to Resources, operational feed/audio controls to Ops and saved map profiles to Places.
- Renamed the visible Discord tab to Finance while preserving the stable `discord` tab key for saved settings and imports.

### Fixed
- Removed duplicate Transport Watcher, Unit Count, Mission Age and Critical View controls from secondary sections.
- Reworked static, row and action-button labels to wrap safely across Desktop, compact Desktop, Tablet and iOS widths instead of clipping or overlapping.

### Compatibility
- Section order, theme support, feature behaviour, localStorage/import-export contracts and keyboard shortcuts remain unchanged.
- Added a fixture-backed section-navigation and narrow-label contract to the permanent userscript preflight.

## [4.14.4] - 2026-07-17

### Fixed
- Replaced content-derived Transport Sweep window ownership with DOM-delta ownership of the exact native lightbox layer created by each `lightboxOpen()` call.
- The sweep now closes the owned layer through its own close control first and force-removes only newly created sweep-owned layers when MissionChief leaves their outer wrappers behind.

### Performance
- Prevents mission and vehicle lightbox shells, iframes and backdrops from accumulating underneath later sweep windows while preserving unrelated MissionChief, LSSM and Toolkit dialogs.

## [4.14.3] - 2026-07-17

### Fixed
- Restored Patient Transport Sweep mission opening after v4.14.2 incorrectly treated unrelated persistent page dialogs as active MissionChief mission windows.
- Window cleanup now targets only the exact lightbox opened and owned by the sweep; when no owned window exists, the next mission opens immediately.
- Restored changed-content baselines so persistent page UI cannot be mistaken for a newly loaded mission or vehicle window.

### Performance and compatibility
- Retains the v4.14.2 single-window lifecycle without closing or blocking unrelated MissionChief, LSSM or Toolkit interface elements.

## [4.14.2] - 2026-07-17

### Fixed
- Prevented Patient Transport Sweep from stacking duplicate MissionChief mission and vehicle lightboxes during repeated alliance-ambulance processing.
- The sweep now closes and verifies removal of the active native window before reopening the same mission, opening a fallback vehicle, advancing to another mission or finishing the current mission.

### Performance
- Only one MissionChief lightbox remains active during the sweep, preventing the severe DOM, rendering and memory overhead caused by accumulated hidden mission windows.

## [4.14.1] - 2026-07-17

### Fixed
- Corrected Patient Transport Sweep so a mission containing several alliance-member ambulances is explicitly reopened after every confirmed release.
- The sweep now waits for release completion before returning to the mission, rescans the fresh mission DOM for the next delayed LSSM control and repeats until no eligible alliance controls remain.

### Safety
- Own-vehicle exclusion, ambiguous-owner rejection, sequential processing, duplicate protection, cancellation, per-run limits and the non-LSSM fallback remain unchanged.

## [4.14.0] - 2026-07-17

### Added
- Upgraded Patient Transport Sweep to use LSSM's mission-level **Release patient (No reward)** controls before opening individual vehicle windows.
- The sweep waits dynamically for delayed LSSM controls, processes alliance-member ambulances sequentially, rescans after every release and supports several patient-held units in the same mission.

### Safety
- The signed-in player's verified vehicle IDs remain excluded before any release action.
- Ambiguous owner rows are skipped, duplicate mission/vehicle actions are blocked, cancellation and per-run limits remain active, and the existing vehicle-window route is retained only as a fallback when LSSM controls do not appear.

## [4.13.9] - 2026-07-16

### Fixed
- Moved the Mission Value indicator clear of MissionChief's upper-right mission-window controls.
- The indicator now measures the visible close/action icon cluster and dynamically reserves enough right-side clearance, with a conservative fallback when game markup differs.

### Compatibility
- Mission Value remains enabled by default and retains its existing persistent toggle, currency formatting, verified value sources and iframe support.
- Native MissionChief controls remain untouched and fully clickable.

## [4.13.8] - 2026-07-16

### Added
- Added a compact Mission Value indicator to dynamically opened MissionChief mission windows.
- Mission Value is enabled by default and can be turned on or off persistently from the Ops section on Desktop, Tablet and iOS.
- Values reuse the Toolkit's verified live marker, mission snapshot, captured overlay and mission-list data sources; unavailable values remain hidden rather than guessed.

### Compatibility
- The indicator uses normal document flow with reserved close-control space, preventing overlap with native mission controls.
- Existing themes, settings import/export, Economy Mode and mission-window behaviour are preserved.

## [4.13.7] - 2026-07-16

### Fixed
- Rebuilt the Desktop panel shell as a two-row command layout so the title controls and eight-section menu rail remain permanently visible.
- Restricted vertical scrolling to the selected section content, preventing the command chrome from moving away or appearing detached on long Ops and Settings pages.
- Added a static regression contract for the fixed command-chrome row and content-only scroll region.

### Compatibility
- The v4.13.6 full operational-workspace sizing and saved-position clamping are preserved.
- Tablet Mode, iOS Mobile Mode, Economy Mode, all themes, settings and import/export contracts are unchanged.

## [4.13.6] - 2026-07-16

### Fixed
- Corrected the v4.13.5 Desktop Mode regression that restricted the command panel to the Leaflet map rectangle.
- Desktop now uses the full visible operational workspace: below the top navigation/mission banners and down to the bottom of the browser workspace.
- Saved and dragged positions are immediately re-clamped so the header, drag controls, help/close controls and tabs cannot remain behind top-page overlays.

### Compatibility
- Fixed panel chrome and active-tab internal scrolling are preserved.
- Tablet Mode, iOS Mobile Mode, Economy Mode, all themes, settings and import/export contracts are unchanged.

## [4.13.5] - 2026-07-16

### Changed
- Constrained the Desktop Mode command menu to the visible MissionChief map area instead of the full browser viewport.
- Kept the Desktop header, tab rail and footer accessible while only the active tab content scrolls internally.
- Added map-resize observation and saved-position clamping so shorter windows and changing map layouts remain usable.

### Compatibility
- Desktop retains its compact draggable layout and saved coordinates.
- Tablet Mode, iOS Mobile Mode, Economy Mode, all interface themes, settings and import/export contracts are unchanged.

## [4.13.4] - 2026-07-16

### Internal reliability
- Added direct fixture coverage for loaded-state normalization, including non-mutating parsed inputs, unchanged defaults and parity with the storage-backed load path.
- Extracted deterministic settings merge, migration and validation into `normaliseLoadedState()` while preserving storage-key precedence, JSON failure fallback, import rollback and saved-setting compatibility.

### Compatibility
- No setting names, defaults, themes, payout presentations, public assets, UI routes, keyboard shortcuts or runtime feature behaviour were changed.

## [4.13.3] - 2026-07-16

### Internal reliability
- Added direct fixture coverage for marker payload normalization, including field preservation, invalid optional values and non-mutating overlay updates.
- Extracted MissionChief marker payload interpretation into `normaliseMissionOverlayRecord()` while preserving candidate discovery, mission IDs, overlay versioning, ownership classification, snapshot invalidation and map lifecycle behaviour.

### Compatibility
- No settings, themes, payout presentations, public assets, Leaflet operations, observers, timers or mission snapshot outputs were changed.

## [4.13.2] - 2026-07-16

### Internal reliability
- Added fixture-backed financial-ledger contracts covering parsing, retries, sequential pagination, archive boundaries, duplicate occurrences, stability restarts, incremental overlap, requested-range fallback and Discord summary inputs.
- Extracted the deterministic ledger-entry normalization stage into a focused helper while preserving pagination order, duplicate handling, archive boundaries, incremental overlap and report calculations.
- Added deterministic Discord payload fixture coverage for summary fields, component structure, embed fallbacks, webhook acknowledgement and failure handling.

### Compatibility
- No Financial Command controls, calculations, credit values, exports, Discord presentation, webhook storage, themes, settings or public asset behaviour changed.

## [4.13.1] - 2026-07-16

### Internal reliability
- Added deterministic fixture coverage for Financial Command CSV export, including RFC 4180 escaping, row order, Blob creation and object-URL cleanup.
- Extracted the CSV serialization and download stages into focused helpers while preserving filenames, headers, data values, click behaviour and URL revocation.

### Compatibility
- No Financial Command controls, calculations, filters, credit totals, Discord payloads, themes, settings or public asset behaviour changed.

## [4.13.0] - 2026-07-16

### Internal reliability
- Added a one-shot canonical userscript preflight that exercises settings, dispatch, financial ledger, Discord payloads, CSV export and control-panel rendering contracts together.
- Added fixture-backed checks for settings parsing and merge fallback, finance snapshots and reconciliation, dispatch guardrails, hidden-unit exclusions, Discord summaries and tabbed control rendering.
- Added automatic distribution rebuild when validation succeeds so source and published artefacts remain byte-identical.

### Compatibility
- No settings, themes, layout modes, map controls, dispatch logic, financial calculations, webhook behavior or public asset paths changed.

## [4.12.7] - 2026-07-16

### Internal reliability
- Added fixture-backed settings-contract validation covering canonical section navigation, feature flags, storage-backed state, import/export visibility and seven-theme invariants.
- Added deterministic Finance-tab coverage for the stable internal `discord` section key, visible Financial Command label and persistent toggle/storage behaviour.

### Compatibility
- No settings keys, tab ordering, themes, layout modes, financial calculations, Discord payloads, map behavior or storage migrations changed.

## [4.12.6] - 2026-07-16

### Internal reliability
- Added fixture-backed finance-calculation coverage for totals, arithmetic means, day averages, rolling periods, active-day averages, deltas, shares and Discord report inputs.
- Extracted deterministic Financial Command calculation helpers while preserving ledger collection, aggregation windows, status rendering, CSV export, webhook delivery and all existing settings.

### Compatibility
- No financial values, Discord messages, CSV content, themes, UI controls, settings keys, map behaviour or storage contracts changed.

## [4.12.5] - 2026-07-16

### Internal reliability
- Added fixture-backed dispatch guardrail coverage for dispatch-button state, in-flight locking, vehicle selection, alliance transport exclusion and stale-window cancellation.
- Extracted deterministic dispatch-validation helpers from the patient transport sweep while preserving request order, fallback paths, delays, limits, cancellation and existing alerts.

### Compatibility
- No sweep settings, transport rules, manual start behaviour, themes, map controls or MissionChief request payloads changed.

## [4.12.4] - 2026-07-16

### Internal reliability
- Added fixture-backed critical-drawer state coverage for filter normalization, badge counts, empty states, view switching and cross-view update behaviour.
- Extracted deterministic drawer-state helpers while preserving mission classification, button actions, saved filters and rendering behaviour.

### Compatibility
- No critical-mission rules, drawer layout, shortcuts, themes, settings, saved-state keys or MissionChief marker behaviour changed.

## [4.12.3] - 2026-07-16

### Internal reliability
- Added fixture-backed runtime-lifecycle ownership coverage for tracked listeners, observers, scheduled tasks and teardown completeness.
- Added explicit runtime registries for listeners, observers, timeouts, intervals and animation frames so Toolkit cleanup is measurable and idempotent.

### Compatibility
- No feature controls, timers, themes, layout modes, map behaviour, notification rules or saved settings changed.

## [4.12.2] - 2026-07-16

### Internal reliability
- Added fixture-backed mission-inspector output coverage for section ordering, resource counts, responding personnel, confidence/closure notes and invalid-target fallbacks.
- Extracted deterministic mission-inspector markup generation while preserving existing drawer discovery, data sources, theming, drag behaviour and cleanup.

### Compatibility
- No mission values, marker behaviour, map controls, themes, settings, exports or storage contracts changed.

## [4.12.1] - 2026-07-16

### Internal reliability
- Added fixture-backed visibility filtering for critical missions, marker search, alliance mission controls and patient transport sweep candidate discovery.
- Centralized actionable-element visibility checks through `isElementActionable()` while preserving hidden/deleted marker behaviour, ownership detection, and existing feature settings.

### Compatibility
- No feature controls, mission classification rules, transport limits, themes, shortcuts or storage behaviour changed.

## [4.12.0] - 2026-07-16

### Internal reliability
- Added deterministic fixture coverage for map-layer filtering, including own/alliance marker ownership, mission and alliance-mission visibility, vehicle visibility and unknown marker handling.
- Extracted map-layer visibility classification into pure helpers while preserving current Leaflet event binding, marker discovery, saved settings and toggle behaviour.

### Compatibility
- No visible controls, themes, layout modes, storage keys, marker styling, layer defaults or map behaviour changed.

## [4.11.3] - 2026-07-14

### Changed
- Refreshed the root README overview and public GitHub Pages landing page around the Toolkit's full seven-system identity instead of presenting one theme as the product centre.
- Added a balanced theme showcase for Map Command, Cyberpunk, Fallout 4, Umbrella, Factorio, 007 Intelligence and Hyrule Command across both public surfaces.
- Reworked the old component and release/readiness sections into clearer capability, proof and operational-status blocks.

### Compatibility
- The Map Command interface remains the original identity, while all seven systems are now represented equally.
- Existing documentation routes, installation links and public asset paths are unchanged.

## [4.11.2] - 2026-07-14

### Internal reliability
- Added canonical Toolkit performance budgets and a pull-request regression workflow for source size, CSS size/rules, timers, observers, animation-frame scheduling, event listeners, selectors and startup-hook calls.
- Added measured performance snapshots plus a release-to-release history ledger generated from the canonical source.
- Added an early `document-start` startup probe and a runtime diagnostics snapshot at `window.__MCMS_STARTUP_METRICS__` without changing feature behaviour.

### Compatibility
- No themes, feature defaults, settings keys, map behaviour, public asset paths or UI layout changed.

## [4.11.1] - 2026-07-14

### Internal reliability
- Added a permanent repository-wide asset health audit covering userscript, public documentation, HTML/CSS/JS/JSON/YAML and workflow references.
- Added a versioned asset-audit report and orphan warning inventory to `status/`.
- Added an automatic repository-health workflow that publishes audit results, posts Discord development status and creates/updates the `asset-audit` issue if integrity fails.

### Compatibility
- No userscript logic, themes, layout modes, settings keys, MissionChief behaviour or public asset paths changed.

## [4.11.0] - 2026-07-14

### Added
- Added a controlled Discord-backed Toolkit development pipeline for issues, pull requests, protected development packages and release readiness checks.
- Added isolated Discord webhook channels for development status and production release announcements.
- Added an immutable release bundle workflow, Greasy Fork source-of-truth workflow and private backup verification.
- Added machine-readable project status, release workflow and maintainer runbooks under `status/` and `docs/`.

### Security
- Development and release Discord webhooks are stored only as repository secrets and never exposed in the public userscript or public repository history.
- Production releases require an explicit owner command and reject malformed, stale or unauthorized requests.

### Compatibility
- Existing public asset paths, userscript installation behaviour, settings, themes, desktop/tablet/iOS layouts and Financial Command remain unchanged.
