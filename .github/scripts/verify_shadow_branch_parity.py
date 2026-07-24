#!/usr/bin/env python3
"""Verify Issue #41 shadow branch roles and governed-file parity.

This verifier is read-only. It compares current checkout files with the selected
operational files on the `release-state` and `distribution` rehearsal branches.
It never creates, updates or force-pushes a ref.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROLE_PATH = ".github/branch-role.json"
BRANCH_POLICIES = {
    "release-state": {
        "purpose": "release-state shadow branch",
        "allowedMutablePaths": [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
            ROLE_PATH,
        ],
        "governedPaths": [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
        ],
    },
    "distribution": {
        "purpose": "distribution shadow branch",
        "allowedMutablePaths": [
            "dist/MissionChief_Map_Command_Toolkit.user.js",
            "dist/MissionChief_Map_Command_Toolkit.txt",
            "dist/SHA256SUMS.txt",
            "dist/release-manifest.json",
            "MissionChief_Map_Command_Toolkit.user.js",
            "MissionChief_Map_Command_Toolkit.txt",
            ROLE_PATH,
        ],
        "governedPaths": [
            "dist/MissionChief_Map_Command_Toolkit.user.js",
            "dist/MissionChief_Map_Command_Toolkit.txt",
            "dist/SHA256SUMS.txt",
            "dist/release-manifest.json",
            "MissionChief_Map_Command_Toolkit.user.js",
            "MissionChief_Map_Command_Toolkit.txt",
        ],
    },
}


def git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=not binary,
    )
    return result.stdout if not binary else result.stdout


def branch_ref(branch: str) -> str:
    return f"refs/remotes/origin/{branch}"


def branch_file(branch: str, path: str) -> bytes:
    return git("show", f"{branch_ref(branch)}:{path}", binary=True)  # type: ignore[return-value]


def branch_json(branch: str, path: str) -> dict:
    value = json.loads(branch_file(branch, path).decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at {branch}:{path}")
    return value


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

    allowed = role.get("allowedMutablePaths")
    if allowed != policy["allowedMutablePaths"]:
        errors.append(f"{branch} allowedMutablePaths differs from reviewed policy")
    authority = str(role.get("authority") or "")
    if "main remains authoritative" not in authority:
        errors.append(f"{branch} role does not preserve main authority during rehearsal")
    return errors


def compare_branch(branch: str, policy: dict) -> dict:
    role = branch_json(branch, ROLE_PATH)
    errors = validate_role(branch, role, policy)
    files: list[dict[str, object]] = []
    for path in policy["governedPaths"]:
        local_path = ROOT / path
        if not local_path.is_file():
            errors.append(f"Current checkout is missing governed path {path}")
            files.append({"path": path, "equal": False, "reason": "local-missing"})
            continue
        local = local_path.read_bytes()
        try:
            remote = branch_file(branch, path)
        except subprocess.CalledProcessError:
            errors.append(f"{branch} is missing governed path {path}")
            files.append({"path": path, "equal": False, "reason": "branch-missing"})
            continue
        equal = local == remote
        files.append({"path": path, "equal": equal, "bytes": len(local)})
        if not equal:
            errors.append(f"{branch}:{path} differs from current checkout")

    return {
        "branch": branch,
        "purpose": policy["purpose"],
        "commit": str(git("rev-parse", branch_ref(branch))).strip(),
        "role": role,
        "files": files,
        "acceptable": not errors,
        "errors": errors,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Issue #41 shadow branch parity",
        "",
        f"- State: **{'synchronized' if report['acceptable'] else 'mismatch'}**",
        f"- Source commit: `{report['sourceCommit']}`",
        f"- Generated: `{report['generatedAt']}`",
        "- Live consumers changed: **no**",
        "- Public `main` changed: **no**",
        "",
    ]
    for branch in report["branches"]:
        lines.extend([
            f"## `{branch['branch']}`",
            "",
            f"- Commit: `{branch['commit']}`",
            f"- Role valid: **{'yes' if not branch['errors'] else 'no'}**",
            f"- Governed paths synchronized: **{'yes' if branch['acceptable'] else 'no'}**",
            "",
        ])
        for file in branch["files"]:
            marker = "✅" if file["equal"] else "❌"
            lines.append(f"- {marker} `{file['path']}`")
        if branch["errors"]:
            lines.extend(["", "### Errors", ""])
            lines.extend(f"- {error}" for error in branch["errors"])
        lines.append("")
    return "\n".join(lines)


def self_test() -> None:
    role = {
        "schemaVersion": 1,
        "branch": "release-state",
        "mode": "shadow-rehearsal",
        "authority": "main remains authoritative until cutover",
        "allowedMutablePaths": BRANCH_POLICIES["release-state"]["allowedMutablePaths"],
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
    }
    assert not validate_role("release-state", role, BRANCH_POLICIES["release-state"])
    broken = dict(role)
    broken["liveConsumersEnabled"] = True
    assert validate_role("release-state", broken, BRANCH_POLICIES["release-state"])
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

    branches = [compare_branch(branch, policy) for branch, policy in BRANCH_POLICIES.items()]
    report = {
        "schemaVersion": 1,
        "state": "synchronized" if all(branch["acceptable"] for branch in branches) else "mismatch",
        "acceptable": all(branch["acceptable"] for branch in branches),
        "sourceCommit": str(git("rev-parse", "HEAD")).strip(),
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "publicMainChanged": False,
        "liveConsumersChanged": False,
        "branches": branches,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["acceptable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
