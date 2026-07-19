#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PACKAGE = ROOT / ".github" / "development-packages" / "issue-203-version-control-family.py"
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_USER = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist" / "MissionChief_Map_Command_Toolkit.txt"
RUNTIME = ROOT / ".github" / "scripts" / "test_version_status_runtime.js"
CONTRACT = ROOT / ".github" / "scripts" / "test_version_status_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


subprocess.run([sys.executable, str(BASE_PACKAGE)], cwd=ROOT, check=True)

# Keep the version control visually aligned with Economy without inheriting the
# Economy behaviour selector, which must continue to identify one real control.
replace_once(
    SOURCE,
    "button.className = 'mcms-economy-btn mcms-version-btn mcms-version-btn--unified';",
    "button.className = 'mcms-version-btn mcms-version-btn--unified';",
    "isolated unified control class",
)

replace_once(
    RUNTIME,
    "    assert(first.className.includes('mcms-economy-btn'), 'version control participates in the Economy control family');\n",
    "    assert(!first.className.includes('mcms-economy-btn'), 'version control avoids Economy behaviour-selector collisions');\n",
    "runtime Economy selector isolation",
)

replace_once(
    CONTRACT,
    "    assert \"button.className = 'mcms-economy-btn mcms-version-btn mcms-version-btn--unified'\" in block\n",
    "    assert \"button.className = 'mcms-version-btn mcms-version-btn--unified'\" in block\n    assert \"button.className = 'mcms-economy-btn mcms-version-btn mcms-version-btn--unified'\" not in block\n",
    "contract Economy selector isolation",
)
replace_once(
    CONTRACT,
    '    assert "[data-state="latest"]::before{content:"✓"!important" in block\n',
    '    assert \'[data-state="latest"]::before{content:"✓"!important\' in block\n',
    "LATEST contract quote correction",
)
replace_once(
    CONTRACT,
    '    assert "[data-state="update"]::before{content:"↑"!important" in block\n',
    '    assert \'[data-state="update"]::before{content:"↑"!important\' in block\n',
    "UPDATE contract quote correction",
)

replace_once(
    CHANGELOG,
    "- Rebuilt the version-status control as a member of the existing Economy control family with the same dark control surface, footprint, radius, shadow rhythm and icon-over-label composition.\n",
    "- Rebuilt the version-status control to match the existing Menu and Economy control family with the same dark surface, footprint, radius, shadow rhythm and icon-over-label composition, without reusing Economy's behavioural selector.\n",
    "changelog selector isolation",
)

# Re-establish canonical source/distribution parity after the targeted source fix.
source = SOURCE.read_text(encoding="utf-8")
DIST_USER.write_text(source, encoding="utf-8")
DIST_TEXT.write_text(source, encoding="utf-8")

for temporary in [
    ROOT / ".github" / "development-packages" / "issue-203-diagnose.py",
    ROOT / ".github" / "workflows" / "issue-203-artifact-diagnostic.yml",
    ROOT / "issue-203-diagnostic.log",
]:
    temporary.unlink(missing_ok=True)

Path(__file__).unlink(missing_ok=True)
print("Corrected v4.20.2 contracts, isolated the Economy selector and removed diagnostics")
