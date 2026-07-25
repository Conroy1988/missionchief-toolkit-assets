# Toolkit performance budget

**Result:** PASSED

| Metric | Base | Candidate | Change | Absolute limit | Utilisation |
|---|---:|---:|---:|---:|---:|
| Source bytes | 1535484 | 1553105 | +17,621 (+1.15%) | 3000000 | 51.8% |
| Source lines | 23234 | 23412 | +178 (+0.77%) | 64000 | 36.6% |
| Non-empty lines | 22169 | 22343 | +174 (+0.78%) | n/a | n/a |
| Estimated embedded CSS bytes | 657301 | 664879 | +7,578 (+1.15%) | 950000 | 70.0% |
| Estimated embedded CSS rule blocks | 5094 | 5177 | +83 (+1.63%) | 7000 | 74.0% |
| Direct setInterval call sites | 1 | 1 | +0 (+0.00%) | 4 | 25.0% |
| Direct setTimeout call sites | 3 | 3 | +0 (+0.00%) | 25 | 12.0% |
| Direct MutationObserver constructions | 8 | 8 | +0 (+0.00%) | 8 | 100.0% |
| Direct ResizeObserver constructions | 1 | 1 | +0 (+0.00%) | 4 | 25.0% |
| Direct requestAnimationFrame call sites | 1 | 1 | +0 (+0.00%) | 20 | 5.0% |
| Direct addEventListener call sites | 33 | 37 | +4 (+12.12%) | 120 | 30.8% |
| querySelector/querySelectorAll call sites | 199 | 204 | +5 (+2.51%) | 400 | 51.0% |
| DOMContentLoaded/load startup hooks | 4 | 4 | +0 (+0.00%) | 10 | 40.0% |
| Managed runtimeSetInterval call sites | 1 | 1 | +0 (+0.00%) | 1 | 100.0% |
| Managed runtimeSetTimeout call sites | 81 | 81 | +0 (+0.00%) | 99 | 81.8% |
| Managed runtimeRequestAnimationFrame call sites | 10 | 10 | +0 (+0.00%) | 14 | 71.4% |
| Managed runtimeListen call sites | 26 | 26 | +0 (+0.00%) | 31 | 83.9% |
| Managed runtimeTrackObserver call sites | 13 | 13 | +0 (+0.00%) | 15 | 86.7% |
| Managed runtimeRunWhenIdle call sites | 3 | 3 | +0 (+0.00%) | 3 | 100.0% |
| MutationObserver constructions including aliases | 10 | 10 | +0 (+0.00%) | 12 | 83.3% |
| ResizeObserver constructions including aliases | 4 | 4 | +0 (+0.00%) | 4 | 100.0% |
| Observer registrations with subtree: true | 8 | 8 | +0 (+0.00%) | 10 | 80.0% |
| Document/body subtree observer registrations | 3 | 3 | +0 (+0.00%) | 3 | 100.0% |
| getElementById call sites | 78 | 78 | +0 (+0.00%) | 113 | 69.0% |
| innerHTML assignment sites | 18 | 18 | +0 (+0.00%) | 22 | 81.8% |
| GM/fetch/XMLHttpRequest request sites | 4 | 4 | +0 (+0.00%) | 4 | 100.0% |

## Findings

- ⚠️ ResizeObserver constructions including aliases uses 4 of 4 (100.0%); review threshold is 100.0%.
- ⚠️ Document/body subtree observer registrations uses 3 of 3 (100.0%); review threshold is 100.0%.
- ⚠️ Estimated embedded CSS rule blocks increased from 5,094 to 5,177 (+83 (+1.63%)), exceeding the review threshold.

## Policy

- Revision: `2026-07-23-issue-385-64k-source-ceiling`
- Rationale: Issue #385 owner-authorized policy change: double the canonical userscript absolute line ceiling from 32,000 to 64,000 lines for the Issue #378 major operational-suite programme. All byte, CSS, observer, timer, listener, selector and network ceilings remain unchanged; relative-growth review thresholds remain active.
- Direct browser primitives and lifecycle-managed Toolkit wrappers are reported separately.
- This is a static regression screen, not a browser benchmark.
