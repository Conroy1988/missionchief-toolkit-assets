#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs/issue-259-lssm-parity-audit.md"


def slice_from(source: str, marker: str, limit: int = 18000) -> str:
    start = source.find(marker)
    if start < 0:
        return f"NOT FOUND: {marker}"
    next_function = source.find("\n    function ", start + len(marker))
    next_const = source.find("\n    const ", start + len(marker))
    ends = [x for x in (next_function, next_const) if x > start]
    end = min(ends) if ends else min(len(source), start + limit)
    return source[start:end].rstrip()


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    sections = [
        "# Issue #259 — LSSM Mission Requirements parity audit",
        "",
        "## Pinned baselines",
        "",
        "- Toolkit: `8619c79b794ad7241e0a37a0c91a6176daee7911` (v4.20.12)",
        "- LSSM V.4: `4f731e1d6d009cbf2129530fb31d10177b21a52a` (4.7.12+20260720.0722)",
        "",
        "## Audit stage",
        "",
        "This generated stage records the current Toolkit implementation before any Issue #259 runtime change.",
    ]
    markers = [
        "    function missionRequirementsEquipmentTypes(",
        "    function missionRequirementsStaffCapacity(",
        "    function missionRequirementsCollectUnits(",
        "    function missionRequirementsAggregate(",
        "    function missionRequirementsProgressValue(",
        "    function missionRequirementsResolve(",
    ]
    for marker in markers:
        name = marker.strip().removeprefix("function ").split("(", 1)[0]
        sections.extend(["", f"## `{name}`", "", "```javascript", slice_from(source, marker), "```"])
    REPORT.write_text("\n".join(sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
