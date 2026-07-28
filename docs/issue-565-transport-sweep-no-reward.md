# Issue #565 — Patient Transport Sweep no-reward release path

Toolkit v8.2.0 recognises only the exact visible `Release patient (No reward)` mission control whose same-origin path matches `/vehicles/{vehicleId}/patient/-1`.

Only vehicle IDs already verified by the existing sweep candidate collector are eligible. The sweep releases one patient, reopens the same mission, verifies that the released vehicle-specific control is absent, records one confirmed patient outcome and then repeats for the next patient. A persistent control, failed mission reopen or cancellation stops the fast path safely. When no matching control exists, the established MissionChief-native vehicle-window discharge process remains unchanged.

The implementation adds no observer, interval or new network-request call site. Permanent executable coverage includes multiple patients, allowance limiting, missing controls, persistent controls, reopen failure, cancellation and mission-progress isolation.
