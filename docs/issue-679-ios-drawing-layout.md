# Issue #679 · iOS Drawing workspace repair

Toolkit `v10.5.1` makes the unified Drawing workspace genuinely usable in iOS Safari without changing its map geometry or lifecycle.

## Touch layout

- Drawing is a compact bottom sheet capped at 52% of the current dynamic viewport and 430px.
- The sheet follows the Toolkit's existing visual-viewport offsets, browser-chrome gaps and safe-area insets.
- At least 96px of the visual viewport remains outside the sheet even in constrained landscape layouts.
- The header, object count and 44px close control remain fixed; only `.mcms-drawing-scroll` scrolls vertically.
- All ten modes sit in one horizontally swipeable 44px tool rail with scroll snapping and no visible scrollbar.
- Colours, line styles, readout, Undo, Finish, Clear All and guidance remain in the internally scrollable content.

## Compatibility

- Desktop and Tablet retain their existing panel presentation.
- Distance and area remain in km and km².
- All ten Drawing modes, style controls, caps, session-only storage and deterministic teardown remain unchanged.
- Safari portrait, landscape, browser-chrome and safe-area geometry are covered by a dedicated static layout contract.

## Performance

The repair reuses the existing visual-viewport refresh and changes only CSS plus Drawing markup containment. It adds no timer, interval, observer, request, animation loop, managed listener, permanent map layer or idle map work.
