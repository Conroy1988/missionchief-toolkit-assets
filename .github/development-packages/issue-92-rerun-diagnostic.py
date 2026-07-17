#!/usr/bin/env python3
from pathlib import Path
import runpy
import traceback

root = Path(__file__).resolve().parents[2]
target = root / ".github/development-packages/issue-92-navigation-implementation.py"
report = root / "docs/internal/issue-92-rerun-error.txt"
paths = [
    root / "src/MissionChief_Map_Command_Toolkit.user.js",
    root / "CHANGELOG.md",
    root / "help/index.html",
    root / ".github/scripts/run_userscript_preflight.sh",
    root / ".github/scripts/test_section_navigation_contract.py",
    root / ".github/fixtures/section-navigation-contract.json",
    root / "docs/internal/issue-92-navigation-audit.md",
    root / "docs/internal/issue-92-panel-source-extract.md",
    root / "docs/internal/issue-92-label-css-audit.md",
    root / "docs/internal/issue-92-implementation-error.txt",
]
snapshots = {path: path.read_bytes() if path.exists() else None for path in paths}
text = target.read_text(encoding="utf-8")
old = '''# Remove duplicated controls. Tools remains the canonical home for shortcuts 6–9 and transport/unit overlays.
for old, label in [
    ("                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}\\n", "Resources Transport Watch duplicate"),
    ("                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}\\n", "Ops Transport Watch duplicate"),
    ("                    ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your own committed unit counts beside missions. Shortcut: 8')}\\n", "Ops Unit Count duplicate"),
    ("                    ${makeToggleButton('criticalView', '9', 'Critical View', 'Show only personal missions aged 8 hours or more. Shortcut: 9')}\\n", "Ops Critical View duplicate"),
    ("                    ${makeToggleButton('missionAge', '6', 'Mission Age', 'Show personal mission age with 8H amber, 16H orange and 24H red warning stages. Shortcut: 6')}\\n", "Ops Mission Age duplicate"),
]:
    source = replace_once(source, old, "", label)
'''
new = '''# Remove duplicated controls. Tools remains the canonical home for shortcuts 6–9 and transport/unit overlays.
transport_duplicate = "                    ${makeToggleButton('transportWatcher', '7', 'Transport Watch', 'Show amber transport-required badges beside missions. Shortcut: 7')}\\n"
transport_count = source.count(transport_duplicate)
if transport_count != 2:
    raise RuntimeError(f"Transport Watch duplicates: expected two matches, found {transport_count}")
source = source.replace(transport_duplicate, "", 2)
for old, label in [
    ("                    ${makeToggleButton('unitCommitment', '8', 'Unit Count', 'Show your own committed unit counts beside missions. Shortcut: 8')}\\n", "Ops Unit Count duplicate"),
    ("                    ${makeToggleButton('criticalView', '9', 'Critical View', 'Show only personal missions aged 8 hours or more. Shortcut: 9')}\\n", "Ops Critical View duplicate"),
    ("                    ${makeToggleButton('missionAge', '6', 'Mission Age', 'Show personal mission age with 8H amber, 16H orange and 24H red warning stages. Shortcut: 6')}\\n", "Ops Mission Age duplicate"),
]:
    source = replace_once(source, old, "", label)
'''
result = "SUCCESS\n"
try:
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one duplicate-removal block, found {text.count(old)}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")
    runpy.run_path(str(target), run_name="__main__")
except Exception:
    result = "FAILED\n\n" + traceback.format_exc()
finally:
    target.write_text(text, encoding="utf-8")
    for path, content in snapshots.items():
        if content is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(result, encoding="utf-8")
print(result)
