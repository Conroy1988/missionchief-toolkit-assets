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
The package is a 0.23.0 test candidate, not a Chrome Store release.

## Acceptance remaining

- Load on desktop and Orion; confirm city-search provider availability and map controls.
- Choose one intended location, a vehicle without additional training and a suitable
  dispatch centre. Review the displayed name, position and Credit budget before confirming.
- Verify exactly one building and its selected vehicle, then test pause/resume on a small batch.
- A request with an unknown result is deliberately blocked from retrying; inspect the
  corresponding building/vehicle in the game. Automatic reconciliation is not implemented.
- Road snapping, reuse of empty Home Responses and automatic staff training are not included.
  Placement is geometric and uses explicit exclusions and editable markers for review.
