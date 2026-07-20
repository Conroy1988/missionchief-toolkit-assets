# Performance and reliability baseline — Toolkit v4.20.10

## Scope

This is the measurement-only baseline for Issue #247. It changes no userscript runtime, distribution asset, feature state, version or release channel.

- Canonical commit at audit start: `f349beb4eaa509e7bc8cc2c89bed17335e000603`
- Userscript version: `4.20.10`
- SHA-256: `3ae45f2c6b875aa071c9cbffe20f84859bda04a96d8e17e97371f0425a14c943`
- Source bytes: `2,017,016`
- Source lines measured by the performance checker: `31,785`
- Gzip level-9 size: `344,739` bytes

A fifteen-run Node syntax/parse proxy produced a median of approximately `92.3 ms`, with a range of approximately `88.7–97.0 ms` on the audit environment. This is a compile proxy only, not a MissionChief browser benchmark.

## Corrected static runtime surface

| Indicator | Direct-only legacy count | Wrapper/alias-aware count |
|---|---:|---:|
| Timeout call sites | 2 | 99 managed call sites |
| Interval call sites | 1 | 1 managed call site |
| Animation-frame call sites | 1 | 14 managed call sites |
| Listener call sites | 39 direct | 31 managed call sites |
| MutationObserver constructions | 8 | 12 including aliases |
| ResizeObserver constructions | 1 | 4 including aliases |
| Observer registrations using `subtree: true` | not reported | 10 |
| Document/body subtree registrations | not reported | 3 |
| Managed observer registrations | not reported | 15 `runtimeTrackObserver` call sites |
| Idle scheduling | not reported | 3 `runtimeRunWhenIdle` call sites |
| Network request sites | not reported | 4 |

The discrepancy is a measurement defect, not evidence that the wrappers themselves are unsafe. The Toolkit runtime registry owns timer, animation-frame, observer, request and listener teardown; its fixture-backed lifecycle contract remains a required safety barrier.

## Structural pressure

| Metric | Current | Limit | Utilisation |
|---|---:|---:|---:|
| Source bytes | 2,017,016 | 3,000,000 | 67.2% |
| Source lines | 31,785 | 32,000 | 99.3% |
| Embedded CSS bytes | 866,334 | 950,000 | 91.2% |
| Embedded CSS rule blocks | 6,621 | 7,000 | 94.6% |
| Alias-aware MutationObservers | 12 | 12 | 100% |
| Alias-aware ResizeObservers | 4 | 4 | 100% |
| Broad subtree observers | 10 | 10 | 100% |

The line ceiling is the immediate repository constraint. CSS parse/style volume and observer breadth are the highest-value runtime investigation areas. The new metrics are baseline-locked so growth cannot occur silently.

## Static audit hotspots for targeted profiling

These are investigation targets, not automatic refactoring instructions:

1. `installMainStyles` contains the large embedded CSS surface. Any split must preserve first-paint behaviour and avoid flashes or missing feature styles.
2. `renderOperationalPanels` is a large, selector-heavy render path. Profiling should determine how often it executes with unchanged data before introducing signatures or keyed patching.
3. `updateUI` contains a high concentration of DOM lookups and is invoked widely. Stable-reference caching is a candidate only with explicit invalidation on MissionChief window replacement.
4. Broad document/body observers are already filtered and debounced. They must be narrowed only when fixture evidence proves identical detection and teardown semantics.
5. Financial-ledger requests are intentionally sequential in several paths. Parallelisation is prohibited without evidence that ordering, retries and rate limits remain safe.

## Optimisation order

1. Correct measurement and preserve the runtime source unchanged.
2. Add browser evidence for invocation frequency, long tasks and DOM mutation volume.
3. Optimise one subsystem per pull request.
4. Require deterministic behavioural fixtures, before/after metrics and a rollback boundary.
5. Merge only after canonical validation, full userscript audit, boot/lifecycle, performance, code-integrity, documentation and distribution checks are green.
