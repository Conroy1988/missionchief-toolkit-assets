#!/usr/bin/env python3
from pathlib import Path

package = Path(__file__).with_name('issue332-mission-monitoring-toggles-v42032.py')
source = package.read_text(encoding='utf-8')
old = '    """    mission_monitoring_toggle_routes = values('
new = '    r"""    mission_monitoring_toggle_routes = values('
if source.count(old) != 1:
    raise RuntimeError('Expected exactly one generated monitoring-route string')
corrected = source.replace(old, new, 1)
old_threshold = '"Stuck detector on · 15 min"'
new_threshold = '"Stuck detector on · 20 min"'
if corrected.count(old_threshold) != 1:
    raise RuntimeError('Expected exactly one stale Stuck Detector threshold assertion')
corrected = corrected.replace(old_threshold, new_threshold, 1)
namespace = {'__file__': str(package), '__name__': '__main__'}
exec(compile(corrected, str(package), 'exec'), namespace)
package.unlink()
