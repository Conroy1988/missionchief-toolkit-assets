# Issue #601 — Operational Pressure Board and Discord SITREP

## Product contract

The Operational Pressure Board is a read-only command surface opened from the persistent map Dashboard group or the Missions section. It combines current personal missions and joined alliance incidents into one operational pressure model.

The board must:

- allocate each available personal vehicle at most once across all current mission requirements;
- expose confirmed shortfall, shared specialist Fleet Conflicts, reserve risk and patient/prisoner transport pressure;
- order no more than three Top Actions using only current evidence;
- provide Focus, Open and Pin navigation without selecting or dispatching vehicles;
- show an explicit `ACTIVE` or `OFF` state on the map button and support shortcut `B`;
- preserve identical geometry across all eight interface themes;
- provide Desktop, Tablet and iOS bottom-sheet layouts with safe-area handling and 44px touch targets.

## Shared evidence

The feature reuses the Toolkit’s existing mission snapshots, vehicle availability records, Resource Gap matching, Unit Commitment, Mission Age, Stuck Detector and Transport Watcher signals. It does not add a polling loop, observer, managed scheduler or network-request site.

Location-bound resource statements remain incomplete when MissionChief does not expose enough location evidence. The board must show partial-evidence status rather than invent coverage.

## Operational SITREP

The SITREP uses the exact current board snapshot and is sent only after a manual **Generate & Post Operational SITREP** action.

- It reuses the saved Finance Discord webhook.
- It suppresses mentions through `allowed_mentions`.
- It never includes the webhook in the payload.
- It respects Discord title, field and total embed limits.
- It states that the briefing is read-only and no units were selected or dispatched.
- It does not post automatically.

## Verification

The Issue #601 fixture and runtime contracts cover:

- global one-vehicle/one-allocation behaviour;
- cross-mission specialist conflict and reserve evidence;
- Top Actions ordering and pin precedence;
- transport aggregation;
- mention-safe, budget-bounded Discord payloads;
- board creation and interaction routing;
- eight-theme geometry parity;
- iOS safe-area layout and minimum touch-target dimensions;
- zero new timer, observer, managed scheduler and network-request sites.
