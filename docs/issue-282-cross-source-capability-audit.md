# Issue 282 — maritime requirements and cross-source capability audit

Toolkit v4.20.19 closes the gap between MissionChief's authoritative maritime wording and the existing LSSM-derived UK capability catalogue.

## Runtime correction

- `Inland Rescue Boat (Trailer)` and reviewed singular/plural variants resolve to the existing type 67/74 inland-boat capability union.
- `Seagoing Vessel` and `Seagoing Vessels` resolve to the ILB/ALB capability union, types 68/69.
- Trailer-capable requirements can no longer be satisfied solely by a compatible towing vehicle. The actual eligible trailer or maritime asset must be present.
- A trailer and its explicit towing vehicle retain a shared contribution identity and count once.
- Selected, Responding and On-site transitions retain bucket precedence and never duplicate the same asset.
- Police Sergeant and Level 2 Public Order ARR attributes remain discoverable by vehicle identity after dispatch, even when the travelling row no longer renders its training badge.
- Exact assigned personnel from the shared vehicle cache remains authoritative for those trained-personnel contributions.

## Screenshot regression

A row with Required `3`, Selected `1`, Responding `0`, On site `0` now remains outstanding with Still needed `2`. The panel summary reports `0/1 covered`; known shortages are not represented as fulfilled.

## Cross-source audit

The pinned, non-mutating compatibility fixture now records:

- LSSM Enhanced Missing Vehicles aliases and type/equipment contracts;
- LSSM Mission Helper UK vehicle captions and reviewed canonical mappings;
- the complete pinned LSSM UK vehicle-caption catalogue;
- MissionChief authoritative Mission Info labels requiring parser support;
- Toolkit aliases, types, equipment, factors, conditional mappings and pair semantics;
- the compiled random-tractive compatibility map.

The audit is executed by the canonical Mission Requirements contract and userscript validation gate. It executes the production parser and capability resolver. Every accepted Toolkit vehicle alias is checked with every eligible type through Selected, Responding and On-site coverage, an ineligible control, and contribution-key deduplication.

## Review boundary

The audit does not import upstream changes automatically. Added or removed labels, types, equipment, factors, conditions, trailer semantics or Mission Helper tokens produce a blocking or actionable report for human review. The Toolkit remains standalone and has no LSSM runtime dependency.
