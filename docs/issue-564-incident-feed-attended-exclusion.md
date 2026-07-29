# Issue #564 — unattended Incident Command Wire

Toolkit v8.3.1 keeps the Incident Command Wire focused on major missions that still need the signed-in player's initial attendance.

A mission is excluded only when the existing personal vehicle commitment index confirms at least one of the player's own units at MissionChief FMS 4 for that mission. Selected units, FMS 3 responding units and alliance-member units do not trigger exclusion.

The normal feed predicate, score ordering and maximum-item bound remain authoritative. When the final personal on-scene unit leaves, the mission can re-enter once if it still qualifies. Current-card removal retains Pause/Play and expanded state, advances at the same queue index, wraps safely and updates the compact reel, counter and expanded queue together.

The implementation reuses existing vehicle radio events, API reconciliation, mission snapshot invalidation and the single coalesced snapshot timer. It introduces no request, observer, interval, broad scan or additional Toolkit-managed timer.

The v8.3.0 tree was the validated internal candidate. v8.3.1 is the production publication through the corrected exact-run artifact resolver.
