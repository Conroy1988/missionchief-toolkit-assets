#!/usr/bin/env python3
"""Implement Issue #565: sequential optional no-reward releases in Patient Transport Sweep."""
from __future__ import annotations

import hashlib
import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
VERSION = "8.2.0"
ISSUE = 565


def clean(value: str) -> str:
    return textwrap.dedent(value).lstrip("\n")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    old_value = clean(old)
    new_value = clean(new)
    count = text.count(old_value)
    if count != 1:
        raise RuntimeError(f"Expected one replacement in {path}, found {count}: {old_value[:120]!r}")
    path.write_text(text.replace(old_value, new_value, 1), encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(clean(content), encoding="utf-8")


source = SOURCE.read_text(encoding="utf-8")
if source.count("// @version      8.1.5") != 1:
    raise RuntimeError("Unexpected metadata version")
if source.count("version: '8.1.5'") != 1:
    raise RuntimeError("Unexpected runtime version")
source = source.replace("// @version      8.1.5", f"// @version      {VERSION}", 1)
source = source.replace("version: '8.1.5'", f"version: '{VERSION}'", 1)

helper_marker = "    function transportSweepVisibleDischargeButtons() {"
if source.count(helper_marker) != 1:
    raise RuntimeError("Native Transport Sweep helper marker changed")

helpers = r'''
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT = 'release patient (no reward)';
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_PATH = /^\/vehicles\/(?<vehicleId>\d+)\/patient\/-1\/?$/u;
    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_LIMIT = 100;

    function transportSweepOptionalReleaseDetails(control) {
        if (!control || !transportSweepElementVisible(control)) return null;
        if (normaliseTransportSweepReleaseText(control.textContent) !== TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT) return null;
        const rawHref = String(control.getAttribute?.('href') || control.href || '').trim();
        if (!rawHref) return null;
        let url;
        try {
            url = new URL(rawHref, location.href);
        } catch (error) {
            return null;
        }
        let currentOrigin = '';
        try { currentOrigin = new URL(location.href).origin; } catch (error) {}
        if (currentOrigin && url.origin !== currentOrigin) return null;
        const match = url.pathname.match(TRANSPORT_SWEEP_OPTIONAL_RELEASE_PATH);
        if (!match?.groups?.vehicleId) return null;
        return {
            control,
            path: url.pathname,
            vehicleId: match.groups.vehicleId,
        };
    }

    function transportSweepOptionalReleaseControls() {
        const controls = [];
        const seen = new Set();
        const selector = 'a[href*="/vehicles/"][href*="/patient/-1"]';
        const addControl = control => {
            if (!control || seen.has(control)) return;
            seen.add(control);
            if (transportSweepOptionalReleaseDetails(control)) controls.push(control);
        };
        const inspect = root => {
            if (!root) return;
            try {
                if (root.matches?.(selector)) addControl(root);
                Array.from(root.querySelectorAll?.(selector) || []).forEach(addControl);
            } catch (error) {}
        };
        transportSweepVisibleWindowRoots().forEach(inspect);
        transportSweepDocumentContexts().forEach(context => inspect(context.doc));
        return controls;
    }

    function transportSweepOptionalReleaseControlForVehicle(vehicleId) {
        const expected = String(vehicleId || '').trim();
        if (!expected) return null;
        for (const control of transportSweepOptionalReleaseControls()) {
            const details = transportSweepOptionalReleaseDetails(control);
            if (details?.vehicleId === expected) return details;
        }
        return null;
    }

    function findTransportSweepOptionalReleaseControl(missionId, excludedReleaseKeys = null) {
        const excluded = excludedReleaseKeys instanceof Set ? excludedReleaseKeys : new Set();
        for (const control of transportSweepOptionalReleaseControls()) {
            const details = transportSweepOptionalReleaseDetails(control);
            if (!details) continue;
            const releaseKey = transportSweepReleaseKey(missionId, details.vehicleId);
            if (!releaseKey || excluded.has(releaseKey) || transportSweepRuntime.confirmedReleaseKeys.has(releaseKey)) continue;
            return { ...details, releaseKey };
        }
        return null;
    }

    function recordTransportSweepOptionalReleaseError(message) {
        transportSweepRuntime.errors += 1;
        transportSweepLog(message, 'error');
        renderTransportSweepPanel();
    }

    async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance) {
        const outcome = { cleared: 0, missionAvailable: true };
        const allowance = Number.isFinite(remainingAllowance)
            ? Math.max(0, Math.floor(remainingAllowance))
            : TRANSPORT_SWEEP_OPTIONAL_RELEASE_LIMIT;
        const maximum = Math.min(allowance, TRANSPORT_SWEEP_OPTIONAL_RELEASE_LIMIT);
        const attemptedReleaseKeys = new Set();

        while (
            transportSweepRuntime.running
            && !transportSweepRuntime.stopRequested
            && outcome.cleared < maximum
        ) {
            const release = findTransportSweepOptionalReleaseControl(missionId, attemptedReleaseKeys);
            if (!release) break;
            attemptedReleaseKeys.add(release.releaseKey);
            transportSweepLog(`Using Release patient (No reward) for vehicle ${release.vehicleId} at ${item.caption}`);

            try {
                release.control.click();
                await transportSweepWaitFor(() => {
                    if (transportSweepRuntime.stopRequested) return true;
                    if (!release.control.isConnected || !transportSweepElementVisible(release.control)) return true;
                    return transportSweepOptionalReleaseControlForVehicle(release.vehicleId) ? null : true;
                }, 5000, 70);
            } catch (error) {
                recordTransportSweepOptionalReleaseError(
                    `Could not activate Release patient (No reward) for vehicle ${release.vehicleId}: ${error?.message || error}`
                );
                break;
            }

            if (transportSweepRuntime.stopRequested) break;
            await closeTransportSweepWindows('reopening mission after no-reward patient release');
            if (transportSweepRuntime.stopRequested) break;

            const reopened = await openTransportSweepPath(`/missions/${missionId}`, 'mission');
            if (!reopened) {
                outcome.missionAvailable = false;
                recordTransportSweepOptionalReleaseError(
                    `Could not reopen ${item.caption} after releasing vehicle ${release.vehicleId}`
                );
                break;
            }

            if (transportSweepOptionalReleaseControlForVehicle(release.vehicleId)) {
                recordTransportSweepOptionalReleaseError(
                    `Release patient (No reward) remained available for vehicle ${release.vehicleId}; stopped repeated clicking`
                );
                break;
            }

            if (recordTransportSweepConfirmedRelease(
                release.releaseKey,
                `Cleared vehicle ${release.vehicleId} at ${item.caption} with Release patient (No reward)`
            )) {
                outcome.cleared += 1;
            }
        }
        return outcome;
    }

'''
source = source.replace(helper_marker, helpers + helper_marker, 1)

candidate_line = "        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId);\n"
if source.count(candidate_line) != 1:
    raise RuntimeError("Transport Sweep candidate collection marker changed")
fast_path = '''        const optionalReleaseResult = await processTransportSweepOptionalReleaseControls(
            item,
            missionId,
            Math.max(0, remainingAllowance - clearedHere)
        );
        clearedHere += optionalReleaseResult.cleared;
        if (
            transportSweepRuntime.stopRequested
            || !optionalReleaseResult.missionAvailable
            || clearedHere >= remainingAllowance
        ) {
            await closeTransportSweepWindows('ending no-reward patient release fast path');
            return clearedHere;
        }

'''
source = source.replace(candidate_line, fast_path + candidate_line, 1)
SOURCE.write_text(source, encoding="utf-8")

static_contract = r'''#!/usr/bin/env python3
"""Issue #565 contract for sequential optional no-reward releases."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
PREFLIGHT = ROOT / ".github/scripts/run_userscript_preflight.sh"
CHANGELOG = ROOT / "CHANGELOG.md"
HELP = ROOT / "help/index.html"


def section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    assert re.search(r"(?m)^//\s*@version\s+8\.2\.0$", source)
    assert "version: '8.2.0'" in source
    for marker in [
        "TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT = 'release patient (no reward)'",
        "TRANSPORT_SWEEP_OPTIONAL_RELEASE_PATH",
        "function transportSweepOptionalReleaseDetails(control)",
        "function transportSweepOptionalReleaseControls()",
        "function transportSweepOptionalReleaseControlForVehicle(vehicleId)",
        "function findTransportSweepOptionalReleaseControl(missionId, excludedReleaseKeys = null)",
        "async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance)",
        "Release patient (No reward) remained available",
        "await closeTransportSweepWindows('reopening mission after no-reward patient release')",
        "await openTransportSweepPath(`/missions/${missionId}`, 'mission')",
        "recordTransportSweepConfirmedRelease(",
    ]:
        assert marker in source, marker

    helper = section(
        source,
        "    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT",
        "    function transportSweepVisibleDischargeButtons()",
    )
    assert r"^\/vehicles\/(?<vehicleId>\d+)\/patient\/-1" in helper
    for forbidden in [
        "GM_xmlhttpRequest",
        "fetch(",
        "setInterval(",
        "setTimeout(",
        "MutationObserver",
        "missionIndex",
        "setTransportSweepMissionProgress",
        "completeTransportSweepMissionProgress",
        "finaliseTransportSweepMissionProgress",
    ]:
        assert forbidden not in helper, forbidden

    processor_match = re.search(
        r"async function processTransportSweepMission\(item, remainingAllowance\) \{([\s\S]*?)\n    \}\n\n    async function startTransportSweep",
        source,
    )
    assert processor_match
    processor = processor_match.group(1)
    assert "processTransportSweepOptionalReleaseControls(" in processor
    assert "collectTransportSweepVehicleCandidatesForMission(missionId)" in processor
    assert processor.index("processTransportSweepOptionalReleaseControls(") < processor.index(
        "collectTransportSweepVehicleCandidatesForMission(missionId)"
    )
    assert "clearedHere += optionalReleaseResult.cleared" in processor
    assert "!optionalReleaseResult.missionAvailable" in processor
    assert "openTransportSweepVehicle(candidate)" in processor

    preflight = PREFLIGHT.read_text(encoding="utf-8")
    assert ".github/scripts/test_issue565_transport_sweep_no_reward.py" in preflight
    assert ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs" in preflight
    assert "## [8.2.0] - 2026-07-28" in CHANGELOG.read_text(encoding="utf-8")
    assert "Release patient (No reward)" in HELP.read_text(encoding="utf-8")
    print("Issue #565 optional no-reward Transport Sweep contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
write(ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward.py", static_contract)

runtime_contract = r'''#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { JSDOM } from "jsdom";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const source = fs.readFileSync(path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"), "utf8");

function extractFunction(name) {
  const markers = [`    function ${name}(`, `    async function ${name}(`];
  const starts = markers.map(marker => source.indexOf(marker)).filter(index => index >= 0);
  assert.ok(starts.length, `${name} missing`);
  const start = Math.min(...starts);
  const signatureEnd = source.indexOf(") {", start);
  assert.ok(signatureEnd >= 0, `${name} signature end missing`);
  const open = signatureEnd + 2;
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = open; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === "'" || char === '"' || char === "`") { quote = char; continue; }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error(`Unable to extract ${name}`);
}

