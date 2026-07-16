# MissionChief Map Command Toolkit — Full Project Audit

## Audit objective

Improve development speed, release predictability, runtime efficiency and long-term maintainability without changing established Toolkit behaviour.

This audit is deliberately conservative. A static-analysis candidate is not treated as dead code until its call path, state effect, event registration, template interpolation, settings compatibility and reflective use have been checked. Behavioural compatibility takes priority over reducing line count.

## Protected invariants

The following remain release-blocking:

1. Canonical source remains `src/MissionChief_Map_Command_Toolkit.user.js`.
2. The `.user.js` and `.txt` distributions remain byte-identical.
3. Userscript metadata version and runtime version remain equal.
4. Existing localStorage keys and settings import/export payloads remain compatible.
5. Desktop, Tablet and iOS modes retain their controls and placement rules.
6. Every existing interface theme and payout presentation remains selectable.
7. Public image and audio paths remain stable.
8. Greasy Fork is not considered released until live metadata reports the requested version.
9. Discord release announcements remain downstream of Greasy Fork verification and private backup.
10. No code is removed solely because a heuristic reports it as unused.

## Verified audit baseline

- Audited and released version: **v4.13.1**
- Canonical SHA-256: `dede1999c8121c7bc73d644711d8b1258e3598db5118aad9da6b0731e038f69c`
- Source scale: **1,750,881 bytes**, **28,710 lines**
- Named function-like blocks: **664**
- Distribution state: canonical source, `.user.js` and `.txt` byte-identical
- Release state: GitHub Release published, Greasy Fork verified, private backup committed and Discord announcement posted

## Audit evidence

The completed audit combined:

1. full structural inventory;
2. refined lexical-scope analysis;
3. AST-backed ESLint analysis;
4. code-integrity comparison against the released baseline;
5. static performance budgets;
6. asset-health and documentation contracts;
7. direct source review of startup, observers, timers, listeners, network work, settings and cleanup;
8. targeted invariants for each changed runtime path;
9. production release-readiness and final publication verification.

The refined v4.13.1 audit completed with:

- definite failures: **0**;
- review findings: **8**;
- dead-code candidates: **1 metadata compatibility candidate**, retained;
- advisories: **21**.

## Dead-code conclusion

No function, branch, binding or CSS block met the complete evidence threshold for safe removal.

The only remaining automated candidate is the `discordapp.com` userscript `@connect` host. It is intentionally retained because imported settings may contain legacy Discord webhook hosts, including `discordapp.com`, `ptb.discordapp.com` and `canary.discordapp.com`.

This is a valid audit result: **no speculative code deletion was performed**.

## Runtime findings and completed reductions

### Economy Mode cache pruning

**Before:** current vehicle and building marker collections were rescanned for every cached hidden layer.

**Change:** each collection is materialised once per prune pass as a `Set`, then reused through constant-time membership checks.

**Result:** less repeated work with identical cache-retention behaviour.

### Auto-load all vehicles

**Before:** every follow-up scan queried the whole document and rebuilt a duplicate mission-root selector list.

**Change:**

- the canonical mission-root selector is reused;
- once a connected, visible mission window is known, follow-up queries are scoped to that window;
- document-wide discovery remains available before a mission is identified or after a stale window disappears;
- bounded retries, duplicate-request protection and native MissionChief clicking remain unchanged.

**Result:** less DOM work during an active mission without changing dispatch or vehicle-selection behaviour.

### Observer and timer review

- The Toolkit uses one runtime-owned interval, limited to an active payout animation and cleared through the runtime registry.
- Global event listeners created through `runtimeListen` are removed during runtime destruction.
- MutationObservers are registered through the runtime registry and disconnected on replacement or shutdown.
- Document-wide observers were retained only where they have a bounded or conditional purpose:
  - alliance-building suppression while that preference is active;
  - temporary main-observer fallback before stable map/mission roots exist;
  - Auto-load all vehicles only while the feature is enabled.
- Payout audio remains lazy: hosted audio uses `preload="none"` and is requested only for a matching payout event.
- Payout presentation DOM remains on demand.

No confirmed observer, timer or listener leak was found.

## High-risk runtime findings deferred with evidence

### Main stylesheet

`installMainStyles()` spans approximately **12,093 lines** and contributes roughly **821 KB** of generated CSS—nearly half of the userscript.

Document-start installation is intentional and avoids a later full-page selector rematch. Splitting it without screenshots and state coverage could introduce unthemed flashes, incomplete theme switching or responsive regressions.

A separate controlled project is tracked in **#63**. It requires a visual matrix across all themes, payout presentations, Desktop, Tablet, iOS, Economy Mode and reduced motion before modularisation.

### High-complexity operational functions

The following functions are active, important and not dead code:

| Function | Refined audit result |
|---|---:|
| `captureMissionMarkerData` | complexity ~135 |
| `fetchFinancialLedger` | complexity ~123 |
| `boot` | complexity ~128; ~332 lines |
| `createPanel` | ~375 lines |
| `loadState` | complexity ~67 |
| `toggleFeature` | complexity ~75 |
| `handleSettingChange` | complexity ~78 |
| `updateUI` | complexity ~75 |

