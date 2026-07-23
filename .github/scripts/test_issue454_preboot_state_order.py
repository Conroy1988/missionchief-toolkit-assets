#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
text = SOURCE.read_text(encoding="utf-8")

settings_declaration = "    const OPERATIONAL_SUITE_SETTINGS_VERSION = 1;"
state_match = re.search(r"(?m)^\s*(?:const|let|var)\s+state\s*=\s*loadState\(\);\s*$", text)
default_function = "    function defaultOperationalWindowState"

assert text.count(settings_declaration) == 1
assert state_match is not None
state_initializer = state_match.group(0)
assert text.index(settings_declaration) < state_match.start()
assert state_match.start() < text.index(default_function)
assert "schemaVersion: OPERATIONAL_SUITE_SETTINGS_VERSION" in text
assert "// @version      5.0.3" in text
assert "version: '5.0.3'," in text
assert len(text.encode("utf-8")) > 500_000
assert text.rstrip().endswith("})();")
print("Issue #454 preboot state-order contract passed.")
