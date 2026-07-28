#!/usr/bin/env python3
"""Apply Issue #565 v8.2.5 real multi-cell FMS 5 patient-row correction."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


source_path = "src/MissionChief_Map_Command_Toolkit.user.js"
source = read(source_path)
source = replace_once(source, "// @version      8.2.4", "// @version      8.2.5", "metadata version")
source = replace_once(source, "version: '8.2.4'", "version: '8.2.5'", "runtime version")

old_counter = """    function transportSweepOptionalReleasePatientCountFromRow(row) {
        const vehicleCell = row?.querySelector?.('td:first-child') || row;
        const text = String(vehicleCell?.textContent || '').replace(/\\s+/gu, ' ').trim();
        const match = text.match(/\\bpatients?\\s*:\\s*(.+)$/iu);
        if (!match?.[1]) return null;
        const names = match[1]
            .split(/\\s*,\\s*/u)
            .map(value => value.trim())
            .filter(Boolean);
        return names.length || null;
    }
"""
new_counter = """    function transportSweepOptionalReleasePatientCountFromRow(row) {
        if (!row) return null;
        let patientCells = [];
        try { patientCells = Array.from(row.querySelectorAll?.('td') || []); } catch (error) {}
        const patientTextSource = patientCells.find(cell =>
            /\\bpatients?\\s*:/iu.test(String(cell?.textContent || ''))
        ) || row;
        const text = String(patientTextSource?.textContent || '').replace(/\\s+/gu, ' ').trim();
        const match = text.match(/\\bpatients?\\s*:\\s*(.+)$/iu);
        if (!match?.[1]) return null;
        const patientText = match[1]
            .replace(/\\s+Release patient \\(No reward\\).*$/iu, '')
            .replace(/\\s*\\([^()]*\\)\\s*$/u, '')
            .trim();
        const names = patientText
            .split(/\\s*,\\s*/u)
            .map(value => value.trim())
            .filter(Boolean);
        return names.length || null;
    }
"""
source = replace_once(source, old_counter, new_counter, "real multi-cell patient counter")
write(source_path, source)

changelog_path = "CHANGELOG.md"
changelog = read(changelog_path)
entry = """## [8.2.5] - 2026-07-28

### Patient Transport Sweep — real MissionChief FMS 5 row layout

- Fixed v8.2.4 rejecting every real FMS 5 patient row because it searched only the first table cell, which contains the FMS badge rather than the patient text.
- Locates the authoritative table cell containing `Patient:` anywhere within the vehicle row while retaining the row-wide fallback.
- Supports the real multi-cell MissionChief layout, owner-profile markup, ambulances, ILBs and several comma-separated patients.
- Preserves verified own-vehicle exclusion, exact no-reward control validation, duplicate-control resolution, delayed readiness, completed requests and native fallback.
- Replaced the one-cell synthetic regression fixture with the supplied browser-faithful multi-cell structure.

