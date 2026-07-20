#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / ".github/development-packages/issue-273-exact-personnel-hotfix-v2.py"
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"
CONTRACT = ROOT / ".github/scripts/test_mission_requirements_contract.py"
CHANGELOG = ROOT / "CHANGELOG.md"
DOC = ROOT / "docs/issue-273-exact-personnel-hotfix.md"
DIST_USER = ROOT / "dist/MissionChief_Map_Command_Toolkit.user.js"
DIST_TEXT = ROOT / "dist/MissionChief_Map_Command_Toolkit.txt"
SUMS = ROOT / "dist/SHA256SUMS.txt"
MANIFEST = ROOT / "dist/release-manifest.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {text.count(old)}")
    return text.replace(old, new, 1)


def function_end(text: str, name: str) -> int:
    start = text.find(f"function {name}(")
    if start < 0:
        raise RuntimeError(f"missing function {name}")
    brace = text.find("{", start)
    depth = 0
    quote = None
    escape = False
    for index in range(brace, len(text)):
        char = text[index]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    raise RuntimeError(f"unterminated function {name}")


def rebuild_distribution() -> str:
    final = SOURCE.read_text(encoding="utf-8")
    DIST_USER.write_text(final, encoding="utf-8")
    DIST_TEXT.write_text(final, encoding="utf-8")
    digest = hashlib.sha256(final.encode("utf-8")).hexdigest()
    SUMS.write_text(
        f"{digest}  MissionChief_Map_Command_Toolkit.user.js\n{digest}  MissionChief_Map_Command_Toolkit.txt\n",
        encoding="utf-8",
    )
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest.update({
        "version": "4.20.17",
        "sha256": digest,
        "bytes": len(final.encode("utf-8")),
        "lines": len(final.splitlines()),
    })
    manifest.setdefault("metadata", {})["runtimeVersion"] = "4.20.17"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return digest


