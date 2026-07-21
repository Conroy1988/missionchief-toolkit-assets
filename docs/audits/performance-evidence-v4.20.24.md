# Performance evidence checkpoint — Toolkit v4.20.24

## Safety boundary

This checkpoint is measurement-only. It changes no userscript source, distribution asset, version, release channel, observer scope, scheduler timing, selector, style rule or rendered state.

Production baseline:

- Toolkit: `4.20.24`
- Source SHA-256: `4bd9a9f3708292a6a48523f2f4d69b105e5957395fb10bcbeec671a4d8a4029c`
- Source: `2,060,506` bytes and `31,657` lines
- Verified public release completed on 21 July 2026

## Refreshed deep audit

The AST-backed v4.20.24 evidence records:

- 1,778 functions and callbacks;
- 121 scheduler call sites;
- 12 MutationObserver constructions;
- 4 ResizeObserver constructions;
- 19 total `.observe()` registrations after manual reconciliation;
- 10 broad `subtree: true` registrations;
- 3 explicit document/body subtree registrations;
- 343 lines of remaining source headroom;
- an 818,141-byte main embedded CSS template with approximately 6,394 rule blocks;
- `updateUI()` as the highest non-style DOM hotspot at 52 reads and 49 writes in static evidence.

Static concentration does not establish live frequency or user-visible cost.

## Observer ownership conclusion — #256

Every construction and registration has been inventoried with its installation condition, target/options, scheduling, owner, teardown, duplicate guard, replacement handling and current deterministic coverage.

- 15 observers are owned by the replaceable Toolkit runtime, with several also having subsystem-specific disconnect paths.
- The early Alliance Buildings context observer is the sole deliberate page-process-lifetime exception and is guarded by `allianceBuildingsContextWatcherInstalled`.
- The three AST-unresolved registrations are all calls on the runtime-tracked main MutationObserver created by `boot()`.
- No observer is orphaned.
- No observer merge or scope reduction is justified by ownership evidence alone.

Issue #256 can close as an audit/inventory task. Any later observer optimisation must remain a separate subsystem-specific PR with equivalent authenticated browser evidence.

## Render evidence status — #255

The existing #279 root-attribute optimisation already guards all 22 root attributes with `setAttributeIfChanged` and deterministic runtime tests. The controlled Chromium harness included in this checkpoint independently verifies the intended browser-DOM contract when executed in CI:

- first application writes all 22 missing attributes;
- an unchanged repeat writes zero;
- one changed state writes one;
- external removal is repaired with one write.

This resolves only the isolated root-write surface. It does not measure unchanged operational-panel renders, mission-window replacements, map movement or settings interactions. Issue #255 therefore remains open pending authenticated scenarios from the external profiler.

## CSS evidence status — #254

The controlled browser harness injects the actual v4.20.24 main CSS template across Desktop, Tablet and iOS-sized viewports and records insertion plus forced style/layout samples. These values are runner-specific diagnostics, not budgets.

Synthetic style installation cannot reproduce MissionChief map tiles, mission markers, settings, mission windows or map-pan workloads. Issue #254 remains open until equivalent authenticated browser captures prove that CSS parsing, style recalculation or layout is a material bottleneck.

## Decision queue

1. Close #256 after the measurement PR merges.
2. Keep #254 and #255 open.
3. Capture equivalent authenticated profiler sessions for idle map, settings open, mission open/close, unit selection, map pan and layout change on Desktop, Tablet and iOS-compatible scenarios.
4. Select one isolated runtime change only when live evidence identifies a measurable target and deterministic invalidation/visual contracts exist.
5. Do not create a public Toolkit release for this measurement-only checkpoint.
