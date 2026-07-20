# Toolkit performance budget

The Toolkit uses a static CI guardrail to detect changes likely to increase startup work, DOM churn or long-lived browser processing before release.

The guardrail is deliberately conservative. It reports workload indicators and lifecycle surface area; it does **not** claim to replace profiling inside MissionChief.

## Measurement model

The checker separates two categories that must not be conflated:

### Direct browser primitives

- `setInterval` and `setTimeout` spellings;
- direct `MutationObserver` and `ResizeObserver` constructions;
- direct `requestAnimationFrame` and `addEventListener` call sites;
- selector calls and document startup hooks.

### Toolkit-managed runtime surface

- `runtimeSetInterval`, `runtimeSetTimeout` and `runtimeRequestAnimationFrame` call sites;
- `runtimeListen`, `runtimeTrackObserver` and `runtimeRunWhenIdle` call sites;
- observer constructions resolved through local aliases such as `MutationObserverCtor`, `ResizeObserverCtor` and document-window `Observer` aliases;
- observer registrations using `subtree: true`, including document/body-wide registrations;
- `getElementById`, `innerHTML` assignment and network-request call sites.

Managed wrappers are not automatically bad. They provide teardown ownership, duplicate-runtime protection and callback suppression after destruction. They are measured because an increase still expands the runtime surface and must remain deliberate.

## Structural metrics

The checker also records:

- source bytes, total lines and non-empty lines;
- estimated embedded CSS bytes and rule blocks;
- absolute-limit utilisation for every governed metric;
- required startup instrumentation and userscript metadata markers.

## Comparison rules

- Pull requests compare the candidate source against the target `main` commit.
- Pushes to `main` compare against the previous `main` commit.
- Release Readiness compares the candidate against the latest versioned release tag.
- When no comparison source is available, absolute limits and utilisation warnings still apply.

The version-controlled policy is stored in `.github/performance-budget.json`.

## Baseline-locked metrics

Issue #247 established the wrapper-aware v4.20.10 baseline. Corrected runtime, observer, DOM and network metrics are initially locked to that verified source.

An increase therefore requires an explicit policy amendment in the same pull request, with a technical rationale. This is not a permanent claim that every count must only decrease; it prevents new workload from bypassing review because it is hidden behind a wrapper or alias.

## Warnings and failures

- Crossing an absolute limit fails the check.
- Crossing an absolute utilisation review threshold creates a warning.
- Relative growth can warn or fail according to the policy.
- Warnings do not fail CI, but must be reviewed before merge.

A legitimate feature may require a budget adjustment. Never raise a ceiling merely to make CI green. Record the measured reason and expected runtime effect in the policy revision and PR.

## Diagnostics

Every run uploads:

- `performance-budget-report.json` for machine-readable metrics;
- `performance-budget-report.md` for the workflow summary.

The report table includes each candidate value, absolute limit and utilisation percentage. For reported runtime problems, also use the structured Performance Report issue form and include `window.__MCMS_STARTUP_METRICS__` where available.

## Limits of the static audit

Static call-site counts do not reveal invocation frequency, DOM size, device speed, network latency or browser scheduling. Runtime optimisations still require deterministic fixtures and before/after browser evidence. The static gate exists to stop unreviewed workload growth and to identify where profiling should be concentrated.
