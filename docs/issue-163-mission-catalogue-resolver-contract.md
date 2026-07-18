# Issue #163 — MissionChief catalogue-backed requirements resolver

## Authority model

1. The active MissionChief mission window remains authoritative for current outstanding requirements.
2. Native selected checkboxes and the native en-route table remain authoritative for selected and travelling units.
3. `/einsaetze/<definition>` is an official static baseline and diagnostic cross-reference only.
4. Catalogue baseline values must never be labelled or calculated as current **Still needed** quantities.

## Retrieval

- Resolve the mission definition from a native `/einsaetze/` help link first, preserving `overlay_index` variations.
- Fall back to MissionChief's native mission type ID.
- Fetch only the active definition, using same-origin credentials.
- Cache a fresh definition for six hours, retain a bounded stale fallback for seven days, and cap the session cache at 96 entries.
- Never bulk-fetch the full mission catalogue during normal startup.

## Failure behaviour

- Live data available: render the live matrix immediately; catalogue retrieval is non-blocking.
- Live source absent or unparseable and catalogue available: render a clearly labelled official baseline table.
- Live source empty: preserve MissionChief's authoritative no-outstanding-requirements state.
- Network failure: use a bounded stale catalogue entry where available; otherwise keep the existing reportable failure state.
- When live data later appears, replace the baseline automatically with the live matrix.

## Diagnostics

Report Mission includes catalogue state, definition ID, variation, official title, parsed and unmapped rows, credits, patients, variation count, requirement summary, and live-versus-baseline mismatches.

## Validation

Recorded fixtures cover a simple mission, a personnel-heavy major incident, alternative vehicles, conditional requirements, public-order personnel, mission variations, cache expiry, stale fallback and live/catalogue mismatch detection.

Maintainer review confirmed that conditional values such as `2 (50%)`, grouped thousands and plain four-digit quantities are parsed independently from probability percentages before the trusted PR validation suite runs.

Performance policy revision `2026-07-18-v4.16.0` increases only the absolute source bytes and line envelope. Runtime-workload, CSS and relative regression limits remain unchanged, and the candidate adds no timers, observers, listeners or startup hooks.

The final candidate was rebased onto canonical `main` commit `7335f819fd3f9ab77f88bb90765a45c1ad9a159d`, the post-v4.15.5 Greasy Fork version-reconciliation commit, before merge.
