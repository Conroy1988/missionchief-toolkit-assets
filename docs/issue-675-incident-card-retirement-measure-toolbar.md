# Issue #675 · Incident Card retirement and Measure toolbar

Toolkit `v10.4.1` permanently retires Shareable Incident Card and makes Measure a first-class map-toolbar action.

## Retirement boundary

- No Incident Card renderer, Canvas or Blob runtime remains in the userscript.
- No Mission Operations button, Command Palette entry, contextual mission action, modal action, analytics key or stylesheet remains.
- Current user documentation and the feature index no longer advertise the retired feature.

## Measure toolbar

- The persistent map command bar includes an action labelled **Measure** on Desktop, Tablet and iOS Mobile layouts.
- Clicking the action starts the existing deliberate measurement lifecycle immediately.
- The control reports **ACTIVE** while Measure is open and **READY** after teardown.
- Existing saved layout preferences automatically gain the new action while retaining their prior order, visibility and device-specific settings.

## Units and performance

- Distance and perimeter use kilometres; area uses square kilometres.
- Measure retains its 64-point cap and route/boundary modes.
- No new interval, observer, request, background cadence or idle listener is introduced.
- The Leaflet click handler, renderer, group and points continue to exist only while Measure is active and are destroyed on close, Safe Mode, route teardown or runtime replacement.
