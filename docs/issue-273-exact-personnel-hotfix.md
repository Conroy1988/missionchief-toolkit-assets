# Issue 273 — exact personnel reconciliation hotfix

Toolkit v4.20.17 resolves the exact assigned personnel count for each visible MissionChief vehicle by vehicle ID.

- Native exact DOM crew evidence remains first priority.
- The existing shared MissionChief `/api/vehicles` cache supplies `assigned_personnel_count` when the dispatch table only exposes a type range.
- The Matrix reuses the Toolkit's existing cache, refresh throttling and error backoff rather than creating a second request path.
- Exact capacity is retained through Selected, Responding and On Site deduplication.
- Level 2 Public Order Officer and generic Police Officers therefore clear only when their real personnel total meets demand.
- Vehicles that cannot be read retain the reviewed minimum/maximum range rather than being guessed.