const helperStart = source.indexOf("    const TRANSPORT_SWEEP_OPTIONAL_RELEASE_TEXT");
const helperEnd = source.indexOf("    function transportSweepVisibleDischargeButtons()", helperStart);
assert.ok(helperStart >= 0 && helperEnd > helperStart, "Optional release helper block missing");
const helperSource = source.slice(helperStart, helperEnd);
const releaseHelpers = [
  "transportSweepReleaseKey",
  "recordTransportSweepConfirmedRelease",
].map(extractFunction).join("\n\n");

function createHarness(pages, options = {}) {
  const dom = new JSDOM("<!doctype html><html><body><main id=mission></main></body></html>", {
    url: "https://www.missionchief.co.uk/missions/9001",
  });
  let generation = 0;
  let opens = 0;
  let closes = 0;
  const clicks = [];
  const logs = [];
  const runtime = {
    running: true,
    stopRequested: false,
    cleared: 0,
    processed: 0,
    errors: 0,
    confirmedReleaseKeys: new Set(),
    missionIndex: 7,
    missionTotal: 11,
    completedMissionCount: 6,
  };

  function render() {
    const ids = pages[Math.min(generation, pages.length - 1)] || [];
    dom.window.document.querySelector("#mission").innerHTML = ids.map(id =>
      `<a class="btn btn-default btn-xs" href="/vehicles/${id}/patient/-1">Release patient (No reward)</a>`
    ).join("");
  }
  render();

  dom.window.document.addEventListener("click", event => {
    const anchor = event.target.closest?.('a[href*="/patient/-1"]');
    if (!anchor) return;
    event.preventDefault();
    const id = anchor.getAttribute("href").match(/\/vehicles\/(\d+)\//)?.[1] || "";
    clicks.push(id);
    anchor.remove();
    if (options.stopOnClick) runtime.stopRequested = true;
  });

  const sandbox = {
    console,
    Array,
    Map,
    Set,
    Math,
    Number,
    Object,
    RegExp,
    String,
    URL: dom.window.URL,
    location: dom.window.location,
    document: dom.window.document,
    transportSweepRuntime: runtime,
    normaliseTransportSweepReleaseText(value) {
      return String(value || "").replace(/\s+/gu, " ").trim().toLowerCase();
    },
    transportSweepElementVisible(element) { return Boolean(element?.isConnected); },
    transportSweepVisibleWindowRoots() { return [dom.window.document.body]; },
    transportSweepDocumentContexts() { return [{ doc: dom.window.document, label: "top" }]; },
    async transportSweepWaitFor(predicate) {
      for (let index = 0; index < 5; index += 1) {
        const value = predicate();
        if (value) return value;
        await Promise.resolve();
      }
      return false;
    },
    async closeTransportSweepWindows() { closes += 1; },
    async openTransportSweepPath(pathname) {
      assert.equal(pathname, "/missions/9001");
      opens += 1;
      if (options.failOpen) return false;
      generation += 1;
      render();
      return true;
    },
    transportSweepLog(message, level = "info") { logs.push({ message, level }); },
    renderTransportSweepPanel() {},
    renderTransportSweepHud() {},
  };
  vm.createContext(sandbox);
  vm.runInContext(
    `${releaseHelpers}\n${helperSource}\nthis.runOptionalRelease = processTransportSweepOptionalReleaseControls;`,
    sandbox,
    { filename: "issue565-optional-release.js" },
  );
  return {
    dom,
    runtime,
    clicks,
    logs,
    get opens() { return opens; },
    get closes() { return closes; },
    run(allowance = Number.POSITIVE_INFINITY) {
      return sandbox.runOptionalRelease({ caption: "Multi-patient mission" }, "9001", allowance);
    },
  };
}

{
  const harness = createHarness([["111"], ["222"], []]);
  const outcome = await harness.run();
  assert.deepEqual(JSON.parse(JSON.stringify(outcome)), { cleared: 2, missionAvailable: true });
  assert.deepEqual(harness.clicks, ["111", "222"]);
  assert.equal(harness.opens, 2);
  assert.equal(harness.closes, 2);
  assert.equal(harness.runtime.cleared, 2);
  assert.equal(harness.runtime.processed, 2);
  assert.equal(harness.runtime.errors, 0);
  assert.equal(harness.runtime.missionIndex, 7);
  assert.equal(harness.runtime.completedMissionCount, 6);
}

{
  const harness = createHarness([[]]);
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(outcome.missionAvailable, true);
  assert.equal(harness.opens, 0);
  assert.equal(harness.clicks.length, 0);
}

{
  const harness = createHarness([["111"], ["111"]]);
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(harness.clicks.length, 1, "A persistent release link must not be clicked repeatedly");
  assert.equal(harness.opens, 1);
  assert.equal(harness.runtime.errors, 1);
  assert.match(harness.logs.at(-1).message, /stopped repeated clicking/u);
}

{
  const harness = createHarness([["111"], ["222"]]);
  const outcome = await harness.run(1);
  assert.equal(outcome.cleared, 1);
  assert.deepEqual(harness.clicks, ["111"]);
  assert.equal(harness.opens, 1);
  assert.ok(harness.dom.window.document.querySelector('a[href="/vehicles/222/patient/-1"]'));
}

{
  const harness = createHarness([["111"], ["222"]], { stopOnClick: true });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(harness.opens, 0);
  assert.equal(harness.runtime.cleared, 0);
}

{
  const harness = createHarness([["111"]], { failOpen: true });
  const outcome = await harness.run();
  assert.equal(outcome.cleared, 0);
  assert.equal(outcome.missionAvailable, false);
  assert.equal(harness.runtime.errors, 1);
}

console.log("Issue #565 optional no-reward Transport Sweep runtime passed: sequential reopening, persistence guard, allowance, fallback and cancellation.");
'''
write(ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs", runtime_contract)

preflight = ROOT / ".github/scripts/run_userscript_preflight.sh"
replace_once(
    preflight,
    ".github/scripts/test_issue530_transport_sweep_discharge_confirmation.py .github/scripts/test_issue537_godfather_css_activation.py",
    ".github/scripts/test_issue530_transport_sweep_discharge_confirmation.py .github/scripts/test_issue565_transport_sweep_no_reward.py .github/scripts/test_issue537_godfather_css_activation.py",
)
replace_once(
    preflight,
    "node .github/scripts/test_issue530_transport_sweep_discharge_confirmation_runtime.js\n",
    "node .github/scripts/test_issue530_transport_sweep_discharge_confirmation_runtime.js\nnode .github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs\n",
)

native_contract = ROOT / ".github/scripts/test_transport_sweep_native_contract.py"
replace_once(
    native_contract,
    "'function transportSweepVisibleDischargeButtons()'",
    "'function transportSweepOptionalReleaseControls()','async function processTransportSweepOptionalReleaseControls(item, missionId, remainingAllowance)','function transportSweepVisibleDischargeButtons()'",
)
replace_once(
    native_contract,
    "for item in ['collectTransportSweepVehicleCandidatesForMission(missionId)'",
    "for item in ['processTransportSweepOptionalReleaseControls(','collectTransportSweepVehicleCandidatesForMission(missionId)'",
)

changelog = ROOT / "CHANGELOG.md"
replace_once(
    changelog,
    "# Changelog\n\n",
    '''# Changelog

## [8.2.0] - 2026-07-28

### Patient Transport Sweep — sequential no-reward releases

- Added an automatic fast path for the exact optional **Release patient (No reward)** mission control.
- Reopens the same mission after every release and verifies the released vehicle/patient control has disappeared before counting success.
- Repeats one patient at a time for multi-patient missions until no matching control remains or the sweep allowance is reached.
- Stops repeated clicking when the same control survives a mission reopen and records a visible sweep error.
- Preserves the existing MissionChief-native **Discharge patient** vehicle-window process as the complete fallback when the optional control is unavailable.
- Adds no observer, recurring interval or additional network-request call site.

''',
)

site_data_path = ROOT / "docs/site-data.json"
site_data = json.loads(site_data_path.read_text(encoding="utf-8"))
transport = None
for category in site_data.get("featureCategories", []):
    for feature in category.get("features", []):
        if feature.get("name") == "Patient Transport Sweep":
            transport = feature
            break
if transport is None:
    raise RuntimeError("Patient Transport Sweep feature catalogue entry missing")
transport["summary"] = (
    "Releases eligible alliance patients through an exact no-reward mission control when available, "
    "then falls back to MissionChief's native vehicle discharge workflow."
)
transport["details"] = [
    "Optional no-reward mission-control fast path",
    "Reopens each mission and verifies every release",
    "Processes multiple patients sequentially",
    "MissionChief native Discharge patient fallback",
    "Bounded retries and confirmation evidence",
]
site_data_path.write_text(json.dumps(site_data, indent=2) + "\n", encoding="utf-8")

help_path = ROOT / "help/index.html"
help_text = help_path.read_text(encoding="utf-8").replace("8.1.5", VERSION)
section_html = '''
<section id="transport-sweep-no-reward"><h2>Patient Transport Sweep — no-reward fast path</h2><p>When the opened mission exposes the exact <strong>Release patient (No reward)</strong> control, the sweep releases one patient, reopens the same mission, verifies that patient is gone and continues with the next patient. Missions with several patients are processed sequentially. When the optional control is unavailable, the existing MissionChief-native <strong>Discharge patient</strong> vehicle-window workflow remains the fallback.</p></section>
'''
if "transport-sweep-no-reward" not in help_text:
    if "</main>" not in help_text:
        raise RuntimeError("Help Centre main closing tag missing")
    help_text = help_text.replace("</main>", section_html + "</main>", 1)
help_path.write_text(help_text, encoding="utf-8")

help_manifest_path = ROOT / "help/manifest.json"
help_manifest = json.loads(help_manifest_path.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = VERSION
help_manifest["toolkitVersion"] = VERSION
help_manifest["updated"] = "2026-07-28"
help_manifest["sections"] = max(21, int(help_manifest.get("sections", 0)))
help_manifest["runtimeGuidePatch"] = (
    "Toolkit v8.2.0 adds sequential verified Release patient (No reward) handling with same-mission reopening, "
    "multi-patient processing, repeated-click protection and the existing native discharge fallback."
)
help_manifest_path.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

write(
    ROOT / "docs/issue-565-transport-sweep-no-reward.md",
    '''# Issue #565 — Patient Transport Sweep no-reward release path

Toolkit v8.2.0 recognises only the exact visible `Release patient (No reward)` mission control whose same-origin path matches `/vehicles/{vehicleId}/patient/-1`.

The sweep releases one patient, reopens the same mission, verifies that the released vehicle-specific control is absent, records one confirmed patient outcome and then repeats for the next patient. A persistent control, failed mission reopen or cancellation stops the fast path safely. When no matching control exists, the established MissionChief-native vehicle-window discharge process remains unchanged.

The implementation adds no observer, interval or new network-request call site. Permanent executable coverage includes multiple patients, allowance limiting, missing controls, persistent controls, reopen failure, cancellation and mission-progress isolation.
''',
)

source_bytes = SOURCE.read_bytes()
source_sha = hashlib.sha256(source_bytes).hexdigest()
source_lines = len(source_bytes.decode("utf-8").splitlines())
for relative in [
    "dist/MissionChief_Map_Command_Toolkit.user.js",
    "dist/MissionChief_Map_Command_Toolkit.txt",
]:
    (ROOT / relative).write_bytes(source_bytes)
(ROOT / "dist/SHA256SUMS.txt").write_text(
    f"{source_sha}  MissionChief_Map_Command_Toolkit.user.js\n"
    f"{source_sha}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest_path = ROOT / "dist/release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({
    "version": VERSION,
    "sha256": source_sha,
    "bytes": len(source_bytes),
    "lines": source_lines,
})
manifest.setdefault("metadata", {})["runtimeVersion"] = VERSION
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

headroom_path = ROOT / ".github/fixtures/main-style-source-headroom.json"
headroom = json.loads(headroom_path.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
previous_bytes = int(candidate["sourceBytes"])
previous_lines = int(candidate["sourceLines"])
candidate.update({
    "issue": ISSUE,
    "version": VERSION,
    "sourceBytes": len(source_bytes),
    "sourceLines": source_lines,
    "sourceSha256": source_sha,
    "maxSourceBytes": max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000),
    "maxSourceLines": max(int(candidate.get("maxSourceLines", 0)), source_lines + 250),
    "baseline": "8.1.5",
    "scope": "Issue #565 sequential no-reward patient releases with same-mission reopening, per-patient verification, repeat-click protection and native discharge fallback",
})
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - previous_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + source_lines - previous_lines
headroom_path.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(
    f"Issue #565 v{VERSION} package applied: {source_sha}, "
    f"{len(source_bytes)} bytes, {source_lines} lines"
)
