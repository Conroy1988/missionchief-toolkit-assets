#!/usr/bin/env python3
from pathlib import Path
import runpy
import traceback

root = Path(__file__).resolve().parents[2]
package = root / '.github/development-packages/issue-181-patient-ambulance-demand.py'
output = root / '.github/diagnostics/issue-181-package-result.txt'
try:
    text = package.read_text(encoding='utf-8')
    helper_anchor = '''def regex_once(text: str, pattern: str, replacement: str, label: str) -> str:'''
    helper = '''def replace_first(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise AssertionError(f"{label}: match not found")
    return text.replace(old, new, 1)


'''
    if 'def replace_first(' not in text:
        if text.count(helper_anchor) != 1:
            raise AssertionError(f'Expected one helper insertion anchor, found {text.count(helper_anchor)}')
        text = text.replace(helper_anchor, helper + helper_anchor, 1)
    selector_call = '''source = replace_once(
    source,
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",'''
    if text.count(selector_call) != 2:
        raise AssertionError(f'Expected two selector calls, found {text.count(selector_call)}')
    text = text.replace(selector_call, selector_call.replace('replace_once', 'replace_first'), 2)
    package.write_text(text, encoding='utf-8')
    output.unlink(missing_ok=True)
    runpy.run_path(str(package), run_name='__main__')
except BaseException:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(traceback.format_exc(), encoding='utf-8')
    print(output.relative_to(root))
