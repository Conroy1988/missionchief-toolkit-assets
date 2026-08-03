# Issue #683 · Balanced Desktop command deck

Toolkit `v10.5.3` makes the persistent map command bar use the available map height when a centred or horizontally constrained Desktop layout has room below the current controls.

## Desktop geometry

- A Desktop workspace that would otherwise use three shallow group columns now selects a balanced two-by-two deck when at least `280px` of safe map height is available.
- Each group can grow to `320px` wide and command targets grow from `36px` to `44px` high.
- Visibility, Intelligence, Dashboard and Performance occupy two balanced rows; Economy Mode stretches through its available Performance card height.
- Quick Jump becomes a full-deck-width bottom row with `36px` targets.
- The existing map attribution strip, Major Incident Wire reservation, position, nudge and obstruction boundaries remain authoritative.

## Responsive fallbacks

- Genuinely wide maps retain the efficient one-band command layout and inline Quick Jump controls.
- Short maps retain the compact three-column layout or bounded internal scrolling rather than overflowing the map.
- Tablet, iOS, saved group/control ordering, hidden controls, auto-hide and custom themes are unchanged.

## Performance

- The change runs only inside the existing Desktop fit pass.
- It adds no interval, timeout, observer, request, map listener, layer, animation loop or movement-time work.
- Runtime coverage reproduces the supplied `1688×1384` viewport with the command bar centred by a `246px` nudge.
