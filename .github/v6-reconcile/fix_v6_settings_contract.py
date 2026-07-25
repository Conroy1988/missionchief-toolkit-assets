#!/usr/bin/env python3
"""Remove retired-feature expectations from the shared settings contract."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / ".github" / "scripts" / "test_settings_ui_contract.py"


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    text = text.replace('        ["missionInspector", "showToast"],\n', '')
    text = text.replace(
        '    resetEnvironment();\n'
        '    toggleFeature("criticalView");\n'
        '    assert.equal(wasCalled("toggleCriticalView"), true);\n'
        '    assert.equal(localStorage.getItem(SCRIPT.storageState), null);\n',
        ''
    )
    text = text.replace(
        '    handleSettingChange({{ dataset: {{ setting: "heatmap-source" }}, value: "invalid" }});\n'
        '    assert.equal(state.heatmap.source, "stations");\n'
        '    handleSettingChange({{ dataset: {{ setting: "heatmap-service" }}, value: "police" }});\n'
        '    assert.equal(state.heatmap.service, "police");\n'
        '    handleSettingChange({{ dataset: {{ setting: "heatmap-opacity" }}, value: "0.42" }});\n'
        '    assert.equal(state.heatmap.opacity, 0.42);\n\n',
        ''
    )
    text = text.replace(
        '    handleSettingChange({{ dataset: {{ setting: "auto-night-start" }}, value: "20:30" }});\n'
        '    assert.equal(state.autoNight.nightStart, "20:30");\n'
        '    handleSettingChange({{ dataset: {{ setting: "auto-night-theme" }}, value: "nightshift" }});\n'
        '    assert.equal(state.autoNight.nightTheme, "nightshift");\n\n',
        ''
    )
    PATH.write_text(text, encoding="utf-8")
    print("v6 settings contract retired-feature expectations removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
