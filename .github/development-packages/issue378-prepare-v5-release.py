#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
ROOT_USER = ROOT / "MissionChief_Map_Command_Toolkit.user.js"
ROOT_TXT = ROOT / "MissionChief_Map_Command_Toolkit.txt"
CHANGELOG = ROOT / "CHANGELOG.md"
HEADROOM = ROOT / ".github" / "fixtures" / "main-style-source-headroom.json"
VALIDATOR = ROOT / ".github" / "scripts" / "validate_userscript.py"
PREFLIGHT = ROOT / ".github" / "scripts" / "run_userscript_preflight.sh"
BUNDLE = ROOT / ".github" / "scripts" / "prepare_release_bundle.py"
CURRENT_VERSION = "4.20.37"
RELEASE_VERSION = "5.0.0"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

source = SOURCE.read_text(encoding="utf-8")
metadata_pattern = re.compile(r"^(//\s*@version\s+)" + re.escape(CURRENT_VERSION) + r"\s*$", re.MULTILINE)
source, metadata_count = metadata_pattern.subn(r"\g<1>" + RELEASE_VERSION, source)
if metadata_count != 1:
    raise RuntimeError(f"userscript metadata version count changed: {metadata_count}")
runtime_pattern = re.compile(
    r"(\bconst\s+SCRIPT\s*=\s*\{\s*name\s*:\s*['\"][^'\"]+['\"]\s*,\s*version\s*:\s*['\"])"
    + re.escape(CURRENT_VERSION)
    + r"(['\"])",
    re.DOTALL,
)
source, runtime_count = runtime_pattern.subn(r"\g<1>" + RELEASE_VERSION + r"\g<2>", source)
if runtime_count != 1:
    raise RuntimeError(f"runtime SCRIPT.version count changed: {runtime_count}")
if CURRENT_VERSION in source[:12000]:
    raise RuntimeError("old version survived userscript metadata/runtime header")

for path in (SOURCE, ROOT_USER, ROOT_TXT):
    path.write_text(source, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
release_heading = f"## [{RELEASE_VERSION}] - 2026-07-23"
if release_heading in changelog:
    raise RuntimeError("v5.0.0 changelog heading already exists")
anchor = "## [Unreleased]\n"
if changelog.count(anchor) != 1:
    raise RuntimeError("Unreleased changelog anchor drifted")
notes = f'''\n{release_heading}\n\n### Major operational-window replacement\n- Replaced the legacy Mission Requirements Matrix with a Toolkit-native operational suite built from the authorised LSSM Extended Call Window, Extended Call List and Enhanced Transport Requests behaviour.\n- Added one versioned `operationalWindow` settings model, one lifecycle coordinator per active document, coalesced rendering and deterministic teardown across MissionChief navigation.\n- Migrated the former Matrix preference once into the new requirements setting and permanently retired the old parser, panel, observers, scheduler and toggle.\n\n### Enhanced mission requirements\n- Added a fixture-first requirements engine covering vehicle, equipment, personnel, conditional, capacity, trailer and tractive requirements.\n- Added selected, en-route and on-scene reconciliation, water/foam/pump progress, unresolved-text preservation and immutable render fingerprints.\n- Added a responsive normal-flow requirements surface for Desktop, Tablet and iOS, with LSSM coexistence detection to prevent duplicate panels.\n\n### Extended Call Window\n- Added patient and vehicle summaries, selected-unit and ARR counters, generation/alarm information, collapsible patient and vehicle areas, permanent vehicle and ARR search, mission keyword badges, map-centre controls and ARR highlighting.\n- Added sticky headers, vehicle-type badges and mobile safe-area handling without creating a second mission-window lifecycle.\n\n### Extended Call List\n- Added mission sorting, starring, collapsing, patient/prisoner/credit/time badges and native share controls.\n- Preserved deterministic ordering and state across live list refreshes while remaining compatible with MissionChief and equivalent LSSM modules.\n\n### Enhanced Transport Requests\n- Added opt-in transport automation with strict route validation, visible/enabled candidate filtering, single-candidate ambiguity rejection and per-route idempotency tokens.\n- Kept automatic transport opening disabled by default; successful vehicle transport controls retain their reviewed safe default.\n\n### Performance and validation\n- Reduced total observer constructions from twelve to eleven and broad subtree observers from ten to nine compared with v4.20.37.\n- Held direct MutationObserver, `getElementById` and `innerHTML` metrics at their existing release ceilings while reducing source bytes, selectors, managed timers, listeners and observer trackers.\n- Added deterministic engine, renderer, runtime, Matrix-retirement, structural, performance and mobile compatibility contracts.\n\n### Upgrade compatibility\n- Existing Toolkit settings are retained. The former Matrix enablement preference is migrated automatically; no manual reset is required.\n- The operational suite supports Desktop, Tablet and iOS/Safari and suppresses equivalent Toolkit surfaces when the matching LSSM module is active.\n'''
changelog = changelog.replace(anchor, anchor + notes, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

fixture = json.loads(HEADROOM.read_text(encoding="utf-8"))
if fixture.get("candidateVersion") != CURRENT_VERSION:
    raise RuntimeError(f"source-headroom candidate version drifted: {fixture.get('candidateVersion')}")
fixture["candidateVersion"] = RELEASE_VERSION
HEADROOM.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

subprocess.run(["python3", str(VALIDATOR)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["node", "--check", str(SOURCE)], cwd=ROOT, env=ENV, check=True)
subprocess.run(["bash", str(PREFLIGHT), "--contracts"], cwd=ROOT, env=ENV, check=True)
subprocess.run(["python3", str(BUNDLE), RELEASE_VERSION, "dry-run"], cwd=ROOT, env=ENV, check=True)
manifest = json.loads((ROOT / "release-bundle" / f"release-manifest-v{RELEASE_VERSION}.json").read_text(encoding="utf-8"))
if manifest.get("version") != RELEASE_VERSION or manifest.get("releaseTag") != f"v{RELEASE_VERSION}":
    raise RuntimeError("v5.0.0 dry-run release bundle metadata is invalid")
shutil.rmtree(ROOT / "release-bundle", ignore_errors=True)

current = Path(__file__).resolve()
for path in (ROOT / ".github" / "development-packages").glob("issue378-*.py"):
    if path.resolve() != current:
        path.unlink(missing_ok=True)
for path in (ROOT / ".github" / "diagnostics").glob("issue378-*.txt"):
    path.unlink(missing_ok=True)

print("MissionChief Map Command Toolkit v5.0.0 release candidate prepared and dry-run bundle verified.")
