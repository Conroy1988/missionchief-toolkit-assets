#!/usr/bin/env python3
"""Correct Phase 1 identity and raw-path evidence for Issue #117."""

from __future__ import annotations

import json
import re
from pathlib import Path

SOURCE_PATH = Path("src/MissionChief_Map_Command_Toolkit.user.js")
INVENTORY_PATH = Path("status/theme-asset-inventory.json")
DOC_PATH = Path(".github/THEME_ASSET_ARCHITECTURE.md")
EVIDENCE_PATH = Path("status/theme-id-evidence.json")

CANONICAL = {
    "mapCommand": {"publicName": "Map Command", "canonicalSlug": "map-command"},
    "cyberpunk": {"publicName": "Cyberpunk", "canonicalSlug": "cyberpunk"},
    "fallout4": {"publicName": "Fallout 4", "canonicalSlug": "fallout"},
    "umbrella": {"publicName": "Umbrella", "canonicalSlug": "umbrella"},
    "factorio": {"publicName": "Factorio", "canonicalSlug": "factorio"},
    "bond007": {"publicName": "007 Intelligence", "canonicalSlug": "james-bond"},
    "hyrule": {"publicName": "Hyrule Command", "canonicalSlug": "hyrule"},
}

RAW_PATH_RE = re.compile(
    r"https://raw\.githubusercontent\.com/Conroy1988/missionchief-toolkit-assets/main/"
    r"(?P<path>[^'\"\s)<>]+)"
)
THEME_ENTRY_RE = re.compile(
    r"^\s*(?P<runtime>[A-Za-z_$][\w$]*):\s*Object\.freeze\(\{\s*"
    r"label:\s*'(?P<label>[^']+)',\s*"
    r"short:\s*'(?P<short>[^']+)',\s*"
    r"icon:\s*'(?P<icon>[^']+)',\s*"
    r"description:\s*'(?P<description>[^']*)'\s*\}\),?\s*$",
    re.MULTILINE,
)


