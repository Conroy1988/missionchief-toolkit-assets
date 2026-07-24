#!/usr/bin/env python3
"""Synchronize only reviewed mirror files to Issue #41 operational branches.

The synchronizer is deliberately non-live. It accepts only the reviewed
``release-state`` and ``distribution`` branches, preserves operational branch
state, requires an exact source SHA and confirmation phrase, and never updates
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


class SyncError(RuntimeError):
    """Fail-closed synchronization error."""


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
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError("Shadow branch policy is missing or invalid") from error
    if not isinstance(value, dict):
        raise SyncError("Shadow branch policy must be a JSON object")
    return value


def validate_path_classes(branch: str, branch_policy: dict) -> tuple[list[str], list[str]]:
    governed = branch_policy.get("governedPaths")
    mirrored = branch_policy.get("mirroredPaths")
    operational = branch_policy.get("operationalPaths")
    if not all(isinstance(value, list) for value in [governed, mirrored, operational]):
        raise SyncError(f"{branch} governed, mirrored and operational paths must be lists")
    if not governed or any(not isinstance(path, str) or not path for path in governed):
        raise SyncError(f"{branch} governedPaths is invalid")
    if any(not isinstance(path, str) or not path for path in [*mirrored, *operational]):
        raise SyncError(f"{branch} path classes contain invalid entries")
    if len(governed) != len(set(governed)):
        raise SyncError(f"{branch} governedPaths contains duplicates")
    if set(mirrored) & set(operational):
        raise SyncError(f"{branch} mirroredPaths and operationalPaths overlap")
    if set(governed) != set(mirrored) | set(operational):
        raise SyncError(f"{branch} path classes do not partition governedPaths")
    if ROLE_PATH in governed:
        raise SyncError(f"{branch} role file must not be synchronized from main")
    if branch == "release-state":
        if operational != [".github/greasyfork-version.txt"]:
            raise SyncError("release-state operational path must remain the fallback tracker only")
        if branch_policy.get("operationalWriter") != ".github/workflows/greasyfork-release-monitor.yml":
            raise SyncError("release-state operational writer changed")
    if branch == "distribution" and operational:
        raise SyncError("distribution cannot have operational paths before cutover")
    if branch_policy.get("externalConsumersEnabled") is not False:
        raise SyncError(f"{branch} external consumers must remain disabled")
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
        raise SyncError("Operational branch definitions differ from the writer allowlist")
    for branch, branch_policy in branches.items():
        if branch == "main" or not isinstance(branch_policy, dict):
            raise SyncError("Invalid operational branch policy")
        validate_path_classes(branch, branch_policy)
    return writer


def selected_targets(value: str, writer: dict) -> list[str]:
    allowed = list(writer["allowedTargets"])
    if value == "both":
        return allowed
    if value not in allowed or value == "main":
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
    raw = git("show", f"refs/remotes/origin/{branch}:{path}")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
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


def validate_role(branch: str, role: dict, branch_policy: dict) -> None:
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
    expected_allowed = [*branch_policy["governedPaths"], ROLE_PATH]
    if role.get("allowedMutablePaths") != expected_allowed:
        raise SyncError(f"{branch} role allowedMutablePaths differs from the reviewed allowlist")
    if "main remains authoritative" not in str(role.get("authority") or ""):
        raise SyncError(f"{branch} role no longer preserves main authority")


def file_hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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


def push_branch(*, worktree: Path, branch: str, repository: str, token: str) -> None:
    url = authenticated_url(repository, token)
    result = subprocess.run(
        ["git", "push", url, f"HEAD:refs/heads/{branch}"],
        cwd=worktree,
        text=True,
        capture_output=True,
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
    role = read_branch_json(branch, ROLE_PATH)
    validate_role(branch, role, branch_policy)

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
        source_bytes = source.read_bytes()
        branch_bytes = read_branch_bytes(branch, path)
        files.append(
            {
                "path": path,
                "mode": "mirror",
                "equalBefore": source_bytes == branch_bytes,
                "sourceSha256": file_hash_bytes(source_bytes),
                "branchSha256": file_hash_bytes(branch_bytes),
            }
        )
    for path in operational_paths:
        branch_bytes = read_branch_bytes(branch, path)
        files.append(
            {
                "path": path,
                "mode": "operational-preserved",
                "equalBefore": None,
                "branchSha256": file_hash_bytes(branch_bytes),
            }
        )

    with tempfile.TemporaryDirectory(prefix=f"shadow-sync-{branch}-") as temporary:
        worktree = Path(temporary) / "worktree"
        git("worktree", "add", "--detach", str(worktree), remote_ref)
        try:
            role_before = (worktree / ROLE_PATH).read_bytes()
            operational_before = {
                path: (worktree / path).read_bytes() for path in operational_paths
            }
            for path in mirrored_paths:
                source = ROOT / path
                destination = worktree / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)

            changed = changed_paths(worktree)
            unexpected = sorted(set(changed) - set(mirrored_paths))
            if unexpected:
                raise SyncError(
                    f"{branch} synchronization changed non-mirrored paths: {unexpected}"
                )
            if (worktree / ROLE_PATH).read_bytes() != role_before:
                raise SyncError(f"{branch} role declaration changed during sync")
            for path, before in operational_before.items():
                if (worktree / path).read_bytes() != before:
                    raise SyncError(f"{branch} operational path was modified during mirror sync: {path}")

            latest_message = git("log", "-1", "--format=%B", cwd=worktree)
            probe_already_recorded = marker in latest_message
            should_commit = bool(changed) or (
                mode == "apply" and write_probe and not probe_already_recorded
            )
            pushed = False
            empty_probe = False
            after_sha = before_sha

            if mode == "apply" and should_commit:
                git("config", "user.name", "Conroy1988 shadow rehearsal", cwd=worktree)
                git(
                    "config",
                    "user.email",
                    "27301455+Conroy1988@users.noreply.github.com",
                    cwd=worktree,
                )
                if changed:
                    git("add", "--", *mirrored_paths, cwd=worktree)
                    staged = {
                        path
                        for path in git("diff", "--cached", "--name-only", cwd=worktree).splitlines()
                        if path
                    }
                    if not staged or not staged <= set(mirrored_paths):
                        raise SyncError(f"Invalid staged mirror paths: {sorted(staged)}")
                    git(
                        "commit",
                        "-m",
                        f"Rehearse {branch} mirror sync from {source_sha[:12]} {marker}",
                        cwd=worktree,
                    )
                else:
                    empty_probe = True
                    git(
                        "commit",
                        "--allow-empty",
                        "-m",
                        f"Rehearse {branch} shadow writer access from {source_sha[:12]} {marker}",
                        cwd=worktree,
                    )
                after_sha = git("rev-parse", "HEAD", cwd=worktree).strip()
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
        f"- Generated: `{report['generatedAt']}`",
        "- Public `main` changed: **no**",
        "- External consumers changed: **no**",
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
                f"- Mirror content changed: **{'yes' if branch['contentChanged'] else 'no'}**",
                f"- Empty write probe: **{'yes' if branch['emptyProbeCommit'] else 'no'}**",
                "",
            ]
        )
        for path in branch["changedPaths"]:
            lines.append(f"- Updated mirrored path: `{path}`")
        for path in branch["preservedOperationalPaths"]:
            lines.append(f"- Preserved operational path: `{path}`")
        if not branch["changedPaths"]:
            lines.append("- Mirrored content already matched `main`.")
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
                "governedPaths": [
                    "status/release-dashboard.json",
                    ".github/greasyfork-version.txt",
                ],
                "mirroredPaths": ["status/release-dashboard.json"],
                "operationalPaths": [".github/greasyfork-version.txt"],
                "operationalWriter": ".github/workflows/greasyfork-release-monitor.yml",
                "externalConsumersEnabled": False,
            },
            "distribution": {
                "governedPaths": ["dist/release-manifest.json"],
                "mirroredPaths": ["dist/release-manifest.json"],
                "operationalPaths": [],
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
    mirrored, operational = validate_path_classes(
        "release-state", policy["branches"]["release-state"]
    )
    assert mirrored == ["status/release-dashboard.json"]
    assert operational == [".github/greasyfork-version.txt"]

    try:
        selected_targets("main", writer)
    except SyncError:
        pass
    else:
        raise AssertionError("main target was not rejected")

    broken = json.loads(json.dumps(policy["branches"]["release-state"]))
    broken["mirroredPaths"].append(".github/greasyfork-version.txt")
    try:
        validate_path_classes("release-state", broken)
    except SyncError:
        pass
    else:
        raise AssertionError("operational path overlap was accepted")

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
        "schemaVersion": 2,
        "state": "synchronized" if args.mode == "apply" else "planned",
        "acceptable": True,
        "mode": args.mode,
        "targetSelection": args.target,
        "sourceBranch": "main",
        "sourceCommit": args.source_sha,
        "generatedAt": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
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
