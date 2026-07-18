# Changelog

All notable changes to the MissionChief Map Command Toolkit will be documented in this file.

The format is based on Keep a Changelog, and releases use semantic version numbers.

## [Unreleased]

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
- Added fixture-backed regression coverage for HUD ownership, lifecycle, confirmed counting and final-summary dismissal.

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
- Extracted the deterministic ledger-entry normalization stage into a focused helper while preserving pagination order, retry timing, archive checkpoints, occurrence counting and report calculations.

### Compatibility
- No settings, themes, payout presentations, public assets or financial-report outputs were changed.

## [4.13.1] - 2026-07-16

### Performance
- Reduced Economy Mode cache-pruning work by building current vehicle and building layer sets once per prune pass instead of rescanning full marker collections for every cached layer.
- Scoped **Auto-load all vehicles** link discovery to the connected, visible mission window after a mission is identified, while preserving the document-wide fallback needed for newly opened missions.
- Reused the canonical mission-window selector for root resolution instead of rebuilding and iterating a duplicate selector list.

### Audit and documentation
- Corrected the full-audit lexical-scope analysis so identically named local helper functions in different blocks are no longer reported as same-scope duplicates.
- Added targeted static invariants for the runtime optimisations.
- Updated the public theme catalogue to include **007 Intelligence** and **Hyrule Command**, plus the Hyrule payout presentation and automatic vehicle loading capability.

### Compatibility
- Preserved all saved settings, import/export contracts, public asset URLs, themes, payout templates and Desktop, Tablet and iOS behaviour.

## [4.13.0] - 2026-07-15

### Added
- Added **Hyrule Command**, a complete new interface theme combining parchment cartography, royal-gold framing, forest tones, ancient-blue illumination and green energy glyphs.
- Added transparent Hyrule-inspired crest, eye rune, energy ring, sword-and-shield, command-map, quest-seal and rupee-burst assets.
- Added the dedicated **Hyrule Quest Reward** payout presentation with tier-specific quest titles, magical rune activation and animated rupee particles.
- Added the supplied quest-reward cashout cue as a trimmed, normalized and browser-compatible hosted MP3.

### Responsive design
- Added dedicated Desktop, Tablet Mode and iOS Mobile Mode layout handling for the interface and payout sequence.
- Added static Economy Mode and reduced-motion fallbacks while preserving the theme's readable reward state.

### Compatibility
- Preserved every existing interface theme, payout template, map skin, saved setting, settings import/export path and operational feature.
- Hyrule artwork and payout audio remain lazy and are used only when the matching theme or payout is selected.


## [4.12.0] - 2026-07-15

### Added
- Added an optional **Auto-load all vehicles** setting that activates MissionChief's native load-more control whenever an opened mission limits the visible vehicle list.
- Added safe sequential loading for additional hidden vehicle batches without relying on the control's displayed language or count text.

### Reliability
- Validates same-origin mission and offset-page URLs before activating the native control.
- Prevents duplicate clicks, bounds each mission to 50 load requests, and stops when MissionChief does not expose a new page.
- Resets request state when the mission window closes, is replaced, or another mission opens.
- Uses event-driven DOM observers only while the option is enabled, with bounded settling retries for controls that render hidden before becoming available.

### Compatibility
- Defaults the new setting to Off and preserves manual use of MissionChief's native control when disabled.
- Preserves settings import/export, all interface themes, Desktop, Tablet Mode and iOS Mobile Mode.

## [4.11.4] - 2026-07-15

### Fixed
- Corrected the Toolkit's internal runtime version so startup metrics and runtime diagnostics report the installed userscript version accurately.
- Added a permanent validation failure when userscript `@version` metadata and internal `SCRIPT.version` do not match.

### Compatibility
- Preserved all Toolkit features, themes, responsive modes, settings, saved data, startup sequencing and operational behaviour.

## [4.11.3] - 2026-07-15

### Fixed
- Corrected three Promise executor callbacks so rejection and canvas-conversion control flow is explicit and no discarded return values remain.
- Corrected postcode-removal regular-expression escaping so mission location text handles compact and unusually spaced UK postcodes reliably.
- Removed initial values that were always overwritten before use, without changing the resulting runtime values.
- Replaced stale hard-coded version text in the settings footer and runtime-ready diagnostic with current, maintainable wording.