def source_line(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def main() -> None:
    if not SOURCE_PATH.is_file() or not INVENTORY_PATH.is_file() or not DOC_PATH.is_file():
        raise RuntimeError("Phase 1 source or outputs are missing")

    source = SOURCE_PATH.read_text(encoding="utf-8", errors="replace")
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    block_match = re.search(
        r"const UI_THEMES = Object\.freeze\(\{(?P<body>.*?)\n\s*\}\);\s*\n\s*"
        r"const UI_THEME_ORDER = Object\.freeze\(\[(?P<order>[^\]]+)\]\);",
        source,
        re.DOTALL,
    )
    if not block_match:
        raise RuntimeError("UI_THEMES definition could not be parsed")

    entries = {}
    body_offset = block_match.start("body")
    for match in THEME_ENTRY_RE.finditer(block_match.group("body")):
        runtime = match.group("runtime")
        if runtime not in CANONICAL:
            continue
        entries[runtime] = {
            "runtimeId": runtime,
            "runtimeLabel": match.group("label"),
            "runtimeShortLabel": match.group("short"),
            "runtimeDescription": match.group("description"),
            "definitionLine": source_line(source, body_offset + match.start()),
        }

    order = re.findall(r"['\"]([A-Za-z_$][\w$]*)['\"]", block_match.group("order"))
    expected_order = list(CANONICAL)
    if order != expected_order:
        raise RuntimeError(f"Unexpected UI theme order: {order}; expected {expected_order}")
    if set(entries) != set(CANONICAL):
        raise RuntimeError(f"Parsed runtime identities do not match expected systems: {sorted(entries)}")

    existing_by_slug = {
        item["slug"]: item for item in inventory.get("existingThemeDirectories", [])
    }
    corrected_systems = []
    for position, runtime in enumerate(order, start=1):
        config = CANONICAL[runtime]
        entry = entries[runtime]
        slug = config["canonicalSlug"]
        corrected_systems.append(
            {
                "order": position,
                "publicName": config["publicName"],
                "runtimeId": runtime,
                "runtimeLabel": entry["runtimeLabel"],
                "runtimeShortLabel": entry["runtimeShortLabel"],
                "runtimeDescription": entry["runtimeDescription"],
                "canonicalSlug": slug,
                "canonicalDirectory": f"themes/{slug}",
                "directoryExists": slug in existing_by_slug,
                "sourceEvidence": {
                    "definitionLine": entry["definitionLine"],
                    "runtimeIdQuotedOccurrences": len(re.findall(rf"(?P<q>['\"])" + re.escape(runtime) + r"(?P=q)", source)),
                    "runtimeLabelOccurrences": source.count(entry["runtimeLabel"]),
                },
            }
        )

    raw_paths = sorted({match.group("path").rstrip(".,;:") for match in RAW_PATH_RE.finditer(source)})
    theme_paths = [path for path in raw_paths if path.startswith("themes/")]
    shared_paths = [path for path in raw_paths if path.startswith("assets/")]
    legacy_root_audio = [
        path for path in raw_paths
        if "/" not in path and Path(path).suffix.lower() in {".mp3", ".wav", ".ogg"}
    ]
    other_paths = [
        path for path in raw_paths
        if path not in theme_paths and path not in shared_paths and path not in legacy_root_audio
    ]

    inventory["themeSystems"] = corrected_systems
    inventory["canonicalSlugDecision"] = {
        item["publicName"]: item["canonicalSlug"] for item in corrected_systems
    }
    inventory["missingCanonicalThemeDirectories"] = sorted(
        item["canonicalDirectory"] for item in corrected_systems if not item["directoryExists"]
    )
    inventory["currentSourceAssetReferences"] = {
        "rawRepositoryPaths": raw_paths,
        "themePaths": theme_paths,
        "sharedAssetPaths": shared_paths,
        "legacyRootAudioPaths": legacy_root_audio,
        "otherRepositoryPaths": other_paths,
    }
    inventory["sourceIdentityDefinition"] = {
        "definitionStartLine": source_line(source, block_match.start()),
        "definitionEndLine": source_line(source, block_match.end()),
        "runtimeOrder": order,
    }
    inventory["namingNotes"] = [
        {
            "subject": "Runtime IDs versus asset slugs",
            "decision": "Do not rename persisted runtime IDs. Use separate kebab-case canonical asset slugs for repository folders.",
        },
        {
            "subject": "007 Intelligence",
            "decision": "Retain runtime ID bond007 and canonical folder slug james-bond while keeping 007 Intelligence as the public display name.",
        },
        {
            "subject": "Umbrella",
            "decision": "The public system name remains Umbrella; the current runtime selector label is Umbrella Containment.",
        },
        {
            "subject": "Non-theme payout presets",
            "decision": "Bad Company, Vice City and Scarface belong under assets/audio/payout-presets, not under themes/.",
        },
        {
            "subject": "Legacy root audio",
            "decision": "All seven public root paths remain indefinitely as compatibility aliases after the current Toolkit migrates.",
        },
        {
            "subject": "Hyrule flagship wording",
            "decision": "The runtime description currently says Flagship fantasy command interface. Remove Flagship during the migration so all seven systems remain equally represented.",
        },
    ]

    INVENTORY_PATH.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    theme_rows = []
    for item in corrected_systems:
        state = "Present" if item["directoryExists"] else "Create in migration"
        theme_rows.append(
            f"| {item['order']} | {item['publicName']} | `{item['runtimeId']}` | {item['runtimeLabel']} | "
            f"`{item['canonicalDirectory']}` | {state} |"
        )

    existing_rows = [
        f"| `{item['path']}` | {item['fileCount']} | {item['mediaCount']} |"
        for item in inventory["existingThemeDirectories"]
    ] or ["| _None_ | 0 | 0 |"]

    migration_rows = []
    for item in inventory["canonicalAudioMigration"]:
        owner = "Interface system" if item["classification"] == "theme-owned" else "Shared payout preset"
        migration_rows.append(
            f"| `{item['legacyPath']}` | `{item['canonicalPath']}` | {owner} | Retain root alias |"
        )

    version = inventory["currentVersion"]
    doc = f"""# Theme and shared-asset architecture

> Phase 1 inventory for [Issue #117](https://github.com/Conroy1988/missionchief-toolkit-assets/issues/117). Generated from Toolkit **v{version}** on 17 July 2026.

## Safety status

This change is **inventory only**. No media file was copied, moved, renamed or removed, and no Toolkit runtime or distribution file was changed.

## Identity model

Runtime IDs are persisted application values and must not be renamed. Canonical asset slugs are separate repository paths chosen for consistency.

| Order | Interface system | Runtime ID | Current runtime label | Canonical folder | Current state |
|---:|---|---|---|---|---|
{chr(10).join(theme_rows)}

### Existing `themes/` directories

| Directory | Files | Media files |
|---|---:|---:|
{chr(10).join(existing_rows)}

The complete file-level inventory, hashes and exact source references are recorded in [`status/theme-asset-inventory.json`](../status/theme-asset-inventory.json).

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

## Confirmed naming decisions

- Runtime IDs remain `mapCommand`, `cyberpunk`, `fallout4`, `umbrella`, `factorio`, `bond007` and `hyrule`.
- Canonical asset slugs are `map-command`, `cyberpunk`, `fallout`, `umbrella`, `factorio`, `james-bond` and `hyrule`.
- **007 Intelligence** keeps runtime ID `bond007` and folder slug `james-bond`.
- **Umbrella** is the public system name; **Umbrella Containment** is its current runtime selector label.
- **Bad Company**, **Vice City** and **Scarface** are payout presentation presets, not Toolkit interface systems.
- **Map Command** receives a canonical folder even when it currently has no external media, keeping all seven systems structurally equal.

> [!WARNING]
> The Hyrule runtime description still says **“Flagship fantasy command interface.”** The migration must remove “Flagship” so no interface system is elevated above the others.

## Phase 2 entry gates

The inventory now confirms:

- three existing theme directories: `hyrule`, `james-bond` and `umbrella`;
- four canonical theme directories to create: `map-command`, `cyberpunk`, `fallout` and `factorio`;
- the seven runtime identities and separate canonical asset slugs;
- all current raw-repository asset paths without substring false positives;
- the complete root-to-canonical audio mapping;
- preservation of all seven public root URLs.

The migration must use a separate reviewed pull request and a normal Toolkit version/release cycle.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")

    if EVIDENCE_PATH.exists():
        EVIDENCE_PATH.unlink()

    print("Corrected runtime identities, raw repository paths and architecture documentation")
    print("Removed temporary source-context evidence file")
    print("No media or runtime files changed")


if __name__ == "__main__":
    main()
