# Issue #661 — long-session memory lifecycle contract

## Scope

This release repairs only resources proven to remain strongly referenced after normal MissionChief window and Toolkit UI churn:

- Mission Value document, frame and toolbar-host observers.
- Custom Vehicle Badge document observers and frame load listeners.
- Command Palette listeners and detached overlays.
- Replaced version-status and command-shell controls.

Mission Value is additionally restricted to a connected MissionChief mission popup that contains actual mission content. A mission link by itself does not qualify a dialog, and a full-page mission route does not qualify as the popup host.

## Ownership rules

- Every observed document is owned by an iterable map so it can be disconnected and untracked while the Toolkit remains running.
- Every frame load listener is removed from both the frame and the runtime listener registry when its frame leaves the active document tree.
- Every Mission Value toolbar observer is removed from both its host record and the runtime observer registry when its host disconnects.
- Every transient Command Palette listener is released before the overlay is removed.
- Replaced version controls release listener ownership before replacement.
- Full Toolkit teardown remains the final fail-safe owner.

## Regression evidence

`.github/scripts/test_issue661_memory_lifecycle_runtime.mjs` executes 250 cycles for each of these paths:

1. Command Palette open and close.
2. Mission Value toolbar-host replacement.
3. Mission document and frame replacement.
4. Custom Vehicle Badge document and frame replacement.

After each cycle, the relevant listener, observer, document, frame and overlay counts must return to zero. Mission Value’s existing contract separately verifies popup-only scope, unrelated-dialog rejection and full-page rejection.

This contract does not claim that the Toolkit is the sole source of a reported 12–13 GB Chromium tab. It removes the confirmed Toolkit retention paths without requiring user-side diagnostics and provides a stable basis for later browser attribution if unusually high memory remains.
