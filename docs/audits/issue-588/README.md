# Issue #588 — Toolkit v8.3.1 performance baseline refresh

This evidence pack is a measurement-only child of Issue #247. It changes no Toolkit source, distribution mirror, version, feature behaviour or release state.

## Exact authority

- Toolkit version: `8.3.1`
- Audited `main`: `4247b7caa7dad78007010e8bf0e33c352f3d45e3`
- Source SHA-256: `363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089`
- Source bytes: `1,654,208`
- Source lines: `25,228`
- Source/distribution parity: exact

## Runtime stress

The runtime test plan is now discovered from the canonical preflight instead of a second hard-coded list.

- Canonical runtime contracts: 10
- Explicit heavy integration contracts: 1
- Repeated executions: 96
- Total elapsed: 15.98 seconds
- Maximum observed RSS: 129,288 KiB
- Issue #564 attended-Incident-Wire runtime coverage: included
- Failures: none

## Static deep-performance inventory

- Functions and callbacks: 1450
- Ranked non-wrapper functions: 1449
- MutationObserver constructions: 11
- ResizeObserver constructions: 4
- Observer registrations: 15
- Broad subtree registrations: 9
- Scheduler call sites: 100
- Repeated literal selectors: 54

## Interpretation boundary

This pack provides exact v8.3.1 static and CI stress evidence. It does **not** claim authenticated MissionChief browser timing, style-recalculation cost, mutation frequency or memory-retention behaviour. Issues #254 and #255 remain gated against unsupported speculative optimisation until equivalent browser evidence or a deterministic exact proof isolates a safe change.
