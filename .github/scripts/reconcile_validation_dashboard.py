#!/usr/bin/env python3
"""Reconcile canonical-validation results without destroying verified release state."""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def reconcile(dashboard: dict, manifest: dict, now: str) -> dict:
    data = deepcopy(dashboard)
    version = str(manifest.get("version") or "").strip()
    sha256 = str(manifest.get("sha256") or "").strip()
    if not version or not sha256:
        raise ValueError("release manifest must contain version and sha256")

    latest = data.get("latestRelease") or {}
    latest_matches = str(latest.get("version") or "") == version
    greasy_verified = latest_matches and latest.get("greasyForkVerified") is True
    github_published = latest_matches and bool(str(latest.get("githubRelease") or "").strip())
    backup_verified = latest_matches and bool(str(latest.get("privateBackupCommit") or "").strip())
    discord_posted = latest_matches and latest.get("discordPosted") is True

    status = data.setdefault("status", {})
    status["validation"] = "passed"
    status["githubRelease"] = "published" if github_published else "not-published"
    status["greasyForkSync"] = "verified" if greasy_verified else "pending-release"
    status["backup"] = "private-repository-verified" if backup_verified else "not-created"
    status["discordRelease"] = "posted" if discord_posted else "not-posted"

    data["currentVersion"] = version
    data["source"] = {
        "canonicalPath": "src/MissionChief_Map_Command_Toolkit.user.js",
        "validatedSha256": sha256,
        "state": "validated-canonical-source",
    }
    data["distributionCandidate"] = {
        "path": "dist/MissionChief_Map_Command_Toolkit.user.js",
        "version": version,
        "state": "validated",
    }

    if latest_matches and greasy_verified:
        data.pop("pendingRelease", None)

    data["lastUpdated"] = now
    return data


def self_test() -> None:
    base = {
        "currentVersion": "4.11.1",
        "status": {
            "validation": "unknown",
            "githubRelease": "published",
            "greasyForkSync": "verified",
            "backup": "private-repository-verified",
            "discordDevelopment": "configured",
            "discordRelease": "posted",
            "assetAudit": "passed",
        },
        "pendingRelease": {"version": "4.11.0"},
        "latestRelease": {
            "version": "4.11.2",
            "githubRelease": "https://github.test/releases/v4.11.2",
            "greasyForkVerified": True,
            "privateBackupCommit": "abc123",
            "discordPosted": True,
        },
    }
    manifest = {"version": "4.11.2", "sha256": "f" * 64}
    result = reconcile(base, manifest, "2026-01-01T00:00:00Z")
    assert result["status"]["githubRelease"] == "published"
    assert result["status"]["greasyForkSync"] == "verified"
    assert result["status"]["backup"] == "private-repository-verified"
    assert result["status"]["discordRelease"] == "posted"
    assert result["status"]["discordDevelopment"] == "configured"
    assert result["status"]["assetAudit"] == "passed"
    assert "pendingRelease" not in result
    assert result["latestRelease"] == base["latestRelease"]

    future = reconcile(base, {"version": "4.12.0", "sha256": "a" * 64}, "2026-01-02T00:00:00Z")
    assert future["status"]["githubRelease"] == "not-published"
    assert future["status"]["greasyForkSync"] == "pending-release"
    assert future["status"]["backup"] == "not-created"
    assert future["status"]["discordRelease"] == "not-posted"
    assert "pendingRelease" in future
    assert future["latestRelease"] == base["latestRelease"]

    try:
        reconcile({}, {"version": "", "sha256": ""}, "now")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid manifest was accepted")

    print("Dashboard reconciliation self-tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard", type=Path, default=Path("status/release-dashboard.json"))
    parser.add_argument("--manifest", type=Path, default=Path("dist/release-manifest.json"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--now")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    dashboard = json.loads(args.dashboard.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = reconcile(dashboard, manifest, args.now or utc_now())
    output = args.output or args.dashboard
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Reconciled validation dashboard for Toolkit {result['currentVersion']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
