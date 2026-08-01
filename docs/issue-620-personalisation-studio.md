# Issue #620 — Personalisation Studio

Toolkit v10.0.0 combines six user-selected personalisation upgrades in one state, interface and lifecycle boundary.

## Product contract

- **Custom Layout Builder:** keeps separate Desktop, Tablet and iOS group order, control order, visibility, dock position, panel position and panel size. Drag-and-drop is supplemented by explicit move buttons for touch, keyboard and assistive technology.
- **Visual Theme Studio:** applies a validated accent, surface, text, radius, transparency and blur layer over any retained Toolkit interface. Exported theme codes contain the visual theme object only.
- **Quick Actions Wheel:** supports four through eight slots. A slot can invoke a safe Toolkit action, jump to a Quick Place or custom bookmark, or open the live Command Palette filtered to missions, vehicles or buildings.
- **Settings Backup Centre:** brings the existing authenticated encrypted full transfer, secret-free safe export and import into one surface, adds manual snapshots and retains five automatic local state snapshots plus the established previous-good recovery copy.
- **Toolkit Setup Wizard:** runs automatically only when no prior Toolkit state exists. It is skippable, reopenable and never edits MissionChief data.
- **Custom Sounds and Notifications:** are disabled by default, synthesize local audio without bundled or remote media, and request browser permission only after an explicit user action. Event cues cover new missions, completion, waiting patients, stuck incidents and Toolkit warnings.

## Compatibility and privacy

The v9 settings schema migrates in place. Missing Personalisation Studio fields receive safe defaults, legacy six-action Quick Wheel choices become slot descriptors, and an existing install is marked setup-complete so no update-time wizard interrupts it.

General settings snapshots contain only the normalized Toolkit state. The Discord webhook and Financial Archive identity or history remain in their dedicated stores and are included only by the existing AES-256-GCM encrypted transfer. Safe export remains deliberately secret-free. Theme codes accept only a fixed schema and normalized colours and numeric style values; they cannot inject arbitrary CSS.

MissionChief stays authoritative. Personalisation never dispatches, selects a vehicle, changes game data or automatically posts externally.

## Runtime boundary

The feature adds no `GM_xmlhttpRequest`, `fetch`, `XMLHttpRequest`, polling interval, managed timer, animation-frame scheduler, observer, raw event listener, direct ID lookup or HTML-assignment site. Studio and Wizard interaction is owned by their removable dialog nodes. Notification events reuse existing mission snapshot, spawn, patient, stuck and Doctor paths.

## Validation

Static and rendered runtime tests cover:

- v9 migration and fresh-install Wizard behaviour;
- device-layout isolation, ordering, visibility and bounds;
- theme-code schema and colour sanitisation;
- Quick Wheel slot migration, range and execution routing;
- bounded snapshots and secret-store separation;
- opt-in and deduplicated notification behaviour;
- Desktop, Tablet and iOS-safe control sizing;
- zero background primitive and network growth;
- byte-identical canonical and distribution copies.
