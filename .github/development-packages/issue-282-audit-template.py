#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / ".github/fixtures/lssm-v4-en_GB-emv-baseline.json"
CROSS_SOURCE = ROOT / ".github/fixtures/mission-requirements-cross-source-en_GB.json"
TOOLKIT = ROOT / "src/data/mission-requirements-en_GB.json"
SOURCE = ROOT / "src/MissionChief_Map_Command_Toolkit.user.js"
RUNTIME_TEST = ROOT / ".github/scripts/test_mission_requirements_runtime.js"


def fold(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_caption(value: object) -> list[str]:
    return [part.strip() for part in str(value or "").split("|") if part.strip()]


def normalise_group(entries: list[dict]) -> list[dict]:
    return [{
        "texts": list(entry.get("texts", [])),
        "vehicles": [int(value) for value in entry.get("vehicles", [])],
        "equipment": list(entry.get("equipment", [])),
        "conditionalVehicles": entry.get("conditionalVehicles", {}),
        "factors": entry.get("factors", {}),
    } for entry in entries]


def capability_snapshot(entry: dict) -> dict:
    return {
        "key": entry["key"],
        "aliases": list(entry.get("aliases", [])),
        "types": [int(value) for value in entry.get("types", [])],
        "equipment": list(entry.get("equipment", [])),
        "conditionalVehicles": entry.get("conditionalVehicles", {}),
        "factors": entry.get("factors", {}),
        "pair": bool(entry.get("pair", False)),
    }


def parse_vehicle_captions(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    captions: dict[str, str] = {}
    pattern = re.compile(r"^\s*(\d+):\s*\{[\s\S]*?^\s*caption:\s*'([^']+)'", re.MULTILINE)
    for match in pattern.finditer(text):
        captions[str(int(match.group(1)))] = match.group(2)
    return captions


def parse_tractive_map(source: str) -> dict[str, list[int]]:
    match = re.search(r"const MISSION_REQUIREMENTS_TRACTIVE_TYPES = Object\.freeze\((\{[^\n]+\})\);", source)
    if not match:
        raise ValueError("MISSION_REQUIREMENTS_TRACTIVE_TYPES could not be parsed")
    parsed = json.loads(match.group(1))
    return {str(key): [int(value) for value in values] for key, values in parsed.items()}


def compare_toolkit(snapshot: dict, cross_source: dict) -> tuple[list[str], dict[str, list]]:
    toolkit = json.loads(TOOLKIT.read_text(encoding="utf-8"))
    source = SOURCE.read_text(encoding="utf-8")
    errors: list[str] = []
    findings: dict[str, list] = {
        "missingLssmAliases": [],
        "missionHelperLabelsMissingParserAlias": [],
        "vehicleCaptionsWithoutCapability": [],
        "expectedVehicleIdsMissing": [],
        "toolkitOnlyVehicleIds": [],
        "ambiguousLabels": [],
        "drift": [],
    }

    entries = [*toolkit.get("vehicleRequirements", []), *toolkit.get("staffRequirements", [])]
    by_key = {entry["key"]: entry for entry in entries}
    alias_index: dict[str, list[str]] = {}
    for entry in entries:
        for alias in entry.get("aliases", []):
            alias_index.setdefault(fold(alias), []).append(entry["key"])
    for alias, keys in sorted(alias_index.items()):
        unique = sorted(set(keys))
        if len(unique) > 1:
            finding = {"label": alias, "keys": unique}
            findings["ambiguousLabels"].append(finding)
            errors.append(f"ambiguous Toolkit alias {alias!r}: {unique}")

    expected_capabilities = {entry["key"]: entry for entry in cross_source.get("capabilities", [])}
    for key, expected in expected_capabilities.items():
        actual = by_key.get(key)
        if not actual:
            errors.append(f"missing Toolkit capability: {key}")
            continue
        normalised_actual = capability_snapshot(actual)
        if normalised_actual != expected:
            findings["drift"].append({"capability": key, "expected": expected, "actual": normalised_actual})
            errors.append(f"capability drift requires review: {key}")
    unexpected_capabilities = sorted(set(by_key) - set(expected_capabilities))
    if unexpected_capabilities:
        findings["drift"].append({"unexpectedToolkitCapabilities": unexpected_capabilities})
        errors.append(f"cross-source fixture missing Toolkit capabilities: {unexpected_capabilities}")

    for upstream_name, toolkit_name in (("vehicleRequirements", "vehicleRequirements"), ("staffRequirements", "staffRequirements")):
        toolkit_entries = toolkit.get(toolkit_name, [])
        by_alias = {fold(alias): entry for entry in toolkit_entries for alias in entry.get("aliases", [])}
        for upstream in snapshot.get(upstream_name, []):
            for text in upstream.get("texts", []):
                match = by_alias.get(fold(text))
                if not match:
                    findings["missingLssmAliases"].append(text)
                    errors.append(f"missing Toolkit alias: {text}")
                    continue
                missing_types = sorted(set(upstream.get("vehicles", [])) - set(match.get("types", [])))
                missing_equipment = sorted(set(upstream.get("equipment", [])) - set(match.get("equipment", [])))
                extra_types = sorted(set(match.get("types", [])) - set(upstream.get("vehicles", [])))
                if missing_types:
                    finding = {"label": text, "types": missing_types}
                    findings["expectedVehicleIdsMissing"].append(finding)
                    errors.append(f"{text}: missing vehicle types {missing_types}")
                if missing_equipment:
                    errors.append(f"{text}: missing equipment {missing_equipment}")
                if extra_types:
                    findings["toolkitOnlyVehicleIds"].append({"label": text, "types": extra_types})

    for group in cross_source.get("authoritativeLabels", []):
        expected_key = group["capability"]
        capability = by_key.get(expected_key)
        if not capability:
            errors.append(f"authoritative label group references missing capability: {expected_key}")
            continue
        if not set(group.get("types", [])) <= set(capability.get("types", [])):
            errors.append(f"{expected_key}: authoritative vehicle types are not fully supported")
        if bool(group.get("pair", False)) != bool(capability.get("pair", False)):
            errors.append(f"{expected_key}: pair contract differs from authoritative fixture")
        for label in group.get("labels", []):
            keys = sorted(set(alias_index.get(fold(label), [])))
            if keys != [expected_key]:
                errors.append(f"authoritative label {label!r} resolves to {keys or 'nothing'}, expected {expected_key}")

    helper_tokens = set()
    for mapping in cross_source.get("missionHelperMappings", []):
        token = mapping["token"]
        helper_tokens.add(token)
        expected_key = mapping["capability"]
        capability = by_key.get(expected_key)
        if not capability:
            errors.append(f"Mission Helper token {token} references missing capability {expected_key}")
            continue
        for label in mapping.get("labels", []):
            accepted = expected_key in alias_index.get(fold(label), [])
            if not accepted:
                finding = {"token": token, "label": label, "capability": expected_key}
                findings["missionHelperLabelsMissingParserAlias"].append(finding)
                if mapping.get("requireParserAlias", False):
                    errors.append(f"Mission Helper label {label!r} is not accepted by {expected_key}")
    expected_tokens = set(cross_source.get("missionHelperVehicleTokens", []))
    reviewed_unsupported = set(cross_source.get("reviewedUnsupportedMissionHelperTokens", []))
    unclassified_tokens = sorted(expected_tokens - helper_tokens - reviewed_unsupported)
    if unclassified_tokens:
        errors.append(f"Mission Helper vehicle tokens lack a canonical review: {unclassified_tokens}")

    used_types = {int(value) for entry in toolkit.get("vehicleRequirements", []) for value in entry.get("types", [])}
    captions = {int(key): value for key, value in cross_source.get("vehicleCaptions", {}).items()}
    missing_captions = sorted(used_types - set(captions))
    if missing_captions:
        errors.append(f"Toolkit vehicle types missing from pinned UK caption catalogue: {missing_captions}")
    for type_id, caption in sorted(captions.items()):
        keys = sorted(entry["key"] for entry in toolkit.get("vehicleRequirements", []) if type_id in entry.get("types", []))
        if not keys:
            findings["vehicleCaptionsWithoutCapability"].append({"type": type_id, "caption": caption})

    required_markers = [
        "MISSION_REQUIREMENTS_TRACTIVE_TYPES",
        "missionRequirementsProgressValue(candidate, requirement.definition.bar, 'missing')",
        "[data-equipment-type], [data-equipment-types]",
        "tractive_random",
        "data-min-personnel",
        "data-max-personnel",
        "definition.pair !== true && compatibleTractiveTypes.length > 0",
        "Inland Rescue Boat (Trailer)",
        "Seagoing Vessel",
    ]
    for marker in required_markers:
        if marker not in source:
            errors.append(f"missing runtime contract marker: {marker}")
    if "const rowText = missionRequirementsCapabilityLabel" in source:
        errors.append("whole-row text is still accepted as personnel-training proof")
    if "v4.lss-manager.de" in source or "max_personnel_override" in source:
        errors.append("Toolkit source contains an LSSM runtime dependency")
    try:
        actual_tractive = parse_tractive_map(source)
        if actual_tractive != cross_source.get("tractiveTypes", {}):
            findings["drift"].append({"tractiveTypes": {"expected": cross_source.get("tractiveTypes", {}), "actual": actual_tractive}})
            errors.append("tractive compatibility map drift requires review")
    except ValueError as exc:
        errors.append(str(exc))
    return errors, findings


def compare_upstream(snapshot: dict, cross_source: dict, upstream_root: Path) -> list[str]:
    errors: list[str] = []
    for name, metadata in cross_source.get("files", {}).items():
        path = upstream_root / metadata["path"]
        if not path.exists():
            errors.append(f"upstream {name} file not found: {path}")
            continue
        actual_hash = sha256(path)
        if actual_hash != metadata["sha256"]:
            errors.append(f"upstream {name} hash drift: expected {metadata['sha256']}, got {actual_hash}")

    catalogue_path = upstream_root / snapshot["files"]["catalogue"]["path"]
    if catalogue_path.exists():
        current = json.loads(catalogue_path.read_text(encoding="utf-8"))["enhancedMissingVehicles"]
        for key, current_entries in (("vehicleRequirements", current.get("vehiclesByRequirement", [])), ("staffRequirements", current.get("staff", []))):
            expected = snapshot.get(key, [])
            actual = normalise_group(current_entries)
            if actual != expected:
                expected_aliases = {fold(text) for entry in expected for text in entry.get("texts", [])}
                actual_aliases = {fold(text) for entry in actual for text in entry.get("texts", [])}
                errors.append(f"{key} drift: added={sorted(actual_aliases - expected_aliases)}, removed={sorted(expected_aliases - actual_aliases)}; inspect types/equipment/factors/conditions")

    helper_meta = cross_source["files"]["missionHelper"]
    helper_path = upstream_root / helper_meta["path"]
    if helper_path.exists():
        helper = json.loads(helper_path.read_text(encoding="utf-8"))
        actual_captions = helper.get("vehicles", {}).get("captions", {})
        expected_captions = cross_source.get("missionHelperVehicleCaptions", {})
        if actual_captions != expected_captions:
            added = sorted(set(actual_captions) - set(expected_captions))
            removed = sorted(set(expected_captions) - set(actual_captions))
            changed = sorted(key for key in set(actual_captions) & set(expected_captions) if actual_captions[key] != expected_captions[key])
            errors.append(f"Mission Helper caption drift: added={added}, removed={removed}, changed={changed}")

    vehicle_meta = cross_source["files"]["vehicles"]
    vehicle_path = upstream_root / vehicle_meta["path"]
    if vehicle_path.exists():
        actual_vehicle_captions = parse_vehicle_captions(vehicle_path)
        if actual_vehicle_captions != cross_source.get("vehicleCaptions", {}):
            added = sorted(set(actual_vehicle_captions) - set(cross_source.get("vehicleCaptions", {})))
            removed = sorted(set(cross_source.get("vehicleCaptions", {})) - set(actual_vehicle_captions))
            changed = sorted(key for key in set(actual_vehicle_captions) & set(cross_source.get("vehicleCaptions", {})) if actual_vehicle_captions[key] != cross_source["vehicleCaptions"][key])
            errors.append(f"UK vehicle caption drift: added={added}, removed={removed}, changed={changed}")
    return errors


def markdown_report(report: dict) -> str:
    lines = [
        "# Mission Requirements cross-source compatibility audit",
        "",
        f"- Status: **{report['status']}**",
        f"- Pinned LSSM commit: `{report['pinnedLssmCommit']}`",
        f"- Runtime parser/resolver fixtures: **{'passed' if report['runtimePassed'] else 'not run'}**",
        f"- Errors: **{len(report['errors'])}**",
        "",
    ]
    if report["errors"]:
        lines.extend(["## Blocking findings", "", *[f"- {item}" for item in report["errors"]], ""])
    lines.extend(["## Actionable review inventory", ""])
    for name, items in report["findings"].items():
        lines.append(f"### {name}")
        lines.append("")
        if not items:
            lines.append("- None")
        else:
            for item in items:
                lines.append(f"- `{json.dumps(item, sort_keys=True)}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path)
    parser.add_argument("--skip-runtime", action="store_true")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    snapshot = json.loads(BASELINE.read_text(encoding="utf-8"))
    cross_source = json.loads(CROSS_SOURCE.read_text(encoding="utf-8"))
    errors, findings = compare_toolkit(snapshot, cross_source)
    if args.upstream_root:
        errors.extend(compare_upstream(snapshot, cross_source, args.upstream_root))

    runtime_passed = False
    if not args.skip_runtime:
        runtime = subprocess.run(["node", str(RUNTIME_TEST)], cwd=ROOT, text=True, capture_output=True)
        if runtime.stdout:
            print(runtime.stdout, end="")
        if runtime.returncode != 0:
            if runtime.stderr:
                print(runtime.stderr, end="", file=sys.stderr)
            errors.append("production parser/resolver runtime fixtures failed")
        else:
            runtime_passed = True

    report = {
        "schemaVersion": 1,
        "status": "passed" if not errors else "failed",
        "pinnedLssmCommit": cross_source["pinnedLssmCommit"],
        "runtimePassed": runtime_passed or args.skip_runtime,
        "errors": errors,
        "findings": findings,
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown_report(report), encoding="utf-8")

    if errors:
        print("LSSM cross-source compatibility audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"LSSM cross-source compatibility audit passed against {cross_source['pinnedLssmCommit']}")
    for name, items in findings.items():
        print(f"- {name}: {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
