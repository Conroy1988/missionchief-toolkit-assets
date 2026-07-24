#!/usr/bin/env python3
"""Prepare and commit governed operational state on the release-state branch.

This helper is intentionally branch-specific. It never targets public ``main``,
never force-pushes, validates the branch-role declaration before every write,
and rejects changes outside the reviewed release-state allowlist.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET_BRANCH = "release-state"
REMOTE_REF = f"refs/remotes/origin/{TARGET_BRANCH}"
PUSH_REF = f"HEAD:refs/heads/{TARGET_BRANCH}"
ROLE_PATH = Path(".github/branch-role.json")


class ReleaseStateError(RuntimeError):
    """Fail-closed release-state operation error."""


def git(*args: str, cwd: Path = ROOT, capture: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=capture,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git command failed").strip()
        raise ReleaseStateError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip() if capture else ""


def load_role(worktree: Path) -> dict:
    path = worktree / ROLE_PATH
    if not path.is_file() or path.is_symlink():
        raise ReleaseStateError("release-state branch role is missing or unsafe")
    try:
        role = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReleaseStateError("release-state branch role is not valid JSON") from error
    if not isinstance(role, dict):
        raise ReleaseStateError("release-state branch role must be a JSON object")
    return role


def validate_role(role: dict) -> set[str]:
    expected = {
        "schemaVersion": 1,
        "branch": TARGET_BRANCH,
        "mode": "shadow-rehearsal",
        "authority": "main remains authoritative until Issue #41 cutover",
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
    }
    for key, value in expected.items():
        if role.get(key) != value:
            raise ReleaseStateError(
                f"release-state role {key}={role.get(key)!r}, expected {value!r}"
            )
    allowed = role.get("allowedMutablePaths")
    if not isinstance(allowed, list) or not all(isinstance(path, str) and path for path in allowed):
        raise ReleaseStateError("release-state allowedMutablePaths is invalid")
    allowed_paths = set(allowed)
    required = {
        "status/release-dashboard.json",
        "status/README.md",
        "status/update-manifest.json",
        ".github/greasyfork-version.txt",
        ROLE_PATH.as_posix(),
    }
    if allowed_paths != required:
        raise ReleaseStateError(
            f"release-state mutable-path allowlist changed: {sorted(allowed_paths)}"
        )
    return allowed_paths - {ROLE_PATH.as_posix()}


def validate_worktree(worktree: Path) -> set[str]:
    if not worktree.is_dir():
        raise ReleaseStateError(f"release-state worktree is missing: {worktree}")
    role = load_role(worktree)
    return validate_role(role)


def write_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with Path(output).open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def prepare(worktree: Path) -> None:
    if TARGET_BRANCH == "main" or PUSH_REF.endswith("/main"):
        raise ReleaseStateError("public main can never be a release-state target")
    if worktree.exists():
        if any(worktree.iterdir()):
            raise ReleaseStateError(f"refusing to reuse non-empty worktree path: {worktree}")
        worktree.rmdir()
    worktree.parent.mkdir(parents=True, exist_ok=True)

    git(
        "fetch",
        "--force",
        "--no-tags",
        "origin",
        f"+refs/heads/{TARGET_BRANCH}:{REMOTE_REF}",
    )
    before = git("rev-parse", REMOTE_REF)
    git("worktree", "add", "--detach", str(worktree), REMOTE_REF, capture=False)
    validate_worktree(worktree)
    head = git("rev-parse", "HEAD", cwd=worktree)
    if head != before:
        raise ReleaseStateError("prepared worktree does not match current release-state ref")

    write_output("root", str(worktree))
    write_output("before_sha", before)
    print(f"Prepared governed {TARGET_BRANCH} worktree at {worktree} ({before})")


def status_paths(worktree: Path) -> set[str]:
    raw = git("status", "--porcelain=v1", "-z", cwd=worktree)
    if not raw:
        return set()
    entries = raw.split("\0")
    paths: set[str] = set()
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        if len(entry) < 4:
            raise ReleaseStateError(f"unrecognised git status entry: {entry!r}")
        status = entry[:2]
        path = entry[3:]
        if "R" in status or "C" in status:
            if index >= len(entries) or not entries[index]:
                raise ReleaseStateError("rename/copy status entry is incomplete")
            paths.add(entries[index])
            index += 1
        paths.add(path)
    return paths


def authorization_header(token: str) -> str:
    encoded = base64.b64encode(f"x-access-token:{token}".encode("utf-8")).decode("ascii")
    return f"AUTHORIZATION: basic {encoded}"


def commit(worktree: Path, message: str, requested_paths: list[str]) -> None:
    if not message.strip():
        raise ReleaseStateError("release-state commit message is required")
    if not requested_paths:
        raise ReleaseStateError("at least one governed release-state path is required")
    if TARGET_BRANCH == "main" or "refs/heads/main" in PUSH_REF:
        raise ReleaseStateError("public main can never be a release-state target")

    allowed = validate_worktree(worktree)
    requested = {Path(path).as_posix() for path in requested_paths}
    if ROLE_PATH.as_posix() in requested:
        raise ReleaseStateError("release-state branch role is immutable")
    if not requested <= allowed:
        raise ReleaseStateError(
            f"unapproved release-state paths requested: {sorted(requested - allowed)}"
        )

    changed = status_paths(worktree)
    if not changed:
        print("Release-state content is already current; no commit required.")
        write_output("changed", "false")
        write_output("commit_sha", git("rev-parse", "HEAD", cwd=worktree))
        return
    if not changed <= requested:
        raise ReleaseStateError(
            f"release-state worktree contains unexpected changes: {sorted(changed - requested)}"
        )

    role_before = (worktree / ROLE_PATH).read_bytes()
    git("add", "--", *sorted(requested), cwd=worktree, capture=False)
    staged = {
        path
        for path in git("diff", "--cached", "--name-only", cwd=worktree).splitlines()
        if path
    }
    if not staged or not staged <= requested:
        raise ReleaseStateError(f"invalid staged release-state paths: {sorted(staged)}")
    if (worktree / ROLE_PATH).read_bytes() != role_before:
        raise ReleaseStateError("release-state branch role changed during the operation")

    git(
        "fetch",
        "--force",
        "--no-tags",
        "origin",
        f"+refs/heads/{TARGET_BRANCH}:{REMOTE_REF}",
        cwd=worktree,
    )
    head = git("rev-parse", "HEAD", cwd=worktree)
    remote = git("rev-parse", REMOTE_REF, cwd=worktree)
    if head != remote:
        raise ReleaseStateError(
            "release-state moved after preparation; rerun against the current branch head"
        )

    git("config", "user.name", "github-actions[bot]", cwd=worktree, capture=False)
    git(
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
        cwd=worktree,
        capture=False,
    )
    git("commit", "-m", message, cwd=worktree, capture=False)
    commit_sha = git("rev-parse", "HEAD", cwd=worktree)

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    if not token:
        raise ReleaseStateError("GH_TOKEN is required to publish release-state changes")
    header = authorization_header(token)
    git(
        "-c",
        f"http.https://github.com/.extraheader={header}",
        "push",
        "origin",
        PUSH_REF,
        cwd=worktree,
        capture=False,
    )

    write_output("changed", "true")
    write_output("commit_sha", commit_sha)
    print(f"Published governed release-state commit {commit_sha}")


def self_test() -> None:
    role = {
        "schemaVersion": 1,
        "branch": "release-state",
        "mode": "shadow-rehearsal",
        "authority": "main remains authoritative until Issue #41 cutover",
        "purpose": "test",
        "allowedMutablePaths": [
            "status/release-dashboard.json",
            "status/README.md",
            "status/update-manifest.json",
            ".github/greasyfork-version.txt",
            ".github/branch-role.json",
        ],
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
    }
    allowed = validate_role(role)
    assert ".github/greasyfork-version.txt" in allowed
    assert ".github/branch-role.json" not in allowed

    broken = dict(role)
    broken["branch"] = "main"
    try:
        validate_role(broken)
    except ReleaseStateError:
        pass
    else:
        raise AssertionError("main branch role was accepted")

    broken = json.loads(json.dumps(role))
    broken["allowedMutablePaths"].append("README.md")
    try:
        validate_role(broken)
    except ReleaseStateError:
        pass
    else:
        raise AssertionError("expanded mutable-path allowlist was accepted")

    assert PUSH_REF == "HEAD:refs/heads/release-state"
    assert "main" not in PUSH_REF
    print("Release-state branch writer self-tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=False)

    prepare_parser = subcommands.add_parser("prepare")
    prepare_parser.add_argument("--worktree", type=Path, required=True)

    commit_parser = subcommands.add_parser("commit")
    commit_parser.add_argument("--worktree", type=Path, required=True)
    commit_parser.add_argument("--message", required=True)
    commit_parser.add_argument("--path", action="append", dest="paths", required=True)

    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.command == "prepare":
        prepare(args.worktree.resolve())
        return 0
    if args.command == "commit":
        commit(args.worktree.resolve(), args.message, args.paths)
        return 0
    raise ReleaseStateError("prepare, commit or --self-test is required")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReleaseStateError as error:
        print(f"release-state operation refused: {error}", file=os.sys.stderr)
        raise SystemExit(1)
