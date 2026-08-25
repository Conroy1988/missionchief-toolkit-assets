# Issue #704 — Alliance Courses

Toolkit v10.7.0 adds **Alliance Admin** as a top-level command section. It contains **Alliance Courses** and the relocated **Co-admin Patient Transport Sweep**.

Alliance Courses is a deliberate, bounded administrator workflow. It reads MissionChief's Alliance Buildings table, identifies buildings assigned to a selected day, maps each academy building name to one verified native course option, and submits ready courses sequentially. It does not bypass MissionChief permissions or classroom availability.

## Alliance building setup

Use one academy building for one course and include a day token as its own word. The recommended format is:

```text
<academy prefix> - <course name> - <capacity> - <day> - <sequence>
```

Examples:

```text
AD - Ambulance Officer - 6 - Sat - 1
AE - Drone Operator - 6 - Tuesday - 2
AF - ARF - 6 - Saturday - 1
AI - Coastal Search Advis - 6 - SAT - 1
```

Accepted day tokens are `SUN`, `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT` and their full English day names. Common Tuesday and Thursday abbreviations (`TUES`, `THUR`, `THURS`) are also accepted. Matching is case-insensitive and punctuation-insensitive.

The native academy icon is authoritative. These name prefixes are supported as a fallback:

| Prefix | Academy |
|---|---|
| `AD` | Ambulance Academy |
| `AE` | Police Academy |
| `AF` | Fire Academy |
| `AI` | Coastal / Rescue Academy |

Academy identity matters for crossover names. For example, `Drone Operator` resolves against the Fire, Police or Coastal / Rescue academy's own native course list; the Toolkit never assumes one academy's option value applies to another.

## Supported course mappings

The building-name text in the left column resolves to the current English MissionChief option in the right column. Optional words such as `Training` are accepted where the Toolkit catalogue declares them.

### Ambulance Academy

| Building name | Native course |
|---|---|
| Ambulance Officer | Ambulance Officer |
| Critical Care | Critical care |
| HART | HART Training |
| Midwifery | Midwifery Training |
| SORT | SORT Training |
| Tactical Command | Tactical Command Course |

### Police Academy

| Building name | Native course |
|---|---|
| Dog Handling | Dog handling |
| Drone Operator | Drone Operator Training |
| Firearms | Firearms training |
| Level 1 Public Order | Level 1 Public Order Training |
| Level 2 Public Order | Level 2 Public Order Training |
| Mounted Police | Mounted Training |
| Police Aviation | Police aviation |
| Police Inspector | Police Inspector Training |
| Police Medic | Police Medic Training |
| Police Search Advisor | Police Search Advisor Training |
| Police Sergeant | Police Sergeant Training |
| Roads Policing | Roads Policing Officer Training |

### Fire Academy

| Building name | Native course |
|---|---|
| ARF | Aircraft Rescue and Firefighting |
| Co-Responder | Co-Responder Training |
| Fire Drone Operator / Drone Operator | Drone Operator Training |
| Fire Lifeguard / Lifeguard | Lifeguard Training |
| Hazmat | HazMat |
| HVPT | High Volume Pump Training |
| Mobile Command | Mobile command |

### Coastal / Rescue Academy

| Building name | Native course |
|---|---|
| Cave Rescue | Cave Rescue Training |
| Coastal Air Rescue | Coastal Air Rescue Operations Training |
| Coastal Command | Coastal Command Training |
| Coastal Search Advis / Coastal Search Advisor | Coastguard Search Advisor Training |
| Dog Handling | Dog handling |
| Drone Operator | Drone Operator Training |
| Flood First Responder | Flood First Responder Training |
| Hovercraft Command | Hovercraft Commander Training |
| Jet Ski Handling | Jet Ski Handling |
| Lifeboat Operations | Lifeboat Operations Training |
| Lifeguard Training / Lifeguard | Lifeguard Training |
| Mud Rescue | Mud Rescue Training |
| Rope Rescue | Rope Rescue Training |
| SAR Search Management | Search Management Training |

## Running Alliance Courses

1. Open **Toolkit → Administration → Alliance Courses**.
2. Select **Today** or a specific building day.
3. Select the alliance sharing duration. The default is **1 day**; **1 hour**, **12 hours** and **2 days** are also supported.
4. Select the delay between courses. The default is **1.5 seconds**.
5. Choose **Scan Courses** and review Ready, Busy and Unmapped totals.
6. Correct unexpected unmapped names before proceeding.
7. Choose **Start Courses**. The Toolkit performs another fresh scan and shows a confirmation containing the exact ready count, day and sharing duration.
8. Confirm only when the displayed plan is correct. Use **Stop** to finish the active request without starting another building.

For every ready building, the Toolkit:

1. Loads the same-origin native building page.
2. Requires the exact `/buildings/<id>/education` form and authenticity token.
3. Finds exactly one course option by its normalised visible label. Opaque option values are discovered from the current form and are never hard-coded.
4. Selects the largest classroom option currently exposed by MissionChief.
5. Selects the configured alliance duration and requires the native `0 Credits` option.
6. Posts `Educate` through the native form.
7. Requires the returned schooling table to contain more matching course evidence than it did before submission.

## Safety boundaries

- Native Admin, Co-Admin or Alliance Educator access is required. The Toolkit does not infer or elevate roles.
- A row is Ready only when MissionChief exposes its green **Start a new training course** action.
- Full classrooms, missing permissions and otherwise unavailable buildings are counted as Busy / unavailable and are not opened.
- Unknown academy/course combinations are Unmapped. Ambiguous text is never guessed.
- A maximum of 150 day-matched buildings is inspected in one scan and a maximum of 100 ready buildings is started in one run.
- Submissions are sequential and have a 12-second request timeout.
- A failed or unverified submission is never retried automatically, because MissionChief may have accepted it even if the response could not be verified.
- No background polling, scheduled automation, broad observer or automatic daily run is added. Scan and Start are manual actions.

## Troubleshooting

| Result | Meaning | Action |
|---|---|---|
| Ready | The day, academy, course name and native green action all matched. | Review and start when correct. |
| Busy / unavailable | The name mapped, but MissionChief did not expose the green course action. | Check classrooms and your current native permissions. |
| Unmapped | Academy identity or the course name did not resolve to exactly one supported mapping. | Compare the building name with the tables above. Preserve a separate day token. |
| Skipped | The building was ready during the list scan, but its native form no longer matched the verified contract. | Inspect the building manually; do not assume a course was created. |
| Error | A request failed or the returned page did not prove a new matching course. | Inspect the building manually. The Toolkit intentionally does not retry. |

If MissionChief adds or renames an education option, report the academy type, building name and visible native course label without including account, alliance or token data.
