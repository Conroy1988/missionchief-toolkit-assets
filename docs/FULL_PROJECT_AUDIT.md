# MissionChief Map Command Toolkit — Full Project Audit

## Audit objective

Improve development speed, release predictability, runtime efficiency and long-term maintainability without changing established Toolkit behaviour.

This audit is deliberately conservative. A static-analysis candidate is not treated as dead code until its call path, state effect, event registration and reflective use have been checked. Behavioural compatibility takes priority over reducing line count.

## Protected invariants

The following are release-blocking invariants for every optimisation change:

1. The canonical source remains `src/MissionChief_Map_Command_Toolkit.user.js`.
2. The `.user.js` and `.txt` distribution files remain byte-identical.
3. Userscript metadata version and runtime version remain equal.
4. Existing localStorage keys and settings import/export payloads remain compatible.
5. Desktop, Tablet and iOS operating modes retain their current controls and placement rules.
6. Every existing interface theme and payout template remains selectable.
7. Public image and audio paths remain stable.
8. Greasy Fork is not considered released until its live metadata reports the requested version.
9. Discord release announcements remain downstream of Greasy Fork verification and private backup.
10. No code is removed solely because a heuristic reports it as unused.

## Baseline

- Audited production line: **v4.13.0**
- Canonical release SHA-256: `7766664a4981f7985a4903f65a395bf0d00cc03472b5b45d18b5d1abf8712367`
- Source scale: approximately **1.75 MB** and **28,700 lines**
- Distribution state: source, `.user.js` and `.txt` validated as byte-identical
- Release path: GitHub → GitHub Release → Greasy Fork verification → private backup → Discord

## Repository and deployment findings

### 1. Deep-audit duplication

**Finding:** `full-userscript-audit.yml` repeated the code-integrity, static asset and performance checks that already run in dedicated workflows.

**Impact:** The same Python tools were executed multiple times for a single source pull request. This increased queue time, runner use and diagnostic noise without adding an independent implementation.

**Action:** The full audit is now focused on its unique responsibilities:

- complete userscript structural analysis;
- refined source evidence;
- AST-backed ESLint analysis.

Code integrity, asset health and performance remain protected by their dedicated workflows.

### 2. Repeated ESLint installation

**Finding:** The deep audit downloaded the exact ESLint package for every run.

**Impact:** Avoidable package-install latency on every userscript pull request.

**Action:** Add an npm cache keyed to the pinned ESLint version. The package remains version-pinned and install scripts remain disabled.

### 3. Code-integrity workflow scope was too broad

**Finding:** `code-integrity-audit.yml` ran for every pull request and every push to `main`, including documentation-only and media-only changes.

**Impact:** Unrelated changes consumed a full checkout, baseline resolution, self-test, code audit and asset audit.

**Action:** Restrict automatic runs to the canonical userscript, integrity policy, integrity checker, checker tests and the workflow itself. Static asset verification remains in the dedicated asset-health workflow.

### 4. Release command occupied a runner for the entire production release

**Finding:** The owner command dispatched `release-toolkit.yml` and then blocked while watching the production workflow, potentially for most of the 45-minute release timeout.

**Impact:** Two runners remained active for one release, and the command workflow appeared to be part of the release critical path even though publication was owned by the permanent production workflow.

**Action:** The owner command now:

1. validates the owner and release-ready dashboard state;
2. dispatches the permanent production workflow;
3. resolves and records the production run ID;
4. exits.

The production workflow remains solely responsible for publication, verification, backup, Discord and dashboard reconciliation.

### 5. Fallback release monitoring is over-frequent

**Finding:** The Greasy Fork fallback monitor is scheduled every five minutes even though the primary production workflow performs live Greasy Fork verification and a separate reconciliation workflow updates the announcement tracker after successful releases.

**Impact:** Up to 288 scheduled runs per day for a fallback path that should normally do no work.

**Recommendation:** Reduce fallback monitoring to every 15–30 minutes after confirming the primary reconciliation path remains healthy for several releases. Do not remove the fallback until equivalent incident detection is proven.

### 6. Generated state can trigger secondary workflows

**Finding:** Validation, release and reconciliation workflows legitimately commit generated distribution or status state back to `main`. Some downstream workflows subscribe to those generated files.

**Impact:** A single feature merge can create several follow-up runs and documentation deployments.

**Recommendation:** Keep status-driven documentation deployment, but remove generated dashboard paths from workflows that do not use them as an input. Continue suppressing bot-created source rebuild loops.

### 7. Development package workflow is a fallback, not the standard path

**Finding:** The reviewed-development-package workflow was introduced to work around large connector payloads. The Hyrule release demonstrated that fragmented package transport is slower and more failure-prone than committing a complete implementation.

