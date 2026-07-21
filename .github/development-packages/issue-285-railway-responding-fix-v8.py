#!/usr/bin/env python3
from __future__ import annotations

import py_compile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V7 = ROOT / ".github/development-packages/issue-285-railway-responding-fix-v7.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    runner = V7.read_text(encoding="utf-8")
    marker = '    ORIGINAL.write_text(payload, encoding="utf-8")\n'
    fixture_patch = '''    validation_marker = '    subprocess.run(["python3", ".github/scripts/validate_userscript.py"], cwd=ROOT, check=True)\\n'
    fixture_update = \'\'\'    cross_source_path = ROOT / ".github/fixtures/mission-requirements-cross-source-en_GB.json"\\n    cross_source = json.loads(cross_source_path.read_text(encoding="utf-8"))\\n    railway_snapshot = {\\n        "aliases": ["Railway Police Officer", "Railway Police Officers"],\\n        "arrAttributes": [],\\n        "conditionalVehicles": {},\\n        "equipment": [],\\n        "factors": {},\\n        "key": "railway-police-officer",\\n        "pair": False,\\n        "training": ["Railway Police Officer", "Railway Police", "railway_police"],\\n        "types": [108],\\n    }\\n    capabilities = cross_source.setdefault("capabilities", [])\\n    existing_index = next((index for index, entry in enumerate(capabilities) if entry.get("key") == "railway-police-officer"), None)\\n    if existing_index is None:\\n        capabilities.append(railway_snapshot)\\n    else:\\n        capabilities[existing_index] = railway_snapshot\\n    cross_source_path.write_text(json.dumps(cross_source, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")\\n\\n\'\'\'
    payload = replace_once(payload, validation_marker, fixture_update + validation_marker, "Railway Police cross-source fixture")
'''
    runner = replace_once(runner, marker, fixture_patch + marker, "inject cross-source fixture update")
    V7.write_text(runner, encoding="utf-8")
    py_compile.compile(str(V7), doraise=True)
    subprocess.run(["python3", str(V7)], cwd=ROOT, check=True)
    for path in (
        V7,
        ROOT / "docs/issue-285-v7-diagnostic.txt",
    ):
        path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
