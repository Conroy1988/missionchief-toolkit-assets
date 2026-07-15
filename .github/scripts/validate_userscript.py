#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
BASELINE = ROOT / "status" / "source-baseline.json"
CHANGELOG = ROOT / "CHANGELOG.md"
DIST = ROOT / "dist"
USER_JS = DIST / "MissionChief_Map_Command_Toolkit.user.js"
TXT = DIST / "MissionChief_Map_Command_Toolkit.txt"
SUMS = DIST / "SHA256SUMS.txt"
MANIFEST = DIST / "release-manifest.json"
INTEGRITY_AUDITOR = ROOT / ".github" / "scripts" / "check_code_integrity.py"
INTEGRITY_POLICY = ROOT / ".github" / "code-integrity-policy.json"
ASSET_AUDITOR = ROOT / ".github" / "scripts" / "check_asset_health.py"

REQUIRED_KEYS = {"name", "version"}
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
CONFLICT_RE = re.compile(r"^(?:<<<<<<< .+|=======|>>>>>>> .+)$", re.MULTILINE)
RELEASE_TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")


def fail(message: str) -> None:
    raise SystemExit(f"VALIDATION ERROR: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def metadata(text: str) -> dict[str, list[str]]:
    start = text.find("// ==UserScript==")
    end = text.find("// ==/UserScript==")
    if start < 0 or end < 0 or end <= start:
        fail("userscript metadata block is missing or malformed")

    result: dict[str, list[str]] = {}
    for line in text[start:end].splitlines():
        match = re.match(r"^//\s*@([A-Za-z0-9:_-]+)\s+(.+?)\s*$", line)
        if match:
            result.setdefault(match.group(1).lower(), []).append(match.group(2))
    return result


def one(meta: dict[str, list[str]], key: str) -> str:
    values = meta.get(key, [])
    if len(values) != 1:
        fail(f"metadata @{key} must appear exactly once")
    return values[0]


def optional_one(meta: dict[str, list[str]], key: str) -> str | None:
    values = meta.get(key, [])
    if len(values) > 1:
        fail(f"metadata @{key} must not appear more than once")
    return values[0] if values else None


def changelog_has_version(version: str) -> bool:
    if not CHANGELOG.exists():
        return False
    text = CHANGELOG.read_text(encoding="utf-8")
    return re.search(
        rf"^## \[{re.escape(version)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$",
        text,
        re.M,
    ) is not None


def is_missionchief_rule(value: str) -> bool:
    return "missionchief.co.uk" in value.casefold()


def latest_release_baseline(output: Path) -> str | None:
    source_path = SOURCE.relative_to(ROOT).as_posix()
    try:
        tags = subprocess.run(
            ["git", "tag", "--merged", "HEAD", "--sort=-version:refname"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return None

    for tag in tags:
        if not RELEASE_TAG_RE.fullmatch(tag.strip()):
            continue
        object_name = f"{tag}:{source_path}"
        exists = subprocess.run(
            ["git", "cat-file", "-e", object_name],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if exists.returncode != 0:
            continue
        try:
            payload = subprocess.run(
                ["git", "show", object_name],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError):
            continue
        output.write_bytes(payload)
        return tag
    return None


def run_integrity_gate() -> None:
    required = [INTEGRITY_AUDITOR, INTEGRITY_POLICY, ASSET_AUDITOR]
    missing = [path.relative_to(ROOT) for path in required if not path.exists()]
    if missing:
        fail(
            "integrity tooling is incomplete: "
            + ", ".join(str(path) for path in missing)
        )

    with tempfile.TemporaryDirectory(prefix="mcms-integrity-") as temp:
        baseline_path = Path(temp) / "release-baseline.user.js"
        baseline_ref = latest_release_baseline(baseline_path)
        integrity_json = Path(temp) / "code-integrity-report.json"
        integrity_markdown = Path(temp) / "code-integrity-report.md"
        asset_json = Path(temp) / "asset-health-report.json"
        asset_markdown = Path(temp) / "asset-health-report.md"

        command = [
            sys.executable,
            str(INTEGRITY_AUDITOR),
            "--candidate",
            str(SOURCE),
            "--policy",
            str(INTEGRITY_POLICY),
            "--json-output",
            str(integrity_json),
            "--markdown-output",
            str(integrity_markdown),
        ]
        if baseline_ref and baseline_path.exists():
            command.extend(["--base", str(baseline_path)])
            print(f"Code-integrity release baseline: {baseline_ref}")
        else:
            print(
                "Code-integrity release baseline unavailable; "
                "current-state checks will still run."
            )

        integrity = subprocess.run(command, cwd=ROOT)
        if integrity.returncode != 0:
            if integrity_markdown.exists():
                print(integrity_markdown.read_text(encoding="utf-8"))
            fail("expanded code-integrity audit failed")

        assets = subprocess.run(
            [
                sys.executable,
                str(ASSET_AUDITOR),
                "--mode",
                "static",
                "--json-output",
                str(asset_json),
                "--markdown-output",
                str(asset_markdown),
            ],
            cwd=ROOT,
        )
        if assets.returncode != 0:
            if asset_markdown.exists():
                print(asset_markdown.read_text(encoding="utf-8"))
            fail("static public-asset integrity audit failed")

        report = json.loads(integrity_json.read_text(encoding="utf-8"))
        metrics = report.get("metrics", {})
        print(
            "Code integrity passed: "
            f"{metrics.get('staticSelectors', 0)} static selectors, "
            f"{metrics.get('shortcutBindings', 0)} shortcut bindings, "
            f"{metrics.get('repositoryTextFiles', 0)} repository text files."
        )


def main() -> int:
    if not SOURCE.exists():
        fail(f"canonical source is missing: {SOURCE.relative_to(ROOT)}")

    raw = SOURCE.read_bytes()
    if len(raw) < 100_000:
        fail(f"source is unexpectedly small: {len(raw)} bytes")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"source is not valid UTF-8: {exc}")

    if CONFLICT_RE.search(text):
        fail("unresolved merge-conflict markers were found")

    meta = metadata(text)
    missing = sorted(REQUIRED_KEYS - set(meta))
    if missing:
        fail("missing required metadata: " + ", ".join("@" + key for key in missing))

    name = one(meta, "name")
    version = one(meta, "version")
    author = optional_one(meta, "author")
    license_name = optional_one(meta, "license")

    if "missionchief map command toolkit" not in name.casefold():
        fail(f"unexpected @name: {name}")
    if not VERSION_RE.fullmatch(version):
        fail(f"invalid semantic @version: {version}")

    matches = meta.get("match", []) + meta.get("include", [])
    missionchief_rules = [value for value in matches if is_missionchief_rule(value)]
    if not missionchief_rules:
        fail("no MissionChief UK @match or @include rule was found")

    if not changelog_has_version(version):
        fail(f"CHANGELOG.md has no release heading for version {version}")

    source_hash = hashlib.sha256(raw).hexdigest()
    baseline_match = None
    if BASELINE.exists():
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        if baseline.get("importedVersion") == version:
            baseline_match = baseline.get("sha256") == source_hash
            if not baseline_match:
                fail("source changed without a version bump from the imported baseline")

    run_integrity_gate()

    DIST.mkdir(parents=True, exist_ok=True)
    USER_JS.write_bytes(raw)
    TXT.write_bytes(raw)

    if USER_JS.read_bytes() != TXT.read_bytes():
        fail("generated .user.js and .txt files are not byte-identical")

    user_hash = sha256(USER_JS)
    txt_hash = sha256(TXT)
    SUMS.write_text(
        f"{user_hash}  {USER_JS.name}\n{txt_hash}  {TXT.name}\n",
        encoding="utf-8",
    )

    metadata_warnings = []
    if not author:
        metadata_warnings.append("@author is absent from the imported legacy baseline")
    elif "conroy1988" not in author.casefold():
        metadata_warnings.append(f"legacy @author value is {author!r}")
    if not license_name:
        metadata_warnings.append("@license is absent from the imported legacy baseline")
    elif "mit" not in license_name.casefold():
        metadata_warnings.append(f"legacy @license value is {license_name!r}")

    manifest = {
        "project": "MissionChief Map Command Toolkit",
        "version": version,
        "source": str(SOURCE.relative_to(ROOT)),
        "distributionFiles": [str(USER_JS.relative_to(ROOT)), str(TXT.relative_to(ROOT))],
        "sha256": user_hash,
        "bytes": len(raw),
        "lines": text.count("\n") + 1,
        "metadata": {
            "name": name,
            "author": author,
            "license": license_name,
            "missionChiefRules": missionchief_rules,
            "warnings": metadata_warnings,
        },
        "baselineHashMatch": baseline_match,
        "distributionStatus": "dry-run-not-yet-greasyfork-source",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "version": version,
                "sha256": user_hash,
                "bytes": len(raw),
                "lines": manifest["lines"],
                "baselineHashMatch": baseline_match,
                "metadataWarnings": metadata_warnings,
                "codeIntegrity": "passed",
                "staticAssetIntegrity": "passed",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
