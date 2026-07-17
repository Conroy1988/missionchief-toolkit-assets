#!/usr/bin/env python3
from pathlib import Path
import runpy
import traceback

root = Path(__file__).resolve().parents[2]
target = root / ".github/development-packages/issue-92-navigation-implementation.py"
report = root / "docs/internal/issue-92-implementation-error.txt"
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
]
snapshots = {path: path.read_bytes() if path.exists() else None for path in paths}
result = "SUCCESS\n"
try:
    runpy.run_path(str(target), run_name="__main__")
except Exception:
    result = "FAILED\n\n" + traceback.format_exc()
finally:
    for path, content in snapshots.items():
        if content is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(result, encoding="utf-8")
print(result)
