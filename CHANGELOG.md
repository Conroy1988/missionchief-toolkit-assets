# Changelog

All notable changes to the MissionChief Map Command Toolkit will be documented in this file.

The format is based on Keep a Changelog, and releases use semantic version numbers.

## [Unreleased]

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
