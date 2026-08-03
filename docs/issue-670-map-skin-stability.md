# Issue #670 — Stable map-skin movement contract

Toolkit `v10.3.9` keeps the selected map skin visually stable throughout every pan, drag and zoom while retaining the `v10.3.8` movement governor.

## Rendering contract

- At movement start, the exact active skin filter moves from the individual Leaflet tile images to the shared `.leaflet-tile-pane` composite in the same style recalculation.
- Road Priority uses its corresponding movement-time composite filter for every map skin.
- Individual tile filters are neutralised only after the shared pane has inherited the same colour formula, avoiding both per-tile compositing and a bright default-tile frame.
- Marker and interface animations, transitions, backdrop blur and `will-change` hints remain paused during the gesture.
- The normal per-tile skin rules resume after the existing 90 ms settled refresh.

## Compatibility and performance boundary

- All eleven map skins and all eleven Road Priority variants must have byte-equivalent normal and movement filter formulas.
- The movement governor, dirty-scope batching, tile-only mutation suppression, Canvas Coverage Rings and single settled refresh remain unchanged.
- No setting, network path, timer, listener, observer, animation-frame loop or polling cadence is added.
- Desktop, Tablet and iOS use the same style-only handoff.
