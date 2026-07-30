# Issue #593 — Toolkit v8.3.2 controlled Chrome CSS baseline

Measurement-only controlled Chrome evidence for parent Issues #247 and #254.

The evidence was generated from exact Toolkit v8.3.2 without modifying the production userscript, distribution files, version or release state. It measures stylesheet insertion, forced style/layout, long tasks, layout shifts and the guarded-root-write contract across Desktop, Tablet and iOS-sized viewports.

## Current controlled results

| Viewport | CSS insertion median | Forced style/layout median | Layout shift | Unchanged root writes |
|---|---:|---:|---:|---:|
| Desktop 1440×900 | 12.75 ms | 9.70 ms | 0 | 0 |
| Tablet 1024×768 | 14.40 ms | 11.65 ms | 0 | 0 |
| iOS-sized 390×844 | 14.00 ms | 12.05 ms | 0 | 0 |

The exact source contains 683,558 bytes of embedded main CSS and approximately 5,379 rule blocks. Chrome 150 used 11 samples per viewport, excluding the first warm-up sample from summary medians.

## Decision

No production CSS change is authorised. Controlled runner timings are hardware-specific diagnostics, not authenticated MissionChief runtime evidence. Equivalent live idle-map, settings, mission-window and map-pan captures remain required before stylesheet modularisation.

See:

- `controlled-browser-evidence.json` — complete samples and machine-readable conclusions;
- `controlled-browser-evidence.md` — reviewed summary;
- `manifest.json` — source, workflow and artifact provenance.
