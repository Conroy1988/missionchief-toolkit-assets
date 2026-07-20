# MissionChief Toolkit development performance profiler

This profiler supports Issue #249 and the staged optimisation programme in #247. It is a **separate development userscript**. It is not part of the Toolkit release, Greasy Fork stable channel or distribution bundle.

## Installation and operation

1. Install `tools/mcms-performance-profiler.user.js` as a separate local userscript in a development browser profile.
2. Load MissionChief with the production Toolkit enabled.
3. Use the isolated bottom-right control to **Start**, **Stop**, **Reset** or **Export**.
4. Run one scenario at a time and export the JSON before navigating away.
5. Remove or disable the profiler when the test is complete.

The API is also available as `window.__MCMS_PROFILER__` with `start()`, `stop()`, `reset()`, `report()`, `export()` and `destroy()`.

## Standard scenarios

Run each scenario from a fresh page load, with browser developer tools closed unless devtools overhead is the subject of the test.

### Desktop baseline

- 1920×1080 or larger viewport.
- Open the main map and wait 30 seconds.
- Open and close the Toolkit settings once.
- Open one mission, select and deselect units, then close the mission.
- Pan and zoom the map for 20 seconds.
- Stop at 90 seconds and export.

### Tablet layout

- Use a real tablet or browser responsive mode at the Toolkit tablet breakpoint.
- Repeat the desktop sequence without changing orientation midway.
- Run a second report after one orientation change.

### iOS-compatible browser

- Use Safari or the userscript host normally used for the Toolkit.
- Run the map-idle and mission-open sequence.
- Note unsupported Performance APIs in the report rather than treating missing entry types as zero-cost evidence.

## Data collected

- Toolkit startup timing values already exposed by `window.__MCMS_STARTUP_METRICS__`.
- Long-task and layout-shift timing where the browser supports those entry types.
- Resource totals grouped only by hostname and initiator type.
- Mutation batch counts and added/removed node totals; no DOM text or selectors.
- Document visibility state transitions.
- Aggregate counts from the Toolkit runtime lifecycle registry.
- Coarse browser/device metadata and viewport dimensions.

## Privacy boundary

The report does not collect mission titles, addresses, coordinates, vehicle or personnel names, alliance messages, webhook values, cookies, storage values or authentication material. Full page URLs and resource paths are not retained.

## Interpretation

The profiler adds a lightweight observer and one runtime-count sample per second while active. Compare equivalent scenarios and focus on large differences, repeated long tasks, mutation bursts and resource counts. Do not optimise solely to reduce one static or sampled count; preserve behaviour and validate every change with existing fixtures.
