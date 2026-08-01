# Issue #624 — v10.2 Operational Map Flow

Version 10.2 adds four deliberately bounded, reversible tools to the existing v10.1 command experience.

> **v10.2.3 retirement:** Mission Progress Rings and Alliance Chat Mission Previews were removed at the user's request. Their settings, rendering, styles and lifecycle work no longer exist. Unit Locator & Follow Mode and One-Click Session Cleanup remain supported.

## Mission Progress Rings

- Retired in v10.2.3.
- The Leaflet layer, marker renderer, settings controls, saved-state key and styling were removed.
- MissionChief's native mission markers are now left unchanged.

## Unit Locator & Follow Mode

- Search current personal vehicles by caption, numeric ID, vehicle type, station and FMS/status bucket.
- Locate performs a one-time map focus. Follow Mode binds only to the explicitly selected live vehicle marker.
- Follow stops on manual map movement, loss/removal of the marker, Safe Mode, Toolkit replacement or explicit Stop.
- It cannot select or dispatch a vehicle.

## Alliance Chat Mission Previews

- Retired in v10.2.3.
- Generated cards, settings controls, saved-state key, styling and chat-specific MutationObserver routing were removed.
- Alliance Chat is now left in its native MissionChief form.

## One-Click Session Cleanup

- Cleanup always opens an exact preview and confirmation before changing anything.
- Its allowlist is limited to vehicle follow, temporary mission focus/spawn effects, stale notification dedupe memory, the recent completion-match queue, transient command surfaces/search text, incident-feed pause/expansion state and rebuildable runtime caches.
- Settings, device layouts, themes, profiles, bookmarks, recovery snapshots, Discord webhooks, secrets, Financial Archive history and MissionChief data are protected and never included.

## Release gates

- The five release copies must be byte-identical.
- No new network request, broad MutationObserver, background poller or interval is permitted; the v10.2.3 retirement reduces observer work.
- Existing v10 settings migrate without reset or secret-bearing export changes.
- Static and runtime Issue #624 contracts join the complete retained userscript preflight.
