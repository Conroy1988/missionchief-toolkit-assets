#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js").read_text(encoding="utf-8")
fixtures = json.loads((ROOT / ".github/fixtures/settings-ui-contract.json").read_text(encoding="utf-8"))


def section(start, end):
    left = source.index(start)
    right = source.index(end, left)
    return source[left:right]


panel = section("    function createPanel(", "    function ensureUi()")
actions = sorted(set(re.findall(r'data-action\s*=\s*["\']([^"\']+)', panel)))
settings = sorted(set(re.findall(r'data-setting\s*=\s*["\']([^"\']+)', panel)))
order_match = re.search(r"const COMMAND_SECTION_ORDER = Object\.freeze\(\[([^\]]+)\]\);", source)
assert order_match
tabs = sorted(re.findall(r"'([^']+)'", order_match.group(1)))
external_dynamic = {
    "profile-delete",
    "profile-load",
    "profile-save",
    "quickWheel",
    "toggle-command-bar",
    "toggle-map-fullscreen",
    "toggle-economy",
}
expected_actions = sorted(
    set(fixtures["actions"]) | (set(fixtures.get("dynamicActions", [])) - external_dynamic)
)
assert actions == expected_actions, (actions, expected_actions)
assert all(action in source for action in external_dynamic)
assert settings == sorted(fixtures["settings"])
assert tabs == sorted(fixtures["tabs"])
assert "delete merged.operationalWindow;" in source and "delete merged.missionRequirements;" in source
assert "data-operational-setting" not in source and "handleOperationalWindowSettingChange" not in source
print("Settings/UI contract passed for v9.")
