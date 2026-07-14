# Toolkit performance budget

The Toolkit uses a static CI guardrail to detect changes that are likely to increase startup work or long-lived browser processing before they are released.

## What is measured

The checker records:

- source bytes and line count;
- estimated embedded CSS bytes and rule blocks;
- `setInterval` and `setTimeout` call sites;
- `MutationObserver` and `ResizeObserver` constructions;
- `requestAnimationFrame` call sites;
- event-listener and selector call sites;
- document startup hooks;
- required startup instrumentation and userscript metadata markers.

These are workload indicators, not a substitute for real browser profiling. A static increase does not automatically prove that runtime performance became worse, but abrupt increases require review.

## Comparison rules

- Pull requests compare the candidate source against the target `main` commit.
- Pushes to `main` compare against the previous `main` commit.
- Release Readiness compares the candidate against the latest versioned release tag.
- When no comparison source is available, absolute source-size limits still apply.

The version-controlled policy is stored in `.github/performance-budget.json`.

## Warnings and failures

Small increases above a review threshold create GitHub Actions warnings but do not block development. Larger increases or absolute-limit violations fail the check and block Release Readiness.

A legitimate feature may require a budget adjustment. Update the policy in the same pull request and explain the reason in its `revision` and `rationale` fields. Budget changes are therefore visible in review rather than hidden in workflow code.

## Diagnostics

Every run uploads:

- `performance-budget-report.json` for machine-readable metrics;
- `performance-budget-report.md` for the workflow summary.

For reported runtime problems, also use the structured Performance Report issue form and include `window.__MCMS_STARTUP_METRICS__` where available.
