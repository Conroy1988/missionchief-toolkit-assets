# Native Building Quick Filters

The Buildings control opens a small popup for the three station filters used most often:

- Ambulance Stations
- Fire Stations
- Police Stations

Press `4`, tap **Buildings**, use the configured Quick Wheel action, or choose **Open Station Filters** in the command palette. `Shift+4` and right-clicking the dock control also open the same popup.

Each row reads the current checked state from MissionChief's own `#map_filters` list and activates that native checkbox. MissionChief therefore remains responsible for layer visibility and `/map_filters` persistence. Multiple station types can be changed without closing the popup. For every other building type, use MissionChief's full Filters menu.

## Performance and compatibility

The Toolkit no longer fetches `/buildings/new`, scans building markers, maintains an ownership/type selection, hides layers with CSS, or runs a building-visibility timer for this control. Economy Mode also leaves building layers to MissionChief's filter service.

Older `buildingVisibility` data is accepted during state import so existing backups remain valid, but it is inert and is not written into new map profiles. The separate alliance-building native-filter leak safeguard remains in place.

The popup is viewport-clamped, scroll-safe, keyboard navigable, and uses wrapping labels and state badges at desktop, tablet, and narrow iPhone widths.

## Validation

Run the focused local lane:

```bash
./toolkit check --feature building-visibility
```

The static, isolated runtime, and Dev Lab fixtures cover exact three-filter discovery, native checkbox events, dock and panel interaction, multi-selection, click-away handling, stale legacy-state isolation, and responsive text containment.
