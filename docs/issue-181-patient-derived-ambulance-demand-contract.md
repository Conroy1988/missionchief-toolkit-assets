# Issue #181 — Patient-derived ambulance demand contract

The Mission Requirements Matrix treats the live patient total as an independent UK ambulance-demand authority. One current patient requires one ordinary Ambulance by default. The implementation reads `#patient_button_text` / `#patient_button_form`, preferring numeric attributes and the patient-total `<strong>` element before bounded text parsing.

Patient demand and MissionChief's stated Ambulance requirement are reconciled with `max(patient total, reconstructed live requirement, catalogue baseline)`. They are never summed blindly. Type 5 remains the conservative transport-Ambulance mapping; non-transport medical responders are excluded.

The existing Selected, Responding and On-site vehicle-ID buckets remain exclusive. Unknown patient totals keep the row unresolved and prevent a green Matrix state. A 1.4-second same-mission transition cache covers temporary AJAX replacement, is isolated by mission ID and expires without polling.

The feature adds no second panel and performs no vehicle selection, dispatch or patient transport. Desktop, Tablet and iOS use the existing Matrix layout, with a compact `Patients` source marker on the Ambulance row.
