#!/usr/bin/env python3
"""Static safety contract for the opt-in Fast Map subsystem."""

from pathlib import Path
import re


SOURCE_PATH = Path("src/MissionChief_Map_Command_Toolkit.user.js")
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")


def require(fragment: str, message: str) -> None:
    if fragment not in SOURCE:
        raise AssertionError(message)


require("// <mcms-fast-map>", "Fast Map subsystem boundary is missing")
require("// </mcms-fast-map>", "Fast Map subsystem boundary is incomplete")
require("// @connect      cdn.jsdelivr.net", "the pinned MapLibre host is not declared")
if re.search(r"^//\s*@require\s+.*maplibre", SOURCE, re.MULTILINE | re.IGNORECASE):
    raise AssertionError("MapLibre must not load eagerly through @require")

for fragment, message in [
    ("engineVersion: '5.24.0'", "MapLibre version is not pinned"),
    ("maplibre-gl@5.24.0/dist/maplibre-gl.js", "MapLibre URL is not exact-version pinned"),
    ("engineSha256: '45a9b07a9189ce56054c620a947ccf41e291e58c95e9b61533b740aaa65ee5cb'", "MapLibre SHA-256 is missing"),
    ("bytes.byteLength !== FAST_MAP.engineBytes", "engine byte length is not verified"),
    ("digest !== FAST_MAP.engineSha256", "engine SHA-256 is not verified before execution"),
    ("The only evaluated bytes are the exact, pinned SHA-256 payload above.", "verified-evaluation boundary is undocumented"),
    ("Function('module', 'exports', 'define'", "the verified UMD evaluation does not shadow CommonJS and AMD loaders"),
    ("library = evaluate(undefined, undefined, undefined);", "the pinned UMD bundle is not forced through its browser export path"),
    ("promoteId: 'ref'", "GeoJSON features do not have stable IDs"),
    ("typeof source.updateData === 'function'", "partial GeoJSON updates are not preferred"),
    ("cluster: true", "large static sources are not clustered"),
]:
    require(fragment, message)

if "new library.Marker" in SOURCE or "new maplibregl.Marker" in SOURCE:
    raise AssertionError("Fast Map must use WebGL source layers, not per-point DOM Marker objects")

default_state = SOURCE[SOURCE.index("function defaultState()") : SOURCE.index("function normaliseLoadedState(")]
if re.search(r"fastMap|fast_map|performanceMap", default_state, re.IGNORECASE):
    raise AssertionError("Fast Map is session-only and must not be persisted in the saved Toolkit state")

performance_group = re.search(
    r"performance:\s*Object\.freeze\(\{[^\n]+controls:\s*Object\.freeze\(\[([^\]]+)\]\)",
    SOURCE,
)
if not performance_group or "'toggle-economy', 'toggle-fast-map'" not in performance_group.group(1):
    raise AssertionError("Fast Map is not placed directly beside Economy Mode")

control_markup_start = SOURCE.index('<div class="mcms-control-group" data-control-group="performance"')
control_markup_end = SOURCE.index("</div>\n            </div>\n            <div class=\"mcms-screen-pins\"", control_markup_start)
control_markup = SOURCE[control_markup_start:control_markup_end]
if control_markup.index('data-action="toggle-economy"') > control_markup.index('data-action="toggle-fast-map"'):
    raise AssertionError("Fast Map must follow Economy Mode in the performance group")
for compact_label in [">Fast</span>", ">OFF</span>"]:
    if compact_label not in control_markup:
        raise AssertionError(f"responsive compact label is missing: {compact_label}")

for fragment, message in [
    ("document.createDocumentFragment()", "native Leaflet container is not disconnected from rendered DOM"),
    ("parking.appendChild(nativeElement)", "native Leaflet container is not parked"),
    ("handler.disable?.()", "native Leaflet handlers are not suspended"),
    ("nativeMap.stop?.()", "native Leaflet animation is not stopped"),
    ("fastMapInstallLeafletRenderGuard(nativeMap)", "detached Leaflet marker DOM writes are not guarded"),
    ("patch('update', original => function", "detached Leaflet marker projection work is not suspended"),
    ("for (const marker of fastMapMissionMarkerLayers(nativeMap))", "Fast Map still depends on a detached-listener mission index"),
    ("fastMapLayerPresent(nativeMap, marker)", "native building filter layer membership is not authoritative in Fast Map"),
    ("connectedLeafletPanes", "single-renderer suspension diagnostic is missing"),
    ("destinationParent.insertBefore(nativeElement, anchor)", "exact native node restoration is missing"),
    ("handler.enable?.()", "native Leaflet handlers are not restored"),
    ("if (fastMapNativeIsSuspended()) return null;", "Toolkit Leaflet work is not blocked while native rendering is suspended"),
    ("disableFastMap({ announce: true, error: message", "fatal renderer errors do not restore native Leaflet"),
    ("disableFastMap({ announce, error: message", "startup failures do not restore native Leaflet"),
    ("Drawing requires the native Leaflet workspace", "Drawing does not safely return to the native map"),
    ("Coverage rings require the native Leaflet workspace", "Coverage does not safely return to the native map"),
]:
    require(fragment, message)

for css_fragment, message in [
    (".mcms-fast-map-btn .mcms-float-label { min-width:0", "Fast Map button lacks text containment"),
    ("max-width:min(720px,calc(100% - 18px))", "Fast Map metrics HUD lacks a viewport width cap"),
    ("text-overflow:ellipsis", "Fast Map text lacks overflow protection"),
    ('html[data-mcms-mobile-active="true"] #${SCRIPT.fastMapHudId}', "Fast Map HUD lacks an iOS layout"),
]:
    require(css_fragment, message)

runtime_test = Path(".github/scripts/test_fast_map_runtime.mjs").read_text(encoding="utf-8")
for device in ["desktop", "tablet", "ios"]:
    if f'await exerciseDevice("{device}"' not in runtime_test:
        raise AssertionError(f"Fast Map runtime proof does not exercise {device}")
for assertion in [
    "connectedLeafletPanes, 0",
    "connectedRenderers, 1",
    "restoration did not return the exact original map node",
    "forced startup failure",
    "startup cancellation",
    "guarded Leaflet marker still wrote",
    "hidden native Fire stations remained in the Fast Map source",
    "live mission added while native events were detached did not reach Fast Map",
    "index < 5000",
    "call.update === 1000",
    "movement storm rebuilt the complete vehicle source",
]:
    if assertion not in runtime_test:
        raise AssertionError(f"Fast Map runtime proof is missing: {assertion}")

print("Fast Map contract pins and verifies MapLibre, remains opt-in/session-only, suspends Leaflet rendering, contains text, and proves exact rollback across all layouts.")
