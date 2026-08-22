#!/usr/bin/env python3
"""Build an opt-in, hash-addressed Toolkit canary from canonical source."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
DEFAULT_OUTPUT = ROOT / ".dev" / "canary"
DEFAULT_BASE_URL = "https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/canary/canary"
BUNDLE_NAME = "MissionChief_Map_Command_Toolkit.canary.user.js"
MANIFEST_NAME = "manifest.json"
REPOSITORY = "Conroy1988/missionchief-toolkit-assets"


class CanaryBuildError(RuntimeError):
    """The canonical source could not produce a safe canary."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise CanaryBuildError(f"Expected one {label} marker, found {count}")
    return source.replace(old, new, 1)


def git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        raise CanaryBuildError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def stable_version(source: str) -> str:
    match = re.search(r"^//\s*@version\s+(?P<version>\d+\.\d+\.\d+)\s*$", source, re.MULTILINE)
    if not match:
        raise CanaryBuildError("Canonical metadata version is missing or invalid")
    return match.group("version")


def normalise_timestamp(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc).replace(microsecond=0)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def build(
    *,
    output: Path = DEFAULT_OUTPUT,
    build_id: str = "",
    created_at: str = "",
    source_commit: str = "",
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, object]:
    canonical = SOURCE.read_text(encoding="utf-8")
    version = stable_version(canonical)
    created = normalise_timestamp(created_at)
    commit = source_commit or git_output("rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{7,40}", commit):
        raise CanaryBuildError("Source commit must be a hexadecimal Git identity")
    short_commit = commit[:10]
    generated_id = f"{created.strftime('%Y%m%dT%H%M%SZ')}-{short_commit}"
    identity = build_id or generated_id
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z._-]{5,79}", identity):
        raise CanaryBuildError("Canary build ID is invalid")
    build_version = f"{version}.{created.strftime('%Y%m%d%H%M%S')}"
    bundle_url = f"{base_url.rstrip('/')}/{BUNDLE_NAME}"

    canary = canonical
    canary = replace_once(canary, "// @name         MissionChief Map Command Toolkit", "// @name         MissionChief Map Command Toolkit — CANARY", "metadata name")
    canary = replace_once(canary, "// @namespace    https://github.com/Conroy1988/missionchief-map-command-toolkit", "// @namespace    https://github.com/Conroy1988/missionchief-map-command-toolkit/canary", "metadata namespace")
    canary = replace_once(canary, f"// @version      {version}", f"// @version      {build_version}", "metadata version")
    canary = replace_once(canary, "// @description  MissionChief operational map command centre.", f"// @description  Maintainer canary {identity}; never distributed to stable users.", "metadata description")
    canary = re.sub(r"^// @downloadURL\s+.+$", f"// @downloadURL  {bundle_url}", canary, count=1, flags=re.MULTILINE)
    canary = re.sub(r"^// @updateURL\s+.+$", f"// @updateURL    {bundle_url}", canary, count=1, flags=re.MULTILINE)
    canary = replace_once(canary, "        name: 'MissionChief Map Command Toolkit',", "        name: 'MissionChief Map Command Toolkit — CANARY',", "runtime name")
    canary = replace_once(canary, f"        version: '{version}',", f"        version: '{build_version}',", "runtime version")

    marker = json.dumps(
        {
            "buildId": identity,
            "buildVersion": build_version,
            "createdAt": created.isoformat().replace("+00:00", "Z"),
            "sourceCommit": commit,
            "stableVersion": version,
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    page_window_line = "    const pageWindow = typeof unsafeWindow !== 'undefined' ? unsafeWindow : window;"
    injection = (
        f"{page_window_line}\n"
        f"    const MCMS_CANARY_BUILD = Object.freeze({marker});\n"
        "    pageWindow.__MCMS_CANARY_RUNTIME__ = MCMS_CANARY_BUILD;\n"
        "    document.documentElement?.setAttribute('data-mcms-canary-runtime', MCMS_CANARY_BUILD.buildId);"
    )
    canary = replace_once(canary, page_window_line, injection, "canary runtime injection")

    bundle_bytes = canary.encode("utf-8")
    source_bytes = canonical.encode("utf-8")
    manifest: dict[str, object] = {
        "schemaVersion": 1,
        "channel": "canary",
        "buildId": identity,
        "buildVersion": build_version,
        "stableVersion": version,
        "createdAt": created.isoformat().replace("+00:00", "Z"),
        "minimumLoaderVersion": 1,
        "source": {
            "repository": REPOSITORY,
            "commit": commit,
            "sha256": sha256_bytes(source_bytes),
            "bytes": len(source_bytes),
        },
        "bundle": {
            "path": f"canary/{BUNDLE_NAME}",
            "url": bundle_url,
            "sha256": sha256_bytes(bundle_bytes),
            "bytes": len(bundle_bytes),
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / BUNDLE_NAME).write_bytes(bundle_bytes)
    (output / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--build-id", default="")
    parser.add_argument("--created-at", default="")
    parser.add_argument("--source-commit", default="")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = build(
        output=args.output.resolve(),
        build_id=args.build_id,
        created_at=args.created_at,
        source_commit=args.source_commit,
        base_url=args.base_url,
    )
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"Canary {manifest['buildId']} built at {args.output}")
        print(f"SHA-256: {manifest['bundle']['sha256']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CanaryBuildError as error:
        raise SystemExit(f"Canary build failed: {error}") from error
