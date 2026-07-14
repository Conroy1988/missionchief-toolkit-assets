# Changelog

All notable changes to the MissionChief Map Command Toolkit will be documented in this file.

The format is based on Keep a Changelog, and releases use semantic version numbers.

## [Unreleased]

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
