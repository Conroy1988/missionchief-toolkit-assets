#!/usr/bin/env python3
"""Apply controlled Toolkit recovery-state transitions on ``release-state``.

The GitHub Release, Greasy Fork, private backup and Discord side effects remain
owned by the workflow. This module owns only the governed operational ledger:
dashboard JSON, rendered Markdown, stable update manifest and announcement
tracker. Every commit is delegated to ``release_state_branch.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / ".github" / "scripts" / "release_state_branch.py"
DASHBOARD_REL = Path("status/release-dashboard.json")
README_REL = Path("status/README.md")
MANIFEST_REL = Path("status/update-manifest.json")
TRACKER_REL = Path(".github/greasyfork-version.txt")
SETTINGS = ROOT / ".github" / "release-settings.json"
GENERATOR = ROOT / ".github" / "scripts" / "generate_release_dashboard.py"
MANIFEST_BUILDER = ROOT / ".github" / "scripts" / "build_stable_update_manifest.py"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[+-][0-9A-Za-z.-]+)?$")
FULL_HASH = re.compile(r"^[0-9a-f]{64}$")
FULL_COMMIT = re.compile(r"^[0-9a-f]{40}$")


class RecoveryStateError(RuntimeError):
    """Fail-closed recovery-state transition error."""


def run(*args: str, cwd: Path = ROOT) -> None:
    result = subprocess.run(args, cwd=cwd, text=True, check=False)
    if result.returncode != 0:
        raise RecoveryStateError(f"Command failed ({result.returncode}): {' '.join(args)}")


def write_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with Path(output).open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_version(version: str) -> str:
    if not SEMVER.fullmatch(version):
        raise RecoveryStateError(f"Invalid stable version: {version!r}")
    return version


def paths(state_root: Path) -> dict[str, Path]:
    state_root = state_root.resolve()
    return {
        "dashboard": state_root / DASHBOARD_REL,
        "readme": state_root / README_REL,
        "manifest": state_root / MANIFEST_REL,
        "tracker": state_root / TRACKER_REL,
    }


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RecoveryStateError(f"Invalid JSON file: {path}") from error
    if not isinstance(value, dict):
        raise RecoveryStateError(f"Expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def dashboard_version(dashboard: dict) -> str:
    return str((dashboard.get("latestRelease") or {}).get("version") or "").strip()


def main_dashboard() -> dict:
    return read_json(ROOT / DASHBOARD_REL)


def render_dashboard(state_root: Path) -> None:
    state = paths(state_root)
    run(
        "python3",
        str(GENERATOR),
        "--source",
        str(state["dashboard"]),
        "--output",
        str(state["readme"]),
    )


def build_manifest(state_root: Path) -> None:
    state = paths(state_root)
    run(
        "python3",
        str(MANIFEST_BUILDER),
        "--dashboard",
        str(state["dashboard"]),
        "--settings",
        str(SETTINGS),
        "--output",
        str(state["manifest"]),
    )


def commit_state(state_root: Path, message: str, changed_paths: list[Path]) -> None:
    arguments = [
        "python3",
        str(HELPER),
        "commit",
        "--worktree",
        str(state_root.resolve()),
        "--message",
        message,
    ]
    for path in changed_paths:
        arguments.extend(["--path", path.as_posix()])
    run(*arguments)


def seed_from_main(state_root: Path, version: str, allow_missing: bool = False) -> None:
    version = validate_version(version)
    state = paths(state_root)
    current = read_json(state["dashboard"])
    if dashboard_version(current) == version:
        print(f"release-state already records Toolkit v{version}")
        return

    source = main_dashboard()
    if dashboard_version(source) != version:
        if allow_missing:
            print(
                f"No v{version} dashboard seed exists on main; the requested rebuild will construct it."
            )
            return
        raise RecoveryStateError(
            f"Neither release-state nor main records the requested latest release v{version}"
        )

    for relative in [DASHBOARD_REL, README_REL, MANIFEST_REL, TRACKER_REL]:
        source_path = ROOT / relative
        target_path = state_root / relative
        if not source_path.is_file():
            raise RecoveryStateError(f"Main compatibility state is missing {relative}")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_path)

    commit_state(
        state_root,
        f"Seed Toolkit {version} recovery state from main",
        [DASHBOARD_REL, README_REL, MANIFEST_REL, TRACKER_REL],
    )


def require_release(dashboard: dict, version: str) -> dict:
    latest = dashboard.get("latestRelease") or {}
    if str(latest.get("version") or "") != version:
        raise RecoveryStateError("release-state latest release does not match recovery version")
    return latest


def record_greasyfork(state_root: Path, version: str) -> None:
    version = validate_version(version)
    state = paths(state_root)
    dashboard = read_json(state["dashboard"])
    latest = require_release(dashboard, version)
    dashboard.setdefault("status", {})["greasyForkSync"] = "verified"
    latest["greasyForkVerified"] = True
    dashboard["lastUpdated"] = now()
    write_json(state["dashboard"], dashboard)
    render_dashboard(state_root)
    commit_state(
        state_root,
        f"Record Toolkit {version} Greasy Fork recovery",
        [DASHBOARD_REL, README_REL],
    )


def record_backup(state_root: Path, version: str, backup_commit: str) -> None:
    version = validate_version(version)
    if not FULL_COMMIT.fullmatch(backup_commit):
        raise RecoveryStateError("Private backup commit must be a full commit SHA")
    state = paths(state_root)
    dashboard = read_json(state["dashboard"])
    latest = require_release(dashboard, version)
    dashboard.setdefault("status", {})["backup"] = "private-repository-verified"
    latest["privateBackupCommit"] = backup_commit
    dashboard["lastUpdated"] = now()
    write_json(state["dashboard"], dashboard)
    render_dashboard(state_root)
    commit_state(
        state_root,
        f"Record Toolkit {version} private backup recovery",
        [DASHBOARD_REL, README_REL],
    )


def claim_discord(state_root: Path, version: str, nonce: str) -> None:
    version = validate_version(version)
    if not nonce.strip():
        raise RecoveryStateError("Discord recovery nonce is required")
    state = paths(state_root)
    dashboard = read_json(state["dashboard"])
    latest = require_release(dashboard, version)
    if latest.get("greasyForkVerified") is not True:
        raise RecoveryStateError("Greasy Fork is not verified; Discord retry is blocked")
    backup_commit = str(latest.get("privateBackupCommit") or "").strip()
    if not backup_commit:
        raise RecoveryStateError("Private backup is not recorded; Discord retry is blocked")
    if latest.get("discordPosted") is True:
        write_output("skip", "true")
        print("Discord is already recorded as posted; retry suppressed.")
        return

    recovery = dashboard.setdefault("recovery", {})
    if (recovery.get("discordAnnouncement") or {}).get("state"):
        raise RecoveryStateError(
            "A previous Discord retry is pending; inspect Discord before another post"
        )
    recovery["discordAnnouncement"] = {
        "version": version,
        "state": "pending",
        "nonce": nonce,
        "startedAt": now(),
    }
    write_json(state["dashboard"], dashboard)
    render_dashboard(state_root)
    commit_state(
        state_root,
        f"Claim Toolkit {version} Discord recovery",
        [DASHBOARD_REL, README_REL],
    )
    write_output("skip", "false")
    write_output("backup_commit", backup_commit)
    write_output("nonce", nonce)


def finalize_discord(state_root: Path, version: str, expected_nonce: str) -> None:
    version = validate_version(version)
    state = paths(state_root)
    dashboard = read_json(state["dashboard"])
    latest = require_release(dashboard, version)
    claim = (dashboard.get("recovery") or {}).get("discordAnnouncement") or {}
    if str(claim.get("nonce") or "") != expected_nonce:
        raise RecoveryStateError("Discord recovery claim changed before finalization")

    completed = now()
    dashboard.setdefault("status", {})["discordRelease"] = "posted"
    latest["discordPosted"] = True
    latest["completedAt"] = str(latest.get("completedAt") or completed)
    dashboard["lastUpdated"] = completed
    recovery = dashboard.get("recovery") or {}
    recovery.pop("discordAnnouncement", None)
    if not recovery:
        dashboard.pop("recovery", None)
    write_json(state["dashboard"], dashboard)
    state["tracker"].write_text(version + "\n", encoding="utf-8")
    render_dashboard(state_root)
    build_manifest(state_root)
    commit_state(
        state_root,
        f"Record Toolkit {version} Discord recovery",
        [DASHBOARD_REL, README_REL, MANIFEST_REL, TRACKER_REL],
    )


def rebuild_dashboard(
    state_root: Path,
    version: str,
    sha256: str,
    release_url: str,
    backup_commit: str,
    discord_state: str,
) -> None:
    version = validate_version(version)
    if not FULL_HASH.fullmatch(sha256):
        raise RecoveryStateError("Release SHA-256 is invalid")
    if not FULL_COMMIT.fullmatch(backup_commit):
        raise RecoveryStateError("Private backup commit is invalid")
    if release_url != (
        f"https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v{version}"
    ):
        raise RecoveryStateError("GitHub Release URL is not canonical")
    if discord_state not in {"preserve", "posted", "not-posted"}:
        raise RecoveryStateError("Unsupported Discord rebuild state")

    state = paths(state_root)
    dashboard = read_json(state["dashboard"])
    if discord_state == "preserve":
        if dashboard_version(dashboard) != version:
            raise RecoveryStateError(
                "Cannot preserve Discord state because release-state records a different version"
            )
        discord_posted = bool((dashboard.get("latestRelease") or {}).get("discordPosted"))
    else:
        discord_posted = discord_state == "posted"

    completed = now()
    dashboard["currentVersion"] = version
    status = dashboard.setdefault("status", {})
    status.update(
        {
            "validation": "passed",
            "githubRelease": "published",
            "greasyForkSync": "verified",
            "backup": "private-repository-verified",
            "discordRelease": "posted" if discord_posted else "not-posted",
            "assetAudit": "passed",
            "releaseReadiness": "passed",
        }
    )
    dashboard["releaseReadiness"] = {
        "version": version,
        "state": "passed",
        "requiredSecrets": True,
        "privateRepositoryReadWrite": True,
        "greasyForkMetadataVerified": True,
        "publicReleaseCreated": False,
        "completedAt": completed,
    }
    dashboard["latestRelease"] = {
        "version": version,
        "sha256": sha256,
        "githubRelease": release_url,
        "greasyForkVerified": True,
        "privateBackupCommit": backup_commit,
        "discordPosted": discord_posted,
        "completedAt": completed,
    }
    dashboard["lastUpdated"] = completed
    recovery = dashboard.get("recovery") or {}
    recovery.pop("discordAnnouncement", None)
    if not recovery:
        dashboard.pop("recovery", None)
    write_json(state["dashboard"], dashboard)
    render_dashboard(state_root)

    changed = [DASHBOARD_REL, README_REL]
    if discord_posted:
        state["tracker"].write_text(version + "\n", encoding="utf-8")
        build_manifest(state_root)
        changed.extend([MANIFEST_REL, TRACKER_REL])
    commit_state(
        state_root,
        f"Rebuild Toolkit {version} release dashboard",
        changed,
    )


def self_test() -> None:
    validate_version("5.0.7")
    try:
        validate_version("latest")
    except RecoveryStateError:
        pass
    else:
        raise AssertionError("Invalid recovery version was accepted")
    assert DASHBOARD_REL.as_posix() == "status/release-dashboard.json"
    assert TRACKER_REL.as_posix() == ".github/greasyfork-version.txt"
    print("Release recovery state self-tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    subcommands = parser.add_subparsers(dest="command")

    seed = subcommands.add_parser("seed")
    seed.add_argument("--state-root", type=Path, required=True)
    seed.add_argument("--version", required=True)
    seed.add_argument("--allow-missing", action="store_true")

    greasyfork = subcommands.add_parser("record-greasyfork")
    greasyfork.add_argument("--state-root", type=Path, required=True)
    greasyfork.add_argument("--version", required=True)

    backup = subcommands.add_parser("record-backup")
    backup.add_argument("--state-root", type=Path, required=True)
    backup.add_argument("--version", required=True)
    backup.add_argument("--backup-commit", required=True)

    claim = subcommands.add_parser("claim-discord")
    claim.add_argument("--state-root", type=Path, required=True)
    claim.add_argument("--version", required=True)
    claim.add_argument("--nonce", required=True)

    finalize = subcommands.add_parser("finalize-discord")
    finalize.add_argument("--state-root", type=Path, required=True)
    finalize.add_argument("--version", required=True)
    finalize.add_argument("--nonce", required=True)

    rebuild = subcommands.add_parser("rebuild-dashboard")
    rebuild.add_argument("--state-root", type=Path, required=True)
    rebuild.add_argument("--version", required=True)
    rebuild.add_argument("--sha256", required=True)
    rebuild.add_argument("--release-url", required=True)
    rebuild.add_argument("--backup-commit", required=True)
    rebuild.add_argument("--discord-state", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.command == "seed":
        seed_from_main(args.state_root, args.version, args.allow_missing)
    elif args.command == "record-greasyfork":
        record_greasyfork(args.state_root, args.version)
    elif args.command == "record-backup":
        record_backup(args.state_root, args.version, args.backup_commit)
    elif args.command == "claim-discord":
        claim_discord(args.state_root, args.version, args.nonce)
    elif args.command == "finalize-discord":
        finalize_discord(args.state_root, args.version, args.nonce)
    elif args.command == "rebuild-dashboard":
        rebuild_dashboard(
            args.state_root,
            args.version,
            args.sha256,
            args.release_url,
            args.backup_commit,
            args.discord_state,
        )
    else:
        raise RecoveryStateError("A recovery-state command or --self-test is required")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecoveryStateError as error:
        print(f"release recovery state refused: {error}", file=os.sys.stderr)
        raise SystemExit(1)
