# Issue #553 — canonical Alliance Member Manager Tools rendering

Toolkit v8.1.3 places Alliance Member Manager directly in the Toolkit's canonical `createPanel()` Tools markup.

- The **Alliance Operations** two-card row is rendered once with Alliance Map Blocker and Alliance Member Manager.
- The manager control uses the same `mcms-toggle-btn` structure as other native Tools controls.
- Clicks are handled by the existing panel `data-action` dispatcher.
- `updateUI()` owns persisted ON/OFF state.
- No post-render selector search, clone, observer, timer, microtask or animation-frame retry is used.
- The member-list runtime remains opt-in, route-scoped and unchanged.
