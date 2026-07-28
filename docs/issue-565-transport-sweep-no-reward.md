# Issue #565 — Patient Transport Sweep no-reward release path

Toolkit v8.2.3 recognises only the exact visible same-origin `Release patient (No reward)` control whose path matches `/vehicles/{vehicleId}/patient/-1`.

The sweep now treats the opened mission as asynchronous. An empty mission DOM is never considered a completed scan. It waits boundedly for an authoritative `#mission_vehicle_at_mission` row and the delayed optional control before falling back. After each completed request and mission reopen, vehicle absence can confirm the final patient only after the authoritative row surface exists. This prevents the mission window from being closed while rows and controls are still loading.

Verified vehicles, sequential same-vehicle patient reduction, allowance, cancellation, request failure and the native MissionChief discharge fallback remain preserved. No persistent observer, interval, additional request site or Toolkit-managed timer is added.

Toolkit v8.2.3 additionally corrects the eligibility boundary: optional release discovery now uses the synchronous live mission-window candidate collector. The asynchronous HTML recovery collector is reserved for the later native fallback and is never converted into an empty eligibility set.

Toolkit v8.2.4 makes the rendered patient row authoritative for optional-release eligibility. Patient-carrying ILBs and other non-ambulance vehicle types are included when they have FMS 5, patient names and the exact release control; own vehicles remain excluded. Duplicate top-alert clones are resolved back to the vehicle row and the finite row patient count is preferred.
