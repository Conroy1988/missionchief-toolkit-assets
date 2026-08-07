# Issue #701 — iOS native patient-state parity

Toolkit v10.6.4 repairs the physical-iPhone failure where Patient Transport Sweep checked all 80 current patient missions but produced an empty queue while the same desktop scan found 13 transport missions.

The iOS path now reads MissionChief's live `patient_timers` registry. Each native patient state is tied to its mission ID and missing-requirement text, then accepted only when the refreshed mission list independently proves that mission is alliance-owned. A mission is marked fully evaluated only when the native registry covers its current patient count; incomplete or unavailable native state continues through the bounded mission-page fallback.

The repair does not introduce polling, observers, background scanning or a new network primitive. The sweep remains manual-start-only, excludes personal and unknown missions, excludes prisoner transports, excludes verified personal vehicle IDs, and performs no release unless MissionChief exposes its native visible **Discharge patient** or **Cancel Transport** control.

The runtime regression models 80 current iOS patient missions with 13 native transport requirements, starts with no Leaflet markers, verifies no desktop-shaped mission page is required, and proves the resulting mission IDs exactly match desktop discovery.
