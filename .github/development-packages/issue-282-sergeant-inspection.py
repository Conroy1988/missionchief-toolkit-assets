#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
REPORT = ROOT / "docs/issue-282-police-sergeant-source-inspection.txt"


def extract_function(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.find(marker)
    if start < 0:
        return f"MISSING: {name}"
    opening = source.find("{", start)
    depth = 0
    quote = None
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        else:
            if char in ("'", '"', "`"):
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return source[start:index + 1]
    return f"UNTERMINATED: {name}"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    output = ["Issue #282 Police Sergeant responding source inspection"]
    for name in (
        "missionRequirementsMetadataValues",
        "missionRequirementsArrCapabilityState",
        "missionRequirementsVehicleApiRecord",
        "missionRequirementsVehicleApiStaff",
        "missionRequirementsResolvedStaffCapacity",
        "missionRequirementsCollectUnits",
        "missionRequirementsUnitContribution",
        "missionRequirementsResolve",
    ):
        output.extend((f"\n===== {name} =====", extract_function(source, name)))
    output.append("\n===== SERGEANT / CACHE SOURCE LINES =====")
    for line_no, line in enumerate(source.splitlines(), 1):
        folded = line.casefold()
        if any(token in folded for token in ("police sergeant", "police_sergeant", "assigned_personnel", "personalvehicleapicache", "arrcapability")):
            output.append(f"{line_no:06d}: {line}")
    REPORT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)} ({REPORT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
