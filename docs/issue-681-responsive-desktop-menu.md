# Issue #681 · Responsive Desktop command surface

Toolkit `v10.5.2` makes the unified menu use mid-sized Desktop windows efficiently without changing Tablet or iOS behaviour.

## Desktop geometry

- The saved default width remains `720px` for compatibility.
- Between `1200px` and `2239px`, the untouched default becomes fluid: it grows with the viewport, reaches at most `1040px`, and returns smoothly to the established wide-Desktop size.
- At `1360px` or wider and `900px` or taller, the untouched default height is capped at `760px`.
- Custom widths, custom heights and saved positions remain authoritative.
- Existing map-aware clamping moves a newly widened panel back inside the visible workspace when required.

## Settings packing

- Settings uses up to three balanced, content-sized columns on suitable Desktop viewports.
- Each command card stays intact inside one column.
- Unequal cards no longer create empty grid rows beside taller neighbours.
- Shorter windows retain the established proportional two-column layout and internal scrolling.

## Compatibility and performance

- Desktop section labels, descriptions, search, active state, header actions and footer remain intact.
- Tablet and iOS selectors are explicitly excluded from the adaptive Desktop rules.
- The change reuses the existing panel resize and viewport-clamping lifecycle.
- It adds no interval, timer, observer, request, map listener, layer, animation loop or idle map work.
