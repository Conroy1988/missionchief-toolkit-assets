from pathlib import Path

source_path = Path('src/MissionChief_Map_Command_Toolkit.user.js')
test_path = Path('.github/scripts/test_desktop_panel_layout_contract.py')
source = source_path.read_text(encoding='utf-8')
test = test_path.read_text(encoding='utf-8')
old_css = '''        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} {
            max-height: var(--mcms-desktop-panel-max-height, calc(100vh - 24px)) !important;
            overflow: hidden !important;
'''
new_css = '''        html[data-mcms-device-layout="desktop"] #${SCRIPT.panelId} {
            box-sizing: border-box !important;
            max-height: var(--mcms-desktop-panel-max-height, calc(100vh - 24px)) !important;
            overflow: hidden !important;
'''
if source.count(old_css) != 1:
    raise RuntimeError(f'Expected one Desktop panel shell rule, found {source.count(old_css)}')
source = source.replace(old_css, new_css, 1)
old_test = "        'flex-direction: column !important',\n"
new_test = "        'flex-direction: column !important',\n        'box-sizing: border-box !important',\n"
if test.count(old_test) != 1:
    raise RuntimeError(f'Expected one static contract insertion point, found {test.count(old_test)}')
test = test.replace(old_test, new_test, 1)
source_path.write_text(source, encoding='utf-8')
test_path.write_text(test, encoding='utf-8')
