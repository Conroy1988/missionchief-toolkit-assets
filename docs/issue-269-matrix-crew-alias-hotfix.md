# Issue 269 — Mission Matrix crew and response-vehicle aliases

## Behavioural correction

- Semantic crew metadata exposed by MissionChief remains the first authority.
- When an eligible selected, responding or on-site vehicle exposes no semantic crew field, the Matrix uses the locally compiled UK vehicle-type minimum and maximum staff range.
- A native per-vehicle maximum override narrows the compiled range when it is exposed on the active vehicle row.
- Specialist personnel requirements still require explicit training evidence; the fallback does not invent training.
- Known bounded capacity remains a bounded range instead of being discarded as fully unknown.

## Canonical labels

The official Mission Info labels `PRV`, `PRVs`, `SRV` and `SRVs` resolve to the existing canonical keys:

- `Primary Response Vehicle`
- `Secondary Response Vehicle`

Abbreviations are accepted as parser aliases only. They must not render as separate Matrix rows.

## Deterministic protection

The runtime contracts cover:

- Police Car minimum and maximum officer capacity;
- native maximum override handling;
- selected Police Officer shortage reduction;
- bounded-capacity preservation;
- PRV/SRV canonical key and full-label resolution;
- catalogue fixture reconciliation;
- canonical source and distribution parity.
