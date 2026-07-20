#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PACKAGE = ROOT / ".github" / "development-packages" / "fix-issue-257-combined-capabilities-v4.20.12.py"
DIAGNOSTIC_PACKAGE = ROOT / ".github" / "development-packages" / "diagnose-issue-257-v4.20.12.py"
RUNTIME_TEST = ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


runpy.run_path(str(BASE_PACKAGE), run_name="__main__")

# MissionChief's live missing count already reflects vehicles on scene. The
# Matrix must recognise and display the on-site unit without subtracting it from
# that live shortage a second time. Selected/responding capacity remains
# subtractive because it is not yet incorporated into the on-scene state.
runtime_test = RUNTIME_TEST.read_text(encoding="utf-8")
runtime_test = replace_once(
    runtime_test,
    "assert.strictEqual(row.stillNeededText, '0', 'on-site Police Drone clears the shortage');",
    "assert.strictEqual(row.stillNeededText, '1', 'live MissionChief shortage remains authoritative after recognising the on-site Police Drone');",
    "Issue #257 on-site live-missing authority assertion",
)
runtime_test = replace_once(
    runtime_test,
    "assert.strictEqual(row.stillNeededText, '1', 'removing the on-site unit restores the shortage');",
    "assert.strictEqual(row.onSiteMin, 0, 'removing the on-site Police Drone removes recognised on-site capacity');\n"
    "assert.strictEqual(row.stillNeededText, '1', 'live MissionChief shortage remains unchanged when the on-site unit is removed');",
    "Issue #257 on-site removal assertion",
)
RUNTIME_TEST.write_text(runtime_test, encoding="utf-8")

BASE_PACKAGE.unlink(missing_ok=True)
DIAGNOSTIC_PACKAGE.unlink(missing_ok=True)

print("Issue #257 final v4.20.12 package applied with live-missing authority preserved")
