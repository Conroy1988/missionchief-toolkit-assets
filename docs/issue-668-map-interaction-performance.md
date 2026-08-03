# Issue #668 — Map interaction performance contract

Toolkit `v10.3.8` makes the movement governor standard for every active map rather than limiting it to Economy Mode. Full feature state remains enabled; work that competes with Leaflet's live transform is delayed until the gesture has settled.

## Runtime contract

- `movestart` and `zoomstart` cancel pending Toolkit-owned map render timers and mark the root as moving.
- Mission, vehicle and building layer changes accumulate in a bounded dirty-scope set. Registry invalidation, marker classification, labels, Coverage Rings, mission snapshots and operational refreshes do not run during movement.
- `moveend`, `zoomend` and non-gesture `viewreset` events share the existing consolidated refresh timer. Repeated end events produce one refresh after a 90 ms settle window.
- Tile-pane-only child-list mutations are ignored. Other map mutations mark one deferred DOM refresh without calling `ensureUi()` or repeatedly reconciling the command shell.
- The settled pass invalidates each dirty registry at most once, restores full visual effects and schedules only the enabled feature work.

## Rendering contract

Coverage Rings retain the 200-visible-building limit, radius, colour and opacity, but every ring uses one shared Leaflet Canvas renderer. The renderer is Toolkit-owned, excluded from native layer-churn handling and released during runtime teardown.

While the map is moving, Toolkit-owned marker and interface animations are paused, tile filters and Toolkit backdrop blur are suspended, and `will-change` hints are neutralised. All theme, skin and animation rules resume automatically after the settled pass.

## Compatibility and regression boundary

- No feature, setting, layout, theme or map skin is removed or changed persistently.
- Desktop, Tablet and iOS use the same movement governor.
- No request, observer, listener, interval, animation-frame loop or recurring timer is added.
- The Issue #661 memory lifecycle remains covered by its zero-retention regression.
- The Issue #668 runtime regression injects 1,000 layer add/remove changes during movement and requires zero heavy work before exactly one settled refresh.
