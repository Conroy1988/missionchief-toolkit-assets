#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_COMMIT = '19759e9d0684a35e69de42ff14a20e32f131c472'
ORIGINAL_REL = Path('.github/development-packages/issue-167-live-capacity.py')
OUTPUT = ROOT / 'docs' / 'diagnostics' / 'issue-167-approved-error.txt'

script = subprocess.check_output(['git', 'show', f'{ORIGINAL_COMMIT}:{ORIGINAL_REL.as_posix()}'], cwd=ROOT, text=True)
spacing_old = '    return text[:start] + replacement.rstrip() + "\\n" + text[next_function + 1:]'
spacing_new = '    return text[:start] + replacement.rstrip() + "\\n\\n" + text[next_function + 1:]'
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
for old, new, label in ((spacing_old, spacing_new, 'spacing'), (runtime_old, runtime_new, 'runtime'), (observer_old, observer_new, 'observer')):
    if script.count(old) != 1:
        raise AssertionError(f'{label} patch expected one match, found {script.count(old)}')
    script = script.replace(old, new, 1)

with tempfile.TemporaryDirectory(prefix='mcms-issue-167-approved-') as temp_dir:
    work = Path(temp_dir) / 'repo'
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    original = work / ORIGINAL_REL
    original.parent.mkdir(parents=True, exist_ok=True)
    original.write_text(script, encoding='utf-8')
    completed = subprocess.run(['python3', str(ORIGINAL_REL)], cwd=work, text=True, capture_output=True)
    status = subprocess.run(['git', 'diff', '--no-index', '/dev/null', '/dev/null'], cwd=work, text=True, capture_output=True)
    candidate_checks = []
    for path in (
        '.github/scripts/validate_userscript.py',
        '.github/scripts/validate_canonical_userscript.py',
        '.github/scripts/validate_release.py',
    ):
        candidate = work / path
        if candidate.exists():
            check = subprocess.run(['python3', path], cwd=work, text=True, capture_output=True)
            candidate_checks.append('\n'.join([f'CHECK {path}: {check.returncode}', check.stdout, check.stderr]))
    result_text = '\n'.join([
        f'Package return code: {completed.returncode}',
        '',
        '--- PACKAGE STDOUT ---',
        completed.stdout,
        '--- PACKAGE STDERR ---',
        completed.stderr,
        '--- CANDIDATE CHECKS ---',
        '\n'.join(candidate_checks) if candidate_checks else 'No named candidate validator found.',
        '--- MODIFIED FILES ---',
        subprocess.run(['find', '.', '-type', 'f', '-newer', str(original)], cwd=work, text=True, capture_output=True).stdout,
    ])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(result_text, encoding='utf-8')
for stale in (
    ROOT / '.github' / 'development-packages' / 'issue-167-live-capacity-approved.py',
    ROOT / 'docs' / 'diagnostics' / 'issue-167-final-error.txt',
):
    stale.unlink(missing_ok=True)
subprocess.run(['node', '--check', 'src/MissionChief_Map_Command_Toolkit.user.js'], cwd=ROOT, check=True)
print(f'Issue #167 approved diagnostic written to {OUTPUT.relative_to(ROOT)}')
