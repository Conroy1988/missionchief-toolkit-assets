#!/usr/bin/env python3
"""Generate the Phase 1 theme/shared-asset inventory for Issue #117.

This package is intentionally inventory-only. It must not move, copy, rename or
remove repository assets.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path.cwd()
SOURCE_PATH = Path("src/MissionChief_Map_Command_Toolkit.user.js")
JSON_PATH = Path("status/theme-asset-inventory.json")
DOC_PATH = Path(".github/THEME_ASSET_ARCHITECTURE.md")

MEDIA_EXTENSIONS = {
    ".mp3", ".wav", ".ogg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"
}
TEXT_EXTENSIONS = {
    ".js", ".txt", ".md", ".json", ".yml", ".yaml", ".html", ".css", ".py", ".toml"
}
EXCLUDED_DIRECTORIES = {
    ".git", "node_modules", "release-bundle", "__pycache__"
}

THEME_SYSTEMS = [
    {
        "order": 1,
        "internalId": "map-command",
        "displayName": "Map Command",
        "canonicalSlug": "map-command",
        "canonicalDirectory": "themes/map-command",
    },
    {
        "order": 2,
        "internalId": "cyberpunk",
        "displayName": "Cyberpunk",
        "canonicalSlug": "cyberpunk",
        "canonicalDirectory": "themes/cyberpunk",
    },
    {
        "order": 3,
        "internalId": "fallout",
        "displayName": "Fallout 4",
        "canonicalSlug": "fallout",
        "canonicalDirectory": "themes/fallout",
    },
    {
        "order": 4,
        "internalId": "umbrella",
        "displayName": "Umbrella",
        "canonicalSlug": "umbrella",
        "canonicalDirectory": "themes/umbrella",
    },
    {
        "order": 5,
        "internalId": "factorio",
        "displayName": "Factorio",
        "canonicalSlug": "factorio",
        "canonicalDirectory": "themes/factorio",
    },
    {
        "order": 6,
        "internalId": "james-bond",
        "displayName": "007 Intelligence",
        "canonicalSlug": "james-bond",
        "canonicalDirectory": "themes/james-bond",
    },
    {
        "order": 7,
        "internalId": "hyrule",
        "displayName": "Hyrule Command",
        "canonicalSlug": "hyrule",
        "canonicalDirectory": "themes/hyrule",
    },
]

AUDIO_MIGRATION = {
    "cyberpunk-cashout.mp3": "themes/cyberpunk/audio/cyberpunk-cashout.mp3",
    "fallout-cashout.mp3": "themes/fallout/audio/fallout-cashout.mp3",
    "factorio-cashout.mp3": "themes/factorio/audio/factorio-cashout.mp3",
    "james-bond-cashout.mp3": "themes/james-bond/audio/james-bond-cashout.mp3",
    "bf-bad-company-cashout.mp3": "assets/audio/payout-presets/bf-bad-company-cashout.mp3",
    "gta-vice-city-cashout.mp3": "assets/audio/payout-presets/gta-vice-city-cashout.mp3",
    "scarface-cashout.mp3": "assets/audio/payout-presets/scarface-cashout.mp3",
}

EXISTING_STRUCTURED_AUDIO = {
    "themes/umbrella/audio/umbrella-containment-cashout.mp3": "theme-owned",
    "themes/hyrule/audio/hyrule-quest-reward.mp3": "theme-owned",
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_excluded(path: Path) -> bool:
    try:
        parts = path.relative_to(ROOT).parts
    except ValueError:
        return True
    if any(part in EXCLUDED_DIRECTORIES for part in parts):
        return True
    return len(parts) >= 3 and parts[:2] == (".github", "development-packages")


def iter_repository_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*")
        if path.is_file() and not is_excluded(path)
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def version_from_source(source: str) -> str:
    match = re.search(r"^//\s*@version\s+(.+?)\s*$", source, re.MULTILINE)
    if not match:
        raise RuntimeError("Canonical userscript version could not be resolved")
    return match.group(1).strip()


def quoted_occurrences(source: str, value: str) -> int:
    return len(re.findall(rf"(?P<q>['\"])" + re.escape(value) + r"(?P=q)", source))


def classify_media(path: str) -> str:
    if path.startswith("themes/"):
        return "theme-owned"
    if path.startswith("assets/audio/payout-presets/"):
        return "shared-payout-preset"
    if "/" not in path and Path(path).suffix.lower() in {".mp3", ".wav", ".ogg"}:
        return "legacy-root-audio"
    if path.startswith("assets/"):
        return "shared-asset"
    return "other-media"


def main() -> None:
    if not SOURCE_PATH.is_file():
        raise RuntimeError(f"Canonical userscript missing: {SOURCE_PATH}")
    if JSON_PATH.exists() or DOC_PATH.exists():
        raise RuntimeError("Phase 1 inventory outputs already exist; review rather than overwrite them")

    source = read_text(SOURCE_PATH)
    version = version_from_source(source)
    repository_files = iter_repository_files()
    text_files = [
        path for path in repository_files
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name.endswith(".user.js")
    ]
    text_cache = {relative(path): read_text(path) for path in text_files}

    themes_root = ROOT / "themes"
    existing_theme_directories = sorted(
        path for path in themes_root.iterdir() if path.is_dir()
    ) if themes_root.is_dir() else []

    theme_directory_inventory = []
    for directory in existing_theme_directories:
        files = sorted(path for path in directory.rglob("*") if path.is_file())
        media = [path for path in files if path.suffix.lower() in MEDIA_EXTENSIONS]
        theme_directory_inventory.append(
            {
                "slug": directory.name,
                "path": relative(directory),
                "fileCount": len(files),
                "mediaCount": len(media),
                "files": [
                    {
                        "path": relative(path),
                        "bytes": path.stat().st_size,
                        "sha256": sha256(path),
                    }
                    for path in files
                ],
            }
        )

    existing_slugs = {entry["slug"] for entry in theme_directory_inventory}
    themes = []
    for item in THEME_SYSTEMS:
        entry = dict(item)
        entry["directoryExists"] = item["canonicalSlug"] in existing_slugs
        entry["sourceEvidence"] = {
            "internalIdQuotedOccurrences": quoted_occurrences(source, item["internalId"]),
            "displayNameOccurrences": source.count(item["displayName"]),
        }
        themes.append(entry)

    media_files = [path for path in repository_files if path.suffix.lower() in MEDIA_EXTENSIONS]
    media_inventory = []
    references_by_media: dict[str, list[str]] = defaultdict(list)
    for media in media_files:
        media_path = relative(media)
        tokens = {media_path, media.name}
        for text_path, text in text_cache.items():
            if any(token in text for token in tokens):
                references_by_media[media_path].append(text_path)
        media_inventory.append(
            {
                "path": media_path,
                "classification": classify_media(media_path),
                "extension": media.suffix.lower(),
                "bytes": media.stat().st_size,
                "sha256": sha256(media),
                "referenceFiles": sorted(references_by_media[media_path]),
                "canonicalSourceReference": media_path in source or media.name in source,
            }
        )

    root_audio = sorted(
        item for item in media_inventory
        if item["classification"] == "legacy-root-audio"
    , key=lambda item: item["path"])
    root_paths = {item["path"] for item in root_audio}
    missing_legacy = sorted(set(AUDIO_MIGRATION) - root_paths)
    if missing_legacy:
        raise RuntimeError(f"Expected public root audio paths are missing: {missing_legacy}")

    missing_existing_structured = sorted(
        path for path in EXISTING_STRUCTURED_AUDIO if not (ROOT / path).is_file()
    )
    if missing_existing_structured:
        raise RuntimeError(f"Expected structured audio paths are missing: {missing_existing_structured}")

    canonical_targets = []
    for legacy, canonical in AUDIO_MIGRATION.items():
        source_entry = next(item for item in root_audio if item["path"] == legacy)
        canonical_targets.append(
            {
                "legacyPath": legacy,
                "canonicalPath": canonical,
                "classification": "theme-owned" if canonical.startswith("themes/") else "shared-payout-preset",
                "legacySha256": source_entry["sha256"],
                "legacyBytes": source_entry["bytes"],
                "legacyReferenceFiles": source_entry["referenceFiles"],
                "canonicalExists": (ROOT / canonical).is_file(),
                "decision": "create-canonical-copy-and-retain-legacy-alias",
            }
        )

    raw_theme_path_references = sorted(set(re.findall(r"themes/[A-Za-z0-9._/-]+", source)))
    raw_asset_path_references = sorted(set(re.findall(r"assets/[A-Za-z0-9._/-]+", source)))

    inventory = {
        "schemaVersion": 1,
        "generatedAt": "2026-07-17",
        "issue": 117,
        "phase": 1,
        "currentVersion": version,
        "source": SOURCE_PATH.as_posix(),
        "constraints": {
            "inventoryOnly": True,
            "assetsMoved": False,
            "assetsCopied": False,
            "assetsDeleted": False,
            "runtimeChanged": False,
        },
        "themeSystems": themes,
        "existingThemeDirectories": theme_directory_inventory,
        "missingCanonicalThemeDirectories": sorted(
            item["canonicalDirectory"] for item in themes if not item["directoryExists"]
        ),
        "mediaSummary": {
            "totalMediaFiles": len(media_inventory),
            "audioFiles": sum(1 for item in media_inventory if item["extension"] in {".mp3", ".wav", ".ogg"}),
            "legacyRootAudioFiles": len(root_audio),
            "themeOwnedMediaFiles": sum(1 for item in media_inventory if item["classification"] == "theme-owned"),
        },
        "mediaFiles": media_inventory,
        "currentSourceAssetReferences": {
            "themePaths": raw_theme_path_references,
            "sharedAssetPaths": raw_asset_path_references,
        },
        "canonicalAudioMigration": canonical_targets,
        "existingStructuredAudio": sorted(EXISTING_STRUCTURED_AUDIO),
        "canonicalSlugDecision": {
            item["displayName"]: item["canonicalSlug"] for item in themes
        },
        "namingNotes": [
            {
                "subject": "007 Intelligence",
                "decision": "Retain the stable internal/canonical slug james-bond while keeping 007 Intelligence as the public display name.",
            },
            {
                "subject": "Non-theme payout presets",
                "decision": "Bad Company, Vice City and Scarface belong under assets/audio/payout-presets, not under themes/.",
            },
            {
                "subject": "Legacy root audio",
                "decision": "All seven public root paths remain indefinitely as compatibility aliases after the current Toolkit migrates.",
            },
        ],
    }

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    directory_rows = []
    for item in themes:
        state = "Present" if item["directoryExists"] else "Create in migration"
        evidence = item["sourceEvidence"]
        directory_rows.append(
            f"| {item['order']} | {item['displayName']} | `{item['internalId']}` | `{item['canonicalDirectory']}` | {state} | "
            f"ID: {evidence['internalIdQuotedOccurrences']}; name: {evidence['displayNameOccurrences']} |"
        )

    migration_rows = []
    for item in canonical_targets:
        owner = "Interface system" if item["classification"] == "theme-owned" else "Shared payout preset"
        migration_rows.append(
            f"| `{item['legacyPath']}` | `{item['canonicalPath']}` | {owner} | Retain root alias |"
        )

    existing_rows = []
    for item in theme_directory_inventory:
        existing_rows.append(
            f"| `{item['path']}` | {item['fileCount']} | {item['mediaCount']} |"
        )
    if not existing_rows:
        existing_rows.append("| _None_ | 0 | 0 |")

    doc = f"""# Theme and shared-asset architecture

