# v10.16.8 performance and responsive-layout audit

Date: 2026-08-22

Candidate: `10.16.8`

Source SHA-256: `3b781defe7e8eafc43f9bb0f4eb0190ee8e2789a5983f985dd1570c86b713856`

Baseline: `origin/main` / `10.16.7`

## Scope

This audit covers Toolkit startup and tab switching, direct mission-list mutation pressure, idle activity, DOM-write suppression, Desktop command workspace geometry, Tablet panel placement, iOS tab flow, dock labels, and visible text containment. Existing actions, settings, storage keys, themes and device modes remain unchanged.

The browser matrix exercised 192 states: Desktop, Tablet and iOS across all eight interface themes and all eight command sections. It measured visible text overflow, viewport escape, startup timing, section-switch timing, DOM queries, mutations and style or attribute writes. Focused screenshots were also reviewed at 1440×900, 1024×768 and 390×844.

The browser matrix was captured from source `c4c7631871eb962030014638290ce4148d729bea54a1e1f461637ea11f661a4d`. The final candidate changes only one release-briefing sentence after that capture; executable logic, CSS and rendered matrix content are byte-identical. The final source hash above separately completed the 72-execution runtime stress audit and all promotion gates.

## Measured results

| Measurement | v10.16.7 baseline | v10.16.8 candidate | Result |
|---|---:|---:|---:|
| Visible text or viewport overflows | 1,220 | 0 | Eliminated across all 192 states |
| Desktop mission-storm selector scans | 3,009 | 2–9 | More than 99.7% reduction across final runs |
| Tablet mission-storm selector scans | 3,021 | 20 | 99.34% reduction |
| iOS mission-storm selector scans | 3,021 | 21 | 99.30% reduction |
| Static selector call sites | 400 | 360 | 10.0% reduction |
| Repeated selector families | 74 | 71 | Reduced without adding observers |
| Stable-refresh write attempts | 14,500 | 0 | Existing zero-write guarantee retained |
| Stable-refresh mutation records | 7,100 | 0 | Existing zero-mutation guarantee retained |
| Runtime stress executions | not portable in this environment | 72/72 passed | Portable peak-memory collection; no failures |

The mutation storm inserts and removes 250 direct mission-sidebar rows. Its fixed 1.1 second observation window is intentionally not a wall-clock benchmark; selector and write counts are the meaningful comparison.

An alternating three-run comparison exercised 192 section switches per build on both Desktop and iOS. Desktop median switching remained effectively at parity (`61.6 ms` to `62.4 ms`, a `0.8 ms` difference) while p95 improved from `92.7 ms` to `81.7 ms`. iOS median improved from `47.9 ms` to `43.9 ms` and p95 improved from `60.5 ms` to `56.6 ms`. Bootstrap elapsed time moved in both directions between runs and was treated as browser/server scheduling variance rather than presented as a performance gain. Deterministic selector, write, mutation, observer and containment counts are the release gates.

## Changes validated

- Direct mission-sidebar batches take a dedicated observer path before generic descendant classification. Mission-value and vehicle-badge observers reject the same irrelevant batch before running selectors.
- Reused controls and settings are indexed once per UI refresh, and unchanged attributes, text, classes and styles are not written again.
- Runtime stress peak-memory measurement uses Node's portable resource usage API instead of a hard-coded GNU `time` executable.
- Tablet size is reapplied after every dock-fit branch, preventing a later layout pass from wiping the safe visual-viewport bounds.
- Tablet command cards use one readable content column while retaining the existing scroll surface and every control.
- iOS tabs occupy three explicit rows and are static within their grid row, preventing the prior sticky offset from moving tabs over active content.
- Desktop navigation, bookmark actions, building summaries, theme names, dock labels and operational state text use breakpoint-safe widths and wrapping.

## Compatibility and safety

- No storage schema or storage key changed.
- No feature, action, theme, keyboard shortcut, device mode or network route was removed.
- Full accessible names and tooltips remain on compact dock controls; only breakpoint-specific visual labels are shortened.
- The layout matrix reported no horizontal document expansion and no visible text overflow after the final pass.
- The performance budget passed. Source size changed by `+0.24%` and embedded CSS by `+0.62%`; timer, observer, listener, request and startup-hook counts did not increase. The inherited CSS headroom warning remains visible at 96.9% of the rule-block ceiling.
- The exact candidate completed all static, performance, integrity, dependency, runtime, development and workflow promotion stages in 65.3 seconds.
- Automated contrast estimates were not treated as authoritative where themed gradients and images obscure the computed background colour; final readability was verified from rendered Desktop, Tablet and iOS captures in addition to containment measurements.
