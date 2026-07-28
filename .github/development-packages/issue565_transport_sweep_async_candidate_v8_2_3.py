#!/usr/bin/env python3
"""Apply v8.2.3 Patient Transport Sweep async-candidate correction."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward_runtime.mjs"
STATIC_TEST = ROOT / ".github/scripts/test_issue565_transport_sweep_no_reward.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DOC = ROOT / "docs/issue-565-transport-sweep-no-reward.md"
HELP = ROOT / "help/index.html"
HELP_MANIFEST = ROOT / "help/manifest.json"
HEADROOM = ROOT / ".github/fixtures/main-style-source-headroom.json"

source = SOURCE.read_text(encoding="utf-8")
if not re.search(r"(?m)^//\s*@version\s+8\.2\.2$", source):
    raise RuntimeError("Expected v8.2.2 canonical source")
old = "        const candidates = collectTransportSweepVehicleCandidatesForMission(missionId) || [];"
new = "        const candidates = collectTransportSweepVehicleCandidates();"
if source.count(old) != 1:
    raise RuntimeError(f"Expected one async candidate misuse, found {source.count(old)}")
source = source.replace(old, new, 1)
source = re.sub(r"(?m)^//\s*@version\s+8\.2\.2$", "// @version      8.2.3", source, count=1)
source = source.replace("version: '8.2.2'", "version: '8.2.3'", 1)
SOURCE.write_text(source, encoding="utf-8")

runtime = RUNTIME_TEST.read_text(encoding="utf-8")
old_stub = '''    collectTransportSweepVehicleCandidatesForMission() {
      return Array.from(dom.window.document.querySelectorAll('tr[data-eligible="true"]')).map(row => ({
        vehicleId: row.id.match(/\\d+$/u)?.[0] || "",
      }));
    },
'''
new_stub = '''    collectTransportSweepVehicleCandidates() {
      return Array.from(dom.window.document.querySelectorAll('tr[data-eligible="true"]')).map(row => ({
        vehicleId: row.id.match(/\\d+$/u)?.[0] || "",
      }));
    },
    async collectTransportSweepVehicleCandidatesForMission() {
      throw new Error("optional release state must not consume an async candidate Promise");
    },
'''
if runtime.count(old_stub) != 1:
    raise RuntimeError("Unable to replace synchronous test double")
runtime = runtime.replace(old_stub, new_stub, 1)
runtime = runtime.replace(
    'console.log("Issue #565 v8.2.2 mission-readiness runtime passed: deferred controls, completed requests, same-vehicle 3→2→1→0, allowance, failure, no-control and cancellation.");',
    'console.log("Issue #565 v8.2.3 async-candidate runtime passed: real synchronous DOM eligibility, deferred controls, completed requests and same-vehicle 3→2→1→0.");',
)
RUNTIME_TEST.write_text(runtime, encoding="utf-8")

static = STATIC_TEST.read_text(encoding="utf-8")
static = static.replace(r"^//\s*@version\s+8\.2\.2$", r"^//\s*@version\s+8\.2\.3$", 1)
static = static.replace("version: '8.2.2'", "version: '8.2.3'", 1)
marker = '    assert "latest.missionReady" in helper\n'
addition = marker + '    assert "const candidates = collectTransportSweepVehicleCandidates();" in helper\n    assert "collectTransportSweepVehicleCandidatesForMission(missionId)" not in helper\n'
if static.count(marker) != 1:
    raise RuntimeError("Unable to extend static async boundary contract")
static = static.replace(marker, addition, 1)
static = static.replace('assert "## [8.2.2] - 2026-07-28"', 'assert "## [8.2.3] - 2026-07-28"', 1)
static = static.replace(
    'print("Issue #565 v8.2.2 mission-readiness Transport Sweep contract passed.")',
    'print("Issue #565 v8.2.3 synchronous DOM eligibility contract passed.")',
    1,
)
STATIC_TEST.write_text(static, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = '''## [8.2.3] - 2026-07-28

### Patient Transport Sweep — synchronous live eligibility

- Fixed the optional release path consuming the asynchronous mission-candidate collector without awaiting it.
- Uses the live synchronous mission-window candidate collector while waiting for the delayed release control.
- Prevents visible verified release buttons from being filtered out by an empty Promise-derived eligibility set.
- Replaces the concealed synchronous test double with the real async boundary and fails if the optional path touches it.
- Adds no observer, interval, request site or Toolkit-managed timer.

'''
if "## [8.2.3]" not in changelog:
    changelog = changelog.replace("# Changelog\n\n", "# Changelog\n\n" + entry, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

doc = DOC.read_text(encoding="utf-8")
doc = doc.replace("Toolkit v8.2.2", "Toolkit v8.2.3", 1)
doc += "\nToolkit v8.2.3 additionally corrects the eligibility boundary: optional release discovery now uses the synchronous live mission-window candidate collector. The asynchronous HTML recovery collector is reserved for the later native fallback and is never converted into an empty eligibility set.\n"
DOC.write_text(doc, encoding="utf-8")

help_text = HELP.read_text(encoding="utf-8").replace("v8.2.2", "v8.2.3")
HELP.write_text(help_text, encoding="utf-8")
help_manifest = json.loads(HELP_MANIFEST.read_text(encoding="utf-8"))
help_manifest["guideVersion"] = "8.2.3"
help_manifest["toolkitVersion"] = "8.2.3"
help_manifest["runtimeGuidePatch"] = "Toolkit v8.2.3 uses synchronous live mission-window eligibility while waiting for delayed no-reward controls, preventing Promise-derived empty candidate sets from rejecting visible buttons."
HELP_MANIFEST.write_text(json.dumps(help_manifest, indent=2) + "\n", encoding="utf-8")

source_bytes = SOURCE.read_bytes()
sha = hashlib.sha256(source_bytes).hexdigest()
lines = len(source_bytes.decode("utf-8").splitlines())
for relative in ["dist/MissionChief_Map_Command_Toolkit.user.js", "dist/MissionChief_Map_Command_Toolkit.txt"]:
    (ROOT / relative).write_bytes(source_bytes)
(ROOT / "dist/SHA256SUMS.txt").write_text(
    f"{sha}  MissionChief_Map_Command_Toolkit.user.js\n{sha}  MissionChief_Map_Command_Toolkit.txt\n",
    encoding="utf-8",
)
manifest_path = ROOT / "dist/release-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.update({"version": "8.2.3", "sha256": sha, "bytes": len(source_bytes), "lines": lines})
manifest["metadata"]["runtimeVersion"] = "8.2.3"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

headroom = json.loads(HEADROOM.read_text(encoding="utf-8"))
candidate = headroom["v8Candidate"]
old_bytes = int(candidate["sourceBytes"])
old_lines = int(candidate["sourceLines"])
candidate.update({
    "issue": 565,
    "version": "8.2.3",
    "sourceBytes": len(source_bytes),
    "sourceLines": lines,
    "sourceSha256": sha,
    "baseline": "8.2.2",
    "scope": "Issue #565 synchronous live mission-window eligibility for delayed no-reward release controls",
})
candidate["maxSourceBytes"] = max(int(candidate.get("maxSourceBytes", 0)), len(source_bytes) + 20000)
candidate["maxSourceLines"] = max(int(candidate.get("maxSourceLines", 0)), lines + 250)
approved = candidate.setdefault("approvedGrowth", {})
approved["sourceBytes"] = int(approved.get("sourceBytes", 0)) + len(source_bytes) - old_bytes
approved["sourceLines"] = int(approved.get("sourceLines", 0)) + lines - old_lines
HEADROOM.write_text(json.dumps(headroom, indent=2) + "\n", encoding="utf-8")

print(f"v8.2.3 async-candidate correction applied: {sha}, {len(source_bytes)} bytes, {lines} lines")
