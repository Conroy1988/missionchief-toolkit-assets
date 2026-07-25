<div align="center">

<img src="docs/media/readme-hero.svg" alt="MissionChief Map Command Toolkit v7 native command platform" width="100%">

# MissionChief Map Command Toolkit

### The fast, native command layer for MissionChief

**Mission intelligence · Fleet identity · Native transport support · Geographic context · Financial reconciliation · Desktop, tablet and iOS**

[![Install now](https://img.shields.io/badge/INSTALL_NOW-GREASY_FORK-8B0000?style=for-the-badge&logo=tampermonkey&logoColor=white)](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)
[![Open documentation](https://img.shields.io/badge/OPEN-DOCUMENTATION-1677A3?style=for-the-badge&logo=readthedocs&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/)
[![Explore interfaces](https://img.shields.io/badge/EXPLORE-7_INTERFACE_SYSTEMS-6D28D9?style=for-the-badge&logo=palette&logoColor=white)](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)
[![Release status](https://img.shields.io/badge/OPEN-RELEASE_CONTROL_PANEL-111827?style=for-the-badge&logo=githubactions&logoColor=white)](status/README.md)

## **Current verified release: `v7.1.0` · Development candidate: `v7.1.1` — Incident Command Wire hotfix**

[![GitHub release](https://img.shields.io/github/v/release/Conroy1988/missionchief-toolkit-assets?display_name=release&label=RELEASE&color=2563eb)](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest)
[![Greasy Fork](https://img.shields.io/greasyfork/v/586018?label=GREASY%20FORK&color=670000)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Installs](https://img.shields.io/greasyfork/dt/586018?label=INSTALLS&color=0f766e)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Stars](https://img.shields.io/github/stars/Conroy1988/missionchief-toolkit-assets?style=flat&color=ca8a04)](https://github.com/Conroy1988/missionchief-toolkit-assets/stargazers)
[![Viewed](https://komarev.com/ghpvc/?username=Conroy1988-missionchief-toolkit-assets&label=VIEWED&color=7b6cf6&style=flat)](https://github.com/Conroy1988/missionchief-toolkit-assets)
[![Canonical validation](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml/badge.svg)](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml)
[![Licence](https://img.shields.io/badge/LICENCE-MIT-111827)](#licence-and-attribution)

[**Mission briefing**](#mission-briefing) · [**What v7 changed**](#v700--the-one-we-knew-before) · [**Command surface**](#native-command-surface) · [**Interfaces**](#seven-complete-interface-systems) · [**Devices**](#built-for-every-screen) · [**Delivery**](#verified-delivery-and-recovery) · [**Install**](#install-in-under-a-minute)

</div>

---

# Mission briefing

MissionChief spreads operational information across the map, opened missions, available-unit tables, transport controls, finance pages, alliance views and separate navigation surfaces.

**MissionChief Map Command Toolkit adds one configurable command layer above those native systems.** It surfaces urgency, identifies fleet capability, adds geographic context, assists selected transport workflows, reconciles financial performance and keeps the result usable across desktop, tablet and iOS.

Version 7 deliberately narrows the product boundary. It does not replace MissionChief's mission windows or mission list, and it does not run a second competing global interaction engine.

> **v7 operating principle:** own less global DOM, do less recurring work, and keep every retained feature independently useful.

<table>
<tr>
<td width="25%" align="center"><strong>◉ SEE</strong><br><sub>Surface age, value, commitment, transport demand and major incidents.</sub></td>
<td width="25%" align="center"><strong>◈ READ</strong><br><sub>Expose response codes, custom fleet identity and nearby availability.</sub></td>
<td width="25%" align="center"><strong>⌖ COMMAND</strong><br><sub>Add range, place and touch-friendly geographic context.</sub></td>
<td width="25%" align="center"><strong>↗ RECONCILE</strong><br><sub>Preserve income, spending, payout and variance evidence.</sub></td>
</tr>
</table>

---

# v7.0.0 — The One We Knew Before

Version 7 is a deliberate product-boundary reset.

The release completely removes the copied extension-derived mission-window stack introduced during the v5 line. The associated settings, persistent state, observers, timers, listeners, schedulers, DOM transforms, compatibility hooks, styles and teardown paths are removed rather than hidden behind disabled switches.

## What the reset achieves

| Decision | Operational result |
|---|---|
| **Retire the copied global window stack** | MissionChief remains authoritative for mission-window and mission-list interaction |
| **Remove retired state and lifecycle ownership** | Less recurring work, fewer mutation paths and a smaller failure surface |
| **Preserve independent native systems** | Map, fleet, transport, finance, themes and responsive modes remain usable on their own |
| **Add permanent retirement contracts** | Repository validation fails if the removed integration is accidentally reintroduced |
| **Restore a clear product identity** | The Toolkit is once again a focused native command layer rather than a competing interface framework |

This is subtraction with intent. The release protects the systems that are uniquely Toolkit-owned and removes the code that diluted that boundary.

---

# Native command surface

## Mission command

| Capability | Operational purpose |
|---|---|
| **Mission Age map timers** | Adds compact age badges above personal missions; shortcut `6` toggles the surface |
| **Mission Value** | Shows verified mission value inside opened MissionChief windows |
| **Incident Command Wire** | Presents one priority incident at a time with manual controls, an expanded queue and click-to-zoom navigation |
| **Unit Commitment** | Presents committed response context without replacing native dispatch controls |
| **Transport Watcher** | Identifies patient and prisoner transport demand |

## Fleet and transport

| Capability | Operational purpose |
|---|---|
| **Vehicle Code Status** | Summarises the live fleet by response code, description and count |
| **Custom Vehicle Badges** | Shows Own Vehicle Categories beside native vehicle types without replacing native identity |
| **Auto-load all vehicles** | Uses MissionChief's native hidden-vehicle batch control |
| **Patient Transport Sweep** | Processes eligible alliance ambulances through MissionChief's native vehicle window and discharge control |
| **Resource Gap** | Compares active demand with nearby personal vehicle availability |

Patient Transport Sweep retains ownership checks, confirmation evidence, idempotent counters and a bounded HUD. It does not expose arbitrary clicks, arbitrary vehicle actions or a generic transport automation console.

## Map and place control

| Capability | Operational purpose |
|---|---|
| **Coverage rings** | Adds readable geographic range around selected locations |
| **Smart Bookmark Labels** | Creates compact place labels, pins and touch previews |
| **Profiles and command layouts** | Preserves separate operational presentation choices without changing the underlying native page |
| **Responsive modes** | Reflows the command surface for desktop, tablet/iPad and iOS Mobile Mode |

## Financial intelligence

| Capability | Operational purpose |
|---|---|
| **Alliance Credits** | Adds mission value and eligibility-aware alliance filtering |
| **Income and spending analysis** | Builds daily, weekly, monthly and custom-period performance context |
| **Reconciliation checkpoints** | Anchors complete periods to MissionChief revenue, spending and sum evidence |
| **Variance preservation** | Keeps unexplained differences visible instead of inventing classifications |
| **Payout presentations** | Provides optional visual and audio payout feedback with reduced-motion controls |
| **Discord reporting** | Sends the reconciled model through the saved Discord webhook configured by the user |

---

# Performance is a feature

The v6 and v7 release line treats lifecycle ownership and recurring work as product behaviour.

- Retired systems are removed from runtime state rather than merely disabled.
- Disabled modules must not retain recurring timers, active listeners or broad mutation work.
- Inactive interface systems do not run interface-specific effects.
- Repeated document-wide cleanup scans are avoided where bounded ownership is possible.
- Map, command and responsive state use deterministic teardown and restoration.
- **Economy Mode** suppresses non-essential work while retaining core command functionality.
- Reduced-motion preferences remove unnecessary presentation overhead without hiding operational information.
- Permanent source contracts protect runtime budgets and retired-feature boundaries.

The goal is not a high feature count. The goal is a useful command surface whose cost remains proportionate to the work it performs.

---

# Seven complete interface systems

The Toolkit retains seven complete interface systems. Every interface provides the same native feature set and stored configuration; the visual language changes, not the operational contract.

| Interface | Command language |
|---|---|
| **Map Command** | Clean cyan telemetry and map-first readability |
| **Cyberpunk** | Neon cyan, warning yellow, magenta accents and angular telemetry |
| **Fallout 4** | Green phosphor, aged terminals and industrial survival interfaces |
| **Umbrella** | Clinical black, white, red and containment-alert discipline |
| **Factorio** | Industrial machinery, amber controls and production-line logic |
| **007 Intelligence** | Classified dossiers, restrained black surfaces and champagne-gold controls |
| **Hyrule Command** | Royal gold, parchment cartography, ancient blue and luminous green energy |

Inactive interfaces do not load their hosted media or continue interface-specific effects.

[Explore all seven interfaces](https://conroy1988.github.io/missionchief-toolkit-assets/themes/)

---

# Built for every screen

| Mode | Designed behaviour |
|---|---|
| **Desktop** | Full command panels, fixed chrome, internal scrolling and keyboard control |
| **Ultrawide** | Expanded layouts without uncontrolled text width or detached controls |
| **Tablet/iPad** | Space-aware landscape presentation, safe touch controls and responsive panels |
| **iPhone Safari** | Safe-area-aware sheets, 44px interaction targets, toolbar recovery and touch-first navigation |
| **iPad Safari** | Split-view resilience, desktop-site awareness, visual-viewport fitting and orientation recovery |
| **Economy / reduced motion** | Complete command information with non-essential presentation work removed |

Responsive behaviour is part of each retained feature contract—not a skin applied after desktop development.

---

# Install in under a minute

1. Install **Tampermonkey** or a compatible userscript manager.
2. Open the verified public installer: **[Install MissionChief Map Command Toolkit](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)**.
3. Confirm installation and reload MissionChief.
4. Open the Toolkit command button on the map.
5. Enable only the native Toolkit systems useful to the current account, device and workflow.

> [!IMPORTANT]
> **Greasy Fork is the supported installation and automatic-update channel.** GitHub is the canonical development source, validation authority, documentation host and immutable release archive.

| Need | Destination |
|---|---|
| Install or update | [Greasy Fork installer](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js) |
| Read the user guide | [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) |
| Explore interfaces | [Theme and interface gallery](https://conroy1988.github.io/missionchief-toolkit-assets/themes/) |
| Review release health | [Release Control Panel](status/README.md) |
| Review releases | [GitHub Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases) |
| Read version history | [CHANGELOG.md](CHANGELOG.md) |
| Report a confirmed problem | [Issue tracker](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) |

---

# Verified delivery and recovery

## Current verified identity

| Field | Verified value |
|---|---|
| **Version** | `7.0.0` |
| **Release name** | `The One We Knew Before` |
| **Canonical source** | `src/MissionChief_Map_Command_Toolkit.user.js` |
| **Validated SHA-256** | `cc9b8a002763013a2c610f0f163ec8f8080aeba4c5831261ca045316feeee8fd` |
| **GitHub Release** | [`v7.0.0`](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v7.0.0) |
| **Greasy Fork** | Verified against the stable release |
| **Private backup** | `49100296997dc80cdcc6e91e9b6e8d075510cbb8` |
| **Discord release delivery** | Posted |
| **Hosted media audit** | 37 discovered · 33 referenced · 0 missing |

## Governed release topology

```text
Issue-scoped development on main
              ↓
Pull request and executable contracts
              ↓
Exact-source validation artefact
              ↓
Governed release-state ledger
              ↓
Stable distribution publication
              ↓
GitHub Release + Greasy Fork verification
              ↓
Private recovery backup
              ↓
Discord release confirmation
```

### Branch responsibilities

| Boundary | Responsibility |
|---|---|
| **`main`** | Canonical development source, documentation and reviewed product state |
| **`release-state`** | Governed release ledger, recovery identity and operational release records |
| **`distribution`** | Stable public distribution source derived from verified release state |
| **Actions artefacts** | Immutable validation candidates, audits, dry runs and diagnostics without transient commits to `main` |
| **Private recovery repository** | Versioned, checksum-backed disaster-recovery source |

GitHub remains authoritative. Greasy Fork is verified as the distribution channel rather than imported back into canonical source.

## Permanent validation scope

Validation covers:

- userscript syntax and metadata;
- canonical source and distribution parity;
- retained native feature ownership;
- v7 retirement boundaries;
- state migration;
- observer, timer, listener and selector budgets;
- Desktop, Tablet/iPad and iOS behaviour;
- hosted media and public-documentation consistency;
- GitHub Release and Greasy Fork channels;
- private recovery evidence;
- sensitive-value guards; and
- GitHub Pages production monitoring against the current v7 documentation surface.

Transient candidate and audit evidence is retained as immutable workflow artefacts rather than written into the public branch.

---

# Configuration and privacy

The Toolkit runs in the browser against the signed-in MissionChief page. It does not operate a separate player-account service.

- Most configuration remains local to the browser.
- Hosted interface media loads only when required by the active interface.
- Financial reporting can use only the saved Discord webhook configured by the user.
- Settings exports can contain that webhook and must be treated as private operational material.
- No exported settings file containing a live webhook should be published.
- The Toolkit does not require a remote account, remote telemetry service or separate player database.

---

# Development model

- `main` is canonical.
- Confirmed work is tracked through GitHub Issues.
- Scoped implementation uses owner-created branches and pull requests.
- Production releases are derived from freshly validated canonical source.
- Documentation, changelog, release notes, status records and distribution copy must describe the same live implementation.
- Desktop, Tablet/iPad and iOS Mobile/Safari remain mandatory release concerns.
- Performance, teardown, disabled-module cost and recovery evidence are release requirements.
- Public release speed is preserved without allowing transient workflow evidence to mutate canonical source.

| Resource | Purpose |
|---|---|
| [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) | User guidance and system explanations |
| [Interface gallery](https://conroy1988.github.io/missionchief-toolkit-assets/themes/) | Seven visual command systems |
| [Release Control Panel](status/README.md) | Current verified release identity and channel health |
| [Issues](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) | Bugs, enhancements and roadmap work |
| [Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases) | Immutable version history and verified assets |
| [Changelog](CHANGELOG.md) | Human-readable production history |
| [Security](SECURITY.md) | Sensitive material and reporting policy |
| [Contributing](CONTRIBUTING.md) | Contribution expectations |

---

# Licence and attribution

The Toolkit source is released under the [MIT Licence](LICENSE).

MissionChief Map Command Toolkit is an independent community userscript created and maintained by [Conroy1988](https://github.com/Conroy1988). It is not operated by, endorsed by or affiliated with SHPlay GmbH or the official MissionChief team.

MissionChief, Leitstellenspiel, Cyberpunk 2077, Fallout, Resident Evil / Umbrella, Factorio, James Bond / 007, The Legend of Zelda and associated names or assets remain the property of their respective owners. Their mention does not imply sponsorship, affiliation or endorsement.

<div align="center">

## **See the mission. Read the fleet. Command the map. Reconcile the operation.**

[![Install Toolkit](https://img.shields.io/badge/INSTALL-MAP_COMMAND_TOOLKIT-8B0000?style=for-the-badge&logo=tampermonkey&logoColor=white)](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)

</div>
