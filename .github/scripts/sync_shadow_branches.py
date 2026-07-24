#!/usr/bin/env python3
"""Synchronize governed files to Issue #41 shadow branches.

The synchronizer is deliberately non-live. It accepts only the reviewed
`release-state` and `distribution` branches, preserves `main` as authority,
requires an exact source SHA and confirmation phrase, and never updates `main`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".github" / "shadow-branch-policy.json"
ROLE_PATH = ".github/branch-role.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


class SyncError(RuntimeError):
    """A fail-closed synchronization error."""


def git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise SyncError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def load_policy(path: Path = POLICY_PATH) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SyncError("Shadow branch policy must be a JSON object")
    return value


def validate_policy(policy: dict) -> dict:
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
        if policy.get(key) != expected_value:
            raise SyncError(f"Shadow policy {key}={policy.get(key)!r}, expected {expected_value!r}")

    writer = policy.get("writerRehearsal")
    if not isinstance(writer, dict):
        raise SyncError("writerRehearsal policy is missing")
    writer_expected = {
        "enabled": True,
        "manualDispatchOnly": True,
        "authorizedActor": "Conroy1988",
        "sourceBranch": "main",
        "planConfirmation": "PLAN SHADOW SYNC",
        "applyConfirmation": "SYNC SHADOWS",
        "credentialSecret": "DEVELOPMENT_PR_TOKEN",
        "workflowPermission": "contents: read",
        "allowIdempotentEmptyProbeCommit": True,
        "liveConsumerCutoverAllowed": False,
        "replacementIdentity": "narrowly scoped GitHub App",
    }
    for key, expected_value in writer_expected.items():
        if writer.get(key) != expected_value:
            raise SyncError(f"writerRehearsal {key}={writer.get(key)!r}, expected {expected_value!r}")

    allowed_targets = writer.get("allowedTargets")
    if allowed_targets != ["release-state", "distribution"]:
        raise SyncError("Shadow writer target allowlist changed")

    branches = policy.get("branches")
    if not isinstance(branches, dict) or set(branches) != set(allowed_targets):
        raise SyncError("Shadow branch definitions differ from the writer allowlist")
    for branch, branch_policy in branches.items():
        if branch == "main" or not isinstance(branch_policy, dict):
            raise SyncError("Invalid shadow branch policy")
        paths = branch_policy.get("governedPaths")
        if not isinstance(paths, list) or not paths or any(not isinstance(path, str) for path in paths):
            raise SyncError(f"{branch} governedPaths is invalid")
        if ROLE_PATH in paths:
            raise SyncError(f"{branch} role file must not be synchronized from main")
    return writer


def selected_targets(value: str, writer: dict) -> list[str]:
    allowed = list(writer["allowedTargets"])
    if value == "both":
        return allowed
    if value not in allowed or value == "main":
        raise SyncError(f"Target {value!r} is not an approved shadow branch")
    return [value]


def validate_request(
    *,
    policy: dict,
    mode: str,
    target: str,
    source_sha: str,
    confirmation: str,
    actor: str,
    write_probe: bool,
) -> tuple[dict, list[str]]:
    writer = validate_policy(policy)
    if mode not in {"plan", "apply"}:
        raise SyncError("Mode must be plan or apply")
    if not FULL_SHA.fullmatch(source_sha):
        raise SyncError("source_sha must be a full lowercase 40-character SHA")
    if actor != writer["authorizedActor"]:
        raise SyncError("Only the reviewed repository owner may run shadow synchronization")
    required_confirmation = writer[f"{mode}Confirmation"]
    if confirmation != required_confirmation:
        raise SyncError(f"Confirmation must be exactly {required_confirmation!r}")
    if mode != "apply" and write_probe:
        raise SyncError("A write probe is valid only in apply mode")
    targets = selected_targets(target, writer)
    return writer, targets


def read_branch_json(branch: str, path: str) -> dict:
    raw = git("show", f"refs/remotes/origin/{branch}:{path}")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise SyncError(f"Expected JSON object at {branch}:{path}")
    return value


def validate_role(branch: str, role: dict, policy: dict) -> None:
    expected = {
        "schemaVersion": 1,
        "branch": branch,
        "mode": "shadow-rehearsal",
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
    }
    for key, expected_value in expected.items():
        if role.get(key) != expected_value:
            raise SyncError(f"{branch} role {key}={role.get(key)!r}, expected {expected_value!r}")
    allowed = role.get("allowedMutablePaths")
    expected_allowed = [*policy["governedPaths"], ROLE_PATH]
    if allowed != expected_allowed:
        raise SyncError(f"{branch} role allowedMutablePaths differs from the reviewed allowlist")
    if "main remains authoritative" not in str(role.get("authority") or ""):
        raise SyncError(f"{branch} role no longer preserves main authority")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_paths(worktree: Path) -> list[str]:
    changed = set(
        line.strip()
        for line in git("-C", str(worktree), "diff", "--name-only").splitlines()
        if line.strip()
    )
    changed.update(
        line.strip()
        for line in git("-C", str(worktree), "ls-files", "--others", "--exclude-standard").splitlines()
        if line.strip()
    )
    return sorted(changed)


def authenticated_url(repository: str, token: str) -> str:
    if not token:
        raise SyncError("DEVELOPMENT_PR_TOKEN is required for apply mode")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise SyncError("GITHUB_REPOSITORY is invalid")
    return f"https://x-access-token:{quote(token, safe='')}@github.com/{repository}.git"


def push_branch(*, worktree: Path, branch: str, repository: str, token: str) -> None:
    url = authenticated_url(repository, token)
    result = subprocess.run(
        ["git", "-C", str(worktree), "push", url, f"HEAD:refs/heads/{branch}"],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SyncError(f"Owner-authenticated push to {branch} failed")


def sync_branch(
    *,
    branch: str,
    branch_policy: dict,
    source_sha: str,
    mode: str,
    write_probe: bool,
    repository: str,
    token: str,
) -> dict:
    if branch == "main" or branch not in {"release-state", "distribution"}:
        raise SyncError("Refusing non-shadow target")

    remote_ref = f"refs/remotes/origin/{branch}"
    before_sha = git("rev-parse", remote_ref).strip()
    role = read_branch_json(branch, ROLE_PATH)
    validate_role(branch, role, branch_policy)
    paths = list(branch_policy["governedPaths"])
    fingerprint = hashlib.sha256(
        (source_sha + "\0" + branch + "\0" + "\0".join(paths)).encode("utf-8")
    ).hexdigest()[:16]
    marker = f"[shadow-sync:{fingerprint}]"

    files: list[dict[str, object]] = []
    for path in paths:
        source = ROOT / path
        if not source.is_file() or source.is_symlink():
            raise SyncError(f"Source governed path is missing or unsafe: {path}")
        try:
            branch_bytes = subprocess.run(
                ["git", "show", f"{remote_ref}:{path}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
        except subprocess.CalledProcessError as exc:
            raise SyncError(f"{branch} is missing governed path {path}") from exc
        files.append(
            {
                "path": path,
                "equalBefore": source.read_bytes() == branch_bytes,
                "sourceSha256": file_hash(source),
            }
        )

    with tempfile.TemporaryDirectory(prefix=f"shadow-sync-{branch}-") as temporary:
        worktree = Path(temporary) / "worktree"
        git("worktree", "add", "--detach", str(worktree), remote_ref)
        try:
            for path in paths:
                source = ROOT / path
                destination = worktree / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)

            changed = changed_paths(worktree)
            unexpected = sorted(set(changed) - set(paths))
            if unexpected:
                raise SyncError(f"{branch} synchronization changed non-governed paths: {unexpected}")
            if ROLE_PATH in changed:
                raise SyncError(f"{branch} role declaration must remain immutable during sync")

            latest_message = git("-C", str(worktree), "log", "-1", "--format=%B")
            probe_already_recorded = marker in latest_message
            should_commit = bool(changed) or (mode == "apply" and write_probe and not probe_already_recorded)
            pushed = False
            empty_probe = False
            after_sha = before_sha

            if mode == "apply" and should_commit:
                git("-C", str(worktree), "config", "user.name", "Conroy1988 shadow rehearsal")
                git(
                    "-C",
                    str(worktree),
                    "config",
                    "user.email",
                    "27301455+Conroy1988@users.noreply.github.com",
                )
                if changed:
                    git("-C", str(worktree), "add", "--", *paths)
                    git(
                        "-C",
                        str(worktree),
                        "commit",
                        "-m",
                        f"Rehearse {branch} shadow sync from {source_sha[:12]} {marker}",
                    )
                else:
                    empty_probe = True
                    git(
                        "-C",
                        str(worktree),
                        "commit",
                        "--allow-empty",
                        "-m",
                        f"Rehearse {branch} shadow writer access from {source_sha[:12]} {marker}",
                    )
                after_sha = git("-C", str(worktree), "rev-parse", "HEAD").strip()
                push_branch(
                    worktree=worktree,
                    branch=branch,
                    repository=repository,
                    token=token,
                )
                pushed = True

            return {
                "branch": branch,
                "beforeCommit": before_sha,
                "afterCommit": after_sha,
                "changedPaths": changed,
                "contentChanged": bool(changed),
                "emptyProbeCommit": empty_probe,
                "probeAlreadyRecorded": probe_already_recorded,
                "pushed": pushed,
                "files": files,
                "acceptable": True,
            }
        finally:
            git("worktree", "remove", "--force", str(worktree), check=False)


def render_markdown(report: dict) -> str:
    lines = [
        "# Issue #41 shadow synchronization rehearsal",
        "",
        f"- State: **{report['state']}**",
        f"- Mode: `{report['mode']}`",
        f"- Source commit: `{report['sourceCommit']}`",
        f"- Target selection: `{report['targetSelection']}`",
        f"- Generated: `{report['generatedAt']}`",
        "- Public `main` changed: **no**",
        "- Live consumers changed: **no**",
        "- Workflow token has contents write: **no**",
        "",
    ]
    for branch in report["branches"]:
        lines.extend(
            [
                f"## `{branch['branch']}`",
                "",
                f"- Before: `{branch['beforeCommit']}`",
                f"- After: `{branch['afterCommit']}`",
                f"- Pushed: **{'yes' if branch['pushed'] else 'no'}**",
                f"- Content changed: **{'yes' if branch['contentChanged'] else 'no'}**",
                f"- Empty write probe: **{'yes' if branch['emptyProbeCommit'] else 'no'}**",
                "",
            ]
        )
        for path in branch["changedPaths"]:
            lines.append(f"- Updated governed path: `{path}`")
        if not branch["changedPaths"]:
            lines.append("- Governed content already matched `main`.")
        lines.append("")
    return "\n".join(lines)


def self_test() -> None:
    policy = {
        "schemaVersion": 1,
        "mode": "shadow-rehearsal",
        "mainAuthorityPreserved": True,
        "liveConsumersEnabled": False,
        "strictProtectionEnabled": False,
        "administratorRecoveryRequired": True,
        "cutoverIssue": 41,
        "writerRehearsal": {
            "enabled": True,
            "manualDispatchOnly": True,
            "authorizedActor": "Conroy1988",
            "sourceBranch": "main",
            "allowedTargets": ["release-state", "distribution"],
            "planConfirmation": "PLAN SHADOW SYNC",
            "applyConfirmation": "SYNC SHADOWS",
            "credentialSecret": "DEVELOPMENT_PR_TOKEN",
            "workflowPermission": "contents: read",
            "allowIdempotentEmptyProbeCommit": True,
            "liveConsumerCutoverAllowed": False,
            "replacementIdentity": "narrowly scoped GitHub App",
        },
        "branches": {
            "release-state": {"governedPaths": ["status/release-dashboard.json"]},
            "distribution": {"governedPaths": ["dist/release-manifest.json"]},
        },
    }
    writer, targets = validate_request(
        policy=policy,
        mode="plan",
        target="both",
        source_sha="a" * 40,
        confirmation="PLAN SHADOW SYNC",
        actor="Conroy1988",
        write_probe=False,
    )
    assert writer["sourceBranch"] == "main"
    assert targets == ["release-state", "distribution"]
    try:
        selected_targets("main", writer)
    except SyncError:
        pass
    else:
        raise AssertionError("main target was not rejected")
    try:
        validate_request(
            policy=policy,
            mode="apply",
            target="release-state",
            source_sha="a" * 40,
            confirmation="PLAN SHADOW SYNC",
            actor="Conroy1988",
            write_probe=True,
        )
    except SyncError:
        pass
    else:
        raise AssertionError("incorrect apply confirmation was not rejected")
    print("Shadow synchronization self-tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("plan", "apply"))
    parser.add_argument("--target", choices=("both", "release-state", "distribution"))
    parser.add_argument("--source-sha")
    parser.add_argument("--confirmation")
    parser.add_argument("--actor")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--write-probe", action="store_true")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    required = [args.mode, args.target, args.source_sha, args.confirmation, args.actor]
    if any(value is None for value in required):
        raise SyncError("mode, target, source-sha, confirmation and actor are required")

    policy = load_policy()
    _writer, targets = validate_request(
        policy=policy,
        mode=args.mode,
        target=args.target,
        source_sha=args.source_sha,
        confirmation=args.confirmation,
        actor=args.actor,
        write_probe=args.write_probe,
    )

    head = git("rev-parse", "HEAD").strip()
    main_head = git("rev-parse", "refs/remotes/origin/main").strip()
    if head != args.source_sha or main_head != args.source_sha:
        raise SyncError("The checked-out source and origin/main must match the authorized source SHA")

    token = os.environ.get("SHADOW_SYNC_TOKEN", "")
    if args.mode == "apply" and not token:
        raise SyncError("DEVELOPMENT_PR_TOKEN is required for apply mode")

    results = [
        sync_branch(
            branch=branch,
            branch_policy=policy["branches"][branch],
            source_sha=args.source_sha,
            mode=args.mode,
            write_probe=args.write_probe,
            repository=args.repository,
            token=token,
        )
        for branch in targets
    ]
    report = {
        "schemaVersion": 1,
        "state": "synchronized" if args.mode == "apply" else "planned",
        "acceptable": True,
        "mode": args.mode,
        "targetSelection": args.target,
        "sourceBranch": "main",
        "sourceCommit": args.source_sha,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "authorizedActor": args.actor,
        "credentialMode": "owner-token-rehearsal" if args.mode == "apply" else "read-only-plan",
        "replacementIdentity": "narrowly scoped GitHub App",
        "publicMainChanged": False,
        "liveConsumersChanged": False,
        "workflowContentsWrite": False,
        "branches": results,
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(render_markdown(report) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncError as error:
        print(f"shadow synchronization refused: {error}", file=os.sys.stderr)
        raise SystemExit(1)
