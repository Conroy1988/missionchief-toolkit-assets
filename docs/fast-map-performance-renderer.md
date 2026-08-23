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

## Base-map readiness

Fast Map does not inherit MissionChief’s Leaflet raster URL. That path can be browser- or provider-specific and can leave MapLibre with a technically mounted but visually empty raster layer. The replacement renderer instead owns the MapLibre-native OpenFreeMap Bright style at `https://tiles.openfreemap.org/styles/bright`.

Activation is positive rather than optimistic. After the base style loads, the Toolkit validates the expected `openmaptiles` vector source, mounts five operational GeoJSON sources and their circle, cluster, symbol and line layers, waits for MapLibre’s next idle render, and only then exposes the `ACTIVE` state. Missing style data, an invalid source/layer topology or the 20-second safety timeout destroys the replacement renderer and restores the exact native map.

## Data path

The bridge reads the existing MissionChief registries without making duplicate game API polling loops:

- personal missions;
- alliance missions;
- personal and alliance buildings, including current native/Toolkit visibility decisions;
- vehicles, including MissionChief's native Show vehicles setting;
- the red destination route attached by MissionChief to each travelling vehicle marker.

Each category is a GeoJSON source with stable string IDs. Buildings and alliance missions cluster at low zoom. Building, mission and vehicle points also retain the active native Leaflet image URL and display size. Shared URLs are deduplicated into MapLibre’s style sprite with six bounded workers; the lightweight coloured point stays beneath the image as a per-item fallback. Once a marker has a decoded picture, a changing or temporarily missing native URL cannot replace it with an unloaded key: Fast Map retains the last ready sprite, decodes the next candidate asynchronously, then promotes it in the same stable-ID source update. Superseded descriptors are pruned after promotion. The mission bridge reads the live registry directly while native Leaflet listeners are detached, so in-place additions and removals do not depend on a stale shared index. Live changes use `GeoJSONSource.updateData()` diffs when supported; a full `setData()` replacement is reserved for initialisation or unusually large source churn. No MapLibre DOM `Marker` object is created per point.

Vehicle routes come from the native `vehicleMarker.polyline` rather than a second routing request. Fast Map copies its current waypoints only while MissionChief keeps that line on the native map, so progress and arrival removal follow the game’s own lifecycle.

Mission, vehicle and building clicks use MissionChief's native lightbox routes. Quick jumps, saved-map views, Command Palette focus, vehicle follow and full-screen resizing target whichever renderer is active. Drawing and Coverage require Leaflet and therefore restore the native map automatically before opening; their settings and objects are not mutated.

## Supply-chain and failure boundary

MapLibre GL JS `5.24.0` is loaded lazily from an exact-version jsDelivr URL. Before execution, the Toolkit requires the exact UTF-8 byte length and SHA-256:

`45a9b07a9189ce56054c620a947ccf41e291e58c95e9b61533b740aaa65ee5cb`

The OpenFreeMap style is declarative map data, not executable Toolkit code. Its expected vector-source topology is checked before operational layers mount. Marker graphics use a dedicated signature-verified boundary for MissionChief PNG/APNG, JPEG, GIF and WebP assets: at most 4 MB and 4,096 pixels at source, then at most 96 pixels in the Fast Map sprite. Cross-origin fetches omit credentials; only MissionChief’s already approved storage host can use the userscript request fallback. A failed candidate retains the prior ready picture when one exists and retries with capped exponential backoff; otherwise its coloured fallback point remains without stopping Fast Map. An unavailable engine request, unexpected HTTP status, byte mismatch, hash mismatch, blocked verified evaluation, unavailable or incomplete base style, unsupported WebGL, startup timeout, invalid adapter, cancelled startup, route change or fatal renderer error uses the same restoration path. Fast Map never writes an enabled preference to saved Toolkit state, so a reload always starts with native MissionChief rendering.

## Player-visible diagnostics

While active, the bounded metrics HUD reports:

- most recent interactive render FPS, or `IDLE` when the map is not rendering;
- total WebGL features and category counts, including vehicle routes;
- data-sync duration;
- optional browser heap reading when exposed;
- renderer warnings;
- the explicit `Leaflet parked · one renderer` state.

The HUD includes zoom and Native-map controls and has dedicated Desktop, Tablet and iOS containment rules. It is anchored at the top centre of the map, with OpenStreetMap/OpenFreeMap attribution directly beneath it, so MissionChief’s bottom command UI cannot hide either surface. The Eco-adjacent toggle exposes OFF, LOAD, START, ACTIVE and ERROR states without exceeding compact labels.

## Permanent proof

`.github/scripts/test_fast_map_contract.py` protects lazy loading, exact pin/integrity checks, OpenFreeMap ownership, native image/sprite and route-line bridges, post-style source/layer mounting, idle-render gating, session-only state, placement beside Economy Mode, top-HUD containment, Leaflet suspension and rollback anchors.

`.github/scripts/test_fast_map_runtime.mjs` mounts the canonical userscript in the Dev Lab and verifies on Desktop, Tablet and iOS that:

- the original map starts connected and Fast Map starts off;
- activation disconnects the exact native node;
- zero Leaflet panes remain connected and exactly one replacement renderer exists;
- the base map is ready before the active phase is exposed;
- OpenStreetMap and OpenFreeMap attribution remains present beneath the top HUD;
- live missions, buildings and vehicles reach the replacement sources with their native image descriptors;
- a loaded vehicle picture remains visible while replacement decoding is delayed, its native URL disappears temporarily and a newer candidate supersedes the queued image;
- only a ready replacement image is promoted, and obsolete descriptors return to the bounded baseline;
- active native vehicle polylines reach the red route source and update in place;
- detached marker movement performs no guarded Leaflet DOM write;
- MissionChief's native Fire checkbox removes and restores the correct Fast Map buildings without reconnecting Leaflet;
- a mission added and removed while native Leaflet listeners are detached appears and disappears on the next Fast Map sync;
- 5,010 live features remain incremental when 1,000 vehicles move together, producing one stable-ID source diff rather than a complete rebuild;
- native mission routes still open;
- stopping returns the exact original node and handlers;
- startup failure restores native rendering;
- cancellation cannot reactivate later from an outstanding async startup.
