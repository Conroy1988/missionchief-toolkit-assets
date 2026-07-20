#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".github/fixtures/lssm-v4-en_GB-emv-baseline.json"
TOOLKIT = ROOT / "src/data/mission-requirements-en_GB.json"
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"


def fold(value: str) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().casefold()


def normalise_group(entries: list[dict]) -> list[dict]:
    return [{
        "texts": list(entry.get("texts", [])),
        "vehicles": [int(value) for value in entry.get("vehicles", [])],
        "equipment": list(entry.get("equipment", [])),
        "conditionalVehicles": entry.get("conditionalVehicles", {}),
        "factors": entry.get("factors", {}),
    } for entry in entries]


def compare_toolkit(snapshot: dict) -> list[str]:
    toolkit = json.loads(TOOLKIT.read_text(encoding="utf-8"))
    errors: list[str] = []
    for upstream_name, toolkit_name in (("vehicleRequirements", "vehicleRequirements"), ("staffRequirements", "staffRequirements")):
        toolkit_entries = toolkit.get(toolkit_name, [])
        by_alias = {}
        for entry in toolkit_entries:
            for alias in entry.get("aliases", []):
                by_alias[fold(alias)] = entry
        for upstream in snapshot.get(upstream_name, []):
            for text in upstream.get("texts", []):
                match = by_alias.get(fold(text))
                if not match:
                    errors.append(f"missing Toolkit alias: {text}")
                    continue
                missing_types = sorted(set(upstream.get("vehicles", [])) - set(match.get("types", [])))
                missing_equipment = sorted(set(upstream.get("equipment", [])) - set(match.get("equipment", [])))
                if missing_types:
                    errors.append(f"{text}: missing vehicle types {missing_types}")
                if missing_equipment:
                    errors.append(f"{text}: missing equipment {missing_equipment}")
    source = SOURCE.read_text(encoding="utf-8")
    required = [
        "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
        "missionRequirementsProgressValue(candidate, requirement.definition.bar, 'missing')",
        "[data-equipment-type], [data-equipment-types]",
        "tractive_random",
        "data-min-personnel",
        "data-max-personnel",
    ]
    for marker in required:
        if marker not in source:
            errors.append(f"missing runtime contract marker: {marker}")
    if "const rowText = missionRequirementsCapabilityLabel" in source:
        errors.append("whole-row text is still accepted as personnel-training proof")
    if "v4.lss-manager.de" in source or "max_personnel_override" in source:
        errors.append("Toolkit source contains an LSSM runtime dependency")
    return errors


def compare_upstream(snapshot: dict, upstream_root: Path) -> list[str]:
    catalogue_path = upstream_root / snapshot["files"]["catalogue"]["path"]
    if not catalogue_path.exists():
        return [f"upstream catalogue not found: {catalogue_path}"]
    current = json.loads(catalogue_path.read_text(encoding="utf-8"))["enhancedMissingVehicles"]
    errors = []
    for key, current_entries in (("vehicleRequirements", current.get("vehiclesByRequirement", [])), ("staffRequirements", current.get("staff", []))):
        expected = snapshot.get(key, [])
        actual = normalise_group(current_entries)
        if actual != expected:
            expected_aliases = {fold(text) for entry in expected for text in entry.get("texts", [])}
            actual_aliases = {fold(text) for entry in actual for text in entry.get("texts", [])}
            added = sorted(actual_aliases - expected_aliases)
            removed = sorted(expected_aliases - actual_aliases)
            errors.append(f"{key} drift: added={added}, removed={removed}; inspect types/equipment/factors/conditions")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path)
    args = parser.parse_args()
    snapshot = json.loads(BASELINE.read_text(encoding="utf-8"))
    errors = compare_toolkit(snapshot)
    if args.upstream_root:
        errors.extend(compare_upstream(snapshot, args.upstream_root))
    if errors:
        print("LSSM compatibility audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"LSSM compatibility audit passed against {snapshot['pinnedCommit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
