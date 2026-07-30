# Issue #255 — `updateUI()` same-value write suppression

Toolkit v8.3.2 applies a narrowly scoped optimisation to the central UI state synchroniser.

## Evidence

The exact v8.3.1 rendered baseline measured 100 warmed unchanged calls at 14,500 attempted writes and 7,100 mutation records. The v8.3.2 fixture records zero writes and zero mutations for the same four scenarios.

## Safety boundary

- Every call still queries the current MissionChief control and panel nodes.
- No element reference is cached across framework replacement.
- First render, state transitions and complete control/panel replacement remain covered and apply state correctly.
- Nested operational renderers, scheduling, observers, requests and teardown semantics are unchanged.
- The evidence proves eliminated rendered-fixture writes and mutation records; it is not a live frame-rate claim.

Source evidence: `docs/audits/issue-255/write-suppression-v832.json`.
Source SHA-256: `e719dd7f26686895cd1ba9e31dd006c775134af86000eb7d32800feea6843cfa`.
