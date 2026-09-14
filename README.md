<p align="center"><a href="https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc"><img src="docs/media/extension-command-cover.svg" width="100%" alt="MissionChief Map Command Toolkit — map intelligence, operations and finance. Chrome extension. Black and red illustrated command map."></a></p>

<h1 align="center">MissionChief Map Command Toolkit</h1>
<p align="center"><strong>Your map. Your fleet. Your next move.</strong><br>A browser extension for MissionChief UK, with practical tools for running a growing operation.</p>
<p align="center">
<a href="https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc"><img src="https://img.shields.io/badge/INSTALL-Chrome_Web_Store-e33442?style=for-the-badge&amp;logo=googlechrome&amp;logoColor=white&amp;labelColor=13151a" alt="Install from Chrome Web Store"></a>
<a href="docs/EXTENSION_GUIDE.md"><img src="https://img.shields.io/badge/READ-Setup_Guide-f2f3f5?style=for-the-badge&amp;labelColor=13151a" alt="Read the setup guide"></a>
<a href="https://github.com/Conroy1988/missionchief-toolkit-assets/issues"><img src="https://img.shields.io/badge/GET-Support-8d98ac?style=for-the-badge&amp;labelColor=13151a" alt="Get support"></a>
</p>

> [!IMPORTANT]
> **The Toolkit is now a Chrome extension. The Tampermonkey/userscript edition is no longer supported.** Install through the **[Chrome Web Store](https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc)**. Existing script users: **[follow the migration guide](docs/MIGRATING_FROM_USERSCRIPT.md)** before disabling the old copy.

<p align="center"><a href="#built-for-your-operation">Features</a> · <a href="#operations-with-a-plan">Operations</a> · <a href="#get-started">Get started</a> · <a href="#privacy-and-control">Privacy</a> · <a href="#source-and-releases">Source</a></p>

## Built for your operation

Bring map controls, mission information, fleet visibility, building workflows and finance into the game. Open **Menu** for the Toolkit and **Game Guide** for the official TKB MissionChief guide.

| Area | What you can do |
|---|---|
| **Map & missions** | Use native mission and building filters, mission-age and value information, saved locations and drawing tools. |
| **Fleet** | Read vehicle status, locate units and inspect resource pressure while keeping the game map in view. |
| **Operations** | Plan Home Response coverage, replace selected Home Response unit types, upgrade hospitals and use recruitment and image-copying tools. |
| **Finance** | Review in-game financial information, reconciliation and reports. Send a chosen report to Discord after reviewing and confirming it. |
| **Your workspace** | Adjust appearance and layout, use keyboard commands and return to Operations without clearing an active task. |

**Install the version available in the Store.** The feature descriptions below include the **1.2.5 submission**; Google review and browser update delivery determine when that version becomes available to you. A source commit or test ZIP is not proof of Store approval.

## Operations with a plan

<p align="center"><img src="docs/media/extension-operations.svg" width="100%" alt="Three Operations tools: Home Response Builder, Home Response Unit Switcher and Hospital Upgrades. Review the scope, confirm the cost and verify progress."></p>

### Home Response Builder

Choose a city from search or the city list, select a boundary directly on the map, draw an area, or use a centre and radius.

- Set **1, 3, 4, 6, 8 or 10-mile spacing**, with up to **1,000 new locations**.
- Preview coverage around existing Home Responses, with mapped sea and major-lake exclusions.
- See named dispatch centres on the map. The nearest is selected automatically; acknowledge its distances before building.
- Select an allowed vehicle and an icon from the saved catalogue. Scan a particular building type when refreshing icons.
- Review estimated Credit costs, then follow saved progress through construction, vehicle purchase and optional icon copying.

Spacing is straight-line distance. Small waterways, road access and staffing/training still need your review. A limit of 20 means at most 20 proposals, spread across the chosen area.

### Home Response Unit Switcher

