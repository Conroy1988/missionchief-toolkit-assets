# Issue #622 — v10.1 Command Experience

Toolkit v10.1.0 joins six user-selected experience upgrades behind the existing revisioned settings, deterministic lifecycle and MissionChief-native action boundary.

## What ships

- **What’s New & Feature Beacon** gives every release feature a direct **Open Feature** action and keeps a `NEW` badge on its Settings route until that route is viewed.
- **Contextual command menus** open from Desktop right-click or Tablet/iOS marker long-press for supported missions, vehicles and buildings. Actions are limited to focus, native open and local Palette search; they never select or dispatch units.
- **Complete MissionChief reskinning** extends the selected Toolkit theme across MissionChief navigation, lists, windows, tables, forms and buttons. Operational success, warning and danger semantics remain protected, and one switch restores the native interface.
- **Smart auto-hiding dock** collapses the command controls toward the configured horizontal or vertical edge while keeping the launcher and version status available. Hover/focus restores it on Desktop and the launcher restores it on touch devices.
- **Hotkey & Gesture Studio** remaps every Toolkit keyboard command with duplicate rejection and assigns four opt-in dock swipes on Tablet/iOS. Editable fields, browser Meta shortcuts, ordinary taps and map panning retain priority.
- **Toolkit Safe Mode** temporarily suspends optional overlays, dashboards, effects, reskinning, Quick Wheel, Palette, context menus and gestures while preserving Settings, Toolkit Doctor, export, recovery and the Safe Mode exit.

## Persistence and recovery

Existing v10 settings migrate without prompting. New state is normalised and device-independent where appropriate. Safe Mode takes a bounded secret-free local settings snapshot before both entry and exit; it does not overwrite the user’s original feature choices, Discord webhook or Financial Archive stores.

Every new root attribute, menu and event path is removed by deterministic teardown. The release adds no request, poller, interval, observer or animation-frame scheduler. It reuses the existing document context-menu listener boundary and dock pointer lifecycle.

## Release acceptance

The candidate must prove version parity across all release copies, conflict-safe hotkey normalisation, opt-in gesture thresholds, feature-beacon acknowledgement, reversible reskin and dock state, Safe Mode preservation/restoration, no dispatch action in contextual menus and full retained preflight compatibility.
