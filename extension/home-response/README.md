# Home Response Builder development

The pure planner and checkpointed serial execution core are independently tested.
UK type 22 and all 14 vehicle options were inspected in the signed-in native game
on 2026-09-13. No game purchases were made during development.

The native adapter uses native forms and Credit links. The user reported successful
live builder operation during the 0.23.x iteration and requested full store release.
Do not run arbitrary purchases as tests. Staff/training readiness remains a user check.

Distances are straight-line separation, not driving time or guaranteed coverage.
Boundary holes and excluded areas are honoured. Geographic candidates still need
road/accessibility review. Unknown mutation results pause and never blindly retry.

Source references: live /buildings/new and an owned type-22 vehicle market;
LSS-Manager/LSSM-V.4 src/i18n/en_GB/buildings.ts and vehicles.ts were cross-checked,
but the native shop supersedes its older summary.

## Rebuild and verify

Run `npm ci --prefix extension/home-response`, then
`node --test extension/home-response/*.test.mjs` and
`python3 extension/build-recovered.py` from the repository root.
The build verifies every recovered file hash before applying the new module.
That command reproduces the 0.23.14 test package. For the full 1.0.0 store package,
run `python3 extension/prepare-store-release.py`. Store listing copy lives in
`extension/store/`. Submission state must be checked in the publisher dashboard.

## Live validation notes (original test checklist)

- Load on desktop and Orion; confirm city-search provider availability and map controls.
- Choose one intended location, a vehicle without additional training and a suitable
  dispatch centre. Review the displayed name, position and Credit budget before confirming.
- Verify exactly one building and its selected vehicle, then test pause/resume on a small batch.
- A request with an unknown result is deliberately blocked from retrying; inspect the
  corresponding building/vehicle in the game. Resume now checks the complete owned-building catalogue for the exact name, type and coordinates. It recovers a unique match without another building request; vehicle recovery requires the selected vehicle in that exact building. Unknown or conflicting records remain paused.
- Road snapping, reuse of empty Home Responses and automatic staff training are not included.
  Placement is geometric and uses explicit exclusions and editable markers for review.

## 0.23.1 recovery fix

A live inspection confirmed the reported first building existed with zero vehicles.
Construction success no longer depends on a /buildings/:id redirect. Legacy 0.23.0
creating checkpoints recover their building cost from the saved reservation.
Opening the builder restores the saved account plan directly. The original error
is retained, and new intents record individual costs before submitting requests.
23 regression tests cover recovery, no duplicate purchases and cost accounting.
No live purchase was made while fixing the issue.

## 0.23.7 — location gap search

Corrects degree-to-mile grid spacing so adjacent candidates are not discarded by the exact distance check. Additional offset passes look for gaps without relaxing minimum spacing, land or exclusion checks. Scanline intersections are cached between passes. This is a deterministic proposal, not an optimal-packing guarantee.

The preview distinguishes existing buildings inside the area from the account-wide catalogue, offers spacing-circle overlays and explains sampled-position exclusions. Radius applies only in Point and radius mode. Changing area settings clears stale proposals. The cap remains 1000; Chrome Store submission remains deferred.

Validation: 41 automated checks, including gap recovery, adjacent grid distances, water, queue recovery and area controls. Real account placement counts and phone acceptance still require testing.

## 0.23.8 — city defaults and finer gap search

Selecting a search result always restores City boundary. A result without a polygon leaves the area unset and explains the explicit radius/drawing alternatives. The default on opening remains City boundary. Location counts and diagnostics now sit above the map; optional circles show both existing and proposed minimum spacing, with a compact checkbox.

Gap search refines to quarter-row/column offsets, preserving already accepted sites and all distance/land checks. This does not guarantee optimal packing or a higher count for every area. Video showed sparse three-mile Wigan proposals; account coordinates were not supplied, so the precise live count was not reproduced. 43 automated checks pass, including narrow dry gaps and city selection after radius mode. Chrome Store review remains untouched.

## 0.23.9 — dispatch centres ready on opening

The builder preloads the building catalogue independently of saved-job recovery. Preview refresh supersedes an older preload so delayed responses cannot overwrite fresher records. Dispatch options sort by straight-line miles from the area's bounding-box centre; without an area they sort by name. Unknown coordinates remain selectable but cannot be ranked geographically or plotted. Existing selection, including Unassigned, is preserved. Named gold markers use text-only tooltips and can select a centre when construction is idle.

