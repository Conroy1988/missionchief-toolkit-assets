# Home Response Builder development

The pure planner and checkpointed serial execution core are independently tested.
UK type 22 and all 14 vehicle options were inspected in the signed-in native game
on 2026-09-13. No game purchases were made during development.

The native adapter uses native forms and Credit links. Before release it requires
an integration test against an explicitly selected one-location plan, including
staff/training readiness, then a small batch. Do not run arbitrary purchases as tests.

Distances are straight-line separation, not driving time or guaranteed coverage.
Boundary holes and excluded areas are honoured. Geographic candidates still need
road/accessibility review. Unknown mutation results pause and never blindly retry.

Source references: live /buildings/new and an owned type-22 vehicle market;
LSS-Manager/LSSM-V.4 src/i18n/en_GB/buildings.ts and vehicles.ts were cross-checked,
but the native shop supersedes its older summary.

## Rebuild and verify

Run `npm ci --prefix extension/home-response`, then
`node --test extension/home-response/*.test.mjs` and
`python3 extension/build-recovered.py` from the repository root.
The build verifies every recovered file hash before applying the new module.
The package is a 0.23.1 test candidate, not a Chrome Store release.

## Acceptance remaining

- Load on desktop and Orion; confirm city-search provider availability and map controls.
- Choose one intended location, a vehicle without additional training and a suitable
  dispatch centre. Review the displayed name, position and Credit budget before confirming.
- Verify exactly one building and its selected vehicle, then test pause/resume on a small batch.
- A request with an unknown result is deliberately blocked from retrying; inspect the
  corresponding building/vehicle in the game. Resume now checks the complete owned-building catalogue for the exact name, type and coordinates. It recovers a unique match without another building request; vehicle recovery requires the selected vehicle in that exact building. Unknown or conflicting records remain paused.
- Road snapping, reuse of empty Home Responses and automatic staff training are not included.
  Placement is geometric and uses explicit exclusions and editable markers for review.

## 0.23.1 recovery fix

A live inspection confirmed the reported first building existed with zero vehicles.
Construction success no longer depends on a /buildings/:id redirect. Legacy 0.23.0
creating checkpoints recover their building cost from the saved reservation.
Opening the builder restores the saved account plan directly. The original error
is retained, and new intents record individual costs before submitting requests.
23 regression tests cover recovery, no duplicate purchases and cost accounting.
No live purchase was made while fixing the issue.

## 0.23.7 — location gap search

Corrects degree-to-mile grid spacing so adjacent candidates are not discarded by the exact distance check. Additional offset passes look for gaps without relaxing minimum spacing, land or exclusion checks. Scanline intersections are cached between passes. This is a deterministic proposal, not an optimal-packing guarantee.

The preview distinguishes existing buildings inside the area from the account-wide catalogue, offers spacing-circle overlays and explains sampled-position exclusions. Radius applies only in Point and radius mode. Changing area settings clears stale proposals. The cap remains 1000; Chrome Store submission remains deferred.

Validation: 41 automated checks, including gap recovery, adjacent grid distances, water, queue recovery and area controls. Real account placement counts and phone acceptance still require testing.

## 0.23.8 — city defaults and finer gap search

Selecting a search result always restores City boundary. A result without a polygon leaves the area unset and explains the explicit radius/drawing alternatives. The default on opening remains City boundary. Location counts and diagnostics now sit above the map; optional circles show both existing and proposed minimum spacing, with a compact checkbox.

Gap search refines to quarter-row/column offsets, preserving already accepted sites and all distance/land checks. This does not guarantee optimal packing or a higher count for every area. Video showed sparse three-mile Wigan proposals; account coordinates were not supplied, so the precise live count was not reproduced. 43 automated checks pass, including narrow dry gaps and city selection after radius mode. Chrome Store review remains untouched.
