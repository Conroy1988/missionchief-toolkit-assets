#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
S = R / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
F = R / '.github' / 'fixtures' / 'settings-ui-contract.json'
T = R / '.github' / 'scripts' / 'test_settings_ui_contract.py'
H = R / '.github' / 'fixtures' / 'main-style-source-headroom.json'
OLD = '4.20.30'
NEW = '4.20.31'


def x(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{name}: expected 1 occurrence, found {count}')
    return text.replace(old, new, 1)


source = S.read_text(encoding='utf-8')
source = x(source, f'// @version      {OLD}', f'// @version      {NEW}', 'metadata version')
source = x(source, f"version: '{OLD}'", f"version: '{NEW}'", 'runtime version')
old_router = """    function handleSettingChange(target) {
        const setting = target.dataset.setting;
        if (!setting) return;
        if (setting === 'mobile-mode' || setting === 'tablet-mode') {
            const nextValue = ['auto', 'on', 'off'].includes(String(target.value)) ? String(target.value) : 'auto';
            const previousLayout = activeDeviceLayout;
            if (setting === 'mobile-mode') {
                state.mobileMode = nextValue;
                if (nextValue === 'on') state.tabletMode = 'off';
            } else {
                state.tabletMode = nextValue;
                if (nextValue === 'on') state.mobileMode = 'off';
            }
            saveState();
            applyRootAttributes();
            refreshTabletModeUi();
            if (previousLayout !== activeDeviceLayout && !isTouchLayoutActive()) {
                clearTabletPanelSizing();
                clearTabletDockSizing();
            }
            fitControlToMap();
            positionPanelOverlay(true);
            showToast(activeDeviceLayout === 'mobile' ? 'iOS Mobile Mode active' : activeDeviceLayout === 'tablet' ? 'Tablet Mode active' : 'Desktop layout active');
            return;
        }
"""
new_router = """    function handleDeviceLayoutSettingChange(target, setting) {
        const nextValue = ['auto', 'on', 'off'].includes(String(target.value)) ? String(target.value) : 'auto';
        const previousLayout = activeDeviceLayout;
        if (setting === 'mobile-mode') {
            state.mobileMode = nextValue;
            if (nextValue === 'on') state.tabletMode = 'off';
        } else if (setting === 'tablet-mode') {
            state.tabletMode = nextValue;
            if (nextValue === 'on') state.mobileMode = 'off';
        } else return false;
        saveState();
        applyRootAttributes();
        refreshTabletModeUi();
        if (previousLayout !== activeDeviceLayout && !isTouchLayoutActive()) {
            clearTabletPanelSizing();
            clearTabletDockSizing();
        }
        fitControlToMap();
        positionPanelOverlay(true);
        showToast(activeDeviceLayout === 'mobile' ? 'iOS Mobile Mode active' : activeDeviceLayout === 'tablet' ? 'Tablet Mode active' : 'Desktop layout active');
        return true; }
    function handleSettingChange(target) {
        const setting = target.dataset.setting;
        if (!setting) return;
        if (handleDeviceLayoutSettingChange(target, setting)) return;
"""
source = x(source, old_router, new_router, 'device layout router extraction')
S.write_text(source, encoding='utf-8')
for path in [
    R / 'MissionChief_Map_Command_Toolkit.user.js',
    R / 'MissionChief_Map_Command_Toolkit.txt',
    R / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js',
    R / 'dist' / 'MissionChief_Map_Command_Toolkit.txt',
]:
    path.write_text(source, encoding='utf-8')

fixtures = json.loads(F.read_text(encoding='utf-8'))
fixtures['extractedDeviceLayoutSettingRoutes'] = ['mobile-mode', 'tablet-mode']
fixtures['extractedDeviceLayoutSettingStatePaths'] = {
    'mobile-mode': 'mobileMode',
    'tablet-mode': 'tabletMode',
}
F.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

test = T.read_text(encoding='utf-8')
test = x(
    test,
    '    "handleDiscordFinancialSettingChange",\n    "handleSettingChange",',
    '    "handleDiscordFinancialSettingChange",\n    "handleDeviceLayoutSettingChange",\n    "handleSettingChange",',
    'function inventory',
)
test = x(
    test,
    '    handle_financial_setting = extract_function(source, masked, "handleDiscordFinancialSettingChange")\n    handle_setting = extract_function(source, masked, "handleSettingChange")',
    '    handle_financial_setting = extract_function(source, masked, "handleDiscordFinancialSettingChange")\n    handle_device_layout_setting = extract_function(source, masked, "handleDeviceLayoutSettingChange")\n    handle_setting = extract_function(source, masked, "handleSettingChange")',
    'static extractor inventory',
)
test = x(
    test,
    '    direct_settings = values(r\'setting\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', handle_setting)\n    extracted_settings = values(r\'setting\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', handle_financial_setting)\n    handled_settings = sorted(set(direct_settings + extracted_settings))',
    '    direct_settings = values(r\'setting\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', handle_setting)\n    extracted_settings = values(r\'setting\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', handle_financial_setting)\n    device_layout_settings = values(r\'setting\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', handle_device_layout_setting)\n    handled_settings = sorted(set(direct_settings + extracted_settings + device_layout_settings))',
    'setting route inventory',
)
test = x(
    test,
    '    assert "handleDiscordFinancialSettingChange(target, setting)" in handle_setting, "Main setting router must delegate to the extracted financial route family"',
    '    assert "handleDiscordFinancialSettingChange(target, setting)" in handle_setting, "Main setting router must delegate to the extracted financial route family"\n    assert device_layout_settings == sorted(fixtures["extractedDeviceLayoutSettingRoutes"]), "Extracted device-layout setting routing changed"\n    assert not set(direct_settings).intersection(device_layout_settings), "Extracted device-layout settings remain duplicated in handleSettingChange"\n    assert "handleDeviceLayoutSettingChange(target, setting)" in handle_setting, "Main setting router must delegate to the extracted device-layout route family"\n    assert handle_device_layout_setting.index("saveState();") < handle_device_layout_setting.index("applyRootAttributes();") < handle_device_layout_setting.index("refreshTabletModeUi();"), "Device-layout persistence and reconciliation ordering changed"\n    assert handle_device_layout_setting.index("fitControlToMap();") < handle_device_layout_setting.index("positionPanelOverlay(true);") < handle_device_layout_setting.index("showToast("), "Device-layout fit, positioning and notification ordering changed"',
    'device layout static invariants',
)
direct_test = r'''

function testDeviceLayoutSettingRoutesDirectly() {{
    resetEnvironment();
    const unknownBefore = JSON.stringify(state);
    assert.equal(handleDeviceLayoutSettingChange({{ value: "ignored" }}, "unknown-layout-setting"), false);
    assert.equal(JSON.stringify(state), unknownBefore);
    assert.equal(calls.length, 0);

    resetEnvironment();
    state.tabletMode = "on";
    assert.equal(handleDeviceLayoutSettingChange({{ value: "on" }}, "mobile-mode"), true);
    assert.equal(state.mobileMode, "on");
    assert.equal(state.tabletMode, "off");
    assert.equal(activeDeviceLayout, "mobile");
    assert.equal(JSON.parse(localStorage.getItem(SCRIPT.storageState)).mobileMode, "on");
    assert.deepEqual(calls.map(call => call.name), ["applyRootAttributes", "refreshTabletModeUi", "fitControlToMap", "positionPanelOverlay", "showToast"]);
    assert.equal(callFor("showToast").args[0], "iOS Mobile Mode active");

    resetEnvironment();
    state.mobileMode = "on";
    assert.equal(handleDeviceLayoutSettingChange({{ value: "on" }}, "tablet-mode"), true);
    assert.equal(state.tabletMode, "on");
    assert.equal(state.mobileMode, "off");
    assert.equal(activeDeviceLayout, "tablet");
    assert.equal(callFor("showToast").args[0], "Tablet Mode active");

    resetEnvironment();
    state.mobileMode = "on";
    applyRootAttributes();
    clearCalls();
    assert.equal(handleDeviceLayoutSettingChange({{ value: "invalid" }}, "mobile-mode"), true);
    assert.equal(state.mobileMode, "auto");
    assert.equal(activeDeviceLayout, "desktop");
    assert.deepEqual(calls.map(call => call.name), ["applyRootAttributes", "refreshTabletModeUi", "clearTabletPanelSizing", "clearTabletDockSizing", "fitControlToMap", "positionPanelOverlay", "showToast"]);
    assert.equal(callFor("showToast").args[0], "Desktop layout active");
}}
'''
test = x(
    test,
    '\nasync function testSettingContracts() {{\n',
    direct_test + '\nasync function testSettingContracts() {{\n',
    'direct device layout contract',
)
test = x(
    test,
    '    await testDiscordFinancialSettingRoutesDirectly();\n    await testSettingContracts();',
    '    await testDiscordFinancialSettingRoutesDirectly();\n    testDeviceLayoutSettingRoutesDirectly();\n    await testSettingContracts();',
    'device layout contract invocation',
)
test = x(
    test,
    'extracted payout/audio toggle parity, extracted financial route parity,',
    'extracted payout/audio toggle parity, extracted financial route parity, extracted device-layout setting parity,',
    'contract summary',
)
T.write_text(test, encoding='utf-8')