"""
if "## [8.2.5] - 2026-07-28" not in changelog:
    changelog = replace_once(changelog, "# Changelog\n\n", "# Changelog\n\n" + entry, "changelog heading")
write(changelog_path, changelog)

static_path = ".github/scripts/test_issue565_transport_sweep_no_reward.py"
static = read(static_path)
static = replace_once(static, 'assert re.search(r"(?m)^//\\s*@version\\s+8\\.2\\.4$", source)', 'assert re.search(r"(?m)^//\\s*@version\\s+8\\.2\\.5$", source)', "static metadata assertion")
static = replace_once(static, "assert \"version: '8.2.4'\" in source", "assert \"version: '8.2.5'\" in source", "static runtime version assertion")
static = replace_once(
    static,
    '    assert "const patientRows = transportSweepOptionalReleasePatientRows();" in helper\n',
    '    assert "const patientRows = transportSweepOptionalReleasePatientRows();" in helper\n'
    '    assert "td:first-child" not in helper\n'
    '    assert "patientCells.find" in helper\n'
    '    assert "patientTextSource" in helper\n',
    "static real-row assertions",
)
static = replace_once(static, 'assert "## [8.2.4] - 2026-07-28" in CHANGELOG.read_text(encoding="utf-8")', 'assert "## [8.2.5] - 2026-07-28" in CHANGELOG.read_text(encoding="utf-8")', "static changelog assertion")
static = replace_once(static, 'print("Issue #565 v8.2.4 authoritative patient-row eligibility contract passed.")', 'print("Issue #565 v8.2.5 real multi-cell patient-row contract passed.")', "static completion message")
write(static_path, static)

runtime_path = ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs"
runtime = read(runtime_path)
runtime = replace_once(
    runtime,
    "      mission.innerHTML = '<table id=\"mission_vehicle_at_mission\"><tbody><tr id=\"vehicle_111\"><td><span class=\"building_list_fms building_list_fms_5\">5</span><a href=\"/vehicles/111\">ILB (ILB)</a></td><td>Station</td><td>Owner</td><td class=\"actions\"></td></tr></tbody></table>';",
    "      const vehicleLabel = options.vehicleLabel || \"ILB (ILB)\";\n"
    "      mission.innerHTML = `<table id=\"mission_vehicle_at_mission\"><tbody><tr id=\"vehicle_row_111\"><td><span class=\"building_list_fms building_list_fms_5\">5</span></td><td><a href=\"/vehicles/111\" vehicle_type_id=\"5\">${vehicleLabel}</a></td><td>Station</td><td>Owner</td><td class=\"actions\"></td></tr></tbody></table>`;",
    "runtime empty real-row fixture",
)
runtime = replace_once(
    runtime,
    '    mission.innerHTML = `<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_111" data-eligible="true"><td><span class="building_list_fms building_list_fms_5">5</span><a href="/vehicles/111">ILB (ILB)</a><br>Patient: ${names}</td><td>Station</td><td>Owner</td><td class="actions">${includeButton ? releaseLink("111") : ""}</td></tr></tbody></table>`;\n    const control = mission.querySelector(\'a[href="/vehicles/111/patient/-1"]\');',
    '    const vehicleLabel = options.vehicleLabel || "ILB (ILB)";\n'
    '    mission.innerHTML = `<table id="mission_vehicle_at_mission"><tbody><tr id="vehicle_row_111" data-eligible="true"><td><span class="building_list_fms building_list_fms_5">5</span></td><td><a href="/vehicles/111" vehicle_type_id="5">${vehicleLabel}</a><br>Patient: ${names}<small class="visible-xs"> (<a href="/profile/485821">CHESHIREFRS</a>)</small></td><td>Station</td><td>Owner</td><td class="actions">${includeButton ? releaseLink("111") : ""}</td></tr></tbody></table>`;\n'
    '    const renderedRow = mission.querySelector("#vehicle_row_111");\n'
    '    assert.doesNotMatch(String(renderedRow?.querySelector("td:first-child")?.textContent || ""), /Patient:/u, "FMS badge cell must not contain patient text");\n'
    '    assert.match(String(renderedRow?.textContent || ""), /Patient:/u, "authoritative row must contain patient text outside the first cell");\n'
    '    const control = mission.querySelector(\'a[href="/vehicles/111/patient/-1"]\');',
    "runtime live multi-cell patient fixture",
)
runtime = replace_once(
    runtime,
    '\n\n{\n  const harness = createHarness([1], { immediateButton: true, ownVehicleIds: ["111"] });',
    '\n\n{\n  const harness = createHarness([1, 0], { immediateButton: true, vehicleLabel: "Ambulance" });\n'
    '  const outcome = await harness.run();\n'
    '  assert.equal(outcome.cleared, 1, "real multi-cell ambulance row must release its patient");\n'
    '  assert.equal(harness.fetches.length, 1);\n'
    '}\n\n{\n  const harness = createHarness([1], { immediateButton: true, ownVehicleIds: ["111"] });',
    "runtime ambulance fixture",
)
runtime = replace_once(
    runtime,
    'console.log("Issue #565 v8.2.4 patient-row runtime passed: ILB eligibility, duplicate clone preference, own exclusion, delayed controls and same-vehicle 3→2→1→0.");',
    'console.log("Issue #565 v8.2.5 real-row runtime passed: multi-cell FMS badge separation, ILB and ambulance eligibility, owner markup, duplicate clone preference, own exclusion, delayed controls and same-vehicle 3→2→1→0.");',
    "runtime completion message",
)
write(runtime_path, runtime)

issue_doc = """# Issue #565 — Patient Transport Sweep no-reward release path

