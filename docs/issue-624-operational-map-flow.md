# Issue #624 — v10.2 Operational Map Flow

Version 10.2 adds four deliberately bounded, reversible tools to the existing v10.1 command experience.

## Mission Progress Rings

- An independent Mission Intelligence toggle draws an accessible ring only when MissionChief exposes an exact live clearing value or exact patient/prisoner totals.
- `liveCurrentValue` is treated as MissionChief's remaining value, so the displayed completion is `100 - liveCurrentValue`.
- Unknown progress is not estimated. Native mission markers remain untouched.
- The overlay uses the existing mission-snapshot lifecycle and shared Leaflet pane; it adds no request, timer, poller or observer.

## Unit Locator & Follow Mode

- Search current personal vehicles by caption, numeric ID, vehicle type, station and FMS/status bucket.
- Locate performs a one-time map focus. Follow Mode binds only to the explicitly selected live vehicle marker.
- Follow stops on manual map movement, loss/removal of the marker, Safe Mode, Toolkit replacement or explicit Stop.
- It cannot select or dispatch a vehicle.

## Alliance Chat Mission Previews

- Mission links already present under `#mission_chat_messages` gain a compact, accessible preview when their live mission snapshot is already available on the page.
- Previews may show caption, approximate credits, current patients/prisoners, personal unit commitment and known missing requirements.
- The feature never fetches a chat-linked mission, stores chat text/user identity or modifies the native mission link.
- It reuses the existing bounded MutationObserver and debounce path.

## One-Click Session Cleanup

- Cleanup always opens an exact preview and confirmation before changing anything.
- Its allowlist is limited to vehicle follow, temporary mission focus/spawn effects, stale notification dedupe memory, the recent completion-match queue, transient command surfaces/search text, incident-feed pause/expansion state and rebuildable runtime caches.
- Settings, device layouts, themes, profiles, bookmarks, recovery snapshots, Discord webhooks, secrets, Financial Archive history and MissionChief data are protected and never included.

## Release gates

- The five release copies must be byte-identical.
- No new network request, broad MutationObserver, background poller or interval is permitted.
- Existing v10 settings migrate without reset or secret-bearing export changes.
- Static and runtime Issue #624 contracts join the complete retained userscript preflight.
