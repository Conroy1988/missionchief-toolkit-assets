# Issue #255 — v8.3.2 `updateUI()` same-value write suppression

- Before unchanged write attempts: 14,500
- After unchanged write attempts: 0
- Before mutation records: 7,100
- After mutation records: 0
- State transition changed writes: 18
- State transition mutation records: 19
- Framework replacement changed writes: 121
- Framework replacement mutation records: 108

The first changed-state and replacement-DOM passes still apply state. Their immediate stable repeats produce zero writes and zero mutation records.

> Exact rendered fixture proof for the direct updateUI shell. Synchronous jsdom timings are diagnostic only and are not a live browser frame-rate claim.

