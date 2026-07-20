#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"


def function_slice(source: str, name: str) -> str:
    marker = f"    function {name}("
    start = source.index(marker)
    next_function = source.find("\n    function ", start + len(marker))
    next_section = source.find("\n    const ", start + len(marker))
    candidates = [value for value in (next_function, next_section) if value > start]
    end = min(candidates) if candidates else min(len(source), start + 12000)
    return source[start:end].rstrip()


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    names = [
        "missionRequirementsEquipmentTypes",
        "missionRequirementsStaffCapacity",
        "missionRequirementsCollectUnits",
        "missionRequirementsAggregate",
        "missionRequirementsResolve",
    ]
    sections = ["## Issue #259 disposable source inspection", "", "No branch or production files were changed by this inspection."]
    for name in names:
        sections.extend(["", f"### `{name}`", "```javascript", function_slice(source, name)[:9000], "```"])
    resource_pos = source.index("water-resource")
    sections.extend(["", "### `water-resource` definition context", "```javascript", source[max(0, resource_pos - 900):resource_pos + 1800], "```"])
    body_file = ROOT / ".issue-259-inspection.md"
    body_file.write_text("\n".join(sections), encoding="utf-8")
    subprocess.run(["gh", "issue", "comment", "259", "--repo", os.environ["GITHUB_REPOSITORY"], "--body-file", str(body_file)], check=True)
    body_file.unlink()


if __name__ == "__main__":
    main()
