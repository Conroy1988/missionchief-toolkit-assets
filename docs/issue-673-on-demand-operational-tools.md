# Issue #673 · On-demand Map Measure

Toolkit `v10.4.0` added Map Measure without idle map work. Version `v10.4.1` makes it kilometre-first and exposes it directly on the persistent map toolbar.

## Map Measure

- Opens only after an explicit Measure toolbar, Map tools, Command Palette or equivalent action.
- Adds one Leaflet click listener and one owned layer group while active; keyboard handling reuses the Toolkit's existing global owner.
- Measures an open distance/route or a closed operational boundary with a maximum of 64 points.
- Shows route distance and boundary perimeter in kilometres, plus boundary area in square kilometres.
- Tags every temporary Leaflet object as Toolkit-owned so normal mission, vehicle and building refresh logic ignores it.
- Removes the click listener, element-owned handlers, Canvas renderer, layer group, points and HUD on close, Safe Mode, route teardown or runtime replacement.

## Performance contract

Measure may not introduce polling, an interval, a MutationObserver, a network request, an always-present map layer or an idle document listener. It owns bounded state only while active, remains subject to the Issue #247 performance budgets and preserves the v10.3.8–v10.4.0 movement governor.

The static and runtime contracts are enforced by:

- `.github/scripts/test_issue673_on_demand_tools.py`
- `.github/scripts/test_issue673_map_measure_runtime.mjs`