Toolkit v8.2.5 recognises the real MissionChief multi-cell FMS 5 vehicle-row structure.

The FMS badge can occupy its own first table cell while the vehicle link and `Patient:` text are rendered in another cell. Patient discovery therefore locates the authoritative cell containing `Patient:` anywhere in the row instead of assuming the first cell contains both status and patient data.

The exact visible same-origin `Release patient (No reward)` control remains required. Own vehicles remain excluded from the verified personal vehicle set. Row and top-alert control clones are deduplicated by vehicle ID, with the authoritative row control preferred when patient-count context is available.

Delayed mission rows, delayed controls, completed requests, repeated same-vehicle releases, cancellation, allowance, failed-request handling and the native MissionChief discharge fallback remain preserved. No persistent observer, interval, additional request site or Toolkit-managed timer is added.
"""
write("docs/issue-565-transport-sweep-no-reward.md", issue_doc)

help_manifest_path = "help/manifest.json"
help_manifest = json.loads(read(help_manifest_path))
help_manifest["guideVersion"] = "8.2.5"
help_manifest["toolkitVersion"] = "8.2.5"
help_manifest["runtimeGuidePatch"] = "Toolkit v8.2.5 recognises MissionChief's real multi-cell FMS 5 patient rows, locating Patient text outside the status-badge cell while preserving exact no-reward control verification."
write(help_manifest_path, json.dumps(help_manifest, indent=2) + "\n")

help_path = "help/index.html"
help_text = read(help_path)
if "Toolkit v8.2.4" in help_text:
    help_text = help_text.replace("Toolkit v8.2.4", "Toolkit v8.2.5")
if "Guide for Toolkit v8.2.4" in help_text:
    help_text = help_text.replace("Guide for Toolkit v8.2.4", "Guide for Toolkit v8.2.5")
write(help_path, help_text)

# Update the exact source-size/hash headroom fixture after the userscript correction.
fixture_path = ".github/fixtures/main-style-source-headroom.json"
fixture = json.loads(read(fixture_path))
text = read(source_path)
start = text.index("function installMainStyles()")
template_start = text.index("addStyle(`", start) + len("addStyle(`")
metric = text.index("recordStartupMetric('stylesheetInstallMs'", template_start)
template_end = text.rfind("`);", template_start, metric)
raw = text[template_start:template_end]
lines = raw.split("\n")
canonical = re.sub(
    r"\n[\t ]*}",
    "}",
    "\n".join(
        line
        for index, line in enumerate(lines)
        if not (0 < index < len(lines) - 1 and not line.strip())
    ),
)
source_bytes = len(text.encode())
source_lines = len(text.splitlines())
source_hash = hashlib.sha256(text.encode()).hexdigest()
candidate = fixture["v8Candidate"]
previous_bytes = int(candidate["sourceBytes"])
previous_lines = int(candidate["sourceLines"])
candidate.update({
    "issue": 565,
    "version": "8.2.5",
    "sourceBytes": source_bytes,
    "sourceLines": source_lines,
    "sourceSha256": source_hash,
    "templateBytes": len(raw.encode()),
    "templateLines": len(lines),
    "templateSha256": hashlib.sha256(raw.encode()).hexdigest(),
    "canonicalCssSha256": hashlib.sha256(canonical.encode()).hexdigest(),
    "maxSourceBytes": source_bytes + 20000,
    "maxSourceLines": source_lines + 250,
    "baseline": "8.2.4",
    "scope": "Issue #565 real MissionChief multi-cell FMS 5 patient-row parsing and browser-faithful regression",
})
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + (source_bytes - previous_bytes)
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + (source_lines - previous_lines)
write(fixture_path, json.dumps(fixture, indent=2) + "\n")

print(json.dumps({
    "version": "8.2.5",
    "sourceBytes": source_bytes,
    "sourceLines": source_lines,
    "sourceSha256": source_hash,
    "fix": "real multi-cell FMS 5 patient row",
}, indent=2))
