#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
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

REQUIRED_KEYS = {"name", "version", "author", "license"}
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")


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

    if any(marker in text for marker in ("<<<<<<<", "=======", ">>>>>>>")):
        fail("unresolved merge-conflict markers were found")

    meta = metadata(text)
    missing = sorted(REQUIRED_KEYS - set(meta))
    if missing:
        fail("missing required metadata: " + ", ".join("@" + key for key in missing))

    name = one(meta, "name")
    version = one(meta, "version")
    author = one(meta, "author")
    license_name = one(meta, "license")

    if "missionchief map command toolkit" not in name.casefold():
        fail(f"unexpected @name: {name}")
    if not VERSION_RE.fullmatch(version):
        fail(f"invalid semantic @version: {version}")
    if "conroy1988" not in author.casefold():
        fail(f"unexpected @author: {author}")
    if "mit" not in license_name.casefold():
        fail(f"unexpected @license: {license_name}")

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
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
