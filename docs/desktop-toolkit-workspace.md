# Desktop Toolkit Workspace

Toolkit v10.15.0 turns the Desktop menu into a movable, resizable workspace while retaining the existing map-attached command toolbar and the Toolkit's single shared runtime.

## Use the workspace

1. Open the Toolkit from the persistent map toolbar.
2. Move the workspace by dragging its title bar.
3. Resize it from the bottom-right grip. The arrow keys resize by 24 pixels while that grip is focused; hold **Shift** for an 80-pixel step.
4. Use the square header control to maximise the workspace inside the safe browser viewport. Select it again to restore the saved windowed geometry.
5. Close and reopen the Toolkit normally. Desktop width, exact height and position are retained locally.

## Layout behaviour

- Narrow workspaces use one content column.
- Standard workspaces use two columns.
- Workspaces at least 1,100 pixels wide use three columns where the active interface permits it.
- Desktop body, supporting text and controls have readable minimum sizes in every density mode.
- Saved geometry is clamped to the currently visible workspace after browser resizing, navigation changes or display changes, so the menu cannot remain stranded off-screen.

## Compatibility boundary

The workspace is not a second browser popup and does not clone the Toolkit. It remains the one body-level Toolkit panel, which preserves all feature state, event ownership, themes, saved settings and teardown behaviour. The map command toolbar is sized independently and remains attached to the map. Tablet and iOS layouts do not receive the Desktop resize grip or maximise control and retain their existing responsive geometry.

Resizing does not create a timer, observer or network request. Pointer movement updates only live geometry; settings are written once when the resize completes. Maximise is temporary and does not overwrite the saved windowed dimensions.