changelog = (R / 'CHANGELOG.md').read_text(encoding='utf-8')
entry = f'''## [{NEW}] - 2026-07-22

### Internal reliability
- Extracted Mobile Mode and Tablet Mode state, layout reconciliation, sizing cleanup, fitting and notification routing from `handleSettingChange()` into a dedicated device-layout handler.
- Added direct and delegated contracts for accepted values, invalid-value normalization, mutual exclusion and Desktop/Tablet/iOS transition ordering.

### Compatibility
- No visual design, breakpoint, viewport, safe-area, touch-target, panel sizing, theme or public asset changed.

'''
(R / 'CHANGELOG.md').write_text(x(changelog, '## [Unreleased]\n\n', '## [Unreleased]\n\n' + entry, 'changelog'), encoding='utf-8')
help_text = (R / 'help' / 'index.html').read_text(encoding='utf-8')
if OLD not in help_text:
    raise RuntimeError('help version missing')
(R / 'help' / 'index.html').write_text(help_text.replace(OLD, NEW), encoding='utf-8')

headroom = json.loads(H.read_text(encoding='utf-8'))
source_lines = len(source.splitlines())
headroom['candidateVersion'] = NEW
headroom['candidateSourceLines'] = source_lines
headroom['recoveredSourceLines'] = headroom['originalSourceLines'] - source_lines
headroom['candidateSourceSha256'] = hashlib.sha256(source.encode()).hexdigest()
headroom['invariant'] = 'The reviewed compact stylesheet retains 504 recovered source lines while device-layout setting routing remains fixture-backed and managed runtime budgets remain unchanged.'
H.write_text(json.dumps(headroom, indent=2) + '\n', encoding='utf-8')

subprocess.check_call(
    [sys.executable, str(T)],
    cwd=R,
    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
)
for cache in R.rglob('__pycache__'):
    shutil.rmtree(cache, ignore_errors=True)
print(f'Prepared {NEW}; source lines={source_lines}; recovered={headroom["recoveredSourceLines"]}')
