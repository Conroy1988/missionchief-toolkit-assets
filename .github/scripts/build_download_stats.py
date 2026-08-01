#!/usr/bin/env python3
"""Aggregate public GitHub Release asset counters for the TKB script hub."""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path


INSTALL_ASSET = "MissionChief_Map_Command_Toolkit.install.user.js"
UPDATE_ASSET = "MissionChief_Map_Command_Toolkit.update.user.js"


def load_releases(path: Path) -> list[dict]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list) and value and all(isinstance(item, list) for item in value):
        value = [release for page in value for release in page]
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise SystemExit("Download statistics input must be a list of GitHub releases")
    return value


def build(releases: list[dict]) -> dict:
    versions = []
    installs = 0
    updates = 0
    latest = None
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        tag = str(release.get("tag_name") or "")
        if not tag.startswith("v"):
            continue
        assets = {str(asset.get("name")): asset for asset in release.get("assets", []) if isinstance(asset, dict)}
        install_count = int(assets.get(INSTALL_ASSET, {}).get("download_count") or 0)
        update_count = int(assets.get(UPDATE_ASSET, {}).get("download_count") or 0)
        installs += install_count
        updates += update_count
        record = {
            "version": tag.removeprefix("v"),
            "publishedAt": release.get("published_at"),
            "releaseUrl": release.get("html_url"),
            "newInstalls": install_count,
            "successfulUpdates": update_count,
        }
        versions.append(record)
        if latest is None:
            latest = record

    return {
        "schemaVersion": 1,
        "project": "MissionChief Map Command Toolkit",
        "channel": "tkb-first-party",
        "latestVersion": latest["version"] if latest else None,
        "newInstalls": installs,
        "successfulUpdates": updates,
        "totalPackageDownloads": installs + updates,
        "measurement": {
            "newInstalls": f"GitHub Release downloads of {INSTALL_ASSET}",
            "successfulUpdates": f"GitHub Release downloads of {UPDATE_ASSET}",
            "excludes": ["metadata checks", "page views", "TKB Website funnel events", "direct source views"],
        },
        "versions": versions,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--releases", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        with tempfile.TemporaryDirectory(prefix="mcms-download-stats-") as temp_dir:
            fixture = Path(temp_dir) / "releases.json"
            fixture.write_text(json.dumps([{
                "tag_name": "v10.2.1",
                "draft": False,
                "prerelease": False,
                "published_at": "2026-08-01T12:00:00Z",
                "html_url": "https://example.invalid/releases/v10.2.1",
                "assets": [
                    {"name": INSTALL_ASSET, "download_count": 17},
                    {"name": UPDATE_ASSET, "download_count": 43},
                    {"name": "MissionChief_Map_Command_Toolkit.meta.js", "download_count": 9000},
                ],
            }, {
                "tag_name": "v10.2.0",
                "draft": False,
                "prerelease": False,
                "assets": [{"name": INSTALL_ASSET, "download_count": 4}],
            }, {
                "tag_name": "v10.3.0-beta.1",
                "draft": False,
                "prerelease": True,
                "assets": [{"name": INSTALL_ASSET, "download_count": 100}],
            }]), encoding="utf-8")
            result = build(load_releases(fixture))
            assert result["latestVersion"] == "10.2.1"
            assert result["newInstalls"] == 21
            assert result["successfulUpdates"] == 43
            assert result["totalPackageDownloads"] == 64
            assert len(result["versions"]) == 2
        print("Download statistics aggregator self-tests passed.")
        return 0
    if args.releases is None or args.output is None:
        parser.error("--releases and --output are required unless --self-test is used")
    result = build(load_releases(args.releases))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ["latestVersion", "newInstalls", "successfulUpdates", "totalPackageDownloads"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
