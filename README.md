<div align="center">

<img src="docs/media/readme-hero.svg" alt="MissionChief Map Command Toolkit operational command suite" width="100%">

# MissionChief Map Command Toolkit

### Turn the MissionChief map into a live operations console.

Mission intelligence · Fleet awareness · Geographic coverage · Financial command · Responsive layouts · Seven complete interface systems

[![Install from Greasy Fork](https://img.shields.io/badge/INSTALL%20NOW-GREASY%20FORK-8B0000?style=for-the-badge&logo=tampermonkey&logoColor=white)](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)
[![Open documentation](https://img.shields.io/badge/OPEN-DOCUMENTATION-1677A3?style=for-the-badge&logo=readthedocs&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/)
[![Explore themes](https://img.shields.io/badge/EXPLORE-7%20INTERFACE%20SYSTEMS-6D28D9?style=for-the-badge&logo=palette&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)

[![GitHub release](https://img.shields.io/github/v/release/Conroy1988/missionchief-toolkit-assets?display_name=release&label=release&color=2563eb)](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest)
[![Greasy Fork version](https://img.shields.io/greasyfork/v/586018?label=Greasy%20Fork&color=670000)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Total installs](https://img.shields.io/greasyfork/dt/586018?label=installs&color=0f766e)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![GitHub stars](https://img.shields.io/github/stars/Conroy1988/missionchief-toolkit-assets?style=flat&color=ca8a04)](https://github.com/Conroy1988/missionchief-toolkit-assets/stargazers)
[![Canonical validation](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml/badge.svg)](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml)
[![Full audit](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/full-userscript-audit.yml/badge.svg)](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/full-userscript-audit.yml)
[![Licence](https://img.shields.io/badge/licence-MIT-111827)](#licence-and-attribution)

[Why it exists](#why-it-exists) · [Install](#install-in-under-a-minute) · [Systems](#operational-systems) · [Themes](#seven-interface-systems) · [Devices](#built-for-every-screen) · [Release confidence](#release-confidence) · [Support](#support-and-roadmap)

</div>

---

## Why it exists

MissionChief can generate an enormous amount of operational information, but the standard interface spreads that information across map markers, mission windows, vehicle lists, finance pages and separate controls.

**MissionChief Map Command Toolkit brings those signals back into one command layer.** It helps you identify what needs attention, understand the state of your fleet, assess coverage, track mission value and move between incidents without losing the map.

<table>
<tr>
<td width="25%" align="center"><strong>🚨 Triage faster</strong><br><sub>Surface old, critical, blocked and transport-dependent missions immediately.</sub></td>
<td width="25%" align="center"><strong>🚓 Read the fleet</strong><br><sub>See response codes, availability, hidden batches and unit demand in context.</sub></td>
<td width="25%" align="center"><strong>🗺️ Understand coverage</strong><br><sub>Use heat maps, rings, labels, bookmarks and focused map states.</sub></td>
<td width="25%" align="center"><strong>📊 Track the operation</strong><br><sub>Monitor mission value, income, spending, payouts and session performance.</sub></td>
</tr>
</table>

> [!TIP]
> Every major system can be enabled independently. Use the complete command suite, or keep only the controls that improve your own account and device.

## Install in under a minute

1. Install a userscript manager such as **Tampermonkey**.
2. Open the verified installer:

   **[Install MissionChief Map Command Toolkit](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)**

3. Confirm the userscript installation.
4. Reload MissionChief.
5. Click the Toolkit command button on the map.

> [!NOTE]
> **Greasy Fork is the supported public installation and automatic-update channel.** GitHub remains the canonical source, validation authority and immutable release archive.

| Need | Open |
|---|---|
| Install or update | [Greasy Fork installer](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js) |
| Read the guide | [Documentation site](https://conroy1988.github.io/missionchief-toolkit-assets/) |
| Check the latest release | [GitHub Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest) |
| Review version history | [Changelog](CHANGELOG.md) |

## Operational systems

### Mission command

| Capability | What it changes |
|---|---|
| **Mission Age Watch** | Sorts and surfaces personal missions by age, urgency, assistance state and clearing progress. |
| **Critical View** | Creates a concentrated workflow for missions that need immediate action. |
| **Mission Value** | Displays a correctly formatted mission value inside opened mission windows, with dynamic clearance from native controls. |
| **Mission Inspector** | Opens deeper mission context only when requested, avoiding unnecessary startup work. |
| **Major Incident Feed** | Places high-priority incidents in a live command feed with click-to-zoom navigation. |
| **Transport Watcher** | Identifies missions that still require patient transport and shows current demand. |

### Fleet and map intelligence

| Capability | What it changes |
|---|---|
| **Vehicle Code Status** | Summarises the live fleet by response code, description and count. |
| **Auto-load all vehicles** | Activates MissionChief's native hidden-vehicle batch control when enabled. |
| **Coverage Heat Map** | Visualises operational coverage directly on the Leaflet map. |
| **Coverage rings** | Adds readable geographic range context around operational locations. |
| **Smart Bookmark Labels** | Produces compact place labels with manual overrides and touch previews. |
| **Visibility command layer** | Controls personal missions, alliance missions, vehicles and buildings without leaving the map. |

### Finance, payouts and presentation

| Capability | What it changes |
|---|---|
| **Alliance Credits** | Adds compact mission values, eligibility-aware colouring and value filters. |
| **Financial intelligence** | Summarises income, spending and net position with Discord-ready reporting. |
| **Payout presentations** | Adds configurable cinematic completion sequences without changing mission logic. |
| **Session performance** | Tracks earned credits, completions, largest payout, aged missions and payout events. |
| **Settings import/export** | Moves the complete Toolkit configuration between devices. |
| **Economy Mode** | Suppresses non-essential animation and presentation overhead. |

<details>
<summary><strong>View the complete capability inventory</strong></summary>

#### Mission workflow

- Personal and alliance mission visibility controls
- Mission Age Watch with progress synchronisation
- Critical mission workflow and clearing-state tracking
- Patient and transport monitoring
- Mission Inspector and rapid map navigation
- Major Incident Feed with location and incident context
- Mission Value inside opened mission windows
- Alliance payout overlays and completion history

#### Fleet workflow

- Vehicle Code Status panel and keyboard shortcut
- Transport demand counts
- Unit-count overlays
- Focus Mode and visibility controls
- Automatic loading of MissionChief's limited vehicle-list batches
- Rapid navigation to active units and incidents

#### Map workflow

- Coverage heat maps and coverage rings
- Landmark bookmarks and quick jumps
- Smart short labels with long-press previews on touch devices
- Day, night and themed map presentation
- Alliance Buildings map suppression for performance-sensitive pages
- Desktop, tablet and iOS-safe placement

#### Financial and presentation workflow

- Daily, weekly and monthly financial summaries
- Alliance value filters and eligibility states
- Smooth mission-payout counters
- Configurable completion duration and emergency flash
- Hosted audio and transparent visual assets
- Persistent completion history
- Discord-ready operational reports

</details>

## Seven interface systems

The Toolkit includes seven complete visual systems. **Map Command is the original identity, not a flagship theme.** Every system exposes the same operational controls, responsive layouts and saved settings.

<div align="center">

[![Map Command](https://img.shields.io/badge/MAP%20COMMAND-0E7490?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Cyberpunk](https://img.shields.io/badge/CYBERPUNK-D500F9?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Fallout 4](https://img.shields.io/badge/FALLOUT%204-4D7C0F?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Umbrella](https://img.shields.io/badge/UMBRELLA-B91C1C?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Factorio](https://img.shields.io/badge/FACTORIO-B45309?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![007 Intelligence](https://img.shields.io/badge/007%20INTELLIGENCE-B59A55?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Hyrule Command](https://img.shields.io/badge/HYRULE%20COMMAND-0F766E?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)

</div>

| Interface system | Command language |
|---|---|
| **Map Command** | Clean cyan telemetry, restrained contrast and map-first readability. |
| **Cyberpunk** | Neon cyan, warning yellow, magenta accents and angular high-density telemetry. |
| **Fallout 4** | Green phosphor readouts, aged terminal surfaces and industrial survival-interface styling. |
| **Umbrella** | Clinical black, white and red with containment alerts and corporate-control discipline. |
| **Factorio** | Industrial machinery, amber controls, production-line logic and mechanical status systems. |
| **007 Intelligence** | Classified dossiers, restrained black surfaces and champagne-gold controls. |
| **Hyrule Command** | Royal gold, parchment cartography, ancient-blue illumination and luminous green energy. |

Interface themes and payout presentations are selected independently. Inactive themes do not load their hosted media or run theme-specific animation logic, while Economy Mode and reduced-motion preferences suppress non-essential effects.

<details>
<summary><strong>Theme and third-party attribution</strong></summary>

The optional interface systems reference visual languages associated with **Cyberpunk 2077**, **Fallout**, **Resident Evil / Umbrella**, **Factorio**, **James Bond / 007** and **The Legend of Zelda**. Those names and properties remain trademarks and copyrighted material of their respective owners. Their inclusion does not imply sponsorship, affiliation or endorsement. MissionChief Map Command Toolkit is an independent community userscript and does not redistribute those games or their media.

</details>

## Built for every screen

| Mode | Designed for | Behaviour |
|---|---|---|
| **Desktop** | Full browser layouts and large displays | Complete command panels, fixed command chrome, internal section scrolling and keyboard control. |
| **Tablet** | Landscape tablet layouts | Space-aware controls without forcing the Desktop structure into a smaller viewport. |
| **iOS Mobile** | Safari with a compatible userscript manager | Touch-safe controls, compact panels and long-press bookmark previews. |
| **Economy Mode** | Performance-sensitive devices or sessions | Static presentation, reduced animation and lower visual overhead. |

The same persisted settings schema is used across modes. Import/export tools provide a portable configuration backup, while each device mode retains its own layout behaviour.

## Keyboard command layer

| Key | Action |
|---:|---|
| `1` | Toggle My Missions |
| `2` | Toggle Alliance Missions |
| `3` | Toggle Vehicles |
| `4` | Toggle My Buildings |
| `5` | Toggle Alliance Credits |
| `6` | Toggle Mission Age Watch |
| `V` | Open or close Vehicle Code Status |

Shortcuts are ignored while typing into form controls.

## Release confidence

The public userscript is not copied manually between services. Every formal version is built from the canonical source and moves through validation, audit, distribution and live verification before it is recorded as released.

<table>
<tr>
<td width="25%" align="center"><strong>1 · Validate</strong><br><sub>Syntax, contracts, integrity, performance and source parity.</sub></td>
<td width="25%" align="center"><strong>2 · Publish</strong><br><sub>Immutable GitHub Release and Greasy Fork distribution.</sub></td>
<td width="25%" align="center"><strong>3 · Verify</strong><br><sub>Live public version, private recovery backup and asset state.</sub></td>
<td width="25%" align="center"><strong>4 · Announce</strong><br><sub>Discord release publication and dashboard reconciliation.</sub></td>
</tr>
</table>

| Release record | Open |
|---|---|
| Human-readable status | [`status/README.md`](status/README.md) |
| Machine-readable dashboard | [`status/release-dashboard.json`](status/release-dashboard.json) |
| Latest immutable release | [GitHub Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest) |
| Public update channel | [Greasy Fork](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit) |

<details>
<summary><strong>View the guarded release path</strong></summary>

```text
Focused branch
      ↓
Pull request validation
      ↓
Canonical source and distribution parity
      ↓
Integrity, performance and full userscript audit
      ↓
Reviewed merge to main
      ↓
/release-toolkit X.Y.Z RELEASE
      ↓
Current-version readiness
      ↓
GitHub Release → Greasy Fork → live verification
      ↓
Private backup → Discord announcement → dashboard reconciliation
```

A release announcement is sent only after the public Greasy Fork version and private recovery backup have both been verified.

</details>

## Support and roadmap

| Route | Use it for |
|---|---|
| [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) | Installation, configuration and feature guidance. |
| [Help and troubleshooting](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/help-and-troubleshooting) | Usage questions and setup problems. |
| [Feature ideas](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/feature-ideas) | Early proposals and community discussion. |
| [Show and tell](https://github.com/Conroy1988/missionchief-toolkit-assets/discussions/categories/show-and-tell) | Layouts, themes and operational setups. |
| [GitHub Issues](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) | Confirmed bugs, regressions and actionable specifications. |
| [Public roadmap](https://github.com/users/Conroy1988/projects) | Current investigation, development and release state. |

## Contributing

Focused, evidence-backed contributions are welcome. Start with the repository guidance before proposing a change:

- [Contributing guide](CONTRIBUTING.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- [Security policy](SECURITY.md)
- [Canonical changelog](CHANGELOG.md)

<details>
<summary><strong>Repository map and engineering principles</strong></summary>

```text
src/                Canonical userscript source
dist/               Byte-identical validated distribution
themes/             Stable theme-specific visual and audio assets
docs/               Documentation, media and GitHub Pages source
status/             Human-readable and machine-readable release state
.github/scripts/    Validation, audit, build and release tooling
.github/workflows/  Permanent automation only
```

Engineering principles:

- **Behaviour before cleanup:** code is removed only when call-path and state-effect evidence prove it is dead.
- **Stable settings:** existing localStorage keys and import/export data remain compatible.
- **Stable assets:** public image and audio paths are not renamed or removed without a migration route.
- **Targeted automation:** workflows run only when their inputs or protected responsibilities change.
- **No premature releases:** GitHub, Greasy Fork, private backup and Discord records must agree.
- **Recoverability:** formal releases include checksums, manifests and an immutable archive.

</details>

## Licence and attribution

MissionChief Map Command Toolkit is maintained by **Conroy1988** and distributed under the [MIT licence](LICENSE).

MissionChief trademarks, game content and all referenced third-party franchises and material remain the property of their respective owners. This is an independent community userscript and is not an official MissionChief product.

---

<div align="center">

<strong>MissionChief Map Command Toolkit</strong><br>
<sub>One map. Every operational layer.</sub>

[Install](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js) · [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) · [Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest) · [Roadmap](https://github.com/users/Conroy1988/projects)

</div>
