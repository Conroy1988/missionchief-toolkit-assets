# Station Icon Copier operator and safety contract

Toolkit v10.11.1 provides **Dispatch → Station Icon Copier** for copying one already-uploaded station icon to an exact, operator-reviewed subset of owned stations.

MissionChief's native image workflow remains authoritative. The Toolkit reads owned buildings from MissionChief, downloads the selected source station's existing custom icon into browser memory, and uses each target station's current native building-edit form. It does not add an external image host, ask for a local upload, or retain image data in Toolkit storage.

## Operator workflow

1. Select **Load Stations**.
2. Choose one Dispatch Centre or **ALL DISPATCH CENTRES**.
3. Choose an owned **Source Station** that already shows the required custom icon.
4. Leave **Protect them (recommended)** selected unless existing custom icons must deliberately be replaced.
5. Select **Scan Matching**. The source station defines the exact native building type and its small/full classification automatically.
6. Review the source thumbnail, exclusion totals, existing-icon policy, and complete target list. Clear any target that should not change.
7. Select **Apply to Selected**, read the exact count and scope, then confirm.
8. Watch the per-station outcomes. **Stop** finishes the active request and its verification, then prevents another station from starting.

Changing the Dispatch Centre, source station, or existing-icon policy destroys the old queue. Apply remains disabled until a fresh scan binds a new queue to all three choices.

## Exact target rules

A station can enter the queue only when all of these are true:

- it is an owned station returned by MissionChief's building API;
- it is assigned to the selected Dispatch Centre, or to one of the currently loaded centres in **ALL DISPATCH CENTRES** mode;
- its native `building_type` is identical to the source station;
- its native `small_building` classification is identical to the source station;
- it is not the source station itself; and
- under the default policy, it has no existing custom icon.

Unassigned stations, stations outside the selected scope, other building types, and the full/small counterpart of the source type are excluded. A scan and an apply run are each capped at 2,000 targets.

## Existing custom icons

**Protect them (recommended)** is the default and excludes every station that already has a custom icon. Each target is checked again immediately before mutation; a station that gains an icon after the preview is skipped.

**Replace selected custom icons** is explicit overwrite mode. Existing custom-icon stations can enter the preview, remain individually selectable, and are named in the final confirmation. If a target's current rendered pixels already match the source, it is reported as **No change** without another upload.

## Native mutation safeguards

Before each upload, the Toolkit:

- fetches authoritative data for that exact target;
- rechecks station ID, Dispatch Centre, building type, small/full classification, name and coordinates against the preview;
- fetches `/buildings/{id}/edit` immediately before use;
- accepts exactly one same-origin POST form for `/buildings/{id}`;
- requires MissionChief's authenticity token, PATCH method override and exactly one `building[image]` file control; and
- constructs `FormData` from the current native form so unrelated current values are preserved, then replaces only `building[image]`.

The upload is sent sequentially with the selected 1–5 second delay. The browser creates the multipart boundary. There are no parallel writes and no blind retry.

## Source and result verification

The source must be a readable MissionChief PNG or JPEG no larger than 200×200 pixels. It is downloaded once per confirmed run and retained only in memory. A normal browser download is attempted first. When MissionChief returns the image from its CORS-restricted MissionChief upload host, the Toolkit uses an anonymous userscript request limited to the exact HTTPS host `leitstellenspiel.s3.amazonaws.com`; it sends no MissionChief cookies or account credentials and requests no wildcard host access.

Both the initial and final response URL must remain on that approved upload host. HTTP status, the 4 MB byte limit, PNG/JPEG response type, decode dimensions and rendered pixels are validated before the confirmation can lead to any station mutation. The same guarded path is used when comparing an existing target icon and verifying the saved result.

After each submitted upload, the Toolkit fetches fresh authoritative target data, proves the non-image identity and assignment fields are unchanged, downloads the saved custom icon, decodes it, and compares its dimensions and rendered pixel digest with the source. Only then is the target counted as **Updated**.

If a request was submitted but its response, authoritative record, or saved pixels cannot be verified, the target is marked **Error** and the complete run stops immediately. The Toolkit never retries that upload automatically because the first request may already have succeeded.

## Failure handling

- A target that changed before submission is skipped safely.
- An unavailable, malformed, external, or ambiguous native form is skipped before any write.
- An unapproved image host, an unsafe upload-host redirect or an invalid image response prevents the run from starting.
- A post-submit mismatch or unverifiable result triggers **SAFETY STOP**.
- Reload and rescan after fixing the reported condition; manually inspect the station named by an ambiguous submitted request before starting another run.

MissionChief documents its manual building-image flow and PNG/JPEG, 200×200 constraints in [How can I use my own graphics for buildings?](https://xyrality.helpshift.com/hc/en/23-mission-chief/faq/1980-how-can-i-use-my-own-graphics-for-buildings/?p=web).
