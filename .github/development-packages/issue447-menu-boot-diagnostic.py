#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / ".github" / "diagnostics" / "v5-menu-boot-diagnostic.txt"

text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()

def add_window(parts: list[str], label: str, needle: str, before: int = 30, after: int = 80) -> None:
    hits = [index for index, line in enumerate(lines) if needle in line]
    parts.append(f"\n===== {label} / {needle!r} / hits={len(hits)} =====\n")
    for number, index in enumerate(hits[:12], 1):
        start = max(0, index - before)
        end = min(len(lines), index + after + 1)
        parts.append(f"--- hit {number} at line {index + 1} ---\n")
        for cursor in range(start, end):
            parts.append(f"{cursor + 1:06d}: {lines[cursor]}\n")

parts: list[str] = [
    "V5_MENU_BOOT_DIAGNOSTIC\n",
    f"source_lines={len(lines)}\n",
]
for label, needle, before, after in (
    ("bootstrap", "function boot", 40, 220),
    ("DOMContentLoaded", "DOMContentLoaded", 30, 80),
    ("settings panel creator", "function createSettingsPanel", 30, 180),
    ("settings panel id", "panelId", 20, 80),
    ("launcher", "launcher", 20, 100),
    ("operational settings handler", "function handleOperationalWindowSettingChange", 40, 180),
    ("operational UI sync", "function operationalWindowSyncSettingsUi", 40, 140),
    ("operational query", "function operationalQuery", 30, 120),
    ("operational install", "function installOperational", 30, 180),
    ("operational coordinator", "operationalWindowCoordinator", 30, 140),
    ("main lifecycle", "installMain", 30, 120),
    ("startup metric", "toolkitBoot", 30, 100),
):
    add_window(parts, label, needle, before, after)

parts.append("\n===== FINAL 350 LINES =====\n")
for cursor in range(max(0, len(lines) - 350), len(lines)):
    parts.append(f"{cursor + 1:06d}: {lines[cursor]}\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote {OUTPUT.relative_to(ROOT)}")
