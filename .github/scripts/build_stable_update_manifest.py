#!/usr/bin/env python3
"""Build the stable Toolkit update manifest from the verified release ledger.

The builder is deterministic and fail-closed. Production writes the resulting manifest
inside the same guarded commit as verified release state. Read-only verification jobs
render to a temporary path and compare against the committed public manifest.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DASHBOARD = ROOT / "status" / "release-dashboard.json"
DEFAULT_SETTINGS = ROOT / ".github" / "release-settings.json"
DEFAULT_OUTPUT = ROOT / "status" / "update-manifest.json"
VERSION_RE = re.compile(r"\d+\.\d+\.\d+")
REQUIRED_STATUS = {
    "validation": "passed",
    "githubRelease": "published",
    "greasyForkSync": "verified",
    "backup": "private-repository-verified",
    "discordRelease": "posted",
    "assetAudit": "passed",
    "releaseReadiness": "passed",
}


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def build_manifest(dashboard: dict, settings: dict) -> dict[str, str | int]:
    latest = dashboard.get("latestRelease") or {}
    status = dashboard.get("status") or {}
    if not isinstance(latest, dict) or not isinstance(status, dict):
        raise ValueError("Release dashboard has invalid latestRelease/status objects")

    for key, expected in REQUIRED_STATUS.items():
        actual = status.get(key)
        if actual != expected:
            raise ValueError(f"Refusing manifest publication: {key}={actual!r}, expected {expected!r}")

    version = str(latest.get("version") or "").strip()
    if not VERSION_RE.fullmatch(version):
        raise ValueError(f"Refusing manifest publication: invalid stable version {version!r}")
    if str(dashboard.get("currentVersion") or "") != version:
        raise ValueError("Dashboard currentVersion is not the verified latest release")
    if latest.get("greasyForkVerified") is not True:
        raise ValueError("Latest release is not verified on Greasy Fork")
    if latest.get("discordPosted") is not True:
        raise ValueError("Latest release is not recorded as announced to Discord")
    if not str(latest.get("privateBackupCommit") or "").strip():
        raise ValueError("Latest release has no verified private backup commit")

    release_url = str(latest.get("githubRelease") or "").strip()
    release_parts = urlparse(release_url)
    expected_path = f"/Conroy1988/missionchief-toolkit-assets/releases/tag/v{version}"
    if (
        release_parts.scheme != "https"
        or release_parts.netloc != "github.com"
        or release_parts.path != expected_path
    ):
        raise ValueError("GitHub release URL is not canonical")

    greasy_fork = settings.get("greasyFork") or {}
    if not isinstance(greasy_fork, dict):
        raise ValueError("release-settings greasyFork value is not an object")
    update_url = str(greasy_fork.get("installUrl") or "").strip()
    update_parts = urlparse(update_url)
    if (
        update_parts.scheme != "https"
        or update_parts.netloc != "update.greasyfork.org"
        or not update_parts.path.startswith("/scripts/586018/")
    ):
        raise ValueError("Greasy Fork update URL is not canonical")

    published_at = str(latest.get("completedAt") or "").strip()
    if not published_at:
        raise ValueError("Verified release completion time is absent")
    sha256 = str(latest.get("sha256") or "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ValueError("Verified release SHA-256 is invalid")

    return {
        "schemaVersion": 1,
        "channel": "stable",
        "version": version,
        "releaseNotesUrl": release_url,
        "updateUrl": update_url,
        "publishedAt": published_at,
        "sha256": sha256,
    }


def self_test() -> None:
    dashboard = {
        "currentVersion": "5.1.0",
        "status": dict(REQUIRED_STATUS),
        "latestRelease": {
            "version": "5.1.0",
            "sha256": "a" * 64,
            "githubRelease": "https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v5.1.0",
            "greasyForkVerified": True,
            "privateBackupCommit": "abc123",
            "discordPosted": True,
            "completedAt": "2026-07-24T00:00:00Z",
        },
    }
    settings = {
        "greasyFork": {
            "installUrl": "https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js"
        }
    }
    manifest = build_manifest(dashboard, settings)
    assert manifest["version"] == "5.1.0"
    assert manifest["sha256"] == "a" * 64

    broken = json.loads(json.dumps(dashboard))
    broken["status"]["discordRelease"] = "not-posted"
    try:
        build_manifest(broken, settings)
    except ValueError:
        pass
    else:
        raise AssertionError("Unannounced release was accepted")

    live_mismatch = json.loads(json.dumps(dashboard))
    live_mismatch["currentVersion"] = "5.0.9"
    try:
        build_manifest(live_mismatch, settings)
    except ValueError:
        pass
    else:
        raise AssertionError("Mismatched current/latest release versions were accepted")

    print("Stable update-manifest self-tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard", type=Path, default=DEFAULT_DASHBOARD)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0

    dashboard = load_json(args.dashboard)
    settings = load_json(args.settings)
    expected = build_manifest(dashboard, settings)

    if args.check:
        committed = load_json(args.output)
        if committed != expected:
            print("Committed stable update manifest differs from the verified release projection.")
            print(json.dumps({"expected": expected, "committed": committed}, indent=2))
            return 1
        print(f"Verified stable update manifest for Toolkit v{expected['version']}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared stable update manifest for Toolkit v{expected['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
