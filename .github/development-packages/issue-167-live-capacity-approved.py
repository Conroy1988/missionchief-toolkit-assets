#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_COMMIT = '19759e9d0684a35e69de42ff14a20e32f131c472'
ORIGINAL_REL = '.github/development-packages/issue-167-live-capacity.py'
DIAGNOSTIC = ROOT / 'docs' / 'diagnostics' / 'issue-167-final-error.txt'

script = subprocess.check_output(
    ['git', 'show', f'{ORIGINAL_COMMIT}:{ORIGINAL_REL}'],
    cwd=ROOT,
    text=True,
)

spacing_old = '    return text[:start] + replacement.rstrip() + "\\n" + text[next_function + 1:]'
spacing_new = '    return text[:start] + replacement.rstrip() + "\\n\\n" + text[next_function + 1:]'
if script.count(spacing_old) != 1:
    raise AssertionError(f'function spacing helper: expected one match, found {script.count(spacing_old)}')
script = script.replace(spacing_old, spacing_new, 1)

runtime_old = '''runtime = replace_once(runtime, "    missionRoot.enRouteRows = [];", "    missionRoot.enRouteRows = [];\\n    missionRoot.onSiteRows = [];", "mission candidate on-site store")
runtime = replace_once(runtime, "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;", "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;\\n        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;", "mission candidate on-site selector")
runtime = replace_once(runtime, "    missionRoot.enRouteRows = [];", "    missionRoot.enRouteRows = [];\\n    missionRoot.onSiteRows = [];", "source-less candidate on-site store")
runtime = replace_once(runtime, "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;", "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;\\n        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;", "source-less candidate on-site selector")'''
runtime_new = '''if runtime.count("    missionRoot.enRouteRows = [];") != 2:
    raise AssertionError("mission candidate on-site stores: expected two anchors")
runtime = runtime.replace("    missionRoot.enRouteRows = [];", "    missionRoot.enRouteRows = [];\\n    missionRoot.onSiteRows = [];", 2)
if runtime.count("        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;") != 2:
    raise AssertionError("mission candidate on-site selectors: expected two anchors")
runtime = runtime.replace("        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;", "        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;\\n        if (selector === '#mission_vehicle_at_mission tbody tr') return missionRoot.onSiteRows;", 2)'''
if script.count(runtime_old) != 1:
    raise AssertionError(f'runtime fixture patch: expected one block, found {script.count(runtime_old)}')
script = script.replace(runtime_old, runtime_new, 1)

observer_old = '''source = replace_once(
    source,
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #vehicle_show_table_body_all",
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "on-site mutation observation",
)'''
observer_new = '''observer_anchor = "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #vehicle_show_table_body_all"
observer_replacement = "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all"
if source.count(observer_anchor) != 2:
    raise AssertionError(f"on-site mutation observation: expected two matches, found {source.count(observer_anchor)}")
source = source.replace(observer_anchor, observer_replacement, 2)'''
if script.count(observer_old) != 1:
    raise AssertionError(f'observer patch: expected one block, found {script.count(observer_old)}')
script = script.replace(observer_old, observer_new, 1)

namespace = {
    '__file__': str(ROOT / ORIGINAL_REL),
    '__name__': '__main__',
}
exec(compile(script, str(ROOT / ORIGINAL_REL), 'exec'), namespace)
DIAGNOSTIC.unlink(missing_ok=True)
try:
    DIAGNOSTIC.parent.rmdir()
except OSError:
    pass
