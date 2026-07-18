# Issue #167 — Live Mission Requirements capacity contract

## Authority and calculation

- The official MissionChief catalogue supplies the total baseline where available.
- Native `#missing_text` remains the live outstanding signal and is reconciled with counted on-site capacity.
- `#mission_vehicle_at_mission`, `#mission_vehicle_driving` and checked dispatch rows are separate, mutually exclusive buckets.
- The displayed result is `max(0, Required - On site - Responding - Selected)`.
- Without a catalogue baseline, Required is reconstructed as native missing plus observed on-site capacity so on-site units are not subtracted twice.

## Lifecycle

Selection changes, dispatch transitions, arrivals, departures, cancellations, missing-text replacement and mission-window navigation schedule one bounded recalculation. On-site capacity takes precedence over responding, which takes precedence over selected during temporary DOM overlap.

## Visual states

- Green: definitely fulfilled.
- Amber: partially fulfilled or capacity is bounded/uncertain.
- Red: definitely outstanding.
- Neutral unresolved: mapping or authority is insufficient; never falsely green.

The panel remains in normal document flow and uses compact Desktop/Tablet tables and a compact five-metric iOS card row.
