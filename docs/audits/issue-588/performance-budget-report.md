# Toolkit performance budget

**Result:** PASSED

| Metric | Base | Candidate | Change | Absolute limit | Utilisation |
|---|---:|---:|---:|---:|---:|
| Source bytes | n/a | 1654208 | n/a | 3000000 | 55.1% |
| Source lines | n/a | 25228 | n/a | 64000 | 39.4% |
| Non-empty lines | n/a | 24072 | n/a | n/a | n/a |
| Estimated embedded CSS bytes | n/a | 704606 | n/a | 950000 | 74.2% |
| Estimated embedded CSS rule blocks | n/a | 5464 | n/a | 7000 | 78.1% |
| Direct setInterval call sites | n/a | 1 | n/a | 4 | 25.0% |
| Direct setTimeout call sites | n/a | 3 | n/a | 25 | 12.0% |
| Direct MutationObserver constructions | n/a | 8 | n/a | 9 | 88.9% |
| Direct ResizeObserver constructions | n/a | 1 | n/a | 4 | 25.0% |
| Direct requestAnimationFrame call sites | n/a | 1 | n/a | 20 | 5.0% |
| Direct addEventListener call sites | n/a | 44 | n/a | 120 | 36.7% |
| querySelector/querySelectorAll call sites | n/a | 228 | n/a | 400 | 57.0% |
| DOMContentLoaded/load startup hooks | n/a | 5 | n/a | 10 | 50.0% |
| Managed runtimeSetInterval call sites | n/a | 1 | n/a | 1 | 100.0% |
| Managed runtimeSetTimeout call sites | n/a | 81 | n/a | 99 | 81.8% |
| Managed runtimeRequestAnimationFrame call sites | n/a | 10 | n/a | 14 | 71.4% |
| Managed runtimeListen call sites | n/a | 26 | n/a | 31 | 83.9% |
| Managed runtimeTrackObserver call sites | n/a | 13 | n/a | 15 | 86.7% |
| Managed runtimeRunWhenIdle call sites | n/a | 3 | n/a | 3 | 100.0% |
| MutationObserver constructions including aliases | n/a | 11 | n/a | 13 | 84.6% |
| ResizeObserver constructions including aliases | n/a | 4 | n/a | 4 | 100.0% |
| Observer registrations with subtree: true | n/a | 9 | n/a | 11 | 81.8% |
| Document/body subtree observer registrations | n/a | 3 | n/a | 4 | 75.0% |
| getElementById call sites | n/a | 78 | n/a | 113 | 69.0% |
| innerHTML assignment sites | n/a | 16 | n/a | 22 | 72.7% |
| GM/fetch/XMLHttpRequest request sites | n/a | 5 | n/a | 5 | 100.0% |

## Findings

- ⚠️ ResizeObserver constructions including aliases uses 4 of 4 (100.0%); review threshold is 100.0%.

## Policy

- Revision: `2026-07-29-v831-exact-artifact-production-proof`
- Rationale: Publish the already validated Issue #564 Incident Command Wire behaviour through the corrected exact-run candidate-artifact pipeline.
- Direct browser primitives and lifecycle-managed Toolkit wrappers are reported separately.
- This is a static regression screen, not a browser benchmark.
