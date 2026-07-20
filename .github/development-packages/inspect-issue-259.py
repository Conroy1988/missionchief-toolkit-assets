#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    markers = [
        "missionRequirementsEquipmentTypes",
        "missionRequirementsStaffCapacity",
        "missionRequirementsCollectUnits",
        "missionRequirementsAggregate",
        "missionRequirementsResolve",
        "water-resource",
        "tractive_vehicle_id",
        "data-equipment-type",
        "max_personnel_override",
        "mission_water_bar_",
    ]
    sections = ["## Issue #259 marker inspection", "", "No branch or production files were changed."]
    for marker in markers:
        pos = source.find(marker)
        sample = "NOT FOUND" if pos < 0 else source[max(0, pos - 240):pos + 900]
        sections.extend(["", f"### `{marker}` — position `{pos}`", "```text", sample, "```"])
    body_file = ROOT / ".issue-259-inspection.md"
    body_file.write_text("\n".join(sections), encoding="utf-8")
    subprocess.run(["gh", "issue", "comment", "259", "--repo", os.environ.get("GITHUB_REPOSITORY", "Conroy1988/missionchief-toolkit-assets"), "--body-file", str(body_file)], check=True)
    body_file.unlink()


if __name__ == "__main__":
    main()
