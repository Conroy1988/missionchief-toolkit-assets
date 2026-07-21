#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src/data/mission-requirements-en_GB.json"


def print_context(lines: list[str], needle: str, radius: int = 35) -> None:
    matches = [index for index, line in enumerate(lines) if needle in line]
    print(f"\n===== {needle} ({len(matches)} matches) =====")
    for match_no, index in enumerate(matches, 1):
        start = max(0, index - radius)
        end = min(len(lines), index + radius + 1)
        print(f"\n--- match {match_no}: lines {start + 1}-{end} ---")
        for line_no in range(start, end):
            print(f"{line_no + 1:06d}: {lines[line_no]}")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    print(f"Source lines: {len(lines)}")
    print(f"Data bytes: {DATA.stat().st_size}")

    for needle in (
        'boat-trailer-or-inland-rescue-boat',
        'ilb-or-alb',
        'MISSION_REQUIREMENTS_TRACTIVE_TYPES',
        'tractive_random',
        'tractive_vehicle_id',
        'tractive_vehicle',
        'function missionRequirementsVehicleId',
        'function missionRequirementsVehicleType',
        'function missionRequirementsCollectUnits',
        'function missionRequirementsAggregate',
        'function missionRequirementsDefinitionCondition',
        'contributionKey',
    ):
        print_context(lines, needle)

    print("\n===== DATASET =====")
    print(DATA.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
