# Controlled Chrome evidence — Toolkit v8.3.2

> Controlled synthetic Chromium evidence. It verifies repeatable micro-contracts, but it is **not** authenticated MissionChief runtime evidence and does not justify CSS modularisation by itself.

## Baseline

- Source SHA-256: `e719dd7f26686895cd1ba9e31dd006c775134af86000eb7d32800feea6843cfa`
- Source: **1,656,814 bytes**, **25,272 lines**
- Main embedded CSS: **683,558 bytes**, approximately **5,379** rule blocks
- Guarded root attributes: **21**
- Samples per viewport: **11** (first sample excluded from summary medians)

## Results

| Scenario | Viewport | CSS insertion median* | CSS insertion P90* | Forced style/layout median* | Forced style/layout P90* | Long tasks | Layout shift | Unchanged root writes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| desktop | 1440×900 | 12.7500 ms | 12.9000 ms | 9.7000 ms | 9.9000 ms | 1 | 0.000000 | 0 |
| tablet | 1024×768 | 14.4000 ms | 15.2000 ms | 11.6500 ms | 12.5000 ms | 1 | 0.000000 | 0 |
| ios | 390×844 | 14.0000 ms | 15.5000 ms | 12.0500 ms | 14.0000 ms | 1 | 0.000000 | 0 |

* The first sample is a warm-up and is excluded. Values are diagnostic, hardware-specific and are not release budgets.

## Decisions

- The guarded root-write contract remains correct for the current authoritative attribute set: first application writes every missing attribute, an unchanged repeat writes zero, one changed value writes one and external tampering is repaired with one write.
- The controlled Chrome measurements establish a current reproducible baseline across Desktop, Tablet and iOS-sized viewports.
- This evidence does not contain MissionChief map, mission-window, settings or pan workloads. It does not prove a user-visible CSS bottleneck and does not authorise stylesheet modularisation.
- Equivalent authenticated MissionChief profiler scenarios remain required before changing style delivery.
