# Issue #255 — v8.3.1 unchanged `updateUI()` baseline

> Disposable render-probe and jsdom evidence. Nested renderers and root-attribute reconciliation are deliberately stubbed so the figures isolate the direct `updateUI()` shell.

- Toolkit: `8.3.1`
- Source SHA-256: `363c6fa8f742840d71a65187c4b2f5b60fcffda519d63f2416c488cd86ca8089`
- Production source modified: `false`
- Total selector reads: 6700
- Total write attempts: 14500
- Proven unchanged write attempts: 14500
- Actual mutation records: 7100
- Same-value attribute mutation records: 4300

| Scenario | Repeats | Selector reads | Write attempts | Unchanged attempts | Mutation records | Same-value attributes | Median synchronous time |
|---|---:|---:|---:|---:|---:|---:|---:|
| idle-panel-closed | 25 | 1675 | 3625 | 3625 | 1775 | 1075 | 6.127 ms |
| settings-open | 25 | 1675 | 3625 | 3625 | 1775 | 1075 | 6.348 ms |
| resources-open | 25 | 1675 | 3625 | 3625 | 1775 | 1075 | 4.982 ms |
| operations-open | 25 | 1675 | 3625 | 3625 | 1775 | 1075 | 4.514 ms |

## Decision boundary

The fixture proves repeated unchanged updateUI shell work only. Production suppression requires an isolated helper, before/after evidence, lifecycle invalidation fixtures and an independently revertible release.


## Production status

This baseline changes no production source or distribution. It proves a candidate optimisation area but does not itself authorise a release.

## v8.3.2 write suppression

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