### Changed
- Removed four functions proven to have no call path: `runtimeUnregisterTask`, `missionWatchType`, `missionWatchTypeLabel`, and `synchronisePersonalBuildingMarkerClasses`.
- Removed write-only render, payout-media, Discord-finance, and boot-retry state that could never affect Toolkit behaviour.
- Simplified one mission-marker parsing loop, Mission Age Watch boolean toggles, and equivalent separator expressions without changing their results.

### Performance
- Coalesced Alliance Buildings page observer updates so repeated DOM mutation batches schedule only one pending render.
- Changed the main mutation observer to leave its document-wide startup fallback as soon as the real map or mission-list roots become available.
- Reduced unnecessary state assignments without adding observers, event listeners, CSS, startup network activity, or feature workload.
- Added a permanent full-userscript audit covering dead-code candidates, complexity, selectors, lifecycle resources, storage, metadata, remote hosts, assets, and AST-backed JavaScript analysis.

### Compatibility
- Preserved all themes, Desktop, Tablet Mode, iOS Mobile Mode, saved settings, bookmark data, public asset paths, legacy Discord webhook hosts, and existing feature behaviour.

## [4.11.2] - 2026-07-14

### Fixed
- Restored the full Toolkit stylesheet to the sparse `document-start` phase so Chrome no longer rematches thousands of selectors against an already-rendered MissionChief page.
- Changed the complete settings panel to first-open construction instead of building hundreds of controls during every page startup.
- Prevented Major Incident Feed rendering from bypassing the deferred operational-startup gate through the general UI refresh path.

### Performance
- Preserved the deferred vehicle API, mission snapshot and operational monitor startup introduced in v4.11.1.
- Reduced initial Toolkit construction to the core map command control and persistent shortcut bar.
- Added lightweight startup timings for stylesheet installation, core UI readiness, settings-panel construction and operational startup under `window.__MCMS_STARTUP_METRICS__`.

### Compatibility
- Preserved Smart Bookmark Labels, all interface themes, responsive modes and the early Alliance Buildings map blocker.

## [4.11.1] - 2026-07-14

### Performance
- Added a two-stage idle bootstrap so MissionChief can finish its own DOM and map construction before the full Toolkit starts.
- Deferred the 789 KB Toolkit stylesheet from `document-start` to the idle startup phase without changing any theme, skin or responsive layout.
- Consolidated the initial vehicle API, mission snapshot and operational overlay work into one coordinated data pass.
- Delayed and narrowed DOM observation to the map, mission list and top-level page changes instead of observing the entire body during initial rendering.

### Changed
- Mission Inspector and Critical View UI are now created on demand rather than eagerly during page load.
- Major Incident Feed, Transport Watcher, Stuck Mission Detector, Resource Gap and related overlays start after the core map controls are usable.
- Startup mutation refreshes use a longer settling debounce and no longer force mission snapshots when no snapshot-dependent feature is active.

### Fixed
- Prevented overlapping startup snapshot refreshes caused by the vehicle API completion timer and the previous 850 ms fallback refresh.
- Added safe recovery for background-tab startup and MissionChief navigation that replaces map or mission-list containers.
- Preserved the early Alliance Buildings map blocker while deferring all unrelated Toolkit work.

## [4.11.0] - 2026-07-14

### Added
- Added Smart Bookmark Labels with UK-aware place and operational-word abbreviation dictionaries.
- Added consonant-compression fallback for custom user-entered locations.
- Added automatic duplicate-label numbering across quick places and custom bookmarks.
- Added manual short-label overrides without requiring the bookmark location to be resaved.
- Added full-name desktop tooltips, accessible labels and touch long-press name previews.

### Changed
- Replaced equal-width bookmark shortcut tiles with compact content-sized controls.
- Reduced bookmark shortcut height and spacing across Desktop, Tablet and iOS Mobile Mode.
- Preserved every existing interface theme, colour treatment, border, shadow and active state.
- Updated responsive dock calculations for the smaller bookmark footprint.

## [4.10.4] - 2026-07-14

### Baseline
- Imported the current live Greasy Fork distribution into GitHub as the canonical source baseline.
- Recorded the source version, SHA-256 hash, byte size and line count.
- Added repository auditing and Release Pipeline v2 foundations.
- Preserved all existing public image, audio, theme, manifest and Help Centre paths.

### Distribution
- No functional userscript changes.
- Greasy Fork remains the active public installation and update source during migration.
