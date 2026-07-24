#!/usr/bin/env python3
"""Synchronize only reviewed mirror files to Issue #41 operational branches.

The synchronizer is deliberately non-live. It accepts only the reviewed
``release-state`` and ``distribution`` branches, preserves every operational
path, requires an exact source SHA and confirmation phrase, and never updates
public ``main``.
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
RELEASE_STATE_PATHS = [
    "status/release-dashboard.json",
    "status/README.md",
    "status/update-manifest.json",
    ".github/greasyfork-version.txt",
]
RELEASE_STATE_WRITERS = [
    ".github/workflows/greasyfork-release-monitor.yml",
    ".github/workflows/release-recovery.yml",
]


class SyncError(RuntimeError):
    """Fail-closed synchronization error."""


def git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=False
    )
    if check and result.returncode != 0:
        raise SyncError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def load_policy(path: Path = POLICY_PATH) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError("Operational branch policy is missing or invalid") from error
    if not isinstance(value, dict):
        raise SyncError("Operational branch policy must be a JSON object")
    return value


def validate_path_classes(branch: str, policy: dict) -> tuple[list[str], list[str]]:
    governed = policy.get("governedPaths")
    mirrored = policy.get("mirroredPaths")
    operational = policy.get("operationalPaths")
    writers = policy.get("operationalWriters")
    if not all(isinstance(value, list) for value in [governed, mirrored, operational, writers]):
        raise SyncError(f"{branch} path classes and writers must be lists")
    if not governed or any(not isinstance(path, str) or not path for path in governed):
        raise SyncError(f"{branch} governedPaths is invalid")
    if len(governed) != len(set(governed)):
        raise SyncError(f"{branch} governedPaths contains duplicates")
    if set(mirrored) & set(operational):
        raise SyncError(f"{branch} mirroredPaths and operationalPaths overlap")
    if set(governed) != set(mirrored) | set(operational):
        raise SyncError(f"{branch} path classes do not partition governedPaths")
    if ROLE_PATH in governed:
        raise SyncError(f"{branch} role file must never be copied from main")
    if policy.get("externalConsumersEnabled") is not False:
        raise SyncError(f"{branch} external consumers must remain disabled")

    if branch == "release-state":
        if mirrored != [] or operational != RELEASE_STATE_PATHS:
            raise SyncError("release-state recovery ledger must remain operational and mirror-free")
        if writers != RELEASE_STATE_WRITERS:
            raise SyncError("release-state operational writers changed")
    elif branch == "distribution":
        if operational or writers:
            raise SyncError("distribution cannot have operational paths before cutover")
        if mirrored != governed:
            raise SyncError("distribution governed paths must remain mirrored")
    else:
        raise SyncError(f"Unsupported operational branch: {branch}")
    return list(mirrored), list(operational)


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
    expected_writer = {
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
    }
    if writer != expected_writer:
        raise SyncError("writerRehearsal policy changed")
    branches = policy.get("branches")
    if not isinstance(branches, dict) or set(branches) != set(writer["allowedTargets"]):
        raise SyncError("Operational branch definitions differ from the target allowlist")
    for branch, branch_policy in branches.items():
        if not isinstance(branch_policy, dict):
            raise SyncError(f"Invalid branch policy for {branch}")
        validate_path_classes(branch, branch_policy)
    return writer


def selected_targets(value: str, writer: dict) -> list[str]:
    allowed = list(writer["allowedTargets"])
    if value == "both":
        return allowed
    if value == "main" or value not in allowed:
        raise SyncError(f"Target {value!r} is not an approved operational branch")
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
    return writer, selected_targets(target, writer)


def read_branch_json(branch: str, path: str) -> dict:
    try:
        value = json.loads(git("show", f"refs/remotes/origin/{branch}:{path}"))
    except (json.JSONDecodeError, SyncError) as error:
        raise SyncError(f"Invalid JSON object at {branch}:{path}") from error
    if not isinstance(value, dict):
        raise SyncError(f"Expected JSON object at {branch}:{path}")
    return value


def read_branch_bytes(branch: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"refs/remotes/origin/{branch}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SyncError(f"{branch} is missing governed path {path}")
    return result.stdout


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
    if role.get("allowedMutablePaths") != [*policy["governedPaths"], ROLE_PATH]:
        raise SyncError(f"{branch} role allowedMutablePaths differs from reviewed policy")
    if "main remains authoritative" not in str(role.get("authority") or ""):
        raise SyncError(f"{branch} role no longer preserves main source authority")


def changed_paths(worktree: Path) -> list[str]:
    changed = {
        line.strip()
        for line in git("diff", "--name-only", cwd=worktree).splitlines()
        if line.strip()
    }
    changed.update(
        line.strip()
        for line in git("ls-files", "--others", "--exclude-standard", cwd=worktree).splitlines()
        if line.strip()
    )
    return sorted(changed)


def authenticated_url(repository: str, token: str) -> str:
    if not token:
        raise SyncError("DEVELOPMENT_PR_TOKEN is required for apply mode")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise SyncError("GITHUB_REPOSITORY is invalid")
    return f"https://x-access-token:{quote(token, safe='')}@github.com/{repository}.git"


def push_branch(worktree: Path, branch: str, repository: str, token: str) -> None:
    result = subprocess.run(
        ["git", "push", authenticated_url(repository, token), f"HEAD:refs/heads/{branch}"],
        cwd=worktree,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SyncError(f"Owner-authenticated non-force push to {branch} failed")


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
        raise SyncError("Refusing non-operational target")
    mirrored_paths, operational_paths = validate_path_classes(branch, branch_policy)
    remote_ref = f"refs/remotes/origin/{branch}"
    before_sha = git("rev-parse", remote_ref).strip()
    validate_role(branch, read_branch_json(branch, ROLE_PATH), branch_policy)

    fingerprint = hashlib.sha256(
        (
            source_sha
            + "\0"
            + branch
            + "\0mirrored\0"
            + "\0".join(mirrored_paths)
            + "\0operational\0"
            + "\0".join(operational_paths)
        ).encode("utf-8")
    ).hexdigest()[:16]
    marker = f"[shadow-sync:{fingerprint}]"

    files: list[dict[str, object]] = []
    for path in mirrored_paths:
        source = ROOT / path
        if not source.is_file() or source.is_symlink():
            raise SyncError(f"Source mirrored path is missing or unsafe: {path}")
        branch_bytes = read_branch_bytes(branch, path)
        files.append({"path": path, "mode": "mirror", "equalBefore": source.read_bytes() == branch_bytes})
    for path in operational_paths:
        read_branch_bytes(branch, path)
        files.append({"path": path, "mode": "operational-preserved", "equalBefore": None})

    with tempfile.TemporaryDirectory(prefix=f"shadow-sync-{branch}-") as temporary:
        worktree = Path(temporary) / "worktree"
        git("worktree", "add", "--detach", str(worktree), remote_ref)
        try:
            role_before = (worktree / ROLE_PATH).read_bytes()
            operational_before = {path: (worktree / path).read_bytes() for path in operational_paths}
            for path in mirrored_paths:
                destination = worktree / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, destination)

            changed = changed_paths(worktree)
            if set(changed) - set(mirrored_paths):
                raise SyncError(f"{branch} synchronization changed non-mirrored paths")
            if (worktree / ROLE_PATH).read_bytes() != role_before:
                raise SyncError(f"{branch} role declaration changed during sync")
            for path, before in operational_before.items():
                if (worktree / path).read_bytes() != before:
                    raise SyncError(f"{branch} operational path was modified during mirror sync: {path}")

            latest_message = git("log", "-1", "--format=%B", cwd=worktree)
            probe_already_recorded = marker in latest_message
            should_commit = bool(changed) or (mode == "apply" and write_probe and not probe_already_recorded)
            pushed = False
            empty_probe = False
            after_sha = before_sha

            if mode == "apply" and should_commit:
                git("config", "user.name", "Conroy1988 shadow rehearsal", cwd=worktree)
                git("config", "user.email", "27301455+Conroy1988@users.noreply.github.com", cwd=worktree)
                if changed:
                    git("add", "--", *mirrored_paths, cwd=worktree)
                    staged = set(git("diff", "--cached", "--name-only", cwd=worktree).splitlines())
                    if not staged or not staged <= set(mirrored_paths):
                        raise SyncError(f"Invalid staged mirror paths: {sorted(staged)}")
                    git("commit", "-m", f"Rehearse {branch} mirror sync from {source_sha[:12]} {marker}", cwd=worktree)
                else:
                    empty_probe = True
                    git("commit", "--allow-empty", "-m", f"Rehearse {branch} shadow writer access from {source_sha[:12]} {marker}", cwd=worktree)
                after_sha = git("rev-parse", "HEAD", cwd=worktree).strip()
                push_branch(worktree, branch, repository, token)
                pushed = True

            return {
                "branch": branch,
                "beforeCommit": before_sha,
                "afterCommit": after_sha,
                "mirroredPaths": mirrored_paths,
                "preservedOperationalPaths": operational_paths,
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
        "- Public `main` changed: **no**",
        "- External consumers changed: **no**",
        "",
    ]
    for branch in report["branches"]:
        lines.extend([
            f"## `{branch['branch']}`",
            "",
            f"- Before: `{branch['beforeCommit']}`",
            f"- After: `{branch['afterCommit']}`",
            f"- Pushed: **{'yes' if branch['pushed'] else 'no'}**",
            f"- Mirror content changed: **{'yes' if branch['contentChanged'] else 'no'}**",
            "",
        ])
        for path in branch["changedPaths"]:
            lines.append(f"- Updated mirrored path: `{path}`")
        for path in branch["preservedOperationalPaths"]:
            lines.append(f"- Preserved operational path: `{path}`")
        if not branch["changedPaths"]:
            lines.append("- No mirrored content required synchronization.")
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
            "release-state": {
                "governedPaths": RELEASE_STATE_PATHS,
                "mirroredPaths": [],
                "operationalPaths": RELEASE_STATE_PATHS,
                "operationalWriters": RELEASE_STATE_WRITERS,
                "externalConsumersEnabled": False,
            },
            "distribution": {
                "governedPaths": ["dist/release-manifest.json"],
                "mirroredPaths": ["dist/release-manifest.json"],
                "operationalPaths": [],
                "operationalWriters": [],
                "externalConsumersEnabled": False,
            },
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
    mirrored, operational = validate_path_classes("release-state", policy["branches"]["release-state"])
    assert mirrored == []
    assert operational == RELEASE_STATE_PATHS
    try:
        selected_targets("main", writer)
    except SyncError:
        pass
    else:
        raise AssertionError("main target was not rejected")
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
    if any(value is None for value in [args.mode, args.target, args.source_sha, args.confirmation, args.actor]):
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
    if git("rev-parse", "HEAD").strip() != args.source_sha or git("rev-parse", "refs/remotes/origin/main").strip() != args.source_sha:
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
        "schemaVersion": 3,
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
        "externalConsumersChanged": False,
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
