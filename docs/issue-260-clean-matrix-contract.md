# Issue #260 — Clean Mission Matrix metadata contract

Toolkit v4.20.14 separates operational labels from provenance and mission-generation metadata.

- Requirement-name text contains only the canonical operational label.
- Provenance is exposed through `data-requirement-source`, never a visible or hidden badge child.
- `Required Personnel Available` is a `spawn-prerequisite` and cannot enter rows, unresolved output, totals or panel colour.
- `Other information → Required Personnel` is operational and produces normal trained-personnel rows.
- Level 2 Public Order Officer and Police Sergeant use explicit MissionChief training evidence for live reconciliation.
- Unsupported operational personnel remain visible without a `Mission info:` prefix.
- Precondition station, extension and organisational unlock metadata remains outside the operational model.
