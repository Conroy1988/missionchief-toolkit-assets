<div align="center">

# MissionChief Map Command Toolkit

**Operational map command, monitoring and presentation suite for MissionChief UK**

[![Greasy Fork](https://img.shields.io/badge/Install-Greasy%20Fork-670000?logo=tampermonkey&logoColor=white)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Current Version](https://img.shields.io/badge/version-4.10.4-2563eb)](status/release-dashboard.json)
[![Validation](https://img.shields.io/badge/validation-passed-16a34a)](../../actions/workflows/validate-userscript.yml)
[![Release Pipeline](https://img.shields.io/badge/release%20pipeline-v2-7c3aed)](docs/RELEASE_PIPELINE.md)
[![Platform](https://img.shields.io/badge/MissionChief-UK-0f766e)](https://www.missionchief.co.uk/)
[![Licence](https://img.shields.io/badge/licence-MIT-111827)](#licence)

[Install Toolkit](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js) · [Greasy Fork](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit) · [Release Pipeline](docs/RELEASE_PIPELINE.md) · [Changelog](CHANGELOG.md) · [Live Status](status/release-dashboard.json)

</div>

---

## Overview

MissionChief Map Command Toolkit expands the MissionChief UK map into a configurable operational command centre. It combines mission awareness, fleet monitoring, map utilities, responsive layouts, themed interfaces, payout presentations and persistent user settings in one userscript.

GitHub is the canonical source of truth. Greasy Fork remains the supported public installation and update platform.

## Release health

| Component | State |
|---|---|
| Canonical source | ✅ GitHub |
| Current validated version | `4.10.4` |
| Validation | ✅ Passed |
| Asset dependency audit | ✅ Passed |
| Distribution candidate | ✅ Built |
| Greasy Fork source sync | ✅ Configured |
| Greasy Fork release webhook | ✅ Releases only |
| Development Discord | `Mission-Chief-Dev` |
| Release Discord | `Mission-Chief` |
| Production release workflow | ✅ Installed |
| Immutable release bundle | ✅ Supported |

Machine-readable status: [`status/release-dashboard.json`](status/release-dashboard.json)

## Core capabilities

### Mission command

- Mission and alliance mission visibility controls
- Mission Age Watch with progress synchronization
- Critical mission workflows and clearing-state tracking
- Patient and transport monitoring
- Alliance payout overlays and completion history
- News-feed incident navigation

### Fleet awareness

- Vehicle code status panel
- Transport watcher and counts
- Unit-count overlays
- Focus and visibility controls
- Rapid map navigation to active incidents

### Map operations

- Coverage heat maps
- Landmark bookmarks and quick jumps
- Coverage rings and overlays
- Day, night and themed map presentation
- Desktop, tablet and iOS mobile layouts

### Presentation and themes

- Full interface themes including Map Command, Cyberpunk, Fallout, Umbrella and Factorio-inspired designs
- Configurable mission-completion presentations
- Hosted audio and visual assets
- Emergency flash effects and completion history
- Persistent UI state and cross-device settings export/import

## Install

Install or update through Greasy Fork:

**[Install MissionChief Map Command Toolkit](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)**

Other public links:

- [Script information](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
- [Version history](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit/versions)
- [Canonical changelog](CHANGELOG.md)

## Release pipeline

```text
Canonical GitHub source
        ↓
Validation and syntax checks
        ↓
Byte-identical .user.js and .txt build
        ↓
Versioned release bundle and SHA-256 manifest
        ↓
GitHub Release
        ↓
Greasy Fork release webhook
        ↓
Live-version verification
        ↓
Discord release post
        ↓
Dashboard and backup records
```

The production workflow does not announce a release until Greasy Fork is verified as serving the expected version. See the full [release-pipeline documentation](docs/RELEASE_PIPELINE.md).

## Repository structure

```text
src/             Canonical userscript source
dist/            Validated distribution candidate
docs/            Project and release documentation
status/          Machine-readable release and audit state
.github/         Validation, release and notification automation
*.mp3 / images   Stable public assets used by installed versions
```

## Asset stability policy

Existing public asset paths are treated as compatibility-critical. Images, sounds, manifests and theme resources already referenced by installed Toolkit versions are not renamed, relocated or deleted without a migration path.

## Development workflow

1. Update `src/MissionChief_Map_Command_Toolkit.user.js`.
2. Increase the userscript `@version`.
3. Add the matching entry to `CHANGELOG.md`.
4. Allow validation to complete.
5. Run **Release Toolkit** for an approved public release.

Routine commits are posted to `Mission-Chief-Dev`. Formal releases are posted separately to `Mission-Chief` only after Greasy Fork verification.

## Project principles

- **Release integrity:** source, metadata, changelog, manifest and tag must agree.
- **No premature announcements:** Discord follows successful distribution verification.
- **Compatibility first:** existing public asset URLs remain stable.
- **Recoverability:** every formal release contains checksums, a manifest and migration handover.
- **Clear separation:** development activity and public release notifications use different channels.

## Licence

The Toolkit is maintained by **Conroy1988** and distributed under the MIT licence. MissionChief trademarks, game content and third-party referenced material remain the property of their respective owners.

---

<div align="center">

**MissionChief Map Command Toolkit**  
GitHub-controlled releases · Greasy Fork distribution · Verified Discord announcements

</div>
