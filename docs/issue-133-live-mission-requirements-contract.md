# Issue #133 — Live Mission Requirements DOM Contract

## Status

Implemented and fixture-validated for the v4.15.1 release candidate.

This document records the MissionChief browser interfaces consumed by the clean-room implementation. It is deliberately independent of LSSM implementation code.

## Source of truth

The active MissionChief mission window is authoritative. The Toolkit derives current state from the live DOM and stable MissionChief attributes rather than maintaining a complete static mission catalogue.

## Requirement source

Primary root:

```css
#missing_text
```

Expected requirement groups where supplied by MissionChief:

```css
#missing_text [data-requirement-type="vehicles"]
#missing_text [data-requirement-type="personnel"]
#missing_text [data-requirement-type="other"]
```

The parser preserves the original text for any requirement fragment it cannot map. Unknown text is never classified as covered.

## En-route source

Primary table:

```css
#mission_vehicle_driving tbody tr
```

Preferred stable attributes:

```text
vehicle_type_id
```

Equipment metadata is consumed only from stable `data-*` attributes exposed by MissionChief. The implementation does not depend on visual labels when a stable identifier is available.

## Selected-vehicle source

Normal list:

```css
#vehicle_show_table_body_all .vehicle_checkbox:checked
```

Occupied or alternate list:

```css
#occupied .vehicle_checkbox:checked
```

Preferred stable attributes:

```text
value
vehicle_type_id
data-equipment-types
tractive_vehicle_id
tractive_random
```

The selected total is recalculated from current checked elements. It is not maintained as a fragile increment/decrement counter.

## Coverage model

For a simple unit requirement:

```text
stillNeeded = max(0, missingOnMission - enRoute)
covered = selected >= stillNeeded
```

The pure calculator also supports:

- several eligible vehicle types for one requirement;
- combined A-or-B requirements;
- equipment capacity;
- exact and bounded personnel capacity;
- trailers and towing vehicles without double counting;
- capacity factors greater than one;
- conditional eligibility based on mission type metadata;
- unknown requirements that remain explicitly unresolved.

Capacity is represented as a minimum/maximum range. The matrix becomes green only when the known minimum capacity guarantees coverage. Ambiguous capacity remains amber rather than being promoted to a false covered state.

## Observation contract

The implementation uses deterministic DOM events and narrowly scoped `MutationObserver` instances.

Only active mission-window surfaces required for the following are observed:

- checkbox checked-state changes;
- selected vehicle count changes;
- equipment metadata changes;
- replacement of the requirement root;
- replacement or mutation of the en-route table;
- MissionChief lightbox/AJAX mission replacement.

Mutation bursts are coalesced into at most one recalculation per animation frame or equivalent bounded scheduler.

## Layout contract

The Toolkit panel is inserted in normal document flow above the mission dispatch controls. It pushes subsequent content downward.

Forbidden layout techniques:

- fixed or absolute positioning for the normal panel;
- negative margins used to overlap native content;
- hard-coded vertical offsets tied to another extension;
- moving or restyling an LSSM-owned panel.

The panel root uses a collision-resistant Toolkit ID and is unique per active mission document.

## LSSM coexistence

The Toolkit works with LSSM absent, present with its equivalent feature disabled, and present with its equivalent feature active.

When an active LSSM enhanced-missing-vehicles panel is detected, the Toolkit does not render a competing second requirements panel. Detection uses explicit observable ownership markers and structure, without dependence on LSSM globals or stores. MissionChief and LSSM can both use the generic `.alert-missing-vehicles` presentation class, so that shared class alone is never treated as LSSM ownership; the active LSSM component must expose a marker such as `data-raw-html`.

## Lifecycle invariants

- One Toolkit requirements panel maximum per active mission document.
- One document observer coordinator maximum.
- Replacing the mission window tears down the previous record and observer.
- Re-rendering does not clear native checkbox selection.
- Toolkit runtime teardown disconnects all observers and listeners.
- Unknown or incomplete data produces a visible unresolved state rather than a false green state.

## Executed deterministic fixture matrix

1. Simple vehicle requirement.
2. Multiple units of one type.
3. Two simultaneous requirements in source order.
4. Several eligible vehicle types.
5. Combined A-or-B requirement.
6. Checkbox selection and deselection.
7. En-route capacity reducing still-needed.
8. En-route vehicle arrival or removal changing DOM state.
9. Equipment requirement and row-owned equipment metadata.
10. Exact and bounded personnel capacity.
11. Trailer and towing vehicle deduplication.
12. Capacity factor greater than one.
13. Normal and occupied-list selections together.
14. Unknown requirement text.
15. Mission-window replacement.
16. Repeated scans without duplicate observers, records or panels.
17. LSSM absent.
18. LSSM present with the equivalent feature disabled.
19. LSSM present with the equivalent feature active.
20. Both Toolkit/LSSM load orders.
21. Desktop table and Tablet/iOS responsive-card contracts.
22. Feature disable and runtime-owned teardown.
23. MissionChief native missing alert using the shared presentation class without LSSM ownership metadata.

## Validation status

The v4.15.1 candidate must pass:

- executable parser, calculator and lifecycle fixtures;
- MissionChief-native versus LSSM ownership fixtures;
- JavaScript syntax validation;
- canonical userscript validation;
- code-integrity audit;
- static public-asset audit;
- documentation-drift audit in guarded source-transition mode;
- canonical source and distribution byte-identity validation.

## Release gate

Production publication remains prohibited until PR #140 is review-ready, all pull-request workflows are green, the branch is merged through the guarded repository process, and `/release-toolkit 4.15.1 RELEASE` completes successfully.
