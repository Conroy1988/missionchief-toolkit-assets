# Issue #565 — native Patient Transport Sweep restoration

Toolkit v8.2.6 restores the original MissionChief-native workflow: open each mission, await the alliance-owned FMS 5 vehicle list, open the flashing vehicle, click **Discharge patient**, confirm **Yes, discharge!**, recognise **Patient isn’t transported**, then continue to the next patient and mission.

The v8.2.0 direct `Release patient (No reward)` detour and its request site are removed. Verified personal vehicle IDs, bounded waits, cancellation, progress, duplicate protection and sweep-owned window cleanup remain preserved.
