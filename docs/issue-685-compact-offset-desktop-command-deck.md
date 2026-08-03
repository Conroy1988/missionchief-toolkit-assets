# Issue #685 · Compact offset Desktop command deck

Toolkit `v10.5.4` uses the full safe map corridor when the persistent Desktop command bar has a saved horizontal nudge.

## Desktop geometry

- The fitter no longer subtracts the saved horizontal nudge from the width available to the command allocator.
- The supplied `1690×1276` layout now keeps Visibility, Intelligence, Dashboard, Performance and Quick Jump inside one shallow band.
- Command targets remain at the compact `36px` Desktop height instead of switching to the `44px` two-by-two treatment.
- The effective visual offset is clamped to the remaining horizontal slack, so the complete dock stays within the safe map workspace while reclaiming space on both sides.

## Responsive fallbacks

- Genuinely narrow Desktop maps still use the balanced two-by-two fallback when sufficient safe height exists.
- Short maps retain the bounded internal-scroll fallback.
- Saved nudge data remains unchanged; only the applied offset is clamped for the current map geometry.
- Tablet, iOS, saved group/control ordering, hidden controls, auto-hide and custom themes are unchanged.

## Performance

- The change runs only inside the existing Desktop fit pass.
- It adds no interval, timeout, observer, request, map listener, layer, animation loop or movement-time work.
- The exact screenshot geometry is covered with a `1688×1384` viewport, `1115px` map corridor and `246px` saved nudge.
