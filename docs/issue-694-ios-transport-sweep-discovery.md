# Issue #694 — iOS Patient Transport Sweep discovery

Toolkit v10.6.1 no longer requires MissionChief's Leaflet `mission_markers` registry to be populated before Patient Transport Sweep can find work on iPhone or iOS Safari.

Scan and Start Sweep first use the normal live marker path. When that path produces no eligible missions or exposes zero markers, the user's manual action refreshes MissionChief's current mission payload once and builds a bounded fallback from the captured current mission IDs and mission sidebar. A fallback record is eligible only when its captured data positively proves alliance ownership.

Personal missions, unknown ownership, prisoners, non-transport requirements and stale overlay records fail closed. The existing verified personal-vehicle list, FMS 5 patient-vehicle checks, native Cancel Transport/Discharge patient controls, sequential processing limits, persistent completion report and exact-once Discord delivery remain authoritative.

The repair adds no interval, MutationObserver, recurring scan, background request or idle map work.
