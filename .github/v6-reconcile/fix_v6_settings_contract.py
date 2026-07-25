#!/usr/bin/env python3
"""Remove final retired-feature expectations from the shared settings contract."""
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
    PATH.write_text(text, encoding="utf-8")
    print("v6 settings contract retired-feature expectations removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
