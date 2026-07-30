# Issue #608 — Tablet Pressure Board header clearance

## Production defect

Toolkit v9.1.2 applied `top: 10px` to the Operational Pressure Board whenever Tablet mode was active. MissionChief's fixed navigation bar occupies the top of the same viewport, so the board title, SITREP, refresh and close controls could render underneath native chrome.

The supplied 730×1200 capture showed the board beginning behind a 53px native header: the subtitle remained visible, but the complete action row was inaccessible.

## v9.1.3 contract

- Resolve the Tablet board's top edge from the live map workspace and visual viewport.
- Preserve a minimum native-chrome allowance even when no map rectangle is available.
- Apply a safe gap below the resolved workspace top.
- Recalculate when the board opens, the visual viewport changes, the page resizes or the device rotates.
- Derive maximum height from the resolved top and bottom safe area so overflow remains internally scrollable.
- Remove Tablet-only geometry when switching to Desktop.
- Preserve the iOS/Mobile fixed bottom sheet.
- Preserve all eight interface themes and minimum 44×44 Tablet actions.
- Add no request, observer, interval or managed scheduler.

## Verification

The executable Issue #608 regression reproduces the supplied 730×1200 viewport and 53px MissionChief header, requiring the board to begin at 76px with 1,114px of remaining safe height. It also covers landscape visual-viewport offsets, mode switching, board-open positioning and viewport-refresh positioning.
