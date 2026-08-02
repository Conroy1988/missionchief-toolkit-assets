# Authenticated MissionChief performance capture — Toolkit v10.3.1

This is the remaining browser-only evidence stage for Issues #247, #254 and #255.

## Capture authority

- Toolkit version: `10.3.1`
- Canonical production merge: `089502a8319b3de116ea2a36a22d2957bbf82050`
- Final release-state HEAD: `9427d27240fed63f130c53c5a57852a912c3dd33`
- Canonical source SHA-256: `b318a72d2bb20c03db75406ed76ecfcf4500a739e32ce9de91490dc02bd5e829`
- Capture profile: `issue247-v1031-live-performance`
- Profiler: development-only, privacy-bounded and excluded from all stable update channels
- Production source, distribution and release state: unchanged by this capture refresh

## Bundle

The `Live Performance Capture Bundle` workflow creates one installable userscript containing:

- an exact disposable copy of Toolkit v10.3.1;
- AST instrumentation around `updateUI()` and `renderOperationalPanels()`;
- the bounded performance profiler;
- an automatic six-stage capture guide;
- exact source/profile markers embedded in the exported report;
- no `@downloadURL` or `@updateURL` metadata.

The generated artifact is named `missionchief-toolkit-v10.3.1-authenticated-performance-capture`. Its installable userscript is `MissionChief_Toolkit_v10.3.1_Authenticated_Performance_Capture.user.js`.

The bundle uses a distinct userscript name and namespace. The normal Toolkit userscript must be disabled during the controlled session to prevent two Toolkit runtimes from mounting concurrently.

## Required scenarios

1. **idle-map** — leave the map idle for at least 20 seconds;
2. **settings-open-close** — open and close Settings five times without changing settings;
3. **mission-open-close** — open and close at least three active mission windows;
4. **unit-selection** — select and deselect several units without dispatching;
5. **map-pan-zoom** — pan and zoom repeatedly;
6. **layout-change** — resize, rotate or change Tablet layout, then restore it.

The capture starts automatically. The bottom-right panel advances through the scenarios and exports a JSON report at completion.

## Privacy boundary

The report contains aggregate timing, mutation, resource-host and runtime-ownership counts. It does not contain mission titles, addresses, coordinates, vehicle or personnel names, alliance messages, cookies, local-storage values, authorization material or Discord webhook contents.

## Validation

`tools/validate-live-performance-report.mjs` rejects reports unless they:

- match the exact capture profile, Toolkit version and canonical source hash;
- are stopped before export and run for at least 60 seconds;
- include all six scenario transitions in order;
- include `updateUI()` measurements for each scenario;
- include bounded runtime, mutation, long-task and layout-shift arrays;
- contain no forbidden sensitive fields.

The workflow also proves that `src/`, `dist/`, the root userscript and `status/` are unchanged, that source/distribution copies remain byte-identical, and that the generated capture userscript contains no stable update URL.

A valid report is evidence for review, not automatic authority to modularise CSS or change render scheduling. Any production optimisation still requires an isolated implementation, before/after evidence, behaviour parity and a clean rollback boundary.

This document supersedes `live-performance-capture-v8.3.2.md`, whose bundle is historical evidence only and must not be used against current production.
