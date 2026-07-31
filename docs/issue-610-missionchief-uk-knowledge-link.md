# Issue #610 — MissionChief UK Knowledge Link

## Authority

MissionChief remains authoritative for each live outstanding requirement and its
quantity. The Toolkit's bundled UK requirement catalogue provides immediate and
offline numeric vehicle-type matching. The TKB MissionChief UK Guide supplies
the enriched unit, staffing, training, personnel and evidence records.

Guide data never changes a live requirement, `Still Needed` value, fleet
allocation or dispatch state.

## Interaction

Every Operational Pressure Board fleet row exposes a contextual intelligence
action: **UK Intel** for known capabilities and **Unknown · Report** for
catalogue drift. The dossier shows:

- qualifying units and MissionChief vehicle-type IDs;
- exact, counts-as and alternative capability evidence;
- minimum and maximum crew;
- course, academy, duration and trained-crew qualifiers;
- associated personnel dossiers;
- guide data version, verification and checked date;
- direct Guide links for capability, unit and personnel records.

Unknown labels remain visible as **Catalogue Drift**. `Report requirement` opens
the existing `Mission Info Missing` issue form for player review; it never
submits an issue automatically.

## Network and cache

The feature uses only:

`https://tkb-gaming.scot/games/missionchief/guides/api/v2/`

Capability, unit and personnel collections load only after the player opens a
dossier. Responses are schema- and size-validated, reduced to bounded fields and
stored in Tampermonkey storage. The fresh lifetime is six hours and the stale
recovery lifetime is seven days.

Failure is non-blocking: a valid stale copy remains available, otherwise the
bundled numeric capability catalogue is rendered as an explicitly limited
offline view. Toolkit startup adds no request, polling loop or observer.

No MissionChief account, alliance, mission-instance, vehicle, coordinate,
cookie, token, webhook or authentication data is sent to the Guide.

## Verification

Fixture-backed contracts cover valid and invalid schemas, collection limits,
cache round-tripping, HazMat unit/training/personnel evidence, combined local
capability fallback, unknown-label reporting, injection-safe rendering, safe
external links, request ownership and Desktop, Tablet and iOS touch geometry.
