#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
CANDIDATES = [
    "biohazard-containment-cashout.mp3",
    "biohazzard-cashout.mp3",
    "dark-fantasy-cashout.mp3",
    "galactic-cashout.mp3",
    "gtav-cashout.mp3",
    "hellfire-cashout.mp3",
]
ACTIVE_AUDIO = [
    "bf-bad-company-cashout.mp3",
    "cyberpunk-cashout.mp3",
    "factorio-cashout.mp3",
    "fallout-cashout.mp3",
    "gta-vice-city-cashout.mp3",
    "james-bond-cashout.mp3",
    "scarface-cashout.mp3",
    "themes/umbrella/audio/umbrella-containment-cashout.mp3",
    "themes/hyrule/audio/hyrule-quest-reward.mp3",
]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)


def tracked_userscript_sources() -> list[Path]:
    sources: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith((".git/", ".github/development-packages/", "node_modules/", "release-bundle/")):
            continue
        if path.name.endswith(".user.js") or (
            path.suffix.lower() == ".txt" and "MissionChief_Map_Command_Toolkit" in path.name
        ):
            sources.append(path)
    return sorted(sources)


def current_references() -> tuple[list[str], dict[str, list[str]]]:
    sources = tracked_userscript_sources()
    findings = {candidate: [] for candidate in CANDIDATES}
    for path in sources:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        for candidate in CANDIDATES:
            if candidate in text:
                findings[candidate].append(rel)
    return [path.relative_to(ROOT).as_posix() for path in sources], findings


def tag_references() -> tuple[list[str], dict[str, list[str]]]:
    run("git", "fetch", "--tags", "--force", "origin")
    tags = [line.strip() for line in run("git", "tag", "--list").stdout.splitlines() if line.strip()]
    findings = {candidate: [] for candidate in CANDIDATES}
    pathspecs = ["*.user.js", "*.js", "*MissionChief_Map_Command_Toolkit*.txt"]
    for tag in tags:
        for candidate in CANDIDATES:
            completed = run(
                "git", "grep", "-n", "-F", candidate, tag, "--", *pathspecs, check=False
            )
            if completed.returncode not in {0, 1}:
                raise RuntimeError(
                    f"git grep failed for {candidate!r} in {tag}: {completed.stderr.strip()}"
                )
            if completed.returncode == 0:
                findings[candidate].extend(
                    f"{tag}:{line}" for line in completed.stdout.splitlines() if line.strip()
                )
    return tags, findings


def assert_zero_references(current: dict[str, list[str]], tags: dict[str, list[str]]) -> None:
    blocked = {
        candidate: {"current": current[candidate], "tags": tags[candidate]}
        for candidate in CANDIDATES
        if current[candidate] or tags[candidate]
    }
    if blocked:
        raise RuntimeError(
            "Refusing to delete payout audio with textual userscript references:\n"
            + json.dumps(blocked, indent=2)
        )


def update_asset_health_tests() -> None:
    path = ROOT / ".github/scripts/test_asset_health.py"
    text = path.read_text(encoding="utf-8")

    constants_anchor = 'SCRIPT_PATH = Path(__file__).with_name("check_asset_health.py")\n'
    constants = '''SCRIPT_PATH = Path(__file__).with_name("check_asset_health.py")
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_USERSCRIPT = "src/MissionChief_Map_Command_Toolkit.user.js"
ACTIVE_AUDIO_PATHS = {
    "bf-bad-company-cashout.mp3",
    "cyberpunk-cashout.mp3",
    "factorio-cashout.mp3",
    "fallout-cashout.mp3",
    "gta-vice-city-cashout.mp3",
    "james-bond-cashout.mp3",
    "scarface-cashout.mp3",
    "themes/umbrella/audio/umbrella-containment-cashout.mp3",
    "themes/hyrule/audio/hyrule-quest-reward.mp3",
}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg"}
'''
    if "ACTIVE_AUDIO_PATHS" not in text:
        if text.count(constants_anchor) != 1:
            raise RuntimeError("Could not locate test_asset_health constants anchor")
        text = text.replace(constants_anchor, constants, 1)

    function_anchor = "\n\ndef main() -> None:\n"
    function = r'''


def test_repository_audio_contract() -> None:
    policy = asset_health.load_json(REPOSITORY_ROOT / ".github/asset-health-policy.json")
    canonical_policy = dict(policy)
    canonical_policy["scanFiles"] = [CANONICAL_USERSCRIPT]
    canonical_policy["scanTextExtensions"] = []

    endpoints, _, local_media = asset_health.discover_endpoints(
        REPOSITORY_ROOT,
        canonical_policy,
        "Conroy1988/missionchief-toolkit-assets",
    )
    audio_paths = {
        asset_health.relative_path(path, REPOSITORY_ROOT)
        for path in local_media
        if path.suffix.lower() in AUDIO_EXTENSIONS
    }
    referenced_audio = {
        endpoint.local_path
        for endpoint in endpoints
        if endpoint.local_path
        and Path(endpoint.local_path).suffix.lower() in AUDIO_EXTENSIONS
        and endpoint.source != "repository-media"
    }

    missing_required = sorted(ACTIVE_AUDIO_PATHS - audio_paths)
    unreferenced_required = sorted(ACTIVE_AUDIO_PATHS - referenced_audio)
    orphaned = sorted(audio_paths - referenced_audio)
    assert not missing_required, f"Required public audio paths are missing: {missing_required}"
    assert not unreferenced_required, f"Required public audio paths are no longer referenced: {unreferenced_required}"
    assert not orphaned, f"Unreferenced repository audio assets detected: {orphaned}"

    hashes: dict[str, list[str]] = {}
    for rel in sorted(audio_paths):
        digest = hashlib.sha256((REPOSITORY_ROOT / rel).read_bytes()).hexdigest()
        hashes.setdefault(digest, []).append(rel)
    duplicates = [paths for paths in hashes.values() if len(paths) > 1]
    assert not duplicates, f"Duplicate repository audio payloads detected: {duplicates}"
'''
    if "def test_repository_audio_contract()" not in text:
        if text.count(function_anchor) != 1:
            raise RuntimeError("Could not locate test_asset_health main anchor")
        text = text.replace(function_anchor, function + function_anchor, 1)

    list_anchor = "        test_base_url_filename_resolution\n"
    replacement = "        test_base_url_filename_resolution,\n        test_repository_audio_contract\n"
    if "        test_repository_audio_contract\n" not in text:
        if text.count(list_anchor) != 1:
            raise RuntimeError("Could not locate test list anchor")
        text = text.replace(list_anchor, replacement, 1)

    path.write_text(text, encoding="utf-8")


