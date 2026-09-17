# Extension guide

[Install from the Chrome Web Store](https://chromewebstore.google.com/detail/lmnojpchebgcochdfnfjmnficicnaaoc) · [Back to the project](../README.md)

## Installation

Install the Store edition, disable duplicate Toolkit copies, enable Toolkit in its popup and fully reload MissionChief UK. Pin the extension if you want quick access to its popup. Menu opens the workspace; Game Guide opens the TKB guide in another tab.

Store updates are delivered by the browser after Google approval. An extension version such as 2.0.0 and a bundled Toolkit core version such as 10.18.1 are separate identifiers. Report both when available. A pending submission is not yet an available update.

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

## Toolkit 2.0 workflows

### Vehicle Purchaser

Select a station type and dispatch-centre scope, scan live offers and free bays, then select stations and quantities. Review Credits, Coins and any preset extension cost before confirming. The ambulance preset can add and complete the Mass Casualty extension where required; its Coin allowance is part of the review. Keep the owning game tab open and verify interrupted purchases before resuming.

### Building Level-Up, Expansions and Complete Builder

Scan eligible buildings and choose the native target level or missing extension. Review prerequisites, exclusions and available currency. Use **Purchase Selected** for the reviewed selection. **Complete Builder** shows construction already in progress, remaining times and available Coin completion offers; its confirmation includes the selected total.

### Staff Training

Choose station type, dispatch scope and training before scanning. Expand rosters or select completely untrained staff in batches. **Train X per station** selects up to X eligible, completely untrained staff from each selected station. **Top up to X** counts existing chosen qualifications and selects only the shortfall. It reports shortages and uncertain rosters; selecting staff does not start a course.

Use Own Academies, Alliance Academies or Combined to find suitable classrooms. Combined prioritises owned capacity; alliance allocations use available matching courses. Review capacity and paid classes before enrolment. **Show In-Training** finds active courses. Coin completion affects the whole class, including other participants; review the full cost before using Complete ALL.

### Account and reporting

Discord sign-in is optional. Cloud preferences load first on sign-in or reconnection; the Account page shows connection state, countdown and sync progress. Use the same linked account on each device. Supported preferences sync; game cookies, running jobs, confirmations and finance archives do not. Your chosen reporting webhook is saved separately for cross-device use. Testing its connection sends no message.

### Finance and time

Use selected periods, comparisons and daily summaries before starting a deeper ledger scan. Timestamp-based reporting uses Europe/London, including GMT/BST changes. Native daily game totals retain UTC boundaries and are labelled. Emergency Payout Flash has 16 styles with separate artwork/audio selection, presentation size and placement, effects controls and previews.

### Dashboards

Awards, Tasks and Events, player profiles, alliance chat, inbox and Dispatch dashboard add search, progress and summary views while retaining supported native controls. Some searches cover only loaded data or the current page. Open the original-page option where offered.

[Complete 2.0 feature reference](FEATURES-2.0.md) · [All release changes](../extension/CHANGELOG.md)
