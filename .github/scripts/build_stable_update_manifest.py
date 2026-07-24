#!/usr/bin/env python3
"""Build or verify the stable Toolkit update manifest.

The stable manifest is derived only from the verified release dashboard and
reviewed release settings. The same implementation is used by production and
read-only verification so the public compatibility URL cannot drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DASHBOARD = ROOT / "status" / "release-dashboard.json"
DEFAULT_SETTINGS = ROOT / ".github" / "release-settings.json"
DEFAULT_OUTPUT = ROOT / "status" / "update-manifest.json"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(RuntimeError):
    """Fail-closed manifest validation error."""


@dataclass(frozen=True)
class BuildResult:
    manifest: dict[str, object]
    rendered: str
    changed: bool


def load_object(path: Path, label: str) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ManifestError(f"{label} is missing or unsafe: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestError(f"{label} is not valid JSON: {path}") from error
    if not isinstance(value, dict):
        raise ManifestError(f"{label} must be a JSON object: {path}")
    return value


def canonical_release_url(version: str, value: object) -> str:
    url = str(value or "").strip()
    parts = urlparse(url)
    expected_path = f"/Conroy1988/missionchief-toolkit-assets/releases/tag/v{version}"
    if parts.scheme != "https" or parts.netloc != "github.com" or parts.path != expected_path:
        raise ManifestError("GitHub release URL is not canonical")
    if parts.params or parts.query or parts.fragment:
        raise ManifestError("GitHub release URL must not contain params, query or fragment")
    return url


def canonical_update_url(value: object) -> str:
    url = str(value or "").strip()
    parts = urlparse(url)
    if parts.scheme != "https" or parts.netloc != "update.greasyfork.org":
        raise ManifestError("Greasy Fork update URL is not canonical")
    if not parts.path.startswith("/scripts/586018/"):
        raise ManifestError("Greasy Fork update URL does not target Toolkit script 586018")
    if parts.params or parts.query or parts.fragment:
        raise ManifestError("Greasy Fork update URL must not contain params, query or fragment")
    return url


def build_manifest(dashboard: dict, settings: dict) -> dict[str, object]:
    status = dashboard.get("status")
    latest = dashboard.get("latestRelease")
    if not isinstance(status, dict) or not isinstance(latest, dict):
        raise ManifestError("Release dashboard is missing status or latestRelease objects")

    required_status = {
        "validation": "passed",
        "githubRelease": "published",
        "greasyForkSync": "verified",
        "backup": "private-repository-verified",
        "discordRelease": "posted",
        "assetAudit": "passed",
        "releaseReadiness": "passed",
    }
    for key, expected in required_status.items():
        actual = status.get(key)
        if actual != expected:
            raise ManifestError(f"Refusing stable manifest: {key}={actual!r}, expected {expected!r}")

    version = str(latest.get("version") or "").strip()
    if not SEMVER.fullmatch(version):
        raise ManifestError(f"Stable semantic version required, found {version!r}")
    if str(dashboard.get("currentVersion") or "").strip() != version:
        raise ManifestError("Dashboard currentVersion is not the verified latest release")
    if latest.get("greasyForkVerified") is not True:
        raise ManifestError("Greasy Fork is not verified")
    if latest.get("discordPosted") is not True:
        raise ManifestError("Discord release is not recorded")
    if not str(latest.get("privateBackupCommit") or "").strip():
        raise ManifestError("Private backup commit is absent")

    sha256 = str(latest.get("sha256") or "").strip()
    if not SHA256.fullmatch(sha256):
        raise ManifestError("Verified release SHA-256 is invalid")

    published_at = str(latest.get("completedAt") or "").strip()
    if not published_at:
        raise ManifestError("Verified release completion time is absent")

    greasy_fork = settings.get("greasyFork")
    if not isinstance(greasy_fork, dict):
        raise ManifestError("Release settings are missing greasyFork configuration")

    return {
        "schemaVersion": 1,
        "channel": "stable",
        "version": version,
        "releaseNotesUrl": canonical_release_url(version, latest.get("githubRelease")),
        "updateUrl": canonical_update_url(greasy_fork.get("installUrl")),
        "publishedAt": published_at,
        "sha256": sha256,
    }


def render_manifest(manifest: dict[str, object]) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build(dashboard_path: Path, settings_path: Path, output_path: Path, check: bool) -> BuildResult:
    manifest = build_manifest(
        load_object(dashboard_path, "Release dashboard"),
        load_object(settings_path, "Release settings"),
    )
    rendered = render_manifest(manifest)
    existing = output_path.read_text(encoding="utf-8") if output_path.is_file() else None
    changed = existing != rendered

    if check:
        if existing is None:
            raise ManifestError(f"Committed stable manifest is missing: {output_path}")
        if changed:
            raise ManifestError("Committed stable update manifest differs from the verified release projection")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")

    return BuildResult(manifest=manifest, rendered=rendered, changed=changed)


def evidence(result: BuildResult, *, check: bool, dashboard_path: Path, output_path: Path) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "state": "synchronized" if check else "prepared",
        "mode": "check" if check else "write",
        "version": result.manifest["version"],
        "sha256": result.manifest["sha256"],
        "manifestSha256": sha256_text(result.rendered),
        "dashboardPath": dashboard_path.relative_to(ROOT).as_posix() if dashboard_path.is_relative_to(ROOT) else str(dashboard_path),
        "outputPath": output_path.relative_to(ROOT).as_posix() if output_path.is_relative_to(ROOT) else str(output_path),
        "manifestChanged": result.changed,
        "publicMainChanged": False,
        "releaseDashboardChanged": False,
        "liveConsumersChanged": False,
    }


def render_evidence_markdown(report: dict[str, object]) -> str:
    return "\n".join(
        [
            "# Toolkit stable update-manifest verification",
            "",
            f"- State: **{report['state']}**",
            f"- Mode: `{report['mode']}`",
            f"- Version: `v{report['version']}`",
            f"- Release SHA-256: `{report['sha256']}`",
            f"- Manifest SHA-256: `{report['manifestSha256']}`",
            f"- Manifest changed: **{'yes' if report['manifestChanged'] else 'no'}**",
            "- Public `main` changed by verification: **no**",
            "- Release dashboard changed: **no**",
            "- Live consumers changed: **no**",
            "",
        ]
    )


def self_test() -> None:
    dashboard = {
        "currentVersion": "1.2.3",
        "status": {
            "validation": "passed",
            "githubRelease": "published",
            "greasyForkSync": "verified",
            "backup": "private-repository-verified",
            "discordRelease": "posted",
            "assetAudit": "passed",
            "releaseReadiness": "passed",
        },
        "latestRelease": {
            "version": "1.2.3",
            "sha256": "a" * 64,
            "githubRelease": "https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v1.2.3",
            "greasyForkVerified": True,
            "privateBackupCommit": "b" * 40,
            "discordPosted": True,
            "completedAt": "2026-07-24T12:00:00Z",
        },
    }
    settings = {
        "greasyFork": {
            "installUrl": "https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js"
        }
    }
    expected = build_manifest(dashboard, settings)
    assert expected["version"] == "1.2.3"
    assert expected["sha256"] == "a" * 64

    broken = json.loads(json.dumps(dashboard))
    broken["status"]["discordRelease"] = "pending"
    try:
        build_manifest(broken, settings)
    except ManifestError:
        pass
    else:
        raise AssertionError("Incomplete release status was accepted")

    with tempfile.TemporaryDirectory(prefix="manifest-self-test-") as directory:
        root = Path(directory)
        dashboard_path = root / "dashboard.json"
        settings_path = root / "settings.json"
        output_path = root / "manifest.json"
        dashboard_path.write_text(json.dumps(dashboard), encoding="utf-8")
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        first = build(dashboard_path, settings_path, output_path, check=False)
        assert first.changed is True
        second = build(dashboard_path, settings_path, output_path, check=True)
        assert second.changed is False
        output_path.write_text("{}\n", encoding="utf-8")
        try:
            build(dashboard_path, settings_path, output_path, check=True)
        except ManifestError:
            pass
        else:
            raise AssertionError("Manifest drift was not rejected")

    print("Stable update manifest self-tests passed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dashboard", type=Path, default=DEFAULT_DASHBOARD)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--evidence-json", type=Path)
    parser.add_argument("--evidence-markdown", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0

    result = build(args.dashboard, args.settings, args.output, args.check)
    report = evidence(result, check=args.check, dashboard_path=args.dashboard, output_path=args.output)
    if args.evidence_json:
        args.evidence_json.parent.mkdir(parents=True, exist_ok=True)
        args.evidence_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.evidence_markdown:
        args.evidence_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.evidence_markdown.write_text(render_evidence_markdown(report), encoding="utf-8")
    print(f"Stable update manifest {report['state']} for Toolkit v{report['version']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ManifestError as error:
        print(f"stable update manifest refused: {error}", file=__import__("sys").stderr)
        raise SystemExit(1)