Fixture-first decomposition is tracked in **#64**. These functions must not be split merely to satisfy a complexity threshold.

## Repository and deployment improvements

### Duplicate audit work removed

The Full Userscript Audit previously repeated code-integrity, static asset and performance checks already enforced by dedicated workflows.

It now focuses on its unique structural, refined-source and AST-backed responsibilities. Code integrity, asset health and performance remain independent required gates.

### Pinned ESLint dependency cached

The exact ESLint audit package remains pinned, install scripts remain disabled and the npm package cache is reused between deep-audit runs.

### Workflow triggers narrowed

Code Integrity now runs only for canonical source, integrity policy, integrity tooling and its own workflow. Documentation-only and unrelated media changes no longer consume the full code-integrity path.

### One release command

The owner-only command remains:

```text
/release-toolkit X.Y.Z RELEASE
```

It now:

1. verifies the requested version is the current validated candidate;
2. checks whether release readiness belongs to that exact version;
3. automatically runs and awaits current-version readiness when required;
4. dispatches the permanent production workflow;
5. records readiness and production run IDs;
6. exits after dispatch.

The permanent production workflow alone owns GitHub Release publication, Greasy Fork verification, private backup, Discord announcement and dashboard reconciliation.

### Release state reconciled

The production workflow now updates together:

- `status/release-dashboard.json`;
- the detailed current-version readiness record;
- generated `status/README.md`.

This prevents the public control panel from showing a stale pre-release state after a successful release.

### Fallback monitor retained

The Greasy Fork fallback monitor remains scheduled every five minutes. It is intentionally retained while the improved primary command and reconciliation path accumulate more production history.

A future low-risk reduction to a 15–30 minute interval remains appropriate after several more successful releases. The fallback should not be removed until equivalent incident detection is proven.

### Development package workflow retained as recovery only

The reviewed-development-package workflow remains an owner-authorised recovery tool for connector payload limits. It is not the standard feature path.

Supported routine delivery is:

```text
complete implementation → focused branch → pull request → targeted gates → merge → single release command
```

## Repository presentation

The README has been rebuilt as a premium project landing page with:

- a custom command-centre hero;
- dynamic release and Greasy Fork badges;
- direct installation calls to action;
- feature and operating-mode matrices;
- Hyrule Command artwork;
- a visual release flow;
- community, support, issue and roadmap routes;
- compatibility and release-integrity principles.

The public documentation catalogue now includes:

- Auto-load all vehicles;
- 007 Intelligence;
- Hyrule Command;
- 007 Intelligence payout;
- Hyrule Quest Reward.

## Before-and-after operational outcome

### Deployment

- fewer duplicate audit executions;
- fewer irrelevant workflow starts;
- cached deep-audit dependency installation;
- one current-version-aware release command;
- no second runner held for the complete production release;
- consistent machine-readable and human-readable release state.

### Runtime

- less repeated marker-layer work during cache pruning;
- less document-wide DOM searching during vehicle batch loading;
- no extra timers or observers introduced;
- inactive payout media remains lazy;
- no settings, feature, theme, payout or public asset removed.

### Quality

- full audit: passed;
- canonical validation: passed;
- JavaScript syntax: passed;
- source/distribution parity: passed;
- code integrity: passed;
- performance budget and targeted runtime invariants: passed;
- asset health: passed;
- documentation drift and Pages build: passed;
- release readiness: passed;
- production release v4.13.1: passed.

## Completed phases

### Phase 1 — audit and deployment simplification

- [x] Create dedicated audit tracking
- [x] Remove duplicate deep-audit execution
- [x] Cache the pinned ESLint dependency
- [x] Restrict code-integrity automation to relevant changes
- [x] Rebuild the README as a premium project landing page
- [x] Synchronise public documentation
- [x] Run and retain complete audit evidence

### Phase 2 — low-risk runtime reductions

- [x] Review findings by call path
- [x] Reduce repeated cache-pruning work
- [x] Scope active mission-window vehicle queries
- [x] Review observers, timers, listeners and cleanup
- [x] Add targeted runtime invariants
- [x] Preserve settings, modes, themes, payouts and assets

### Phase 3 — dead-code decision

- [x] Check direct, indirect, event, observer, timer, hook and template references
- [x] Retain the only compatibility-sensitive metadata candidate
- [x] Record that no code currently meets the safe-removal threshold
- [x] Separate high-risk refactors into fixture-first issues

### Phase 4 — release and reconciliation

- [x] Validate every documented theme and operating-mode contract
- [x] Validate asset paths and public documentation
- [x] Run integrity, performance and full-userscript audits
- [x] Run current-version release readiness
- [x] Release v4.13.1 through GitHub, Greasy Fork, private backup and Discord
- [x] Reconcile generated release state

## Final decision

The conservative audit is complete.

The Toolkit is faster in identified low-risk paths, the deployment process is materially simpler, the release state is more reliable, the repository presentation is substantially improved and no unsupported deletion or behavioural rewrite was introduced.

Larger optimisations remain deliberately separated into **#63** and **#64**, where they can receive the visual and fixture coverage required to protect the current production behaviour.
