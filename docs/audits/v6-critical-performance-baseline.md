# v6.0.0 critical performance baseline

**Issue:** #510  
**Baseline release:** v5.0.7  
**Baseline canonical SHA-256:** `97a71c7df20a9d896872e554b671f789c74069f2ec8a1dbb8f4afd7135c303da`  
**Candidate canonical SHA-256:** `9c3199e9eee3fe6937abddb045f4bcfdff127bb18c87014a77bf5627c3da71b1`  
**LSSM settings reference:** `LSS-Manager/LSSM-V.4@88e41646e59a7d620624f90f1d9a0a62320c2775`

## Scope

This evidence covers the first v6.0.0 performance implementation: obsolete feature retirement, Operational Window settings reconstruction, observer scoping, owned-node cleanup and recurring-work reduction.

The numbers below are measured directly from the exact v5.0.7 validated userscript and the v6 candidate source. They are static implementation measurements, not a claim about browser frame rate. MissionChief browser profiling remains a required release gate.

## Root-cause analysis

The largest identifiable hot path was the Operational Window lifecycle:

1. Its MutationObserver watched structural roots with `subtree`, attributes and `characterData` enabled together.
2. MissionChief countdown text can change continuously, so unrelated timer text was capable of scheduling complete Operational Window reconciliation.
3. The observer could see DOM written by the Toolkit itself unless every mutation happened beneath a recognised owned node.
4. Every reconciliation removed feature UI through document-wide selectors.
5. Every reconciliation restored decorated native nodes through additional document-wide selectors.
6. The global MissionChief observer scheduled the Operational Window scan twice for one mission mutation.
7. A settings change rebuilt the complete Toolkit panel rather than synchronising only the typed Operational Window controls.

This combination could create repeated full mission-window scans and rebuilds during ordinary countdown and DOM activity. That is the primary code-supported explanation for the reported severe lag.

## Corrective architecture

- Split observed roots into **content roots** and **structural roots**.
- Permit `characterData` observation only on requirement content roots.
- Ignore Toolkit-owned settings and Operational Window mutations.
- Coalesce relevant renders to a 120 ms boundary.
- Replace full-document feature cleanup with a per-document owned-node registry.
- Replace full-document native-decoration reset with a per-document decorated-node registry.
- Remove duplicate global Operational Window scheduling.
- Synchronise only the typed settings root after a settings change.
- Retain deterministic observer, listener, timer, native-decoration and created-node teardown.

## Measured static delta

| Metric | v5.0.7 | v6 candidate | Delta |
|---|---:|---:|---:|
| Source bytes | 2,060,765 | 1,727,090 | −333,675 (−16.2%) |
| Source lines | 31,761 | 25,146 | −6,615 (−20.8%) |
| Named function declarations | 979 | 886 | −93 (−9.5%) |
| MutationObserver constructions | 9 | 9 | no increase |
| Registered recurring tasks | 8 | 6 | −2 (−25.0%) |
| `runtimeSetTimeout` call sites | 97 | 85 | −12 (−12.4%) |
| `runtimeRequestAnimationFrame` call sites | 12 | 11 | −1 (−8.3%) |
| `addEventListener` call sites | 38 | 34 | −4 (−10.5%) |
| `querySelectorAll` call sites | 73 | 63 | −10 (−13.7%) |
| Operational owned-node full-document cleanup scans | 1 | 0 | −100% |
| Operational native-decoration full-document cleanup scans | 1 | 0 | −100% |

## Retired runtime ownership

The following systems are removed from state defaults, settings UI, routes, map layers, timers, observers, animation frames, styles and teardown:

- Automatic day/night.
- Heatmap.
- Mission Intelligence Inspector.
- Mission Age Workflow.
- Age Watch.

Legacy persisted keys are deleted during state normalisation and cannot reactivate runtime work.

The separate **Mission Age map timer badge** remains supported and has its own regression contract.

## Operational Window settings reconstruction

The screenshot defect was caused by the panel invoking an obsolete raw settings renderer despite a typed renderer existing in the source. v6 removes the obsolete renderer and mounts only typed controls.

The control schema is aligned with current LSSM V.4 settings definitions:

- toggles;
- numbers with bounds;
- colours;
- selects;
- multiselects;
- dependency and mutual-exclusion rules;
- structured list editors;
- hidden runtime state omitted from the user settings panel.

Only Enhanced Requirements is expanded initially. The larger Call Window, Call List, Transport and structured-editor sections remain collapsible to prevent another unmanageable settings wall.

## Release evidence still required

Before v6.0.0 production publication:

- capture idle and active profiles with `tools/mcms-performance-profiler.user.js`;
- compare repeated mission open/close cycles;
- compare repeated settings open/close cycles;
- confirm observer/listener/timer totals remain stable;
- confirm no sustained long-task loop while MissionChief countdowns update;
- confirm no new console errors on Desktop, Tablet/iPad and iOS Safari;
- run all existing Toolkit regression, performance and release-readiness suites.

No FPS or elapsed-time claim is made until those browser-level profiles are retained.
