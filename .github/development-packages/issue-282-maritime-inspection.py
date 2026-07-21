#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
DATA = ROOT / "src/data/mission-requirements-en_GB.json"
REPORT = ROOT / "docs/issue-282-maritime-source-inspection.txt"


def append_context(output: list[str], lines: list[str], needle: str, radius: int = 35) -> None:
    matches = [index for index, line in enumerate(lines) if needle in line]
    output.append(f"\n===== {needle} ({len(matches)} matches) =====")
    for match_no, index in enumerate(matches, 1):
        start = max(0, index - radius)
        end = min(len(lines), index + radius + 1)
        output.append(f"\n--- match {match_no}: lines {start + 1}-{end} ---")
        for line_no in range(start, end):
            output.append(f"{line_no + 1:06d}: {lines[line_no]}")


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    output = [
        "Issue #282 maritime source inspection",
        f"Source lines: {len(lines)}",
        f"Data bytes: {DATA.stat().st_size}",
    ]

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
        append_context(output, lines, needle)

    output.append("\n===== DATASET =====")
    output.append(DATA.read_text(encoding="utf-8"))
    REPORT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)} ({REPORT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
