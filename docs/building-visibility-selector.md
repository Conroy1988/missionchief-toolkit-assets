# Building Visibility Selector

The Buildings control now toggles a saved view instead of forcing a single undifferentiated map state.

## Interaction

- Press `4` (or tap Buildings) to hide or restore the current saved building view.
- Press `Shift+4`, right-click the Buildings dock control, or choose **Choose building types & ownership** in Map Visibility to open the selector.
- Choose **Own**, **Alliance**, or **Own + Alliance** as the ownership scope.
- Search native MissionChief building types, tick any combination, or use **Only** for a one-type view.
- **All** shows every type in the current ownership scope.
- **None** hides every building without discarding the saved selection, so `4` restores it immediately.
- **Restore** rolls the selector back to the state captured when it was opened.

The dock and panel report the effective state (`ALL`, a single type, `N TYPES`, or `HIDDEN`). Selection, ownership scope, and map profiles persist through Toolkit state storage.

## Layer behaviour

The selector uses MissionChief's `map_filters_service.getFilterLayerByBuildingParams` targets when available, then enforces the same decision on confidently identified marker layers as a fallback. This keeps newly loaded markers aligned with the saved selection. The broad native My Buildings setting is bridged independently from the Toolkit master state, allowing Alliance-only views without the native bridge turning the whole selector off.

Toolkit teardown restores the native target visibility captured before the selector managed each target.

## Validation

Run the focused local lane:

```bash
./toolkit check --feature building-visibility
```

The contract and runtime fixtures cover persistence anchors, responsive controls, type and ownership decisions, native target enforcement, fallback marker restoration, and teardown restoration.
