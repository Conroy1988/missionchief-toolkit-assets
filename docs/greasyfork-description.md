# MissionChief Map Command Toolkit

## v9.2.0 candidate — MissionChief UK Knowledge Link

A native MissionChief map command and operational-support userscript for Desktop, Tablet/iPad and iOS.

Version 9.2.0 adds **UK Intel** to every Operational Pressure Board requirement. Open it to see verified qualifying units, numeric MissionChief vehicle-type IDs, alternatives, crew ranges, training courses, academies, durations, trained-crew qualifiers and associated personnel from the MissionChief UK Guide. Unknown labels remain visible as **Catalogue Drift** with a review-before-submit report that contains no private player data. Guide intelligence loads only after the user asks for it, uses a schema-validated bounded cache and falls back to the bundled UK catalogue offline. Numeric vehicle recognition, custom callsigns, Tablet header clearance, settings persistence, readable and draggable Tablet controls and the Stuck button remain intact while preserving The One We Knew Before: MissionChief remains authoritative, navigation actions stay read-only and every retained Toolkit system keeps deterministic teardown.

### Retained native systems

- Mission Age map timers and shortcut `6`
- Mission Value
- Patient Transport Sweep using MissionChief’s native Discharge patient control
- Transport Watcher
- Unit Commitment
- Resource Gap
- Main-map Stuck overlay ON/OFF control
- Operational Pressure Board with shortcut `B`
- MissionChief UK Knowledge Link with verified units, crew, training and personnel
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

The Pressure Board allocates each available personal vehicle at most once across current personal and joined alliance mission demand. Select **UK Intel** beside a requirement for its read-only Guide dossier. The three public Guide collections are requested only when the user opens a dossier without a fresh cache or explicitly selects **Refresh Guide data**. On Tablet, the complete title, actions and dossier remain below native top chrome, with overflow contained inside the visible viewport. Custom callsigns cannot hide the underlying numeric vehicle capability, and missing coordinates are reported as partial evidence rather than zero availability. Focus, Open and Pin do not select or dispatch vehicles. The SITREP is posted only after the user selects Generate & Post.

Toolkit settings are retained in revisioned userscript storage and a compatible MissionChief page copy, with a previous good revision available for recovery. Financial and operational reports use the saved Discord webhook configured by the user. Settings exports can contain that webhook and should be treated as private.

Install stable: https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js
Source and releases: https://github.com/Conroy1988/missionchief-toolkit-assets
