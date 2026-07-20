# Issue #259 — LSSM Mission Requirements parity audit

## Audited baselines

- Toolkit: `8619c79b794ad7241e0a37a0c91a6176daee7911` — v4.20.12.
- LSSM V.4: `4f731e1d6d009cbf2129530fb31d10177b21a52a` — 4.7.12+20260720.0722.

## Result

The Toolkit already matched or exceeded LSSM for requirement parsing, reverse vehicle/equipment capability maps, normal and occupied selected lists, responding and on-site acquisition, factors, conditional requirements, bounded personnel, explicit trailer pairing, de-duplication, patient demand and fail-closed unknown states.

The audit found one incomplete integration and two hardening opportunities.

### Corrected in v4.20.13

1. **Resource progress bars:** water, foam and pumping already had definitions, selectors and observers, but the resolver ignored MissionChief's authoritative `missing` progress value. Required capacity is now reconstructed as `missing + driving + optional on-site`, so driving and selected values are subtracted exactly once.
2. **Random tractive vehicles:** LSSM's reviewed UK `tractiveVehicles` metadata is compiled into a local static map. A trailer contributes an implicit tractive capability only when every compatible tractive type satisfies that requirement.
3. **Personnel reliability:** unrestricted whole-row prose is no longer accepted as proof of specialist training. Explicit MissionChief training attributes and bracketed qualification badges remain supported; absent evidence remains bounded or unknown.

### Already implemented and now fixture-locked

- nested `data-equipment-type` and `data-equipment-types` markers;
- Selected, Responding and On-site equipment reconciliation;
- one contribution for type-plus-equipment evidence;
- native exact/minimum/maximum personnel attributes;
- explicit tractive/trailer pair de-duplication;
- progress-holder mutation observation;
- LSSM coexistence without a runtime dependency.

## Drift control

`.github/fixtures/lssm-v4-en_GB-emv-baseline.json` records the reviewed upstream aliases, vehicle types, equipment, factors, conditional mappings, tractive compatibility and file hashes. `.github/scripts/audit_lssm_requirement_compatibility.py` checks that every pinned LSSM UK capability remains covered by the Toolkit. Passing `--upstream-root` compares a future local LSSM checkout against the pinned snapshot and reports added or removed aliases and structural changes for human review.

The audit never imports or executes LSSM runtime code and cannot modify Toolkit production data.

## Deliberate differences retained

- Toolkit has a separate On-site bucket; LSSM EMV exposes En-route and Selected only.
- Toolkit keeps Mission Info, patients and uncertainty ranges authoritative.
- Toolkit does not depend on LSSM stores or `max_personnel_override`; it uses stable MissionChief-native personnel evidence and fails closed when exact qualification capacity is unavailable.

## Pinned snapshot

- Vehicle requirements: 68
- Staff requirements: 2
- Random-tractive vehicle types: 3
