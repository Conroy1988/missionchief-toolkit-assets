#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

R = Path(__file__).resolve().parents[2]
S = R / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
F = R / '.github' / 'fixtures' / 'settings-ui-contract.json'
T = R / '.github' / 'scripts' / 'test_settings_ui_contract.py'
H = R / '.github' / 'fixtures' / 'main-style-source-headroom.json'
OLD = '4.20.31'
NEW = '4.20.32'
FEATURES = ('missionSpawn', 'stuckDetector')


def x(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{name}: expected 1 occurrence, found {count}')
    return text.replace(old, new, 1)


def mask_javascript(text):
    out = list(text)
    state = 'code'
    quote = ''
    escaped = False
    index = 0
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ''
        if state == 'code':
            if char in ("'", '"', '`'):
                state = 'string'
                quote = char
                out[index] = ' '
            elif char == '/' and nxt == '/':
                state = 'line-comment'
                out[index] = out[index + 1] = ' '
                index += 1
            elif char == '/' and nxt == '*':
                state = 'block-comment'
                out[index] = out[index + 1] = ' '
                index += 1
        elif state == 'string':
            out[index] = ' '
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                state = 'code'
        elif state == 'line-comment':
            if char == '\n':
                state = 'code'
            else:
                out[index] = ' '
        elif state == 'block-comment':
            out[index] = ' '
            if char == '*' and nxt == '/':
                out[index + 1] = ' '
                index += 1
                state = 'code'
        index += 1
    return ''.join(out)


def matching(masked, start, opening, closing):
    depth = 0
    for index in range(start, len(masked)):
        char = masked[index]
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
    raise RuntimeError(f'unmatched {opening} at {start}')


def function_span(source, name):
    masked = mask_javascript(source)
    match = re.search(rf'\bfunction\s+{re.escape(name)}\s*\(', masked)
    if not match:
        raise RuntimeError(f'function {name} not found')
    open_brace = masked.find('{', match.start())
    close_brace = matching(masked, open_brace, '{', '}')
    return match.start(), close_brace + 1


def feature_statements(function_text):
    masked = mask_javascript(function_text)
    pattern = re.compile(r"if\s*\(\s*feature\s*===\s*(['\"])(missionSpawn|stuckDetector)\1\s*\)")
    statements = []
    for match in pattern.finditer(function_text):
        start = function_text.rfind('\n', 0, match.start()) + 1
        condition_open = masked.find('(', match.start(), match.end())
        condition_close = matching(masked, condition_open, '(', ')')
        cursor = condition_close + 1
        while cursor < len(function_text) and function_text[cursor].isspace():
            cursor += 1
        if function_text[cursor] == '{':
            end = matching(masked, cursor, '{', '}') + 1
        else:
            semicolon = masked.find(';', cursor)
            if semicolon < 0:
                raise RuntimeError(f'{match.group(2)} statement terminator not found')
            end = semicolon + 1
        statements.append({
            'feature': match.group(2),
            'start': start,
            'end': end,
            'text': function_text[start:end],
        })
    return statements


def statement_body(statement):
    text = statement['text']
    masked = mask_javascript(text)
    condition = re.search(r"if\s*\(\s*feature\s*===\s*(['\"])(missionSpawn|stuckDetector)\1\s*\)", text)
    if not condition:
        raise RuntimeError(f"unable to parse {statement['feature']} statement")
    open_paren = masked.find('(', condition.start(), condition.end())
    close_paren = matching(masked, open_paren, '(', ')')
    remainder = text[close_paren + 1:].strip()
    if remainder.startswith('{'):
        close_brace = matching(mask_javascript(remainder), 0, '{', '}')
        body = remainder[1:close_brace]
    else:
        body = remainder
    return textwrap.dedent(body).strip()


def render_helper(name, grouped, return_handled):
    lines = [f'    function {name}(feature) {{']
    for index, feature in enumerate(FEATURES):
        bodies = grouped.get(feature) or []
        if not bodies:
            raise RuntimeError(f'{name}: no body found for {feature}')
        prefix = 'if' if index == 0 else 'else if'
        body = '\n'.join(bodies)
        if '\n' not in body:
            lines.append(f"        {prefix} (feature === '{feature}') {{ {body} }}")
        else:
            lines.append(f"        {prefix} (feature === '{feature}') {{")
            lines.extend('            ' + line if line else '' for line in body.splitlines())
            lines.append('        }')
    if return_handled:
        lines.append('        else return false;')
        lines.append('        return true; }')
    else:
        lines.append('    }')
    return '\n'.join(lines)


source = S.read_text(encoding='utf-8')
original_line_count = len(source.splitlines())
source = x(source, f'// @version      {OLD}', f'// @version      {NEW}', 'metadata version')
source = x(source, f"version: '{OLD}'", f"version: '{NEW}'", 'runtime version')
if 'function handleMissionMonitoringToggle(' in source or 'function applyMissionMonitoringToggleEffects(' in source:
    raise RuntimeError('mission-monitoring helpers already exist')

function_start, function_end = function_span(source, 'toggleFeature')
toggle = source[function_start:function_end]
statements = feature_statements(toggle)
for feature in FEATURES:
    count = sum(statement['feature'] == feature for statement in statements)
    if count < 2:
        raise RuntimeError(f'{feature}: expected state and effect statements, found {count}')

save_index = toggle.find('saveState();')
reconcile_index = toggle.find('reconcileFeatureRefreshes(feature);')
if save_index < 0 or reconcile_index < 0 or save_index >= reconcile_index:
    raise RuntimeError('common toggle lifecycle boundary not found')

state_statements = []
effect_statements = []
for statement in statements:
    assignment = f"state.{statement['feature']}.enabled"
    if assignment in statement['text'] and statement['start'] < save_index:
        state_statements.append(statement)
    elif statement['start'] > reconcile_index:
        effect_statements.append(statement)
    else:
        raise RuntimeError(f"{statement['feature']}: statement crossed the common lifecycle boundary")

for feature in FEATURES:
    if sum(statement['feature'] == feature for statement in state_statements) != 1:
        raise RuntimeError(f'{feature}: expected exactly one state statement')
    if not any(statement['feature'] == feature for statement in effect_statements):
        raise RuntimeError(f'{feature}: expected at least one post-reconciliation effect statement')

state_bodies = {
    feature: [statement_body(statement) for statement in state_statements if statement['feature'] == feature]
    for feature in FEATURES
}
effect_bodies = {
    feature: [statement_body(statement) for statement in effect_statements if statement['feature'] == feature]
    for feature in FEATURES
}
state_helper = render_helper('handleMissionMonitoringToggle', state_bodies, True)
effect_helper = render_helper('applyMissionMonitoringToggleEffects', effect_bodies, False)

replacements = {}
first_state = min(statement['start'] for statement in state_statements)
first_effect = min(statement['start'] for statement in effect_statements)
for statement in state_statements:
    replacements[(statement['start'], statement['end'])] = (
        '        handleMissionMonitoringToggle(feature);' if statement['start'] == first_state else ''
    )
for statement in effect_statements:
    replacements[(statement['start'], statement['end'])] = (
        '        applyMissionMonitoringToggleEffects(feature);' if statement['start'] == first_effect else ''
    )
for (start, end), replacement in sorted(replacements.items(), reverse=True):
    toggle = toggle[:start] + replacement + toggle[end:]

helper_block = state_helper + '\n' + effect_helper + '\n'
source = source[:function_start] + helper_block + toggle + source[function_end:]

current_line_count = len(source.splitlines())
if current_line_count < original_line_count:
    padding = '\n' * (original_line_count - current_line_count)
    marker = '    function handleMissionMonitoringToggle(feature) {'
    source = source.replace(marker, padding + marker, 1)
elif current_line_count > original_line_count:
    excess = current_line_count - original_line_count
    helper_start = source.index('    function handleMissionMonitoringToggle(feature) {')
    toggle_start = source.index('    function toggleFeature(feature) {', helper_start)
    segment = source[helper_start:toggle_start]
    while excess and '\n\n' in segment:
        segment = segment.replace('\n\n', '\n', 1)
        excess -= 1
    if excess:
        raise RuntimeError(f'mission-monitoring extraction consumed {excess} protected source-headroom lines')
    source = source[:helper_start] + segment + source[toggle_start:]
if len(source.splitlines()) != original_line_count:
    raise RuntimeError('source-headroom line count changed')

S.write_text(source, encoding='utf-8')
for path in [
    R / 'MissionChief_Map_Command_Toolkit.user.js',
    R / 'MissionChief_Map_Command_Toolkit.txt',
    R / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js',
    R / 'dist' / 'MissionChief_Map_Command_Toolkit.txt',
]:
    path.write_text(source, encoding='utf-8')

fixtures = json.loads(F.read_text(encoding='utf-8'))
fixtures['extractedMissionMonitoringToggleRoutes'] = list(FEATURES)
fixtures['extractedMissionMonitoringEffectRoutes'] = list(FEATURES)
fixtures['extractedMissionMonitoringToggleStatePaths'] = {
    'missionSpawn': 'missionSpawn.enabled',
    'stuckDetector': 'stuckDetector.enabled',
}
F.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

test = T.read_text(encoding='utf-8')
test = x(
    test,
    '    "applyPayoutAudioToggleEffects",\n    "toggleFeature",',
    '    "applyPayoutAudioToggleEffects",\n    "handleMissionMonitoringToggle",\n    "applyMissionMonitoringToggleEffects",\n    "toggleFeature",',
    'function inventory',
)
test = x(
    test,
    '    apply_payout_audio_effects = extract_function(source, masked, "applyPayoutAudioToggleEffects")\n    toggle_feature = extract_function(source, masked, "toggleFeature")',
    '    apply_payout_audio_effects = extract_function(source, masked, "applyPayoutAudioToggleEffects")\n    handle_mission_monitoring_toggle = extract_function(source, masked, "handleMissionMonitoringToggle")\n    apply_mission_monitoring_effects = extract_function(source, masked, "applyMissionMonitoringToggleEffects")\n    toggle_feature = extract_function(source, masked, "toggleFeature")',
    'static extractor inventory',
)
test = x(
    test,
    '    payout_audio_toggle_routes = values(r\'feature\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', handle_payout_audio_toggle)\n    payout_audio_effect_routes = values(r\'feature\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', apply_payout_audio_effects)\n    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes + payout_audio_toggle_routes))',
    '    payout_audio_toggle_routes = values(r\'feature\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', handle_payout_audio_toggle)\n    payout_audio_effect_routes = values(r\'feature\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', apply_payout_audio_effects)\n    mission_monitoring_toggle_routes = values(r\'feature\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', handle_mission_monitoring_toggle)\n    mission_monitoring_effect_routes = values(r\'feature\\s*===\\s*["\\\']([^"\\\']+)["\\\']\', apply_mission_monitoring_effects)\n    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes + payout_audio_toggle_routes + mission_monitoring_toggle_routes))',
    'mission-monitoring route inventory',
)
test = x(
    test,
    '    assert "applyPayoutAudioToggleEffects(feature)" in toggle_feature',
    '    assert "applyPayoutAudioToggleEffects(feature)" in toggle_feature\n    assert mission_monitoring_toggle_routes == sorted(fixtures["extractedMissionMonitoringToggleRoutes"]), "Extracted mission-monitoring toggle routing changed"\n    assert mission_monitoring_effect_routes == sorted(fixtures["extractedMissionMonitoringEffectRoutes"]), "Extracted mission-monitoring effect routing changed"\n    assert not set(direct_toggle_routes).intersection(mission_monitoring_toggle_routes), "Extracted mission-monitoring toggles remain duplicated"\n    assert "handleMissionMonitoringToggle(feature)" in toggle_feature\n    assert "applyMissionMonitoringToggleEffects(feature)" in toggle_feature',
    'mission-monitoring static invariants',
)
direct_test = r'''

function testExtractedMissionMonitoringToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedMissionMonitoringToggleStatePaths)) {{
        resetEnvironment();
        const before = pathValue(state, path);
        assert.equal(handleMissionMonitoringToggle(feature), true, `${{feature}} was not handled directly`);
        assert.notEqual(pathValue(state, path), before, `${{feature}} did not toggle ${{path}} directly`);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null);
        assert.equal(wasCalled("updateUI"), false);
    }}

    resetEnvironment();
    const unknownBefore = JSON.stringify(state);
    assert.equal(handleMissionMonitoringToggle("unknown-monitoring-toggle"), false);
    assert.equal(JSON.stringify(state), unknownBefore);
    assert.equal(calls.length, 0);

    resetEnvironment();
    state.missionSpawn.enabled = false;
    missionSpawnPrimeTimer = 73;
    missionSpawnArmed = true;
    handleMissionMonitoringToggle("missionSpawn");
    assert.equal(state.missionSpawn.enabled, true);
    assert.equal(missionSpawnPrimeTimer, null);
    assert.equal(missionSpawnArmed, false);
    assert.equal(wasCalled("runtimeClearTimeout"), true);
    assert.equal(wasCalled("primeMissionSpawnDetector"), true);

    resetEnvironment();
    state.missionSpawn.enabled = true;
    missionSpawnPrimeTimer = 74;
    missionSpawnArmed = true;
    handleMissionMonitoringToggle("missionSpawn");
    assert.equal(state.missionSpawn.enabled, false);
    assert.equal(missionSpawnPrimeTimer, null);
    assert.equal(missionSpawnArmed, false);
    assert.equal(wasCalled("runtimeClearTimeout"), true);
    assert.equal(wasCalled("primeMissionSpawnDetector"), false);

    resetEnvironment();
    applyMissionMonitoringToggleEffects("missionSpawn");
    assert.equal(wasCalled("showToast"), true);

    resetEnvironment();
    applyMissionMonitoringToggleEffects("stuckDetector");
    assert.equal(wasCalled("scheduleStuckMissionRefresh"), true);

    resetEnvironment();
    applyMissionMonitoringToggleEffects("coverage");
    assert.equal(calls.length, 0);
}}
'''
test = x(
    test,
    '\nasync function testToggleContracts() {{\n',
    direct_test + '\nasync function testToggleContracts() {{\n',
    'direct mission-monitoring contract',
)
delegated_test = r'''

    resetEnvironment();
    state.missionSpawn.enabled = false;
    missionSpawnPrimeTimer = 75;
    missionSpawnArmed = true;
    toggleFeature("missionSpawn");
    const spawnClearIndex = calls.findIndex(call => call.name === "runtimeClearTimeout");
    const spawnPrimeIndex = calls.findIndex(call => call.name === "primeMissionSpawnDetector");
    const spawnUpdateIndex = calls.findIndex(call => call.name === "updateUI");
    const spawnReconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
    const spawnToastIndex = calls.findIndex(call => call.name === "showToast");
    assert.ok(spawnClearIndex >= 0 && spawnClearIndex < spawnUpdateIndex);
    assert.ok(spawnPrimeIndex >= 0 && spawnPrimeIndex < spawnUpdateIndex);
    assert.ok(spawnUpdateIndex < spawnReconcileIndex && spawnReconcileIndex < spawnToastIndex);

    resetEnvironment();
    toggleFeature("stuckDetector");
    const stuckUpdateIndex = calls.findIndex(call => call.name === "updateUI");
    const stuckReconcileIndex = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
    const stuckRefreshIndex = calls.findIndex(call => call.name === "scheduleStuckMissionRefresh");
    assert.ok(stuckUpdateIndex >= 0 && stuckUpdateIndex < stuckReconcileIndex);
    assert.ok(stuckReconcileIndex < stuckRefreshIndex);
'''
test = x(
    test,
    '\n    resetEnvironment();\n    toggleFeature("criticalView");',
    delegated_test + '\n    resetEnvironment();\n    toggleFeature("criticalView");',
    'delegated mission-monitoring order contract',
)
test = x(
    test,
    '    testExtractedPayoutAudioToggleContracts();\n    await testToggleContracts();',
    '    testExtractedPayoutAudioToggleContracts();\n    testExtractedMissionMonitoringToggleContracts();\n    await testToggleContracts();',
    'mission-monitoring contract invocation',
)
test = x(
    test,
    'extracted payout/audio toggle parity, extracted financial route parity,',
    'extracted payout/audio toggle parity, extracted mission-monitoring toggle parity, extracted financial route parity,',
    'contract summary',
)
T.write_text(test, encoding='utf-8')

