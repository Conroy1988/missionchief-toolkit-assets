#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs/issue-259-lssm-parity-audit.md"


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
    sections = [
        "# Issue #259 — LSSM Mission Requirements parity audit",
        "",
        "## Pinned baselines",
        "",
        "- Toolkit: `8619c79b794ad7241e0a37a0c91a6176daee7911` (v4.20.12)",
        "- LSSM V.4: `4f731e1d6d009cbf2129530fb31d10177b21a52a` (4.7.12+20260720.0722)",
        "",
        "## Source marker inspection",
        "",
        "This section is generated from the canonical Toolkit source during the guarded development-package preflight.",
    ]
    for marker in markers:
        pos = source.find(marker)
        sample = "NOT FOUND" if pos < 0 else source[max(0, pos - 240):pos + 900]
        sections.extend(["", f"### `{marker}` — position `{pos}`", "```text", sample, "```"])
    REPORT.write_text("\n".join(sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
