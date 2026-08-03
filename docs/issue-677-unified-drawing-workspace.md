# Issue #677 · Unified on-demand Drawing workspace

Toolkit `v10.5.0` evolves the existing kilometre-first Measure tool into one complete **Drawing** workspace without adding idle map work.

## One workspace

- The persistent Desktop, Tablet and iOS toolbar action, Map tools action and Command Palette entry are labelled **Drawing**.
- The historical `open-map-measure` control ID and Map Measure runtime names remain internal compatibility details so existing saved layouts and regression ownership are not broken.
- Distance and perimeter remain in kilometres; area remains in square kilometres.
- Line, arrow, freehand, circle, rectangle, polygon zone, text and marker tools live inside the same panel.
- Six colours, solid/dashed lines and thin/normal/bold weights apply to the next draft without rewriting existing objects.
- Undo first removes the current draft point, then the most recently completed object. Finish commits routes, areas and zones. Clear All removes the complete session drawing.

## Bounded lifecycle

- Drawings are session-local and never uploaded or persisted.
- The workspace permits at most 48 completed objects, 64 points per click-built route or zone and 160 six-pixel-thresholded samples per freehand stroke.
- Committed objects and the current draft use separate Toolkit-owned Leaflet groups. Freehand movement updates only the draft group.
- Map dragging is disabled only while Freehand is selected, then restored to its prior state when another tool is chosen or Drawing closes.
- All click, pointer/touch, layer-group, renderer, HUD and draft state is removed on close, Safe Mode, route teardown or runtime replacement.

## Performance contract

Drawing adds no interval, timeout, animation-frame cadence, observer, request, managed listener or permanent layer. Its Leaflet handlers exist only while the workspace is open. The v10.3.8 movement governor, unchanged-render suppression and long-session zero-retention gates remain mandatory.
