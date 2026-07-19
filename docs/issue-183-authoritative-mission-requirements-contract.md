# Issue #183 — Authoritative Requirements for this Mission contract

The Mission Requirements Matrix automatically reads the official MissionChief `/einsaetze/<definition>` page linked by **Requirements for this Mission**. Vehicle and personnel rows are parsed through the existing UK requirement definitions and merged into the live Matrix model.

The reconciliation contract is a key-based union. Existing live rows are retained and receive the official baseline; rows present only in mission information are added once with a compact `Mission info` source badge. Required capacity uses the largest supported authority rather than summing duplicate sources. Patient-derived Ambulance demand remains independent and can raise the Ambulance minimum above mission information.

Requirements with a probability below 100% are displayed as uncertain capacity rather than being falsely declared definitely outstanding. Unknown or unmapped mission-information rows remain unresolved, and a pending or failed authoritative request prevents a false complete state.

Definitions are cached by official definition URL because all mission instances of that definition share the same baseline. Each record also captures the active mission-instance identity, so a delayed response cannot apply after AJAX navigation. No polling, automatic selection or dispatch is introduced. Desktop, Tablet, iOS and LSSM use the existing single Matrix panel.
