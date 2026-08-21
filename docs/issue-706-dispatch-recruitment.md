# Issue #706 — Dispatch Recruitment

Toolkit v10.10.0 provides **Dispatch → Dispatch Recruitment**, a deliberate bulk editor for one exact native building type or every type across one Dispatch Centre or every loaded Dispatch Centre in a single plan.

It updates two native MissionChief station settings:

- **Hiring Phase:** Off, 1 day, 2 days, 3 days or Automatic.
- **Personnel (Desired):** a whole number from 0 to 10,000.

The Toolkit discovers the player's current Dispatch Centres and MissionChief's current building-type options from the native **New Building** page. Station types are not hard-coded, so new game types can appear in the filter without requiring a Toolkit catalogue update.

## Running Dispatch Recruitment

1. Open **Toolkit → Dispatch → Dispatch Recruitment**.
2. Choose **Load Dispatch Centres**.
3. Select one Dispatch Centre or choose **ALL DISPATCH CENTRES**.
4. Choose **ALL BUILDING TYPES** or one exact native type such as Fire Station, Police Station or Ambulance Station. The list is supplied by MissionChief and therefore includes every type exposed for the current game region.
5. Choose **Scan Stations**. A single-centre scan loads that centre's native Buildings matrix and admits only exact centre/type matches. An all-centres scan loads every centre-specific matrix in sequence, shows `Scanning 12 of 38 · Centre name` progress, then globally deduplicates exact assignments belonging to the freshly loaded catalogue before applying the selected type scope.
6. Review the editable, unavailable and station-type totals.
7. Leave the returned station-type filters selected or narrow an **ALL BUILDING TYPES** preview further.
8. Use **Select All Filtered**, **Clear Filtered** and the station checkboxes to create the exact target set.
9. Choose the Hiring Phase and enter Personnel (Desired).
10. Choose **Apply to Selected** and review the confirmation showing the Dispatch Centre scope, exact station and centre counts, types and both requested values.
11. Confirm to start. **Stop** finishes the active request and prevents another station from starting.

All editable stations are selected after a scan. A disabled type filter removes that type from the current target plan without discarding its station checkboxes; re-enabling the type restores the prior per-station selection. Select/Clear affects only stations visible under the active type filters.

Every successful scan is bound to both the selected Dispatch Centre scope and the selected **Building Type**. Changing either control immediately destroys the prior queue, clears its selections and leaves **Apply to Selected** disabled until the replacement scan completes. A saved native type that is no longer returned by MissionChief safely falls back to **ALL BUILDING TYPES** rather than guessing a replacement.

An **ALL DISPATCH CENTRES** result becomes selectable only after every loaded centre matrix returns successfully and is verified as the exact native Buildings page requested. A failed, timed-out, redirected or malformed centre response discards the complete scan, leaves **Apply to Selected** disabled and reports the centre failure. Conflicting assignment or building-type evidence for the same station across matrices is also rejected instead of guessed.

For one centre, the scan summary separates **Assigned here**, **Other centres** and **Unavailable**. For **ALL DISPATCH CENTRES**, it shows **Assigned**, **Selected**, **Centres** and **Unavailable**, and each station row names its centre. Native **No control center** / `- None -` rows are reported separately as **Unassigned** and never enter either mutation queue. A missing or ambiguous native assignment marker is treated as unavailable rather than guessed. An assignment not present in the freshly loaded catalogue is excluded and explained.

## Native action contract

For every selected station, the Toolkit:

1. Loads the selected centre's native matrix, or every freshly loaded centre matrix for **ALL DISPATCH CENTRES**, then reads each row's active native assignment and admits only exact centre and selected building-type matches after the complete scan succeeds.
2. Stores each admitted station's exact centre, then loads `/api/buildings/<id>` before mutation and requires the station still to belong to that scanned Dispatch Centre and retain the scanned native building type.
3. If Personnel (Desired) differs, loads the station's native **Edit** endpoint and requires the exact same-origin `personal_count_target_only=1` form, its current native PUT or PATCH override, authenticity token, number input and Save control. It constructs a strict allow-listed payload, sends the native CSRF and AJAX headers and refuses any additional `building[...]` field.
4. Applies Personnel (Desired) independently first and performs bounded authoritative building read-back until the requested target is visible, while never repeating the mutation. Exact Dispatch Centre and building type remain mandatory on every read.
5. If Hiring Phase differs, loads the station's native recruitment page and requires the exact same-origin native action for Off, 1 day, 2 days, 3 days or Automatic.
6. When an active phase must change, uses the exposed Cancel action first, then reloads the page and requires the requested native action. If that action is unavailable, it restores the original phase when MissionChief exposes the restoration action and reports a safe partial result without undoing an already verified Personnel (Desired) change.
7. Rechecks authoritative assignment, building type and Hiring Phase after the native Hiring action, then submits the next station only after the configured delay.

An already matching station is reported as **No change**. A moved station, changed building type, missing edit form, unavailable Automatic action or changed native control is skipped without guessing. Safe one-field success is reported as **Partial**. If MissionChief reports an assignment/type change after a mutation, or cannot authoritatively verify a submitted mutation, the entire run stops immediately and no automatic retry is made.

The Toolkit does not call `/leitstelle-set/`, include `building[leitstelle_building_id]` in a mutation payload, use coin or credit recruitment endpoints, bypass premium access, change stations outside the confirmed snapshot, poll in the background or start work merely because the Dispatch section was opened.

## Limits and compatibility

- A scan and apply run are bounded to one queue of 2,000 deduplicated editable stations. For a specific **Building Type**, unselected types do not consume that limit; for **ALL BUILDING TYPES**, the limit remains global across every selected Dispatch Centre. Duplicate centre-matrix rows never consume it twice.
- Personnel (Desired) accepts 0–10,000 because the native form currently exposes no smaller maximum.
- Every valid Personnel (Desired) keystroke updates saved Toolkit state immediately, so another UI refresh or main-page change cannot restore an older value before blur.
- Automatic recruitment works only when MissionChief exposes its native Automatic action for that station and account.
- The workflow is user-triggered and uses no persistent observer, timer or polling loop.
- The same selection and safeguards are used on Desktop, Tablet and iOS. Mobile checkboxes and station rows retain touch-safe sizing.

If MissionChief reports unavailable rows, inspect them before applying. They are never placed in the mutable queue.
