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
    const bounds = {
      contains: () => true,
      getNorth: () => 56.2,
      getSouth: () => 55.7,
      getEast: () => -2.8,
      getWest: () => -3.6,
    };
    return {
      _leaflet_id: 1,
      _layers: layers,
      addLayer(layer) { layers[layer?._leaflet_id || Object.keys(layers).length + 2] = layer; return this; },
      removeLayer(layer) { for (const [key, value] of Object.entries(layers)) if (value === layer) delete layers[key]; return this; },
      hasLayer(layer) { return Object.values(layers).includes(layer); },
      eachLayer(callback) { Object.values(layers).forEach(callback); },
      getBounds: () => bounds,
      getCenter: () => ({ lat: 55.9533, lng: -3.1883 }),
      getZoom: () => 12,
      getContainer: () => document.getElementById("map"),
      latLngToContainerPoint: () => ({ x: viewport().width / 2, y: viewport().height / 2 }),
      containerPointToLatLng: () => ({ lat: 55.9533, lng: -3.1883 }),
      invalidateSize() { return this; },
      panTo() { return this; },
      setView() { return this; },
      fitBounds() { return this; },
      on(types, handler) { String(types).split(/\s+/u).forEach(type => listeners.set(`${type}:${listeners.size}`, handler)); return this; },
      off() { return this; },
      fire(type, payload = {}) { for (const [key, handler] of listeners) if (key.startsWith(`${type}:`)) handler({ type, target: this, ...payload }); return this; },
    };
  }

  function createLeafletStub(map) {
    let id = 10;
    const layer = extra => ({
      _leaflet_id: id++,
      options: {},
      addTo(target = map) { target.addLayer(this); return this; },
      remove() { map.removeLayer(this); return this; },
      bindTooltip() { return this; },
      setIcon() { return this; },
      setLatLng() { return this; },
      setStyle() { return this; },
      getLatLng: () => ({ lat: 55.9533, lng: -3.1883 }),
      ...extra,
    });
    return {
      map: () => map,
      stamp(value) { if (!value._leaflet_id) value._leaflet_id = id++; return value._leaflet_id; },
      layerGroup: () => layer({ clearLayers() { return this; }, addLayer() { return this; }, eachLayer() {} }),
      featureGroup: () => layer({ clearLayers() { return this; }, addLayer() { return this; }, eachLayer() {} }),
      marker: latlng => layer({ getLatLng: () => latlng }),
      circle: latlng => layer({ getLatLng: () => latlng }),
      circleMarker: latlng => layer({ getLatLng: () => latlng }),
      polyline: () => layer({ getBounds: () => map.getBounds() }),
      divIcon: options => ({ options }),
      latLng: (lat, lng) => ({ lat: Number(lat), lng: Number(lng) }),
      latLngBounds: () => map.getBounds(),
      point: (x, y) => ({ x, y }),
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
    if (/\/api\/vehicles|\/vehicles\.json/iu.test(url.pathname)) return jsonResponse([]);
    if (/\/api\/buildings|\/buildings\.json/iu.test(url.pathname)) return jsonResponse([]);
    if (/toolkit-update-manifest|update-manifest\.json/iu.test(url.pathname)) {
      return jsonResponse({ schemaVersion: 1, version: "10.15.3", downloadUrl: "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/", sha256: "0".repeat(64) });
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
    const mapElement = document.getElementById("map");
    mapElement._leaflet_map = map;
    mapElement._leaflet_id = 1;

    const gmValues = new Map();
    window.GM_getValue = (key, fallback) => gmValues.has(key) ? gmValues.get(key) : fallback;
    window.GM_setValue = (key, value) => { gmValues.set(key, value); };
    window.GM_deleteValue = key => { gmValues.delete(key); };
    window.GM_xmlhttpRequest = options => {
      const response = { status: 200, responseText: JSON.stringify({ schemaVersion: 1, version: "10.15.3", downloadUrl: "https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/", sha256: "0".repeat(64) }) };
      const timer = window.setTimeout(() => options?.onload?.(response), 0);
      return { abort() { window.clearTimeout(timer); options?.onabort?.(); } };
    };

    const state = {
      activeTab: fixture.tab,
      uiTheme: fixture.theme,
      setupWizard: { completed: true, schema: 1 },
      updateBriefing: { enabled: false, seenVersion: "10.15.3", seenFeatures: [] },
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
    if (healthRunning) return;
    window.clearTimeout(healthTimer);
    healthTimer = window.setTimeout(async () => {
      if (healthRunning) return;
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

  async function boot(options = {}) {
    try {
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

  window.__MCMS_DEV_LAB_API__ = Object.freeze({ boot, fixture, installEnvironment, loadToolkit, openTarget, buildHealthReport });
  if (!window.__MCMS_DEV_LAB_TEST__) void boot();
})();
