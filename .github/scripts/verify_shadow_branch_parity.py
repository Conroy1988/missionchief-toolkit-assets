#!/usr/bin/env python3
"""Verify Issue #41 operational branch roles and governed-file policy.

Mirrored paths must remain byte-identical to the current checkout. Transitional
operational paths may differ, but must satisfy their reviewed schema. This
verifier is read-only and never creates, updates or force-pushes a ref.
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


def load_policy() -> dict:
    value = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Shadow branch policy must be a JSON object")
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
                f"Shadow branch policy {key}={value.get(key)!r}, expected {expected_value!r}"
            )
    branches = value.get("branches")
    if not isinstance(branches, dict) or set(branches) != {"release-state", "distribution"}:
        raise ValueError("Shadow branch policy must define release-state and distribution")
    for branch, policy in branches.items():
        validate_path_classes(branch, policy)
    return value


def validate_path_classes(branch: str, policy: dict) -> None:
    governed = policy.get("governedPaths")
    mirrored = policy.get("mirroredPaths")
    operational = policy.get("operationalPaths")
    if not all(isinstance(value, list) for value in [governed, mirrored, operational]):
        raise ValueError(f"{branch} path classes must be lists")
    if len(governed) != len(set(governed)):
        raise ValueError(f"{branch} governedPaths contains duplicates")
    if set(mirrored) & set(operational):
        raise ValueError(f"{branch} mirrored and operational paths overlap")
    if set(governed) != set(mirrored) | set(operational):
        raise ValueError(f"{branch} path classes do not partition governedPaths")
    if branch == "release-state":
        if operational != [".github/greasyfork-version.txt"]:
            raise ValueError("release-state operational path must remain the fallback tracker only")
        if policy.get("operationalWriter") != ".github/workflows/greasyfork-release-monitor.yml":
            raise ValueError("release-state operational writer changed")
    if branch == "distribution" and operational:
        raise ValueError("distribution cannot have operational paths before cutover")
    if policy.get("externalConsumersEnabled") is not False:
        raise ValueError(f"{branch} external consumers must remain disabled")


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
    authority = str(role.get("authority") or "")
    if "main remains authoritative" not in authority:
        errors.append(f"{branch} role does not preserve main authority during migration")
    return errors


def validate_operational_content(path: str, content: bytes) -> tuple[bool, str]:
    if path == ".github/greasyfork-version.txt":
        value = content.decode("utf-8").strip()
        if not SEMVER.fullmatch(value):
            return False, f"fallback tracker is not a stable semantic version: {value!r}"
        return True, f"operational tracker v{value}"
    return False, f"no operational schema is defined for {path}"


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
            files.append(
                {
                    "path": path,
                    "mode": "operational" if path in operational else "mirror",
                    "equal": False,
                    "acceptable": False,
                    "reason": "branch-missing",
                }
            )
            continue

        local = local_path.read_bytes() if local_path.is_file() else None
        equal = local == remote if local is not None else False
        if path in mirrored:
            acceptable = local is not None and equal
            reason = "byte-identical" if acceptable else "mirror-mismatch"
            if local is None:
                errors.append(f"Current checkout is missing mirrored path {path}")
            elif not equal:
                errors.append(f"{branch}:{path} differs from current checkout")
            mode = "mirror"
        elif path in operational:
            acceptable, reason = validate_operational_content(path, remote)
            if not acceptable:
                errors.append(f"{branch}:{path} is invalid: {reason}")
            mode = "operational"
        else:
            acceptable = False
            reason = "unclassified"
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
            }
        )

    return {
        "branch": branch,
        "purpose": policy["purpose"],
        "commit": str(git("rev-parse", branch_ref(branch))).strip(),
        "role": role,
        "files": files,
        "acceptable": not errors and all(bool(file["acceptable"]) for file in files),
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
            marker = "✅" if file["acceptable"] else "❌"
            suffix = "mirror" if file["mode"] == "mirror" else "operational"
            equality = "equal" if file["equal"] else "independent"
            lines.append(
                f"- {marker} `{file['path']}` — {suffix}, {equality}: {file['reason']}"
            )
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
            ".github/greasyfork-version.txt",
        ],
        "mirroredPaths": ["status/release-dashboard.json"],
        "operationalPaths": [".github/greasyfork-version.txt"],
        "operationalWriter": ".github/workflows/greasyfork-release-monitor.yml",
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

    broken = dict(policy)
    broken["mirroredPaths"] = [*policy["mirroredPaths"], ".github/greasyfork-version.txt"]
    try:
        validate_path_classes("release-state", broken)
    except ValueError:
        pass
    else:
        raise AssertionError("overlapping path classes were accepted")
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
        "schemaVersion": 2,
        "state": "acceptable" if acceptable else "mismatch",
        "acceptable": acceptable,
        "sourceCommit": str(git("rev-parse", "HEAD")).strip(),
        "generatedAt": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
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
