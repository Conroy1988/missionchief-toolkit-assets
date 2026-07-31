# Issue #618 — Toolkit Command Palette

## Outcome

Toolkit v9.4.0 adds one global search surface for the complete retained command system. Open it with the map-bar **Palette** control, press `K` outside a text field, use the Settings button, or assign **Palette** to a Tablet Quick Wheel slot.

## Search catalogue

The catalogue is assembled from current local runtime evidence only when the Palette opens:

- safe Toolkit actions and visibility toggles;
- active personal and alliance missions already known to the map runtime;
- personal vehicles and their current FMS/classification evidence;
- personal and alliance buildings already known to the Toolkit;
- Edinburgh, Fife, Wakefield, London and Newcastle Quick Places;
- saved bookmarks and map profiles; and
- all six Settings sections plus their live command cards.

Search normalises case, accents and punctuation. Every query token must match; exact titles, title prefixes and complete phrases rank above partial matches. Empty search shows a short set of safe, featured actions.

## Action boundary

Mission results use the established mission-focus pathway. Vehicles and buildings focus their existing map marker when location evidence exists and otherwise open MissionChief’s native lightbox route. Location results reuse the existing Quick Place, bookmark and profile functions. Settings results open and highlight the exact existing card.

The Palette never selects or dispatches a vehicle. Reset, import, export and Discord-posting actions are deliberately absent. MissionChief stays authoritative.

## Responsive and accessible operation

The dialog supports touch and mouse selection, Arrow Up/Down wrapping, Home/End, Enter, Escape, contained Tab focus, focus restoration, combobox/listbox semantics and live result counts. It becomes a safe-area-aware full-screen sheet on narrow iOS layouts and retains every interface theme plus Economy and reduced-motion behaviour.

## Lifecycle and performance

The result snapshot exists only while the user-triggered Palette is open and is discarded on close or runtime teardown. Issue #618 adds no network request, MutationObserver, ResizeObserver, interval, timeout, animation-frame scheduler or background task.

## Executable evidence

- `.github/scripts/test_issue618_command_palette_contract.py`
- `.github/scripts/test_issue618_command_palette_runtime.mjs`

The tests prove the complete source catalogue, safety exclusions, entry deduplication, local ranking, keyboard wrapping, focus containment, exact Settings targeting, responsive surface contract and lifecycle cleanup.
