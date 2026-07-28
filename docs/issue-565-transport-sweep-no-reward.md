# Issue #565 — Patient Transport Sweep no-reward release path

Toolkit v8.2.1 recognises only the exact visible `Release patient (No reward)` control whose same-origin path matches `/vehicles/{vehicleId}/patient/-1` and whose vehicle is already verified by the existing sweep candidate collector.

The control may be inserted after mission render, so the sweep waits boundedly before selecting native fallback. It then completes one same-origin GET using the exact inspected href, waits for the response body, reopens the mission and verifies the patient count in that vehicle row has decreased. A vehicle carrying several patients may therefore be released repeatedly (`3 → 2 → 1 → 0`) with a unique confirmation identity for every patient.

A failed request, unchanged patient count, cancellation or failed mission reopen stops the optional path safely. The established MissionChief-native vehicle-window discharge process remains the fallback. The correction adds one user-invoked network-request site and no observer, interval or disabled-state work.