**Decision:** Retain it temporarily as an explicitly owner-authorised recovery tool. The supported routine path is:

```text
complete local implementation → focused branch → pull request → targeted gates → merge → readiness → release command
```

Remove the package workflow only after the direct implementation path has completed multiple large updates without requiring it.

## Documentation and repository presentation findings

### 1. README maintenance cost

**Finding:** The previous README contained a hard-coded current version and primarily read as an operations checklist.

**Impact:** Every release risked documentation drift, while the repository landing page undersold the Toolkit's visual and operational scope.

**Action:** Replace it with a premium project landing page using:

- a custom repository hero;
- dynamic release and Greasy Fork badges;
- concise installation calls to action;
- an operational feature matrix;
- a Hyrule Command asset showcase;
- a visual release pipeline;
- direct routes to documentation, support, roadmap and confirmed-bug reporting.

### 2. Public documentation catalogue lag

**Finding:** The documentation contract and site catalogue pre-date Hyrule Command and Auto-load all vehicles.

**Impact:** The public site can pass its internal contract while still omitting current production capabilities.

**Required action:** Add Hyrule Command, Hyrule Quest Reward and Auto-load all vehicles to the documentation contract and site data, then rebuild and validate GitHub Pages.

## Runtime audit methodology

The runtime review uses four evidence layers:

1. **Structural inventory** — function size, complexity, selectors, observers, timers, listeners, storage and generated CSS.
2. **AST analysis** — ESLint-backed unused bindings and code-quality findings.
3. **Lifecycle review** — startup, mission-open refresh, settings changes, panel construction, cleanup and mission-switch state.
4. **Behavioural proof** — source inspection and targeted invariant checks before any removal.

### High-risk areas requiring manual proof

- document-wide MutationObservers;
- recurring intervals below one second;
- event listeners attached to persistent global objects;
- theme CSS generators with intentional selector duplication;
- callback functions referenced indirectly through MissionChief hooks;
- settings migrations and legacy key aliases;
- Leaflet guards and alliance-building suppression;
- payout audio and animation cleanup;
- mission-window replacement and stale asynchronous requests.

### Safe optimisation order

1. Stop work earlier when a feature or theme is disabled.
2. Replace repeated DOM searches only where node lifetime is stable.
3. Batch mutation-driven refreshes into one queued render.
4. Disconnect observers and clear timers at existing lifecycle boundaries.
5. Remove provably unreachable declarations.
6. Consolidate duplicated pure calculations.
7. Defer architectural decomposition until regression coverage exists.

## Dead-code removal rule

A candidate may be removed only when all of the following are true:

- its declaration has no direct call sites;
- it is not registered as an event, observer, timer or MissionChief callback;
- its name is not used through an object property, string lookup or exported page context;
- removing it does not change settings migration, CSS output or public metadata;
- syntax, validation, integrity, performance and full-audit gates pass afterward;
- the diff is narrow enough to revert independently.

## Delivery phases

### Phase 1 — audit and deployment simplification

- [x] Create a dedicated audit issue and branch
- [x] Remove duplicate deep-audit execution
- [x] Cache the pinned ESLint dependency
- [x] Restrict code-integrity automation to relevant changes
- [x] Make the owner release command asynchronous
- [x] Rebuild the README as a premium project landing page
- [ ] Synchronise public documentation with v4.13.0
- [ ] Run the complete PR audit suite and collect evidence

### Phase 2 — low-risk runtime reductions

- [ ] Review audit evidence by call path
- [ ] Reduce unnecessary disabled-feature work
- [ ] Batch repeated mission-window refresh work
- [ ] Correct confirmed observer, timer and listener lifecycle gaps
- [ ] Add targeted invariants for each changed subsystem

### Phase 3 — proven dead-code removal

- [ ] Remove only evidence-backed dead functions and bindings
- [ ] Remove stale maintenance markers and commented code
- [ ] Confirm source/distribution parity and settings compatibility
- [ ] Publish before/after structural metrics

### Phase 4 — final regression and release readiness

- [ ] Validate every theme and operating mode contract
- [ ] Validate asset paths and public documentation
- [ ] Run code integrity, performance and full userscript audit
- [ ] Run release readiness without publishing
- [ ] Release only after all protected invariants pass

## Expected outcome

- Faster and less noisy pull-request validation
- Lower GitHub Actions consumption
- One predictable release-dispatch route
- Better repository presentation and discoverability
- Fewer unnecessary runtime operations
- Smaller, clearer source only where removal is proven safe
- No loss of features, settings, themes, public assets or release safeguards