Validation: 46 automated checks, including preload before preview, nearest-first ordering, selection preservation, and safe map labels. Chrome Store review remains untouched.

## 0.23.10 — remembered icon catalogues and type scans

Icon scans persist in same-origin browser storage, scoped by verified game account and selected building type. The last scanned type is restored on opening. Saved results include source references and counts, not downloaded image bytes; thumbnails still load normally. A manual refresh rechecks images, filters records by type before downloading, and replaces that scope's saved catalogue. Game catalogue metadata is still loaded to obtain buildings/types. Existing source and target verification during copying is retained. Storage failures are reported without discarding scan results. Clearing site storage removes the saved catalogues.

Validation: 49 tests including cache reuse without catalogue/image scanning, account and type isolation, type-filtered image requests, storage failure, and UI restoration. Chrome Store review remains untouched.

## 0.23.11 — capped plans sample the whole area

The Bristol video shows a maximum of 20 and the preview explicitly reaching it. Previous south-to-north traversal therefore placed all 20 near the bottom before stopping. Cell traversal now uses a deterministic bit-reversed order to sample distant parts of the grid early, with cached scanline geometry and throttled progress updates. Caps, exact spacing, water and exclusion checks remain enforced. This improves distribution; it does not guarantee optimal coverage or packing. The selected maximum remains unchanged.

Validation: 50 automated tests, including a capped 20-site fixture spanning all four quadrants, water constraints and minimum spacing. Chrome Store review remains untouched.

## 0.23.12 — automatic dispatch assignment with acknowledgement

Selecting an area automatically chooses the nearest centre with known coordinates. Manual choices are preserved for that area across preview/settings updates; changing the area resets the automatic choice. Before build or resume, the current building catalogue verifies the saved job's actual dispatch ID. The confirmation names that centre, gives the area-centre distance and planned building distance range, and explicitly requires acknowledgement. Distances are straight-line. Unassigned is explicitly disclosed; missing assigned centres block continuation.

Validation: 52 automated checks, including auto-selection, manual override preservation, confirmation content and cancellation without purchases. Chrome Store review remains untouched.

## 0.23.13 — choose an area directly on the map

Select area on map is an explicit mode; City boundary remains the default. A click performs city/town-level reverse lookups, retaining only UK polygon boundaries containing that point and removing duplicate results. One result is selected directly; multiple results appear in Search results for user selection. The normal boundary selection path handles map fitting, preview invalidation and nearest dispatch selection. No radius fallback is automatic. Marker clicks do not trigger area selection; late lookup results cannot replace a newer selection.

Search and reverse requests share a serial, rate-limited, in-dialog cache. API references: https://nominatim.org/release-docs/latest/api/Reverse/ and https://operations.osmfoundation.org/policies/nominatim/ . Returned choices depend on mapped data and are not an exhaustive list of every administrative boundary.

Validation: 55 automated tests, including polygon containment, duplicate/foreign/point rejection, request spacing/cache, and map-click selection through the UI. Real browser lookup acceptance still requires testing. Chrome Store review remains untouched.

## 0.23.14 — faster sequential construction

Native purchase checks validate account identity and balance themselves, so the queue omits two redundant standalone account reads on the normal purchase path. Recovery and image-only resume retain their standalone identity check; other adapters retain the old behavior. Building catalogue/form/account reads run together; vehicle form/account/current-vehicle reads run together. The image copier reuses the target record just verified by the builder while retaining scope, form, post-upload and pixel checks. This removes one duplicate icon-target read.

Purchase writes remain sequential with durable intent and authoritative completion checks. Whole-catalogue receipt verification remains where no proven equivalent targeted response has been established. The icon settling delay is retained. Per-item cumulative stage timings cover checks, build/receipt, vehicle purchase/verification, recovery and icon copy, including failed attempts. Live speedup is unmeasured until phone testing.

Validation: 59 tests pass, including concurrent reads, changed-account rejection, full-garage rejection, durable purchase recovery, timing records and retained icon post-upload validation. Chrome Store review remains untouched.

## 1.0.0 — full release packaging

Promotes approved 0.23.14 functionality with stable metadata, refreshed bundled help,
release notes, privacy disclosures and store copy. No gameplay logic or permissions
changed. 59 automated tests and all packaged JavaScript syntax checks passed.
Latest speed improvement remains unmeasured. Submission requires the authenticated
Chrome Web Store dashboard; do not infer approval from package creation.
