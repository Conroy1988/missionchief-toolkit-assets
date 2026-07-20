#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs/issue-259-lssm-parity-audit.md"


def around(source: str, marker: str, before: int, after: int) -> str:
    pos = source.find(marker)
    if pos < 0:
        return f"NOT FOUND: {marker}"
    return source[max(0, pos - before):min(len(source), pos + after)]


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
        "## Confirmed source capabilities",
        "",
        "- Nested `data-equipment-type` and `data-equipment-types` markers are already read from the unit and closest row.",
        "- Water, foam and pumping definitions already carry MissionChief progress-bar keys.",
        "- A MissionChief progress-bar reader already exists; integration and fixture coverage remain under audit.",
        "- Explicit tractive/trailer IDs already share one contribution key.",
        "- No LSSM `max_personnel_override` dependency exists.",
    ]
    contexts = [
        ("Equipment metadata", "function missionRequirementsEquipmentTypes", 300, 2600),
        ("Personnel capacity", "function missionRequirementsStaffCapacity", 300, 7000),
        ("Unit collection and tractive pairing", "function missionRequirementsCollectUnits", 300, 10000),
        ("Progress-bar reader", "function missionRequirementsProgressValue", 1200, 5000),
        ("Resolver integration", "function missionRequirementsResolve", 600, 16000),
        ("Observer integration", "function observeMissionRequirementsDocument", 500, 9000),
    ]
    for title, marker, before, after in contexts:
        sections.extend(["", f"## {title}", "", "```javascript", around(source, marker, before, after), "```"])
    REPORT.write_text("\n".join(sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
