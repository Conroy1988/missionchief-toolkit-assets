# Issue #706 — Dispatch Recruitment

Toolkit v10.8.0 adds **Dispatch → Dispatch Recruitment**, a deliberate bulk editor for stations assigned to one Dispatch Centre or every loaded Dispatch Centre in a single plan.

It updates two native MissionChief station settings:

- **Hiring Phase:** Off, 1 day, 2 days, 3 days or Automatic.
- **Personnel (Desired):** a whole number from 0 to 10,000.

The Toolkit discovers the player's current Dispatch Centres and MissionChief's current building-type options from the native **New Building** page. Station types are not hard-coded, so new game types can appear in the filter without requiring a Toolkit catalogue update.

## Running Dispatch Recruitment

1. Open **Toolkit → Dispatch → Dispatch Recruitment**.
2. Choose **Load Dispatch Centres**.
3. Select one Dispatch Centre, or choose **ALL DISPATCH CENTRES**, then choose **Scan Stations**. MissionChief's page is an assignment matrix containing each row's active native centre. A single-centre scan admits only exact matches; the all-centres scan admits exact assignments belonging to any centre in the freshly loaded catalogue and deduplicates stations by ID.
4. Review the editable, unavailable and station-type totals.
5. Leave every native station-type filter selected, or narrow the preview to Fire Stations, Police Stations, Ambulance Stations or any other types returned by MissionChief.
6. Use **Select All Filtered**, **Clear Filtered** and the station checkboxes to create the exact target set.
7. Choose the Hiring Phase and enter Personnel (Desired).
8. Choose **Apply to Selected** and review the confirmation showing the Dispatch Centre scope, exact station and centre counts, types and both requested values.
9. Confirm to start. **Stop** finishes the active request and prevents another station from starting.

All editable stations are selected after a scan. A disabled type filter removes that type from the current target plan without discarding its station checkboxes; re-enabling the type restores the prior per-station selection. Select/Clear affects only stations visible under the active type filters.

For one centre, the scan summary separates **Assigned here**, **Other centres** and **Unavailable**. For **ALL DISPATCH CENTRES**, it shows **Assigned**, **Selected**, **Centres** and **Unavailable**, and each station row names its centre. A missing or ambiguous native assignment marker is treated as unavailable rather than guessed. An assignment not present in the freshly loaded catalogue is excluded and explained.

## Native action contract

For every selected station, the Toolkit:

1. Reads the active native Dispatch Centre assignment on every matrix row and admits only exact matches to the selected centre, or exact assignments belonging to the freshly loaded catalogue for **ALL DISPATCH CENTRES**.
2. Stores each admitted station's exact centre, then loads `/api/buildings/<id>` before mutation and requires the station still to belong to that scanned Dispatch Centre and retain the scanned native building type.
3. If Personnel (Desired) differs, loads the station's native **Edit** endpoint and requires the exact same-origin `personal_count_target_only=1` PATCH form, authenticity token, number input and Save control.
4. If Hiring Phase differs, loads the station's native recruitment page and requires the exact same-origin native action for Off, 1 day, 2 days, 3 days or Automatic.
5. When an active phase must change, uses the exposed Cancel action first, then reloads the page and requires the requested native action. If that action is unavailable, it restores the original phase when MissionChief exposes the restoration action and reports a safe skip.
6. Submits one station at a time with the configured delay.
7. Reloads authoritative building data and requires both `hiring_phase`/`hiring_automatic` and `personal_count_target` to match the confirmed plan.

An already matching station is reported as **No change**. A moved station, changed building type, missing edit form, unavailable Automatic action or changed native control is skipped without guessing. A failed or unverified mutation is reported as an error and is never retried automatically.

The Toolkit does not use coin or credit recruitment endpoints, bypass premium access, change stations outside the confirmed snapshot, poll in the background or start work merely because the Dispatch section was opened.

## Limits and compatibility

- A scan and apply run are bounded to 2,000 deduplicated stations, including **ALL DISPATCH CENTRES** runs.
- Personnel (Desired) accepts 0–10,000 because the native form currently exposes no smaller maximum.
- Automatic recruitment works only when MissionChief exposes its native Automatic action for that station and account.
- The workflow is user-triggered and uses no persistent observer, timer or polling loop.
- The same selection and safeguards are used on Desktop, Tablet and iOS. Mobile checkboxes and station rows retain touch-safe sizing.

If MissionChief reports unavailable rows, inspect them before applying. They are never placed in the mutable queue.
