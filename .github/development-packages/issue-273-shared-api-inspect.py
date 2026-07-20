#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "docs/issue-273-shared-vehicle-api-snippets.txt"


def block(text: str, marker: str, before: int = 1200, after: int = 5000) -> str:
    pos = text.find(marker)
    if pos < 0:
        return f"MISSING: {marker}"
    return text[max(0, pos - before):min(len(text), pos + after)]


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    sections = []
    for marker in [
        "/api/vehicles",
        "function rebuildCustomVehicleClassificationCache()",
        "function customVehicleClassificationForId(vehicleId)",
        "__MCMS_CUSTOM_VEHICLE_CLASSIFICATIONS__",
        "CUSTOM VEHICLE BADGES START",
    ]:
        sections.append(f"=== {marker} ===\n{block(source, marker)}")
    OUTPUT.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
