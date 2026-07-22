#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import traceback

package = Path(__file__).with_name('issue332-mission-monitoring-toggles-v42032.py')
source = package.read_text(encoding='utf-8')
old = "reconcile_marker = '        reconcileFeatureRefreshes(feature);'"
new = "reconcile_marker = '        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });'"
if source.count(old) != 1:
    raise RuntimeError('Expected exactly one outdated reconciliation marker in the reviewed package')
corrected = source.replace(old, new, 1)
try:
    namespace = {'__file__': str(package), '__name__': '__main__'}
    exec(compile(corrected, str(package), 'exec'), namespace)
except Exception:
    details = traceback.format_exc()
    body = '## Issue #332 package diagnostic\n\n```text\n' + details[-12000:] + '\n```'
    repository = os.environ.get('GITHUB_REPOSITORY', 'Conroy1988/missionchief-toolkit-assets')
    issue = os.environ.get('ISSUE_NUMBER', '332')
    subprocess.run(['gh', 'api', f'repos/{repository}/issues/{issue}/comments', '-f', f'body={body}'], check=False)
    raise
raise RuntimeError('Diagnostic wrapper completed without reproducing the package failure')
