# Theme and shared-asset architecture

> Phase 1 inventory for [Issue #117](https://github.com/Conroy1988/missionchief-toolkit-assets/issues/117). Generated from Toolkit **v4.14.6** on 17 July 2026.

## Safety status

This change is **inventory only**. No media file was copied, moved, renamed or removed, and no Toolkit runtime or distribution file was changed.

## Canonical interface-system folders

The seven interface systems remain equal. Folder slugs follow stable internal identities; public presentation names remain unchanged.

| Order | Interface system | Internal ID | Canonical folder | Current state | Source evidence |
|---:|---|---|---|---|---:|
| 1 | Map Command | `map-command` | `themes/map-command` | Create in migration | ID: 0; name: 10 |
| 2 | Cyberpunk | `cyberpunk` | `themes/cyberpunk` | Create in migration | ID: 251; name: 10 |
| 3 | Fallout 4 | `fallout` | `themes/fallout` | Create in migration | ID: 0; name: 4 |
| 4 | Umbrella | `umbrella` | `themes/umbrella` | Present | ID: 444; name: 36 |
| 5 | Factorio | `factorio` | `themes/factorio` | Create in migration | ID: 224; name: 15 |
| 6 | 007 Intelligence | `james-bond` | `themes/james-bond` | Present | ID: 0; name: 6 |
| 7 | Hyrule Command | `hyrule` | `themes/hyrule` | Present | ID: 108; name: 3 |

### Existing `themes/` directories

| Directory | Files | Media files |
|---|---:|---:|
| `themes/hyrule` | 8 | 8 |
| `themes/james-bond` | 9 | 8 |
| `themes/umbrella` | 9 | 7 |

The complete file-level inventory, hashes and references are recorded in [`status/theme-asset-inventory.json`](../status/theme-asset-inventory.json).

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
