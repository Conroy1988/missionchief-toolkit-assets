# Issue #696 — iOS Patient Transport Sweep parity

Toolkit v10.6.2 repairs the real-device gap left by v10.6.1. MissionChief can serve the iPhone mission surface as current mission-list HTML without desktop `missionMarkerAdd(...)` scripts or a populated Leaflet `mission_markers` registry. Manual Scan and Start Sweep now recognise `#missions-panel-body`, suffixed alliance lists and native `mission_id` records instead of rejecting that valid mobile response.

The fallback first requires positive alliance-list or explicit owner evidence. It then hydrates only current patient-bearing alliance candidates from their same-origin mission pages, with a maximum of 80 candidates and four concurrent requests. The work occurs only after the user deliberately presses Scan or Start Sweep; there is no interval, observer, recurring scan or background request.

Personal, unknown-owner, deleted, stale, prisoner and non-transport records fail closed. Desktop marker discovery remains the first path, verified personal-vehicle exclusion and MissionChief's native Cancel Transport and Discharge patient controls remain authoritative, and persistent completion reports plus exact-once Discord delivery are unchanged.

The permanent regression starts with an empty marker registry, no preloaded overlays and mobile mission-list HTML containing no `missionMarkerAdd` signature. It proves that the iOS and desktop paths produce the same eligible mission IDs while personal, unknown-owner, stale, prisoner and non-transport records remain excluded.
