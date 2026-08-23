# Fast Map performance renderer

Fast Map is an opt-in, session-only MapLibre renderer for the canonical MissionChief map. Its control sits directly beside Economy Mode and always starts **OFF**. Normal Toolkit startup performs no MapLibre request, parsing, worker creation, polling or WebGL allocation.

## Renderer ownership

Fast Map is a replacement renderer, not an overlay:

1. capture the exact MissionChief Leaflet object, DOM node, centre, zoom, enabled handlers and Toolkit-control position;
2. stop Leaflet animation and disable its interaction handlers;
3. move the Toolkit controls into the replacement shell so the off switch remains available;
4. move the original `#map` node into a `DocumentFragment`, outside the rendered document;
5. guard Leaflet marker projection, zoom-animation, position and opacity DOM writes while the node is parked;
6. mount one MapLibre canvas in the canonical `#map` slot;
7. retain MissionChief's marker registries only as the live data feed.

There are no connected Leaflet panes beneath Fast Map. MissionChief networking and marker coordinates continue because those are the authoritative live-game data required by the replacement renderer.

When Fast Map stops, its current centre and zoom are transferred back, the WebGL renderer and sync timer are destroyed, the exact original node is reinserted at its original DOM anchor, the exact control node is returned, guarded marker writes are refreshed in bounded batches, previously enabled handlers are re-enabled, and Leaflet receives a non-animated size refresh.

## Data path

The bridge reads the existing MissionChief registries without making duplicate game API polling loops:

- personal missions;
- alliance missions;
- personal and alliance buildings, including current native/Toolkit visibility decisions;
- vehicles, including MissionChief's native Show vehicles setting.

Each category is a GeoJSON source with stable string IDs. Buildings and alliance missions cluster at low zoom. The mission bridge reads the live registry directly while native Leaflet listeners are detached, so in-place additions and removals do not depend on a stale shared index. Live changes use `GeoJSONSource.updateData()` diffs when supported; a full `setData()` replacement is reserved for initialisation or unusually large source churn. No MapLibre DOM `Marker` object is created per point.

Mission, vehicle and building clicks use MissionChief's native lightbox routes. Quick jumps, saved-map views, Command Palette focus, vehicle follow and full-screen resizing target whichever renderer is active. Drawing and Coverage require Leaflet and therefore restore the native map automatically before opening; their settings and objects are not mutated.

## Supply-chain and failure boundary

MapLibre GL JS `5.24.0` is loaded lazily from an exact-version jsDelivr URL. Before execution, the Toolkit requires the exact UTF-8 byte length and SHA-256:

`45a9b07a9189ce56054c620a947ccf41e291e58c95e9b61533b740aaa65ee5cb`

An unavailable userscript request, unexpected HTTP status, byte mismatch, hash mismatch, blocked verified evaluation, unsupported WebGL, startup timeout, invalid adapter, cancelled startup, route change or fatal renderer error uses the same restoration path. Fast Map never writes an enabled preference to saved Toolkit state, so a reload always starts with native MissionChief rendering.

## Player-visible diagnostics

While active, the bounded metrics HUD reports:

- most recent interactive render FPS, or `IDLE` when the map is not rendering;
- total WebGL points and category counts;
- data-sync duration;
- optional browser heap reading when exposed;
- renderer warnings;
- the explicit `Leaflet parked · one renderer` state.

The HUD includes zoom and Native-map controls and has dedicated Desktop, Tablet and iOS containment rules. The Eco-adjacent toggle exposes OFF, LOAD, START, ACTIVE and ERROR states without exceeding compact labels.

## Permanent proof

`.github/scripts/test_fast_map_contract.py` protects lazy loading, exact pin/integrity checks, session-only state, source-layer rendering, placement beside Economy Mode, text containment, Leaflet suspension and rollback anchors.

`.github/scripts/test_fast_map_runtime.mjs` mounts the canonical userscript in the Dev Lab and verifies on Desktop, Tablet and iOS that:

- the original map starts connected and Fast Map starts off;
- activation disconnects the exact native node;
- zero Leaflet panes remain connected and exactly one replacement renderer exists;
- live missions, buildings and vehicles reach the replacement sources;
- detached marker movement performs no guarded Leaflet DOM write;
- MissionChief's native Fire checkbox removes and restores the correct Fast Map buildings without reconnecting Leaflet;
- a mission added and removed while native Leaflet listeners are detached appears and disappears on the next Fast Map sync;
- 5,009 live points remain incremental when 1,000 vehicles move together, producing one stable-ID source diff rather than a complete rebuild;
- native mission routes still open;
- stopping returns the exact original node and handlers;
- startup failure restores native rendering;
- cancellation cannot reactivate later from an outstanding async startup.
