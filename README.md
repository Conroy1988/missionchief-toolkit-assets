# MissionChief Map Command Toolkit

[![Greasy Fork](https://img.shields.io/badge/Greasy%20Fork-Install-670000?logo=tampermonkey&logoColor=white)](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
[![Release Pipeline](https://img.shields.io/badge/Release%20Pipeline-v2%20Foundation-2563eb)](status/release-dashboard.json)
[![Platform](https://img.shields.io/badge/MissionChief-UK-0f766e)](https://www.missionchief.co.uk/)
[![Licence](https://img.shields.io/badge/Licence-MIT-16a34a)](#licence)

A feature-rich MissionChief userscript providing an expanded map command interface, operational overlays, mission monitoring, payout presentation, responsive desktop/tablet/mobile layouts, themed interfaces and supporting media assets.

> **Migration status:** GitHub is being established as the canonical source of truth. Greasy Fork remains the public installation and update platform. Existing public asset paths are being preserved to avoid breaking installed versions.

## Release dashboard

| Component | Current state |
|---|---|
| Canonical source | GitHub migration in progress |
| Public distribution | Greasy Fork |
| Development notifications | `Mission-Chief-Dev` |
| Release notifications | `Mission-Chief` |
| Existing Greasy Fork monitor | Active during migration |
| Validation pipeline | Foundation stage |
| Automated GitHub releases | Planned |
| Automated backups | Planned |

Machine-readable status: [`status/release-dashboard.json`](status/release-dashboard.json)

## Toolkit highlights

- Mission and alliance visibility controls
- Mission Age Watch and critical mission workflows
- Alliance payout overlays and completion history
- Vehicle code status and transport monitoring
- Coverage heat maps, bookmarks and map jumps
- Desktop, tablet and iOS mobile modes
- Multiple complete interface themes
- Configurable payout presentations and hosted audio
- Import/export settings and persistent UI state
- MissionChief-specific performance and usability improvements

## Distribution

The supported public release remains available through Greasy Fork:

- [View the script](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit)
- [Install or update](https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js)
- [Version history](https://greasyfork.org/en/scripts/586018-missionchief-map-command-toolkit/versions)

## Repository role

This repository currently serves several connected purposes:

1. Hosting stable images, theme packages and audio used by existing Toolkit installations.
2. Running the current Greasy Fork monitoring and Discord notification automation.
3. Becoming the canonical source, validation and release system for future Toolkit versions.
4. Providing release-state, documentation and backup records.

### Asset stability policy

Existing public files will not be renamed, moved or deleted until every reference has been audited. New organisation will be introduced alongside current paths first. Compatibility takes priority over cosmetic restructuring.

## Release Pipeline v2

The planned controlled release path is:

```text
Canonical userscript in GitHub
        ↓
Automated validation
        ↓
Version and changelog verification
        ↓
GitHub tag, release and immutable backup
        ↓
Greasy Fork synchronisation
        ↓
Greasy Fork version verification
        ↓
Discord release announcement
```

Routine development pushes are routed to the development channel. Verified public releases are routed separately to the release channel.

## Project structure

The repository is being migrated incrementally. Planned additions include:

```text
src/          Canonical userscript source
dist/         Validated public release files
status/       Release dashboard state
docs/         Project and user documentation
backups/      Release manifests and migration records
.github/      Validation, release and notification automation
```

Current media and theme paths remain unchanged during this process.

## Development

The project is maintained by **Conroy1988** for the MissionChief UK community. Release automation is designed to prevent mismatched versions, repeated changelogs, incomplete backups and premature Discord announcements.

## Licence

The Toolkit code is intended to remain available under the MIT licence. Individual third-party references, game trademarks and externally hosted materials remain the property of their respective owners.

---

**MissionChief Map Command Toolkit** · GitHub-controlled releases · Greasy Fork distribution
