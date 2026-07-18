#!/usr/bin/env python3
from pathlib import Path
import runpy
import traceback

root = Path(__file__).resolve().parents[2]
package = root / '.github/development-packages/issue-181-patient-ambulance-demand.py'
output = root / '.github/diagnostics/issue-181-package-result.txt'
text = package.read_text(encoding='utf-8')
old = '''source = replace_once(
    source,
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "#missing_text, [data-mcms-requirements-anchor], #patient_button_form, #patient_button_text, #patient_button_text strong, [data-patient-count], [data-patient-total], [data-patients], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "record patient mutation selectors",
)
source = replace_once(
    source,
    "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "#missing_text, [data-mcms-requirements-anchor], #patient_button_form, #patient_button_text, #patient_button_text strong, [data-patient-count], [data-patient-total], [data-patients], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all",
    "document patient activity selectors",
)'''
new = '''patient_selector_old = "#missing_text, [data-mcms-requirements-anchor], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all"
patient_selector_new = "#missing_text, [data-mcms-requirements-anchor], #patient_button_form, #patient_button_text, #patient_button_text strong, [data-patient-count], [data-patient-total], [data-patients], #mission_vehicle_driving, #mission_vehicle_at_mission, #vehicle_show_table_body_all"
if source.count(patient_selector_old) != 2:
    raise AssertionError(f"patient mutation selectors: expected two matches, found {source.count(patient_selector_old)}")
source = source.replace(patient_selector_old, patient_selector_new, 2)'''
if text.count(old) != 1:
    raise AssertionError(f'Expected one dual-selector package block, found {text.count(old)}')
package.write_text(text.replace(old, new, 1), encoding='utf-8')
output.unlink(missing_ok=True)
try:
    runpy.run_path(str(package), run_name='__main__')
except BaseException:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(traceback.format_exc(), encoding='utf-8')
    print(output.relative_to(root))
