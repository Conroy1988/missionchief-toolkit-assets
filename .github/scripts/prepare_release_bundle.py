#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
CHANGELOG = ROOT / "CHANGELOG.md"
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
OUTPUT = ROOT / "release-bundle"


def fail(message: str) -> None:
    raise SystemExit(f"RELEASE PREPARATION ERROR: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_release_notes(version: str) -> str:
    text = CHANGELOG.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^## \[{re.escape(version)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$\n(.*?)(?=^## \[|\Z)",
        re.M | re.S,
    )
    match = pattern.search(text)
    if not match:
        fail(f"CHANGELOG.md has no section for {version}")
    notes = match.group(1).strip()
    if not notes:
        fail(f"CHANGELOG.md section for {version} is empty")
    return notes + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: prepare_release_bundle.py <version>")

    requested_version = sys.argv[1].strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", requested_version):
        fail(f"invalid version: {requested_version}")

    manifest_path = DIST / "release-manifest.json"
    if not manifest_path.exists():
        fail("dist/release-manifest.json is missing; run validation first")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    built_version = str(manifest.get("version", ""))
    if built_version != requested_version:
        fail(f"requested version {requested_version} does not match validated dist version {built_version}")

    required = [
        SOURCE,
        DIST / "MissionChief_Map_Command_Toolkit.user.js",
        DIST / "MissionChief_Map_Command_Toolkit.txt",
        DIST / "SHA256SUMS.txt",
        manifest_path,
        CHANGELOG,
    ]
    for path in required:
        if not path.exists():
            fail(f"required release input is missing: {path.relative_to(ROOT)}")

    source_hash = sha256(SOURCE)
    dist_hash = sha256(DIST / "MissionChief_Map_Command_Toolkit.user.js")
    txt_hash = sha256(DIST / "MissionChief_Map_Command_Toolkit.txt")
    manifest_hash = str(manifest.get("sha256", ""))
    if len({source_hash, dist_hash, txt_hash, manifest_hash}) != 1:
        fail("canonical source, distribution files and manifest hashes do not match")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    versioned_user = OUTPUT / f"MissionChief_Map_Command_Toolkit_v{requested_version}.user.js"
    versioned_txt = OUTPUT / f"MissionChief_Map_Command_Toolkit_v{requested_version}.txt"
    shutil.copy2(DIST / "MissionChief_Map_Command_Toolkit.user.js", versioned_user)
    shutil.copy2(DIST / "MissionChief_Map_Command_Toolkit.txt", versioned_txt)
    shutil.copy2(DIST / "SHA256SUMS.txt", OUTPUT / "SHA256SUMS.txt")

    notes = extract_release_notes(requested_version)
    (OUTPUT / f"CHANGELOG-v{requested_version}.md").write_text(
        f"# MissionChief Map Command Toolkit v{requested_version}\n\n{notes}",
        encoding="utf-8",
    )

    release_manifest = {
        **manifest,
        "releaseMode": "dry-run",
        "preparedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "releaseTag": f"v{requested_version}",
        "releaseNotesFile": f"CHANGELOG-v{requested_version}.md",
        "bundleFiles": [
            versioned_user.name,
            versioned_txt.name,
            "SHA256SUMS.txt",
            f"CHANGELOG-v{requested_version}.md",
            f"release-manifest-v{requested_version}.json",
            f"migration-handover-v{requested_version}.md",
        ],
    }
    (OUTPUT / f"release-manifest-v{requested_version}.json").write_text(
        json.dumps(release_manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    (OUTPUT / f"migration-handover-v{requested_version}.md").write_text(
        "\n".join(
            [
                f"# MissionChief Map Command Toolkit v{requested_version} — migration handover",
                "",
                "## Release state",
                "",
                "- GitHub canonical source: validated",
                "- Distribution bundle: prepared in dry-run mode",
                "- GitHub Release: not published",
                "- Greasy Fork: unchanged and still serving the live public script",
                "- Discord release announcement: not sent",
                "",
                "## Integrity",
                "",
                f"- SHA-256: `{source_hash}`",
                f"- Source bytes: `{manifest.get('bytes')}`",
                f"- Source lines: `{manifest.get('lines')}`",
                "",
                "## Next approval gate",
                "",
                "Configure Greasy Fork code synchronisation to the validated GitHub distribution URL only after the release workflow has passed an end-to-end dry run.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps({
        "version": requested_version,
        "sha256": source_hash,
        "bundle": str(OUTPUT.relative_to(ROOT)),
        "files": sorted(path.name for path in OUTPUT.iterdir()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
