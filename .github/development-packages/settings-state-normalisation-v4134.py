#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_USER = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.user.js'
DIST_TXT = ROOT / 'dist' / 'MissionChief_Map_Command_Toolkit.txt'
CHANGELOG = ROOT / 'CHANGELOG.md'
SETTINGS_TEST = ROOT / '.github' / 'scripts' / 'test_settings_ui_contract.py'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


def extract_load_state(text: str) -> tuple[str, int, int]:
    start_marker = '    function loadState() {'
    end_marker = '    function saveState() {'
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError('loadState declaration not found')
    end = text.find(end_marker, start)
    if end < 0:
        raise RuntimeError('saveState declaration not found after loadState')
    return text[start:end], start, end


def build_normalisation_extraction(load_state: str) -> str:
    normal_start_marker = '            const merged = {'
    normal_end_marker = '            return merged;\n'
    normal_start = load_state.find(normal_start_marker)
    if normal_start < 0:
        raise RuntimeError('loadState normalization start not found')
    normal_end_start = load_state.find(normal_end_marker, normal_start)
    if normal_end_start < 0:
        raise RuntimeError('loadState normalization return not found')
    normal_end = normal_end_start + len(normal_end_marker)
    normalization = load_state[normal_start:normal_end]

    deindented_lines = []
    for line in normalization.splitlines(keepends=True):
        if line.startswith('    '):
            line = line[4:]
        deindented_lines.append(line)
    normalization = ''.join(deindented_lines)

    helper = (
        '    function normaliseLoadedState(parsed, base = defaultState()) {\n'
        f'{normalization}'
        '    }\n\n'
    )
    replacement_load = '''    function loadState() {
        const base = defaultState();
        const raw = localStorage.getItem(SCRIPT.storageState) || SCRIPT.oldStorageKeys.map(key => localStorage.getItem(key)).find(Boolean);
        if (!raw) return base;

        try {
            return normaliseLoadedState(JSON.parse(raw), base);
        } catch (err) {
            return base;
        }
    }

'''
    return helper + replacement_load


def update_source() -> None:
    text = SOURCE.read_text(encoding='utf-8')
    text = replace_once(text, '// @version      4.13.3', '// @version      4.13.4', 'metadata version')
    text = replace_once(text, "version: '4.13.3'", "version: '4.13.4'", 'runtime version')
    text = replace_once(text, "styleId: 'mc-map-command-toolkit-style-v4133'", "styleId: 'mc-map-command-toolkit-style-v4134'", 'style id')
    text = replace_once(text, "guideVersion: '4.13.3'", "guideVersion: '4.13.4'", 'help guide version')
    text = replace_once(
        text,
        "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4133__ = true;\n",
        "    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4133__ = true;\n    pageWindow.__MC_MAP_COMMAND_TOOLKIT_V4134__ = true;\n",
        'runtime sentinel',
    )

    load_state, start, end = extract_load_state(text)
    if 'normaliseLoadedState' in load_state:
        raise RuntimeError('loadState is already normalized through a helper')
    text = text[:start] + build_normalisation_extraction(load_state) + text[end:]

    SOURCE.write_text(text, encoding='utf-8')
    DIST_USER.write_text(text, encoding='utf-8')
    DIST_TXT.write_text(text, encoding='utf-8')


def update_settings_contract() -> None:
    text = SETTINGS_TEST.read_text(encoding='utf-8')
    text = replace_once(
        text,
        '    "defaultState",\n    "loadState",\n',
        '    "defaultState",\n    "normaliseLoadedState",\n    "loadState",\n',
        'settings helper extraction list',
    )

    old = '''function testStateMigration() {{
    resetEnvironment();
    assertDefaultShape(loadState());

    localStorage.setItem(SCRIPT.storageState, "{{not-json");
'''
    new = '''function testStateMigration() {{
    resetEnvironment();
    assertDefaultShape(loadState());

    const directInput = JSON.parse(JSON.stringify(fixtures.legacyMigration));
    const directInputBefore = JSON.stringify(directInput);
    const directBase = defaultState();
    const directBaseBefore = JSON.stringify(directBase);
    const directMigrated = normaliseLoadedState(directInput, directBase);
    assert.equal(JSON.stringify(directInput), directInputBefore, "normalization must not mutate parsed settings");
    assert.equal(JSON.stringify(directBase), directBaseBefore, "normalization must not mutate default settings");
    assert.equal(directMigrated.activeTab, "resources");
    assert.equal(directMigrated.visibility.buildings, true);
    assert.equal(directMigrated.payoutFlash.template, "gta5");

    localStorage.setItem(SCRIPT.storageState, "{{not-json");
'''
    text = replace_once(text, old, new, 'direct settings normalization contract')
    text = replace_once(
        text,
        '''    const migrated = loadState();
    assert.equal(migrated.uiTheme, "mapCommand");
''',
        '''    const migrated = loadState();
    assert.deepEqual(migrated, directMigrated, "loadState must preserve direct normalization output");
    assert.equal(migrated.uiTheme, "mapCommand");
''',
        'load state parity assertion',
    )
    text = replace_once(
        text,
        'Settings/UI contract passed: defaults, migrations, import rollback, ',
        'Settings/UI contract passed: direct normalization, defaults, migrations, import rollback, ',
        'settings contract success message',
    )
    SETTINGS_TEST.write_text(text, encoding='utf-8')


def update_changelog() -> None:
    text = CHANGELOG.read_text(encoding='utf-8')
    entry = '''## [Unreleased]

## [4.13.4] - 2026-07-16

### Internal reliability
- Added direct fixture coverage for loaded-state normalization, including non-mutating parsed inputs, unchanged defaults and parity with the storage-backed load path.
- Extracted deterministic settings merge, migration and validation into `normaliseLoadedState()` while preserving storage-key precedence, JSON failure fallback, import rollback and saved-setting compatibility.

### Compatibility
- No setting names, defaults, themes, payout presentations, public assets, UI routes, keyboard shortcuts or runtime feature behaviour were changed.

'''
    text = replace_once(text, '## [Unreleased]\n\n', entry, '4.13.4 changelog entry')
    CHANGELOG.write_text(text, encoding='utf-8')


def main() -> int:
    update_source()
    update_settings_contract()
    update_changelog()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
