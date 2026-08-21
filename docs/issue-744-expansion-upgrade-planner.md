# Expansion & Upgrade Planner (Issue #744)

Toolkit v10.14.2 provides the manual, Credit-only Expansion & Upgrade Planner under **Dispatch** and supports MissionChief's current native expansion-page, level and vehicle-bay purchase flow.

## Operator workflow

1. Choose **Load Stations**.
2. Select one Dispatch Centre or **ALL DISPATCH CENTRES**, an exact building type or **ALL BUILDING TYPES**, and the required upgrade class.
3. Set the maximum number of stations to inspect and choose **Scan Upgrades**.
4. Review the current station, operation and Credit price for every available native action. A scan approves nothing by default.
5. Select the exact operations required. The planner permits at most one operation per station in a run.
6. Enter a hard Credit budget. **Purchase Selected** remains disabled if the exact selected total exceeds it.
7. Review the freshly revalidated list, exact total, hard budget and unspent amount in the final confirmation.
8. Leave the map open while the planner purchases and verifies one operation at a time. **Stop** finishes the active request and verification, then prevents the next purchase.
9. Review the retained result report and dismiss it when no longer needed.

## Fixed safety boundaries

- No request runs until Load, Scan or Purchase is selected; there is no polling or automatic schedule.
- Prices are read only from the current native action's own **Credits** text. Static price tables are not used.
- Level and vehicle-bay discovery follows only the station page's exact same-origin `/buildings/<id>/expand` link. Queried, external, redirected and inferred discovery pages are rejected.
- Native extension actions remain POST-only. A level or vehicle-bay action may use GET only for the exact same-origin `expand_do/credits?level=<next>` route, where `level` is the sole query field and equals the next authoritative station level.
- Coin, gold, external, wrong-level, extra-query, completion, cancellation, method-mismatched and ambiguous controls are rejected.
- Owned-station identity, Dispatch Centre, building type, small/full classification, name and coordinates stay bound to the scan.
- A station with an expansion already under construction is excluded.
- The selected level and extension state, exact discovery page, action path, action fingerprint and price are revalidated before confirmation and again before the write.
- Purchases are sequential and constrained by the hard per-run operation and Credit limits.
- The current native CSRF token or complete native POST form is used. The exact next-level GET carries MissionChief's CSRF header; form fields unrelated to POST purchases are preserved.
- MissionChief's authoritative building record and native page are fetched after every write. The next purchase starts only after the expected change is proven.
- An uncertain submitted request, changed response, missing action or failed verification stops the complete run. Mutation requests are never retried automatically.

The scan summary reports how many native expansion pages and Credit-labelled controls were inspected, plus price, route and method rejections. The planner cannot make an unsupported MissionChief control safe; if a current page does not expose an unambiguous Credit action, that operation remains unavailable and must be handled natively.
