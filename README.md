<div align="center">

<img src="docs/media/readme-hero.svg" alt="MissionChief Map Command Toolkit operational command suite" width="100%">

# MissionChief Map Command Toolkit

### Turn the MissionChief map into a live operations console

**Mission intelligence · Specialist fleet identity · Geographic coverage · Financial command · Responsive layouts · Seven complete interface systems**

[![Install from Greasy Fork](https://img.shields.io/badge/INSTALL_NOW-GREASY_FORK-8B0000?style=for-the-badge&logo=tampermonkey&logoColor=white)](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)
[![Open documentation](https://img.shields.io/badge/OPEN-DOCUMENTATION-1677A3?style=for-the-badge&logo=readthedocs&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/)
[![Explore themes](https://img.shields.io/badge/EXPLORE-7_INTERFACE_SYSTEMS-6D28D9?style=for-the-badge&logo=palette&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)

**Current verified release:** `v4.20.27`

[![GitHub release](https://img.shields.io/github/v/release/Conroy1988/missionchief-toolkit-assets?display_name=release&label=release&color=2563eb)](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest)
[![Greasy Fork version](https://img.shields.io/greasyfork/v/586018?label=Greasy%20Fork&color=670000)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Total installs](https://img.shields.io/greasyfork/dt/586018?label=installs&color=0f766e)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![GitHub stars](https://img.shields.io/github/stars/Conroy1988/missionchief-toolkit-assets?style=flat&color=ca8a04)](https://github.com/Conroy1988/missionchief-toolkit-assets/stargazers)
[![Canonical validation](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml/badge.svg)](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml)
[![Full audit](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/full-userscript-audit.yml/badge.svg)](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/full-userscript-audit.yml)
[![Licence](https://img.shields.io/badge/licence-MIT-111827)](#licence-and-attribution)

[**Why it exists**](#why-it-exists) · [**Install**](#install-in-under-a-minute) · [**v4.20.27**](#current-v42027-release) · [**Systems**](#operational-systems) · [**Themes**](#seven-interface-systems) · [**Devices**](#built-for-every-screen) · [**Release confidence**](#release-confidence) · [**Support**](#support-and-development)

</div>

---

## Why it exists

MissionChief produces a large amount of operational information, but the standard interface distributes that information across map markers, mission windows, vehicle tables, finance pages, transport controls, and separate navigation surfaces.

**MissionChief Map Command Toolkit brings those signals into one configurable command layer.** It helps the player identify what needs attention, understand fleet capability, reconcile current mission demand, assess geographic coverage, track financial performance, and move between incidents without losing operational context.

<table>
<tr>
<td width="25%" align="center"><strong>🚨 TRIAGE</strong><br><sub>Surface old, critical, blocked, and transport-dependent missions.</sub></td>
<td width="25%" align="center"><strong>🚓 IDENTIFY</strong><br><sub>Expose specialist fleet roles and live response state.</sub></td>
<td width="25%" align="center"><strong>🗺️ COMMAND</strong><br><sub>Use heat maps, rings, bookmarks, focus modes, and visibility controls.</sub></td>
<td width="25%" align="center"><strong>📊 RECONCILE</strong><br><sub>Track mission value, income, spending, net movement, and performance.</sub></td>
</tr>
</table>

Every major module can be enabled independently. Use the complete suite or retain only the systems that improve your account, workflow, and device.

## Install in under a minute

1. Install a userscript manager such as **Tampermonkey**.
2. Open the verified public installer:

   **[Install MissionChief Map Command Toolkit](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)**

3. Confirm installation.
4. Reload MissionChief.
5. Open the Toolkit command button on the map.

> [!NOTE]
> **Greasy Fork is the supported public installation and automatic-update channel.** GitHub remains the canonical development source, validation authority, documentation host, and immutable release archive.

| Need | Open |
|---|---|
| Install or update | [Greasy Fork installer](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js) |
| Read the guide | [Documentation site](https://conroy1988.github.io/missionchief-toolkit-assets/) |
| Check the latest release | [GitHub Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest) |
| Review version history | [CHANGELOG.md](CHANGELOG.md) |
| Report a confirmed problem | [Issue tracker](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) |

## Current v4.20.27 release

### Map and visibility lifecycle hardening

Version `4.20.27` extracts the nine map and visibility state routes from the main `toggleFeature()` dispatcher into the independently tested `handleMapVisibilityToggle()` helper:

- marker focus;
- mission pulse;
- road priority;
- coverage;
- heat map;
- alliance missions;
- personal missions;
- vehicles; and
- buildings.

Vehicle and building layer synchronisation now runs through `applyMapVisibilityToggleEffects()` at the same post-render position as before, including Economy Mode resynchronisation. Direct and delegated fixture coverage verifies route inventory, unknown-route safety, saved-state parity, and the exact **update → layer synchronisation → Economy Mode → reconciliation** order.

> [!IMPORTANT]
> This is an internal reliability release. Map presentation, mission visibility, overlays, Desktop/Tablet/iOS layouts, setting names, themes, payout presentation, and public assets are intentionally unchanged.

### Settings routing retained from v4.20.26

The current production line also retains the `v4.20.26` extraction of fourteen Discord financial-report and Local Financial Archive setting routes into `handleDiscordFinancialSettingChange()`.

The contract preserves:

- all existing setting names and normalisation rules;
- persistence and preview invalidation;
- asynchronous feed refresh behaviour;
- all 36 rendered settings;
- intentional no-op handling;
- source/distribution parity; and
- the permanent 500-line source-headroom margin.

### Boot lifecycle and performance evidence

The seven recurring Boot maintenance registrations remain isolated in `registerBootMaintenanceTasks()` while `boot()` retains initialization-order ownership. Callback logic, intervals, Economy Mode scheduling, observer/listener coverage, teardown behaviour, and distribution parity remain fixture-backed.

The repository also carries measurement-only tooling for unchanged-render analysis: an instrumented profiler, deterministic scenarios, a render-probe generator, evidence documentation, and a dedicated evidence workflow. These tools do not modify production runtime behaviour.

### Financial Advisor reconciliation

Detailed Financial Advisor transactions remain anchored against MissionChief's `/credits/overview` Revenue, Spendings, and Sum checkpoints without adding aggregate values on top of the ledger.

The system:

- paginates through bounded historical overview coverage;
- preserves detailed transaction categories;
- exposes unexplained income, spending, and net variance instead of inventing categories;
- applies overview-confirmed totals only to complete covered days;
- retains detailed-ledger totals for partial days;
- shares one canonical model with the dashboard, Discord reports, and generated Financial Command graphics; and
- degrades safely when the overview is unavailable, malformed, duplicated, or outside the requested range.

Deterministic contracts cover parsing, sign handling, pagination, bounded caching, duplicate dates, exact matches, variance, negative net movement, partial periods, safe failure, and no-double-counting behaviour.

### Release communication

Release delivery produces a compact deployment transmission containing the current changelog summary, Install / Update, release notes, Greasy Fork, integrity posture, verification evidence, and fallback rendering. An owner-only preview path tests the real release embed without publishing a release or changing Greasy Fork.

## Specialist fleet intelligence

MissionChief can display the same base vehicle type for vehicles serving very different operational roles. **Custom Vehicle Badges restores that identity inside Available Units.**

<div align="center">

### `IRV` · `[Railway Police Officer]`

<sub>Native vehicle type retained. Own Vehicle Category exposed. Specialist intent visible.</sub>

</div>

- Own Vehicle Categories appear beside the native vehicle type rather than replacing it.
- Category-only vehicles remain visually distinct without changing selection or dispatch behaviour.
- Stable vehicle-ID classification supplies Mission Requirements and Resource Gap with safer specialist context.
- Badges are restored after MissionChief or LSSM filters, sorts, or replaces the vehicle list.
- Vehicles without an Own Vehicle Category remain untouched.

## Operational systems

### Mission command

| Capability | Operational purpose |
|---|---|
| **Mission Age Watch** | Surfaces personal and alliance missions by age, ownership, category, urgency, assistance state, and clearing progress |
| **Critical View** | Creates a concentrated workflow for missions requiring immediate attention |
| **Mission Value** | Displays formatted mission value inside opened mission windows |
| **Mission Requirements** | Reconciles required, on-site, responding, selected, and still-needed capacity in normal document flow |
| **Mission Inspector** | Loads deeper mission context only when requested |
| **Major Incident Feed** | Maintains a high-priority incident feed with click-to-zoom navigation |
| **Transport Watcher** | Identifies patient and prisoner transport demand |
| **Patient Transport Sweep** | Processes eligible alliance ambulances sequentially while excluding the signed-in player's own vehicles |
| **Resource Gap** | Compares demand with available personal vehicle context inside a selected radius |

### Fleet and map intelligence

| Capability | Operational purpose |
|---|---|
| **Vehicle Code Status** | Summarises the live fleet by response code, description, and count |
| **Custom Vehicle Badges** | Exposes Own Vehicle Categories beside native vehicle types |
| **Auto-load all vehicles** | Uses MissionChief's native hidden-vehicle batch control |
| **Coverage Heat Map** | Visualises geographic operational coverage |
| **Coverage rings** | Adds readable range context around locations |
| **Smart Bookmark Labels** | Creates compact place labels with overrides and touch previews |
| **Visibility command layer** | Controls personal missions, alliance missions, vehicles, and buildings without leaving the map |
| **Focus / compact modes** | Reduces map and interface noise for the active workflow |

### Financial command

| Capability | Operational purpose |
|---|---|
| **Alliance Credits** | Adds mission values, eligibility-aware states, and filters |
| **Financial Advisor** | Builds daily, weekly, monthly, and custom-period income/spending analysis |
| **Overview reconciliation** | Anchors complete days to MissionChief Revenue, Spendings, and Sum checkpoints |
| **Variance reporting** | Preserves unexplained differences without false classification |
| **Discord financial reports** | Sends the canonical reconciled model through configured webhook reporting |
| **Financial Command graphics** | Generates visual summaries from the same reconciled data model |
| **Session performance** | Tracks credits, completions, largest payout, aged missions, and payout events |

### Presentation and configuration

- Seven complete interface systems
- Independent payout-presentation selection
- Economy Mode
- Reduced-motion support
- Settings import/export
- Hosted transparent assets and optional audio
- Configurable completion duration and emergency flash
- Persistent completion history

> [!WARNING]
> Settings exports can include the saved Discord webhook. Treat exported settings as private operational material.

## Seven interface systems

Every interface system provides the same operational functionality and stored configuration. **Map Command is the original identity, not a privileged feature tier.**

<div align="center">

[![Map Command](https://img.shields.io/badge/MAP_COMMAND-0E7490?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Cyberpunk](https://img.shields.io/badge/CYBERPUNK-D500F9?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Fallout 4](https://img.shields.io/badge/FALLOUT_4-4D7C0F?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Umbrella](https://img.shields.io/badge/UMBRELLA-B91C1C?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Factorio](https://img.shields.io/badge/FACTORIO-B45309?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![007 Intelligence](https://img.shields.io/badge/007_INTELLIGENCE-B59A55?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Hyrule Command](https://img.shields.io/badge/HYRULE_COMMAND-0F766E?style=for-the-badge&labelColor=111827)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)

</div>

| Interface system | Visual command language |
|---|---|
| **Map Command** | Clean cyan telemetry, restrained contrast, and map-first readability |
| **Cyberpunk** | Neon cyan, warning yellow, magenta accents, and angular telemetry |
| **Fallout 4** | Green phosphor, aged terminals, and industrial survival interfaces |
| **Umbrella** | Clinical black, white, red, and containment-alert discipline |
| **Factorio** | Industrial machinery, amber controls, and production-line logic |
| **007 Intelligence** | Classified dossiers, restrained black surfaces, and champagne-gold controls |
| **Hyrule Command** | Royal gold, parchment cartography, ancient blue, and luminous green energy |

Inactive themes do not load their hosted media or run theme-specific effects. Economy Mode and reduced-motion preferences suppress non-essential presentation overhead.

## Built for every screen

| Mode | Designed behaviour |
|---|---|
| **Desktop** | Full command panels, fixed chrome, internal section scrolling, and keyboard control |
| **Ultrawide** | Expanded operational layouts without uncontrolled line length or detached controls |
| **Tablet** | Space-aware landscape layouts rather than compressed desktop panels |
| **iOS mobile** | Touch-safe controls, mobile sheet behaviour, and browser-specific placement protections |
| **Economy / reduced motion** | Functional command surface with non-essential effects removed |

Responsive behaviour is part of each feature contract, not a separate skin applied afterwards.

## Compatibility

The Toolkit is developed for MissionChief and is designed to coexist with supported companion tooling where explicit compatibility logic exists.

Current integration work includes:

- LSSM-aware mission and transport controls;
- patient demand and responding/on-site reconciliation;
- live Available Units replacement handling;
- custom category identity without overriding native vehicle types;
- bounded fallbacks where third-party controls are unavailable; and
- fail-closed behaviour where the page does not expose enough reliable evidence.

## Release confidence

The canonical userscript is:

```text
src/MissionChief_Map_Command_Toolkit.user.js
```

The release path is designed as a verified delivery chain:

```text
Issue-scoped development
        ↓
Source and regression tests
        ↓
Pull request review and CI
        ↓
Validated distribution candidate
        ↓
GitHub Release publication
        ↓
Asset checksum verification
        ↓
Greasy Fork parity verification
        ↓
Private recovery backup
        ↓
Discord release transmission
        ↓
Release-readiness and asset audit
```

### Validation surfaces

- Userscript syntax and metadata
- Source/dist/version consistency
- Repository and asset integrity
- Full userscript audit
- Theme manifests and hosted assets
- Release and Greasy Fork parity
- Private backup evidence
- Discord payload contracts and preview route
- Observer ownership and teardown inventory
- Boot lifecycle registration contract
- Discord financial and Local Archive setting-route contract
- Map and visibility route/effect ordering contract
- Controlled performance and unchanged-render measurement
- Sensitive-value and webhook guards

### v4.20.27 recovery identity

| Field | Value |
|---|---|
| Validated candidate commit | `c60ec6e17c2a980e73d9d92afb5d2ad59a9ad081` |
| SHA-256 | `8927d7064d2c757cae791cbcb14f2eaefcf3e831c32197727cbd846f95b05ea2` |
| Verified release record | `3bac8b32c352eae627a9dd7ad778fd3263b730c5` |
| Update manifest commit | `fee42c4af3ca6ec9a74152165e48201a5d32e626` |
| Public release | [v4.20.27](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v4.20.27) |
| Private backup commit | `db9c8669d535df7e7347613c3e2ad6aa2ec91127` |
| Private archive | `Conroy1988/missionchief-map-command-toolkit-private` |

## Development model

- `main` is canonical.
- Confirmed work is tracked through GitHub Issues.
- One scoped issue may generate one focused branch and pull request.
- Production releases are derived from validated source, not manually edited distribution copies.
- Private backup exists for recovery and evidence, not as a competing development source.
- README, documentation, changelog, manifests, release notes, and Discord output are expected to describe the live implementation.

## Support and development

| Destination | Purpose |
|---|---|
| [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) | User guides and system explanations |
| [Themes](https://conroy1988.github.io/missionchief-toolkit-assets/themes/) | Interface-system gallery |
| [Issues](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) | Confirmed bugs, enhancements, and roadmap work |
| [Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases) | Immutable version history and assets |
| [Changelog](CHANGELOG.md) | Human-readable release history |
| [Security](SECURITY.md) | Sensitive material and reporting policy |
| [Contributing](CONTRIBUTING.md) | Contribution expectations |

## Licence and attribution

The Toolkit source is released under the [MIT Licence](LICENSE).

MissionChief Map Command Toolkit is an independent community userscript. MissionChief, Leitstellenspiel, LSSM, Cyberpunk 2077, Fallout, Resident Evil / Umbrella, Factorio, James Bond / 007, The Legend of Zelda, and associated names or assets remain the property of their respective owners. Their mention does not imply sponsorship, affiliation, or endorsement.

<div align="center">

## **See the mission. Read the fleet. Command the map. Reconcile the operation.**

Created and maintained by [Conroy1988](https://github.com/Conroy1988).

</div>