def main() -> None:
    subprocess.run(["python3", str(V2)], cwd=ROOT, check=True)

    source = SOURCE.read_text(encoding="utf-8")
    start = source.find("    const MISSION_REQUIREMENTS_VEHICLE_API_TTL_MS")
    if start < 0:
        raise RuntimeError("temporary independent vehicle API runtime not found")
    end = function_end(source, "missionRequirementsResolvedStaffCapacity")
    shared_runtime = r'''
    function missionRequirementsVehicleApiRecord(vehicleId) { const id = Number(vehicleId); if (!Number.isFinite(id) || id < 0) return null; return personalVehicleApiCache.get(String(id)) || personalVehicleApiCache.get(id) || null; }
    function missionRequirementsVehicleApiStaff(record) { const assigned = missionRequirementsOptionalNumber(record?.assigned_personnel_count ?? record?.assignedPersonnelCount ?? record?.personnel_count); if (assigned === null) return null; return missionRequirementsCapacity(assigned, assigned, true); }
    function missionRequirementsEnsureSharedVehicleData() { if (vehicleApiReady || vehicleApiFetchPromise) return; Promise.resolve(refreshPersonalVehicleData(false)).then(ready => { if (ready && !runtime.destroyed && state.missionRequirements) scheduleMissionRequirementsScan(0); }).catch(() => {}); }
    function missionRequirementsResolvedVehicleType(vehicleId, element) { const detected = missionRequirementsVehicleType(element); if (detected >= 0) return detected; const record = missionRequirementsVehicleApiRecord(vehicleId); const recordType = missionRequirementsOptionalNumber(record?.vehicle_type ?? record?.vehicleType ?? record?.vehicle_type_id ?? record?.vehicleTypeId); return recordType === null ? -1 : recordType; }
    function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element) { const native = missionRequirementsStaffCapacity(element); if (native?.known) return native; const exact = missionRequirementsVehicleApiStaff(missionRequirementsVehicleApiRecord(vehicleId)); if (exact) return exact; missionRequirementsEnsureSharedVehicleData(); return native || missionRequirementsDefaultStaffCapacity(typeId, element); }
'''
    source = source[:start] + shared_runtime + source[end:]
    SOURCE.write_text(source, encoding="utf-8")

    test = TEST.read_text(encoding="utf-8")
    test = replace_once(
        test,
        "    vehicleApiCache: missionRequirementsVehicleApiCache,",
        "    vehicleApiCache: personalVehicleApiCache,",
        "shared test cache export",
    )
    test = replace_once(
        test,
        "    missionRequirementsRecords: new Map(),",
        "    missionRequirementsRecords: new Map(),\n    personalVehicleApiCache: new Map(),\n    vehicleApiReady: true,\n    vehicleApiFetchPromise: null,\n    refreshPersonalVehicleData: () => Promise.resolve(true),",
        "shared API test context",
    )
    TEST.write_text(test, encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    contract = replace_once(
        contract,
        '        "function missionRequirementsVehicleApiRecord(vehicleId, now = Date.now())",\n        "function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element)",\n        "assigned_personnel_count",\n        "/api/vehicles/",\n        "data-personnel-training",',
        '        "function missionRequirementsVehicleApiRecord(vehicleId)",\n        "function missionRequirementsResolvedStaffCapacity(vehicleId, typeId, element)",\n        "personalVehicleApiCache",\n        "refreshPersonalVehicleData",\n        "assigned_personnel_count",\n        "data-personnel-training",',
        "shared API contract markers",
    )
    contract = replace_once(
        contract,
        '    assert "assigned_personnel_count" in source and "missionRequirementsVehicleApiStaff" in source, "exact vehicle personnel API evidence is required"\n',
        '    assert "assigned_personnel_count" in source and "missionRequirementsVehicleApiStaff" in source, "exact vehicle personnel API evidence is required"\n    assert "personalVehicleApiCache" in source and "refreshPersonalVehicleData(false)" in source, "Matrix must reuse the shared vehicle API cache"\n',
        "shared API contract assertion",
    )
    CONTRACT.write_text(contract, encoding="utf-8")

    CHANGELOG.write_text(
        CHANGELOG.read_text(encoding="utf-8").replace(
            "Level 2 Public Order Officer ARR selections now use each vehicle's exact MissionChief `assigned_personnel_count` when available",
            "Level 2 Public Order Officer ARR selections now use each vehicle's exact MissionChief `assigned_personnel_count` from the Toolkit's shared vehicle cache when available",
        ),
        encoding="utf-8",
    )
    DOC.write_text(
        DOC.read_text(encoding="utf-8")
        .replace(
            "The same-origin MissionChief `/api/vehicles/{id}` record supplies `assigned_personnel_count` when the dispatch table only exposes a type range.",
            "The existing shared MissionChief `/api/vehicles` cache supplies `assigned_personnel_count` when the dispatch table only exposes a type range.",
        )
        .replace(
            "Results are cached for sixty seconds and failed lookups back off for fifteen seconds.",
            "The Matrix reuses the Toolkit's existing cache, refresh throttling and error backoff rather than creating a second request path.",
        ),
        encoding="utf-8",
    )

    for path in list((ROOT / ".github/development-packages").glob("issue-273-*.py")):
        if path.resolve() != Path(__file__).resolve():
            path.unlink(missing_ok=True)
    for name in [
        "issue-273-validation-diagnostic.txt",
        "issue-273-validation-diagnostic-v2.txt",
        "issue-273-shared-vehicle-api-snippets.txt",
        "issue-273-runtime-snippets.txt",
        "issue-273-resolve-wrapped.txt",
    ]:
        (ROOT / "docs" / name).unlink(missing_ok=True)

    digest = rebuild_distribution()
    print(f"Prepared Toolkit 4.20.17 shared-cache exact-personnel hotfix: {digest}")


if __name__ == "__main__":
    main()