def update_documentation() -> None:
    path = ROOT / ".github/ASSET_HEALTH.md"
    text = path.read_text(encoding="utf-8")
    marker = "## Repository audio contract"
    if marker in text:
        return
    text = text.rstrip() + r'''

## Repository audio contract

The asset-health self-test also enforces the payout-audio inventory:

- every retained public payout-audio path must exist and remain referenced by the canonical userscript;
- newly added `.mp3`, `.wav` or `.ogg` files must be referenced by the canonical userscript;
- byte-identical audio duplicates are rejected;
- historical releases are protected by an explicit tag scan before any legacy asset is removed.

This contract deliberately preserves the active root-level raw GitHub URLs. Repository tidiness must never silently break an installed or previously published Toolkit version.
''' + "\n"
    path.write_text(text, encoding="utf-8")


def write_audit(
    sources: list[str],
    current: dict[str, list[str]],
    tags: list[str],
    historical: dict[str, list[str]],
) -> None:
    audit = {
        "schemaVersion": 1,
        "generatedAt": "2026-07-17",
        "issue": 115,
        "currentVersion": "4.14.6",
        "method": {
            "currentTree": "Exact filename scan across every retained userscript and Toolkit text distribution.",
            "publishedHistory": "Exact filename scan across userscript, JavaScript and Toolkit text files in every fetched Git tag.",
        },
        "scannedCurrentSources": sources,
        "scannedTags": tags,
        "retainedAudioPaths": ACTIVE_AUDIO,
        "removedCandidates": {
            candidate: {
                "currentReferences": current[candidate],
                "tagReferences": historical[candidate],
                "referenceCount": len(current[candidate]) + len(historical[candidate]),
                "decision": "remove-zero-reference-orphan",
            }
            for candidate in CANDIDATES
        },
    }
    path = ROOT / "status/media-asset-audit.json"
    path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")


def delete_candidates() -> None:
    missing = [candidate for candidate in CANDIDATES if not (ROOT / candidate).is_file()]
    if missing:
        raise RuntimeError(f"Expected cleanup candidates are missing before deletion: {missing}")
    for candidate in CANDIDATES:
        (ROOT / candidate).unlink()


def validate() -> None:
    run(sys.executable, ".github/scripts/test_asset_health.py")
    run(
        sys.executable,
        ".github/scripts/check_asset_health.py",
        "--mode",
        "static",
        "--json-output",
        "/tmp/issue-115-asset-health.json",
        "--markdown-output",
        "/tmp/issue-115-asset-health.md",
    )
    for candidate in CANDIDATES:
        if (ROOT / candidate).exists():
            raise RuntimeError(f"Cleanup candidate still exists: {candidate}")


def main() -> None:
    sources, current = current_references()
    tags, historical = tag_references()
    assert_zero_references(current, historical)
    delete_candidates()
    update_asset_health_tests()
    update_documentation()
    write_audit(sources, current, tags, historical)
    validate()
    print(
        f"Issue #115 cleanup complete: removed {len(CANDIDATES)} zero-reference audio files; "
        f"retained {len(ACTIVE_AUDIO)} public audio paths; scanned {len(tags)} tags."
    )


if __name__ == "__main__":
    main()
