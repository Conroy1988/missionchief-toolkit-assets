#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "issue-176-source-map.txt"
TESTS = [
    ROOT / ".github" / "scripts" / "test_mission_requirements_runtime.js",
    ROOT / ".github" / "scripts" / "test_settings_ui_contract.py",
]

patterns = [
    "vehicle_type_caption",
    "/api/vehicles",
    "api/vehicles",
    "vehicle_show_table_body_all",
    "vehicle_select_table",
    "vehicle_type_id",
    "missionRequirements",
    "mission requirements",
    "available units",
    "Available Units",
    "settingsDefinitions",
    "SETTING",
    "DEFAULT",
    "MutationObserver",
]


def excerpts(path: Path, terms: list[str], radius: int = 22) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    blocks: list[str] = []
    seen: set[tuple[int, int]] = set()
    for term in terms:
        matches = [index for index, line in enumerate(lines) if term.lower() in line.lower()]
        blocks.append(f"\n===== {path.relative_to(ROOT)} :: {term!r} ({len(matches)} matches) =====")
        for index in matches[:24]:
            start = max(0, index - radius)
            end = min(len(lines), index + radius + 1)
            key = (start, end)
            if key in seen:
                continue
            seen.add(key)
            blocks.append(f"--- lines {start + 1}-{end} (match {index + 1}) ---")
            blocks.extend(f"{number + 1:06d}: {lines[number]}" for number in range(start, end))
    return blocks

output: list[str] = ["Issue #176 source inspection", ""]
output.extend(excerpts(SOURCE, patterns))
for test in TESTS:
    if test.exists():
        output.extend(excerpts(test, ["missionRequirements", "settings", "vehicle", "toggle"], radius=16))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
