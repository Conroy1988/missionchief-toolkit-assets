# Issue #133 — Live Mission Requirements DOM Contract

## Status

Initial fixture and integration contract for the MissionChief Map Command Toolkit live mission requirements matrix.

This document records the MissionChief browser interfaces that the clean-room implementation may consume. It is deliberately independent of LSSM implementation code.

## Source of truth

The active MissionChief mission window is authoritative. The Toolkit must derive the current state from the live DOM and stable MissionChief attributes rather than maintaining a complete static mission catalogue.

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

The parser must preserve the original text for any requirement fragment it cannot map. Unknown text must never be classified as covered.

## En-route source

Primary table:

```css
#mission_vehicle_driving tbody tr
```

Preferred stable attributes:

```text
vehicle_type_id
```

Equipment metadata should be consumed only from stable `data-*` attributes exposed by MissionChief. The implementation must not depend on visual labels when a stable identifier is available.

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

The selected total must be recalculated from current checked elements. It must not be maintained as a fragile increment/decrement counter.

## Coverage model

For a simple unit requirement:

```text
stillNeeded = max(0, missingOnMission - enRoute)
covered = selected >= stillNeeded
```

The pure calculator must also support:

- several eligible vehicle types for one requirement;
- combined A-or-B requirements;
- equipment capacity;
- personnel minimum and maximum capacity;
- trailers and towing vehicles without double counting;
- capacity factors greater than one;
- conditional eligibility based on mission type metadata;
- unknown requirements that remain explicitly unresolved.

## Observation contract

The implementation should prefer deterministic DOM events and narrowly scoped `MutationObserver` instances.

Observe only the active mission window surfaces required for:

- checkbox checked-state changes;
- selected vehicle count changes;
- equipment metadata changes;
- replacement of the requirement root;
- replacement or mutation of the en-route table;
- MissionChief lightbox/AJAX mission replacement.

Mutation bursts must be coalesced into at most one recalculation per animation frame or equivalent bounded scheduler.

## Layout contract

The Toolkit panel must be inserted in normal document flow above the mission dispatch controls. It must push subsequent content downward.

Forbidden layout techniques:

- fixed or absolute positioning for the normal panel;
- negative margins used to overlap native content;
- hard-coded vertical offsets tied to another extension;
- moving or restyling an LSSM-owned panel.

The panel root must use a collision-resistant Toolkit ID and must be unique per active mission window.

## LSSM coexistence

The Toolkit must work with LSSM absent, present with its equivalent feature disabled, and present with its equivalent feature active.

When an active LSSM enhanced-missing-vehicles panel is detected, the Toolkit must not render a competing second requirements panel. Detection must be based on observable ownership markers and structure, not on dependence on LSSM globals or stores.

## Lifecycle invariants

- One Toolkit requirements panel maximum.
- One active observer coordinator maximum.
- Replacing the mission window tears down observers bound to the previous window.
- Re-rendering does not clear native checkbox selection.
- Toolkit runtime teardown disconnects all observers and listeners.
- Unknown or incomplete data produces a visible unresolved state rather than a false green state.

## Initial deterministic fixture matrix

1. Simple vehicle requirement.
2. Multiple units of one type.
3. Two simultaneous requirements.
4. Several eligible vehicle types.
5. Combined A-or-B requirement.
6. Checkbox selected and deselected.
7. En-route capacity reducing still-needed.
8. En-route vehicle arrival replacing DOM state.
9. Equipment requirement.
10. Personnel minimum and maximum capacity.
11. Trailer and towing vehicle.
12. Capacity factor greater than one.
13. Occupied-list selection.
14. Unknown requirement text.
15. Mission-window replacement.
16. Repeated mutations without duplication.
17. LSSM absent.
18. LSSM present, equivalent feature disabled.
19. LSSM present, equivalent feature active.
20. Both Toolkit/LSSM load orders.
21. Desktop, Tablet and iOS responsive layout contracts.

## Release gate

Production code must not be released until parser, mapping, calculator, lifecycle, coexistence and responsive layout fixtures pass together with the full canonical userscript validation and source/distribution byte-identity checks.
