# Issue #230 — Probability and availability metadata

## Corrected model

The Mission Requirements Matrix now follows the same structural separation used by the official LSSM V4 Mission Helper:

- `requirements` supplies resource quantities;
- `chances` supplies probability metadata;
- `prerequisites` and availability rules remain non-operational metadata.

The Toolkit has no LSSM runtime dependency. The reviewed LSSM implementation was used only to verify the semantic model.

## Runtime behaviour

- Probability and chance captions are classified before capability matching or generic fallback.
- Availability-only boolean rows are consumed as modifiers and never become unresolved requirements.
- Conditional catalogue quantities are associated by canonical capability key.
- Catalogue-only conditional quantities remain dormant.
- A live MissionChief requirement activates the corresponding row and retains its catalogue baseline and modifier metadata.
- Unconditional catalogue requirements and patient-derived Ambulance demand remain unchanged.
- Modifier state is local to one parsed mission catalogue and cannot leak across AJAX or normal-page mission transitions.

## Regression coverage

Fixtures cover Traffic Cars, Water Carrier, Aerial Appliance Truck, patient transport probability, critical-care probability, unknown booleans, direct parsing, normal source parsing, conditional activation, unconditional preservation, cross-mission isolation and header totals.
