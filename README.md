<div align="center">

<img src="docs/media/readme-hero.svg" alt="MissionChief Map Command Toolkit United Kingdom emergency command network" width="100%">

# MissionChief Map Command Toolkit

### **The operational command layer for the MissionChief map**

**See the incident · Read the fleet · Control the map · Reconcile the operation**

<table>
<tr>
<td width="25%" align="center"><a href="https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/"><strong>⬇ INSTALL / UPDATE</strong><br><sub>Official TKB channel</sub></a></td>
<td width="25%" align="center"><a href="https://conroy1988.github.io/missionchief-toolkit-assets/"><strong>📘 OPEN THE GUIDE</strong><br><sub>Features, setup and operation</sub></a></td>
<td width="25%" align="center"><a href="https://conroy1988.github.io/missionchief-toolkit-assets/themes/"><strong>🎛 EXPLORE INTERFACES</strong><br><sub>Eight complete command systems</sub></a></td>
<td width="25%" align="center"><a href="status/README.md"><strong>✓ RELEASE CONTROL</strong><br><sub>Verified production state</sub></a></td>
</tr>
</table>

## **Verified production release**

### **Live version and distribution authority: [Release Control](status/README.md)**

[![GitHub release](https://img.shields.io/github/v/release/Conroy1988/missionchief-toolkit-assets?display_name=release&label=RELEASE&color=2563eb)](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest)
[![TKB distribution](https://img.shields.io/badge/TKB-OFFICIAL%20INSTALL-e52b32)](https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/)
[![Greasy Fork mirror](https://img.shields.io/greasyfork/v/586018?label=GREASY%20FORK%20MIRROR&color=670000)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Canonical validation](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml/badge.svg)](https://github.com/Conroy1988/missionchief-toolkit-assets/actions/workflows/validate-userscript.yml)
[![Licence](https://img.shields.io/badge/LICENCE-MIT-111827)](#licence-and-attribution)

[**Command brief**](#command-brief) · [**Current interface**](#current-interface--v1020) · [**Systems**](#operational-divisions) · [**Interfaces**](#eight-complete-interface-systems) · [**Devices**](#field-terminal-coverage) · [**Install**](#install-and-update) · [**Release control**](#release-and-recovery-control)

</div>

---

## Command brief

MissionChief spreads operational information across the map, mission windows, vehicle tables, alliance pages, transport requests and finance views.

**MissionChief Map Command Toolkit converts those native signals into one configurable command layer.** It improves situational awareness, fleet readability, map context, selected transport workflows and financial reconciliation without replacing MissionChief’s own mission windows or dispatch controls.

<table>
<tr>
<td width="25%" align="center"><strong>🚨 INCIDENT</strong><br><sub>Priority awareness through one bounded Incident Command Wire.</sub></td>
<td width="25%" align="center"><strong>🚒 FLEET</strong><br><sub>Response codes, custom identity and nearby resource context.</sub></td>
<td width="25%" align="center"><strong>🗺 MAP</strong><br><sub>Coverage, saved places and mission geography made operational.</sub></td>
<td width="25%" align="center"><strong>📊 CONTROL</strong><br><sub>Financial intelligence, recovery evidence and device-aware layouts.</sub></td>
</tr>
</table>

> **Command doctrine:** expose the signal, preserve the source, act through the correct native control, and leave the page recoverable.

<div align="center">

<img src="docs/media/readme-command-board.svg" alt="MissionChief Map Command Toolkit operational divisions surrounding the central product identity" width="100%">

</div>

---

## Current interface — v10.2.3

### One command system across desktop, tablet and iPhone

Version `10.2.3` restores a cleaner native MissionChief map and Alliance Chat by retiring Mission Progress Rings and Alliance Chat Mission Previews completely. Their map layer, generated cards, settings, saved-state keys, observer branch and styling have been removed. **Unit Locator & Follow Mode** remains available to search personal vehicles by caption, ID, type, station or FMS/status and follows only the explicitly selected live marker until the map is moved manually, the marker disappears, Safe Mode starts or Stop is selected. **One-Click Session Cleanup** continues to preview an exact transient-state allowlist before confirmation and protects settings, device layouts, themes, profiles, bookmarks, recovery snapshots, Discord webhooks, secrets, Financial Archive history and MissionChief data.

Version `10.1.0` makes the command experience easier to discover, faster to reach and safer to recover. **What’s New & Feature Beacon** introduces each addition with a direct Open Feature action and leaves a `NEW` marker on its Settings route until viewed. Right-click a supported mission, vehicle or building—or long-press its marker on Tablet/iOS—for a contextual menu containing safe focus, native open and local search actions only.

**Complete MissionChief Reskinning** can extend the active Toolkit interface across MissionChief navigation, mission lists, windows, tables, forms and buttons while preserving operational warning, success and danger meaning. **Smart Auto-Hiding Dock** tucks the command controls against the configured edge without hiding the launcher or live version status.

**Hotkey & Gesture Studio** remaps every Toolkit keyboard command with duplicate rejection and assigns four optional touch swipes. **Toolkit Safe Mode** temporarily suspends optional overlays, dashboards, effects and input surfaces while retaining Settings, Toolkit Doctor, export, recovery and a guaranteed exit. Existing feature choices, webhooks and Financial Archive data are not overwritten.

Version `10.0.0` adds the six-part **Personalisation Studio**. Open it from Settings or search for it in the Command Palette to configure independent Desktop, Tablet and iOS control layouts, custom interface colours and surfaces, four through eight Quick Wheel slots, protected settings backups, first-run guidance and opt-in sounds or browser notifications.

The Layout Builder supports drag, touch and keyboard-friendly arrow controls; hidden controls remain reachable through Settings and the Palette. Theme codes contain visual choices only. The Backup Centre keeps the established authenticated AES-256-GCM full transfer for private data, a secret-free safe export and five bounded local settings snapshots. Automatic snapshots contain Toolkit state only—Discord webhooks and Financial Archive identity or history remain in their dedicated stores and enter only the encrypted transfer.

The Setup Wizard appears automatically only on a genuinely fresh install. Every existing user upgrades without interruption and can reopen or skip it at any time. Sounds are synthesised locally, browser permission is requested only after an explicit choice, and alerts reuse existing mission and diagnostic lifecycles without adding a network request, poller, timer or observer.

Version `9.4.0` added the global **Toolkit Command Palette**. Press `K`, select the permanent **Palette** map control, open it from Settings or assign it to the Tablet Quick Wheel. Search active missions, personal vehicles, buildings, Quick Places, bookmarks, map profiles, Settings cards and safe Toolkit actions without leaving the map.

Results are ranked locally from the live runtime snapshot only when the Palette opens. It adds no network request or background task, never selects or dispatches a vehicle and routes every result through an existing Toolkit or MissionChief-native pathway. The fixed Locations Quick Jumps remain **Edinburgh, Fife, Wakefield, London and Newcastle**.

The six daily command-experience tools introduced in v9.3.0 remain intact. **Toolkit Doctor** checks the installed version, interface ownership, saved-state recovery, map shell, UK intelligence and responsive bounds without copying secrets. **Full-Screen Map** maximises the operational workspace with persistent and `Escape` recovery. Tablet users can long-press the map for a configurable six-action **Quick Wheel**, and Desktop and Tablet keep independent Spacious, Standard, Compact or Command Centre density choices.

Full settings transfer is now passphrase-encrypted and authenticated before leaving the browser. It includes the Discord webhook and Financial Archive only inside AES-256-GCM ciphertext; a separate safe JSON export omits private integrations, archive identity and history. A once-per-version **Update Briefing** introduces changes after a safe deferred startup and can always be reopened from Settings. MissionChief UK Knowledge Link, the six-section Command Interface, map-native Pressure Board, Tablet header clearance, custom callsigns and every retained v9.2 system remain intact.

- **Map** contains visibility, overlays and map tools.
- **Missions** contains intelligence, the Operational Pressure Board, resource planning, Patient Transport Sweep and response operations.
- **Finance** contains Discord reports, Payout Flash and the local Financial Archive.
- **Locations** contains quick jumps, bookmarks and map profiles.
- **Appearance** clearly separates Toolkit interface themes from operational map skins.
- **Settings** contains device layout, dock position, keyboard controls, Economy Mode, command-bar visibility and recovery.

The board reconciles active personal and joined alliance missions against the available personal fleet so the same specialist vehicle cannot satisfy several missions at once. Canonical UK type IDs take priority over callsign text; own-vehicle classification evidence is considered next and fuzzy text is reserved for requirements with no catalogue entry. It shows Top Actions, confirmed shortfalls, partial location evidence, Fleet Conflicts, reserve risk and patient/prisoner transport pressure. **Focus**, **Open** and **Pin** remain read-only navigation actions; the board never selects or dispatches vehicles.

The matching **Operational SITREP** is posted only when the user selects **Generate & Post Operational SITREP**. It reuses the saved Finance Discord webhook, suppresses mentions and sends the same evidence snapshot shown on the board. The single map launcher, explicit command states, current-section search and responsive navigation continue to behave consistently under every interface theme.

Toolkit settings survive normal page refreshes and userscript updates through a revisioned Tampermonkey copy plus the existing MissionChief page-storage copy. A previous good revision is retained for recovery, and legacy settings are migrated before defaults are considered. The Tablet panel uses a 44×44 drag grip and a wider readable navigation rail; iOS Mobile remains a fixed bottom sheet.

---

## Operational divisions

### Mission command

| Capability | Operational purpose |
|---|---|
| **Incident Command Wire** | Broadcasts the priority incident sequence with an expanded queue and direct map navigation |
| **Operational Pressure Board** | Opens from the map with shortcut `B` and combines mission priority, shared fleet demand, reserve risk and transport pressure into one evidence-led board |
| **Toolkit Command Palette** | Opens with `K` and searches live missions, vehicles, buildings, locations, Settings and safe commands from one responsive surface |
| **Contextual Command Menus** | Opens safe item-specific focus, native-open and Palette-search actions by right-click or touch long-press without dispatching units |
| **MissionChief UK Knowledge Link** | Explains live requirements with verified units, crew, training and personnel evidence plus direct TKB Guide records |
| **Toolkit Doctor** | Runs privacy-safe diagnostics for version, runtime ownership, persistence, map mount, public Guide reachability and responsive geometry |
| **Personalisation Studio** | Builds independent device layouts, custom themes, a four-to-eight-slot Quick Wheel, protected backups, setup guidance and opt-in alerts |
| **MissionChief Reskin, Smart Dock and Input Studio** | Extends the active theme across the game, auto-hides the dock and remaps every Toolkit hotkey or opt-in touch gesture |
| **What’s New & Toolkit Safe Mode** | Makes new features discoverable and supplies a settings-preserving recovery state with Doctor, export and recovery access |
| **Unit Locator & Follow Mode** | Searches personal vehicles locally and follows one explicitly selected live marker with visible cancellation |
| **One-Click Session Cleanup** | Previews and clears only allowlisted transient Toolkit state while protecting settings, secrets and history |
| **Full-Screen Map and Tablet Quick Wheel** | Maximises the map with guaranteed recovery and exposes configurable long-press actions on Tablet |
| **Operational SITREP** | Manually posts the current board snapshot to the saved Discord webhook with mention suppression and no automatic dispatch or posting |
| **Mission Age map timers** | Adds compact age badges above personal missions; shortcut `6` toggles the surface |
| **Mission Value** | Shows verified mission value inside opened MissionChief windows |
| **Unit Commitment** | Presents committed response context without replacing native dispatch controls |
| **Transport Watcher** | Identifies patient and prisoner transport demand |

### Fleet and transport command

| Capability | Operational purpose |
|---|---|
| **Vehicle Code Status** | Summarises the live fleet by response code, description and count |
| **Custom Vehicle Badges** | Shows Own Vehicle Categories beside native vehicle types without replacing native identity |
| **Auto-load all vehicles** | Uses MissionChief’s native hidden-vehicle batch control |
| **Patient Transport Sweep** | Processes eligible alliance patient vehicles through MissionChief’s native vehicle and release controls |
| **Resource Gap** | Compares active demand with nearby personal vehicle availability |

Patient Transport Sweep remains deliberately bounded. It uses MissionChief-owned windows and controls, verifies the native result, and stops safely when authoritative evidence does not change.

### Map and place command

| Capability | Operational purpose |
|---|---|
| **Coverage rings** | Adds readable response-range context around selected locations |
| **Smart Bookmark Labels** | Creates compact place labels, pins and touch previews |
| **Profiles and layouts** | Preserves distinct command presentations without changing MissionChief data |
| **Toolkit Command Palette** | Finds Quick Places, bookmarks, map profiles, map records and existing Toolkit controls without duplicating or automating them |
| **Responsive modes** | Reflows the command surface for Desktop, Tablet and iOS Mobile Mode, with separate Desktop and Tablet density choices |
| **Update Briefing** | Explains each installed release once, defers around active dialogs and transport work, and remains manually reopenable |

### Finance and recovery command

| Capability | Operational purpose |
|---|---|
| **Alliance Credits** | Adds mission-value and eligibility-aware alliance filtering |
| **Financial intelligence** | Builds daily, weekly, monthly and custom-period performance context |
| **Reconciliation checkpoints** | Anchors complete periods to MissionChief revenue, spending and sum evidence |
| **Variance preservation** | Keeps unexplained differences visible instead of inventing classifications |
| **Payout presentations** | Provides optional visual and audio payout feedback with reduced-motion controls |
| **Discord reporting** | Sends Simple, Informative or The Wolf finance reports only through the saved Discord webhook configured by the user |

---

## The One We Knew Before

Version 7 restored the Toolkit’s product boundary, and the v8 line continues it:

| Boundary | Operational result |
|---|---|
| **MissionChief remains authoritative** | Native mission windows, lists and dispatch controls stay in charge |
| **Retired lifecycle ownership stays deleted** | Removed observers, timers, listeners, settings and DOM transforms do not return |
| **Independent Toolkit systems remain protected** | Mission, fleet, transport, map, finance, interfaces and responsive modes remain independently useful |
| **Retirement contracts remain executable** | Validation fails if removed integration code is accidentally reintroduced |
| **The product identity stays focused** | The Toolkit remains a map-command and operational-intelligence layer |

---

## Runtime command discipline

A command tool that slows the incident map is not a command tool.

- Disabled modules must not retain recurring timers or active lifecycle work.
- Inactive interfaces do not load hosted media or continue interface-specific effects.
- Broad document scans are avoided where bounded ownership is possible.
- Map, command and responsive state use deterministic teardown and restoration.
- **Economy Mode** suppresses non-essential work while retaining core information.
- Reduced-motion preferences remove presentation overhead without hiding operational facts.
- Source contracts protect observer, timer, listener, selector and retired-feature budgets.

---

## Eight complete interface systems

Every interface presents the same retained capability and stored configuration. The visual language changes; the operational contract does not.

| Interface | Command-room character |
|---|---|
| **Map Command** | Clean cyan telemetry and modern dispatch-console readability |
| **Cyberpunk** | Neon incident signalling and angular high-contrast controls |
| **Fallout 4** | Green phosphor terminals and industrial emergency-survival controls |
| **Umbrella** | Clinical containment, black surfaces and red-alert discipline |
| **Factorio** | Machinery panels, amber controls and production-line logic |
| **007 Intelligence** | Classified dossiers, restrained black surfaces and champagne-gold controls |
| **Hyrule Command** | Royal cartography, luminous energy and ancient command motifs |
| **The Godfather** | Oxblood, antique gold, polished wood and restrained family-command authority |

Inactive interfaces do not run theme-specific effects. [Explore all eight interfaces](https://conroy1988.github.io/missionchief-toolkit-assets/themes/).

---

## Field terminal coverage

| Mode | Designed behaviour |
|---|---|
| **Desktop** | Full command panels, fixed chrome, internal scrolling and keyboard control |
| **Ultrawide** | Expanded layouts without uncontrolled text width or detached controls |
| **Tablet/iPad** | Space-aware landscape presentation, safe touch controls and responsive panels |
| **iPhone Safari** | Safe-area-aware sheets, 44px interaction targets, toolbar recovery and touch-first navigation |
| **iPad Safari** | Split-view resilience, desktop-site awareness, visual-viewport fitting and orientation recovery |
| **Economy / reduced motion** | Complete command information with non-essential movement removed |

Responsive behaviour is part of the feature contract—not a cosmetic patch added after desktop development.

---

## Install and update

1. Install **Tampermonkey** or another compatible userscript manager.
2. Open the verified installer: **[Install MissionChief Map Command Toolkit](https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/)**.
3. Confirm installation and reload MissionChief.
4. Open the Toolkit command button on the map.
5. Enable only the systems useful to the current account, device and workflow.

> [!IMPORTANT]
> **TKB is the supported installation and automatic-update channel.** GitHub is the canonical source, validation authority and immutable release archive. Greasy Fork is a non-blocking discovery mirror.

| Need | Destination |
|---|---|
| Install or update | [Official TKB installer](https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/) |
| View download statistics | [TKB product page](https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/#stats-title) |
| Read the guide | [Documentation](https://conroy1988.github.io/missionchief-toolkit-assets/) |
| Explore interfaces | [Theme and interface gallery](https://conroy1988.github.io/missionchief-toolkit-assets/themes/) |
| Check release health | [Release Control Panel](status/README.md) |
| Review releases | [GitHub Releases](https://github.com/Conroy1988/missionchief-toolkit-assets/releases) |
| Read version history | [CHANGELOG.md](CHANGELOG.md) |
| Report a confirmed issue | [Issue tracker](https://github.com/Conroy1988/missionchief-toolkit-assets/issues) |

---

## Release and recovery control

<div align="center">

<img src="docs/media/readme-release-control.svg" alt="MissionChief Map Command Toolkit verified release and recovery control room" width="100%">

</div>

### Current verified identity

| Field | Verified value |
|---|---|
| **Version and release focus** | [Release Control Panel](status/README.md) |
| **Canonical source** | `src/MissionChief_Map_Command_Toolkit.user.js` |
| **Validated SHA-256** | [`dist/SHA256SUMS.txt`](dist/SHA256SUMS.txt) |
| **GitHub Release** | [Latest verified release](https://github.com/Conroy1988/missionchief-toolkit-assets/releases/latest) |
| **Official distribution** | [TKB MissionChief Scripts](https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/) |
| **Greasy Fork** | [Non-blocking mirror](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit) |
| **Private backup and Discord delivery** | [Release Control Panel](status/README.md) |
| **Hosted media audit** | [Asset Health](.github/ASSET_HEALTH.md) |

```text
Canonical source
      ↓
Exact-head validation
      ↓
Immutable GitHub Release
      ↓
TKB install/update verification
      ↓
Private recovery backup + optional Greasy Fork check
      ↓
Discord release confirmation
```

GitHub remains authoritative. TKB owns the supported public distribution URLs; Greasy Fork is checked as a discovery mirror and is never imported back into canonical source.

---

## Security and engineering

- Configuration remains local to the browser unless the user explicitly uses a supported reporting feature.
- MissionChief UK Guide intelligence is downloaded only after a user opens **UK Intel**, is schema-validated and never includes player or mission-instance data.
- Full settings transfer includes the saved Discord webhook and Financial Archive only inside passphrase-authenticated AES-256-GCM ciphertext; safe JSON exports exclude those private values.
- The Toolkit does not require a remote player account, remote telemetry service or separate player database.
- `main` is canonical.
- Confirmed work is tracked through GitHub Issues.
- Production releases are derived from freshly validated canonical source.
- Documentation, release notes, status records and distribution copy must describe the same implementation.
- Desktop, Tablet/iPad and iOS Mobile/Safari remain mandatory release concerns.

---

## Licence and attribution

The Toolkit source is released under the [MIT Licence](LICENSE).

MissionChief Map Command Toolkit is an independent community userscript created and maintained by [Conroy1988](https://github.com/Conroy1988). It is not operated by, endorsed by or affiliated with SHPlay GmbH or the official MissionChief team.

MissionChief, Leitstellenspiel, Cyberpunk 2077, Fallout, Resident Evil / Umbrella, Factorio, James Bond / 007, The Legend of Zelda and associated names or assets remain the property of their respective owners. Their mention does not imply sponsorship, affiliation or endorsement.

<div align="center">

---

## **SEE THE MISSION · READ THE FLEET · COMMAND THE MAP · RECONCILE THE OPERATION**

[![Install Toolkit](https://img.shields.io/badge/INSTALL-MAP_COMMAND_TOOLKIT-8B0000?style=for-the-badge&logo=tampermonkey&logoColor=white)](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)

</div>