Select **All dispatch centres**, a named centre or Unassigned. Choose the current vehicle type and an allowed replacement, then select the vehicles to change.

- Shared fleet checks and concurrent shop reads make previews faster.
- Native **Credit** offers are checked across shop categories.
- Full single-vehicle buildings may show a clearly labelled estimate before removal; an enabled purchase offer is required afterwards.
- **Review & resume** checks saved progress before continuing an interrupted replacement.

> [!WARNING]
> Replacement permanently removes the selected old vehicle. If the next purchase fails, that building can temporarily have an empty slot. New vehicles use game-default names; staff and training are not automatically supplied. Review the selected vehicles and costs before confirming.

### Hospital Upgrades

Select hospitals and a **target level from 1 to 30**. The tool uses the game's direct target-level purchase rather than buying each intermediate level separately. Review your current balance, estimated costs and results; maximum-level completion is checked against the hospital record.

[Detailed setup and operating guidance →](docs/EXTENSION_GUIDE.md)

## Get started

1. **[Install from the Chrome Web Store](https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc)** in a compatible browser.
2. Disable any older **Toolkit** userscript or duplicate Toolkit extension. You can keep Tampermonkey for other scripts.
3. Open the extension popup, enable the Toolkit and apply/reload.
4. Fully reload **[MissionChief UK](https://www.missionchief.co.uk/)**, then open **Menu**.

**Already using Tampermonkey?** Export any settings you need before disabling the old copy. Ordinary settings may migrate, but complete transfers between userscript, unpacked and Store installations are not guaranteed. **[Migration steps →](docs/MIGRATING_FROM_USERSCRIPT.md)**

**Mobile:** Orion on iOS has been used for testing ZIP builds. Browser extension support varies; ordinary iPhone Safari cannot install this Chrome extension. Test packages are for explicit testing, not the public release channel.

## Privacy and control

- The Toolkit starts disabled until you enable it.
- Settings, supported caches and saved task progress stay in browser storage; they are not synced across devices by the Toolkit.
- Confirmed operations act on your signed-in MissionChief account and can spend Credits. Saved queues do not authorise automatic replay.
- Discord reporting is optional and requires confirmation. Webhook credentials stay in extension storage.
- City lookup and map tiles use OpenStreetMap services. Executable extension code is packaged locally.

Read the **[privacy policy](extension/store/PRIVACY.md)** for storage, requests, retention and provider details. Never put account credentials or webhook URLs in a public issue.

## Source and releases

| Looking for | Location |
|---|---|
| **Public installation and updates** | [Chrome Web Store](https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc) |
| **Extension source and build instructions** | [extension/](extension/README.md) |
| **Release notes** | [Extension changelog](extension/CHANGELOG.md) |
| **Bugs and performance reports** | [GitHub Issues](https://github.com/Conroy1988/missionchief-toolkit-assets/issues/new/choose) · [Support](SUPPORT.md) |
| **Legacy migration delivery** | [Migration package and deployment notes](legacy/README.md) |
| **Historical userscript source** | [src/](src/) — retained for provenance and recovery; unsupported |

The extension build currently composes the recovered release baseline with maintained feature modules. **[Development instructions](CONTRIBUTING.md)** explain how to reproduce the package and run its checks. Historical GitHub userscript releases and release-state dashboards are archives; their version numbers do not describe the Chrome Store extension.

## Community

**[TKB MissionChief Game Guide](https://tkb-gaming.scot/games/missionchief/guides/)** · **[TKB Gaming](https://tkb-gaming.scot/)** · **[Discord](https://discord.gg/3ZdXhYjgDm)**

**Developer: [Conroy1988](https://github.com/Conroy1988).**

Independent community software; not an official MissionChief, SHPlay or XYRALITY product. Existing source licence notices remain applicable. The artwork above is original schematic branding, not a screenshot or a real emergency operation.

<p align="center"><a href="https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc"><strong>GET THE TOOLKIT ON THE CHROME WEB STORE →</strong></a></p>
