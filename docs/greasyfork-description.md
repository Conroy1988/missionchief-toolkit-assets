# MissionChief Map Command Toolkit

## v9.1.3 candidate — Tablet Pressure Board header clearance

A native MissionChief map command and operational-support userscript for Desktop, Tablet/iPad and iOS.

Version 9.1.3 keeps the Operational Pressure Board fully below MissionChief's fixed navigation bar in Tablet mode. Its top edge is resolved from the live map workspace and visual viewport whenever the board opens, the viewport changes or the device rotates, while its maximum height is reduced to the remaining safe space. Numeric UK vehicle recognition, custom callsigns, settings persistence, the readable and draggable Tablet menu, and the Stuck control remain intact while preserving The One We Knew Before: MissionChief remains authoritative, navigation actions stay read-only and every retained Toolkit system keeps deterministic teardown.

### Retained native systems

- Mission Age map timers and shortcut `6`
- Mission Value
- Patient Transport Sweep using MissionChief’s native Discharge patient control
- Transport Watcher
- Unit Commitment
- Resource Gap
- Main-map Stuck overlay ON/OFF control
- Operational Pressure Board with shortcut `B`
- Evidence-ordered Top Actions, Fleet Conflicts, reserve risk and transport pressure
- Manual mention-safe Operational SITREP through the saved Discord webhook
- Incident Command Wire
- Vehicle Code Status
- Custom Vehicle Badges
- Auto-load all vehicles
- Coverage rings and Smart Bookmark Labels
- Alliance Credits and financial intelligence
- Payout presentations and Economy Mode
- Eight complete interface systems, including The Godfather
- Desktop, Tablet and iOS Mobile Mode

The Pressure Board allocates each available personal vehicle at most once across current personal and joined alliance mission demand. On Tablet, the complete title, SITREP, refresh and close controls remain visible below native top chrome, with overflow contained inside the visible viewport. Custom callsigns cannot hide the underlying numeric vehicle capability, and missing coordinates are reported as partial evidence rather than zero availability. Focus, Open and Pin do not select or dispatch vehicles. The SITREP is posted only after the user selects Generate & Post.

Toolkit settings are retained in revisioned userscript storage and a compatible MissionChief page copy, with a previous good revision available for recovery. Financial and operational reports use the saved Discord webhook configured by the user. Settings exports can contain that webhook and should be treated as private.

Install stable: https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js
Source and releases: https://github.com/Conroy1988/missionchief-toolkit-assets
