#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github" / "development-packages" / "issue-167-live-capacity.py"

script = ORIGINAL.read_text(encoding="utf-8")
old = '''runtime = replace_once(runtime, "    missionRoot.enRouteRows = [];", "    missionRoot.enRouteRows = [];\\n    missionRoot.onSiteRows = [];", "mission candidate on-site store")
runtime = replace_once(runtime, "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;", "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;\\n        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;", "mission candidate on-site selector")
runtime = replace_once(runtime, "    missionRoot.enRouteRows = [];", "    missionRoot.enRouteRows = [];\\n    missionRoot.onSiteRows = [];", "source-less candidate on-site store")
runtime = replace_once(runtime, "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;", "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;\\n        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;", "source-less candidate on-site selector")'''
new = '''if runtime.count("    missionRoot.enRouteRows = [];") != 2:
    raise AssertionError("mission candidate on-site stores: expected two anchors")
runtime = runtime.replace("    missionRoot.enRouteRows = [];", "    missionRoot.enRouteRows = [];\\n    missionRoot.onSiteRows = [];", 2)
if runtime.count("        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;") != 2:
    raise AssertionError("mission candidate on-site selectors: expected two anchors")
runtime = runtime.replace("        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;", "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;\\n        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;", 2)'''
if script.count(old) != 1:
    raise AssertionError(f"fixture replacement block: expected one match, found {script.count(old)}")
script = script.replace(old, new, 1)
namespace = {"__file__": str(ORIGINAL), "__name__": "__main__"}
exec(compile(script, str(ORIGINAL), "exec"), namespace)
ORIGINAL.unlink(missing_ok=True)
