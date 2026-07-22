#!/usr/bin/env python3
from pathlib import Path

package = Path(__file__).with_name('issue332-mission-monitoring-toggles-v42032.py')
source = package.read_text(encoding='utf-8')
old = '    """    mission_monitoring_toggle_routes = values('
new = '    r"""    mission_monitoring_toggle_routes = values('
if source.count(old) != 1:
    raise RuntimeError('Expected exactly one generated monitoring-route string')
corrected = source.replace(old, new, 1)
namespace = {'__file__': str(package), '__name__': '__main__'}
exec(compile(corrected, str(package), 'exec'), namespace)
package.unlink()