changelog = (R / 'CHANGELOG.md').read_text(encoding='utf-8')
entry = f'''## [{NEW}] - 2026-07-22

### Internal reliability
- Extracted Mission Spawn and Stuck Detector state and post-reconciliation routing from `toggleFeature()` into dedicated mission-monitoring helpers.
- Added direct and delegated contracts for timer cleanup, arming reset, enabled-only detector priming, stuck-mission refresh scheduling and lifecycle ordering.

### Compatibility
- No monitoring threshold, timer duration, mission classification, visual design, device layout, theme or public asset changed.

'''
(R / 'CHANGELOG.md').write_text(
    x(changelog, '## [Unreleased]\n\n', '## [Unreleased]\n\n' + entry, 'changelog'),
    encoding='utf-8',
)
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
headroom['invariant'] = (
    f'The reviewed compact stylesheet retains {headroom["recoveredSourceLines"]} recovered source lines '
    'while mission-monitoring toggle routing remains fixture-backed and managed runtime budgets remain unchanged.'
)
H.write_text(json.dumps(headroom, indent=2) + '\n', encoding='utf-8')

subprocess.check_call(
    [sys.executable, str(T)],
    cwd=R,
    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
)
for cache in R.rglob('__pycache__'):
    shutil.rmtree(cache, ignore_errors=True)
print(f'Prepared {NEW}; source lines={source_lines}; recovered={headroom["recoveredSourceLines"]}')
