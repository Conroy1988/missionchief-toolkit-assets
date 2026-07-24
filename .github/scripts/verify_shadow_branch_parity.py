#!/usr/bin/env python3
"""Verify Issue #41 operational branch roles and governed-file policy.

Mirrored paths must remain byte-identical to the current checkout. Operational
paths may differ, but must satisfy their reviewed schemas and cross-file
consistency rules. This verifier is read-only and never updates a ref.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".github" / "shadow-branch-policy.json"
ROLE_PATH = ".github/branch-role.json"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[+-][0-9A-Za-z.-]+)?$")
FULL_HASH = re.compile(r"^[0-9a-f]{64}$")


def git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=not binary,
    )
    return result.stdout


def branch_ref(branch: str) -> str:
    return f"refs/remotes/origin/{branch}"


def branch_file(branch: str, path: str) -> bytes:
    return git("show", f"{branch_ref(branch)}:{path}", binary=True)  # type: ignore[return-value]


def branch_json(branch: str, path: str) -> dict:
    value = json.loads(branch_file(branch, path).decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at {branch}:{path}")
    return value


def semver_tuple(value: str) -> tuple[int, int, int]:
    core = value.split("+", 1)[0].split("-", 1)[0]
    parts = core.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"Invalid semantic version: {value!r}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def load_policy() -> dict:
    value = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Operational branch policy must be a JSON object")
    expected = {
        "schemaVersion": 1,
        "mode": "shadow-rehearsal",
        "mainAuthorityPreserved": True,
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            raise ValueError(
                f"Operational branch policy {key}={value.get(key)!r}, expected {expected_value!r}"
            )
    branches = value.get("branches")
    if not isinstance(branches, dict) or set(branches) != {"release-state", "distribution"}:
        raise ValueError("Operational policy must define release-state and distribution")
    for branch, policy in branches.items():
        validate_path_classes(branch, policy)
    return value


def validate_path_classes(branch: str, policy: dict) -> None:
    governed = policy.get("governedPaths")
    mirrored = policy.get("mirroredPaths")
    operational = policy.get("operationalPaths")
    writers = policy.get("operationalWriters")
    if not all(isinstance(value, list) for value in [governed, mirrored, operational, writers]):
        raise ValueError(f"{branch} path classes and writers must be lists")
    if len(governed) != len(set(governed)):
        raise ValueError(f"{branch} governedPaths contains duplicates")
    if set(mirrored) & set(operational):
        raise ValueError(f"{branch} mirrored and operational paths overlap")
    if set(governed) != set(mirrored) | set(operational):
        raise ValueError(f"{branch} path classes do not partition governedPaths")
    if policy.get("externalConsumersEnabled") is not False:
        raise ValueError(f"{branch} external consumers must remain disabled")

    if branch == "release-state":
        expected_operational = [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
        ]
        expected_writers = [
            ".github/workflows/greasyfork-release-monitor.yml",
            ".github/workflows/release-recovery.yml",
        ]
        if mirrored != [] or operational != expected_operational:
            raise ValueError("release-state must keep all recovery-ledger paths operational")
        if writers != expected_writers:
            raise ValueError("release-state operational writers changed")
    if branch == "distribution":
        if operational or writers:
            raise ValueError("distribution cannot have operational paths before cutover")
        if mirrored != governed:
            raise ValueError("distribution paths must remain mirrored before cutover")


def validate_role(branch: str, role: dict, policy: dict) -> list[str]:
    errors: list[str] = []
    expected = {
        "schemaVersion": 1,
        "branch": branch,
        "mode": "shadow-rehearsal",
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
    }
    for key, value in expected.items():
        if role.get(key) != value:
            errors.append(f"{branch} role {key}={role.get(key)!r}, expected {value!r}")
    expected_allowed = [*policy["governedPaths"], ROLE_PATH]
    if role.get("allowedMutablePaths") != expected_allowed:
        errors.append(f"{branch} allowedMutablePaths differs from reviewed policy")
    if "main remains authoritative" not in str(role.get("authority") or ""):
        errors.append(f"{branch} role no longer preserves main source authority")
    return errors


def validate_operational_content(path: str, content: bytes) -> tuple[bool, str, dict]:
    metadata: dict[str, object] = {}
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return False, "content is not UTF-8", metadata

    if path == "status/release-dashboard.json":
        try:
            dashboard = json.loads(text)
        except json.JSONDecodeError:
            return False, "dashboard is not valid JSON", metadata
        if not isinstance(dashboard, dict):
            return False, "dashboard is not a JSON object", metadata
        latest = dashboard.get("latestRelease") or {}
        version = str(latest.get("version") or "")
        current = str(dashboard.get("currentVersion") or "")
        if not SEMVER.fullmatch(version) or current != version:
            return False, "dashboard current/latest version is invalid", metadata
        if not isinstance(dashboard.get("status"), dict):
            return False, "dashboard status object is missing", metadata
        sha256 = str(latest.get("sha256") or "")
        if sha256 and not FULL_HASH.fullmatch(sha256):
            return False, "dashboard release SHA-256 is invalid", metadata
        metadata.update({"version": version, "dashboard": dashboard})
        return True, f"operational dashboard v{version}", metadata

    if path == "status/README.md":
        if not text.startswith("# MissionChief Toolkit Control Panel"):
            return False, "rendered dashboard heading is invalid", metadata
        match = re.search(r"## Current version: `([^`]+)`", text)
        if not match or not SEMVER.fullmatch(match.group(1)):
            return False, "rendered dashboard version is invalid", metadata
        metadata["version"] = match.group(1)
        return True, f"rendered dashboard v{match.group(1)}", metadata

    if path == "status/update-manifest.json":
        try:
            manifest = json.loads(text)
        except json.JSONDecodeError:
            return False, "stable manifest is not valid JSON", metadata
        if not isinstance(manifest, dict):
            return False, "stable manifest is not a JSON object", metadata
        version = str(manifest.get("version") or "")
        sha256 = str(manifest.get("sha256") or "")
        if manifest.get("schemaVersion") != 1 or manifest.get("channel") != "stable":
            return False, "stable manifest schema/channel is invalid", metadata
        if not SEMVER.fullmatch(version) or not FULL_HASH.fullmatch(sha256):
            return False, "stable manifest version or SHA-256 is invalid", metadata
        metadata.update({"version": version, "manifest": manifest})
        return True, f"stable manifest v{version}", metadata

    if path == ".github/greasyfork-version.txt":
        value = text.strip()
        if not SEMVER.fullmatch(value):
            return False, f"fallback tracker is not a stable semantic version: {value!r}", metadata
        metadata["version"] = value
        return True, f"announcement tracker v{value}", metadata

    return False, f"no operational schema is defined for {path}", metadata


def cross_validate_release_state(files: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    by_path = {str(file["path"]): file for file in files}
    dashboard_version = str((by_path["status/release-dashboard.json"].get("metadata") or {}).get("version") or "")
    readme_version = str((by_path["status/README.md"].get("metadata") or {}).get("version") or "")
    manifest_version = str((by_path["status/update-manifest.json"].get("metadata") or {}).get("version") or "")
    tracker_version = str((by_path[".github/greasyfork-version.txt"].get("metadata") or {}).get("version") or "")

    if dashboard_version and readme_version and dashboard_version != readme_version:
        errors.append("release-state dashboard and rendered Markdown versions differ")
    if dashboard_version and manifest_version:
        if semver_tuple(manifest_version) > semver_tuple(dashboard_version):
            errors.append("release-state stable manifest is ahead of the recovery dashboard")
    if dashboard_version and tracker_version:
        if semver_tuple(tracker_version) > semver_tuple(dashboard_version):
            errors.append("release-state announcement tracker is ahead of the recovery dashboard")
    return errors


def compare_branch(branch: str, policy: dict) -> dict:
    role = branch_json(branch, ROLE_PATH)
    errors = validate_role(branch, role, policy)
    files: list[dict[str, object]] = []
    mirrored = set(policy["mirroredPaths"])
    operational = set(policy["operationalPaths"])

    for path in policy["governedPaths"]:
        local_path = ROOT / path
        try:
            remote = branch_file(branch, path)
        except subprocess.CalledProcessError:
            errors.append(f"{branch} is missing governed path {path}")
            files.append({"path": path, "mode": "missing", "acceptable": False})
            continue
        local = local_path.read_bytes() if local_path.is_file() else None
        equal = local == remote if local is not None else False

        if path in mirrored:
            acceptable = local is not None and equal
            reason = "byte-identical" if acceptable else "mirror-mismatch"
            metadata: dict[str, object] = {}
            if not acceptable:
                errors.append(f"{branch}:{path} differs from current checkout")
            mode = "mirror"
        elif path in operational:
            acceptable, reason, metadata = validate_operational_content(path, remote)
            if not acceptable:
                errors.append(f"{branch}:{path} is invalid: {reason}")
            mode = "operational"
        else:
            acceptable = False
            reason = "unclassified"
            metadata = {}
            mode = "unknown"
            errors.append(f"{branch}:{path} has no reviewed path class")

        files.append(
            {
                "path": path,
                "mode": mode,
                "equal": equal,
                "acceptable": acceptable,
                "reason": reason,
                "bytes": len(remote),
                "metadata": metadata,
            }
        )

    if branch == "release-state" and all(bool(file.get("acceptable")) for file in files):
        errors.extend(cross_validate_release_state(files))
    return {
        "branch": branch,
        "purpose": policy["purpose"],
        "commit": str(git("rev-parse", branch_ref(branch))).strip(),
        "role": role,
        "files": files,
        "acceptable": not errors and all(bool(file.get("acceptable")) for file in files),
        "errors": errors,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Issue #41 operational branch governance",
        "",
        f"- State: **{'acceptable' if report['acceptable'] else 'mismatch'}**",
        f"- Source commit: `{report['sourceCommit']}`",
        f"- Generated: `{report['generatedAt']}`",
        "- External consumers changed: **no**",
        "- Public `main` changed: **no**",
        "",
    ]
    for branch in report["branches"]:
        lines.extend(
            [
                f"## `{branch['branch']}`",
                "",
                f"- Commit: `{branch['commit']}`",
                f"- Role valid: **{'yes' if not branch['errors'] else 'no'}**",
                f"- Governed paths acceptable: **{'yes' if branch['acceptable'] else 'no'}**",
                "",
            ]
        )
        for file in branch["files"]:
            marker = "✅" if file.get("acceptable") else "❌"
            mode = str(file.get("mode") or "unknown")
            equality = "equal" if file.get("equal") else "independent"
            lines.append(f"- {marker} `{file['path']}` — {mode}, {equality}: {file.get('reason', '')}")
        if branch["errors"]:
            lines.extend(["", "### Errors", ""])
            lines.extend(f"- {error}" for error in branch["errors"])
        lines.append("")
    return "\n".join(lines)


def self_test() -> None:
    policy = {
        "purpose": "test",
        "governedPaths": [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
        ],
        "mirroredPaths": [],
        "operationalPaths": [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
        ],
        "operationalWriters": [
            ".github/workflows/greasyfork-release-monitor.yml",
            ".github/workflows/release-recovery.yml",
        ],
        "externalConsumersEnabled": False,
    }
    validate_path_classes("release-state", policy)
    role = {
        "schemaVersion": 1,
        "branch": "release-state",
        "mode": "shadow-rehearsal",
        "authority": "main remains authoritative until cutover",
        "allowedMutablePaths": [*policy["governedPaths"], ROLE_PATH],
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
    }
    assert not validate_role("release-state", role, policy)
    assert validate_operational_content(".github/greasyfork-version.txt", b"5.0.7\n")[0]
    assert not validate_operational_content(".github/greasyfork-version.txt", b"latest\n")[0]
    assert semver_tuple("5.0.7") < semver_tuple("5.0.8")
    print("Shadow branch parity self-tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.json_output or not args.markdown_output:
        raise SystemExit("--json-output and --markdown-output are required")

    policy = load_policy()
    branches = [
        compare_branch(branch, branch_policy)
        for branch, branch_policy in policy["branches"].items()
    ]
    acceptable = all(branch["acceptable"] for branch in branches)
    report = {
        "schemaVersion": 3,
        "state": "acceptable" if acceptable else "mismatch",
        "acceptable": acceptable,
        "sourceCommit": str(git("rev-parse", "HEAD")).strip(),
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "publicMainChanged": False,
        "externalConsumersChanged": False,
        "branches": branches,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if acceptable else 1


if __name__ == "__main__":
    raise SystemExit(main())
