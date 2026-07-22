#!/usr/bin/env python3
from pathlib import Path

package = Path(__file__).with_name('issue332-mission-monitoring-toggles-v42032.py')
source = package.read_text(encoding='utf-8')
old = "reconcile_marker = '        reconcileFeatureRefreshes(feature);'"
new = "reconcile_marker = '        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });'"
if source.count(old) != 1:
    raise RuntimeError('Expected exactly one outdated reconciliation marker in the reviewed package')
corrected = source.replace(old, new, 1)
namespace = {'__file__': str(package), '__name__': '__main__'}
exec(compile(corrected, str(package), 'exec'), namespace)
package.unlink()
