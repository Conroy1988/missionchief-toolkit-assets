# Theme and shared-asset architecture

> Implemented by [Issue #117](https://github.com/Conroy1988/missionchief-toolkit-assets/issues/117) for Toolkit **v4.14.7**.

## Identity model

Runtime IDs are persisted application values and remain unchanged. Canonical asset slugs are separate repository paths.

| Order | Interface system | Runtime ID | Canonical folder |
|---:|---|---|---|
| 1 | Map Command | `mapCommand` | `themes/map-command` |
| 2 | Cyberpunk | `cyberpunk` | `themes/cyberpunk` |
| 3 | Fallout 4 | `fallout4` | `themes/fallout` |
| 4 | Umbrella | `umbrella` | `themes/umbrella` |
| 5 | Factorio | `factorio` | `themes/factorio` |
| 6 | 007 Intelligence | `bond007` | `themes/james-bond` |
| 7 | Hyrule Command | `hyrule` | `themes/hyrule` |

All seven interface systems have a canonical namespace. No system is designated as flagship.

## Canonical audio ownership

| Canonical active path | Ownership |
|---|---|
| `themes/cyberpunk/audio/cyberpunk-cashout.mp3` | Cyberpunk |
| `themes/fallout/audio/fallout-cashout.mp3` | Fallout 4 |
| `themes/umbrella/audio/umbrella-containment-cashout.mp3` | Umbrella |
| `themes/factorio/audio/factorio-cashout.mp3` | Factorio |
| `themes/james-bond/audio/james-bond-cashout.mp3` | 007 Intelligence |
| `themes/hyrule/audio/hyrule-quest-reward.mp3` | Hyrule Command |
| `assets/audio/payout-presets/bf-bad-company-cashout.mp3` | Bad Company payout preset |
| `assets/audio/payout-presets/gta-vice-city-cashout.mp3` | Vice City payout preset |
| `assets/audio/payout-presets/scarface-cashout.mp3` | Scarface payout preset |

Map Command currently has no hosted audio but retains its canonical theme namespace.

## Canonical-only audio policy

The repository supports only the structured canonical paths listed above. Historical root-level MP3 copies were removed by Issue #120 after the support policy changed to require users to update to the current Toolkit release.

The canonical audio inventory remains machine-validated. Root-level audio, missing canonical files, source references outside the inventory, orphaned media and duplicate payloads are rejected.

## Development rules

- Add interface-owned assets beneath the matching `themes/<slug>/` package.
- Add cross-theme payout presentation assets beneath `assets/audio/payout-presets/`.
- Reference only canonical structured paths from current source code.
- Never rename persisted runtime IDs as part of repository organisation.
- Update the canonical audio inventory and deterministic tests whenever audio assets change.
