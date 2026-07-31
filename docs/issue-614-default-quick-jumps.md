# Issue #614 — Default Quick Jump refresh

## Product decision

The fixed Locations catalogue is now:

1. Edinburgh — `EDI`
2. Fife — `FIFE`
3. Wakefield — `WKFD`
4. London — `LDN`
5. Newcastle — `NCL`

Wakefield, London and Newcastle replace Glasgow, Dundee and Stirling respectively. The targets use city-centre coordinates; London opens one zoom level wider for area context.

## Persistence contract

Quick Jump pins and user bookmarks are separate state. During settings normalisation, a selected legacy fixed-place pin moves to its replacement unless an explicit replacement value is already present. Obsolete and unrelated Quick Jump keys are discarded. Custom bookmarks, saved profiles and all other settings are not read or changed by this migration.

## Toolkit Doctor context

The supplied v9.3.0 tablet report recorded responsive-layout and overlay-safety warnings. Those checks intentionally describe live viewport bounds and competing MissionChief page overlays; they are not caused by the fixed place catalogue. Issue #614 does not weaken or suppress them, and the existing privacy-safe Repair action remains available for reconciliation.

## Verification

- Static contract: exact order, IDs, compact labels, coordinates, zoom levels, migration markers and update briefing.
- Runtime contract: fresh defaults, legacy selected-pin transfer, explicit replacement precedence, obsolete-key removal and input immutability.
- Canonical source, root mirrors and distribution mirrors remain byte-identical.
