# Issue #673 · On-demand operational tools

Toolkit `v10.4.0` adds Map Measure and Shareable Incident Card without adding idle map work.

## Map Measure

- Opens only after an explicit Map tools, Command Palette or equivalent action.
- Adds one Leaflet click listener and one owned layer group while active.
- Measures an open distance/route or a closed operational boundary with a maximum of 64 points.
- Shows miles and kilometres for distance, plus square miles, hectares and perimeter for boundaries.
- Tags every temporary Leaflet object as Toolkit-owned so normal mission, vehicle and building refresh logic ignores it.
- Removes the click listener, keyboard listener, layer group, points and HUD on close, Safe Mode, route teardown or runtime replacement.

## Shareable Incident Card

- Generates a 1200 × 675 PNG only after an explicit action for the current or selected mission.
- Reuses the existing mission snapshot, overlay, requirements and unit-commitment state; it performs no extra request or continuous scan.
- Renders the mission identity, location, value, progress, responding units, exposed requirements, patients and prisoners when available.
- Creates the image locally with Canvas and offers Copy Image where the browser permits it plus a Download PNG fallback.
- Releases the generated Blob and preview reference when the modal closes or the Toolkit tears down.

## Performance contract

Neither feature may introduce polling, an interval, a MutationObserver, a network request, an always-present map layer or an idle document listener. Map Measure owns bounded state only while active; Incident Card owns one bounded image only while its preview is open. Both remain subject to the Issue #247 performance budgets and preserve the v10.3.8–v10.3.9 movement governor.

The static and runtime contracts are enforced by:

- `.github/scripts/test_issue673_on_demand_tools.py`
- `.github/scripts/test_issue673_map_measure_runtime.mjs`
