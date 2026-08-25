const DEVICES = ["desktop", "tablet", "ios"];
const DEFAULTS = Object.freeze({ device: "desktop", tab: "administration", focus: "", theme: "mapCommand" });
const controls = {
  device: document.querySelector("[data-device-controls]"),
  tab: document.querySelector("[data-tab]"),
  focus: document.querySelector("[data-focus]"),
  theme: document.querySelector("[data-theme]"),
  reload: document.querySelector("[data-reload]"),
  stage: document.querySelector("[data-preview-stage]"),
  grid: document.querySelector("[data-preview-grid]"),
  build: document.querySelector(".build-state"),
  buildLabel: document.querySelector("[data-build-label]"),
  healthSummary: document.querySelector("[data-health-summary]"),
};

const query = new URLSearchParams(location.search);
const state = {
  device: ["desktop", "tablet", "ios", "matrix"].includes(query.get("device")) ? query.get("device") : DEFAULTS.device,
  tab: query.get("tab") || DEFAULTS.tab,
  focus: query.get("focus") || DEFAULTS.focus,
  theme: query.get("theme") || DEFAULTS.theme,
};
const reports = new Map();
let sourceIdentity = "";
let pendingReload = null;

function frameDevices() {
  return state.device === "matrix" ? DEVICES : [state.device];
}

function synchronizeControls() {
  controls.device.querySelectorAll("[data-device]").forEach(button => {
    button.setAttribute("aria-pressed", String(button.dataset.device === state.device));
  });
  controls.tab.value = state.tab;
  controls.focus.value = state.focus;
  controls.theme.value = state.theme;
  controls.stage.dataset.device = state.device;
  const next = new URL(location.href);
  Object.entries(state).forEach(([key, value]) => {
    if (value) next.searchParams.set(key, value);
    else next.searchParams.delete(key);
  });
  history.replaceState(null, "", next);
}

function frameUrl(device) {
  const params = new URLSearchParams({
    device,
    tab: state.tab,
    focus: state.focus,
    theme: state.theme,
    revision: String(Date.now()),
  });
  return `/devlab/frame.html?${params}`;
}

function renderFrames() {
  reports.clear();
  controls.grid.replaceChildren();
  for (const device of frameDevices()) {
    const shell = document.createElement("div");
    shell.className = "preview-shell";
    shell.dataset.device = device;
    const label = document.createElement("span");
    label.className = "preview-label";
    label.textContent = device === "ios" ? "iOS · 390 × 844" : device === "tablet" ? "Tablet · 1024 × 768" : "Desktop · 1440 × 900";
    const frame = document.createElement("iframe");
    frame.className = "preview-frame";
    frame.title = `${device} Toolkit preview`;
    frame.src = frameUrl(device);
    frame.setAttribute("loading", "eager");
    shell.append(label, frame);
    controls.grid.append(shell);
  }
  renderHealth();
}

function setHealth(name, stateName, label) {
  const element = document.querySelector(`[data-health="${name}"]`);
  if (!element) return;
  element.dataset.state = stateName;
  element.textContent = label;
}

function renderHealth() {
  const expected = frameDevices();
  const complete = expected.every(device => reports.has(device));
  if (!complete) {
    for (const key of ["mount", "width", "overflow", "runtime"]) setHealth(key, "waiting", `${key[0].toUpperCase()}${key.slice(1)} waiting`);
    controls.healthSummary.textContent = `Waiting for ${expected.filter(device => !reports.has(device)).join(", ")}…`;
    return;
  }
  const values = expected.map(device => reports.get(device));
  const checks = {
    mount: values.every(report => report.mount),
    width: values.every(report => report.widthStable),
    overflow: values.every(report => report.noHorizontalOverflow),
    runtime: values.every(report => report.runtimeHealthy && !report.errors.length),
  };
  setHealth("mount", checks.mount ? "pass" : "fail", checks.mount ? "Mount passed" : "Mount failed");
  setHealth("width", checks.width ? "pass" : "fail", checks.width ? "Width stable" : "Width unstable");
  setHealth("overflow", checks.overflow ? "pass" : "fail", checks.overflow ? "No overflow" : "Overflow detected");
  setHealth("runtime", checks.runtime ? "pass" : "fail", checks.runtime ? "Runtime clean" : "Runtime error");
  const passed = Object.values(checks).every(Boolean);
  controls.healthSummary.textContent = passed
    ? `${expected.length} viewport${expected.length === 1 ? "" : "s"} passed the live UI probe.`
    : values.flatMap(report => report.errors).at(0) || "Preview requires attention.";
}

function scheduleReload() {
  clearTimeout(pendingReload);
  pendingReload = setTimeout(renderFrames, 180);
}

controls.device.addEventListener("click", event => {
  const button = event.target.closest("[data-device]");
  if (!button || button.dataset.device === state.device) return;
  state.device = button.dataset.device;
  synchronizeControls();
  renderFrames();
});
controls.tab.addEventListener("change", () => { state.tab = controls.tab.value; synchronizeControls(); scheduleReload(); });
controls.focus.addEventListener("change", () => { state.focus = controls.focus.value; synchronizeControls(); scheduleReload(); });
controls.theme.addEventListener("change", () => { state.theme = controls.theme.value; synchronizeControls(); scheduleReload(); });
controls.reload.addEventListener("click", renderFrames);

window.addEventListener("message", event => {
  if (event.origin !== location.origin || event.data?.source !== "mcms-dev-lab" || event.data?.type !== "health") return;
  reports.set(event.data.device, event.data.report);
  renderHealth();
});

async function pollSource() {
  try {
    const response = await fetch(`/__mcms_dev_state?now=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const build = await response.json();
    const nextIdentity = `${build.sha256}:${build.labSha256}`;
    controls.build.dataset.buildState = "ready";
    controls.buildLabel.textContent = `Toolkit ${build.version} · ${build.sha256.slice(0, 9)}`;
    if (sourceIdentity && nextIdentity !== sourceIdentity) renderFrames();
    sourceIdentity = nextIdentity;
  } catch (error) {
    controls.build.dataset.buildState = "error";
    controls.buildLabel.textContent = `Watcher unavailable · ${error.message}`;
  } finally {
    setTimeout(pollSource, 750);
  }
}

synchronizeControls();
renderFrames();
void pollSource();
