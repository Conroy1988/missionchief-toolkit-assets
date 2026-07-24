<div align="center">

<img src="docs/media/readme-hero.svg" alt="MissionChief Map Command Toolkit operational command platform" width="100%">

# MissionChief Map Command Toolkit

### Turn the MissionChief map into a live operations console

**Operational mission windows · Live requirements intelligence · Fleet identity · Geographic command · Financial reconciliation · Desktop, tablet and iOS**

[![Install now](https://img.shields.io/badge/INSTALL_NOW-GREASY_FORK-8B0000?style=for-the-badge&logo=tampermonkey&logoColor=white)](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)
[![Open documentation](https://img.shields.io/badge/OPEN-DOCUMENTATION-1677A3?style=for-the-badge&logo=readthedocs&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/)
[![Explore interfaces](https://img.shields.io/badge/EXPLORE-7_INTERFACE_SYSTEMS-6D28D9?style=for-the-badge&logo=palette&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)

**Current verified release: `v5.0.7`**

[![GitHub release](https://img.shields.io/github/v/release/Conroy1988/missionchief-toolkit-assets?display_name=release&label=RELEASE&color=2563eb)](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest)
[![Greasy Fork](https://img.shields.io/greasyfork/v/586018?label=GREASY%20FORK&color=670000)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Installs](https://img.shields.io/greasyfork/dt/586018?label=INSTALLS&color=0f766e)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Stars](https://img.shields.io/github/stars/Conroy1988/missionchief-toolkit-assets?style=flat&color=ca8a04)](https://github.com/Conroy1988/missionchief-toolkit-assets/stargazers)
[![Viewed](https://komarev.com/ghpvc/?username=Conroy1988-missionchief-toolkit-assets&label=VIEWED&color=7b6cf6&style=flat)](https://github.com/Conroy1988/missionchief-toolkit-assets)
[![Canonical validation](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml/badge.svg)](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml)
[![Licence](https://img.shields.io/badge/LICENCE-MIT-111827)](#licence-and-attribution)

[**Mission briefing**](#mission-briefing) · [**Install**](#install-in-under-a-minute) · [**Operational Window**](#operational-window-suite) · [**Command systems**](#operational-command-systems) · [**Interfaces**](#seven-complete-interface-systems) · [**Devices**](#built-for-every-screen) · [**Delivery**](#verified-delivery-and-recovery)

</div>

---

# 🚨 Mission briefing

MissionChief exposes operational information across map markers, mission windows, available-unit tables, transport controls, finance pages and separate navigation surfaces.

**MissionChief Map Command Toolkit unifies those signals into one configurable command layer.** It helps players identify urgent work, understand live mission demand, distinguish specialist capability, assess geographic coverage, reconcile financial performance and move between incidents without losing context.

| Operational task | Toolkit response |
|---|---|
| **Triage** | Surface old, critical, blocked and transport-dependent missions |
| **Understand demand** | Reconcile required, selected, en-route, on-scene and still-needed capability |
| **Identify capability** | Expose specialist vehicle roles, equipment and qualified personnel evidence |
| **Command the map** | Use heat maps, rings, bookmarks, focus modes and visibility controls |
| **Reconcile performance** | Track income, spending, variance, mission value and session results |

Every major family can be enabled independently. Run the complete suite or retain only the systems that improve the current account, workflow and device.

> **Operating principle:** information is useful only when its source is visible, its limits are explicit and the player can act without fighting the interface.

---

# ⚡ Install in under a minute

1. Install a userscript manager such as **Tampermonkey**.
2. Open the verified public installer: **[Install MissionChief Map Command Toolkit](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)**.
3. Confirm installation and reload MissionChief.
4. Open the Toolkit command button on the map.

> [!NOTE]
> **Greasy Fork is the supported installation and automatic-update channel.** GitHub is the canonical development source, validation authority, documentation host and immutable release archive.

| Need | Destination |
|---|---|
| Install or update | [Greasy Fork installer](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js) |
| Read the user guide | [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) |
| Explore all interfaces | [Theme and interface gallery](https://conroy1988.github.io/missionchief-toolkit-assets/themes/) |
| Review releases | [GitHub Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases) |
| Read version history | [CHANGELOG.md](CHANGELOG.md) |
| Report a confirmed problem | [Issue tracker](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) |

---

# 🧭 Operational Window Suite

Toolkit v5 replaced the former requirements-only mission panel with one coordinated, versioned mission-window system. One lifecycle coordinator owns the active document, coalesces rendering and tears down deterministically when MissionChief replaces the window.

## Four operational families

| Family | Purpose |
|---|---|
| **Enhanced Operational Requirements** | Reconciles vehicles, equipment, personnel, capacity, trailers, selected units, en-route units, on-scene units and remaining demand |
| **Extended Call Window** | Adds patient and vehicle summaries, selected and ARR counters, search, highlighting, generation/alarm context, keywords and map controls |
| **Extended Mission List** | Adds sorting, starring, collapsing, patient/prisoner indicators, credit and remaining-time badges, and native sharing controls |
| **Enhanced Transport Requests** | Provides opt-in guarded transport assistance with exact-route validation, candidate filtering, ambiguity rejection and per-route duplicate protection |

All settings use typed controls—switches, numbers, colour controls, selects and structured editors. Internal drag, overlay and persisted list state is not exposed as raw configuration.

## Requirements truth states

Enhanced Operational Requirements treats the live MissionChief page as authoritative and never converts missing evidence into a complete-looking result.

| State | Presentation | Meaning |
|---|---|---|
| **Covered** | Green | Positive requirement evidence was parsed and every known row is satisfied |
| **Open** | Requirement rows | Positive evidence shows remaining vehicles, equipment or personnel |
| **Waiting** | Amber | MissionChief has not supplied usable requirement evidence yet |
| **Unresolved** | Amber warning | Evidence exists but cannot be classified safely |

The engine keeps guaranteed, probabilistic, conditional and alternative demand separate; tracks qualified personnel only from reviewed evidence; handles patient-derived demand and trailer/towing relationships; and fails closed where MissionChief does not expose enough information.

## MissionChief and LSSM coexistence

The Toolkit searches active native requirement sources, grouped requirement data and compatible hidden LSSM raw-data carriers. It scores candidate sources by parsed evidence, active mission ownership, visibility and connection state, then rebinds when MissionChief replaces the authoritative source.

A genuinely visible equivalent LSSM panel suppresses the matching Toolkit surface to prevent duplication. Hidden raw evidence may still be used for reconciliation. When the live mission placeholder is empty, v5.0.7 can perform one bounded same-origin mission-page recovery with mission-scoped caching, error backoff and automatic rebinding.

---

# 📡 Current production line

| Release | Production result |
|---|---|
| **v5.0.0** | Introduced the Operational Window Suite and migrated existing requirements enablement automatically |
| **v5.0.1–v5.0.3** | Recovered menu startup, isolated launcher bootstrap and fixed the fatal preboot declaration-order failure |
| **v5.0.4** | Stopped empty or failed requirement parsing from appearing as confirmed green coverage |
| **v5.0.5** | Added authoritative native/LSSM source discovery, raw-data recovery and source rebinding |
| **v5.0.6** | Restored launcher lifecycle, typed settings, complete runtime mapping and Mission Age labels |
| **v5.0.7** | Preserved collapsed command state, isolated child mission frames and added bounded mission-page requirement recovery |

Existing Toolkit settings are retained. No manual reset is required when upgrading from the v4 production line.

---

# 🛰️ Operational command systems

## Mission command

| Capability | Operational purpose |
|---|---|
| **Mission Age Watch** | Surfaces personal and alliance missions by age, ownership, category, urgency, assistance state and clearing progress |
| **Critical View** | Creates a concentrated workflow for missions requiring immediate attention |
| **Mission Value** | Displays verified mission value inside opened mission windows |
| **Operational Window Suite** | Coordinates requirements, mission-window intelligence, mission-list controls and guarded transport assistance |
| **Mission Inspector** | Loads deeper mission context only when requested |
| **Mission Spawn** | Detects newly appearing mission activity through bounded state ownership |
| **Stuck Detector** | Identifies missions that remain unresolved beyond the configured monitoring contract |
| **Major Incident Feed** | Maintains a high-priority incident feed with click-to-zoom navigation |
| **Transport Watcher** | Identifies patient and prisoner transport demand |
| **Patient Transport Sweep** | Processes eligible alliance ambulances sequentially while excluding the signed-in player’s own vehicles |
| **Resource Gap** | Compares active demand with available personal vehicle context inside a selected radius |

## Fleet and map intelligence

| Capability | Operational purpose |
|---|---|
| **Vehicle Code Status** | Summarises the live fleet by response code, description and count |
| **Custom Vehicle Badges** | Exposes Own Vehicle Categories beside native vehicle types without replacing them |
| **Auto-load all vehicles** | Uses MissionChief’s native hidden-vehicle batch control |
| **Coverage Heat Map** | Visualises geographic operational coverage |
| **Coverage rings** | Adds readable range context around locations |
| **Smart Bookmark Labels** | Creates compact place labels with overrides and touch previews |
| **Visibility command layer** | Controls missions, vehicles and buildings without leaving the map |
| **Focus, Clean and Compact modes** | Reduce interface noise while preserving restoration and command ownership |

MissionChief can display the same base vehicle type for assets serving different operational roles. Custom Vehicle Badges retains the native vehicle type while exposing the player’s Own Vehicle Category. Stable vehicle-ID classification can then provide safer specialist context to Enhanced Operational Requirements and Resource Gap.

## Financial command

| Capability | Operational purpose |
|---|---|
| **Alliance Credits** | Adds mission values, eligibility-aware states and filters |
| **Financial Advisor** | Builds daily, weekly, monthly and custom-period income/spending analysis |
| **Overview reconciliation** | Anchors complete days to MissionChief Revenue, Spendings and Sum checkpoints |
| **Variance reporting** | Preserves unexplained differences without inventing classifications |
| **Discord financial reports** | Sends the canonical reconciled model through the saved Discord webhook |
| **Financial Command graphics** | Generates visual summaries from the same reconciled data model |
| **Session performance** | Tracks credits, completions, largest payout, aged missions and payout events |

---

# 🎛️ Seven complete interface systems

Every interface system provides the same operational functionality and stored configuration. Inactive interfaces do not load their hosted media or run theme-specific effects.

| Interface | Visual command language |
|---|---|
| **Map Command** | Clean cyan telemetry and map-first readability |
| **Cyberpunk** | Neon cyan, warning yellow, magenta accents and angular telemetry |
| **Fallout 4** | Green phosphor, aged terminals and industrial survival interfaces |
| **Umbrella** | Clinical black, white, red and containment-alert discipline |
| **Factorio** | Industrial machinery, amber controls and production-line logic |
| **007 Intelligence** | Classified dossiers, restrained black surfaces and champagne-gold controls |
| **Hyrule Command** | Royal gold, parchment cartography, ancient blue and luminous green energy |

Economy Mode and reduced-motion preferences suppress non-essential presentation overhead without removing operational information.

---

# 📱 Built for every screen

| Mode | Designed behaviour |
|---|---|
| **Desktop** | Full command panels, fixed chrome, internal section scrolling and keyboard control |
| **Ultrawide** | Expanded operational layouts without uncontrolled line length or detached controls |
| **Tablet/iPad** | Space-aware landscape layouts, touch controls and safe single-column mission-window settings |
| **iPhone Safari** | Safe-area-aware sheets, 44px targets, browser-toolbar recovery and touch-first navigation |
| **iPad Safari** | Split-view resilience, desktop-site awareness, visual-viewport fitting and orientation recovery |
| **Economy/reduced motion** | Complete functional command surface with non-essential effects removed |

Responsive behaviour is part of each feature contract—not a skin applied after desktop development.

---

# 🛡️ Verified delivery and recovery

The canonical userscript is:

```text
src/MissionChief_Map_Command_Toolkit.user.js
```

```text
Issue-scoped development
        ↓
Owner-created branch and pull request
        ↓
Source, regression and documentation contracts
        ↓
Validated distribution candidate
        ↓
GitHub Release and checksum verification
        ↓
Greasy Fork parity verification
        ↓
Private recovery backup
        ↓
Discord release transmission
        ↓
Public asset and release-readiness audit
```

Validation covers userscript syntax and metadata, source/distribution parity, requirement truth states, Operational Window lifecycle, Desktop/Tablet/iOS behaviour, LSSM coexistence, observer/listener teardown, performance budgets, public documentation consistency, hosted assets, release channels and sensitive-value guards.

---

# 🔐 Configuration and privacy

The Toolkit runs in the browser against the signed-in MissionChief page. It does not operate a separate player-account service.

- Most settings remain local to the browser.
- Hosted assets are loaded only when required by the active interface.
- Financial reporting can send configured summaries to a user-supplied Discord webhook.
- Settings exports can contain that webhook and should be treated as private operational material.

> [!WARNING]
> Never publish an exported settings file containing a live Discord webhook.

---

# 🧭 Development model

- `main` is canonical.
- Confirmed work is tracked through GitHub Issues.
- Scoped work uses owner-created branches and pull requests.
- Production releases are derived from validated canonical source—not manually edited distribution copies.
- Desktop, Tablet/iPad and iOS Mobile/Safari compatibility are mandatory release concerns.
- README, documentation, changelog, manifests, release notes and Discord output must describe the live implementation.

---

# 🤝 Support and development

| Destination | Purpose |
|---|---|
| [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) | User guides and system explanations |
| [Interface gallery](https://conroy1988.github.io/missionchief-toolkit-assets/themes/) | Seven complete visual systems |
| [Issues](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) | Confirmed bugs, enhancements and roadmap work |
| [Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases) | Immutable version history and verified assets |
| [Changelog](CHANGELOG.md) | Human-readable release history |
| [Security](SECURITY.md) | Sensitive material and reporting policy |
| [Contributing](CONTRIBUTING.md) | Contribution expectations |

---

# ⚖️ Licence and attribution

The Toolkit source is released under the [MIT Licence](LICENSE).

MissionChief Map Command Toolkit is an independent community userscript created and maintained by [Conroy1988](https://github.com/Conroy1988). It is not operated by, endorsed by or affiliated with SHPlay GmbH or the official MissionChief team.

MissionChief, Leitstellenspiel, LSSM, Cyberpunk 2077, Fallout, Resident Evil / Umbrella, Factorio, James Bond / 007, The Legend of Zelda and associated names or assets remain the property of their respective owners. Their mention does not imply sponsorship, affiliation or endorsement.

<div align="center">

## **See the mission. Read the fleet. Command the map. Reconcile the operation.**

[![Install Toolkit](https://img.shields.io/badge/INSTALL-MAP_COMMAND_TOOLKIT-8B0000?style=for-the-badge&logo=tampermonkey&logoColor=white)](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)

</div>