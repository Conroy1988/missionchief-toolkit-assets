(function () {
  "use strict";

  const params = new URLSearchParams(location.search);
  const fixture = Object.freeze({
    device: ["desktop", "tablet", "ios"].includes(params.get("device")) ? params.get("device") : "desktop",
    tab: params.get("tab") || "dispatch",
    focus: params.get("focus") || "",
    theme: params.get("theme") || "mapCommand",
  });
  const errors = [];
  let healthTimer = 0;
  let healthRunning = false;
  let healthMonitoringEnabled = true;

  function recordError(error) {
    const message = String(error?.stack || error?.message || error || "Unknown Dev Lab error");
    if (!errors.includes(message)) errors.push(message);
  }

  function viewport() {
    if (fixture.device === "ios") return { width: 390, height: 844, coarse: true };
    if (fixture.device === "tablet") return { width: 1024, height: 768, coarse: true };
    return { width: 1440, height: 900, coarse: false };
  }

  function createMapStub() {
    const listeners = new Map();
    const layers = {};
    const container = document.getElementById("map");
    let centre = { lat: 55.9533, lng: -3.1883 };
    let zoom = 12;
    const bounds = {
      contains: () => true,
      getNorth: () => 56.2,
      getSouth: () => 55.7,
      getEast: () => -2.8,
      getWest: () => -3.6,
    };
    const makeHandler = name => ({
      name,
      _enabled: true,
      enabled() { return this._enabled; },
      enable() { this._enabled = true; return this; },
      disable() { this._enabled = false; return this; },
    });
    const dragging = makeHandler("dragging");
    const scrollWheelZoom = makeHandler("scrollWheelZoom");
    const touchZoom = makeHandler("touchZoom");
    const map = {
      _leaflet_id: 1,
      _layers: layers,
      _handlers: [dragging, scrollWheelZoom, touchZoom],
      dragging,
      scrollWheelZoom,
      touchZoom,
      stopCalls: 0,
      addLayer(layer) {
        layers[layer?._leaflet_id || Object.keys(layers).length + 2] = layer;
        if (layer && typeof layer === "object") {
          layer._map = this;
          layer._mountIcon?.();
        }
        this.fire("layeradd", { layer });
        return this;
      },
      removeLayer(layer) {
        for (const [key, value] of Object.entries(layers)) if (value === layer) delete layers[key];
        if (layer?._map === this) layer._map = null;
        layer?._icon?.remove?.();
        this.fire("layerremove", { layer });
        return this;
      },
      hasLayer(layer) { return Object.values(layers).includes(layer); },
      eachLayer(callback) { Object.values(layers).forEach(callback); },
      getBounds: () => bounds,
      getCenter: () => ({ ...centre }),
      getZoom: () => zoom,
      getContainer: () => container,
      latLngToContainerPoint: () => ({ x: viewport().width / 2, y: viewport().height / 2 }),
      containerPointToLatLng: () => ({ lat: 55.9533, lng: -3.1883 }),
      invalidateSize() { return this; },
      stop() { this.stopCalls += 1; return this; },
      panTo(latlng) { return this.setView(latlng, zoom); },
      setView(latlng, nextZoom = zoom) {
        const value = Array.isArray(latlng) ? { lat: latlng[0], lng: latlng[1] } : latlng;
        if (Number.isFinite(Number(value?.lat)) && Number.isFinite(Number(value?.lng))) centre = { lat: Number(value.lat), lng: Number(value.lng) };
        if (Number.isFinite(Number(nextZoom))) zoom = Number(nextZoom);
        this.fire("moveend", { center: centre, zoom });
        return this;
      },
      fitBounds() { return this; },
      on(types, handler) {
        String(types).split(/\s+/u).filter(Boolean).forEach(type => {
          const handlers = listeners.get(type) || new Set();
          handlers.add(handler);
          listeners.set(type, handlers);
        });
        return this;
      },
      once(type, handler) {
        const wrapped = event => { this.off(type, wrapped); handler(event); };
        return this.on(type, wrapped);
      },
      off(types, handler) {
        if (!types) { listeners.clear(); return this; }
        String(types).split(/\s+/u).filter(Boolean).forEach(type => {
          if (!handler) listeners.delete(type);
          else listeners.get(type)?.delete(handler);
        });
        return this;
      },
      fire(type, payload = {}) {
        for (const handler of Array.from(listeners.get(type) || [])) handler({ type, target: this, ...payload });
        return this;
      },
    };
    return map;
  }

  function createLeafletStub(map) {
    let id = 10;
    class Marker {
      constructor(latlng = { lat: 55.9533, lng: -3.1883 }, options = {}) {
        this._leaflet_id = id++;
        this.options = { ...options };
        this._latlng = { lat: Number(latlng?.lat ?? latlng?.[0] ?? 55.9533), lng: Number(latlng?.lng ?? latlng?.[1] ?? -3.1883) };
        this._events = new Map();
        this._map = null;
        this._icon = null;
        this._renderWrites = 0;
      }
      _mountIcon() {
        const iconUrl = this.options?.icon?.options?.iconUrl || "";
        const expectedTag = iconUrl ? "IMG" : "DIV";
        if (!this._icon || this._icon.tagName !== expectedTag) {
          this._icon?.remove?.();
          this._icon = document.createElement(iconUrl ? "img" : "div");
          this._icon.className = "leaflet-marker-icon";
          this._icon.dataset.fixtureMarkerId = String(this._leaflet_id);
        }
        if (iconUrl) this._icon.src = iconUrl;
        const pane = map.getContainer()?.querySelector?.("[data-fixture-markers]");
        if (pane && this._icon.parentNode !== pane) pane.appendChild(this._icon);
        this.update();
      }
      _setPos() {
        this._renderWrites += 1;
        if (this._icon) this._icon.style.transform = `translate3d(${this._latlng.lng}px,${this._latlng.lat}px,0)`;
      }
      _updateOpacity() {
        this._renderWrites += 1;
        if (this._icon) this._icon.style.opacity = String(this.options.opacity ?? 1);
      }
      update() { this._setPos(); return this; }
      addTo(target = map) { target.addLayer(this); return this; }
      remove() { (this._map || map).removeLayer(this); return this; }
      bindTooltip() { return this; }
      bindPopup() { return this; }
      openPopup() { this.fire("popupopen"); return this; }
      setIcon(icon) { this.options.icon = icon; if (this._map) this._mountIcon(); return this; }
      setLatLng(latlng) {
        this._latlng = { lat: Number(latlng?.lat ?? latlng?.[0]), lng: Number(latlng?.lng ?? latlng?.[1]) };
        this.update();
        this.fire("move", { latlng: this.getLatLng() });
        return this;
      }
      setOpacity(value) { this.options.opacity = Number(value); this._updateOpacity(); return this; }
      setStyle() { return this; }
      getLatLng() { return { ...this._latlng }; }
      on(type, handler) { const handlers = this._events.get(type) || new Set(); handlers.add(handler); this._events.set(type, handlers); return this; }
      off(type, handler) { if (!handler) this._events.delete(type); else this._events.get(type)?.delete(handler); return this; }
      fire(type, payload = {}) { for (const handler of Array.from(this._events.get(type) || [])) handler({ type, target: this, ...payload }); return this; }
    }
    const layer = extra => Object.assign(new Marker(), extra);
    const group = () => {
      const children = new Set();
      const value = layer({
        _icon: null,
        _mountIcon() {},
        update() { return this; },
        addLayer(child) { children.add(child); if (this._map) this._map.addLayer(child); return this; },
        removeLayer(child) { children.delete(child); if (child?._map) child._map.removeLayer(child); return this; },
        hasLayer(child) { return children.has(child); },
        clearLayers() { for (const child of Array.from(children)) this.removeLayer(child); return this; },
        eachLayer(callback) { children.forEach(callback); },
      });
      return value;
    };
    return {
      Marker,
      map: () => map,
      stamp(value) { if (!value._leaflet_id) value._leaflet_id = id++; return value._leaflet_id; },
      layerGroup: group,
      featureGroup: group,
      marker: (latlng, options) => new Marker(latlng, options),
      circle: (latlng, options) => new Marker(latlng, options),
      circleMarker: (latlng, options) => new Marker(latlng, options),
      polyline: () => layer({ getBounds: () => map.getBounds() }),
      icon: options => ({ options: { ...options } }),
      divIcon: options => ({ options }),
      latLng: (lat, lng) => ({ lat: Number(lat), lng: Number(lng) }),
      latLngBounds: () => map.getBounds(),
      point: (x, y) => ({ x, y }),
    };
  }

  function installFastMapTestEngine() {
    const state = {
      createCount: 0,
      destroyCount: 0,
      failNext: false,
      readyDelayMs: 0,
      adapters: [],
      lastConfig: null,
    };
    window.__MCMS_FAST_MAP_TEST_ENGINE_STATE__ = state;
    window.__MCMS_FAST_MAP_TEST_ENGINE__ = {
      create(config) {
        state.createCount += 1;
        state.lastConfig = config;
        const shouldFail = state.failNext;
        state.failNext = false;
        const canvas = document.createElement("canvas");
        canvas.className = "maplibregl-canvas";
        canvas.setAttribute("aria-label", "Dev Lab Fast Map renderer");
        config.container.appendChild(canvas);
        const pointLayer = document.createElement("div");
        pointLayer.className = "mcms-fast-map-fixture-points";
        config.container.appendChild(pointLayer);
        const sources = new Map(Object.entries(config.collections || {}).map(([id, collection]) => [id, new Map((collection.features || []).map(feature => [String(feature.properties?.ref || feature.id), feature]))]));
        const images = new Map(config.images || []);
        let view = { ...config.view };
        let destroyed = false;

        const renderPoints = () => {
          pointLayer.replaceChildren();
          const features = Array.from(sources.values()).flatMap(source => Array.from(source.values())).filter(feature => feature.geometry?.type === "Point").slice(0, 80);
          features.forEach((feature, index) => {
            const point = document.createElement("button");
            point.type = "button";
            point.className = `mcms-fast-map-fixture-point mcms-fast-map-fixture-${feature.properties?.kind || "point"}`;
            point.style.left = `${10 + ((index * 37) % 80)}%`;
            point.style.top = `${12 + ((index * 23) % 72)}%`;
            point.style.setProperty("--mcms-fixture-colour", feature.properties?.colour || "#6ed7ff");
            point.title = feature.properties?.title || feature.properties?.ref || "Fast Map point";
            point.addEventListener("click", () => config.onFeature?.(feature.properties?.ref));
            pointLayer.appendChild(point);
          });
        };
        renderPoints();

        const adapter = {
          kind: "fixture",
          updateCalls: [],
          ready: new Promise((resolve, reject) => window.setTimeout(() => shouldFail ? reject(new Error("Dev Lab forced Fast Map startup failure")) : resolve(true), state.readyDelayMs)),
          updateSource(sourceId, collection, diff) {
            this.updateCalls.push({
              sourceId,
              mode: diff ? "diff" : "replace",
              remove: diff?.remove?.length || 0,
              add: diff?.add?.length || 0,
              update: diff?.update?.length || 0,
            });
            const source = sources.get(sourceId) || new Map();
            if (!diff) {
              sources.set(sourceId, new Map((collection.features || []).map(feature => [String(feature.properties?.ref || feature.id), feature])));
            } else {
              for (const id of diff.remove || []) source.delete(String(id));
              for (const feature of diff.add || []) source.set(String(feature.properties?.ref || feature.id), feature);
              for (const update of diff.update || []) {
                const current = source.get(String(update.id));
                if (!current) continue;
                const properties = update.removeAllProperties ? {} : { ...(current.properties || {}) };
                for (const item of update.addOrUpdateProperties || []) properties[item.key] = item.value;
                source.set(String(update.id), { ...current, geometry: update.newGeometry || current.geometry, properties });
              }
              sources.set(sourceId, source);
            }
            renderPoints();
            return true;
          },
          updateImages(descriptors) { for (const [id, descriptor] of new Map(descriptors || [])) images.set(id, descriptor); return true; },
          setPresentation(presentation) { this.presentation = { ...presentation }; return true; },
          getView() { return { ...view }; },
          setView(lat, lng, zoom) { view = { lat: Number(lat), lng: Number(lng), zoom: Number(zoom) }; config.onFps?.(60); return true; },
          resize() { this.resizeCount = (this.resizeCount || 0) + 1; return true; },
          isBaseMapReady() { return !destroyed; },
          getMarkerImageStats() { return { available: images.size, loaded: images.size, failed: 0, pending: 0 }; },
          getRendererCount() { return destroyed ? 0 : config.container.querySelectorAll("canvas").length; },
          triggerFeature(ref) { config.onFeature?.(ref); },
          sourceFeatures(sourceId) { return Array.from(sources.get(sourceId)?.values?.() || []); },
          imageDescriptor(imageId) { return images.get(imageId) || null; },
          destroy() {
            if (destroyed) return;
            destroyed = true;
            state.destroyCount += 1;
            canvas.remove();
            pointLayer.remove();
          },
        };
        state.adapters.push(adapter);
        return adapter;
      },
    };
  }

  function jsonResponse(value, status = 200) {
    return Promise.resolve(new Response(JSON.stringify(value), {
      status,
      headers: { "Content-Type": "application/json" },
    }));
  }

  function fixtureFetch(input) {
    const url = new URL(typeof input === "string" ? input : input?.url || String(input), location.origin);
    if (url.pathname === "/buildings/new") {
      return Promise.resolve(new Response('<select id="building_leitstelle_building_id" name="building[leitstelle_building_id]"></select><select id="building_building_type" name="building[building_type]"><option value="2">Fire Station</option><option value="6">Police Station</option><option value="22">Ambulance Station</option></select>', { status: 200, headers: { "Content-Type": "text/html" } }));
    }
    if (/\/api\/vehicles|\/vehicles\.json/iu.test(url.pathname)) return jsonResponse(window.vehicles || []);
    if (/\/api\/buildings|\/buildings\.json/iu.test(url.pathname)) return jsonResponse(window.buildings || []);
    if (/toolkit-update-manifest|update-manifest\.json/iu.test(url.pathname)) {
      return jsonResponse({ schemaVersion: 1, version: "10.16.7", downloadUrl: "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/", sha256: "0".repeat(64) });
    }
    return Promise.resolve(new Response("", { status: 200, headers: { "Content-Type": "text/html" } }));
  }

  function setReadonly(target, key, value) {
    try { Object.defineProperty(target, key, { configurable: true, value }); } catch (error) {}
  }

  function installEnvironment() {
    const view = viewport();
    document.documentElement.dataset.mcmsDeviceFixture = fixture.device;
    history.replaceState(null, "", `/?device=${fixture.device}&tab=${fixture.tab}`);
    setReadonly(window, "innerWidth", view.width);
    setReadonly(window, "innerHeight", view.height);
    setReadonly(document, "hidden", false);
    setReadonly(document, "visibilityState", "visible");
    setReadonly(navigator, "maxTouchPoints", view.coarse ? 5 : 0);
    setReadonly(navigator, "globalPrivacyControl", true);
    setReadonly(navigator, "doNotTrack", "1");

    window.unsafeWindow = window;
    window.user_id = 1988;
    window.I18n = { locale: "en_GB", t: key => key };
    window.buildings = [];
    window.vehicles = [];
    window.missions = [];
    window.fetch = fixtureFetch;
    window.alert = () => undefined;
    window.confirm = () => false;
    window.prompt = () => null;
    window.open = () => null;
    window.lightboxOpen = path => { window.__MCMS_LAST_LIGHTBOX__ = String(path || ""); };
    window.scrollTo = () => undefined;
    window.matchMedia = query => ({
      matches: /coarse/iu.test(query) ? view.coarse : /max-width\s*:\s*(?:720|760|820|900|1100)px/iu.test(query) ? view.width <= Number(query.match(/(\d+)/u)?.[1] || 0) : false,
      media: query,
      onchange: null,
      addEventListener() {},
      removeEventListener() {},
      addListener() {},
      removeListener() {},
      dispatchEvent: () => true,
    });
    window.requestIdleCallback = callback => window.setTimeout(() => callback({ didTimeout: false, timeRemaining: () => 50 }), 0);
    window.cancelIdleCallback = id => window.clearTimeout(id);
    if (!window.ResizeObserver) window.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
    if (!window.IntersectionObserver) window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
    if (!window.CSS) window.CSS = {};
    if (!window.CSS.escape) window.CSS.escape = value => String(value).replace(/[^a-zA-Z0-9_-]/gu, match => `\\${match}`);

    const map = createMapStub();
    window.map = map;
    window.mapkit = map;
    window.L = createLeafletStub(map);
    installFastMapTestEngine();
    const mapElement = document.getElementById("map");
    mapElement._leaflet_map = map;
    mapElement._leaflet_id = 1;

    const buildingRecords = [
      { id: 501, user_id: 1988, building_type: 2, building_type_caption: "Fire Station", caption: "Leith Fire Station" },
      { id: 502, user_id: 1988, building_type: 6, building_type_caption: "Police Station", caption: "Central Police Station" },
      { id: 601, user_id: 77, building_type: 2, building_type_caption: "Fire Station", caption: "Alliance Fire Station" },
      { id: 602, user_id: 77, building_type: 22, building_type_caption: "Ambulance Station", caption: "Alliance Ambulance Station" },
    ];
    const buildingTargets = new Map();
    const buildingMarkers = buildingRecords.map((record, index) => {
      const marker = window.L.marker(
        { lat: 55.91 + (index * 0.025), lng: -3.27 + (index * 0.038) },
        { icon: window.L.icon({ iconUrl: `/images/fixture-building-${record.building_type}.png`, iconSize: [32, 37], iconAnchor: [16, 37] }) },
      );
      Object.assign(marker, { building_id: record.id, user_id: record.user_id, building_type: record.building_type, building: record });
      marker.setOpacity = value => { marker.options.opacity = Number(value); return marker; };
      const key = `${record.user_id}:${record.building_type}`;
      if (!buildingTargets.has(key)) {
        const children = new Set();
        buildingTargets.set(key, {
          _leaflet_id: 1000 + buildingTargets.size,
          children,
          addLayer(layer) { children.add(layer); return this; },
          hasLayer(layer) { return children.has(layer); },
        });
      }
      buildingTargets.get(key).addLayer(marker);
      map.addLayer(marker);
      return marker;
    });
    for (const target of buildingTargets.values()) map.addLayer(target);
    window.building_markers = buildingMarkers;
    window.building_markers_params_cache_per_id = buildingRecords;
    window.building_markers_cache = buildingRecords;
    window.buildings = buildingRecords;
    window.map_filters_service = {
      getFilterLayerByBuildingParams(params) { return buildingTargets.get(`${params.user_id}:${params.building_type}`) || null; },
    };
    for (const control of document.querySelectorAll("#map_filters input[type='checkbox']")) {
      control.addEventListener("change", () => {
        const typeId = Number(control.value);
        buildingRecords.forEach((record, index) => {
          if (Number(record.building_type) !== typeId) return;
          const marker = buildingMarkers[index];
          const target = buildingTargets.get(`${record.user_id}:${record.building_type}`);
          if (control.checked) {
            if (target && !map.hasLayer(target)) map.addLayer(target);
            if (!map.hasLayer(marker)) map.addLayer(marker);
          } else {
            if (map.hasLayer(marker)) map.removeLayer(marker);
            if (target && map.hasLayer(target)) map.removeLayer(target);
          }
        });
      });
    }

    const missionRecords = [
      { id: 1001, mission_id: 1001, user_id: 1988, caption: "Warehouse Fire", created_at: new Date(Date.now() - 45 * 60 * 1000).toISOString() },
      { id: 1002, mission_id: 1002, user_id: 77, caption: "Road Traffic Collision", created_at: new Date(Date.now() - 90 * 60 * 1000).toISOString(), alliance_id: 44 },
    ];
    const missionMarkers = missionRecords.map((record, index) => {
      const marker = window.L.marker(
        { lat: 55.945 + (index * 0.045), lng: -3.22 + (index * 0.075) },
        { icon: window.L.icon({ iconUrl: `/images/fixture-mission-${index + 1}.png`, iconSize: [32, 37], iconAnchor: [16, 37] }) },
      );
      Object.assign(marker, record);
      marker.options = { ...marker.options, mission_id: record.id, user_id: record.user_id };
      map.addLayer(marker);
      return marker;
    });
    window.missions = missionRecords;
    window.mission_markers = missionMarkers;

    const vehicleRecords = [
      { id: 701, vehicle_id: 701, user_id: 1988, caption: "Pump 1", vehicle_type_caption: "Fire Engine", fms_real: 2 },
      { id: 702, vehicle_id: 702, user_id: 1988, caption: "ARV 2", vehicle_type_caption: "Armed Response Vehicle", fms_real: 3 },
      { id: 703, vehicle_id: 703, user_id: 1988, caption: "Ambulance 3", vehicle_type_caption: "Ambulance", fms_real: 4 },
    ];
    const vehicleMarkers = vehicleRecords.map((record, index) => {
      const marker = window.L.marker(
        { lat: 55.925 + (index * 0.022), lng: -3.16 + (index * 0.041) },
        { icon: window.L.icon({ iconUrl: `/images/fixture-vehicle-${index + 1}.png`, iconSize: [28, 32], iconAnchor: [14, 32] }) },
      );
      Object.assign(marker, record);
      marker.options = { ...marker.options, vehicle_id: record.id, user_id: record.user_id };
      map.addLayer(marker);
      return marker;
    });
    const fixtureRouteLatLngs = [
      { lat: vehicleMarkers[1].getLatLng().lat, lng: vehicleMarkers[1].getLatLng().lng },
      { lat: 55.972, lng: -3.102 },
      { lat: 55.998, lng: -3.061 },
    ];
    const fixtureVehicleRoute = {
      _leaflet_id: 8702,
      options: { color: "red", opacity: 1, weight: 3 },
      getLatLngs() { return fixtureRouteLatLngs.map(point => ({ ...point })); },
      setLatLngs(points) {
        fixtureRouteLatLngs.splice(0, fixtureRouteLatLngs.length, ...points.map(point => ({ lat: Number(point.lat ?? point[0]), lng: Number(point.lng ?? point[1]) })));
        return this;
      },
      spliceLatLngs(index, count) { fixtureRouteLatLngs.splice(index, count); return this; },
    };
    map.addLayer(fixtureVehicleRoute);
    vehicleMarkers[1].polyline = fixtureVehicleRoute;
    window.__MCMS_FIXTURE_VEHICLE_ROUTE__ = fixtureVehicleRoute;
    window.vehicles = vehicleRecords;
    window.vehicle_markers = vehicleMarkers;

    map.addLayer({
      _leaflet_id: 9001,
      _url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      options: { tileSize: 256, minZoom: 0, maxZoom: 19, attribution: "© OpenStreetMap contributors" },
      getTileUrl() { return this._url; },
    });

    const gmValues = new Map();
    window.GM_getValue = (key, fallback) => gmValues.has(key) ? gmValues.get(key) : fallback;
    window.GM_setValue = (key, value) => { gmValues.set(key, value); };
    window.GM_deleteValue = key => { gmValues.delete(key); };
    window.GM_xmlhttpRequest = options => {
      const response = { status: 200, responseText: JSON.stringify({ schemaVersion: 1, version: "10.16.7", downloadUrl: "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/", sha256: "0".repeat(64) }) };
      const timer = window.setTimeout(() => options?.onload?.(response), 0);
      return { abort() { window.clearTimeout(timer); options?.onabort?.(); } };
    };

    const state = {
      activeTab: fixture.tab,
      uiTheme: fixture.theme,
      setupWizard: { completed: true, schema: 1 },
      updateBriefing: { enabled: false, seenVersion: "10.16.7", seenFeatures: [] },
      tabletMode: fixture.device === "tablet" ? "on" : "off",
      mobileMode: fixture.device === "ios" ? "on" : "off",
      majorIncidentFeed: { enabled: false, minimumCredits: 25000 },
      dispatchRecruitment: { dispatchId: "all", buildingTypeId: "all", hiringPhase: "3", personnelDesired: "400", delayMs: 1000 },
      expansionPlanner: { dispatchId: "all", buildingTypeId: "all", operationKind: "all", creditBudget: "50000000", maxStations: 100, delayMs: 1000 },
    };
    localStorage.setItem("mc_map_command_toolkit_state_v150", JSON.stringify(state));

    if (/jsdom/iu.test(navigator.userAgent)) {
      const originalRect = Element.prototype.getBoundingClientRect;
      Element.prototype.getBoundingClientRect = function () {
        if (this.id === "map" || this.id === "map_outer") return { x: 0, y: 46, left: 0, top: 46, right: view.width, bottom: view.height, width: view.width, height: view.height - 46, toJSON() { return this; } };
        if (this.id === "mc-map-command-toolkit-panel") {
          const width = fixture.device === "desktop" ? Math.min(1152, view.width - 64) : fixture.device === "tablet" ? view.width - 24 : view.width - 12;
          return { x: 6, y: 52, left: 6, top: 52, right: 6 + width, bottom: view.height - 6, width, height: view.height - 58, toJSON() { return this; } };
        }
        const rect = originalRect.call(this);
        return rect.width || rect.height ? rect : { x: 0, y: 0, left: 0, top: 0, right: 100, bottom: 30, width: 100, height: 30, toJSON() { return this; } };
      };
    }

    window.addEventListener("error", event => recordError(event.error || event.message));
    window.addEventListener("unhandledrejection", event => recordError(event.reason));
  }

  function waitFor(selector, timeoutMs = 5000) {
    const started = Date.now();
    return new Promise((resolve, reject) => {
      const check = () => {
        const element = document.querySelector(selector);
        if (element) { resolve(element); return; }
        if (Date.now() - started >= timeoutMs) { reject(new Error(`Timed out waiting for ${selector}`)); return; }
        window.setTimeout(check, 20);
      };
      check();
    });
  }

  async function loadToolkit(sourceText = "") {
    const script = document.createElement("script");
    if (sourceText) script.textContent = sourceText;
    else script.src = `/src/MissionChief_Map_Command_Toolkit.user.js?dev=${Date.now()}`;
    const loaded = new Promise((resolve, reject) => {
      script.addEventListener("load", resolve, { once: true });
      script.addEventListener("error", () => reject(new Error("Canonical userscript failed to load")), { once: true });
    });
    document.head.append(script);
    if (sourceText) return;
    await loaded;
  }

  async function openTarget() {
    const menu = await waitFor("#mc-map-command-toolkit-control .mcms-menu-btn");
    menu.click();
    const panel = await waitFor("#mc-map-command-toolkit-panel");
    const tab = panel.querySelector(`[data-tab="${fixture.tab}"]`);
    tab?.click();
    await new Promise(resolve => window.requestAnimationFrame(() => window.requestAnimationFrame(resolve)));
    if (fixture.focus) {
      const card = panel.querySelector(`[data-command-card="${fixture.focus}"]`);
      if (card) {
        card.classList.add("mcms-dev-focus");
        card.scrollIntoView?.({ block: "center" });
      }
    }
    return panel;
  }

  async function probeWidth(panel) {
    const widths = [];
    const buttons = Array.from(panel.querySelectorAll(".mcms-tabs [data-tab]"));
    const target = buttons.find(button => button.dataset.tab === fixture.tab);
    for (const button of buttons) {
      button.click();
      await new Promise(resolve => window.requestAnimationFrame(resolve));
      const width = panel.getBoundingClientRect().width;
      if (width > 0) widths.push(Math.round(width * 10) / 10);
    }
    target?.click();
    await new Promise(resolve => window.requestAnimationFrame(resolve));
    return widths;
  }

  async function buildHealthReport(panel) {
    const widths = await probeWidth(panel);
    const widthRange = widths.length ? Math.max(...widths) - Math.min(...widths) : Infinity;
    const documentOverflow = document.documentElement.scrollWidth > document.documentElement.clientWidth + 2;
    const visibleCards = Array.from(panel.querySelectorAll(".mcms-tab-panel.mcms-active .mcms-command-card"));
    const overflowingCards = visibleCards.filter(card => card.scrollWidth > card.clientWidth + 2);
    return {
      mount: panel.isConnected && panel.classList.contains("mcms-open"),
      runtimeHealthy: Boolean(window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__ && !window.__MC_MAP_COMMAND_TOOLKIT_RUNTIME__.destroyed),
      widthStable: widthRange <= 2,
      widthRange,
      widths,
      noHorizontalOverflow: !documentOverflow && overflowingCards.length === 0,
      overflowingCards: overflowingCards.map(card => card.dataset.commandCard || card.className),
      panel: {
        width: Math.round(panel.getBoundingClientRect().width * 10) / 10,
        scrollWidth: panel.scrollWidth,
        clientWidth: panel.clientWidth,
      },
      errors: errors.slice(),
    };
  }

  async function publishHealth(panel) {
    if (!healthMonitoringEnabled || healthRunning) return;
    window.clearTimeout(healthTimer);
    healthTimer = window.setTimeout(async () => {
      if (!healthMonitoringEnabled || healthRunning) return;
      healthRunning = true;
      try {
        const report = await buildHealthReport(panel);
        window.parent?.postMessage({ source: "mcms-dev-lab", type: "health", device: fixture.device, report }, location.origin);
        window.__MCMS_DEV_LAB_LAST_REPORT__ = report;
      } catch (error) {
        recordError(error);
      } finally {
        healthRunning = false;
      }
    }, 120);
  }

  function stopHealthMonitoring() {
    healthMonitoringEnabled = false;
    window.clearTimeout(healthTimer);
    healthTimer = 0;
    window.__MCMS_DEV_LAB_OBSERVER__?.disconnect?.();
    window.__MCMS_DEV_LAB_OBSERVER__ = null;
  }

  async function boot(options = {}) {
    try {
      healthMonitoringEnabled = true;
      installEnvironment();
      await loadToolkit(options.sourceText || "");
      const panel = await openTarget();
      await publishHealth(panel);
      const observer = new MutationObserver(() => { void publishHealth(panel); });
      observer.observe(panel, { childList: true, subtree: true });
      window.__MCMS_DEV_LAB_OBSERVER__ = observer;
      return panel;
    } catch (error) {
      recordError(error);
      const output = document.createElement("pre");
      output.id = "mcms-dev-lab-error";
      output.textContent = errors.join("\n\n");
      document.body.append(output);
      window.parent?.postMessage({
        source: "mcms-dev-lab",
        type: "health",
        device: fixture.device,
        report: { mount: false, runtimeHealthy: false, widthStable: false, noHorizontalOverflow: false, errors: errors.slice() },
      }, location.origin);
      throw error;
    }
  }

  window.__MCMS_DEV_LAB_API__ = Object.freeze({ boot, fixture, installEnvironment, loadToolkit, openTarget, buildHealthReport, stopHealthMonitoring });
  if (!window.__MCMS_DEV_LAB_TEST__) void boot();
})();
