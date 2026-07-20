# Issue #167 — Live Mission Requirements capacity contract

## Authority and calculation

- The official MissionChief catalogue supplies the total baseline where available.
- Native `#missing_text` remains the live outstanding signal and is reconciled with counted on-site capacity.
- `#mission_vehicle_at_mission`, `#mission_vehicle_driving` and checked dispatch rows are separate, mutually exclusive buckets.
- The displayed result is `max(0, Required - On site - Responding - Selected)`.
- Without a catalogue baseline, Required is reconstructed as native missing plus observed on-site capacity so on-site units are not subtracted twice.

## Operational table ownership

- Canonical MissionChief **Units Responding** rows remain authoritative when their section is collapsed or relocated inside the active mission window.
- Canonical MissionChief **Vehicles on Scene** rows remain authoritative when their section is collapsed or relocated inside the active mission window.
- Collapse-only visual hiding never removes committed capacity, but hidden stale lightboxes, mismatched mission IDs and unrelated tables remain excluded.

## Lifecycle

Selection changes, dispatch transitions, arrivals, departures, cancellations, missing-text replacement and mission-window navigation schedule one bounded recalculation. On-site capacity takes precedence over responding, which takes precedence over selected during temporary DOM overlap.

## Visual states

- Green: definitely fulfilled.
- Amber: partially fulfilled or capacity is bounded/uncertain.
- Red: definitely outstanding.
- Neutral unresolved: mapping or authority is insufficient; never falsely green.

Definitively fulfilled rows are suppressed from the active list and return immediately if committed capacity is removed or demand increases. The panel remains in normal document flow and uses compact Desktop/Tablet tables and a compact five-metric iOS card row.
