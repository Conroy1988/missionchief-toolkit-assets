# Issue #732 — Station Icon Consistency Manager

Toolkit v10.12.0 upgrades the Station Icon Copier from a single-scope copy queue into a multi-centre consistency workflow. The existing native-form, sequential-write and post-save verification controls remain unchanged.

## Operator workflow

1. Open **Dispatch → Station Icon Copier** and select **Load Stations**.
2. Tick one or more Dispatch Centres, or use **Select All Centres**.
3. Choose a source station that already uses the desired custom icon. Its exact native building type and small/full classification define the comparison group.
4. Choose a repair policy:
   - **Fill default icons only (safest)** never overwrites an existing custom icon.
   - **Fix inconsistencies only (pixel verified)** includes default icons and custom icons whose decoded pixels are proven to differ from the source.
   - **Replace all selected custom icons** preserves the explicit broad replacement workflow.
5. Select **Scan Matching**. The Toolkit downloads the source once for the audit, checks all same-type custom icons sequentially, and shows the overall score plus a per-centre breakdown.
6. Review the eligible stations, adjust their checkboxes if required, then select **Apply to Selected** and approve the native-write confirmation.

Changing the centre selection, source station or policy invalidates the scan. Stop can end either an audit or an apply run after the active request finishes.

## Consistency definition

The score denominator contains the source and every owned station in the selected centres with the same exact native building type and the same small/full classification.

- The source is consistent after its image is decoded successfully.
- A custom icon is consistent only when its decoded width, height and rendered pixel digest match the source.
- A default or missing icon is inconsistent.
- A custom icon that cannot be downloaded, decoded or read at pixel level is unverified. Unverified stations count against the score and are never selected automatically by inconsistency-only mode.

URL equality and compressed file-byte equality are not treated as the consistency result. A scan-local URL cache retains only image signatures, not target image blobs, and avoids downloading an identical URL more than once.

## Write safeguards

Apply re-downloads the source and requires its pixels to match the scanned source signature before the first write. Every target is then freshly loaded and checked against the scanned station identity, Dispatch Centre, native type, small/full state, name and coordinates.

In inconsistency-only mode, a current custom icon must still match its audited pre-write pixel signature. If it changed, became unreadable, or appeared on a target that was default during the scan, the station is skipped unless it already matches the source. This prevents the Toolkit from overwriting an icon that was not part of the reviewed audit.

Writes continue to use the station's exact current MissionChief edit form, preserve unrelated native fields, upload one station at a time, and pixel-verify the saved icon before continuing. An ambiguous submitted write stops the whole run and is never retried automatically. Successful updates and already-matching no-ops move their stations to consistent immediately, so the visible score improves without another scan.

## State migration

The saved single `dispatchId` preference is migrated to the `dispatchIds` array. A legacy **all** value expands to the complete native Dispatch Centre catalogue on the next load. Invalid or removed centres are discarded. An empty selection remains empty so the Toolkit never silently expands an operator-cleared scope.