> Phase 1 inventory for [Issue #117](https://github.com/Conroy1988/missionchief-toolkit-assets/issues/117). Generated from Toolkit **v{version}** on 17 July 2026.

## Safety status

This change is **inventory only**. No media file was copied, moved, renamed or removed, and no Toolkit runtime or distribution file was changed.

## Canonical interface-system folders

The seven interface systems remain equal. Folder slugs follow stable internal identities; public presentation names remain unchanged.

| Order | Interface system | Internal ID | Canonical folder | Current state | Source evidence |
|---:|---|---|---|---|---:|
{chr(10).join(directory_rows)}

### Existing `themes/` directories

| Directory | Files | Media files |
|---|---:|---:|
{chr(10).join(existing_rows)}

The complete file-level inventory, hashes and references are recorded in [`status/theme-asset-inventory.json`](../status/theme-asset-inventory.json).

## Audio ownership and canonical migration

| Existing public path | Canonical active path | Ownership | Compatibility treatment |
|---|---|---|---|
{chr(10).join(migration_rows)}

Already-structured audio remains at:

- `themes/umbrella/audio/umbrella-containment-cashout.mp3`
- `themes/hyrule/audio/hyrule-quest-reward.mp3`

## Compatibility contract to implement

1. The current Toolkit will reference only canonical structured paths.
2. The seven root files will remain available as legacy compatibility aliases.
3. Every alias must be byte-identical to its canonical target.
4. Asset Health will permit duplicates only when declared in the alias manifest.
5. Missing aliases, mismatched hashes, undeclared duplicates and orphaned canonical audio will fail CI.

## Naming decisions

- **007 Intelligence** keeps the stable `james-bond` internal and folder slug; only the display identity uses 007 Intelligence.
- **Bad Company**, **Vice City** and **Scarface** are payout presentation presets, not Toolkit interface systems.
- **Map Command** receives a canonical folder even when it currently has no external media, keeping all seven systems structurally equal.

## Phase 2 entry gates

Asset movement may begin only after this inventory confirms:

- the real `themes/` tree and all media hashes;
- the seven internal/display identities;
- the root-to-canonical audio mapping;
- every current source, distribution, documentation and policy reference;
- preservation of all seven public root URLs.

The next implementation must use a separate reviewed pull request and a normal Toolkit version/release cycle.
"""
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(doc, encoding="utf-8")

    print(f"Wrote {JSON_PATH} and {DOC_PATH}")
    print(f"Theme directories discovered: {len(theme_directory_inventory)}")
    print(f"Media files inventoried: {len(media_inventory)}")
    print("No media or runtime files changed.")


if __name__ == "__main__":
    main()
