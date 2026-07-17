# Theme and shared-asset architecture

> Phase 1 inventory for [Issue #117](https://github.com/Conroy1988/missionchief-toolkit-assets/issues/117). Generated from Toolkit **v4.14.6** on 17 July 2026.

## Safety status

This change is **inventory only**. No media file was copied, moved, renamed or removed, and no Toolkit runtime or distribution file was changed.

## Identity model

Runtime IDs are persisted application values and must not be renamed. Canonical asset slugs are separate repository paths chosen for consistency.

| Order | Interface system | Runtime ID | Current runtime label | Canonical folder | Current state |
|---:|---|---|---|---|---|
| 1 | Map Command | `mapCommand` | Map Command | `themes/map-command` | Create in migration |
| 2 | Cyberpunk | `cyberpunk` | Cyberpunk | `themes/cyberpunk` | Create in migration |
| 3 | Fallout 4 | `fallout4` | Fallout 4 | `themes/fallout` | Create in migration |
| 4 | Umbrella | `umbrella` | Umbrella Containment | `themes/umbrella` | Present |
| 5 | Factorio | `factorio` | Factorio | `themes/factorio` | Create in migration |
| 6 | 007 Intelligence | `bond007` | 007 Intelligence | `themes/james-bond` | Present |
| 7 | Hyrule Command | `hyrule` | Hyrule Command | `themes/hyrule` | Present |

### Existing `themes/` directories

| Directory | Files | Media files |
|---|---:|---:|
| `themes/hyrule` | 8 | 8 |
| `themes/james-bond` | 9 | 8 |
| `themes/umbrella` | 9 | 7 |

The complete file-level inventory, hashes and exact source references are recorded in [`status/theme-asset-inventory.json`](../status/theme-asset-inventory.json).

## Audio ownership and canonical migration

| Existing public path | Canonical active path | Ownership | Compatibility treatment |
|---|---|---|---|
| `cyberpunk-cashout.mp3` | `themes/cyberpunk/audio/cyberpunk-cashout.mp3` | Interface system | Retain root alias |
| `fallout-cashout.mp3` | `themes/fallout/audio/fallout-cashout.mp3` | Interface system | Retain root alias |
| `factorio-cashout.mp3` | `themes/factorio/audio/factorio-cashout.mp3` | Interface system | Retain root alias |
| `james-bond-cashout.mp3` | `themes/james-bond/audio/james-bond-cashout.mp3` | Interface system | Retain root alias |
| `bf-bad-company-cashout.mp3` | `assets/audio/payout-presets/bf-bad-company-cashout.mp3` | Shared payout preset | Retain root alias |
| `gta-vice-city-cashout.mp3` | `assets/audio/payout-presets/gta-vice-city-cashout.mp3` | Shared payout preset | Retain root alias |
| `scarface-cashout.mp3` | `assets/audio/payout-presets/scarface-cashout.mp3` | Shared payout preset | Retain root alias |

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

## Phase 1 review conclusion

The inventory is approved as the migration baseline. It confirms a strict separation between persisted runtime IDs and repository asset slugs, and it establishes the root-to-canonical mapping without changing any public endpoint.

Phase 1 does **not** complete Issue #117. The issue remains open until structured copies, the compatibility alias manifest, Asset Health enforcement, userscript migration and the production release are complete.

## Phase 2 entry gates

The inventory now confirms:

- three existing theme directories: `hyrule`, `james-bond` and `umbrella`;
- four canonical theme directories to create: `map-command`, `cyberpunk`, `fallout` and `factorio`;
- the seven runtime identities and separate canonical asset slugs;
- all current raw-repository asset paths without substring false positives;
- the complete root-to-canonical audio mapping;
- preservation of all seven public root URLs.

The migration must use a separate reviewed pull request and a normal Toolkit version/release cycle.
