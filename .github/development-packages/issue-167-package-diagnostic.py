#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_REL = Path('.github/development-packages/issue-167-live-capacity.py')
V2_REL = Path('.github/development-packages/issue-167-live-capacity-v2.py')
OUTPUT = ROOT / 'docs' / 'diagnostics' / 'issue-167-package-error.txt'

with tempfile.TemporaryDirectory(prefix='mcms-issue-167-') as temp_dir:
    work = Path(temp_dir) / 'repo'
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    original = work / ORIGINAL_REL
    script = original.read_text(encoding='utf-8')
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
        result_text = f'Wrapper patch mismatch: expected one block, found {script.count(old)}\n'
    else:
        original.write_text(script.replace(old, new, 1), encoding='utf-8')
        completed = subprocess.run(
            ['python3', str(ORIGINAL_REL)],
            cwd=work,
            text=True,
            capture_output=True,
        )
        result_text = '\n'.join([
            f'Return code: {completed.returncode}',
            '',
            '--- STDOUT ---',
            completed.stdout,
            '--- STDERR ---',
            completed.stderr,
        ])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(result_text, encoding='utf-8')
(ROOT / ORIGINAL_REL).unlink(missing_ok=True)
(ROOT / V2_REL).unlink(missing_ok=True)
subprocess.run(['node', '--check', 'src/MissionChief_Map_Command_Toolkit.user.js'], cwd=ROOT, check=True)
print(f'Issue #167 isolated package diagnostic written to {OUTPUT.relative_to(ROOT)}')
