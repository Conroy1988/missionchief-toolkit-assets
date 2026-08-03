# Authenticated MissionChief performance capture — Toolkit v10.5.4

This measurement-only capture refresh is the evidence gate for Issues #247, #255 and #687. It does not change the production userscript, distribution assets, version or release channel.

## Capture authority

- Toolkit version: `10.5.4`
- Canonical production merge: `06396e63b3f5473cdde73c68791f7cfaa0afba16`
- Canonical source SHA-256: `3b7f344883f9d44980a7a416cba3dfff1d68cfa5571ce9612a9565390fc21a77`
- Capture profile: `issue247-v1054-feed-performance`
- Profiler: development-only, privacy-bounded and excluded from stable update channels
- Production source, distribution and release state: unchanged

## Instrumented paths

The disposable bundle records aggregate timings and mutation counts around:

- `updateUI()`;
- `renderOperationalPanels()`;
- `ensureUi()`;
- `renderMajorIncidentFeed()`;
- `positionMajorIncidentFeed()`.

The Feed-specific paths expose the v10.5.4 healthy-state baseline before Issue #687 can change runtime scheduling.

## Required scenarios

1. **idle-map** — leave the map idle for at least 20 seconds;
2. **settings-open-close** — open and close Settings five times without changing settings;
3. **mission-open-close** — open and close at least three active mission windows;
4. **unit-selection** — select and deselect several units without dispatching;
5. **map-pan-zoom** — pan and zoom repeatedly;
6. **layout-change** — resize, rotate or change Tablet layout, then restore it.

The validator requires ordered coverage for all six scenarios from both `updateUI()` and `renderMajorIncidentFeed()`. Feed positioning and UI-integrity measurements remain reported when they occur, but are not fabricated when a scenario legitimately produces no call.

## Privacy boundary

The report contains aggregate timing, mutation, resource-host and runtime-ownership counts. It does not contain mission titles, addresses, coordinates, vehicle or personnel names, alliance messages, cookies, local-storage values, authorization material or Discord webhook contents.

## Release boundary

A valid v10.5.4 report is baseline evidence only. Issue #687 must produce an equivalent candidate report, deterministic regression fixtures, identical feature behaviour and a clean rollback boundary before production landing. The v10.3.1 capture remains historical and must not be used as the current baseline.
