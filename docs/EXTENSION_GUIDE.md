# Extension guide

[Install from the Chrome Web Store](https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc) · [Back to the project](../README.md)

## Installation

Install the Store edition, disable duplicate Toolkit copies, enable Toolkit in its popup and fully reload MissionChief UK. Pin the extension if you want quick access to its popup. Menu opens the workspace; Game Guide opens the TKB guide in another tab.

Store updates are delivered by the browser after Google approval. An extension version such as 1.2.5 and a bundled Toolkit core version such as 10.18.1 are separate identifiers. Report both when available. A pending submission is not yet an available update.

## Moving from the userscript

Use [the migration guide](MIGRATING_FROM_USERSCRIPT.md). Disable only this Toolkit script; other Tampermonkey scripts can remain. Do not run two Toolkit copies together. Export settings before removing an installation, and verify settings after the change.

## Operations

Open Operations and select a tool. **Back to Operations**, or the Operations sidebar entry, returns to the selection screen while preserving selections and running-task state.

### Home Response Builder

1. Choose a city/boundary, draw an area or set a point and radius. Selecting a city uses City boundary mode.
2. Choose spacing, a building limit and an allowed vehicle. The limit is a cap, not a target.
3. Refresh buildings and preview. Check spacing circles, existing-building counts and suitable land near roads.
4. Review the nearest dispatch centre, or choose another. Named gold markers can be selected on the map.
5. Optionally load saved icons or scan one building type. Saved icon catalogues are account-scoped in this browser.
6. Review costs and acknowledge dispatch-centre distances before starting. Watch progress and stage timings.

One-mile spacing normally fits more buildings than three-mile spacing. Existing buildings just outside the boundary can still exclude locations near its edge. Water checks use bundled mapped coastlines and major lakes; they do not establish road accessibility.

### Home Response Unit Switcher

Select the dispatch-centre scope, old vehicle type and desired type. Preview and select exact vehicles. Confirm permanent removal and the estimated Credit cost only after checking the list. Busy vehicles are skipped. A full shop can supply an estimate before removal, but the subsequent purchase requires a valid enabled Credit offer. Old vehicle names are not preserved.

### Hospital Upgrades

Choose eligible hospitals and the target level, from 1–30. Review the total and current balance. Each hospital uses a direct native target-level action, followed by verification. The total is not a series of separate intermediate-level clicks.

## Interrupted tasks

Keep the game tab open during operations. Use Pause when available. If a request fails or the tab reloads, use **Review & resume**: the tool checks what actually exists before repeating any action. Read the affected building's status. A created building, removed vehicle or successful purchase may already exist even if a later step failed. Avoid starting a duplicate plan while recovering.

## Troubleshooting

- **No Menu:** confirm the extension is enabled, the Toolkit toggle is on and you are on MissionChief UK; fully reload.
- **Duplicate UI:** disable old Toolkit userscripts and duplicate extension entries, then reload every game tab.
- **Slow operation:** record the scope/count, stage timings and exact stage that stalls. Game response time still limits purchases.
- **Credit warning:** capture the displayed account balance, estimated cost and exact error. Do not include account credentials.
- **Missing feature:** compare the installed extension version with the Store version; a test build or pending review may be newer.
- **Different settings:** Store, unpacked and mobile installs can use separate storage. Do not delete the previous installation until you have backed up what you need.

[Report a bug](../SUPPORT.md). Review screenshots and exports for secrets before sharing.
