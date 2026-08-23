# Native Building Quick Filters

The Buildings control opens MissionChief's complete active UK building catalogue in a compact, scrollable popup. The first three positions remain the most important everyday services:

- Ambulance Stations
- Police Stations
- Fire Stations

Every other building follows in this fixed UK gameplay popularity order:

1. Hospitals
2. Small Ambulance Stations
3. Small Fire Stations
4. Small Police Stations
5. Medical Helicopter Stations
6. Police Aviation
7. Dispatch Centres
8. Fire Academies
9. Medical Academies
10. Police Training Centres
11. Search and Rescue HQs
12. Coastguard Rescue Stations
13. Lifeboat Stations
14. HART Bases
15. Home Response Locations
16. GP Surgeries
17. Urgent Treatment Centres
18. Mountain Rescue Stations
19. Coastal Rescue Heliports
20. Search and Rescue Colleges
21. Recovery Centres
22. Bomb Disposal HQs
23. Large Police Depots
24. Custody Suites
25. Prisons
26. Staging Areas
27. Building Complexes

This is a deliberate product order based on common UK gameplay use, not per-player tracking or claimed live usage telemetry. Large and Small Building Complexes share MissionChief's single native Building Complexes control, so 30 rows cover all 31 active UK building type IDs.

Press `4`, tap **Buildings**, use the configured Quick Wheel action, or choose **Open Building Filters** in the command palette. `Shift+4` and right-clicking the dock control also open the same popup.

Each row reads the current checked state from MissionChief's own `#map_filters` list and activates that native checkbox. MissionChief therefore remains responsible for layer visibility and `/map_filters` persistence. Multiple building types can be changed without closing the popup. A row marked **Unavailable** means the current MissionChief map did not expose its native control; the Toolkit does not synthesize a replacement layer.

## Performance and compatibility

The Toolkit no longer fetches `/buildings/new`, scans building markers, maintains an ownership/type selection, hides layers with CSS, or runs a building-visibility timer for this control. Economy Mode also leaves building layers to MissionChief's filter service.

Older `buildingVisibility` data is accepted during state import so existing backups remain valid, but it is inert and is not written into new map profiles. The separate alliance-building native-filter leak safeguard remains in place.

Native controls are scanned once per popup render. Exact labels, current MissionChief filter tokens, live I18n translations and UK/US spelling variants are supported without allowing a small-station control to be mistaken for its full-size counterpart.

The popup is viewport-clamped, scroll-safe, keyboard navigable, and uses sticky section labels, wrapping names and state badges at desktop, tablet, and narrow iPhone widths.

## Validation

Run the focused local lane:

```bash
./toolkit check --feature building-visibility
```

The static, isolated runtime, and Dev Lab fixtures cover all 31 type IDs, the exact popularity order, grouped complexes, main/small-station collision protection, translated native labels, native checkbox events, dock and panel interaction, multi-selection, click-away handling, stale legacy-state isolation, and responsive text containment.
