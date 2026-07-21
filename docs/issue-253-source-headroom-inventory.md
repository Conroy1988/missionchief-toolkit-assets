# Issue #253 — safe source headroom

## Measured baseline

- Toolkit version: `4.20.20`
- Source: **31,671 lines** / 32,000
- Remaining headroom: **329 lines**
- Source SHA-256: `281f1635a8aacced565d7211956ba7d9a4a87e7c6de99f2fd18ade2acedc5832`
- Main stylesheet template: **12,218 physical lines**

## Selected bounded subsystem

Only standalone source formatting inside the existing `installMainStyles` template is removed: **300 blank lines**, **185 lines across 125 full-line CSS comment blocks**, and **15 newlines immediately before full-line closing braces**. The canonical CSS content is identical before and after.

The implementation deliberately excludes inline comment removal, selector grouping, declaration consolidation, stylesheet splitting, deferred delivery, observer scope, scheduler timing, state ownership and network sequencing.

## Result

- Candidate version: `4.20.21`
- Recovered source lines: **500**
- Candidate source lines: **31,171**
- Resulting headroom: **829 lines**
- Canonical CSS hash: `29ebbb034614b751ee485ce2c02468e8b98cdd4a81bec31d94f1a1959d7ddb69`
- Candidate template hash: `6fe8a5e148a0f57c66ab08981790cd8d02f5160f9e0452b252aaea6662afdd2f`
- MutationObserver constructions: **12 → 12**
- ResizeObserver constructions: **4 → 4**
- Scheduler calls: **121 → 121**

## Permanent contract

The committed fixture records the exact formatting categories removed, canonical CSS hash and exact candidate template hash. Validation fails if the reviewed template changes, removable formatting returns without review, line arithmetic drifts or the recovery falls below 500 lines.

## Rollback boundary

Revert the single implementation commit. No storage migration, retained DOM reference, lifecycle change or external dependency is introduced.
