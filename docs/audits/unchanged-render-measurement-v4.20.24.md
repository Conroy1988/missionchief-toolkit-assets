# Unchanged-render measurement protocol — Toolkit v4.20.24

This document implements the measurement infrastructure for Issue #255. It does **not** change the production Toolkit userscript, distribution files, version, update channel or runtime behaviour.

## What is measured

The development profiler now accepts render-probe events from two shortlisted synchronous paths:

- `updateUI()`;
- `renderOperationalPanels()`.

For each invocation it records only:

- the allowlisted render-path name;
- the allowlisted scenario;
- start time and synchronous duration;
- nested depth;
- the count of DOM mutation records delivered before the deferred finaliser;
- whether that invocation produced zero or one-or-more mutation records.

The report aggregates attempts, changed attempts, unchanged attempts, unchanged ratio, average duration, maximum duration and mutation-record totals by scenario and render path.

A zero-mutation invocation is classified as **unchanged output evidence**. The observer counts child-list, attribute and character-data records while excluding the profiler panel itself. Concurrent MissionChief mutations can still overlap a deferred render window, so this is correlation evidence rather than an exclusive write trace. It does not prove zero CPU, style recalculation or layout cost. Long tasks, layout shifts and equivalent browser conditions remain part of the interpretation contract.

## Why a generated development build is required

The production Toolkit deliberately keeps `updateUI()` and `renderOperationalPanels()` private inside its runtime closure. The external profiler cannot count function entries without either monkeypatching browser APIs or adding production hooks.

Neither is acceptable for a measurement-only change. Instead, CI generates a disposable local userscript from the verified canonical source:

```bash
npm install --no-save --ignore-scripts --no-audit --no-fund acorn@8.15.0
node tools/build-render-probe-userscript.mjs \
  --source src/MissionChief_Map_Command_Toolkit.user.js \
  --output MissionChief_Map_Command_Toolkit.render-probe.user.js \
  --manifest render-probe-manifest.json
```

The generator:

1. parses the current canonical userscript with pinned Acorn;
2. locates exactly one declaration of each target function;
3. wraps each development-copy function body in `try/finally`;
4. calls the optional profiler bridge at entry and exit;
5. marks the generated userscript as `[Render Probe]`;
6. records source and output SHA-256 values;
7. refuses to overwrite the canonical source.

The generated copy is an evidence tool only. It must never be committed to `src/`, copied into `dist/`, uploaded to Greasy Fork or used as a normal production installation.

## Installation order

Use a separate development browser profile.

1. Disable the normal stable Toolkit userscript for the duration of the capture.
2. Install `tools/mcms-performance-profiler.user.js` and ensure it runs first at `document-start`.
3. Install the generated `MissionChief_Map_Command_Toolkit.render-probe.user.js`.
4. Load MissionChief and confirm the small profiler control appears.
5. Reset, select one scenario, start, perform only that scenario, stop and export.
6. Repeat from a fresh page load for each scenario and device profile.
7. Remove the generated probe and restore the normal stable Toolkit after capture.

If the profiler is absent or loads late, the generated Toolkit continues because all bridge calls are optional. Such a run produces no render measurements and is not valid evidence.

## Required scenarios

The canonical machine-readable protocol is `.github/fixtures/unchanged-render-scenarios-v4.20.24.json`.

| Scenario | Minimum capture | Required activity |
|---|---:|---|
| `idle-map` | 30 seconds | Leave the settled map idle. |
| `settings-open-close` | 20 seconds | Open settings, switch one settings tab and close. |
| `mission-open-close` | 20 seconds | Open one mission, wait for live content and close. |
| `unit-selection` | 20 seconds | Select and deselect units while the mission remains open. |
| `map-pan-zoom` | 20 seconds | Pan, zoom in, zoom out and allow settling. |
| `layout-change` | 20 seconds | Resize or rotate once and allow layout settling. |

Run the sequence on:

- Desktop at 1920×1080 or larger;
- Tablet at approximately 1024×768;
- the normal iOS-compatible userscript host at approximately 430×932.

## Interpretation rules

Do not select an optimisation from one run.

A render path becomes an optimisation candidate only when equivalent repeated captures show:

- a material number of attempts;
- a consistently high unchanged ratio;
- non-trivial duration, mutation bursts, long tasks or layout evidence;
- identical lifecycle conditions;
- a clear invalidation boundary for MissionChief document, mission-window and layout replacement.

`updateUI()` and `renderOperationalPanels()` must be evaluated separately. Nested calls may legitimately attribute the same mutation batch to both paths; this is retained rather than guessed away.

## Privacy boundary

Scenario names are fixed and allowlisted. The profiler rejects free-text scenario labels.

The report does not retain mission titles, addresses, coordinates, unit or personnel names, alliance messages, DOM text, selectors, cookies, storage, webhook data, authentication material, full page URLs or resource paths.

## Current decision

The tooling is ready to collect authenticated equivalent evidence. No additional production render suppression is justified until those captures exist. Issue #255 therefore remains open after this infrastructure PR.
